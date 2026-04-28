"""
Phase 5: Google Docs Delivery
Appends the rendered Markdown report to a Google Doc for record-keeping.
Uses the Google Docs API via OAuth2.
"""

import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from googleapiclient.discovery import build
from dotenv import load_dotenv
from src.google_auth_helper import get_google_credentials
from src.phase_3.summarizer import ThemeSummary
from src.phase_4.renderer import _detect_audiences, _scrub_pii, _SENTIMENT_ICON

load_dotenv()


def build_doc_requests(
    summaries: List[ThemeSummary],
    product_name: str,
    total_reviews: int,
    start_index: int
) -> List[Dict[str, Any]]:
    """
    Builds a list of Google Docs batchUpdate requests to insert and style
    the report with proper headings, bold text, and bullet points.
    """
    requests = []
    
    full_text = ""
    styles = [] # list of (start, end, type, value)
    
    def add_text(text: str, p_style="NORMAL_TEXT", bold=False, bullet=False):
        nonlocal full_text
        start = start_index + len(full_text)
        full_text += text
        end = start_index + len(full_text)
        
        if p_style != "NORMAL_TEXT":
            styles.append((start, end, "p_style", p_style))
        if bold:
            styles.append((start, end, "bold", True))
        if bullet:
            styles.append((start, end, "bullet", True))

    now = datetime.now()
    week_id = f"{now.year}-W{now.isocalendar()[1]:02d}"
    date_str = now.strftime("%B %d, %Y")

    # Divider
    add_text("\n\n" + ("=" * 50) + "\n\n")
    
    # Header
    add_text(f"📊 Weekly Product Pulse — {product_name}\n", p_style="HEADING_1")
    add_text(f"Week: {week_id} | Date: {date_str}\n\n")
    
    # Overview
    add_text("Overview\n", p_style="HEADING_2")
    add_text(f"This report highlights critical user feedback and product friction points across {total_reviews} reviews to drive actionable product decisions.\n")
    audiences = _detect_audiences(summaries)
    add_text(f"Primary Stakeholders: {', '.join(audiences)}\n\n")

    # Key Metrics
    add_text("Key Metrics\n", p_style="HEADING_2")
    add_text(f"Total Reviews Analyzed: {total_reviews}\n", bullet=True)
    add_text(f"Themes Detected: {len(summaries)}\n\n", bullet=True)

    # Sort themes
    sorted_summaries = sorted(summaries, key=lambda s: s.review_count, reverse=True)
    top_themes = sorted_summaries[:5]
    
    add_text("Top Issues\n", p_style="HEADING_1")

    for idx, s in enumerate(top_themes, 1):
        icon = _SENTIMENT_ICON.get(s.sentiment, "⚪")
        safe_theme = _scrub_pii(s.theme_name)
        
        add_text(f"{icon} {idx}. {safe_theme} ({s.review_count} reviews)\n", p_style="HEADING_2")
        
        add_text("Problem Statement: ", bold=True)
        add_text(f"{_scrub_pii(s.problem_statement)}\n\n")
        
        add_text("Why it matters: ", bold=True)
        add_text(f"{_scrub_pii(s.why_this_matters)}\n\n")
        
        impact_icon = "⚠️ " if s.impact_level.lower() == "high" else ""
        sentiment_label = s.sentiment.capitalize()
        add_text("Sentiment Summary: ", bold=True)
        add_text(f"{impact_icon}{s.impact_level} Priority | {sentiment_label} Sentiment\n\n")
        
        if s.quotes:
            add_text("User Voices\n", p_style="HEADING_3")
            for q in s.quotes[:3]:
                add_text(f'"{_scrub_pii(q.text)}"\n', bullet=True)
            add_text("\n")

        if s.product_recommendations:
            add_text("Actionable Insights\n", p_style="HEADING_3")
            for item in s.product_recommendations[:3]:
                add_text(f"{_scrub_pii(item)}\n", bullet=True)
            add_text("\n")

    # Remaining Themes
    remaining = sorted_summaries[5:]
    if remaining:
        add_text("Other Themes\n", p_style="HEADING_2")
        for s in remaining:
            icon = _SENTIMENT_ICON.get(s.sentiment, "⚪")
            safe_theme = _scrub_pii(s.theme_name)
            add_text(f"{icon} {safe_theme} ({s.review_count} reviews)\n", bullet=True)
        add_text("\n")
        
    # Compile Requests
    # 1. Insert all text at once
    requests.append({
        "insertText": {
            "location": {"index": start_index},
            "text": full_text
        }
    })
    
    # 2. Apply styles
    for start, end, s_type, val in styles:
        if s_type == "p_style":
            requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": start, "endIndex": end},
                    "paragraphStyle": {"namedStyleType": val},
                    "fields": "namedStyleType"
                }
            })
        elif s_type == "bold":
            requests.append({
                "updateTextStyle": {
                    "range": {"startIndex": start, "endIndex": end},
                    "textStyle": {"bold": val},
                    "fields": "bold"
                }
            })
        elif s_type == "bullet":
            requests.append({
                "createParagraphBullets": {
                    "range": {"startIndex": start, "endIndex": end},
                    "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"
                }
            })

    return requests


def append_to_doc(
    summaries: List[ThemeSummary],
    product_name: str = "Groww",
    total_reviews: int = 0,
    doc_id: Optional[str] = None
) -> str:
    """
    Appends the structured report to a Google Doc using batchUpdate styles.
    """
    if doc_id is None:
        doc_id = os.getenv("GOOGLE_DOC_ID")

    if not doc_id or doc_id == "your_google_doc_id_here":
        raise ValueError(
            "GOOGLE_DOC_ID is not configured. Set it in your .env file."
        )

    creds = get_google_credentials()
    service = build("docs", "v1", credentials=creds)

    # Get end index of document
    doc = service.documents().get(documentId=doc_id).execute()
    end_index = doc["body"]["content"][-1]["endIndex"] - 1

    # Build and execute requests
    requests = build_doc_requests(summaries, product_name, total_reviews, end_index)

    # Save doc requests as an artifact
    import json
    now = datetime.now()
    artifact_dir = f"data/artifacts/{now.strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(artifact_dir, exist_ok=True)
    
    with open(f"{artifact_dir}/doc_requests.json", "w", encoding="utf-8") as f:
        json.dump(requests, f, indent=2)
    print(f"[Phase 5] Requests artifact saved to: {artifact_dir}/doc_requests.json")

    service.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": requests},
    ).execute()

    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"[Phase 5] Styled report appended to Google Doc: {doc_url}")
    return doc_url

