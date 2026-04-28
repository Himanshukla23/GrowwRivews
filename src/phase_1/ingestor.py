import os
import json
import sqlite3
from datetime import datetime
from typing import List
from src.phase_1.playstore import fetch_playstore_reviews
from src.phase_1.appstore import fetch_appstore_reviews
from src.phase_1.models import RawReview

def save_to_db(reviews: List[RawReview], db_path="data/audit_log.db"):
    """Saves/Updates reviews in the database using SHA1 IDs."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Ensure table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_reviews (
            review_id TEXT PRIMARY KEY,
            product_id TEXT,
            rating INTEGER,
            content TEXT,
            review_date TEXT
        )
    """)
    
    new_count = 0
    for r in reviews:
        sha1 = r.sha1_id
        # Dedup-upsert
        cursor.execute("""
            INSERT INTO processed_reviews (review_id, product_id, rating, content, review_date)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(review_id) DO UPDATE SET
                content = excluded.content,
                rating = excluded.rating
        """, (sha1, 'Groww', r.rating, r.content, r.review_date.isoformat()))
        if cursor.rowcount > 0:
            new_count += 1
            
    conn.commit()
    conn.close()
    return new_count

def save_snapshot(reviews: List[RawReview], product: str):
    """Saves a JSONL snapshot for audit purposes."""
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_dir = f"data/raw/{product}"
    os.makedirs(snapshot_dir, exist_ok=True)
    
    snapshot_path = os.path.join(snapshot_dir, f"{run_id}.jsonl")
    
    with open(snapshot_path, 'w', encoding='utf-8') as f:
        for r in reviews:
            f.write(json.dumps(r.model_dump(), default=str) + "\n")
            
    return snapshot_path

def run_ingestion(product_name="Groww", play_id="com.nextbillion.groww", apple_id="1404871703", weeks=12):
    """Orchestrates the full ingestion process."""
    print(f"--- Ingestion Start: {product_name} ---")
    
    # 1. Fetch
    ps_reviews = fetch_playstore_reviews(play_id, weeks=weeks)
    as_reviews = fetch_appstore_reviews(product_name.lower(), apple_id, weeks=weeks)
    
    all_reviews = ps_reviews + as_reviews
    
    if not all_reviews:
        print("No new reviews found.")
        return
        
    # 2. Audit Snapshot
    snapshot_path = save_snapshot(all_reviews, product_name)
    print(f"Snapshot saved at: {snapshot_path}")
    
    # 3. Save to DB
    new_inserts = save_to_db(all_reviews)
    print(f"DB Sync Complete. Processed {len(all_reviews)} reviews ({new_inserts} new/updated).")
    print(f"--- Ingestion End ---")

if __name__ == "__main__":
    run_ingestion()
