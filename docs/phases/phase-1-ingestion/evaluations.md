# Evaluations: Phase 1 (Ingestion)
| Metric | Verification Method | Target |
| :--- | :--- | :--- |
| **Data Coverage** | Run `ingestor.py` for a popular app (e.g., "Groww"). | Successfully fetch >500 reviews. |
| **Window Integrity** | Check the `date` field of fetched reviews. | All reviews must be within the last 84 days. |
| **Schema Accuracy** | Inspect the `List[dict]` output. | Must contain `rating`, `text`, and `date`. |
