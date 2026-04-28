import sqlite3
import os
from pathlib import Path

def initialize_database(db_path="data/audit_log.db"):
    """
    Initializes the SQLite database with tables for reports and processed reviews.
    """
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Table to track weekly reports (Idempotency)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT NOT NULL,
            week_id TEXT NOT NULL, -- Format: YYYY-WW
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            doc_link TEXT,
            status TEXT,
            UNIQUE(product_id, week_id)
        )
    """)
    
    # Table to track processed reviews to avoid redundant clustering
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_reviews (
            review_id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            rating INTEGER,
            content TEXT,
            review_date TEXT,
            week_id TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {db_path}")

if __name__ == "__main__":
    # If run directly, initialize in the default location
    initialize_database()
