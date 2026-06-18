# Code Evidence — `@token` → code snippet map

**Purpose.** Some `@token`s in the decision logs point at **code that proves an
implementation claim** (a constant, a function, an endpoint, a regex set, a
test). This document is the screenshot guide for those tokens only. For each one
it records:

- the **decision log** it appears in,
- the **`@token`** and the **first and last sentence** where that token is used in the prose,
- the **code file** and the **exact line range** to capture,
- a **description** of what the snippet shows, so a screenshot can be captioned without re-reading the code.

**Scope.** Only tokens that resolve to *code or data files* are listed
(`.py`, `.html`, `.jsonl`). Tokens for diagrams (`@gap-as-is`,
`@campaign-lifecycle`, …), PDFs, and design/analysis docs (`@gap-analysis`,
`@pipeline-architecture`, `@agent-contracts`, `@constraints`,
`@requirements-scope`, …) are evidence of *reasoning*, not *implementation*, and
are deliberately excluded. Many logs foreground a design doc in the prose and
keep the code one hop away in a `¹` footnote — those footnoted code tokens **are**
in scope and are listed below.

Line numbers are 1-based and match the files in the repo root. `@config` resolves
to `config.example.py` (the committed, secret-free copy; `config.py` is
git-ignored but identical in shape).

> Format per entry:
> **Decision log** · **`@token`** · *"first sentence … last sentence"* · **file** `folder/file` · **lines `###-###`** · **Description**

---

## DL-01 — Scope and zero-cost model stack

### `@app` (the full pipeline runs)
- **Sentence(s):** footnote ¹ — *"The agency-function reasoning is set out in the gap analysis; the running pipeline that realises it is @app."* (body: *"The pipeline runs end to end on a product image with no API errors and no timeout, in under 120 seconds."*)
- **File:** `app.py`
- **Lines:** `89-130` (the `_stream()` body running the five agents in order); helper imports at `9`
- **Description:** The Flask `/generate` handler runs vision → audience → copywriter → guardrails → cta_optimizer in sequence — the running proof that the five-agent pipeline executes end to end.

### `@config` (cloud-vision / local-text split)
- **Sentence(s):** *"The split was the only configuration left, and it landed total pipeline time at 60–90 seconds with no billing set up (@config)."*
- **File:** `config.example.py`
- **Lines:** `4-9` (OpenRouter vision keys + the two Ollama model constants)
- **Description:** The model stack: OpenRouter free tier for vision only, Ollama for all text. The split that makes the pipeline run for free on a developer laptop.

---

## DL-02 — One agent vs five specialists

### `@vision`
- **Sentence(s):** footnote ¹ — *"The specialisation argument is laid out in the pipeline architecture; the agents that realise it are @vision, @audience, and @copywriter."*
- **File:** `agents/vision.py`
- **Lines:** `54-92` (`analyze()` — the first stage that produces the structured product analysis)
- **Description:** Specialist #1: the vision agent that turns a product image into structured tags every downstream agent reads.

### `@audience`
- **Sentence(s):** *"The audience agent receives vision data and returns persona_label, age_range, interests, and platform_behavior."* … *"Adding the audience agent as a dedicated middle step — its own call, its own narrow input — is what made copy persona-specific."*
- **File:** `agents/audience.py`
- **Lines:** `6-66` (`segment()`); required-keys system prompt at `14-21`; input is vision tags only at `23-29`
- **Description:** The dedicated middle stage. It receives vision tags (not the raw image) and returns the persona — the step that broke the "general public" circular dependency.

### `@copywriter`
- **Sentence(s):** *"The copywriter receives the full audience output and the description, but never the raw vision JSON (@agent-contracts)."* … *"The copywriter received a pre-built persona instead of raw tags — one job instead of four."*
- **File:** `agents/copywriter.py`
- **Lines:** `6-69` (`generate()`); the persona-constrained, two-distinct-angle prompt at `14-23`
- **Description:** Specialist #3: takes the pre-built persona and writes two structurally distinct variants (variant_1 = emotional hook, variant_2 = product benefit) — one narrow job.

---

## DL-03 — Vision model fallback + output schema

