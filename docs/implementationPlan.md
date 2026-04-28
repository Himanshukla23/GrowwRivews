# Implementation Plan: Weekly Product Review Pulse System

This plan follows the [Detailed Architecture](file:///c:/Users/himan/GrowwRevieweAI/docs/architecture.md) and is organized into 8 distinct phases for clear, modular development.

---

## Phase 0: Foundations
**Goal**: Establish the project environment and persistent storage.
- **Tasks**:
    1.  Initialize directory structure and `requirements.txt`.
    2.  Set up `.env.example` with required keys (MCP, OpenAI/Gemini).
    3.  Implement `src/phase_0/database.py` for SQLite schema initialization.
- **Exit Criteria**:
    - Database initialized with `reports` and `reviews` tables.
    - Environment variables validated.

---

## Phase 1: Review Ingestion
**Goal**: Reliably pull and store 8–12 weeks of reviews for any supported product.
- **Scope**:
    - `src/phase_1/appstore.py`: iTunes RSS `customerreviews` feed, paginated (1..10), country-configurable.
    - `src/phase_1/playstore.py`: `google-play-scraper` wrapper with time-bounded pagination.
    - **Data Model**: Unified `RawReview` Pydantic model; stable `id = sha1(source + external_id)`.
    - **Persistence**: Dedup-upsert into `reviews` table.
    - **Safety**: Regex PII scrubber (emails, phone numbers, Aadhaar-like) applied to body **before** persistence.
    - **Audit**: Raw JSON snapshot written to `data/raw/{product}/{run_id}.jsonl`.
    - **CLI**: `pulse ingest --product groww --weeks 10`.
- **Exit Criteria**:
    - Fixture-replay test: feeding canned HTTP responses produces a deterministic reviews snapshot.
    - Smoke test: Running for "groww" returns ≥ 200 reviews.
    - Idempotency: Re-running within a minute is a no-op (0 inserts).

---

## Phase 2: Embeddings & Clustering
**Goal**: Turn a pile of reviews into a small set of coherent clusters with representative members.
- **Scope**:
    - `src/phase_2/clustering.py`:
        - **Pre-filtering**: Language filter (keep `en`), length filter (≥ 20 chars).
        - **Embedding Interface**: Support for OpenAI (`text-embedding-3-small`) and local (`bge-small-en-v1.5`).
        - **Caching**: Batch embed with on-disk cache keyed by `sha1(text)`.
        - **ML Pipeline**: UMAP (n_components=15, metric=cosine) + HDBSCAN (min_cluster_size=8, configurable).
- **Exit Criteria**:
    - >80% of reviews assigned to a non-noise cluster in test datasets.

---

## Phase 3: Summarization
**Goal**: Use LLMs to transform clusters into meaningful themes and quotes.
- **Tasks**:
    1.  Design LLM prompts for theme naming and action item generation.
    2.  Implement quote extraction logic (verbatim) in `src/phase_3/summarizer.py`.
    3.  Add validation to ensure every quote exists in the original review data.

---

## Phase 4: Renderer
**Goal**: Format the analyzed data into a professional, PII-free Markdown report.
- **Tasks**:
    1.  Design the Markdown template in `src/phase_4/renderer.py` (≤ 250 words).
    2.  Add logic to dynamically select "Who this helps" based on detected themes.

---

## Phase 5: Google Docs MCP
**Goal**: Establish a secure connection to Google Docs for record-keeping.
- **Tasks**:
    1.  Implement `src/phase_5/docs_delivery.py` using MCP `google_docs.append_text`.
    2.  Verify formatting consistency when appending new sections to an existing Doc.

---

## Phase 6: Gmail MCP
**Goal**: Implement the notification layer to alert stakeholders.
- **Tasks**:
    1.  Implement `src/phase_6/gmail_delivery.py` using MCP `gmail.send_message`.
    2.  Design a concise email template that links to the Google Doc.

---

## Phase 7: Orchestration
**Goal**: Tie all modules together into a production-ready autonomous system.
- **Tasks**:
    1.  Finalize `main.py` to orchestrate the end-to-end flow.
    2.  Implement the **Idempotency Check** (Audit Log) to prevent duplicate runs.
    3.  Create the automation guide (Cron/GitHub Actions) in `docs/phases/phase-7-orchestration/`.
