# Research Questions
Marketing Agent POC

---

## Primary Question

*Can a team of specialised AI agents produce professional marketing campaign output — audience persona, ad copy, compliance check, CTA optimisation — that a single generalist agent cannot, and where does the improvement actually come from?*

---

## Sub-Questions

### 1. What does a marketing agency actually do, and which functions map to agents?
- What outputs does even the smallest agency produce at minimum viable scale?
- Which functions require genuinely different context versus just a different prompt?
- Is a dedicated audience stage worth the latency overhead, or can the copywriter infer the persona inline?
- Source: agency function research (A1)

### 2. How do you run a multi-agent pipeline at zero cost on a developer laptop?
- Which tasks require cloud inference (vision) versus local models (text)?
- What free-tier vision models are reliable enough for product image analysis?
- Can one local text model handle both creative and structured-output tasks, or does that require a split?
- Source: model stack evaluation (DL-00, DL-06)

### 3. What is the right mechanism for compliance checking in an ad copy pipeline?
- Should compliance use an LLM judge, a rule-based system, or a moderation API?
- What are the consequences of a false negative (missed guarantee claim) in each case?
- Is deterministic compliance worth the coverage limitation?
- Source: guardrails design (DL-03)

### 4. How do you let a user iterate on campaign output without re-running the full pipeline?
- Which pipeline stages are stable (vision, color) and which are re-runnable (copy, CTA)?
- What routing mechanism decides which agents re-run on each refinement request?
- How do you make agent routing visible to the user rather than hiding it?
- Source: refinement UI design (DL-05)

### 5. What does this system do to the profession it automates, and who is accountable?
- Where do the accountability gaps sit in a pipeline where no single component decides the outcome?
- What are the limits of the compliance check and persona generation?
- Source: ethics DL (DL-08), assignment brief (Project_case.md)
