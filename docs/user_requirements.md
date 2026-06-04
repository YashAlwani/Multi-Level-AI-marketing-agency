# User Requirements
Marketing Agent POC

Written before result.html was designed. Describes what the user needs
from the tool — not what the pipeline does technically.

---

## Who is using this

Two personas:

**The small business owner / solo marketer**
No agency. No copywriter on staff. Has a product and wants to run ads.
Knows what their product is; doesn't know what a "target persona" is or
how to write a CTA.

**The marketing student / researcher**
Wants to see how multi-agent systems work in practice. Cares about the
routing decisions, the agent structure, the compliance mechanism —
not just the ad copy output.

The UI must serve both at the same time.

---

## What the user needs from the upload page

- One form, minimal fields: image + description + tone. Nothing else required.
- Clear indication of what "15-40 words" means for the description.
- Progress feedback during generation — a blank screen for 90 seconds feels broken.
- No redirect to a results page that loses context if they hit back.

---

## What the user needs from the result page

**From the campaign report (left column):**
- Audience persona they can actually act on — not "adults interested in wellness"
- Two copy variants that are visibly different from each other, with labels explaining why
- Character counts so they know if a variant is over the platform limit
- Compliance flags with the specific matched text, not just a warning icon
- CTA scores with the reasoning, not just a number
- Raw JSON available for export — some users will want to pipe this into other tools

**From the refinement panel (right column):**
- Sliders for tone, audience age, formality — fast to try, no LLM call until they click Refine
- Chat input for freeform requests ("make the CTA more urgent")
- Visibility into which agents ran on each refinement — this is the multi-agent proof
- A suggestion from the assistant before they have to ask — they don't always know what to fix
- The panel must stay visible while they scroll the report

---

## What the user does NOT need

- A theme picker before generation (deferred — adds friction before value)
- A landing page generator (deferred — out of scope for first iteration)
- An account or login (POC — single-session, no persistence required)
- Explanation of what each agent does (visible routing label is sufficient)
- Multiple campaigns per session (one at a time is the use case)

---

## Trust requirements

The user needs to trust:
1. The persona is derived from the product, not invented
2. The compliance flags mean something real
3. The copy will not include specs or claims not present in the input

Design responses:
1. Vision output (product_tags, target_signals) is shown in the report — user can trace the persona back to it
2. Compliance flags show the matched text, not just a warning — user can evaluate the flag
3. Vision prompt explicitly says "do not invent features not visible in the image or description"
