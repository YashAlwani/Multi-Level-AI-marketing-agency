# Multi-Level AI Marketing Agency

A Flask-based AI marketing agent that replaces a traditional agency workflow. Upload a product image, describe it, set a tone — and get back audience personas, ad copy variants, CTA scores, and compliance flags in seconds.

Built as a local-first POC: no cloud databases, no paid inference for text generation.

---

## What it does

Given a product image + description + tone, the pipeline produces:

- **Audience persona** — age range, interests, platform behavior, persona label
- **Two TikTok ad copy variants** — persona-aware, tone-matched, ≤150 chars + CTA
- **CTA analysis** — scores each variant's CTA and suggests a stronger alternative
- **Compliance flags** — regex-based guardrails (no LLM, fast + deterministic)
- **Vision analysis** — product type, tags, buyer signals, mood, hashtags

Optionally, upload brand briefs, product specs, or competitor docs to a **local knowledge base** — retrieved chunks are injected into the audience, copywriter, and CTA stages automatically.

---

## Agent pipeline

```
color.extract()          LOCAL — Pillow / ColorThief
vision.analyze()         OpenRouter (nvidia/nemotron-nano-12b-v2-vl:free, fallback: meta-llama/llama-3.2-11b-vision-instruct:free)
rag.retrieve()           LOCAL — ChromaDB + nomic-embed-text via Ollama
audience.segment()       Ollama — mistral:7b
copywriter.generate()    Ollama — mistral:7b
guardrails.check()       LOCAL — pure Python regex
cta_optimizer.optimize() Ollama — mistral:7b
```

See `ARCHITECTURE.md` for the full pipeline diagram.

---

## Setup

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com) running locally with the following models pulled:

```bash
ollama pull mistral:7b
ollama pull nomic-embed-text
```

- An [OpenRouter](https://openrouter.ai) API key (free tier works)

### Install

```bash
git clone https://github.com/YashAlwani/Multi-Level-AI-marketing-agency.git
cd Multi-Level-AI-marketing-agency
pip install -r requirements.txt
```

### Configure

```bash
cp config.example.py config.py
```

Edit `config.py` and set your `OPENROUTER_API_KEY`. Everything else works out of the box.

### Run

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000).

---

## Knowledge base (RAG)

Upload PDF, TXT, or MD files from the home page or at `/docs`. Documents are chunked, embedded locally via `nomic-embed-text`, and stored in ChromaDB. On each campaign run, the top 4 most relevant chunks are retrieved and injected into the audience, copywriter, and CTA prompts.

- Duplicate uploads are safe — content is hashed and skipped if already indexed
- The knowledge base persists in `chroma_store/` (local, git-ignored)

---

## File layout

```
app.py                  Flask routes + pipeline orchestration
config.py               Secrets + runtime config (git-ignored)
config.example.py       Template — copy to config.py
agents/
  vision.py             OpenRouter vision analysis (primary + fallback model)
  color.py              Local color palette extraction
  audience.py           Ollama audience segmentation
  copywriter.py         Ollama ad copy generation
  guardrails.py         Regex compliance checks
  cta_optimizer.py      Ollama CTA scoring + suggestions
  rag.py                ChromaDB ingestion + retrieval
templates/
  index.html            Upload form + knowledge base upload
  result.html           Campaign report
  docs.html             Knowledge base document viewer
ARCHITECTURE.md         Full pipeline diagram
DECISIONS.md            Decision log — tool choices and rationale
```

---

## Stack

| Layer | Tool |
|---|---|
| Web framework | Flask |
| Vision inference | OpenRouter (free tier) |
| Text inference | Ollama + mistral:7b |
| Embeddings | Ollama + nomic-embed-text |
| Vector store | ChromaDB (local, persistent) |
| Color extraction | Pillow + ColorThief |
| PDF parsing | pypdf |
