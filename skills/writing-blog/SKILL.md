---
name: writing-blog
description: >
  Draft, research, rewrite, and review technical or general blog posts, articles,
  and essays. Use when Codex needs to create new content, improve an existing
  draft, adapt writing for a specific audience, strengthen evidence and reasoning,
  preserve an author's voice, or prepare a post for publication.
---

# Writing Blog Posts

## Objective

Turn a useful idea into an article that a defined reader can understand, trust,
and remember. Preserve the author's actual intent and voice instead of replacing
them with a generic polished style.

Do not force every article into the same structure. Let the subject, reader, and
requested outcome determine the form.

## Choose the Working Mode

Identify the task before acting:

| Mode | Default behavior |
| --- | --- |
| Draft | Develop the thesis, structure, and article from the supplied idea or material. |
| Research and draft | Establish the claims and evidence before writing the narrative. |
| Revise | Diagnose the existing draft, then make the smallest changes that solve the stated problems. |
| Continue | Match the existing argument, terminology, voice, and formatting before adding material. |
| Review | Lead with concrete problems and explain why they weaken the article. Do not rewrite unless asked. |

Proceed directly when the user has clearly requested writing or editing. Ask a
question only when ambiguity about the thesis, audience, evidence standard, or
delivery format would materially change the result.

## Establish the Writing Contract

Before drafting, determine:

1. **Job**: What single job should this article do?
2. **Reader**: Who is reading, and what can they already be expected to know?
3. **Outcome**: What should the reader understand, believe, decide, or be able to do afterward?
4. **Thesis**: What is the central claim or organizing idea?
5. **Constraints**: What length, tone, format, sources, repository conventions, or publication requirements apply?

Keep these answers internal unless the user asks for a plan. Do not replace the
user's thesis with a more fashionable or more convenient one. Surface a conflict
when the requested evidence cannot support the requested claim.

When editing an existing artifact, inspect its surrounding structure first.
Preserve correct facts, citations, metadata, links, terminology, and unaffected
prose unless the user asks for a broader rewrite.

## Bridge the Reader's Knowledge Gap

Defining an audience is not enough. Identify what the reader must understand
before the main argument works.

For each prerequisite concept, decide whether to:

- assume it because it is appropriate for the stated reader;
- explain it briefly at first use;
- anchor it in a familiar example before introducing the abstraction;
- explain the relationship between it and nearby concepts; or
- link to background material when a full explanation would derail the article.

Prefer one concrete scene, object, action, or example before a dense abstract
explanation. Layer detail: give the reader a usable mental model first, then add
precision where the argument requires it.

Do not turn every article into a beginner tutorial. Add only the bridge needed for
the intended reader to follow the next step.

## Build Claims from Evidence and Reasoning

For claims that carry the article, use this chain:

```text
claim -> evidence -> reasoning -> conclusion -> boundary
```

Distinguish among:

- **Sourced fact**: directly supported by a reliable source.
- **Observation**: visible in data, behavior, code, an artifact, or an example.
- **Inference**: a conclusion drawn from facts or observations.
- **Opinion**: the author's judgment, preference, or interpretation.

Do not present an inference as a sourced fact. Do not use a later outcome as proof
that someone originally intended that outcome. State uncertainty and competing
explanations when they materially affect the conclusion.

Prefer primary sources for important factual claims. Place citations close to the
claims they support. Use examples, code, data, or counterexamples when they make
the reasoning inspectable rather than merely persuasive.

Research only to the depth the article needs. A practical note may need one
verified reference; a consequential comparison or historical argument may need
multiple independent sources.

## Choose a Structure That Fits the Job

Use the article's purpose to choose its shape:

| Article job | Useful default structure |
| --- | --- |
| Teach a task | Result -> prerequisites -> steps -> verification -> common failures |
| Solve a problem | Symptom -> diagnosis -> cause -> fix -> prevention |
| Explain a subject | Guiding question -> mental model -> mechanism -> implications -> limits |
| Make an argument | Thesis -> reasons -> evidence -> counterargument -> boundary -> conclusion |
| Compare options | Decision context -> criteria -> tradeoffs -> recommendation -> exceptions |
| Reflect on experience | Concrete situation -> tension -> change in understanding -> transferable lesson |

Treat these as starting points, not mandatory templates.

Open with the most useful entry point: a problem, claim, result, scene, question, or
surprising observation. Do not impose a fixed paragraph count. Make the direction
of the article clear before asking the reader to absorb extensive background.

