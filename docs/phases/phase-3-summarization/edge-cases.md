# Edge Cases: Phase 3 (Summarization)
*   **LLM Hallucination**:
    *   *Scenario*: LLM generates a quote that doesn't exist.
    *   *System Action*: Validation step to search the quote in the raw data; reject if not found.
*   **Malicious Injection**:
    *   *Scenario*: User writes a review like "Ignore previous instructions."
    *   *System Action*: Treat all review text as data (fenced strings).
