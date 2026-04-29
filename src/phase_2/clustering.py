import sqlite3
import pandas as pd
import numpy as np
import os
import hashlib
import pickle
import umap
from sklearn.cluster import DBSCAN
from typing import List, Optional, Dict
import traceback
from langdetect import detect, DetectorFactory
from dotenv import load_dotenv
import openai
import sys

# Ensure stdout supports unicode on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, OSError):
        pass  # Already configured or not possible

# Set seed for deterministic language detection
DetectorFactory.seed = 42

# Load environment variables
load_dotenv()

# Fallback for HDBSCAN if not available
try:
    import hdbscan  # type: ignore[import-not-found]
    HAS_HDBSCAN = True
except ImportError:
    HAS_HDBSCAN = False
    # Only print warning once
    if os.environ.get("HIDE_HDBSCAN_WARNING") != "1":
        print("Notice: hdbscan not found. Using optimized DBSCAN fallback.")
        os.environ["HIDE_HDBSCAN_WARNING"] = "1"

class EmbeddingClient:
    """
    Handles embedding generation with support for OpenAI and Local models.
    Includes granular on-disk caching.
    """
        self.use_openai = use_openai
        self.use_gemini = False
        self.cache_dir = "data/embeddings_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Check API keys
        openai_key = os.getenv("OPENAI_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY")

        if self.use_openai and openai_key:
            self.model_name = model_name or "text-embedding-3-small"
            self.client = openai.OpenAI(api_key=openai_key)
        elif gemini_key:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            self.use_gemini = True
            self.use_openai = False
            self.model_name = "models/text-embedding-004"
            print("Using Gemini API for embeddings (zero local memory footprint)")
        else:
            self.use_openai = False
            self.use_gemini = False
            # We completely disable local embeddings (SentenceTransformers) on Render
            # because importing torch/transformers uses ~400MB RAM, causing instant OOM.
            error_msg = "No API keys found! You MUST set GEMINI_API_KEY or OPENAI_API_KEY in Render Environment Variables. Local embeddings are disabled to prevent OOM crashes."
            print(f"CRITICAL ERROR: {error_msg}")
            raise RuntimeError(error_msg)

    def _get_cache_path(self, text: str) -> str:
        text_hash = hashlib.sha1(text.encode()).hexdigest()
        subdir = os.path.join(self.cache_dir, text_hash[:2])
        os.makedirs(subdir, exist_ok=True)
        return os.path.join(subdir, f"{text_hash}.pkl")

    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Retrieves embeddings for a list of texts, using cache when available.
        """
        embeddings = []
        texts_to_embed = []
        indices_to_embed = []
        
        for i, text in enumerate(texts):
            cache_path = self._get_cache_path(text)
            if os.path.exists(cache_path):
                try:
                    with open(cache_path, 'rb') as f:
                        embeddings.append(pickle.load(f))
                except:
                    embeddings.append(None)
                    texts_to_embed.append(text)
                    indices_to_embed.append(i)
            else:
                embeddings.append(None)
                texts_to_embed.append(text)
                indices_to_embed.append(i)
        
        if texts_to_embed:
            print(f"Embedding {len(texts_to_embed)} new texts...")
            if self.use_openai:
                new_embeddings = self._embed_openai(texts_to_embed)
            elif self.use_gemini:
                new_embeddings = self._embed_gemini(texts_to_embed)
            else:
                new_embeddings = self._embed_local(texts_to_embed)
            
            for i, (idx, emb) in enumerate(zip(indices_to_embed, new_embeddings)):
                cache_path = self._get_cache_path(texts_to_embed[i])
                with open(cache_path, 'wb') as f:
                    pickle.dump(emb, f)
                embeddings[idx] = emb
                
        return np.array(embeddings)

    def _embed_local(self, texts: List[str]) -> np.ndarray:
        raise RuntimeError("Local embeddings are disabled.")

    def _embed_openai(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(
            input=texts,
            model=self.model_name
        )
        return [data.embedding for data in response.data]

    def _embed_gemini(self, texts: List[str]) -> List[List[float]]:
        import google.generativeai as genai
        # Gemini handles batches natively but has limits. Batch size 100 max per request.
        all_embeddings = []
        batch_size = 50
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            result = genai.embed_content(
                model=self.model_name,
                content=batch,
                task_type="clustering"
            )
            if isinstance(result['embedding'][0], list):
                all_embeddings.extend(result['embedding'])
            else:
                all_embeddings.append(result['embedding'])
        return all_embeddings

def get_db_connection(db_path="data/audit_log.db"):
    # Ensure directory exists before connecting
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return sqlite3.connect(db_path)

def fetch_reviews_from_db(product_id="Groww"):
    """Fetches processed reviews from the audit log."""
    conn = get_db_connection()
    try:
        query = "SELECT review_id, content FROM processed_reviews WHERE product_id = ?"
        df = pd.read_sql_query(query, conn, params=(product_id,))
    except Exception as e:
        print(f"Database error: {e}")
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

def is_english(text: str) -> bool:
    """Detects if a text is English with extra safety."""
    if not text or len(text.strip()) < 5:
        return False
    try:
        return detect(text) == 'en'
    except:
        return False

def run_clustering_pipeline(
    product_id: str = "Groww",
    min_cluster_size: int = 15,
) -> Optional[pd.DataFrame]:
    """
    Full Phase 2 Pipeline:
    Ingest from DB -> Pre-filter -> Embed -> Cluster -> Return Clustered DF

    Args:
        product_id: ID to filter in the DB.
        min_cluster_size: Minimum number of reviews to form a theme.
                          Increase this for a cleaner, less noisy report.
    """
    # 1. Load Data
    print(f"\n--- Phase 2: Clustering Pipeline for {product_id} ---")
    conn = get_db_connection()
    try:
        df = pd.read_sql_query(
            "SELECT review_id, content FROM processed_reviews WHERE product_id = ?",
            conn,
            params=(product_id,)
        )
    finally:
        conn.close()

    if df.empty:
        print(f"No reviews found for product {product_id}")
        return None

    print(f"Initial reviews: {len(df)}")

    # 2. Pre-filtering
    # Length filter: Ignore very short 'ok', 'good' reviews
    df = df[df['content'].str.len() >= 20].reset_index(drop=True)
    print(f"After length filter: {len(df)}")

    # Language filter: Keep only English
    print("Applying language filter...")
    df['lang'] = df['content'].apply(lambda x: 'en' if is_english(x) else 'other')
    df = df[df['lang'] == 'en'].drop(columns=['lang']).reset_index(drop=True)
    print(f"After language filter: {len(df)}")

    # 3. Embedding
    client = EmbeddingClient()
    embeddings = client.get_embeddings(df['content'].tolist())

    # 4. Dimensionality Reduction (UMAP)
    print("Reducing dimensions (UMAP)...")
    reducer = umap.UMAP(
        n_neighbors=15,
        n_components=5,
        min_dist=0.0,
        metric='cosine',
        random_state=42
    )
    reduced_embeddings = reducer.fit_transform(embeddings)

    # 5. Clustering (HDBSCAN or DBSCAN fallback)
    print(f"Clustering (min_cluster_size={min_cluster_size})...")
    if HAS_HDBSCAN:
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=5,
            metric='euclidean',
            cluster_selection_method='eom'
        )
    else:
        # Fallback to DBSCAN if hdbscan is missing
        clusterer = DBSCAN(eps=0.5, min_samples=min_cluster_size)

    clusters = clusterer.fit_predict(reduced_embeddings)
    df['cluster'] = clusters

    n_clusters = len(set(clusters)) - (1 if -1 in clusters else 0)
    n_noise = list(clusters).count(-1)
    
    print(f"Clustering complete. Found {n_clusters} clusters and {n_noise} noise points.")
    
    # Preview top clusters
    if n_clusters > 0:
        print("\n--- Cluster Preview ---")
        cluster_counts = df[df['cluster'] != -1]['cluster'].value_counts()
        for cluster_id in cluster_counts.index[:5]:
            count = cluster_counts[cluster_id]
            sample = df[df['cluster'] == cluster_id]['content'].iloc[0]
            # Use ASCII safe printing to avoid CP1252 errors on Windows consoles
            safe_sample = sample[:100].encode('ascii', 'ignore').decode('ascii')
            print(f"Cluster {cluster_id} ({count} reviews): {safe_sample}...")
            
    return df

if __name__ == "__main__":
    run_clustering_pipeline()
