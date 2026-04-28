"""Quick test: skip Phase 2 re-run, load DB directly, test Phase 3 with Groq."""
import os
import sys
import sqlite3
import pandas as pd

os.environ["GEMINI_API_KEY"] = ""  # Force Groq
sys.path.insert(0, ".")

# Load reviews directly from DB (skip Phase 2 re-run)
print("Loading reviews from DB...")
conn = sqlite3.connect("data/audit_log.db")
df = pd.read_sql_query(
    "SELECT review_id, content FROM processed_reviews WHERE product_id = 'Groww'",
    conn
)
conn.close()
print(f"Loaded {len(df)} reviews")

# Assign fake clusters for testing (just take top 3 groups by first word)
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 42

df = df[df['content'].str.len() >= 20].head(100).reset_index(drop=True)

# Simple mock clustering: assign cluster based on rating-like keywords
def simple_cluster(text):
    t = text.lower()
    if any(w in t for w in ["bad", "worst", "poor", "terrible", "scam"]):
        return 0
    elif any(w in t for w in ["good", "best", "great", "nice", "love"]):
        return 1
    elif any(w in t for w in ["charge", "fee", "brokerage", "commission"]):
        return 2
    return -1

df['cluster'] = df['content'].apply(simple_cluster)
non_noise = df[df['cluster'] != -1]
print(f"Mock clusters: {len(non_noise)} reviews in {non_noise['cluster'].nunique()} clusters")

# Run Phase 3
from src.phase_3.summarizer import run_summarization_pipeline
summaries = run_summarization_pipeline(df, product_name="Groww")

print(f"\n{'='*50}")
print(f"RESULTS: {len(summaries)} themes summarized")
print(f"{'='*50}")
for s in summaries:
    try:
        print(f"\n[{s.sentiment.upper()}] {s.theme_name} ({s.review_count} reviews)")
        print(f"  {s.description}")
        for ai in s.action_items[:2]:
            print(f"  -> {ai}")
        for q in s.quotes[:2]:
            safe = q.text[:80].encode('ascii', 'ignore').decode('ascii')
            print(f'  "{safe}..."')
    except:
        print(f"  (display error for cluster {s.cluster_id})")
