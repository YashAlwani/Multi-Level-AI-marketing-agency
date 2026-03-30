# Decision Log — Marketing Agent POC

| # | Research Question | LO Stage | Date | Status |
|---|-------------------|----------|------|--------|
| 1 | Which free vision model(s) on OpenRouter should power product image analysis, given free-tier instability? | Realizing | 2026-03-19 | Accepted |
| 2 | What model stack can run the full pipeline at zero cost during the POC phase? | Designing | 2026-03-19 | Accepted |
| 3 | How should the project be branded to reflect its full scope as a marketing agency replacement? | Realizing | 2026-03-19 | Accepted |
| 4 | What should the vision agent's prompt and output schema look like to drive meaningful audience segmentation? | Realizing | 2026-03-19 | Accepted |
| 5 | Should audience segmentation be a separate pipeline stage between vision and copywriter? | Designing | 2026-03-19 | Accepted |
| 6 | How should CTA optimizer handle inconsistent JSON keys from Ollama/mistral? | Realizing | 2026-03-19 | Accepted |
| 7 | How should API credentials be managed for safe GitHub publishing? | Realizing | 2026-03-19 | Accepted |
| 8 | What is the correct Ollama model tag format for mistral? | Realizing | 2026-03-19 | Accepted |
| 9 | What role and function do marketing agencies perform, and which of those functions can form the base of an AI replacement tool? | Analyzing / Designing | 2026-03-20 | Accepted |
| 10 | Which vector database should store RAG document embeddings for the marketing agent? | Advising | 2026-03-30 | Accepted |
| 11 | Which embedding model should generate vector representations for RAG retrieval? | Advising | 2026-03-30 | Accepted |

---

## Decision Log Entry 1

### 0. Context: Why does this question exist?

**Project/assignment this belongs to:**
Marketing Agent POC — a Flask-based AI marketing agency replacement that automates product analysis, audience segmentation, ad copywriting, and CTA optimization. The vision analysis pipeline is the first stage: it feeds structured product tags into all downstream agents.

**Why this matters right now:**
The vision agent is the entry point of the entire pipeline. If it cannot analyze a product image, the audience segmentation agent (Ollama/mistral:7b) receives empty tags, and the ad copy and CTA agents produce generic, low-quality output. The pipeline was completely blocked because the initially configured model could not process images at all.

**Where this fits:**
- Pipeline file: `agents/vision.py`
- Config: `config.py` (OPENROUTER_MODEL, OPENROUTER_FALLBACK_MODEL)
- Downstream consumers: audience segmentation, ad copywriting, CTA optimization agents (all depend on vision output JSON)

---

### 1. My research question
Which free vision model(s) on OpenRouter should power product image analysis, given free-tier instability and the need for reliable structured JSON output?

---

### 2. Current LO stage
[ ] Analyzing    [ ] Advising    [ ] Designing    [x] Realizing    [ ] Managing

---

### 3. What makes a good decision here?

**My criteria for success:**
- **C1 — Vision capability:** The model must actually support image input via the OpenRouter chat completions API (not text-only).
- **C2 — Availability:** The pipeline must not hard-fail when a single free-tier model is congested or down; at least one model should respond successfully on any given attempt.
- **C3 — Structured output quality:** The model must return parseable JSON containing product_type, product_tags, mood, target_signals, and suggested_hashtags — keys the downstream agents depend on.

---

### 4. What I decided
Use `nvidia/nemotron-nano-12b-v2-vl:free` as the primary vision model and `meta-llama/llama-3.2-11b-vision-instruct:free` as an automatic fallback, with a hardcoded error dict as the final safety net.

---

### 5. Why this decision

**Method I used:**
Trial-and-error testing of three free OpenRouter models against the product analysis endpoint, observing HTTP status codes and response content.

**What I found/observed:**
1. `google/gemma-3-27b-it:free` — returned HTTP 400. Gemma is a text-only model; it does not support the `image_url` content type in the OpenRouter API. This was a broken assumption: the model name does not indicate vision support.
2. `nvidia/nemotron-nano-12b-v2-vl:free` — correctly processes images (VL = vision-language), but intermittently returns HTTP 502 due to free-tier server congestion.
3. `meta-llama/llama-3.2-11b-vision-instruct:free` — also supports vision input and is available as a free model on OpenRouter. Provides a second chance when Nemotron is overloaded.

**Evidence & artifacts:**
- Implementation: `agents/vision.py` — fallback loop across `VISION_MODELS` list (lines 63-82)
- Config: `config.py` — `OPENROUTER_MODEL` and `OPENROUTER_FALLBACK_MODEL` definitions
- Output traceability: `model_used` field added to the vision output JSON (line 78), allowing downstream debugging

**What this means:**
Free-tier vision models on OpenRouter are unreliable individually, but combining two independent models behind a retry loop gives the pipeline a much higher chance of returning real product analysis data on any given request.

**So I decided:**
A primary + fallback pattern is the minimum viable reliability strategy for free-tier models. Nemotron stays primary because its 12B VL architecture is purpose-built for vision-language tasks. Llama 3.2 11B Vision Instruct is the fallback because it is also free, vision-capable, and runs on different infrastructure — so correlated downtime is unlikely.

---

### 6. Does this hold up?

**How well this meets my criteria:**
- C1 — Vision capability: [checkmark] Both models accept image_url input and return product analysis JSON. Gemma was eliminated precisely because it failed this criterion.
- C2 — Availability: [yellow] Two models reduce single-point-of-failure risk, but both are free-tier and could be down simultaneously. No paid fallback exists yet.
- C3 — Structured output quality: [yellow] Both models return JSON, but free-tier models occasionally include markdown fencing or extra text. The `_parse_content` function (lines 45-51) strips markdown code fences, but edge cases may still break parsing.

**Assumptions I'm making:**
- OpenRouter will continue offering both models on the free tier.
- The two models run on different backend infrastructure, so their outages are not correlated.
- 30-second timeout per model (60 seconds worst-case for both) is acceptable for user experience.
- Free-tier rate limits will not be hit during POC-scale usage.

**What surprised me:**
The Gemma model name (`gemma-3-27b-it`) gave no indication that it lacked vision support. The "it" suffix suggests instruction-tuning, not modality. This was only discovered at runtime via an HTTP 400 error — OpenRouter does not validate modality compatibility before accepting the request. Lesson: always verify a model's supported modalities in the OpenRouter docs, not just its name.

---

### 7. What this unlocks

**Implementation evidence:**
- `agents/vision.py` — full fallback loop with model tracking
- `config.py` — OPENROUTER_MODEL and OPENROUTER_FALLBACK_MODEL

**Next LO stage:**
Managing — monitor which model is actually being used in practice (`model_used` field) and whether the fallback is triggered frequently enough to warrant a paid model.

