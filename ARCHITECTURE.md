# Marketing Agent — Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INPUT                               │
│              image (jpg/png/webp) + description + tone          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
               ┌────────────┴────────────┐
               │                         │
               ▼                         ▼
┌──────────────────────┐   ┌──────────────────────────────────────┐
│   color.extract()    │   │         vision.analyze()             │
│   LOCAL — Pillow /   │   │   OPENROUTER (remote, vision-capable)│
│   ColorThief         │   │                                      │
│                      │   │  Primary:                            │
│  → dominant color    │   │    nvidia/nemotron-nano-12b-v2-vl    │
│  → palette (5 swatches)  │  Fallback:                           │
└──────────┬───────────┘   │    meta/llama-3.2-11b-vision-instruct│
           │               │                                      │
           │               │  → product_type                      │
           │               │  → product_tags                      │
           │               │  → target_signals  ◄── feeds next    │
           │               │  → mood                              │
           │               │  → suggested_hashtags                │
           │               │  → model_used                        │
           │               └──────────────┬───────────────────────┘
           │                              │
           │                             ▼
           │              ┌──────────────────────────────────────┐
           │              │       audience.segment()             │
           │              │       OLLAMA — mistral:7b            │
           │              │                                      │
           │              │  inputs: description                 │
           │              │        + product_tags                │
           │              │        + target_signals              │
           │              │        + mood                        │
           │              │                                      │
           │              │  → persona_label                     │
           │              │  → age_range                         │
           │              │  → interests                         │
           │              │  → platform_behavior                 │
           │              └──────────────┬───────────────────────┘
           │                             │
           └──────────────┬──────────────┘
                          │  (color_data + vision_data + audience_data)
                          ▼
          ┌──────────────────────────────────────────┐
          │         copywriter.generate()            │
          │         OLLAMA — mistral:7b              │
          │                                          │
          │  system: persona-aware prompt            │
          │  user:   description, product_tags,      │
          │          dominant color, mood, tone,     │
          │          hashtags                        │
          │                                          │
          │  → variant_1 (str, ≤150 chars + CTA)    │
          │  → variant_2 (str, ≤150 chars + CTA)    │
          └──────────────────┬───────────────────────┘
                             │
                             ▼
          ┌──────────────────────────────────────────┐
          │         guardrails.check()               │
          │         LOCAL — pure Python regex        │
          │                                          │
          │  flags: guarantees, health claims,       │
          │         superlatives, free offers,       │
          │         urgency language, sci. claims,   │
          │         weight loss claims               │
          │                                          │
          │  → clean_copy {variant_1, variant_2}     │
          │  → flags [{variant, matched, reason}]    │
          └──────────────────┬───────────────────────┘
                             │
                             ▼
          ┌──────────────────────────────────────────┐
          │       cta_optimizer.optimize()           │
          │       OLLAMA — mistral:7b                │
          │                                          │
          │  inputs: clean_copy + tone +             │
          │          audience_data                   │
          │                                          │
          │  → variant_1: {original_cta, score 1-10,│
          │                suggestion, reasoning}    │
          │  → variant_2: {original_cta, score 1-10,│
          │                suggestion, reasoning}    │
          └──────────────────┬───────────────────────┘
                             │
                             ▼
          ┌──────────────────────────────────────────┐
          │           CAMPAIGN REPORT                │
          │                                          │
          │  • Audience persona                      │
          │  • Vision analysis (tags + signals)      │
          │  • Color palette                         │
          │  • Ad copy variants (with char count)    │
          │  • CTA scores + suggestions              │
          │  • Compliance flags                      │
          │  • Raw JSON + summary notes              │
          └──────────────────────────────────────────┘


  RUNTIME KEY
  ───────────
  LOCAL        Pillow/ColorThief + regex — no network, instant
  OPENROUTER   Remote vision API — primary + fallback, free tier
  OLLAMA       Local LLM (mistral:7b) — audience, copy, CTA
```