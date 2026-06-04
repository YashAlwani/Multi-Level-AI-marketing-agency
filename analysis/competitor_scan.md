# Competitor Scan — Why Existing Tools Don't Answer the Research Question
Marketing Agent POC

---

## What this is

A brief scan of existing AI marketing tools, done before the build, to clarify why this project exists and what gap it occupies. The research question is about *agent architecture* — whether specialised agents produce better output than a single generalist. Existing tools answer a different question.

---

## Tools Scanned

### Jasper AI
**What it does:** LLM-powered copywriting tool. Single model, many templates.
**Output:** Ad copy, blog posts, email sequences.
**Architecture:** Single-agent. One LLM call per template fill.
**Why it doesn't answer the research question:** Jasper is a well-engineered monolith — it's what the marketing agent monolith prototype is. The research question is whether decomposing that into specialists with clean handoffs produces better output. Jasper is the baseline, not the answer.

### Copy.ai
**What it does:** Generates marketing copy from a brief. Workflow builder in paid tier.
**Output:** Ad variants, product descriptions, social posts.
**Architecture:** Primarily single-agent. The workflow builder is sequential prompts, not specialist agents with distinct context scopes.
**Why it doesn't answer the research question:** The workflow builder is closer to the multi-agent concept, but the stages share the same model with different prompts rather than agents with genuinely different context inputs. The audience persona is not derived from an independent analysis — it's inferred inline by the copy generator.

### ChatGPT (with browsing or plugins)
**What it does:** General-purpose LLM. Can write ad copy with a good prompt.
**Architecture:** Single model, single context window.
**Why it doesn't answer the research question:** This is the purest version of the monolith. The research question exists because ChatGPT with a marketing prompt produces "general public" as the audience and generic copy. The project tests whether a structured multi-agent pipeline fixes that.

### Canva Magic Write / Adobe Express AI
**What it does:** Integrated copy generation inside design tools.
**Architecture:** Single model, design-context prompt.
**Why it doesn't answer the research question:** These tools optimise for design integration, not copy quality or audience specificity. The audience is assumed, not derived.

---

## The Gap

None of these tools:
1. Derive a target audience from product image signals and use it as a hard constraint for copy generation
2. Run compliance checking as a separate deterministic stage (not a prompted suggestion)
3. Make the agent collaboration visible to the user in the output
4. Allow post-generation refinement that re-runs only the affected pipeline stages

The gap is not "there is no AI copywriting tool." The gap is: **no existing tool treats campaign generation as a multi-agent collaboration problem with visible specialisation and selective re-runs.** That is what this project tests.

---

## What This Means for the Build

The monolith prototype (one Ollama call with a long marketing prompt) is intentionally the same as what Jasper and Copy.ai do at their core. Running it first and comparing its output to the multi-agent pipeline gives the research question a concrete, observable answer rather than a theoretical one.
