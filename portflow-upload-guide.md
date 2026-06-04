# PortFlow Upload Guide — Marketing Agent POC

---

## COLLECTION DETAILS

### Collection Title
**Marketing Agent — AI-Powered Campaign Studio**

### Collection Description (paste this into PortFlow)

> **What is this project about?**
> Marketing Agent is a multi-agent AI system that takes a product image and short description and produces a complete marketing campaign in under 90 seconds. Eight specialised agents collaborate: one analyses the product image, one segments the target audience, one writes two ad copy variants with distinct angles, one checks for compliance violations, one scores and improves the CTAs. A RAG layer lets users inject brand briefs or product specs. A live refinement panel lets them iterate on tone, audience age, and copy without re-running the full pipeline.
>
> **Why does it exist?**
> The project responds to a documented shift in the industry: one Dutch advertising agency went from 290 copywriters to 20 after implementing AI. The assignment asked the same question Reclamebureau Eva answered on Dutch national television: *can a team of specialised AI agents produce professional campaign output that a single generalist agent cannot?* The system was built to test that question with real evidence, not theory.
>
> **What was actually accomplished?**
> A fully working end-to-end system: a Flask backend with SSE streaming progress, a two-column result UI with a sticky refinement panel, eight specialised agents with clean input/output contracts, a ChromaDB RAG layer, ReAct routing that re-runs only the affected pipeline stages on each refinement, and an append-only telemetry log that tracks output quality across runs. Every architectural decision is documented in a nine-entry Decision Log that includes the research question, the LO stage progression, evidence, and what the decision unlocked.

---

## PHASE STORY (Phase 0 → Phase 3)

*Based on git commit history and decision log arc.*

---

### Phase 0 — Analyzing: what does an agency actually do? (March 2026)

The project started with a question that felt obvious but wasn't: before building an AI marketing team, what does a real marketing agency actually do? I read two research sources (ironpaper.com and setup.us) and answered six questions about agency functions, team structure, and skill overlap. The finding that mattered: even the smallest agency performs exactly five distinct functions — product analysis, audience definition, copy generation, CTA optimisation, compliance review. These five became the agent pipeline.

The requirements spec followed: ten functional requirements were written, five were scoped for the POC, five deferred. Compliance (FR7) made it into the required set — not as a nice-to-have, but because ungrounded claims in ad copy are a legal risk.

**Key commits:**
- `1ae96ea` — Initial commit: Marketing Agent POC with audience segmentation and CTA optimizer

**DLs produced:** A1 (agency research), A2 (requirements spec), DL-00 (scope + model stack)

**What it unlocked:** A fixed pipeline target before any agent was written. Five agents. No scope drift.

---

### Phase 1 — Designing → Realizing: monolith first, then specialists (March 2026)

The first working version was a single Ollama call. System prompt: "You are a marketing expert. Write two ad variants." Output: "Check out this amazing product! Shop now." Audience: "general public."

That output was the evidence. Running the monolith and seeing "general public" as the persona made the specialisation argument concrete — not theoretical. The multi-agent pipeline on the same input produced "Eco-Conscious Millennial Athlete, 25-34" and copy that referenced that persona's identity rather than describing the product generically.

This phase also hit the first model error: the vision agent's first pick (gemma-3-4b-it:free) returned a 400 — "model does not support vision." The ":it" suffix means instruction-tuned, not vision-capable. Switched to nemotron-nano-12b-v2-vl:free with a llama-3.2-11b fallback. Redesigned the vision output schema from visual attributes to buyer signals — the `target_signals` field is what makes the audience agent's persona specific rather than generic.

Compliance was the other key build. Testing an LLM judge (mistral:7b) against five samples with known violations: it missed two of five. "Results guaranteed or your money back" was not flagged because the model decided the refund offer mitigated the guarantee. That's a legal judgment call it's not qualified to make. Switched to pure Python regex — seven patterns, under 1ms, zero false negatives on the test set.

**Key commits:**
- `1ae96ea` — Initial commit (base pipeline including all five agents)
- `c058c21` — docs: log decisions

**DLs produced:** DL-01 (monolith → specialists), DL-02 (vision agent), DL-03 (guardrails)

