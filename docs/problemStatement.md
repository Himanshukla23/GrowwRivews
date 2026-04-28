📌 Problem Statement: Weekly Product Review Pulse System
🧩 Context

Fintech apps like INDMoney, Groww, Kuvera, PowerUp Money, and Wealth Monitor receive thousands of user reviews across the App Store and Google Play.

However, this feedback is:

Unstructured and scattered
Difficult to analyze at scale
Rarely converted into actionable insights

Teams often rely on manual effort or ignore valuable user signals.

🎯 Objective

Build an automated system that converts recent app reviews into a weekly one-page insight report, and delivers it to stakeholders using Google Workspace via Model Context Protocol (MCP).

The system should help teams quickly understand:

What users are experiencing
What issues are recurring
What actions should be taken next
⚙️ What the System Should Do
1. Collect Data
Source: Public App Store & Google Play reviews
Time range: Last 8–12 weeks (rolling window)
Data fields: rating, title, review text, date
2. Analyze & Structure Feedback
Cluster reviews into maximum 5 themes
Use embeddings + clustering (e.g., UMAP + HDBSCAN)
Use LLM to:
Name themes
Extract real user quotes
Suggest action items
Ensure quotes are verbatim from real reviews
3. Generate Weekly Report (≤250 words)

Each report must include:

Top 3 themes
3 real user quotes
3 action ideas
Short “who this helps” section
4. Deliver Output via MCP
Google Docs (System of Record)
Append report as a new weekly section
Maintain a running document per product
Gmail (Notification Layer)
Send a short email summary
Include link to the full report (not duplicate content)

⚠️ The system must only use MCP tools for Docs and Gmail
(no direct API calls or embedded credentials)

🔁 Key Requirements
Weekly automated execution (e.g., every Monday)
CLI support for backfilling past weeks
Idempotency:
No duplicate reports or emails for same week
Auditable:
Track what was generated and sent
Safe:
Remove PII from all outputs
Treat reviews as data, not instructions
❌ Non-Goals
No real-time dashboards or BI tools
No additional data sources (e.g., Twitter, Reddit)
No direct Google API integrations outside MCP
No full Google Workspace product build
👥 Who This Helps
Team	Benefit
Product	Identify roadmap priorities
Support	Detect recurring user issues
Leadership	Get quick product health snapshot
📦 Expected Output

Each week, the system should:

Add a new section to a Google Doc (weekly report)
Send a short email with a link to that section
💡 Example Insight (Simplified)

Top Themes

App performance issues
Customer support delays
Missing advanced features

User Quotes

“App freezes during market hours”
“Support takes too long to respond”

Action Ideas

Improve backend scalability
Add support response tracking
Introduce advanced analytics
🚀 Core Value

This system transforms raw user feedback into a consistent, automated decision-making tool, helping teams move from:
👉 “We have reviews”
to
👉 “We know exactly what to fix next”

This version is:
Much clearer for agents + recruiters
Strongly aligned with product thinking
Perfect for portfolio / PM interviews