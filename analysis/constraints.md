# Constraints
Marketing Agent POC

---

## Technical Constraints

- **Budget:** Zero. No API spend, no paid subscriptions. Every component must have a free tier or run locally.
- **Hardware:** Developer laptop (8GB RAM, no dedicated GPU). Local model inference must run on CPU.
- **Vision inference:** Local vision models (LLaVA, Qwen-VL) require 8–16GB VRAM and run at <3 tokens/s on CPU — too slow. Cloud vision required for image analysis.
- **Model hosting:** Ollama only for local text generation. No Docker, no self-hosted inference server.
- **Dependencies:** pip install only. No external services beyond Ollama and an OpenRouter account.

---

## Functional Constraints

- **Input:** Product image (PNG/JPG/WEBP, ≤16MB) + short description (15–40 words). No other required input.
- **Output scope:** Audience persona, two copy variants, compliance flags, CTA scores. No landing page, no theme selection, no evaluation scoring in the POC.
- **Character limit:** Each ad copy variant ≤150 characters primary text.
- **Compliance:** Must flag guarantee claims, health claims, superlatives, urgency language, scientific claims, weight loss claims. No false negatives acceptable on these categories.
- **Pipeline time:** Complete campaign generation in under 120 seconds.

---

## Design Constraints

- **No session state:** The refinement loop must work without server-side sessions — the full output state travels with each /refine request.
- **No frontend framework:** Plain HTML/CSS/JS only. No React, no build step.
- **Guardrails in code:** Compliance logic cannot live in a prompt. A prompt-based compliance check can hallucinate. Rules must be deterministic.
- **Visible routing:** Agent routing decisions must be shown in the UI. The assignment explicitly requires visible agent collaboration.

---

## Scope Constraints

- **POC only:** The system demonstrates the architecture, not a production deployment. No authentication, no multi-tenancy, no rate limiting.
- **Single product per run:** One image, one description, one campaign. Batch generation is out of scope.
- **Deferred:** Theme selection (FR3), landing page generation (FR6), evaluation scoring (FR10).

---

## Educational Constraints

- **Decision logs required:** Every significant architectural choice must be documented with a research question, evidence, and what it unlocks.
- **Ethics required:** The assignment brief explicitly states "your decision log must grapple with this reality" (job displacement). This is a graded requirement.
- **LO coverage required:** Evidence must exist across all five LO stages — Analyzing, Advising, Designing, Realizing, Managing.
