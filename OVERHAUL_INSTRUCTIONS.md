# Docs Overhaul — Instruction List (apply to any project)

A practical, ordered runbook for repeating this documentation overhaul on a
different project. The **why** lives in `DOCS_OVERHAUL_PLAYBOOK.md`; this file is
the **what to do**, in order. Adapt every path/name — the principles are fixed,
the filenames are not.

---

## 0. One-time toolchain

```
# Node (for diagram + wireframe rendering)
node --version                      # need Node 18+
npm install -g wiremd               # text-first wireframes
# mermaid-cli is fetched on demand via:  npx -y @mermaid-js/mermaid-cli
# Python
pip install reportlab Pillow markdown
# Windows: Microsoft Edge is used headless for wiremd screenshots (already present)
```

---

## 1. Make the docs accurate (no drift)

- [ ] Read the **real source** before writing anything.
- [ ] In every existing doc, fix names to match the code that actually exists;
      delete descriptions of files/classes/flags that don't.
- [ ] Note doc/code mismatches as you go — drift is the worst failure.

## 2. Lead with the GAP (before vs after)

- [ ] Find or create the business-process **as-is vs to-be** artifact (a styled
      `bpm_analysis.html` or similar).
- [ ] Decompose it into Mermaid diagrams: `gap-as-is`, `gap-to-be`, and one per
      scenario. These justify every feature later.

## 3. Stand up the diagram system

- [ ] Create `diagrams/` with one `<name>.mmd` per diagram.
- [ ] Add a plain-text `diagrams/00-INDEX.txt` "point document": for each diagram,
      what it shows · which doc it belongs to · the matching code file.
- [ ] Add a C4 **container** diagram as a flowchart styled with C4 colours
      (person = dark blue, container = mid blue, external = grey) inside a
      `subgraph` boundary — native Mermaid C4 renders messy.
- [ ] Swimlanes/flows: `flowchart TB` (top-to-bottom stays legible in portrait
      PDFs). Sequences: `sequenceDiagram`.
- [ ] **Render high-res:**
      `npx -y @mermaid-js/mermaid-cli -i x.mmd -o x.png -b white -s 3 -w 1600`
      (`-s 3` = sharp on zoom; wider `-w` for wide diagrams like C4).
      Gotcha: builders that skip "png newer than mmd" won't re-render — delete
      stale `.png`s to force it.

## 4. Design docs (per component)

- [ ] Keep the accurate technical `.md` source (inline mermaid ok for GitHub).
- [ ] Write a plain-English `.txt` deliverable: *what this is · the parts · how
      the tricky bit works · if it breaks · why it's built this way (link the
      GAP) · where it lives in the code · diagrams used.*
- [ ] Put a `See the picture: diagrams/<name>.mmd` marker where each diagram
      belongs; the PDF builder embeds the PNG there.
- [ ] Build with a diagram-aware `build_design_docs.py` (reportlab): render
      `.mmd → .png`, then `.txt → PDF` with images embedded. Generic md→pdf
      converters can't do mermaid/images/tables — don't rely on them for visuals.

## 5. Wireframes (proper, not ASCII)

- [ ] Author screens in **wiremd** under `diagrams/wireframes/*.wmd.md`.
      Syntax: input `[____]{type:search}`, primary button `[Label]*`, grid
      `## Title {.grid-N}` with `###` items, GFM tables, blockquote = AI summary.
- [ ] Render with `--style wireframe`, screenshot the HTML with headless Edge
      (`--headless=new --screenshot=out.png --window-size=W,H
      --force-device-scale-factor=2`), then **auto-crop** whitespace with Pillow.
      Wrap it in `build_wireframes.py`. Git-ignore the `.html` intermediates.

## 6. Rewrite the decision logs

- [ ] Keep the required structure/scaffold; rewrite only the **prose** — plain,
      direct, steady paragraphs. No witty fragments. Replace `✅ 🟡 ✦` with words.