**What it unlocked:** A working five-agent pipeline that produces specific, persona-grounded copy and flags compliance violations deterministically.

---

### Phase 2 — Realizing: RAG layer and refinement UI (March–April 2026)

Two additions that moved the pipeline from "adequate for demos" to "usable for real products."

**RAG (March 2026):** Campaigns were generic when the product had specs not visible in the image. Added ChromaDB (local, pip install, deduplication built-in) and nomic-embed-text via Ollama. Users can upload a product manual or brand brief before generating — the copywriter receives relevant chunks as context and writes to the spec, not the image alone. Ingest completes in under 10 seconds. Copy with a product manual uploaded produced specific technical claims; copy without it produced generic descriptions.

**Refinement UI (April 2026):** The one-shot report was not a usable workflow. Designed the two-column layout in a wireframe (wireframe.txt) before writing any HTML — eight layout decisions documented with rationale. Sticky right panel. Sliders above chat (deterministic controls first). Routing label visible. Proactive `/suggest` call fires on page load. ReAct routing: one LLM call decides which agents re-run, then runs them in pipeline order. Vision never re-runs during refinement. SSE streaming replaced the blank-screen wait with live step-by-step progress.

Also in this phase: the copywriter timed out at 60 seconds on a long-context run. mistral:7b stalled on creative prose with four RAG chunks in context. Tested three alternatives — gemma4:e2b ran in 25-40 seconds with noticeably better syntactic variety. Split the config: gemma4:e2b for copywriter, mistral:7b for all JSON-structured tasks (audience, CTA, routing). One config line each.

**Key commits:**
- `d61495c` — feat: add RAG pipeline with ChromaDB and document knowledge base
- `6c0aa61` — docs: add ARCHITECTURE.md
- `0002e6c` — docs: add README
- `16b76b9` — feat: add ReAct assistant agent with interactive refinement UI

**DLs produced:** DL-04 (RAG), DL-05 (refinement UI + routing), DL-06 (model split)

**What it unlocked:** An interactive creative tool. Users generate → read → adjust sliders → refine → iterate. The 90-second generation becomes a 30-second refinement cycle.

---

### Phase 3 — Managing: telemetry, validation, and the honest accounting (June 2026)

With the pipeline stable, focus shifted to observability and evidence.

**Telemetry:** Added `run_log.jsonl` — one JSONL line per run recording timestamp, run_id, vision model used, pipeline time, compliance flag count, average CTA score, RAG chunks used, and persona label. Added `/stats` endpoint that reads the log and returns aggregates. First finding: compliance flags appear in ~40% of runs, almost always urgency language ("limited time", "act now") generated without user request. The copywriter prompt needs adjustment — the telemetry made this visible.

**Validation:** `tests/validate.py` runs the pipeline agents directly against acceptance criteria without the web server. Guardrails detection, persona specificity, variant distinctiveness, character limits, pipeline timing.

**Scripts:** `scripts/setup.py` installs dependencies and pulls all required Ollama models. `scripts/health_check.py` verifies Ollama and OpenRouter are reachable before a demo — no mid-demo "model not found" surprises.

**Ethics DL:** Required by the assignment brief. The pipeline automates copywriting, audience analysis, and campaign strategy — roles down 28% year-over-year. Three accountability gaps named: no inter-agent critique (errors cascade), compliance coverage is not exhaustive (novel phrasing slips through), persona bias (training data distributions, not market research). Documented so anyone using the output knows to apply human judgment before publishing.

**DLs produced:** DL-07 (pipeline telemetry), DL-08 (ethics)

**What it unlocked:** Evidence that the system works and evidence of where it falls short. Both matter.

---

## EVIDENCE FILE LIST WITH LO TAGS

*All paths relative to the `marketingAI/` project root.*

---

### Decision Logs (primary evidence — tag to multiple LOs)