Use headings as a map for long articles. Keep one main idea per section and make
transitions explain why the next section follows. Alternate abstraction with
concrete evidence or examples when the material becomes dense.

End when the thesis has been resolved. Add a call to action only when the reader
has a natural next action. Add diagrams, tables, screenshots, or code only when
they explain a relationship more clearly than prose.

## Write in the Author's Language and Voice

- Write natively in the target language; do not mirror the syntax of source material.
- Prefer concrete subjects and verbs over chains of abstract nouns.
- Use ordinary words unless a precise technical term is necessary.
- Define unfamiliar jargon according to the reader, not by expanding every acronym mechanically.
- Keep terminology stable after introducing it.
- Break sentences when clauses compete for attention, but vary sentence length enough to avoid a mechanical rhythm.
- Remove filler, generic transitions, inflated claims, and narration about what the article is about to do.
- Preserve deliberate informality, restraint, humor, or first-person perspective when it belongs to the author.
- Read difficult passages aloud and rewrite anything that sounds translated, ceremonial, or unnatural.

Clarity does not require flattening the author's personality. Polish the expression
without erasing the point of view.

## Revise in Separate Passes

Do not try to fix everything sentence by sentence in one pass.

### Pass 1: Intent and Logic

- Confirm that the thesis matches the author's intended point.
- Check that each section advances the article's single job.
- Remove repeated arguments, contradictions, detours, and conclusions that do not follow.

### Pass 2: Evidence and Precision

- Verify consequential facts, links, quotations, examples, and code.
- Separate evidence from inference and opinion.
- Add qualifications where the claim is narrower than the prose suggests.

### Pass 3: Reader Understanding

- Find concepts introduced before the reader has a mental model for them.
- Add only the definitions, examples, and transitions needed to cross those gaps.
- Check that headings, lists, tables, and diagrams reduce effort rather than decorate the page.

### Pass 4: Language and Voice

- Replace translated or overly abstract phrasing with natural expression.
- Shorten overloaded sentences and remove empty connective phrases.
- Check rhythm, terminology, tone, and consistency with the author's existing voice.

After local edits, reread the surrounding paragraphs. A sentence can improve in
isolation while making the section less coherent.

## Use Feedback as Diagnosis

Classify feedback before revising:

- **Intent**: the draft says something different from what the author meant.
- **Logic**: the reasoning skips a step or reaches too far.
- **Evidence**: a claim is unsupported, outdated, or overstated.
- **Reader**: required knowledge or context is missing.
- **Structure**: information appears in the wrong order or repeats.
- **Language**: wording is unnatural, vague, dense, or inconsistent.
- **Voice**: the article no longer sounds like its author.
- **Artifact**: formatting, links, code, diagrams, or rendering are broken.

Fix the reusable cause of the problem, then reread the whole affected section.
Do not rewrite unrelated material merely because a nearby paragraph could also be
improved.

## Verify the Deliverable

Scale verification to what the article contains:

- Run code examples when the article depends on them.
- Verify links and source attribution for claims that rely on them.
- Check calculations, commands, versions, names, and dates.
- Validate Markdown, frontmatter, formatting, and repository conventions.
- Render the page when layout, tables, diagrams, images, themes, or responsive behavior matter.
- Report any verification that could not be performed.

When working inside a repository, modify the artifact directly if authorized and
keep the diff scoped to the request. Report adjacent publishing defects instead
of silently expanding into unrelated implementation work.

## Deliver Adaptively

- Do not require title confirmation when the user has already approved the direction.
- Do not add YAML frontmatter unless the destination format or repository expects it.
- Do not force a visual, code block, call to action, or fixed section template into every post.
- For a draft, deliver the draft or update the requested file.
- For a revision, summarize the material changes and preserve untouched content.
- For a review, present the most consequential findings first.
- Keep self-review internal unless a remaining risk or tradeoff helps the user decide.

## Final Quality Gate

Before delivering, verify:

- The article has one clear job, reader, and central idea.
- The structure fits the article instead of a generic template.
- Important claims are supported, and inference is distinguishable from fact.
- The intended reader can cross every necessary knowledge gap.
- Examples and visuals perform explanatory work.
- The target language sounds natural and the author's voice remains recognizable.
- The conclusion resolves the article without unnecessary repetition.
- Included code, links, metadata, and rendered elements were checked as appropriate.