### `@vision` — two-model fallback chain
- **Sentence(s):** *"A two-model fallback chain: nemotron-nano-12b-v2-vl:free primary, llama-3.2-11b-vision-instruct:free fallback."* … footnote ¹ — *"the code that enforces them is @vision."*
- **File:** `agents/vision.py`
- **Lines:** `6` (the `VISION_MODELS` chain) and `62-92` (the try-each-model loop + the safe empty-tags dict on total failure)
- **Description:** The fallback loop: try the primary `:vl` model, fall back to llama, and on double-failure return a safe dict with empty tags so downstream agents run rather than crash.

### `@vision` — buyer-signal output schema
- **Sentence(s):** *"Redesign the output schema from visual attributes to buyer signals — target_signals is the key field, not colours or materials."* … *"target_signals — 'eco-conscious', 'fitness enthusiast', 'outdoor lifestyle' — hands it the product already in buyer-identity language."*
- **File:** `agents/vision.py`
- **Lines:** `14-26` (the system prompt defining `product_type`, `product_tags`, `mood`, `target_signals`, `suggested_hashtags`)
- **Description:** The redesigned schema — buyer signals, not visual attributes — that the audience agent consumes first.

### `@config` — vision model names
- **Sentence(s):** *"A two-model fallback chain: nemotron-nano-12b-v2-vl:free primary, llama-3.2-11b-vision-instruct:free fallback."*
- **File:** `config.example.py`
- **Lines:** `5-6` (`OPENROUTER_MODEL` + `OPENROUTER_FALLBACK_MODEL`)
- **Description:** The exact primary and fallback vision model identifiers the chain in `vision.py` reads.

---

## DL-04 — Regex compliance over an LLM judge

### `@guardrails`
- **Sentence(s):** *"Pure Python regex. Seven patterns covering the required categories …"* … *"guardrails.py returns clean_copy (unchanged — it flags, it does not edit) and a flags list (@agent-contracts)."*
- **File:** `agents/guardrails.py`
- **Lines:** `4-12` (the seven `FLAGGED_PATTERNS`) and `15-40` (`check()` — returns `clean_copy` + `flags`, each flag = variant / matched text / reason)
- **Description:** The deterministic compliance gate: seven case-insensitive regex categories; the check flags but never edits, and each flag is a three-field auditable record.

### `@validate`
- **Sentence(s):** *"Zero false negatives on the test set: pass — all 7 patterns detected correctly in @validate."*
- **File:** `tests/validate.py`
- **Lines:** `56-75` (`test_guardrails()`)
- **Description:** The acceptance test asserting guardrails detects "guaranteed" and clinical/scientific claims, and returns an empty flags list on clean copy — the zero-false-negative evidence.

---

## DL-05 — Local RAG layer (ChromaDB)

### `@rag`
- **Sentence(s):** *"ChromaDB for the vector store — local file persistence, pip install, built-in deduplication by content hash."* … footnote ¹ — *"the code is @rag."*
- **File:** `agents/rag.py`
- **Lines:** `57-58` (`_content_hash`), `61-115` (`ingest_files` — dedup by hashed IDs at `82-95`, returns `{ingested, skipped}` at `111`), `118-134` (`retrieve` top-k), `32-43` (`_chunk_text`)
- **Description:** The retrieval layer: content-hash chunk IDs give free deduplication (re-upload → `skipped: N, ingested: 0`); `retrieve()` returns the top-k chunks injected into the text agents.

### `@config` — RAG settings
- **Sentence(s):** *"At 400 characters with 80-character overlap, retrieval pulls coherent sentences; smaller chunks returned mid-sentence fragments."* (and *"nomic-embed-text via Ollama for embeddings."*)
- **File:** `config.example.py`
- **Lines:** `13-19` (`CHROMA_PERSIST_DIR`, `CHROMA_COLLECTION`, `EMBED_MODEL = nomic-embed-text`, `RAG_CHUNK_SIZE = 400`, `RAG_CHUNK_OVERLAP = 80`, `RAG_TOP_K = 4`)
- **Description:** The RAG configuration — local Chroma store, nomic embeddings, and the 400/80 chunking that mattered more than the embedding model.

### `@app` — RAG wired into the pipeline
- **Sentence(s):** *"Retrieval connects at every text stage: audience, copywriter, and cta_optimizer all accept doc_context as an optional parameter …"*
- **File:** `app.py`
- **Lines:** `96-112` (`rag.retrieve(...)` → `doc_context` passed into audience, copywriter, and cta_optimizer)
- **Description:** Where retrieval plugs in: one `rag.retrieve` call feeds `doc_context` to every text agent that benefits, in the live `/generate` stream.

