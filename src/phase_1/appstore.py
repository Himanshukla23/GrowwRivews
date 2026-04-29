from app_store_scraper import AppStore
from datetime import datetime, timedelta
from typing import List
from src.phase_1.models import RawReview, scrub_pii, is_valid_review
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0

def fetch_appstore_reviews(app_name: str, app_id: str, weeks: int = 12, max_reviews: int = 200) -> List[RawReview]:
    """
    Fetches reviews from Apple App Store.
    Note: AppStore scraper works slightly differently (paginated).
    """
    all_raw_reviews = []
    cutoff_date = datetime.now() - timedelta(weeks=weeks)
    
    app = AppStore(country='in', app_name=app_name, app_id=app_id)
    
    print(f"Fetching App Store reviews for {app_name}...")
    
    # app.review() fetches reviews and stores them in app.reviews
    # We limit to max_reviews to avoid excessive memory usage
    app.review(how_many=max_reviews)
    
    for r in app.reviews:
        review_date = r['date']
        if review_date < cutoff_date:
            continue
            
        content = r['review']
        
        # Apply filters
        if not is_valid_review(content):
            continue
            
        try:
            if detect(content) != 'en':
                continue
        except:
            continue
            
        clean_content = scrub_pii(content)
        
        all_raw_reviews.append(RawReview(
            source='app_store',
            external_id=str(r['date'].timestamp()), # AppStore scraper doesn't provide unique ID, using timestamp
            content=clean_content,
            rating=r['rating'],
            review_date=review_date,
            user_name=r['userName'],
            version=r.get('version')
        ))
        
        if len(all_raw_reviews) >= max_reviews:
            break
            
    print(f"Fetched {len(all_raw_reviews)} valid App Store reviews.")
    return all_raw_reviews
