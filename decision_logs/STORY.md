# The Marketing Agent — Build Story

## What this is

A multi-agent AI system that takes a product image and short description and
produces a complete marketing campaign: audience persona, two ad copy variants
with distinct angles, compliance flags, and CTA scores. Built in response to
the Reclamebureau Eva assignment — a Dutch advertising agency that replaced
270 copywriters with AI agents and demonstrated the result on national television.

This is the story of how it was built. Not the cleaned-up version — the actual
sequence, including the wrong turns.

---

## The question

The assignment asked: how do you build a multi-agent system where specialized
AI agents collaborate to produce results that exceed what any single agent
could achieve alone?

Before answering that, a more basic question: what does a marketing agency
actually do?

---

## Six questions

The research phase (A1) worked through six questions about agency function.
What do agencies produce? Who is involved? What are the skill overlaps?

The finding that mattered most: even the smallest agency performs five distinct
functions at minimum viable scale. Product analysis. Audience definition.
Copy generation. Conversion optimization. Compliance review.

These five functions exist because they require genuinely different context
and judgment. The same person who writes the copy cannot also review it for
compliance — they are too close to the copy to flag their own risky claims.
The creative team that defines the audience writes for the audience they imagine
wanting the copy they've already mentally written, not the audience the data
suggests.

Specialization is not a management convenience. It produces better output.
The agency research was the foundation for the agent decomposition. Five functions.
Five agents.

---

## The monolith

The first version was one Ollama call.

System prompt: *"You are a marketing expert. Analyze this product image and write
two TikTok ad variants for a potential customer."*

Output on the eco water bottle test case:

> "Check out this amazing product! Stay hydrated and save the planet. Shop now!"
> "Your next favorite water bottle. Keeps drinks cold all day. Get yours today!"
> Audience: "general public"

Technically correct. Useless in practice. "General public" is not an audience.
Copy written for everyone is written for no one. The two variants had the same
structure. They were not distinct. They could describe any product.

The monolith was not a bad attempt — it was the necessary baseline. Without
running it, the improvement from specialization is a claim. With it, the
improvement is observable.

---

## The specialization

The multi-agent pipeline ran the same input and produced:

> Audience: "Eco-Conscious Millennial Athlete, 25-34, interests: sustainability,
> fitness, zero-waste lifestyle."
>
> Variant 1: "Stay hydrated, stay green. 24h cold, zero plastic compromise.
> For athletes who give back. #LiveGreen"
>
> Variant 2: "Insulated. BPA-free. Built for your gym bag and the planet.
> Shop the change."

Same model. Same image. Same description.

The difference was context injection. The audience agent derived a specific
persona from the product signals. The copywriter received that persona and wrote
for it. Variant 1 opens with identity (emotional hook). Variant 2 opens with specs
(product benefit). They are genuinely distinct because the copywriter prompt
constrains the angles.

This is the core answer to the assignment's question. Specialization improves
output not because the specialists are smarter, but because each one is given
a narrow scope and only the context it needs. The copywriter does not also
define the audience. The audience agent does not also check compliance.

---

## The compliance decision

FR7 required compliance checking. The question was how to do it.

An LLM compliance judge was tested. It missed two of five violations — judging
that "the context makes the guarantee claim acceptable." That is a legal
judgment call an LLM is not qualified to make. A missed guarantee claim in
a published ad is an FTC violation.

The compliance check is pure Python regex. Seven patterns. "Guaranteed" always
triggers. There is no context that makes it not trigger. The regex does not
decide acceptability. It matches or it does not.

guardrails.py is the only agent in the pipeline with no LLM call. It adds
less than one millisecond. It is also the only stage that cannot be wrong
in a direction that causes legal exposure.

---

## The first bugs

After the pipeline ran end-to-end for the first time, two bugs surfaced.

The CTA optimizer returned `"Variant 1"` instead of `"variant_1"`. The Jinja2
template expected `variant_1`. The result was a 500 error on the report page.
Fix: normalize all LLM output keys to snake_case before returning.

The Ollama configuration said `"mistral"`. The correct model name is `"mistral:7b"`.
Ollama does not default to the most recent version of an untagged model name.
Fix: config updated, setup script added to pull the correct tag.

