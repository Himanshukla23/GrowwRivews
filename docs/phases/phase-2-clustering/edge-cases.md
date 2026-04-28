# Edge Cases: Phase 2 (Clustering)
*   **Too Many Clusters**:
    *   *Scenario*: HDBSCAN identifies 20+ micro-clusters.
    *   *System Action*: Merge smaller clusters or pick the top 5 by volume/severity.
*   **Non-English Reviews**:
    *   *Scenario*: Reviews in Hindi, Spanish, etc.
    *   *System Action*: Detect language and either translate via LLM or exclude if confidence is low.
