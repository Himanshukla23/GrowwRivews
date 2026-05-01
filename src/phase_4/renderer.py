"""
Phase 4: Renderer
Formats the analyzed theme data into a professional, PII-free Markdown report.
The report is kept concise (≤ 250 words) and dynamically selects
"Who this helps" based on the detected themes.
"""

import re
from datetime import datetime
from typing import List, Optional
from src.phase_3.summarizer import ThemeSummary, Quote, _PII_PATTERNS


# ---------------------------------------------------------------------------
# PII Final Sweep
# ---------------------------------------------------------------------------

def _scrub_pii(text: str) -> str:
    """Final PII scrub on any text before it enters the report."""
    for pat in _PII_PATTERNS:
        text = pat.sub("[REDACTED]", text)
    return text


# ---------------------------------------------------------------------------
# "Who This Helps" Dynamic Mapping
# ---------------------------------------------------------------------------

# Maps keywords found in theme names / descriptions to stakeholder teams
_THEME_TO_AUDIENCE = {
    "charge":      "Finance & Pricing",
    "brokerage":   "Finance & Pricing",
    "fee":         "Finance & Pricing",
    "price":       "Finance & Pricing",
    "cost":        "Finance & Pricing",
    "ui":          "Design & UX",
    "design":      "Design & UX",
    "interface":   "Design & UX",
    "layout":      "Design & UX",
    "navigation":  "Design & UX",
    "bug":         "Engineering",
    "crash":       "Engineering",
    "error":       "Engineering",
    "slow":        "Engineering",
    "performance": "Engineering",
    "loading":     "Engineering",
    "login":       "Engineering",
    "otp":         "Engineering",
    "support":     "Customer Support",
    "help":        "Customer Support",
    "response":    "Customer Support",
    "complaint":   "Customer Support",
    "resolve":     "Customer Support",
    "beginner":    "Product & Growth",
    "onboard":     "Product & Growth",
    "learn":       "Product & Growth",
    "feature":     "Product Management",
    "update":      "Product Management",
    "withdraw":    "Operations",
    "payment":     "Operations",
    "deposit":     "Operations",
    "kyc":         "Compliance",
    "security":    "Security & Trust",
    "fraud":       "Security & Trust",
    "scam":        "Security & Trust",
}


def _detect_audiences(summaries: List[ThemeSummary]) -> List[str]:
    """
    Dynamically detect which teams/roles benefit from this report
    based on the themes found.
    """
    audiences = set()

    for s in summaries:
        # Check theme name and problem statement for keyword matches
        searchable = f"{s.theme_name} {s.problem_statement}".lower()
        for keyword, audience in _THEME_TO_AUDIENCE.items():
            if keyword in searchable:
                audiences.add(audience)

        # Also include any who_this_helps the LLM explicitly set
        for wth in s.who_this_helps:
            audiences.add(wth)

    # Always include Product Management
    audiences.add("Product Management")

    return sorted(audiences)


# ---------------------------------------------------------------------------
# Core Renderer
# ---------------------------------------------------------------------------

