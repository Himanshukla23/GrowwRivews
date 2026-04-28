from pydantic import BaseModel, Field
import hashlib
import re
from datetime import datetime
from typing import Optional

class RawReview(BaseModel):
    source: str  # 'google_play' or 'app_store'
    external_id: str
    content: str
    rating: int
    review_date: datetime
    user_name: Optional[str] = None
    version: Optional[str] = None
    
    @property
    def sha1_id(self) -> str:
        """Generates a stable ID based on source and external ID."""
        unique_str = f"{self.source}:{self.external_id}"
        return hashlib.sha1(unique_str.encode()).hexdigest()

def scrub_pii(text: str) -> str:
    """Removes emails, phone numbers, and generic ID patterns."""
    # Email
    text = re.sub(r'\S+@\S+\.\S+', '[EMAIL_REMOVED]', text)
    # Phone (Generic 10-digit)
    text = re.sub(r'\b\d{10}\b', '[PHONE_REMOVED]', text)
    # Aadhaar/PAN like patterns (Generic 12-digit or 10-char alphanumeric)
    text = re.sub(r'\b\d{12}\b', '[ID_REMOVED]', text)
    return text

def has_emoji(text: str) -> bool:
    """Checks if text contains emojis."""
    # Simple check for common emoji ranges
    emoji_pattern = re.compile("["
        "\U00010000-\U0010FFFF"  # Supplemental Planes
        "]+", flags=re.UNICODE)
    return bool(emoji_pattern.search(text))

def is_valid_review(text: str) -> bool:
    """
    Applies user-requested filters:
    - No emojis
    - At least 4 words
    """
    if has_emoji(text):
        return False
    
    words = text.split()
    if len(words) < 4:
        return False
        
    return True
