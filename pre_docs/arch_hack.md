# ContextOS — Architecture Reference

## Request pipeline

```
User question
      │
      ▼
┌─────────────────────────────────────┐
│  Auth boundary                      │
│  Resolve tenant_id + principal      │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  Input guardrail                    │
│  PII redact + injection scan        │
└──────┬──────────────────────────────┘
       │                    │ high injection score
       │ safe               ▼
       │         ┌──────────────────┐
       │         │  Blocked         │
       │         │  Safe response   │──────────┐
       │         └──────────────────┘          │
       ▼                                       │
┌─────────────────────────────────────┐        │
│  RAG retrieval                      │        │
│  Top-k + per-chunk injection scan   │        │
└──────┬──────────────────────────────┘        │
       │                    │ below MIN_SCORE   │
       │ evidence found     ▼                  │
       │         ┌──────────────────┐          │
       │         │  Abstained       │──────┐   │
       │         │  Low evidence    │      │   │
       │         └──────────────────┘      │   │
       ▼                                   │   │
┌─────────────────────────────────────┐    │   │
│  run_qa                             │    │   │
│  Featherless Llama · grounded prompt│    │   │
│  temperature = 0.0                  │    │   │
└────────────────┬────────────────────┘    │   │
                 │                         │   │
                 ▼                         │   │
┌─────────────────────────────────────┐    │   │
│  Groundedness gate                  │    │   │
│  NLI verify per claim               │    │   │
│  Strip unsupported claims           │    │   │
│  Tavily external verify (weak)      │────┘   │
│  Abstain if nothing left            │        │
└────────────────┬────────────────────┘        │
                 │                             │
                 ▼                             │
┌─────────────────────────────────────┐        │
│  Output guardrail                   │        │
│  PII redact outbound                │        │
└────────────────┬────────────────────┘        │
                 │                             │
                 ▼                             │
┌─────────────────────────────────────┐        │
│  Score confidence                   │        │
│  f(groundedness, retrieval, cites)  │        │
└────────────────┬────────────────────┘        │
                 │                             │
                 ▼                             │
┌─────────────────────────────────────┐        │
│  Audit log  ◄───────────────────────┼────────┘
│  Per-claim verdicts · tenant-scoped │
└────────────────┬────────────────────┘
                 │
                 ▼
        Response to user
    answer · confidence · audit id
```

---

## System structure

```
┌─────────────────────────────────────────────────────────┐
│  ContextOS system                                       │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Client layer                                     │  │
│  │  Streamlit UI                                     │  │
│  │  Ingest panel · Ask panel · Answer view · 4 states│  │
│  └───────────────────────┬───────────────────────────┘  │
│                          │ HTTP                         │
│  ┌───────────────────────▼───────────────────────────┐  │
│  │  API layer                                        │  │
│  │  FastAPI                                          │  │
│  │  POST /ask · POST /ingest · auth · tenant_id      │  │
│  └───────────────────────┬───────────────────────────┘  │
│                          │                              │
│  ┌───────────────────────▼───────────────────────────┐  │
│  │  Pipeline core  (LangGraph)                       │  │
│  │  PipelineState flows through every node           │  │
│  │                                                   │  │
│  │  ┌───────────────┐   ┌───────────────┐            │  │
│  │  │  Guardrails   │   │  RAG          │            │  │
│  │  │  PII          │   │  Chunker      │            │  │
│  │  │  Injection    │   │  Ingest       │            │  │
│  │  │  Input+output │   │  Retrieval    │            │  │
│  │  │  Block branch │   │  run_qa       │            │  │
│  │  └───────────────┘   └───────────────┘            │  │
│  │                                                   │  │
│  │  ┌───────────────┐   ┌───────────────┐            │  │
│  │  │  Faithfulness │   │  Score+Audit  │            │  │
│  │  │  NLI deberta  │   │  Confidence   │            │  │
│  │  │  Claim split  │   │  structlog    │            │  │
│  │  │  Strip/abstain│   │  Per-claim    │            │  │
│  │  │  Tavily verify│   │  Tenant-scoped│            │  │
│  │  └───────────────┘   └───────────────┘            │  │
│  │                                                   │  │
│  └───────────────────────┬───────────────────────────┘  │
│                          │                              │
│  ┌───────────────────────▼───────────────────────────┐  │
│  │  Persistence layer                                │  │
│  │                                                   │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  │  │
│  │  │ ChromaDB   │  │ Audit log  │  │ Langfuse   │  │  │
│  │  │ Tenant     │  │ Append-    │  │ Traces     │  │  │
│  │  │ collections│  │ only JSONL │  │ Self-hosted│  │  │
│  │  └────────────┘  └────────────┘  └────────────┘  │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

                  External services
          ┌──────────────────────────────┐
          │  Featherless AI              │
          │  Llama 3.3-70B · $25 credit  │
          │                              │
          │  Tavily                      │
          │  Web search · $2,000 credit  │
          │                              │
          │  NLI model                   │
          │  nli-deberta-v3-base · local │
          └──────────────────────────────┘

Note: Ingest path bypasses the pipeline graph entirely.
      POST /ingest → chunker → embed → ChromaDB directly.
```