| File | Description | LO Tags |
|------|-------------|---------|
| `decision_logs/A1_agency_function_research.txt` | Agency role research: six questions answered, five-function baseline identified | LO1 |
| `decision_logs/A2_requirements_and_scope.txt` | FR/BR/US spec with POC scope decisions and deferral reasoning | LO1, LO3 |
| `decision_logs/ADV1_agent_decomposition.txt` | Pre-build advisory: why five specialists, pipeline order, what to watch for | LO2 |
| `decision_logs/ADV2_compliance_strategy.txt` | Pre-build advisory: LLM judge vs regex — risk profile, recommendation, seven patterns | LO2 |
| `decision_logs/00_scope_and_model_stack.txt` | Scope locked to five agents; cloud/local model split decided | LO1, LO3 |
| `decision_logs/01_monolith_to_specialists.txt` | Monolith comparison, specialisation proof, audience stage validated | LO1, LO2, LO3, LO4 |
| `decision_logs/02_vision_agent.txt` | Model fallback chain + output schema redesign from visual → buyer signals | LO3, LO4, LO5 |
| `decision_logs/03_guardrails_pure_python.txt` | LLM judge rejected; regex chosen; zero false negatives | LO3, LO4 |
| `decision_logs/04_rag_chromadb.txt` | ChromaDB + nomic-embed-text; copy improves with brand documents | LO2, LO3, LO4 |
| `decision_logs/05_refinement_ui_routing.txt` | Wireframe → ReAct routing → SSE progress; CTA key bug fixed | LO3, LO4, LO5 |
| `decision_logs/06_model_split.txt` | Timeout → gemma4:e2b for copy, mistral:7b for JSON; one config line each | LO4, LO5 |
| `decision_logs/07_pipeline_telemetry.txt` | run_log.jsonl, /stats endpoint, first findings (40% compliance rate) | LO5 |
| `decision_logs/08_ethics.txt` | Workforce displacement, three accountability gaps, system limits | LO1, LO5 |
| `decision_logs/STORY.md` | 10-minute narrative arc connecting all phases | LO1, LO2, LO3, LO4, LO5 |
| `decision_logs/INDEX.txt` | Reading guide and file registry | LO1 |

---

### Research and Analysis (LO1 — Analyzing)

| File | Description | LO Tags |
|------|-------------|---------|
| `Project_case.md` | Assignment brief: Reclamebureau Eva case, success criteria, ethics requirement | LO1 |
| `2518cd57-..._AI_marketing_agent2.pdf` | Agency function research source (ironpaper.com + setup.us) | LO1 |
| `2ec2ea0f-..._Requirements3.pdf` | Formal requirements spec: FR1-FR10, BR1-BR4, US-1 to US-5 | LO1 |
| `analysis/research_questions.md` | Five formal research questions driving the project | LO1 |
| `analysis/stakeholder_analysis.md` | Four stakeholder groups: small business owner, student, displaced copywriter, ethical | LO1 |
| `analysis/constraints.md` | Technical, functional, design, scope, and educational constraints | LO1 |
| `analysis/competitor_scan.md` | Jasper, Copy.ai, ChatGPT scan — why existing tools don't answer the research question | LO1, LO2 |

---

### Design Documents (LO3 — Designing)

| File | Description | LO Tags |
|------|-------------|---------|
| `wireframe.txt` | ASCII wireframe of result.html two-column layout; 8 design decisions with rationale | LO3 |
| `ARCHITECTURE.md` | Agent pipeline diagram: vision → color → RAG → audience → copywriter → guardrails → CTA | LO3 |
| `config.example.py` | Model stack configuration; OLLAMA_MODEL / OLLAMA_FAST_MODEL split | LO3 |
| `docs/agent_contracts.md` | Input/output contracts per agent — what each receives, what each returns, what it cannot see | LO3 |
| `docs/user_requirements.md` | User needs from the upload page, result page, refinement panel; trust requirements | LO3 |

---

### Implementation (LO4 — Realizing)

