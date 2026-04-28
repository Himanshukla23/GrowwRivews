# Evaluations: Phase 7 (Orchestration)
| Metric | Verification Method | Target |
| :--- | :--- | :--- |
| **Idempotency** | Run the system twice for the same week. | Second run must exit with "Already processed". |
| **End-to-End Success** | Run `python main.py --mode full`. | Complete cycle completes without errors. |
| **Doc Formatting** | Inspect the Google Doc via UI. | New section must have header and clean formatting. |
| **Email Clarity** | Check the Gmail notification. | Must contain correct summary and link. |
