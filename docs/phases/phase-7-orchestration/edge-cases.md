# Edge Cases: Phase 7 (Orchestration)
*   **MCP Tool Disconnected**:
    *   *Scenario*: Google Workspace MCP server is down.
    *   *System Action*: Save report locally in `failed_delivery/` and retry later.
*   **Permission Denied**:
    *   *Scenario*: Revoked access to Google Doc.
    *   *System Action*: Log "Critical Delivery Failure" and fail the build.
*   **Doc ID Missing**:
    *   *Scenario*: Incorrect Google Doc ID in `.env`.
    *   *System Action*: Validate ID via `read` call before `append`.
