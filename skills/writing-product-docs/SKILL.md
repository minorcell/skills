---
name: writing-product-docs
description: >
  Use when drafting, rewriting, or reviewing a product definition or product
  design document — the artifact that states what a product is, what problem it
  solves, who it is for, and its core concepts and information structure. Applies
  when the user asks for a product definition, product design doc, or "PRD-lite",
  or pushes back that a draft reads like a technical proposal, RFC, or data-model
  spec. Enforces user-perspective wording, information-structure over schemas,
  problem-before-solution ordering, and mental-model-first concept writing.
---

# Writing Product Docs

## What a product doc is (and is not)

A product doc answers four questions and nothing more:

1. **What is it** — one paragraph a reader can repeat to someone else.
2. **What problem does it solve** — the pain, and today's inadequate workaround.
3. **Who is it for** — user profiles concrete enough to test membership.
4. **Core concepts & information structure** — the concepts, and what the user *sees*.

It is NOT a technical proposal, RFC, or design spec. When a draft starts carrying
the things below, it has drifted out of "product" and into "engineering" — cut them:

| Belongs in a design doc / RFC, NOT a product doc |
|---|
| Data models / schemas (`id`, `createdAt`, foreign keys, field types) |
| Technical constraints (storage layout, model selection, library/engine choice) |
| Phase plans / milestones / testing strategy |
| "Alternatives considered" trade-off analysis |
| Error-handling matrices, boundary-case tables framed for implementers |

If the user says "this reads like a technical/proposal doc," the fix is almost
always deleting one of these sections — not rewording it.

## The five sections

Order matters. Lead with the problem so the reader feels the need before the
solution is named. Keep the tail light.

```
1. Problem       — the pain + today's workaround, ideally a table
2. User profiles — primary profile + "to-be-validated" secondaries
3. User stories  — concrete narratives; end with the shared pattern they reveal
4. Core concepts — each concept: definition + mental model + behavior
5. Information structure — what the user SEES per view + concept relationships
```

A one-paragraph product definition sits above section 1 (unnumbered intro).
Optional closing sections (non-goals, interface compatibility, future directions)
stay short — one bullet each, no elaboration.

**Anti-pattern:** opening with "What it is" fully explained, *then* justifying why
it's needed. Readers can't judge a solution to a need they don't yet feel. Problem first.

## User perspective over developer perspective

The single most common defect. The doc describes what the user experiences, in the
user's words — never the system's internals or the developer's vocabulary.

### Wording: use what the user would say, not what the code calls it

Engineering names leak into product docs because the writer is close to the
implementation. Translate them back to the concept the user actually perceives.
Common categories of leak:

| Leak category | Typical engineering terms | Fix |
|---|---|---|
| Data-layer nouns | source, record, entity, artifact, blob, node | Name the thing as the user thinks of it (the file they added, the content they got) |
| Pipeline verbs | ingest, index, parse, embed, sync, hydrate | Describe the visible process/state, not the mechanism ("processing…" → "ready") |
| Invisible internals | vector, chunk, token, cache, hash | Omit entirely — if the user never sees it, it isn't product |
| Infra choices | local vs cloud, service X vs Y, endpoint | Mention only the choice the user actually makes, in their terms |
| Generic tech placeholders | object, item, resource, handler, config | Replace with the concrete domain concept |

The specific mapping is domain-specific; the *rule* is universal: **if the user
never sees or says the word, it does not belong in a product doc.** Test each noun
and verb with "would a non-technical user of this product use this word?" If no,
translate it.

### Tone: considered, not casual

Product docs read as deliberate, not chatty. Casual or vague phrasing signals the
idea isn't fully formed. Categories to watch, with the direction of the fix:

| Undignified pattern | Direction of fix |
|---|---|
| Colloquial place/action names ("the spot where you do stuff", "the doing area") | Name it by its function or role ("the workspace", "the authoring surface") |
| Hand-wavy ease claims ("just click and you're done", "super easy") | State the concrete action ("complete in one step") |
| Filler and hedging ("basically", "kind of", "for the most part") | Delete; make the claim or drop it |
| Jokes / winks / emoji as substance | Remove; keep voice neutral and precise |
| Vague intensifiers ("powerful", "seamless", "magical") | Replace with the specific capability |

The underlying rule: **every phrase should be one a serious spec would carry.**

### Information structure = what the user sees, not data fields

The information-structure section describes each screen or view in terms of **what
appears to the user**: titles, icons, status labels, counts, lists, buttons, empty
states. It never lists database fields. Describe the row the user reads, not the
record the system stores. A visible list of attributes the user perceives is
product; a struct definition with types and keys is a schema — move it out.

## Concepts: mental model first

Each core concept gets, in this order:

1. **Definition** — one or two plain sentences.
2. **Mental model** — the analogy the user holds in their head. This is the most
   valuable and most-skipped line: a physical or familiar metaphor ("a desk",
   "a folder", "a timeline", "a shopping cart", "a knowledge pack").
3. **Behavior** — what the user can do with it, in user-visible steps.

A concept without a mental-model line is under-specified. If you can't name the
analogy, the concept probably isn't crisp yet — surface that to the user rather
than papering over it.

Optionally state a short list of **design invariants** — the rules that must hold
no matter how the product evolves. These are the durable core; distinguish them
from mutable UI decisions.

## Diagrams and notation

- Prefer **Mermaid** for concept relationships so it renders in common hosts
  (GitHub/GitLab) without external tooling.
- **Rendering gotcha:** `erDiagram` with non-Latin (e.g. CJK) entity names fails
  to parse on GitHub (`ONLY_ONE` / cardinality errors). For non-Latin labels use
  `graph TD` with plain nodes and labeled edges instead. Verify any diagram
  actually renders before shipping.
- ASCII box layouts are fine for screen mockups (sidebar / main-area sketches) —
  they convey user-facing structure, not implementation.

## Review checklist

Before delivering, verify:

- [ ] Opens with the problem, not the "what is it" explanation.
- [ ] Every term is one a real user would say (no data-layer nouns, pipeline verbs, or invisible internals).
- [ ] The information-structure section lists what the user *sees*, not data fields.
- [ ] Each concept has an explicit mental-model line.
- [ ] No schema, no phase plan, no test strategy, no tech-constraint section.
- [ ] Tone is considered, not casual — no filler, hype, or hand-wavy claims.
- [ ] Mermaid diagrams actually render (non-Latin labels → `graph TD`, not `erDiagram`).
- [ ] Closing sections (non-goals, future work) are one bullet each, unexpanded.

## Common corrections (symptom → fix)

| Symptom | Fix |
|---|---|
| Draft has a data-model / schema section | Delete it; rewrite as "what the user sees" |
| Draft has tech constraints / phase plan / alternatives analysis | Move to a separate design doc; product doc drops them |
| Uses data-layer nouns or pipeline verbs | Translate to the user's word for the same thing |
| "What it is" appears before "why it's needed" | Reorder: problem → solution |
| Concept explained but no analogy given | Add a mental-model sentence |
| Casual, vague, or hyped phrasing | Elevate to considered, specific wording |
| `erDiagram` with non-Latin names won't render | Switch to `graph TD` |
| Closing sections over-explained | Compress each to a single bullet |