---

## DL-06 — Refinement UI without a full re-run

### `@result-html`
- **Sentence(s):** *"A wireframe designed before result.html was coded; 8 layout decisions documented with rationale."* … footnote ¹ — *"the code that runs it is @result-html and @assistant."*
- **File:** `templates/result.html`
- **Lines:** sliders markup `349-381` + instant slider JS `419-434`; routing label `392-393` + update `529-531`; the `/refine` call `502-538`; proactive `/suggest` on load `471-489`
- **Description:** The two-column refinement page: sliders update labels instantly with no server call, the routing label renders after each refine, and a proactive `/suggest` fires on load.

### `@assistant`
- **Sentence(s):** *"Single-pass ReAct routing: one LLM call decides which agents re-run, then they run in pipeline order."* … *"After each /refine, get_routing returns agents_to_run, reasoning, and routing_label, and the label renders in the panel (@agent-contracts)."*
- **File:** `agents/assistant.py`
- **Lines:** `21-22` (`ALL_AGENTS` pipeline order), `78-180` (`get_routing` — one LLM call, whitelist + order enforcement + guardrails-always-after-copywriter at `162-167`), `183-194` (`map_sliders_to_params`)
- **Description:** The ReAct router: a single LLM call picks the agent subset, which is then forced into pipeline order with guardrails always following the copywriter. `map_sliders_to_params` turns slider ints into tone/age/formality strings.

### `@cta-optimizer` — the key-normalisation fix
- **Sentence(s):** *"…mistral:7b sometimes returned 'Variant 1' with a capital V and a space instead of 'variant_1', and the template threw a KeyError. The fix normalises all LLM output keys to snake_case before any agent returns."*
- **File:** `agents/cta_optimizer.py`
- **Lines:** `63-76` (the key-normalisation block in `optimize`)
- **Description:** The fix: lower-case + de-space the model's variant keys and remap to `variant_1` / `variant_2`, so a "Variant 1" response no longer throws a KeyError in the template.

### `@app` — the /refine and /suggest endpoints
- **Sentence(s):** *"…the /refine endpoint, ReAct routing in assistant.py, SSE progress on /generate …"* (and *"The full output state travels as JSON in every /refine request, so every call is independently auditable.")*
- **File:** `app.py`
- **Lines:** `227-308` (`/refine` — stateless, runs only the routed agents), `215-224` (`/suggest`); SSE producer at `89-139`
- **Description:** The stateless refine endpoint: it reads the full output state from the request, runs only the agents the router chose, and returns the updated state + routing label. `/suggest` powers the proactive review.

---

## DL-07 — Creative vs structured model split

### `@config` — the two model constants
- **Sentence(s):** *"The split lives in config as OLLAMA_MODEL and OLLAMA_FAST_MODEL, and each agent imports the constant it needs."* … *"One-line config swap: pass — OLLAMA_MODEL / OLLAMA_FAST_MODEL in config."*
- **File:** `config.example.py`
- **Lines:** `8-9` (`OLLAMA_MODEL = "gemma4:e2b"` creative; `OLLAMA_FAST_MODEL = "mistral:7b"` structured)
- **Description:** The split as two constants — swapping either model is a one-line change with no code edit.

### `@copywriter` — imports the creative model
- **Sentence(s):** *"gemma4:e2b for the copywriter only."* … footnote ¹ — *"the constants live in @config and are used by @copywriter, @audience, and @assistant."*
- **File:** `agents/copywriter.py`
- **Lines:** `3` (`from config import OLLAMA_URL, OLLAMA_MODEL`)
- **Description:** The copywriter imports `OLLAMA_MODEL` (gemma4:e2b) — the only agent on the creative model, chosen for expressive range.

### `@audience` — imports the structured model
- **Sentence(s):** *"mistral:7b for everything else."* … footnote ¹ (same as above)
- **File:** `agents/audience.py`
- **Lines:** `3` (`from config import OLLAMA_URL, OLLAMA_FAST_MODEL as OLLAMA_MODEL`)
- **Description:** The audience agent aliases `OLLAMA_FAST_MODEL` (mistral:7b) — kept on the structured model for JSON-schema reliability. (Same import in `agents/cta_optimizer.py:4` and `agents/assistant.py:3`.)

