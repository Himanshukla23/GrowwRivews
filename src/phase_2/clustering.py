import sqlite3
import pandas as pd
import numpy as np
import os
import hashlib
import pickle
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
HAS_HDBSCAN = False
if "RENDER" not in os.environ and "FLY_APP_NAME" not in os.environ and "VERCEL" not in os.environ:
    try:
        import hdbscan  # type: ignore[import-not-found]
        HAS_HDBSCAN = True
    except ImportError:
        pass

class EmbeddingClient:
    """
    Handles embedding generation with support for OpenAI and Local models.
    Includes granular on-disk caching.
    """
    def __init__(self, use_openai: bool = False, model_name: Optional[str] = None):
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
            self.model_name = "models/gemini-embedding-001"
            print("Using Gemini API for embeddings (zero local memory footprint)")
        else:
            self.use_openai = False
            self.use_gemini = False
            # We completely disable local embeddings (SentenceTransformers) on Render
            # because importing torch/transformers uses ~400MB RAM, causing instant OOM.
            print("No external API keys found. Defaulting to TF-IDF embeddings to prevent OOM crashes.")

    def _get_cache_path(self, text: str) -> str:
        text_hash = hashlib.sha1(text.encode()).hexdigest()
        subdir = os.path.join(self.cache_dir, text_hash[:2])
        os.makedirs(subdir, exist_ok=True)
        return os.path.join(subdir, f"{text_hash}.pkl")

    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Retrieves embeddings for a list of texts, using cache when available.
        """
        embeddings = [None] * len(texts)
        indices_to_embed = []
        texts_to_embed = []
        
        expected_dim = None

        # 1. Load from cache
        for i, text in enumerate(texts):
            cache_path = self._get_cache_path(text)
            if os.path.exists(cache_path):
                try:
                    with open(cache_path, 'rb') as f:
                        emb = pickle.load(f)
                        if emb is not None and isinstance(emb, (list, np.ndarray)):
                            embeddings[i] = emb
                            if expected_dim is None:
                                expected_dim = len(emb)
                        else:
                            indices_to_embed.append(i)
                            texts_to_embed.append(text)
                except:
                    indices_to_embed.append(i)
                    texts_to_embed.append(text)
            else:
                indices_to_embed.append(i)
                texts_to_embed.append(text)
        
        # 2. Embed missing texts
        if texts_to_embed:
            print(f"Embedding {len(texts_to_embed)} new texts...")
            if self.use_openai:
                new_embeddings = self._embed_openai(texts_to_embed)
            elif self.use_gemini:
                new_embeddings = self._embed_gemini(texts_to_embed)
            else:
                new_embeddings = self._embed_tfidf(texts_to_embed, dim=expected_dim or 384)
            
            # Ensure new_embeddings is a list of the same length as texts_to_embed
            if len(new_embeddings) != len(texts_to_embed):
                print(f"Warning: Expected {len(texts_to_embed)} embeddings, got {len(new_embeddings)}. Filling with zeros.")
                # This shouldn't happen with correct logic, but adding as safety
                
            for i, (idx, emb) in enumerate(zip(indices_to_embed, new_embeddings)):
                cache_path = self._get_cache_path(texts_to_embed[i])
                try:
                    with open(cache_path, 'wb') as f:
                        pickle.dump(emb, f)
                except:
                    pass
                embeddings[idx] = emb
                if expected_dim is None and emb is not None:
                    expected_dim = len(emb)

        # 3. Final validation and conversion
        # Filter out any None values that might have slipped through
        valid_embeddings = []
        if expected_dim is None:
            expected_dim = 384 # Default fallback

        for i, emb in enumerate(embeddings):
            if emb is None or not isinstance(emb, (list, np.ndarray)) or len(emb) == 0:
                valid_embeddings.append([0.0] * expected_dim)
            elif len(emb) != expected_dim:
                # Dimension mismatch (likely due to model change)
                # Pad or truncate to match expected_dim
                if len(emb) > expected_dim:
                    valid_embeddings.append(emb[:expected_dim])
                else:
                    valid_embeddings.append(list(emb) + [0.0] * (expected_dim - len(emb)))
            else:
                valid_embeddings.append(emb)
                
        return np.array(valid_embeddings, dtype=np.float32)

    def _embed_local(self, texts: List[str]) -> np.ndarray:
        return np.array(self._embed_tfidf(texts), dtype=np.float32)

    def _embed_openai(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(
            input=texts,
            model=self.model_name
        )
        return [data.embedding for data in response.data]

    def _embed_gemini(self, texts: List[str]) -> List[List[float]]:
        import google.generativeai as genai
        import time
        all_embeddings = []
        batch_size = 50
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            success = False
            retries = 3
            while not success and retries > 0:
                try:
                    result = genai.embed_content(
                        model=self.model_name,
                        content=batch,
                        task_type="clustering"
                    )
                    # Result['embedding'] can be a list of lists or a single list (if batch size 1)
                    embs = result.get('embedding', [])
                    
                    if len(batch) == 1:
                        # If batch was 1, it might return [x, y, z] instead of [[x, y, z]]
                        if embs and not isinstance(embs[0], (list, np.ndarray)):
                            all_embeddings.append(embs)
                        else:
                            all_embeddings.extend(embs)
                    else:
                        all_embeddings.extend(embs)
                        
                    success = True
                    if len(texts) > batch_size:
                        time.sleep(2) # Reduced sleep but kept for safety
                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower():
                        retries -= 1
                        print(f"Quota/Rate limit hit. Waiting 5 seconds... ({retries} retries left)")
                        time.sleep(5)
                    else:
                        print(f"Gemini Error: {e}")
                        break # Break retry loop
            
            if not success:
                print("Batch failed. Falling back to TF-IDF for this batch.")
                # Fallback for just this batch to maintain overall list length
                batch_tfidf = self._embed_tfidf(batch, dim=768)
                all_embeddings.extend(batch_tfidf)
        
        return all_embeddings

    def _embed_tfidf(self, texts: List[str], dim: int = 384) -> List[List[float]]:
        from sklearn.feature_extraction.text import TfidfVectorizer
        print(f"Running TF-IDF Vectorizer fallback (dim={dim})...")
        vectorizer = TfidfVectorizer(max_features=dim, stop_words='english')
        X = vectorizer.fit_transform(texts).toarray()
        
        # If TF-IDF found fewer features than requested dim, pad with zeros
        if X.shape[1] < dim:
            padding = np.zeros((X.shape[0], dim - X.shape[1]))
            X = np.hstack((X, padding))
            
        return X.tolist()

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
            "SELECT review_id, content FROM processed_reviews WHERE product_id = ? ORDER BY review_date DESC LIMIT 300",
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
    # Include all reviews with length >= 12
    df = df[df['content'].str.len() >= 12].reset_index(drop=True)
    print(f"After length filter: {len(df)}")

    # 3. Embedding
    client = EmbeddingClient()
    embeddings = client.get_embeddings(df['content'].tolist())

    # 4. Dimensionality Reduction (UMAP / TruncatedSVD on Cloud)
    if "RENDER" in os.environ or "FLY_APP_NAME" in os.environ or "VERCEL" in os.environ:
        print("Detected cloud deployment. Using TruncatedSVD for fast dimensionality reduction to prevent timeouts/OOM.")
        from sklearn.decomposition import TruncatedSVD
        reducer = TruncatedSVD(n_components=5, random_state=42)
        reduced_embeddings = reducer.fit_transform(embeddings)
    else:
        import umap
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
            min_cluster_size=max(5, min_cluster_size),
            min_samples=3,
            metric='euclidean',
            cluster_selection_method='eom'
        )
    else:
        # Fallback to DBSCAN if hdbscan is missing
        clusterer = DBSCAN(eps=1.2, min_samples=max(4, min_cluster_size // 2))

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