**What I can now do (that I couldn't before):**
The vision analysis pipeline returns real structured product tags (product_type, product_tags, mood, target_signals, suggested_hashtags) even when one free-tier model is unavailable. The audience segmentation, ad copywriting, and CTA optimization agents now receive meaningful input instead of empty fallback values.

**How I'll know this worked:**
- The `model_used` field in the vision output JSON is non-null for the majority of requests.
- Downstream agents (audience segmentation, ad copy) produce output that references specific product attributes rather than generic defaults.
- The `error` field in the vision output appears rarely (only when both models are simultaneously unavailable).

---

## Decision Log Entry 2

### 0. Context: Why does this question exist?

**Project/assignment this belongs to:**
Marketing Agent POC — initial architecture and model selection phase. Before any pipeline code can be written, the model stack must be chosen.

**Why this matters right now:**
Every agent in the pipeline (vision, audience, copywriter, CTA optimizer) needs a backing LLM. Paid APIs would require budget approval that does not exist. The entire POC is blocked until a viable zero-cost model stack is identified.

**Where this fits:**
- Follows from project brief requirement: validate the concept before committing budget
- Feeds into: Decision #1 (vision model fallback), all downstream agent implementations
- Config: `config.py`

---

### 1. My research question
What model stack can run the full marketing agent pipeline at zero cost during the POC phase?

---

### 2. Current LO stage
[ ] Analyzing    [ ] Advising    [x] Designing    [ ] Realizing    [ ] Managing

---

### 3. What makes a good decision here?

**My criteria for success:**
- **C1 — Zero monetary cost:** No API charges incurred during POC development and testing.
- **C2 — Full pipeline coverage:** Every agent (vision, audience, copywriter, CTA optimizer) must have a model that can run its task.
- **C3 — Acceptable quality for POC demonstration:** Output must be coherent enough to demonstrate the concept to stakeholders, even if not production-grade.

---

### 4. What I decided
Use OpenRouter free-tier models (nvidia/nemotron-nano and meta-llama/llama-3.2-11b-vision-instruct) for the vision agent, and local Ollama running mistral:7b for all text-generation agents (audience, copywriter, CTA optimizer).

---

### 5. Why this decision

**Method I used:**
Surveyed available free options: OpenRouter's free-tier model catalog for vision-capable models, and Ollama's local model library for text generation.

**What I found/observed:**
1. OpenRouter offers several free vision-language models. Nemotron 12B VL and Llama 3.2 11B Vision Instruct both accept image input at no cost.
2. Ollama runs entirely locally with no API fees. Mistral 7B is small enough to run on consumer hardware and produces reasonable instruction-following output.
3. The split architecture (cloud for vision, local for text) avoids relying on a single provider for everything.

**Evidence & artifacts:**
- OpenRouter free-tier models: nemotron-nano-12b-v2-vl:free, llama-3.2-11b-vision-instruct:free
- Ollama local model: mistral:7b
- Config: `config.py` — OPENROUTER_MODEL, OPENROUTER_FALLBACK_MODEL, OLLAMA_MODEL

**What this means:**
Vision requires cloud-hosted models because local vision inference is too resource-intensive. Text generation can run locally via Ollama, keeping that portion fully offline and free.

**So I decided:**
The hybrid stack (OpenRouter free tier for vision + Ollama local for text) covers all pipeline stages at zero cost. The tradeoff is free-tier congestion and rate limits on the vision side, which Decision #1 mitigates with the fallback pattern.

---

### 6. Does this hold up?

**How well this meets my criteria:**
- C1 — Zero monetary cost: [checkmark] Both OpenRouter free tier and Ollama local incur $0 in API charges.
- C2 — Full pipeline coverage: [checkmark] Vision agent uses OpenRouter; audience, copywriter, CTA optimizer all use Ollama/mistral:7b.
- C3 — Acceptable quality for POC: [yellow] Mistral 7B is adequate for structured text generation but occasionally produces inconsistent JSON keys (see Decision #6). Free-tier vision models intermittently return 502 errors.

**Assumptions I'm making:**
- OpenRouter will continue offering free-tier vision models for the duration of the POC.
- The local machine has enough resources to run Ollama with mistral:7b without unacceptable latency.
- Free-tier rate limits and congestion are tolerable for development and demo purposes.

**What surprised me:**
Free-tier congestion is real and unpredictable — the vision models intermittently return 502 errors even during off-peak hours. This was anticipated but more frequent than expected, which motivated the fallback pattern in Decision #1.

---

### 7. What this unlocks

**Implementation evidence:**
- `config.py` — full model configuration
- `agents/vision.py` — OpenRouter integration
- `agents/audience.py`, `agents/copywriter.py`, `agents/cta_optimizer.py` — Ollama integration

**Next LO stage:**
Realizing — implement each agent against the chosen model stack.

**What I can now do (that I couldn't before):**
The full pipeline (image analysis, audience segmentation, ad copy generation, CTA optimization) can be developed and tested end-to-end without any API costs. This removes the budget blocker entirely.

**How I'll know this worked:**
- All four pipeline stages produce non-error output for a test product image.
- No charges appear on the OpenRouter billing dashboard.
- Ollama responds within a reasonable time (under 30 seconds per agent call on the dev machine).

---

## Decision Log Entry 3

### 0. Context: Why does this question exist?

**Project/assignment this belongs to:**
Marketing Agent POC — UI/branding pass during the Realizing phase.

**Why this matters right now:**
The Flask app's UI displayed "TikTok Ad Generator" in titles and headings. This name misrepresents the project's scope and gives stakeholders (and evaluators) the wrong mental model of what the system does. The branding needed to be corrected before any demo or presentation.

**Where this fits:**
- UI templates: Flask HTML templates (headings, page titles)
- Project identity: affects how the project is perceived by anyone who sees it

---

### 1. My research question
How should the project be branded to reflect its full scope as a marketing agency replacement, not just a TikTok ad tool?

---

### 2. Current LO stage
[ ] Analyzing    [ ] Advising    [ ] Designing    [x] Realizing    [ ] Managing

---

### 3. What makes a good decision here?

**My criteria for success:**
- **C1 — Accurate scope representation:** The name and branding must communicate that this is a multi-capability marketing platform, not a single-channel ad generator.
- **C2 — Future-proof:** The name should not need to change when new platforms or agent types are added.
- **C3 — Professional presentation:** The branding should look credible in a demo or portfolio context.

---

### 4. What I decided
Rename all UI titles and headings from "TikTok Ad Generator" to "Marketing Agent -- AI-Powered Campaign Studio" for the main app title, and "Campaign Report" for the results page heading.

---

### 5. Why this decision

**Method I used:**
Direct feedback from the user during the session, who flagged the existing branding as misleading.

**What I found/observed:**
The user explicitly stated: "this gives bad context for this project. This project is a replacement for a marketing agency." The TikTok-specific naming was a leftover from the initial prototype scope and no longer reflected the project's ambition.

**Evidence & artifacts:**
- User feedback during session (verbatim: "this gives bad context for this project")
- Updated templates: Flask HTML templates with new titles/headings

**What this means:**
The naming was actively harmful to how the project would be perceived. "TikTok Ad Generator" implies a narrow, single-purpose tool. "Marketing Agent" implies an autonomous system that can handle multiple marketing tasks — which is the actual goal.

**So I decided:**
"Marketing Agent -- AI-Powered Campaign Studio" communicates both the autonomous agent nature and the broad campaign scope. "Campaign Report" for the output page is platform-agnostic and works whether the output is for TikTok, Instagram, or any future channel.

---

### 6. Does this hold up?

**How well this meets my criteria:**
- C1 — Accurate scope representation: [checkmark] "Marketing Agent" and "Campaign Studio" clearly indicate a multi-capability platform.
- C2 — Future-proof: [checkmark] Neither the app title nor "Campaign Report" references any specific platform. Adding Instagram or Facebook support later requires no rebrand.
- C3 — Professional presentation: [checkmark] "AI-Powered Campaign Studio" reads as a professional product name suitable for demos and portfolios.

**Assumptions I'm making:**
- The project will indeed expand beyond TikTok ad generation.
- Stakeholders/evaluators will see the UI and form impressions based on the branding.

**What surprised me:**
Nothing technically surprising — this was a straightforward naming correction. The lesson is that branding decisions made early in prototyping tend to persist unless explicitly challenged. The "TikTok Ad Generator" name was never a deliberate decision; it was just the first thing typed during initial scaffolding.

---

### 7. What this unlocks

**Implementation evidence:**
- Updated Flask templates with new titles/headings

**Next LO stage:**
Managing — monitor whether the branding communicates effectively during demos and feedback sessions.

**What I can now do (that I couldn't before):**
The project can be demoed or submitted without requiring a verbal disclaimer that "it's actually more than a TikTok tool." The UI now speaks for itself.

**How I'll know this worked:**
- No stakeholder or evaluator describes the project as "just a TikTok ad tool" after seeing the UI.
- The branding still fits if/when new marketing channels are added.

---

## Decision Log Entry 4

### 0. Context: Why does this question exist?

**Project/assignment this belongs to:**
Marketing Agent POC — vision agent redesign during the Realizing phase. The vision agent is the first pipeline stage and its output schema directly determines what downstream agents can work with.

**Why this matters right now:**
The original vision agent prompt asked for generic image analysis ("analyze this image for a TikTok ad"), producing vague visual descriptions. The audience segmentation agent (audience.py) needs specific buyer-intent signals to create meaningful personas, not just "the image contains a product on a white background."

**Where this fits:**
- Pipeline order: vision.py -> audience.py -> copywriter.py -> cta_optimizer.py
- `agents/vision.py` — prompt and output schema
- Downstream consumer: `agents/audience.py` uses vision output to derive audience personas

---

### 1. My research question
What should the vision agent's prompt and output schema look like to drive meaningful audience segmentation downstream?

---

### 2. Current LO stage
[ ] Analyzing    [ ] Advising    [ ] Designing    [x] Realizing    [ ] Managing

---

### 3. What makes a good decision here?

**My criteria for success:**
- **C1 — Buyer-intent signal extraction:** The vision output must include explicit cues about who would buy this product (not just what it looks like).
- **C2 — Structured downstream consumption:** Output keys must map directly to what audience.py needs as input — no manual interpretation required.
- **C3 — Richer than generic tagging:** Output must go beyond visual attributes (color, shape) to include materials, use-case, lifestyle fit, and target demographics.

---

### 4. What I decided
Redesign the vision agent as a "product analyst" rather than an "image tagger." Replace the `visual_attributes` output field with `product_tags` (materials, use-case, lifestyle fit) and add a new `target_signals` field containing explicit buyer cues (e.g., "eco-conscious", "fitness enthusiast").

---

### 5. Why this decision

**Method I used:**
Traced the data flow from vision output through audience.py to copywriter.py, identifying what information was missing at each handoff.

**What I found/observed:**
1. The original vision output contained `visual_attributes` like "white background", "product centered" — useful for image search but useless for audience segmentation.
2. audience.py was essentially guessing at buyer personas because it had no product-specific signals to work with.
3. By adding `product_tags` (materials, use-case, lifestyle fit) and `target_signals` (buyer-intent cues), the vision agent now extracts the exact information audience.py needs.

**Evidence & artifacts:**
- `agents/vision.py` — redesigned system prompt framing the model as a "product analyst"
- Output schema: `product_tags`, `target_signals`, `mood`, `suggested_hashtags`
- `agents/audience.py` — now injects both `product_tags` and `target_signals` into its prompt

**What this means:**
The vision agent is no longer just describing what it sees — it is interpreting the image through a marketing lens, extracting the same kind of product intelligence a human marketing analyst would.

**So I decided:**
The prompt redesign and schema change give audience.py direct access to buyer-intent signals derived from the product image itself, not just the text description the user provided. This grounds the entire pipeline in visual evidence.

---

### 6. Does this hold up?

**How well this meets my criteria:**
- C1 — Buyer-intent signal extraction: [checkmark] `target_signals` explicitly contains buyer persona cues like "eco-conscious", "fitness enthusiast", "budget-conscious parent."
- C2 — Structured downstream consumption: [checkmark] audience.py reads `product_tags` and `target_signals` directly from the vision output JSON — no parsing or interpretation layer needed.
- C3 — Richer than generic tagging: [checkmark] `product_tags` includes materials, use-case, and lifestyle fit. Combined with `target_signals`, this is substantially richer than the old `visual_attributes`.

**Assumptions I'm making:**
- Free-tier vision models can reliably extract marketing-relevant signals (not just visual features) when prompted correctly.
- The "product analyst" framing in the system prompt is sufficient to steer the model toward marketing-oriented output.
- `target_signals` are accurate enough to drive audience segmentation — the model is inferring buyer intent, which is inherently speculative.

**What surprised me:**
The free-tier vision models responded well to the product analyst framing. When asked to be a "visual product analyst for a digital marketing agency," the output quality shifted noticeably from generic descriptions to marketing-relevant insights. Prompt framing mattered more than model size here.

---

### 7. What this unlocks

**Implementation evidence:**
- `agents/vision.py` — redesigned prompt and output schema
- `agents/audience.py` — now consumes `product_tags` and `target_signals`

**Next LO stage:**
Managing — evaluate whether the target_signals produced by vision models are accurate enough to produce useful audience personas.

**What I can now do (that I couldn't before):**
Audience segmentation is now grounded in visual product evidence rather than relying solely on the user's text description. The personas generated by audience.py reference specific product attributes (materials, use-cases) that are visible in the image.

**How I'll know this worked:**
- audience.py output references specific product_tags and target_signals from the vision output (not generic personas).
- The ad copy produced by copywriter.py contains product-specific language that traces back to vision-extracted tags.

---

## Decision Log Entry 5

### 0. Context: Why does this question exist?

**Project/assignment this belongs to:**
Marketing Agent POC — pipeline architecture design. Determining the right number of pipeline stages and what each stage is responsible for.

**Why this matters right now:**
The initial pipeline was vision -> copywriter (two stages). The copywriter was producing generic ad copy because it had no audience context. Adding audience segmentation as a separate stage could fix this, but it also adds complexity and another LLM call (latency + potential failure point).

**Where this fits:**
- Pipeline architecture: `app.py` orchestration
- New file: `agents/audience.py`
- Downstream: `agents/copywriter.py` now depends on audience output
- Related: Decision #4 (vision redesign provides the input audience.py needs)

---

### 1. My research question
Should audience segmentation be a separate pipeline stage between vision analysis and ad copywriting?

---

### 2. Current LO stage
[ ] Analyzing    [ ] Advising    [x] Designing    [ ] Realizing    [ ] Managing

---

### 3. What makes a good decision here?

**My criteria for success:**
- **C1 — Copy quality improvement:** Ad copy must be noticeably more targeted and persona-specific compared to the two-stage pipeline.
- **C2 — Standalone deliverable value:** The audience analysis should be useful on its own (visible in the Campaign Report), not just an invisible intermediate step.
- **C3 — Acceptable complexity cost:** Adding a third LLM call should not make the pipeline unreliable or unacceptably slow for POC demos.

---

### 4. What I decided
Insert audience.py as a dedicated pipeline stage between vision and copywriter. It derives persona_label, age_range, interests, and platform_behavior from the vision output's product_tags and target_signals, plus the user's text description. Copywriter.py receives this audience data and injects persona context into its system prompt.

---

### 5. Why this decision

**Method I used:**
Analyzed the information gap between vision output and what a copywriter needs to write targeted ad copy. A real marketing agency always defines a target audience before writing copy — this pipeline should mirror that workflow.

**What I found/observed:**
1. Without audience context, copywriter.py wrote generic ad copy like "Check out this amazing product!" — no persona targeting, no tone adaptation.
2. With audience data injected (persona_label, age_range, interests), the copywriter prompt becomes: "Target audience: {persona_label} (age {age_range}), interested in {interests}" — giving the model concrete constraints to write against.
3. The audience analysis itself (persona, demographics, platform behavior) is a valuable deliverable for the Campaign Report, not just plumbing.

**Evidence & artifacts:**
- `agents/audience.py` — new pipeline stage
- `agents/copywriter.py` — updated system prompt with audience injection: "Target audience: {persona_label} (age {age_range}), interested in {interests}"
- Pipeline order: vision.py -> audience.py -> copywriter.py -> cta_optimizer.py

**What this means:**
The three-stage pipeline mirrors the real agency workflow: analyze the product, define the audience, then write copy for that audience. Each stage has a clear input/output contract and produces a standalone deliverable.

**So I decided:**
A dedicated audience stage is worth the added complexity because it solves the generic-copy problem and produces a second deliverable (audience analysis) for the Campaign Report. The alternative — having the copywriter infer its own audience — would conflate two distinct analytical tasks and produce less transparent results.

---

### 6. Does this hold up?

**How well this meets my criteria:**
- C1 — Copy quality improvement: [checkmark] Copywriter output now references specific persona attributes. The system prompt constrains the model to write for a defined audience rather than "everyone."
- C2 — Standalone deliverable value: [checkmark] The Campaign Report displays the audience persona (label, age range, interests, platform behavior) as its own section.
- C3 — Acceptable complexity cost: [yellow] Adding a third Ollama call increases total pipeline latency. On the dev machine, each Ollama call takes 10-20 seconds, so the full pipeline is now 40-80 seconds. Acceptable for POC demos but would need optimization for production.

**Assumptions I'm making:**
- Ollama/mistral:7b can produce useful audience segmentation from product tags and description alone (no real market data).
- The audience personas are plausible enough for POC demonstration, even if not validated against real customer data.
- Pipeline latency of 40-80 seconds is tolerable for POC demos where stakeholders expect to wait.

**What surprised me:**
The audience stage had a bigger impact on copy quality than expected. Even a rough persona (e.g., "Eco-Conscious Millennial, age 25-34, interested in sustainable living") gave the copywriter enough context to produce noticeably more specific and engaging ad copy. The constraint of writing for someone specific is more valuable than a detailed product description alone.

---

### 7. What this unlocks

**Implementation evidence:**
- `agents/audience.py` — audience segmentation agent
- `agents/copywriter.py` — persona-aware system prompt
- `app.py` — updated pipeline orchestration (4 stages)

**Next LO stage:**
Realizing — implement and test the full four-stage pipeline end-to-end.

**What I can now do (that I couldn't before):**
Ad copy is persona-targeted rather than generic. The Campaign Report now includes an audience analysis section that shows who the marketing is aimed at — a deliverable a real agency would produce.

**How I'll know this worked:**
- Ad copy references the persona's interests or demographics (e.g., "As someone who cares about sustainability..." for an eco-conscious persona).
- The Campaign Report's audience section contains a specific persona_label, age_range, and interests — not "general audience."

---

## Decision Log Entry 6

### 0. Context: Why does this question exist?

**Project/assignment this belongs to:**
Marketing Agent POC — CTA optimizer agent, Realizing phase. This was a live production bug discovered during the first real end-to-end test run.

**Why this matters right now:**
The CTA optimizer agent asks Ollama/mistral:7b to return two CTA variants as JSON keys. The Jinja2 template expects `variant_1` and `variant_2`. If the model returns different key names (which it does), the Flask app crashes with a 500 error. The entire demo is broken.

**Where this fits:**
- `agents/cta_optimizer.py` — JSON output parsing
- Flask templates — expect `variant_1` and `variant_2` keys
- Live bug: Jinja2 UndefinedError crashed the app during the first test

---

### 1. My research question
How should the CTA optimizer handle inconsistent JSON key naming from Ollama/mistral when the downstream template expects exact key names?

---

### 2. Current LO stage
[ ] Analyzing    [ ] Advising    [ ] Designing    [x] Realizing    [ ] Managing

---

### 3. What makes a good decision here?

**My criteria for success:**
- **C1 — No 500 crashes:** The CTA optimizer must never crash the app due to key naming variations from the model.
- **C2 — Handles observed variants:** Must normalize at least the key formats actually observed: "Variant 1", "variant1", "Variant_1", "variant 1".
- **C3 — Transparent normalization:** The normalization logic should be obvious and maintainable, not a fragile regex.

---

### 4. What I decided
Add key normalization logic in cta_optimizer.py after JSON parsing. The normalizer lowercases, strips spaces, and maps common patterns ("Variant 1", "variant1", "Variant_1", etc.) to canonical "variant_1" / "variant_2" keys.

---

### 5. Why this decision

**Method I used:**
Diagnosed the live 500 error, identified the root cause as a key mismatch between model output and template expectation, then implemented defensive normalization.

**What I found/observed:**
1. The live error was: `jinja2.exceptions.UndefinedError: 'dict object' has no attribute 'variant_1'`
2. Ollama/mistral:7b returned the key as "Variant 1" (capitalized, with a space) instead of the expected "variant_1" (lowercase, with underscore).
3. This is inherent to LLM text generation — even with a JSON schema in the prompt, small models like mistral:7b do not reliably follow exact key naming conventions.

**Evidence & artifacts:**
- Live 500 error: `jinja2.exceptions.UndefinedError: 'dict object' has no attribute 'variant_1'`
- `agents/cta_optimizer.py` — key normalization logic after JSON parse

**What this means:**
Any pipeline that relies on exact JSON keys from a small LLM needs defensive normalization. The model will not always follow the schema exactly, and the cost of failure (500 crash) is too high to leave this to chance.

**So I decided:**
Post-parse key normalization is the simplest fix that handles the problem at the right layer (data transformation, not prompt engineering). Trying to fix this with better prompting alone would be fragile — the model might comply 90% of the time but still crash the app on the other 10%.

---

### 6. Does this hold up?

**How well this meets my criteria:**
- C1 — No 500 crashes: [checkmark] The normalizer catches all observed key variants and maps them to the expected canonical form. The template always receives `variant_1` and `variant_2`.
- C2 — Handles observed variants: [checkmark] Tested against "Variant 1", "variant1", "Variant_1", and "variant 1" — all normalize correctly.
- C3 — Transparent normalization: [checkmark] The logic is a straightforward lowercase + replace pattern, not a regex. Easy to extend if new variants appear.

**Assumptions I'm making:**
- The model will only produce variants of "variant_1" and "variant_2" — not completely different key names like "option_a" or "cta_1."
- Two variants are always returned. If the model returns only one, a different error would occur (not addressed by this fix).

**What surprised me:**
Mistral:7b does not reliably follow JSON key naming even when the prompt includes an explicit example schema. This is a general lesson for working with small local models: always normalize LLM-generated structured output before consuming it in templates or downstream code.

---

### 7. What this unlocks

**Implementation evidence:**
- `agents/cta_optimizer.py` — key normalization logic

**Next LO stage:**
Managing — monitor whether new key variants appear that the normalizer does not handle.

**What I can now do (that I couldn't before):**
The CTA optimizer results display correctly in the Campaign Report regardless of how mistral:7b names its output keys. The demo no longer crashes on the results page.

**How I'll know this worked:**
- Zero 500 errors on the results page across multiple test runs with different product images.
- The Campaign Report consistently displays both CTA variants.

---

## Decision Log Entry 7

### 0. Context: Why does this question exist?

**Project/assignment this belongs to:**
Marketing Agent POC — repository hygiene and credential management before pushing to GitHub.

**Why this matters right now:**
The project uses an OpenRouter API key stored in `config.py`. If this file is committed to Git and pushed to GitHub, the API key is publicly exposed. Even though the free tier has limited billing, the key could be used by anyone who finds it.

**Where this fits:**
- `config.py` — contains OPENROUTER_API_KEY
- `.gitignore` — must exclude config.py
- `config.example.py` — template for new developers

---

### 1. My research question
How should API credentials be managed so the repository can be safely published to GitHub?

---

### 2. Current LO stage
[ ] Analyzing    [ ] Advising    [ ] Designing    [x] Realizing    [ ] Managing

---

### 3. What makes a good decision here?

**My criteria for success:**
- **C1 — No credentials in Git history:** The real API key must never appear in any committed file.
- **C2 — Onboarding clarity:** A new developer cloning the repo must immediately understand what credentials are needed and where to put them.
- **C3 — Minimal setup friction:** The solution should not require environment variable managers, secret vaults, or other tooling beyond basic Git.

---

### 4. What I decided
Add `config.py` to `.gitignore` so it is never committed. Create and commit `config.example.py` with placeholder values that show the required configuration structure.

---

### 5. Why this decision

**Method I used:**
Applied standard open-source credential management practice: gitignore the real config, commit an example template.

**What I found/observed:**
1. `config.py` contains `OPENROUTER_API_KEY` with a real key value.
2. The `.gitignore` pattern ensures `config.py` is excluded from all future commits.
3. `config.example.py` contains `OPENROUTER_API_KEY = "your-openrouter-api-key-here"` and all other config values, serving as both documentation and template.

**Evidence & artifacts:**
- `.gitignore` — includes `config.py`
- `config.example.py` — committed template with placeholder values

**What this means:**
The repo is safe to push publicly. Anyone cloning it copies `config.example.py` to `config.py` and fills in their own key.

**So I decided:**
The gitignore + example file pattern is the simplest approach that meets all criteria without adding tooling dependencies. Environment variables (via .env files or os.environ) would be more "correct" for production, but for a POC with a single secret, the config file pattern is simpler and sufficient.

---

### 6. Does this hold up?

**How well this meets my criteria:**
- C1 — No credentials in Git history: [checkmark] `config.py` is gitignored. As long as it was never committed before being added to `.gitignore`, the key is safe.
- C2 — Onboarding clarity: [checkmark] `config.example.py` explicitly shows every required config value with descriptive placeholder names.
- C3 — Minimal setup friction: [checkmark] Copy one file and edit one value. No additional tooling required.

**Assumptions I'm making:**
- `config.py` was never committed to Git before being added to `.gitignore`. If it was, the key exists in Git history and the repo should not be pushed without history rewriting.
- Only one secret (OpenRouter API key) needs management. If more secrets are added later, a `.env` file approach might be cleaner.

**What surprised me:**
Nothing surprising here — this is a well-established pattern. The main value of logging this decision is documenting that credential management was deliberately considered, not accidentally overlooked.

---

### 7. What this unlocks

**Implementation evidence:**
- `.gitignore` — config.py excluded
- `config.example.py` — committed template

**Next LO stage:**
Managing — verify the key never appears in Git history before pushing to a public repository.

**What I can now do (that I couldn't before):**
The repository can be safely pushed to GitHub. New developers can clone and set up the project by following the config.example.py template.

**How I'll know this worked:**
- `git log --all -p | grep "sk-or-"` returns zero results (no API key in history).
- A fresh clone of the repo fails gracefully with a clear error when config.py is missing, prompting the user to create it.

---

## Decision Log Entry 8

### 0. Context: Why does this question exist?

**Project/assignment this belongs to:**
Marketing Agent POC — Ollama integration debugging during the Realizing phase.

**Why this matters right now:**
Three of the four pipeline agents (audience, copywriter, CTA optimizer) use Ollama's local API. None of them could reach the model because the model tag in config.py was wrong. The entire text-generation side of the pipeline was returning errors.

**Where this fits:**
- `config.py` — OLLAMA_MODEL setting
- All Ollama-backed agents: `agents/audience.py`, `agents/copywriter.py`, `agents/cta_optimizer.py`

---

### 1. My research question
What is the correct Ollama model tag format required for the API to find a locally installed model?

---

### 2. Current LO stage
[ ] Analyzing    [ ] Advising    [ ] Designing    [x] Realizing    [ ] Managing

---

### 3. What makes a good decision here?

**My criteria for success:**
- **C1 — Model reachable:** All three Ollama agents must successfully connect to the model without errors.
- **C2 — Correct tag format documented:** The config must use the exact tag that Ollama requires, so this issue does not recur.

---

### 4. What I decided
Change `OLLAMA_MODEL` in config.py from `"mistral"` to `"mistral:7b"` — the full model tag including the version/size suffix.

---

### 5. Why this decision

**Method I used:**
Diagnosed the error returned by Ollama's API when using the short tag, then tested with the full tag.

**What I found/observed:**
1. With `OLLAMA_MODEL = "mistral"`, Ollama returned: `{"error":"model 'mistral' not found"}`
2. With `OLLAMA_MODEL = "mistral:7b"`, all three agents connected successfully.
3. Ollama requires the full tag (`name:version`) even when only one version is installed. The short name alone is not resolved to the installed version.

**Evidence & artifacts:**
- Error from Ollama API: `{"error":"model 'mistral' not found"}`
- Fix in `config.py`: `OLLAMA_MODEL = "mistral:7b"`

**What this means:**
Ollama's model resolution does not fall back to the only installed version of a model. The tag must be exact. This is different from Docker (where `image` resolves to `image:latest`) and is a potential gotcha for anyone setting up Ollama for the first time.

**So I decided:**
Always use the full `name:version` tag in Ollama config. The short name behavior is not reliable and caused a complete pipeline failure.

---

### 6. Does this hold up?

**How well this meets my criteria:**
- C1 — Model reachable: [checkmark] All three Ollama agents (audience, copywriter, CTA optimizer) successfully connect and receive responses after the fix.
- C2 — Correct tag format documented: [checkmark] `config.py` now uses `"mistral:7b"` and `config.example.py` documents this as the expected format.

**Assumptions I'm making:**
- The `mistral:7b` tag will remain valid across Ollama updates. If Ollama changes its tagging scheme, this config value would need updating.
- Other models pulled in the future will also require the full `name:version` tag.

**What surprised me:**
Ollama does not resolve short model names to installed versions. Coming from Docker conventions where `image` resolves to `image:latest`, this was unexpected. The error message was clear ("model 'mistral' not found"), but the root cause was not obvious until you know that Ollama requires the full tag.

---

### 7. What this unlocks

**Implementation evidence:**
- `config.py` — `OLLAMA_MODEL = "mistral:7b"`

**Next LO stage:**
Managing — the model tag is now correct and all Ollama agents are functional.

**What I can now do (that I couldn't before):**
All three Ollama-backed pipeline agents (audience segmentation, ad copywriting, CTA optimization) can reach the model and produce output. The text-generation side of the pipeline is fully operational.

**How I'll know this worked:**
- A health check / model ping to Ollama returns success for "mistral:7b".
- All three agents return non-error output in an end-to-end pipeline test.
## Decision Log Entry 9

### 0. Context: Why does this question exist?

**Project/assignment this belongs to:**
Marketing Agent POC — foundational research phase. Before building any AI agents, the project needed a grounded understanding of what a real marketing agency does, so the tool's scope could be defined by evidence rather than guesswork.

**Why this matters right now:**
Without a clear mapping of agency functions to tool capabilities, the POC risks either building too much (over-engineering features no agency actually provides) or too little (missing core functions that make the tool credible as an "agency replacement"). The entire agent architecture depends on this decomposition.

**Where this fits:**
- Project brief: "replacement for a marketing agency"
- Feeds into: all pipeline agents (vision, audience, copywriter, CTA optimizer) and the layered build roadmap
- Defines: what is in-scope for the POC vs. deferred to future layers

---

### 1. My research question
What role and function do marketing agencies perform, and which of those functions can form the base of an AI replacement tool?

---

### 2. Current LO stage
[x] Analyzing    [ ] Advising    [x] Designing    [ ] Realizing    [ ] Managing

---

### 3. What makes a good decision here?

**My criteria for success:**
- **C1 — Consistent output across different product types:** The base pipeline should produce coherent, structured output whether the input is a shoe, a skincare product, or a tech gadget.
- **C2 — All base pipeline agents return structured output without crashing:** Every agent in the base layer must return valid structured data under normal conditions.
- **C3 — Output is policy-safe:** No fabricated facts, prices, discounts, guarantees, or medical/financial claims in generated content. Claims must be flagged by guardrails.
- **C4 — Formal test suite / edge case coverage:** Automated tests exist to validate output structure and guardrail behavior across product types.

---

### 4. What I decided
Build in layers, smallest marketing agency functions first ("base"), then add more niche functions as the tool matures — mirroring how smaller agencies offer fewer services than larger ones.

Current base (built in POC):
- Product image analysis (vision tagging producing product tags + buyer signals)
- Audience segmentation (persona derivation from tags)
- Ad copy generation (2 variants, persona-aware)
- CTA optimization (scoring + suggestions)
- Compliance guardrails (claim flagging)

Intentionally descoped from POC (complexity + function priority):
- FR3 Theme selection
- FR6 Landing page skeleton
- FR9 Regeneration
- FR10 Lexicon adherence scoring

Next layer (planned):
- Theme/tone language system
- Landing page skeleton to integrate campaigns into a company's website
- More niche agency functions to be added incrementally

---

### 5. Why this decision

**Method I used:**
Manual industry research (ironpaper.com, setup.us) combined with personal experience working in group/industry marketing projects and own technical experience. No AI was used for the research itself. Six core questions were investigated to decompose the agency function.

**What I found/observed:**
Six questions answered:

1. **What do agencies produce?** Strategy & research, campaigns & media, content & creative, digital products/experiences, sales enablement, analytics & optimization.
2. **Who is involved?** Account management, creative (copywriters, designers, art directors), media planners/buyers, technology & analytics, operations/PM.
3. **Degree of contribution?** Varies by phase: strategy led by account planning, production by creative/tech, distribution by media, measurement by analytics.
4. **Skill overlaps?** Communication and strategic thinking span account/creative/media; analytical skills span account/media/analytics; marketing acumen is foundational across all.
5. **What customers do agencies serve?** B2B (complex buying committees, long cycles) and B2C brands of all sizes.
6. **Who is the audience of agency output?** Buying committees, end consumers, internal sales teams (for enablement assets).

From this decomposition, a POC spec was derived with formal functional and business requirements:

Functional Requirements (POC):
- FR1: Input — image (jpg/png/webp, up to 5MB) + 15-40 word description
- FR2: Vision tagging — category, 3-7 tags, confidence per tag
- FR3: Theme selection — auto or user override, tone/lexicon exposed to later steps (descoped)
- FR4: Campaign generation — 2 ad variants (primary text up to 125 chars, headline up to 40 chars, description up to 30 chars, CTA)
- FR6: Landing page skeleton — H1, subhead, 3 benefit bullets, trust microcopy, alt text (descoped)
- FR7: Guardrails — remove/flag prices, discounts, guarantees, medical/financial claims
- FR8: Output — single JSON + parallel text summary
- FR9: Regeneration — switch theme/channel and regenerate (descoped)
- FR10: Evaluation — per-field character counts + lexicon adherence score 0-100 (descoped)

Business Requirements:
- BR1: Produce a policy-safe mini-campaign from one image + description
- BR2: Maintain internal thematic consistency across outputs
- BR3: Avoid fabricating facts; use placeholders where facts are missing
- BR4: Provide JSON output + readable text summary

**Evidence & artifacts:**
- Industry sources: ironpaper.com, setup.us (agency function breakdowns)
- Personal experience: group/industry marketing projects
- Technical experience: own assessment of what is feasible in a POC
- Requirements spec derived from the research (FR1-FR10, BR1-BR4 listed above)

**What this means:**
A real marketing agency's functions map to a layered architecture. The smallest viable agencies handle product analysis, audience definition, copy creation, and basic compliance — exactly what the POC's base layer covers. Larger agencies add theme systems, landing pages, multi-channel regeneration, and quality scoring — these map to the deferred layers.

**So I decided:**
The layered build order is justified by real agency role decomposition. Base functions come first because they represent the minimum viable agency — the functions even the smallest agency performs. Niche functions (theme selection, landing pages, regeneration, scoring) are deferred because they represent specialization that larger agencies add on top of the base. This avoids over-engineering the POC while documenting exactly what was deferred and why.

---

### 6. Does this hold up?

**How well this meets my criteria:**
- C1 — Consistent output across different product types: [checkmark] Target — not yet fully validated across a wide range of product types, but the pipeline structure supports it.
- C2 — All base pipeline agents return structured output without crashing: [yellow] Mostly working. CTA key normalization fix was needed (Decision #6). No other crash bugs observed, but formal testing is still pending.
- C3 — Output is policy-safe (no fabricated facts, claims flagged): [checkmark] Guardrails are implemented. No fabricated facts observed in manual testing.
- C4 — Formal test suite / edge case coverage: [red x] Not yet built. Identified as the next milestone.

**Assumptions I'm making:**
- The agency function decomposition from two industry sources and personal experience is representative enough to define tool scope.
- The "layered build" analogy (small agency = base functions, large agency = niche functions) holds as a useful architecture guide.
- Descoped features (FR3, FR6, FR9, FR10) can be added incrementally without requiring a major refactor of the base pipeline.
- The POC's base layer is sufficient to demonstrate the concept to stakeholders before investing in niche features.

**What surprised me:**
The agency decomposition revealed that even the simplest agency performs five distinct functions (product analysis, audience definition, copy creation, CTA optimization, compliance). This validated the four-agent pipeline architecture — it was not over-engineered. If anything, the pipeline was missing one function (compliance guardrails) that had to be added based on the research.

---

### 7. What this unlocks

**Implementation evidence:**
- Agency function research: manual analysis of ironpaper.com, setup.us, personal experience
- POC spec: FR1-FR10 and BR1-BR4 derived from the decomposition
- Pipeline agents: vision.py, audience.py, copywriter.py, cta_optimizer.py (base layer)
- Descoped items documented: FR3, FR6, FR9, FR10

**Next LO stage:**
Realizing / Managing — the base layer is built; next steps are formal testing (C4) and beginning the next layer (theme system, landing page skeleton).

**What I can now do (that I couldn't before):**
- The agent structure is justified by real agency role decomposition, not guesswork.
- There is a clear build order: base functions first, niche functions later — preventing over-engineering of the POC.
- Descoped items are documented as deliberate deferrals with specific FR numbers, not forgotten features.
- Success is defined concretely (consistent output across product types) giving an exit criterion for the current layer before building the next.

**How I'll know this worked:**
- The base pipeline produces coherent output for at least 3 different product types (e.g., footwear, skincare, electronics) without crashing.
- The guardrails catch fabricated claims in test cases.
- When the next layer is started, the descoped FR numbers (FR3, FR6, FR9, FR10) serve as the backlog — no scope rediscovery needed.

---

## Decision Log Entry 10

### 0. Context: Why does this question exist?

**Project/assignment this belongs to:**
Marketing Agent POC — adding a RAG (Retrieval-Augmented Generation) layer so that uploaded brand documents (style guides, product specs, compliance policies) can inform the downstream agents. This is a new capability layer on top of the base pipeline.

**Why this matters right now:**
The base pipeline generates ad copy and audience personas from only a product image + short description. Without access to brand-specific documents, the agents have no way to incorporate a company's actual tone guidelines, product details, or compliance requirements. A vector database is needed to store and retrieve document chunks at query time.

**Where this fits:**
- New file: `agents/rag.py` — document ingestion and retrieval
- Config: `config.example.py` — `CHROMA_PERSIST_DIR`, `CHROMA_COLLECTION`
- Downstream: audience, copywriter, and CTA optimizer agents will receive retrieved context
- Related: Decision #9 (layered build — RAG is part of the next capability layer)

---

### 1. My research question
Which vector database should store RAG document embeddings for the marketing agent?

---

### 2. Current LO stage
[ ] Analyzing    [x] Advising    [ ] Designing    [ ] Realizing    [ ] Managing

---

### 3. What makes a good decision here?

**My criteria for success:**
- **C1 — Runs locally with no cloud dependency:** The POC must work entirely offline / on localhost. No hosted database services, no API keys for storage.
- **C2 — Persistent storage across server restarts:** Embeddings must survive app restarts so documents do not need re-ingestion every time.
- **C3 — Minimal setup complexity:** Should install via pip and require no separate server process, database daemon, or Docker container.

---

### 4. What I decided
Use ChromaDB as the vector database, configured with `PersistentClient` to store embeddings on disk in a local directory (`chroma_store/`).

---

### 5. Why this decision

**Method I used:**
Evaluated the primary constraint — local-first storage with no cloud dependency — and selected ChromaDB as the option that best fits the POC's zero-cost, fully-local architecture.

**What I found/observed:**
1. ChromaDB provides `PersistentClient` which writes to a local directory — no server daemon required.
2. It installs as a pure Python pip package (`chromadb`), consistent with the project's existing dependency management.
3. It supports cosine similarity search natively (configured via `metadata={"hnsw:space": "cosine"}`).
4. Alternatives like FAISS were not deeply compared because the driving constraint was local-first simplicity, not raw performance at scale. ChromaDB met the constraint immediately.
5. Cloud-hosted options (Pinecone, Weaviate Cloud) were ruled out because they violate the local-only requirement and would add an API key dependency.

**Evidence & artifacts:**
- `agents/rag.py` lines 11-16 — `PersistentClient` initialization with local path
- `config.example.py` line 12 — `CHROMA_PERSIST_DIR = "chroma_store"`
- `requirements.txt` — `chromadb` dependency added

**What this means:**
ChromaDB gives the project a vector store that behaves like a local file — no infrastructure, no accounts, no network calls for storage. This matches the project's existing architecture where Ollama is also a local service.

**So I decided:**
ChromaDB is the right choice for this POC because the primary constraint was local-first operation with minimal setup, not vector search performance at scale. A more thorough comparison with FAISS would matter for production workloads, but for a POC storing tens to hundreds of document chunks, ChromaDB's developer experience advantage (built-in persistence, pip install, Python-native API) outweighs any theoretical performance difference.

---

### 6. Does this hold up?

**How well this meets my criteria:**
- C1 — Runs locally with no cloud dependency: [checkmark] `PersistentClient` writes to a local directory. No network calls, no API keys, no external services.
- C2 — Persistent storage across server restarts: [checkmark] The `chroma_store/` directory retains all embeddings across app restarts. Verified by the deduplication logic in `rag.py` (lines 83-84) which checks for existing IDs on re-ingestion.
- C3 — Minimal setup complexity: [checkmark] Single pip install. No Docker, no daemon, no config beyond a directory path.

**Assumptions I'm making:**
- The POC will store at most hundreds of document chunks, not millions. ChromaDB's performance characteristics are untested at scale for this project.
- FAISS would not have offered meaningful advantages at this data volume. This assumption is reasonable but unvalidated.
- The `chroma_store/` directory will be gitignored and not grow unmanageably large during POC use.

**What surprised me:**
Nothing unexpected — ChromaDB was a straightforward fit. The main value of logging this is documenting that FAISS and cloud options were consciously excluded (not overlooked), and that the selection was driven by the local-first constraint rather than a feature comparison.

---

### 7. What this unlocks

**Implementation evidence:**
- `agents/rag.py` — ChromaDB integration with PersistentClient
- `config.example.py` — CHROMA_PERSIST_DIR and CHROMA_COLLECTION settings

**Next LO stage:**
Realizing — integrate ChromaDB retrieval into the pipeline so downstream agents receive document context.

**What I can now do (that I couldn't before):**
Documents can be ingested (chunked, embedded, and stored) and retrieved by semantic similarity. The RAG infrastructure exists as a queryable knowledge base that persists across server restarts.

**How I'll know this worked:**
- Ingesting a PDF or text file results in chunks appearing in `chroma_store/` that survive an app restart.
- Querying with a product-related string returns relevant chunks from previously ingested documents.
- The `list_documents()` function returns accurate source and chunk counts.

---

## Decision Log Entry 11

### 0. Context: Why does this question exist?

**Project/assignment this belongs to:**
Marketing Agent POC — RAG embedding model selection. Paired with Decision #10 (ChromaDB as vector store), this determines how text chunks are converted to vector representations for storage and retrieval.

**Why this matters right now:**
ChromaDB stores and searches vectors, but the quality of retrieval depends entirely on the embedding model. A poor embedding model will return irrelevant chunks, which means the downstream agents (audience, copywriter, CTA optimizer) receive noise instead of useful brand context. The model also runs through Ollama locally, so size and speed matter.

**Where this fits:**
- Config: `config.example.py` — `EMBED_MODEL = "nomic-embed-text"`
- `agents/rag.py` lines 22-29 — `_embed()` function calls Ollama's `/api/embed` endpoint
- Related: Decision #10 (ChromaDB), Decision #2 (zero-cost model stack)

---

### 1. My research question
Which embedding model should generate vector representations for RAG document retrieval in the marketing agent?

---

### 2. Current LO stage
[ ] Analyzing    [x] Advising    [ ] Designing    [ ] Realizing    [ ] Managing

---

### 3. What makes a good decision here?

**My criteria for success:**
- **C1 — Text-only efficiency:** The model should be optimized for text embedding specifically, without unnecessary multimodal overhead.
- **C2 — Runs locally via Ollama:** Must be available as an Ollama model, consistent with the project's local-first architecture.
- **C3 — Retrieval quality adequate for brand documents:** Retrieved chunks must be semantically relevant to marketing queries (product descriptions, audience terms, brand guidelines).

---

### 4. What I decided
Use `nomic-embed-text` as the embedding model, run locally through Ollama's `/api/embed` endpoint.

---

### 5. Why this decision

**Method I used:**
Compared `nomic-embed-text` against `mxbai-embed-large` (a model previously used in other work) based on the specific requirements of this use case: pure text embedding for marketing documents.

**What I found/observed:**
1. `mxbai-embed-large` — previously used and familiar. However, it is a larger model designed for broader embedding tasks including multimodal scenarios. For a pure text embedding use case, the additional model size provides minimal benefit.
2. `nomic-embed-text` — a text-only embedding model. Smaller and more efficient because it does not carry multimodal weights. Since the RAG pipeline only embeds text (document chunks and query strings), the text-only specialization is a better architectural fit.
3. Both models are available through Ollama, so the local-first constraint is met by either option.
4. The use case is strictly text-to-text: brand documents (PDFs, text files) are chunked into text, embedded as text, and queried with text strings. No image embedding is needed — the vision pipeline handles images separately via OpenRouter.

**Evidence & artifacts:**
- `config.example.py` line 14 — `EMBED_MODEL = "nomic-embed-text"`
- `agents/rag.py` lines 22-29 — `_embed()` function using Ollama `/api/embed` endpoint
- Prior experience with `mxbai-embed-large` provided the comparison baseline

**What this means:**
When the use case is purely textual, a text-specialized embedding model is more efficient than a general-purpose or multimodal one. The smaller model size means faster embedding during both ingestion and retrieval, with no quality penalty for text-only tasks.

**So I decided:**
`nomic-embed-text` is the better fit because this RAG pipeline is text-only by design. The vision agent handles image understanding separately via OpenRouter — the embedding model never sees images. Choosing a text-specialized model over a larger multimodal one avoids carrying unnecessary weights and reduces embedding latency, which matters when ingesting documents with many chunks.

---

### 6. Does this hold up?

**How well this meets my criteria:**
- C1 — Text-only efficiency: [checkmark] `nomic-embed-text` is a text-specialized model with no multimodal overhead. Smaller download size and faster inference than `mxbai-embed-large`.
- C2 — Runs locally via Ollama: [checkmark] Available as an Ollama model (`ollama pull nomic-embed-text`). Embedding calls go to `localhost:11434/api/embed`.
- C3 — Retrieval quality adequate for brand documents: [yellow] Not yet validated with real brand documents. The model is well-regarded for text embedding tasks, but retrieval quality for marketing-specific terminology (persona names, brand tone descriptors) has not been formally tested.

**Assumptions I'm making:**
- `nomic-embed-text` produces embeddings of sufficient quality for marketing domain text. General-purpose text embedding benchmarks suggest it performs well, but marketing-specific retrieval has not been tested.
- The performance difference between `nomic-embed-text` and `mxbai-embed-large` is meaningful enough to justify the choice. At POC scale (tens of documents), the difference may be negligible in practice.
- No future RAG requirement will need image embeddings. If multimodal RAG is added later, the embedding model choice would need revisiting.

**What surprised me:**
The comparison highlighted a useful general principle: match your model's specialization to your data modality. Using a multimodal embedding model for a text-only pipeline is like using a sledgehammer for a nail — it works, but a hammer is the right tool. This is the same logic that drives the project's separation of vision (OpenRouter) and text generation (Ollama) into different model stacks.

---

### 7. What this unlocks

**Implementation evidence:**
- `config.example.py` — `EMBED_MODEL = "nomic-embed-text"`
- `agents/rag.py` — `_embed()` function using the configured model

**Next LO stage:**
Realizing — with the vector store (ChromaDB) and embedding model (nomic-embed-text) selected, the next step is wiring RAG retrieval into the pipeline so downstream agents receive document context.

**What I can now do (that I couldn't before):**
Text documents can be chunked, embedded with a text-specialized model, stored in ChromaDB, and retrieved by semantic similarity. The full RAG infrastructure (storage + embedding) is in place and ready to be connected to the agent pipeline.

**How I'll know this worked:**
- Embedding a set of brand document chunks completes without errors and produces vectors stored in ChromaDB.
- Querying with a marketing-related string (e.g., "eco-friendly audience targeting") returns chunks from relevant brand documents, not random text.
- Embedding speed is fast enough that ingesting a multi-page PDF does not noticeably delay the user experience (target: under 10 seconds for a typical brand guide).
