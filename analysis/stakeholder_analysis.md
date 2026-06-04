# Stakeholder Analysis
Marketing Agent POC

---

## Primary Stakeholder: Small Business Owner / Solo Marketer

**Needs:**
- Campaign output without hiring an agency or knowing prompt engineering
- Two copy variants ready to post, not a rough draft that needs rewriting
- Clear indication of any risky claims before publishing
- Ability to adjust tone and audience without starting over

**Concerns:**
- Is the output actually usable, or is it obviously AI-written?
- Will it hallucinate product specs I didn't provide?
- What do I do if the compliance flags are wrong?

**Success from their perspective:**
- Upload a product image, get two variants, post one with minor edits
- The persona feels accurate to who actually buys this product
- No compliance surprises after publishing

---

## Secondary Stakeholder: Marketing Student / Course Evaluator

**Needs:**
- Visible agent collaboration — not just output, but evidence of which agents ran
- Decision documentation connecting design choices to evidence
- A system that demonstrates specialisation rather than just parallel prompts

**Concerns:**
- Is the multi-agent structure genuinely adding value, or just adding complexity?
- Are the design decisions documented with real evidence?
- Does the system show LO1–LO5 coverage across the full build arc?

**Success from their perspective:**
- The routing label shows which agents ran and why
- Each architectural decision has a before/after comparison or a test result
- The ethics section grapples with real consequences, not generic platitudes

---

## Tertiary Stakeholder: Copywriter / Creative Professional (Displaced)

**Needs:**
- Transparency about what the system can and can't do
- Acknowledgment that this automates real work currently done by people

**Concerns:**
- Will users treat AI copy as finished rather than a starting point?
- Is the compliance check comprehensive enough to catch what a human reviewer would?
- Who is accountable if the output causes harm?

**Success from their perspective:**
- The system is honest about its limits (persona is a hypothesis, not market research)
- Human review is framed as required, not optional
- The DL-08 ethics entry names the displacement data directly

---

## Ethical Stakeholder: Future Users and Affected Workforce

**Needs:**
- Documented accountability gaps before they become production incidents
- Clear framing of what "professional output" means and doesn't mean

**Concerns:**
- Inter-agent error propagation (hallucinated product tag → wrong persona → wrong copy)
- Compliance coverage that appears exhaustive but isn't
- Persona bias from training data distributions

**Success from this perspective:**
- Three accountability gaps documented in DL-08
- Output framed as a starting point requiring human review, not a finished campaign