| File | Description | LO Tags |
|------|-------------|---------|
| `app.py` | Flask orchestrator: SSE /generate, /refine, /result/<run_id>, /export, /health, /stats | LO4 |
| `agents/vision.py` | Product analyst agent; nemotron primary, llama fallback; target_signals output | LO4 |
| `agents/audience.py` | Persona segmentation from product signals; mistral:7b JSON | LO4 |
| `agents/copywriter.py` | Two variants with enforced angles (emotional hook / product benefit); gemma4:e2b | LO4 |
| `agents/guardrails.py` | Pure Python regex; seven compliance patterns; no LLM call | LO4 |
| `agents/cta_optimizer.py` | CTA scoring and improvement suggestions per variant; mistral:7b | LO4 |
| `agents/rag.py` | ChromaDB retrieval; nomic-embed-text embeddings; chunk deduplication | LO4 |
| `agents/assistant.py` | ReAct routing, slider mapping, proactive suggestions; mistral:7b | LO4 |
| `agents/color.py` | Dominant color extraction from product image | LO4 |
| `templates/index.html` | Upload form with SSE progress overlay and step indicators | LO4 |
| `templates/result.html` | Two-column report + sticky refinement panel + export button | LO4 |
| `templates/docs.html` | Knowledge base management UI | LO4 |
| `tests/validate.py` | Pipeline acceptance tests: compliance detection, persona specificity, char limits, timing | LO4 |
| `scripts/setup.py` | Install deps + pull Ollama models in one command | LO4 |
| `scripts/health_check.py` | Pre-demo check: Ollama reachable, models present, OpenRouter key valid | LO4 |
| `requirements.txt` | Python dependencies | LO4 |
| `README.md` | Setup guide and project overview | LO4 |

---

### Monitoring and Managing (LO5 — Managing)

| File | Description | LO Tags |
|------|-------------|---------|
| `app.py` `/health` + `/stats` routes | Health endpoint (Ollama status) and stats endpoint (run aggregates) | LO5 |
| `decision_logs/07_pipeline_telemetry.txt` | run_log.jsonl design, /stats endpoint, first findings from initial runs | LO5 |
| `decision_logs/08_ethics.txt` | Three accountability gaps; system limits documented; workforce context | LO5 |

---

## QUICK LO SUMMARY

| LO | What it covers in this project | Primary files |
|----|-------------------------------|---------------|
| **LO1 Analyzing** | Agency research, requirements spec, research questions, stakeholder analysis, constraints, competitor scan, ethics | A1, A2, analysis/, DL-00, DL-08, Project_case.md, PDFs |
| **LO2 Advising** | ADV1 (agent decomposition), ADV2 (compliance strategy), monolith comparison evidence, RAG option evaluation | ADV1, ADV2, DL-01, DL-04, analysis/competitor_scan.md |
| **LO3 Designing** | Pipeline design, model stack, wireframe, agent contracts, user requirements, compliance mechanism | DL-00, DL-03, DL-05, wireframe.txt, ARCHITECTURE.md, docs/ |
| **LO4 Realizing** | All agent implementation, Flask server, SSE streaming, refinement loop, tests, scripts | DL-01 through DL-06, agents/, app.py, templates/, tests/, scripts/ |
| **LO5 Managing** | Telemetry, /health + /stats, run_log monitoring, startup model check, ethics accountability gaps | DL-07, DL-08, DL-02 (model_used logging), DL-06 (startup check) |

---

## UPLOAD ORDER RECOMMENDATION

Upload in this order so evidence is in place before DLs that reference it:

1. Collection description — create the collection first
2. Sprint story (STORY.md) — narrative anchor for the whole collection
3. Project_case.md + both PDFs — establish the research context and brief
4. A1 + A2 research files — LO1 foundation before any design files
5. analysis/ files (research_questions, stakeholder_analysis, constraints, competitor_scan) — supporting LO1 context
6. ADV1 + ADV2 advisory files — LO2 pre-build recommendations before code
7. DL-00 (scope + model stack)
8. wireframe.txt + ARCHITECTURE.md + docs/ (agent_contracts, user_requirements) — design artifacts together
9. DL-01 (monolith → specialists) — the key decision
10. DL-02 (vision agent) + DL-03 (guardrails)
11. Agent code files (agents/*.py) — implementation evidence
12. app.py + templates/ — Flask server and UI
13. DL-04 (RAG) + DL-05 (refinement UI)
14. DL-06 (model split)
15. tests/validate.py + scripts/ — validation and tooling
16. DL-07 (telemetry) + DL-08 (ethics)
17. INDEX.txt + README last — ties everything together
