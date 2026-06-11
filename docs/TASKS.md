# TASKS — Phase 0 and RAG work plan

This file captures the current team task direction. It is intentionally module-based so work can be divided, but all work must integrate into one shared API contract.

## Execution order

Do not start with four developers coding separate RAG pieces immediately. First create the base structure.

1. Create `development` branch from `main`.
2. Create one setup branch from `development`.
3. Scaffold the Python project with `uv`.
4. Add the shared package/app structure.
5. Add stable contracts and smoke test.
6. Merge setup branch into `development`.
7. Then split RAG work into feature branches.
8. Merge feature branches into `development` through PRs.
9. Merge `development` into `main` only when smoke tests pass.

## Branch model

```text
main
  stable repo docs and reviewed working code

development
  integration branch for active skeleton work

feature/setup-uv-project
  project structure, uv, base dependencies, smoke test

feature/rag-extractors
  PDF/TXT/CSV extractors and dispatcher

feature/rag-locators-idempotency
  locator validation, idempotent ingest, collection scoping

feature/rag-chunk-embed-store
  chunker, embedder, Chroma/local store adapter

feature/rag-retrieval-api
  retrieval query, score threshold, /ingest endpoint
```

Avoid one shared `rag` branch where everyone commits directly. That creates merge pain and hidden overwrites.

## Phase 0 setup task

Owner: one developer initially. Others should wait for this branch to merge before writing module code.

### Goal

Create a runnable Python skeleton that all RAG tasks can plug into.

### Tasks

- [ ] Create Python project with `uv`
- [ ] Add `.python-version`, `pyproject.toml`, `uv.lock`
- [ ] Add `.gitignore` for `.venv`, `.env`, caches, build artifacts
- [ ] Add base folders:
  - `apps/api`
  - `apps/demo`
  - `packages/contracts`
  - `packages/retrieval`
  - `packages/agent_core`
  - `packages/tools`
  - `packages/guardrails`
  - `packages/evals`
  - `packages/observability`
  - `scripts`
- [ ] Add FastAPI `/health` endpoint
- [ ] Add FastAPI `/ask` mock endpoint
- [ ] Add Pydantic shared contracts
- [ ] Add smoke test script
- [ ] Add README local run instructions

### Acceptance criteria

- [ ] `uv sync` works
- [ ] `uv run python scripts/smoke.py` passes
- [ ] FastAPI starts locally
- [ ] no real API keys committed
- [ ] no generated files committed

## RAG task slices

The RAG pipeline can start after Phase 0 setup is merged into `development`.

## Dev A — Extractors + Dispatcher

### Tasks

- [ ] PDF extractor: page text + page number locator
- [ ] TXT extractor: encoding detection + char offset locator
- [ ] CSV extractor: row-to-text, header preservation, row number locator
- [ ] Format dispatcher: magic-byte detection, not only extension

### Tests

- [ ] PDF page text correct and `locator.page` equals page number
- [ ] TXT UTF-8, latin-1, UTF-16 detection pass
- [ ] TXT char offsets reconstruct original span
- [ ] CSV header appears in every row representation
- [ ] CSV `locator.row` matches source row index
- [ ] Dispatcher routes PDF magic bytes to PDF extractor
- [ ] Unsupported magic bytes raise `UnsupportedFormat`

## Dev B — Locator Integrity + Idempotency

### Tasks

- [ ] Reject chunks with no resolvable locator
- [ ] Re-ingesting same filename replaces old chunks instead of duplicating
- [ ] Collection scoping for tenant/project separation

### Tests

- [ ] Chunk missing locator raises validation error
- [ ] Chunk with null page and null offset is rejected
- [ ] First ingest of `file-A` stores N chunks
- [ ] Re-ingest same `file-A` keeps chunk count stable
- [ ] Re-ingest modified `file-A` replaces old chunks
- [ ] Two different filenames coexist

## Dev C — Chunker + Embed + Store

### Tasks

- [ ] Chunker with 512-token target and 64-token overlap
- [ ] Embedder with `all-MiniLM-L6-v2` or configured embedding adapter
- [ ] Store chunks and embeddings into the chosen local/vector store
- [ ] Expose `store(chunks, tenant) -> stored_count`
- [ ] Expose `delete_by_source(filename, tenant)`

### Tests

- [ ] 512-token input creates one chunk
- [ ] 1024-token input creates expected overlapping chunks
- [ ] Chunk preserves source locator metadata after split
- [ ] Embedding shape is correct for the configured model
- [ ] Stored chunk retrievable by ID
- [ ] Two tenants/projects do not cross-contaminate

## Dev D — Retrieval + API Endpoint

### Tasks

- [ ] Retrieval function returns top-k results with scores
- [ ] Add score threshold and abstain branch
- [ ] Add `POST /ingest` endpoint for file upload
- [ ] Return `chunk_count` and `skipped_count`
- [ ] End-to-end test: upload file, query, retrieve relevant chunk

### Tests

- [ ] Query returns top-k results sorted by score
- [ ] Each returned chunk has `score`
- [ ] Below threshold returns abstain path
- [ ] `POST /ingest` returns 200 with counts
- [ ] Unsupported file returns 422 with reason
- [ ] E2E retrieval finds expected locator
- [ ] Re-upload same file does not duplicate chunks

## Shared contract draft

Prefer Pydantic models over dataclasses because the API boundary also needs validation and serialization.

```python
class Locator(BaseModel):
    page: int | None = None
    char_start: int | None = None
    char_end: int | None = None
    row: int | None = None

class Chunk(BaseModel):
    text: str
    source_file: str
    locator: Locator
    chunk_id: str
```

## Integration rule

No branch is complete until it passes the current smoke test and plugs into the shared contract.

Do not merge code that only works in isolation.
