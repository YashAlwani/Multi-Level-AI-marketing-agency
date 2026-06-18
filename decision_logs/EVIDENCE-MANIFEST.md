# Evidence Manifest — `@token` → evidence name → file to upload

**Purpose.** On the upload platform, every `@token` in a decision log or the
summary links to an uploaded evidence of the **same name**. This table is the
upload checklist: for each `@token`, upload the listed file and name the evidence
exactly the token (without the `@`).

**Rule.** Every distinct file = one evidence = one unique `@name`. The footer
lines (`Files:` / `Diagrams:` / `Source:` / `Decision logs:`) are token lists too —
no path survives anywhere a `@` appears. Only `[IMAGE: ...]` callouts in the body
keep a path, because they point a human at the actual picture.

**Footnote bridge (`¹`).** When a log's body points straight at a design doc but
the underlying code lives in the footer, a superscript number bridges them: e.g.
DL-02 body `¹` (the pipeline architecture) ↔ footer `@vision`, `@audience`,
`@copywriter`. Design is foregrounded in the prose; the code stays one hop away.

**Collisions.** None. Design-doc tokens (`@gap-analysis`) and diagram tokens
(`@gap-as-is`, `@gap-to-be`) are deliberately distinct names, so no `@name` points
at two files.

---

## Design docs (upload the PDF)

| `@token` | File to upload |
|----------|----------------|
| `@gap-analysis` | pdf_exports/design/gap-analysis.pdf |
| `@pipeline-architecture` | pdf_exports/design/pipeline-architecture.pdf |
| `@refinement-loop` | pdf_exports/design/refinement-loop.pdf |
| `@wireframes` | pdf_exports/docs/wireframes.pdf |

## Diagrams (upload the PNG)

| `@token` | File to upload |
|----------|----------------|
| `@gap-as-is` | diagrams/gap-as-is.png |
| `@gap-to-be` | diagrams/gap-to-be.png |
| `@pipeline-overview` | diagrams/pipeline-overview.png |
| `@pipeline-dataflow` | diagrams/pipeline-dataflow.png |
| `@system-c4-container` | diagrams/system-c4-container.png |
| `@refinement-routing` | diagrams/refinement-routing.png |
| `@campaign-lifecycle` | diagrams/campaign-lifecycle.png |
| `@wireframe-result-page` | diagrams/wireframe-result-page.png |

## Analysis / requirements (upload the PDF)

| `@token` | File to upload |
|----------|----------------|
| `@requirements-scope` | pdf_exports/analysis/requirements_and_scope.pdf |
| `@constraints` | pdf_exports/analysis/constraints.pdf |
| `@research-questions` | pdf_exports/analysis/research_questions.pdf |
| `@stakeholder-analysis` | pdf_exports/analysis/stakeholder_analysis.pdf |
| `@competitor-scan` | pdf_exports/analysis/competitor_scan.pdf |
| `@agent-contracts` | pdf_exports/docs/agent_contracts.pdf |
| `@case` | pdf_exports/Project_case.pdf |

## Code & data (upload the source file, name = token)

| `@token` | Evidence name | File to upload | Used in |
|----------|---------------|----------------|---------|
| `@app` | app | app.py | DL-01..08 |
| `@config` | config | config.example.py | DL-01, DL-03, DL-05, DL-07 |
| `@vision` | vision | agents/vision.py | DL-02, DL-03 |
| `@audience` | audience | agents/audience.py | DL-02, DL-07 |
| `@copywriter` | copywriter | agents/copywriter.py | DL-02, DL-07 |
| `@guardrails` | guardrails | agents/guardrails.py | DL-04 |
| `@cta-optimizer` | cta-optimizer | agents/cta_optimizer.py | DL-06 |
| `@rag` | rag | agents/rag.py | DL-05 |
| `@assistant` | assistant | agents/assistant.py | DL-06, DL-07 |
| `@result-html` | result-html | templates/result.html | DL-06 |
| `@validate` | validate | tests/validate.py | DL-04 |
| `@setup` | setup | scripts/setup.py | DL-07 |
| `@run-log` | run-log | run_log.jsonl | DL-08 |

---

## Decision-log files (upload each as `[DL-0N]`)

`@[DL-01]` … `@[DL-08]` → the eight `decision_logs/[DL-0N] *.txt` files, plus
`DL-SUMMARY.txt`.

| Token | File |
|-------|------|
| `@[DL-01]` | [DL-01] How do I run the full pipeline at zero cost before writing any agent code.txt |
| `@[DL-02]` | [DL-02] Should I build one marketing agent or five specialists.txt |
| `@[DL-03]` | [DL-03] Which vision model should I use when free-tier APIs are unreliable.txt |
| `@[DL-04]` | [DL-04] Should I use an LLM judge or regex patterns to enforce ad compliance.txt |
| `@[DL-05]` | [DL-05] Which vector store should I use for a local RAG layer with no infrastructure.txt |
| `@[DL-06]` | [DL-06] How do I let users refine campaign output without re-running the full pipeline.txt |
| `@[DL-07]` | [DL-07] Which Ollama model should handle creative copy versus structured JSON output.txt |
| `@[DL-08]` | [DL-08] How do I make the pipeline's behavior observable across many runs.txt |