- [ ] Justify with the pattern: *"[File] does X. According to [design doc] this
      is why. This led to [outcome / next gap]."*
- [ ] **Tie each log to the GAP** with one sentence (e.g. "this is the escalation
      gateway in the TO-BE process").
- [ ] **Give each log a diagram** — author one if it lacks one.
- [ ] **Reference conventions (so logs survive upload):**
  - Inline file refs = **bare name, no path, no extension**: `@state`, `@decide`.
    (Upload platforms linkify `@file.ext`; `@name` is safe.)
  - **No `.md` files in body text** — only in the footer `Source:` line.
  - Footer = plain lines: `Files:` · `Diagrams:` · `Source:` · `LO stages:`
    (these keep extensions — they're not `@`-mentions).
  - Images = bracket callouts `[IMAGE: path/name.png — caption]`; **point only at
    files that exist** (audit for dead screenshot refs).
  - Filename format: `[DL-0N] <research question>.txt` (rename with `git mv`).

## 7. Collection summary (`.txt`)

- [ ] Intro: **What is this? / Why / What was accomplished.**
- [ ] Then a **sprint story** from `git log`: each sprint = explanation first,
      then `Designs & reports:` (`@`-pointers to design docs / diagrams / reports
      by stripped name — **never code**), `Decision logs:` (`@[DL-0N]`), and
      **What it unlocked**.
- [ ] No embedded images, no commit hashes. Verify every `@`-pointer resolves.

## 8. Test reports

- [ ] Rewrite prose plain; **keep** the results table and any formula as evidence.
- [ ] Swap `✅ → pass`; trim raw JSON to a short plain note.

## 9. Other docs

- [ ] Only rewrite analysis/planning `.md` that are genuinely old-style. Leave
      already-plain docs (README, requirements) and intentionally-technical `.md`
      sources alone (their plain twin is the `.txt`).

## 10. Regenerate PDFs

- [ ] `python build_design_docs.py` (design `.txt` → PDF + diagrams)
- [ ] `python convert_md_to_pdf.py` (the `.md` set → PDF)
- [ ] If a PDF is locked (open in a viewer) on Windows: build to `*.new.pdf`,
      verify, swap when the viewer closes.

## 11. Package: `deletable/` + `upload/`

- [ ] `deletable/` — flat, **git-ignored**, local-only. *Move* unused/superseded
      files here (screenshots, scratch, build artifacts, duplicate evidence,
      orphaned PDFs). Add `deletable/` to `.gitignore`. Remove moved docs from the
      PDF builder's file list. **Nothing is deleted.**
- [ ] `upload/` — **committed** bundle. *Copy* deliverables into a clean tree:
      `decision-logs/`, `design-docs/` (`.txt` + PDFs), `diagrams/` (referenced
      `.png` + `00-INDEX.txt`), `reports/`, plus the GAP artifact and README/plan
      PDFs. Regenerate PDFs *before* copying.

## 12. Deliver with git

```
git checkout -b <branch-name>        # NO spaces in the name
git add -A                           # deletable/ ignored; upload/ included
git commit -m "docs: overhaul ..."
git push -u origin <branch-name>
# merge to main (fetch + merge if the remote diverged — never force-push)
git checkout main && git merge --no-ff <branch-name> && git push origin main
```

---

## Final checklist

- [ ] Every doc matches the current code.
- [ ] Every feature traces to the GAP via a referenced diagram.
- [ ] Diagrams render sharp (high-res) and have a `00-INDEX` entry.
- [ ] Wireframes are real wiremd renders, not ASCII.
- [ ] Decision logs: bare `@` refs, no `.md` in body, plain footer, real image
      refs, `[DL-0N]` filenames, one diagram each.
- [ ] Summary is a `.txt` of explanation → `@`-pointers → what it unlocked.
- [ ] Test reports plain, evidence kept.
- [ ] All PDFs current. `deletable/` (ignored) and `upload/` (committed) sorted.
- [ ] Branched, committed, pushed, merged.