---

## File structure

```
contextos/
├── app/
│   ├── security/
│   │   ├── tenancy.py          # tenant_id resolution
│   │   ├── auth.py             # authN / authZ
│   │   └── secrets.py          # env / vault loader
│   ├── guardrails/
│   │   ├── pii.py              # redact() — inbound + outbound
│   │   ├── injection.py        # score() — pure function
│   │   └── groundedness.py     # verify() + gate node
│   ├── rag/
│   │   ├── ingest.py           # format dispatcher
│   │   ├── retrieval.py        # rag_retrieval node
│   │   └── chunker.py          # RecursiveCharacterTextSplitter
│   ├── orchestration/
│   │   ├── graph.py            # LangGraph assembly
│   │   ├── state.py            # PipelineState dataclass
│   │   └── nodes/              # one file per node
│   ├── tools/
│   │   ├── rag_tool.py         # wraps retrieval for ReAct
│   │   └── web_search.py       # Tavily wrapper
│   ├── main.py                 # FastAPI app
│   └── config.py               # reads from .env
├── ui/
│   └── app.py                  # Streamlit
├── eval/
│   ├── corpus.json             # 30 labeled rows
│   └── harness.py              # RAGAS runner
├── data/
│   ├── chroma/                 # ChromaDB persistent store
│   └── audit.jsonl             # append-only audit log
├── .env                        # config (never commit real values)
├── .env.example                # all keys with comments
├── docker-compose.yml          # ChromaDB + Langfuse
└── requirements.txt
```

---

## PipelineState fields

```
Tenancy       tenant_id · principal
Input         question · history
PII           redacted_question · redacted_answer · pii_found
Injection     injection_detected · injection_score · flagged_spans
Retrieval     rag_context · retrieval_scores
Generation    answer
Groundedness  groundedness_score · unsupported_claims · abstained
              abstain_reason · regenerated · sources_conflict
              external_verified
Confidence    confidence_score
ReAct (v2)    thoughts · actions_taken · observations
              iterations · should_continue
Audit         audit_id · blocked
```

---

## Config flags — MVP values, upgrade path in comments

