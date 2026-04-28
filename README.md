# Weekly Product Review Pulse System

An automated, agent-centric pipeline that transforms App Store and Google Play reviews into actionable weekly reports delivered via Google Workspace.

## 🚀 Quick Links
- **[Problem Statement](file:///c:/Users/himan/GrowwRevieweAI/docs/problemStatement.md)**
- **[Architecture](file:///c:/Users/himan/GrowwRevieweAI/docs/architecture.md)**
- **[Implementation Plan](file:///c:/Users/himan/GrowwRevieweAI/docs/implementationPlan.md)**

## 📂 Documentation Structure
```text
docs/
├── phases/                # Phase-specific evaluations & edge cases
│   ├── phase-0-foundations/
│   ├── phase-1-ingestion/
│   ├── phase-2-clustering/
│   ├── phase-3-summarization/
│   ├── phase-4-renderer/
│   ├── phase-5-docs-mcp/
│   ├── phase-6-gmail-mcp/
│   └── phase-7-orchestration/
│       ├── edge-cases.md
│       └── evaluations.md
├── architecture.md
├── implementationPlan.md
└── problemStatement.md
```

## 🛠️ Setup
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Configure your MCP servers for Google Workspace.
4. Set up environment variables in `.env`.

## 🤖 Running the System
```bash
# Preview clusters and analysis
python main.py --mode analyze

# Full execution (Append to Google Doc & Send Email)
python main.py --mode full
```