def render_report(
    summaries: List[ThemeSummary],
    product_name: str = "Groww",
    week_id: Optional[str] = None,
    total_reviews: int = 0,
) -> str:
    """
    Render a professional, corporate-grade Markdown report.
    Focuses on strategic intelligence and operational impact.
    """
    if week_id is None:
        now = datetime.now()
        week_id = f"{now.year}-W{now.isocalendar()[1]:02d}"

    date_str = datetime.now().strftime("%B %d, %Y")

    # --- Header Section ---
    lines = [
        f"# Product Intelligence Report: {product_name}",
        f"**Reporting Period:** Week {week_id} | **Date:** {date_str}  ",
        "",
        "## 1. Executive Summary",
        f"Analysis of **{total_reviews} feedback entries** identifying **{len(summaries)} key intelligence themes**.",
        "This report prioritizes systemic friction points based on volume and operational impact.",
        "",
        "## 2. Key Intelligence Metrics",
        f"- **Total Analysis Volume:** {total_reviews} items",
        f"- **Thematic Density:** {len(summaries)} active themes",
    ]

    # --- Stakeholder Mapping ---
    audiences = _detect_audiences(summaries)
    lines.append(f"- **Primary Distribution:** {', '.join(audiences)}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 3. Detailed Strategic Analysis")
    lines.append("")

    # --- Thematic Breakdown ---
    sorted_summaries = sorted(summaries, key=lambda s: s.review_count, reverse=True)
    top_themes = sorted_summaries[:5]

    for idx, s in enumerate(top_themes, 1):
        safe_theme = _scrub_pii(s.theme_name).upper()
        sentiment = s.sentiment.upper()
        priority = "URGENT" if s.impact_level.lower() == "high" else s.impact_level.upper()

        lines.append(f"### {idx}. {safe_theme} ({s.review_count} cases)")
        lines.append(f"**Thematic Summary:** {_scrub_pii(s.problem_statement)}")
        lines.append("")
        lines.append(f"**Strategic Context:**")
        lines.append(f"{_scrub_pii(s.why_this_matters)}")
        lines.append("")
        lines.append(f"**Operational Impact:** {priority} | **Sentiment:** {sentiment}")
        lines.append("")

        # Action Items
        if s.product_recommendations:
            lines.append("**Recommended Action Plan:**")
            for item in s.product_recommendations[:2]:
                lines.append(f"- {_scrub_pii(item)}")
            lines.append("")

        # User Voices
        if s.quotes:
            lines.append("**Direct Stakeholder Feedback:**")
            for q in s.quotes[:2]:
                lines.append(f'> *"{_scrub_pii(q.text)}"*')
            lines.append("")

        lines.append("---")
        lines.append("")

    # --- Secondary Observations ---
    remaining = sorted_summaries[5:]
    if remaining:
        lines.append("## 4. Secondary Observations")
        for s in remaining:
            safe_theme = _scrub_pii(s.theme_name)
            lines.append(f"- **{safe_theme}** ({s.review_count} cases)")
        lines.append("")

    # --- Footer ---
    lines.append("---")
    lines.append(f"*Document generated by Pulse Intelligence Systems | {date_str}*")
    lines.append("*Confidential - For Internal Distribution Only*")

    report = "\n".join(lines)
    return report


# ---------------------------------------------------------------------------
# Standalone execution for testing
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

    # Create mock data to test rendering without running Phases 1-3
    mock_summaries = [
        ThemeSummary(
            cluster_id=0,
            theme_name="High Brokerage Charges",
            problem_statement="Users are frustrated with the high brokerage fees, especially on F&O trades.",
            why_this_matters="Trust is the core currency. Perceived hidden fees directly cause churn to competitors.",
            impact_level="High",
            sentiment="negative",
            review_count=1214,
            product_recommendations=["Review F&O fee structure", "Add Estimated Fees tooltip in-app"],
            quotes=[
                Quote(text="too much brokerage charges on FNO", review_id="r001"),
                Quote(text="brokerage is eating all my profits", review_id="r002"),
            ],
            who_this_helps=["Product", "Finance"],
        ),
        ThemeSummary(
            cluster_id=1,
            theme_name="Great Beginner Experience",
            problem_statement="New users appreciate the clean UI and easy onboarding process.",
            why_this_matters="Smooth onboarding significantly lowers customer acquisition cost and boosts referral rates.",
            impact_level="Medium",
            sentiment="positive",
            review_count=738,
            product_recommendations=["Continue investing in onboarding flow"],
            quotes=[
                Quote(text="best app for beginners, UI is user friendly", review_id="r003"),
            ],
            who_this_helps=["Product", "Design"],
        ),
        ThemeSummary(
            cluster_id=2,
            theme_name="Poor Customer Support",
            problem_statement="Multiple users report slow or unresponsive customer support.",
            why_this_matters="Unresolved issues during high-volatility trading days lead to severe brand damage and 1-star reviews.",
            impact_level="High",
            sentiment="negative",
            review_count=435,
            product_recommendations=["Reduce support response SLA", "Add live chat option"],
            quotes=[
                Quote(text="customer support not good very poor service", review_id="r004"),
                Quote(text="complaint not resolved after multiple calls", review_id="r005"),
            ],
            who_this_helps=["Support", "Operations"],
        ),
    ]

    report = render_report(
        summaries=mock_summaries,
        product_name="Groww",
        total_reviews=3774,
    )

    print(report)

    # Count words
    word_count = len(report.split())
    print(f"\n--- Word count: {word_count} ---")
