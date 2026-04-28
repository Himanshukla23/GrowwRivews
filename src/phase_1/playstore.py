from google_play_scraper import reviews, Sort
from datetime import datetime, timedelta
from typing import List
from src.phase_1.models import RawReview, scrub_pii, is_valid_review
from langdetect import detect, DetectorFactory

# Ensure consistent language detection
DetectorFactory.seed = 0

def fetch_playstore_reviews(app_id: str, weeks: int = 12) -> List[RawReview]:
    """
    Fetches reviews from Google Play Store for the given app_id.
    Filters by:
    - Time window (weeks)
    - Language (English only)
    - Word count (>= 4)
    - No Emojis
    """
    all_raw_reviews = []
    cutoff_date = datetime.now() - timedelta(weeks=weeks)
    
    # Fetching reviews in batches
    continuation_token = None
    stop_fetching = False
    
    print(f"Fetching Play Store reviews for {app_id}...")
    
    while not stop_fetching:
        result, continuation_token = reviews(
            app_id,
            lang='en', # Built-in lang filter
            country='in',
            sort=Sort.NEWEST,
            count=100,
            continuation_token=continuation_token
        )
        
        if not result:
            break
            
        for r in result:
            review_date = r['at']
            if review_date < cutoff_date:
                stop_fetching = True
                break
            
            content = r['content']
            
            # Apply user filters
            if not is_valid_review(content):
                continue
                
            # Extra language check for accuracy
            try:
                if detect(content) != 'en':
                    continue
            except:
                continue # Skip if lang detection fails
                
            # Scrub PII before creating model
            clean_content = scrub_pii(content)
            
            all_raw_reviews.append(RawReview(
                source='google_play',
                external_id=r['reviewId'],
                content=clean_content,
                rating=r['score'],
                review_date=review_date,
                user_name=r['userName'],
                version=r.get('reviewCreatedVersion')
            ))
            
        if not continuation_token:
            break
            
    print(f"Fetched {len(all_raw_reviews)} valid Play Store reviews.")
    return all_raw_reviews
