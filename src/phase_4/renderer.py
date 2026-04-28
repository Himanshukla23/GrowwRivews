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
# Sentiment Emoji Helper
# ---------------------------------------------------------------------------

_SENTIMENT_ICON = {
    "positive": "🟢",
    "negative": "🔴",
    "mixed":    "🟡",
}


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
    Render a professional, PII-free Markdown report from theme summaries.

    The report is designed to be ≤ 250 words so it stays scannable for
    busy stakeholders.

    Args:
        summaries: List of ThemeSummary from Phase 3.
        product_name: Product name for the header.
        week_id: ISO week identifier (e.g. "2026-W17"). Auto-generated if None.
        total_reviews: Total number of reviews analyzed (pre-filter count).

    Returns:
        A complete Markdown string ready for Google Docs or email.
    """
    if week_id is None:
        now = datetime.now()
        week_id = f"{now.year}-W{now.isocalendar()[1]:02d}"

    date_str = datetime.now().strftime("%B %d, %Y")

    # --- Header ---
    lines = [
        f"# 📊 Weekly Product Pulse — {product_name}",
        f"**Subtitle:** Week {week_id} | {date_str}  ",
        "",
        "### 📝 Overview",
        f"This week's analysis of **{total_reviews} user reviews** highlights **{len(summaries)} key areas of focus** for the {product_name} platform.",
        "",
        "### 📈 Key Metrics",
        f"- **Total Reviews Analyzed:** {total_reviews}",
        f"- **Top Themes Detected:** {len(summaries)} Primary Issues",
    ]

    # --- Who This Helps ---
    audiences = _detect_audiences(summaries)
    lines.append(f"- **Primary Stakeholders:** {', '.join(audiences)}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🔍 Top Issues & Themes")
    lines.append("")

    # --- Theme Sections (top 5 by review count) ---
    sorted_summaries = sorted(summaries, key=lambda s: s.review_count, reverse=True)
    top_themes = sorted_summaries[:5]

    lines.append("---")
    lines.append("")

    for idx, s in enumerate(top_themes, 1):
        icon = _SENTIMENT_ICON.get(s.sentiment, "⚪")
        safe_theme = _scrub_pii(s.theme_name)
        safe_problem = _scrub_pii(s.problem_statement)
        safe_why = _scrub_pii(s.why_this_matters)
        impact = s.impact_level

        # Add warning icon if high impact
        impact_icon = "⚠️ " if impact.lower() == "high" else ""

        lines.append(f"### {icon} {idx}. {safe_theme} ({s.review_count} reviews)")
        lines.append(f"**Problem Statement:** {safe_problem}")
        lines.append("")
        lines.append(f"**💡 Why this matters:**")
        lines.append(f"{safe_why}")
        lines.append("")
        lines.append(f"**{impact_icon}Impact Level:** {impact}")
        lines.append("")

        # Product Recommendations
        if s.product_recommendations:
            lines.append("**🎯 Product Recommendations:**")
            for item in s.product_recommendations[:2]:
                safe_item = _scrub_pii(item)
                lines.append(f"- {safe_item}")
            lines.append("")

        # Quotes
        if s.quotes:
            lines.append("**🗣️ User Voices:**")
            for q in s.quotes[:2]:
                safe_quote = _scrub_pii(q.text)
                lines.append(f'> *"{safe_quote}"*')
            lines.append("")

        lines.append("---")
        lines.append("")

    # --- Remaining themes as a compact list ---
    remaining = sorted_summaries[5:]
    if remaining:
        lines.append("---")
        lines.append("")
        lines.append("### Other Themes")
        for s in remaining:
            icon = _SENTIMENT_ICON.get(s.sentiment, "⚪")
            safe_theme = _scrub_pii(s.theme_name)
            lines.append(f"- {icon} **{safe_theme}** ({s.review_count} reviews)")
        lines.append("")

    # --- Footer ---
    lines.append("---")
    lines.append(f"*Generated by Weekly Product Pulse System — {date_str}*")

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