### `@assistant` — imports the structured model
- **Sentence(s):** footnote ¹ — *"…and are used by @copywriter, @audience, and @assistant."*
- **File:** `agents/assistant.py`
- **Lines:** `3` (`from config import OLLAMA_URL, OLLAMA_FAST_MODEL as OLLAMA_MODEL`)
- **Description:** The router/assistant runs on mistral:7b — the schema-reliable side of the split, since routing depends on valid JSON.

### `@setup`
- **Sentence(s):** *"gemma4:e2b is pulled before the server starts. setup.py handles this; if the model is missing, the copywriter returns an error dict rather than crashing."*
- **File:** `scripts/setup.py`
- **Lines:** `11-15` (`OLLAMA_MODELS` list) and `54-57` (the `ollama pull` loop)
- **Description:** The setup script pulls both split models plus the embedding model, so the creative model is present before first run. (The matching startup guard is `_check_models_on_startup` in `app.py:49-61`.)

---

## DL-08 — Telemetry across runs

### `@app` — the logging + stats code
- **Sentence(s):** *"Append-only JSONL (run_log.jsonl). One line per run …"* … footnote ¹ — *"the logging code is @app, writing to @run-log."*
- **File:** `app.py`
- **Lines:** `30-46` (`_log_run` — one metrics-only JSONL line after the pipeline completes) and `175-189` (`/stats` — reads the file and returns aggregates)
- **Description:** `_log_run` writes ~200 bytes of metrics (no copy text) per run off the critical path; `/stats` aggregates runs, avg pipeline seconds, avg CTA score, and compliance rate.

### `@run-log`
- **Sentence(s):** *"One line per run: timestamp, run_id, vision model_used, pipeline_s, compliance_flags count, cta_score_avg, rag_chunks_used, persona_label."* … *"/stats reads it and returns aggregates."*
- **File:** `run_log.jsonl` *(runtime artifact — generated on first run, not committed to the repo)*
- **Lines:** schema is defined by the `entry` dict in `app.py:35-44`; screenshot that, or a generated sample line
- **Description:** The append-only telemetry file. Each line carries only metrics + the single categorical `persona` field — never copy or descriptions. Because it is created at runtime, the canonical evidence of its shape is the `_log_run` entry dict in `app.py`.

---

## Quick index (token → file → lines)

| `@token` | DL(s) | File | Lines |
|----------|-------|------|-------|
| `@app` (pipeline) | 01 | `app.py` | 89-130 |
| `@app` (RAG wiring) | 05 | `app.py` | 96-112 |
| `@app` (refine/suggest) | 06 | `app.py` | 215-224, 227-308 |
| `@app` (telemetry) | 08 | `app.py` | 30-46, 175-189 |
| `@config` (stack split) | 01 | `config.example.py` | 4-9 |
| `@config` (vision models) | 03 | `config.example.py` | 5-6 |
| `@config` (RAG settings) | 05 | `config.example.py` | 13-19 |
| `@config` (model split) | 07 | `config.example.py` | 8-9 |
| `@vision` (specialist) | 02 | `agents/vision.py` | 54-92 |
| `@vision` (fallback chain) | 03 | `agents/vision.py` | 6, 62-92 |
| `@vision` (output schema) | 03 | `agents/vision.py` | 14-26 |
| `@audience` (middle stage) | 02 | `agents/audience.py` | 6-66 |
| `@audience` (model import) | 07 | `agents/audience.py` | 3 |
| `@copywriter` (two variants) | 02 | `agents/copywriter.py` | 6-69 |
| `@copywriter` (model import) | 07 | `agents/copywriter.py` | 3 |
| `@guardrails` | 04 | `agents/guardrails.py` | 4-12, 15-40 |
| `@validate` | 04 | `tests/validate.py` | 56-75 |
| `@rag` | 05 | `agents/rag.py` | 57-58, 61-115, 118-134 |
| `@result-html` | 06 | `templates/result.html` | 349-381, 392-393, 471-489, 502-538 |
| `@assistant` | 06 | `agents/assistant.py` | 21-22, 78-180, 183-194 |
| `@assistant` (model import) | 07 | `agents/assistant.py` | 3 |
| `@cta-optimizer` | 06 | `agents/cta_optimizer.py` | 63-76 |
| `@setup` | 07 | `scripts/setup.py` | 11-15, 54-57 |
| `@run-log` | 08 | `run_log.jsonl` (schema in `app.py` 35-44) | — |