```
# LLM
LLM_PROVIDER              = featherless        # → bedrock | vertexai
FEATHERLESS_API_KEY        = REPLACE
LLM_MODEL_MAIN             = meta-llama/Llama-3.3-70B-Instruct
LLM_MODEL_JUDGE            = meta-llama/Llama-3.1-8B-Instruct
LLM_TEMPERATURE            = 0.0               # never change
LLM_USE_BATCH_API          = false             # → true for eval runs
ANTHROPIC_API_KEY          = REPLACE           # reserve for eval judge only
MODEL_ROUTER               = false             # → true in v2

# Tenancy + auth
TENANCY_MODEL              = single            # → collection_per_tenant
TENANT_ID_DEFAULT          = demo
AUTH_PROVIDER              = none              # → api_key → oidc
AUTH_API_KEY               = change-me
SECRETS_BACKEND            = env               # → aws_ssm | vault

# Vector store
VECTOR_STORE               = chromadb          # → pgvector
CHROMA_MODE                = persistent        # never in-memory
CHROMA_PATH                = ./data/chroma
EMBED_MODEL                = all-MiniLM-L6-v2

# Retrieval
RETRIEVAL_TOP_K            = 5
RETRIEVAL_MIN_SCORE        = 0.35              # set from eval sweep
RETRIEVAL_RERANK           = false             # → true in v2

# PII
PII_ENABLED                = true
PII_MODE                   = mask
PII_USE_NER                = false             # → true in v2
PII_FAIL_MODE              = fail_closed       # never change

# Injection
INJECTION_ENABLED          = true
INJECTION_THRESHOLD        = 0.75              # tune from corpus
INJECTION_MODE             = flag_only         # → block once tuned
INJECTION_USE_CLASSIFIER   = false             # → true in v2
INJECTION_FAIL_MODE        = fail_closed       # never change

# Groundedness
GROUNDEDNESS_ENABLED       = true
GROUNDEDNESS_THRESHOLD     = 0.6               # set from eval sweep
GROUNDEDNESS_MODE          = strip             # → regenerate in v2
GROUNDEDNESS_REGENERATE_CAP= 0                 # → 1 in v2
GROUNDEDNESS_EXTERNAL_VERIFY = true            # Tavily fallback
GROUNDEDNESS_FAIL_MODE     = fail_closed       # never change
NLI_MODEL                  = cross-encoder/nli-deberta-v3-base

# Tavily
TAVILY_API_KEY             = tvly-REPLACE      # $2,000 hackathon credits
TAVILY_SEARCH_DEPTH        = advanced
TAVILY_MAX_RESULTS         = 5

# Ingest
INGEST_MAX_FILE_MB         = 20
INGEST_FORMATS             = pdf,txt           # → pdf,txt,csv in phase 3
INGEST_REJECT_BAD_LOCATOR  = true              # never set false

# ReAct (off in MVP)
REACT_ENABLED              = false             # → true in v2
REACT_MAX_ITERATIONS       = 5
REACT_TOOLS                = rag               # → rag,web_search in v2
REACT_TOKEN_BUDGET         = 50000

# Observability
OBSERVABILITY_BACKEND      = langfuse
LANGFUSE_HOST              = http://localhost:3000  # → cloud in prod
LANGFUSE_PUBLIC_KEY        = pk-lf-REPLACE
LANGFUSE_SECRET_KEY        = sk-lf-REPLACE

# Eval
EVAL_GATE_ENABLED          = false             # → true in v2
EVAL_CORPUS_PATH           = ./eval/corpus.json
EVAL_MIN_FAITHFULNESS      = 0.80
EVAL_MAX_HALLUCINATION     = 0.05
EVAL_MAX_FALSE_REFUSAL     = 0.15

# Cache + audit + limits
CACHE_ENABLED              = false             # → true in v3
AUDIT_LOG_PATH             = ./data/audit.jsonl
AUDIT_HASH_CHAIN           = false             # → true before clients
AUDIT_RETENTION_DAYS       = 30                # → 90 in prod
RATE_LIMIT_PER_TENANT      = 0                 # → 100 req/hr in prod
TOKEN_BUDGET_PER_TENANT    = 0                 # → 500000/month in prod
```

---

## Hackathon credits mapped to stack

```
Featherless AI   $25        Primary LLM. Use from day one.
Tavily           $2,000     External verify in gate + web_search in ReAct.
Anthropic        $5         Reserve for eval judge milestone runs only.
Pipecode         $500       Host Docker stack on real URL for demo.
Lovable          $100       Landing page for hackathon presentation.
Just Videos      unlimited  90-second demo walkthrough video.
Geodo            $300       Check product — if Postgres, use for audit store.
GiraffyReach     $80        Skip — marketing, no stack relevance.
CallFort         $20        Skip — telephony, no stack relevance.
```

---

## Production upgrade gates

```
Gate 1 — before any second client (non-negotiable)
  TENANCY_MODEL=collection_per_tenant   4h
  AUDIT_HASH_CHAIN=true                 3h
  SECRETS_BACKEND=aws_ssm               3h
  Cross-tenant isolation test in CI

Gate 2 — before clients depend on it daily
  EVAL_GATE_ENABLED=true                3h
  RATE_LIMIT_PER_TENANT=100             3h
  Online monitoring + drift alerts      3h
  Backup and restore tested             —
  Security review done                  —

Gate 3 — quality and scale hardening
  RETRIEVAL_RERANK=true                 2h
  PII_USE_NER=true                      2h
  GROUNDEDNESS_REGENERATE_CAP=1         2h
  MODEL_ROUTER=true                     3h
  REACT_ENABLED=true                    8h   (do Gates 1+2 first)
  CACHE_ENABLED=true                    5h
```

---

*ContextOS · Architecture Reference · Salman Shaik*