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
from src.phase_4.renderer import _detect_audiences, _scrub_pii

load_dotenv()


def build_doc_requests(
    summaries: List[ThemeSummary],
    product_name: str,
    total_reviews: int,
    start_index: int,
) -> List[Dict[str, Any]]:
    """
    Builds professional Google Docs batchUpdate requests with a corporate structure.
    No emojis, clear hierarchy, and focus on actionable insights.
    """
    requests = []
    
    full_text = ""
    styles = [] # list of (start, end, type, value)
    
    def add_text(text: str, p_style="NORMAL_TEXT", bold=False, indent=0):
        nonlocal full_text
        start = start_index + len(full_text)
        
        # Apply manual indentation if requested
        prefix = "    " * indent
        text_with_indent = prefix + text
        
        full_text += text_with_indent
        end = start_index + len(full_text)
        
        if p_style != "NORMAL_TEXT":
            styles.append((start, end, "p_style", p_style))
        if bold:
            styles.append((start, end, "bold", True))

    now = datetime.now()
    week_id = f"{now.year}-W{now.isocalendar()[1]:02d}"
    date_str = now.strftime("%B %d, %Y")

    # --- Header Section ---
    add_text(f"PRODUCT INTELLIGENCE REPORT: {product_name}\n", p_style="HEADING_1")
    add_text(f"REPORTING PERIOD: WEEK {week_id} | DATE: {date_str}\n", bold=True)
    add_text("-" * 60 + "\n\n")
    
    # --- Section 1: Executive Summary ---
    add_text("1. EXECUTIVE SUMMARY\n", p_style="HEADING_2")
    add_text(f"This intelligence report provides a consolidated analysis of {total_reviews} user feedback entries. ")
    add_text(f"The primary objective is to identify systemic friction points and strategic opportunities for the {product_name} ecosystem.\n\n")
    
    audiences = _detect_audiences(summaries)
    add_text("STAKEHOLDER DISTRIBUTION: ", bold=True)
    add_text(f"{', '.join(audiences)}\n\n")

    # --- Section 2: Key Performance Metrics ---
    add_text("2. KEY PERFORMANCE METRICS\n", p_style="HEADING_2")
    add_text(f"2.1 Total Feedback Volume: {total_reviews}\n", indent=1)
    add_text(f"2.2 Distinct Themes Identified: {len(summaries)}\n", indent=1)
    
    negative_themes = [s for s in summaries if s.sentiment == "negative"]
    negative_pct = (len(negative_themes) / len(summaries) * 100) if summaries else 0
    add_text(f"2.3 Critical Sentiment Concentration: {negative_pct:.1f}%\n\n", indent=1)

    # --- Section 3: Detailed Theme Analysis ---
    add_text("3. PRIORITIZED THEME ANALYSIS\n", p_style="HEADING_1")
    add_text("-" * 60 + "\n\n")

    # Sort themes by impact and count
    sorted_summaries = sorted(summaries, key=lambda s: s.review_count, reverse=True)
    top_themes = sorted_summaries[:5]

    for idx, s in enumerate(top_themes, 1):
        safe_theme = _scrub_pii(s.theme_name).upper()
        sentiment_label = s.sentiment.upper()
        
        # Heading for the theme
        add_text(f"3.{idx} THEME: {safe_theme} ({s.review_count} CASES)\n", p_style="HEADING_2")
        
        # Summary
        add_text("    A. SUMMARY: ", bold=True)
        add_text(f"{_scrub_pii(s.problem_statement)}\n")
        
        # Strategic Context
        add_text("    B. STRATEGIC CONTEXT: ", bold=True)
        add_text(f"{_scrub_pii(s.why_this_matters)}\n")
        
        # Operational Metrics
        priority = "URGENT" if s.impact_level.lower() == "high" else s.impact_level.upper()
        add_text(f"    C. OPERATIONAL IMPACT: {priority} | SENTIMENT: {sentiment_label}\n\n", bold=True)
        
        # Direct Feedback
        if s.quotes:
            add_text("    REPRESENTATIVE FEEDBACK:\n", bold=True)
            for q_idx, q in enumerate(s.quotes[:2], 1):
                add_text(f"        {q_idx}) \"{_scrub_pii(q.text)}\"\n")
            add_text("\n")

        # Recommended Action Plan
        if s.product_recommendations:
            add_text("    RECOMMENDED ACTION PLAN:\n", bold=True)
            for r_idx, item in enumerate(s.product_recommendations[:3], 1):
                add_text(f"        {r_idx}. {_scrub_pii(item)}\n")
            add_text("\n")
        
        add_text("-" * 40 + "\n\n")

    # --- Section 4: Secondary Observations ---
    remaining = sorted_summaries[5:]
    if remaining:
        add_text("4. SECONDARY OBSERVATIONS\n", p_style="HEADING_2")
        for s_idx, s in enumerate(remaining, 1):
            safe_theme = _scrub_pii(s.theme_name)
            add_text(f"4.{s_idx} {safe_theme} ({s.review_count} cases)\n", indent=1)
        add_text("\n")
        
    add_text("\n" + ("=" * 60) + "\n")
    add_text(f"DOCUMENT GENERATED BY PULSE INTELLIGENCE SYSTEMS | {date_str}\n")
    add_text("CONFIDENTIAL - FOR INTERNAL DISTRIBUTION ONLY")

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

    return requests


def append_to_doc(
    summaries: List[ThemeSummary],
    product_name: str = "Groww",
    total_reviews: int = 0,
    doc_id: Optional[str] = None
) -> str:
    """
    Clears the document and inserts a professional structured report.
    """
    if doc_id is None:
        doc_id = os.getenv("GOOGLE_DOC_ID")

    if not doc_id or doc_id == "your_google_doc_id_here":
        raise ValueError(
            "GOOGLE_DOC_ID is not configured. Set it in your .env file."
        )

    creds = get_google_credentials()
    service = build("docs", "v1", credentials=creds)

    # 1. Get current document state
    doc = service.documents().get(documentId=doc_id).execute()
    end_index = doc["body"]["content"][-1]["endIndex"] - 1

    requests = []

    # 2. Clear document if it has content
    if end_index > 1:
        requests.append({
            "deleteContentRange": {
                "range": {
                    "startIndex": 1,
                    "endIndex": end_index
                }
            }
        })

    # 3. Build and execute insert requests
    new_report_requests = build_doc_requests(summaries, product_name, total_reviews, 1)
    requests.extend(new_report_requests)

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
    print(f"[Phase 5] Professional report delivered to Google Doc: {doc_url}")
    return doc_url