Both bugs were integration mismatches. Unit tests with controlled inputs did not
catch them. The real pipeline did.

---

## The RAG layer

Campaigns were generic when the product had brand guidelines or detailed
specifications not visible in the image. A product manual or brand brief
should be able to influence the output.

ChromaDB and nomic-embed-text were chosen as a stack. Both run locally.
Both install with single commands. ChromaDB handles document persistence and
deduplication. nomic-embed-text is fast enough that ingest completes before
a user runs out of patience during a demo.

The text-only choice was deliberate. The vision agent handles image understanding.
The RAG system retrieves text documents. Mixing modalities in the embedding space
adds complexity without clear benefit for this use case.

---

## The refinement loop

The first result page was a one-shot report. The user read the output, decided
they wanted a different tone, went back, re-uploaded the image, and waited
90 seconds.

This was not a usable workflow.

The refinement panel was designed before it was coded. The wireframe captured
eight layout decisions:

- Sticky right panel (refinement always visible)
- Sliders above chat (deterministic changes first)
- Routing label visible (not a black box)
- Proactive suggestions on page load (the assistant reviews before the user asks)

The routing logic uses a single LLM call to decide which agents need to re-run.
Tone slider moved? Copywriter, guardrails, CTA. Age slider moved? Audience,
copywriter, guardrails, CTA. Vision never re-runs during refinement — the product
did not change.

The stateless design — full output state travels with every /refine request —
was not planned. It emerged from the constraint of wanting the tool deployable
without session infrastructure. It turned out to be simpler and more auditable
than the session-based approach it replaced.

---

## The timeout

During a run with a long product description and four RAG chunks, the copywriter
agent timed out at 60 seconds. mistral:7b had been handling all text generation.
It handled JSON tasks well. For creative prose with rich context, it was too slow.

Three models were tested as copywriter replacements. gemma4:e2b produced
noticeably better copy — more varied sentence structure, stronger emotional hooks.
It ran in 25-40 seconds. It was adopted for the copywriter role.

mistral:7b stayed for everything else (audience, CTA, routing). Its JSON
reliability is better than gemma4 on structured output tasks.

The model split was always available as an architecture. It took a production
timeout to implement it.

---

## The telemetry

Once the pipeline was working, a new question: what is actually happening
across runs?

run_log.jsonl records one line per run: timestamp, run ID, vision model used,
pipeline time, compliance flags, average CTA score, RAG chunks retrieved, persona.

Not content — metrics. The persona label is stored; the copy text is not.
The purpose is to detect trends: is CTA quality improving? Is the fallback
vision model being used frequently? Are runs with RAG context producing better scores?

First findings from the initial run set: the primary vision model (nemotron)
served 8 of 10 runs. Compliance flags appeared in 40% of runs — mostly urgency
language generated without user request. The copywriter prompt may benefit from
an explicit instruction to avoid urgency language by default.

---

## What the system does and does not do

What it does: takes a product image and description, runs five specialized agents,
produces a campaign in 70-90 seconds. The output is specific enough that a
marketer could use it as a starting point without extensive revision.

What it does not do: replace human judgment. The persona is a hypothesis from
training data patterns. The compliance check flags known patterns; novel phrasing
slips through. The copy is a first draft. The routing label shows which agents
ran; it does not show why mistral:7b chose the words it chose.

This system automates what the assignment called "execution." Copywriting iterations,
audience inference, CTA scoring — these are real jobs currently held by people
whose employment rates are declining. The 28% year-over-year drop in copywriter
positions is not a projection. It is documented.

The counterargument is also true: creative leadership, strategic direction, and
quality judgment are growing roles. AI does not replace the account manager who
understands the client's business. It replaces the junior copywriter writing the
third iteration of copy for a product brief they did not write.

That is not a comfortable conclusion. It is the honest one.

The system is ready to run. The decision log documents how it got here.

---

*All decisions documented in the decision_logs/ folder.*
*Source research: A1_agency_function_research.txt, A2_requirements_and_scope.txt*
*Code: app.py, agents/, templates/*
