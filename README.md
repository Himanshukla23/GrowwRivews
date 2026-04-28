# Weekly Product Review Pulse System

An automated, agent-centric pipeline that transforms App Store and Google Play reviews into actionable weekly reports delivered via Google Workspace, complete with a beautiful Next.js frontend dashboard.

## 🚀 Quick Links
- **[Problem Statement](docs/problemStatement.md)**
- **[Architecture](docs/architecture.md)**
- **[Implementation Plan](docs/implementationPlan.md)**

## 📂 Project Structure
```text
GrowwRevieweAI/
├── frontend/              # Next.js 15 App Router Frontend Dashboard
├── src/                   # FastAPI Backend & AI Pipeline Source
├── docs/                  # Architecture & Phase documentation
├── data/                  # Local SQLite DB & Outputs
├── app.py                 # FastAPI Application Entrypoint
├── main.py                # Pipeline CLI Entrypoint
└── requirements.txt       # Backend dependencies
```

## 🛠️ Setup

### Backend (FastAPI & Pipeline)
1. Clone the repository.
2. Install Python dependencies: `pip install -r requirements.txt`.
3. Configure your MCP servers for Google Workspace if using MCP features.
4. Set up environment variables by copying `.env.example` to `.env` and filling in your API keys (Gemini, Groq, Google Workspace IDs).
5. Place your Google OAuth `credentials.json` in the root folder.

### Frontend (Next.js)
1. Navigate to the frontend directory: `cd frontend`
2. Install Node.js dependencies: `npm install`

## 🤖 Running the System

### 1. Start the Backend API
From the root directory, start the FastAPI server:
```bash
python app.py
# The API will be available at http://localhost:8000
```

### 2. Start the Frontend Dashboard
Open a new terminal, navigate to the `frontend` folder and start the dev server:
```bash
cd frontend
npm run dev
# The Dashboard will be available at http://localhost:3000
```

### 3. CLI Mode (Alternative)
You can also run the reporting pipeline directly from the command line without the UI:
```bash
# Preview clusters and analysis
python main.py --mode analyze

# Full execution (Append to Google Doc & Send Email)
python main.py --mode full
```
