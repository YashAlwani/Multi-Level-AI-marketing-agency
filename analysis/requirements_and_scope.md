ANALYZING EVIDENCE — A2
Requirements and Scope Specification
Source: Requirements3.pdf (formal FR/BR/US spec)
Stage: Analyzing
────────────────────────────────────────────────────────────


0. What this document captures

The requirements PDF was written after the agency research (A1) and before
any code. It translates the assignment brief into a formal specification:
functional requirements, business rules, user stories, and acceptance
criteria. Ten FRs were drafted; only five were built in the POC.


1. Functional Requirements — full list with POC status

FR1  Input validation
     Scope: reject non-image files, enforce ≤16MB limit,
            require non-empty description
     Status: [x] BUILT — app.py lines 33-43, allowed_file()

FR2  Vision analysis and tagging
     Scope: product_type, ≥3 product_tags, mood, target_signals,
            suggested_hashtags extracted from image
     Status: [x] BUILT — agents/vision.py, OpenRouter vision models

FR3  Theme selection
     Scope: user picks from 3 campaign themes before copy generates;
            each theme changes tone, color palette reference, hashtags
     Status: [ ] DEFERRED — added complexity without clear output value
                            over the tone slider approach

FR4  Campaign copy generation
     Scope: exactly 2 variants, each ≤150 chars primary text,
            distinct creative angles, clear CTA in each variant
     Status: [x] BUILT — agents/copywriter.py
             Note: variant angle constraint (emotional/benefit) added
             in Realizing phase after observing generic output

FR5  Audience persona
     Scope: persona_label, age_range, interests (list), platform_behavior
     Status: [x] BUILT — agents/audience.py

FR6  Landing page skeleton
     Scope: generate a minimal HTML landing page from campaign output;
            hero copy, CTA button, color palette applied
     Status: [ ] DEFERRED — useful but not core to the campaign proof
                            of concept; output is already professional

FR7  Compliance guardrails
     Scope: flag guarantee claims, health claims, superlatives,
            urgency language, scientific claims, weight loss claims;
            return flags with variant ID, matched text, reason
     Status: [x] BUILT — agents/guardrails.py (7 regex patterns)

FR8  Structured output
     Scope: JSON output with all required keys; human-readable
            summary in addition to raw JSON
     Status: [x] BUILT — app.py output dict, result.html rendering

FR9  Regeneration with different parameters
     Scope: user selects different tone or channel, full pipeline reruns
     Status: [ ] DEFERRED but EVOLVED — became the interactive ReAct
                            refinement loop (richer than a simple re-run)
                            See DL-09 for the design evolution

FR10 Evaluation scoring
     Scope: compare variant quality using a pre-defined lexicon;
            score each variant on clarity, audience fit, urgency
     Status: [ ] DEFERRED — requires a reference lexicon that does not
                            exist yet; CTA scoring (FR8) partially covers this


2. Business Requirements

BR1  Policy-safe output
     No fabricated prices, invented specifications, or unverifiable claims.
     Guardrails (FR7) addresses the most common violation patterns.
     The vision agent is explicitly instructed not to invent features
     not visible in the image or description.

BR2  Thematic consistency
     Color palette extracted from the product image must be referenced
     in copy generation context. The dominant color is passed to the
     copywriter so color references in copy match the actual product.

BR3  No fabricated statistics
     Copy must not include percentage claims, survey data, or clinical
     results that were not present in the input. Guardrails pattern
     "scientific claim" catches "clinically proven" and similar.
     The vision agent prompt explicitly says "do not invent features."

BR4  JSON + text output
     Every pipeline run produces a structured JSON output (for export)
     and a human-readable HTML report (result.html). Both update live
     during the refinement loop.


3. User Stories

US-1  As a small business owner, I want to upload a product photo and
      short description and receive two ready-to-post ad copy variants,
      so I can launch a campaign without hiring an agency.
      Acceptance: ≤2 minutes from upload to visible output.

US-2  As a marketing student, I want to see which agents ran and why,
      so I can understand how the multi-agent pipeline works.
      Acceptance: routing label visible in refinement panel.

US-3  As a compliance reviewer, I want flagged risky claims highlighted,
      so I can decide whether to edit before publishing.
      Acceptance: compliance flags shown with matched text and reason.

US-4  As a product manager, I want to refine the copy by tone and
      audience age without re-running the full pipeline,
      so I can iterate quickly in a live meeting.
      Acceptance: slider changes + Refine button triggers only the
      affected agents, not the vision analysis.

US-5  As a developer evaluating the system, I want to export the full
      campaign JSON with one click,
      so I can integrate the output into other tools.
      Acceptance: /export/<run_id> returns valid JSON with all keys.


4. What the requirements revealed

Compliance is not optional. FR7 was marked as a required functional
requirement — not a nice-to-have. The brief explicitly says "policy-safe
output" (BR1). This made guardrails a mandatory stage in the pipeline,
not an optional quality gate. That had architectural consequences: see DL-06.

FR9 evolved. The original requirement imagined a simple "regenerate with
different theme" button. During Realizing, the refinement loop (ReAct
routing + slider controls + proactive suggestions) became something more
capable and more interesting. The FR9 intent is fully delivered; the
implementation is richer than the spec anticipated.

FR3 was the right deferral. Theme selection would have required a reference
system for what each theme implies across tone, hashtag style, and
color references. Building that before the base pipeline was stable would
have been premature. The tone slider covers the core use case.


*@2ec2ea0f-fd3c-4e92-9fd5-1c2bd1e36f06_Requirements3.pdf · @Project_case.md*
