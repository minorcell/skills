---
name: writing-proposals
description: >
  Draft, rewrite, continue, or review technical proposals, RFCs, design issues,
  product-change proposals, API or language proposals, tooling proposals, and
  implementation plans intended to support a decision. Use when Codex needs to
  turn a change idea into a reviewable argument, improve an existing proposal
  without imposing a generic template, or diagnose why a proposal is hard to
  evaluate. Adapt structure, depth, language, and evidence to the proposal's
  audience and context. Do not use for ordinary coding tasks or brief execution
  plans unless the user asks for a proposal, RFC, or design document.
---

# Writing Proposals

## Objective

Help a specific audience make a well-informed decision. Treat a proposal as an
argument for a decision, not as a document schema.

Preserve the author's intent while making the need, proposed change, reasoning,
and material consequences clear enough to evaluate. Do not force proposals into
a fixed structure. Let the decision, audience, risk, subject, and repository
conventions determine the form and depth.

## Choose the Working Mode

Identify the task before acting:

| Mode | Default behavior |
| --- | --- |
| Draft | Develop the decision, reasoning, and document from the supplied idea or evidence. |
| Research and draft | Establish the important facts and constraints before making the case. |
| Revise | Diagnose the existing proposal, then make the smallest changes that solve the stated problems. |
| Continue | Match the existing argument, terminology, language, and structure before adding material. |
| Review | Lead with the most consequential problems. Do not rewrite unless asked. |

Proceed directly when the requested outcome is clear. Ask a question only when
ambiguity about the decision, audience, evidence, or destination format would
materially change the result.

## Establish the Decision Contract

Before drafting, determine:

1. **Decision**: What should the reader approve, reject, choose, or align on?
2. **Audience**: Who makes or influences that decision, and what do they need to understand?
3. **Need**: What problem, opportunity, constraint, or prior decision makes this proposal necessary?
4. **Change**: What would become different if the proposal were accepted?
5. **Consequences**: Which effects, risks, tradeoffs, or unknowns could change the decision?
6. **Constraints**: What length, language, format, evidence standard, or repository convention applies?

Keep these answers internal unless the user asks for a plan or the proposal needs
to state them. When working on an existing artifact, inspect its surrounding
documents and conventions before changing its structure or voice.

## Find the Real Decision

Separate the motivating facts from the interpretation and the proposed response.
A reported problem does not automatically justify a particular solution.

Prefer the smallest decision that can be evaluated independently, but do not
split a system-wide decision merely to make the document appear incremental.
Some proposals are inherently cross-cutting or require a complete migration,
policy, or semantic model to be coherent.

Ground the case in the evidence actually available: user experience, incidents,
code, operational cost, constraints, prior decisions, research, or examples. One
real case can justify a narrow proposal. Look for a broader pattern only when the
evidence supports one; do not invent user stories or generality.

## Build a Reviewable Case

Make the reasoning inspectable. A useful chain is:

```text
evidence -> interpretation -> proposed change -> expected consequence -> boundary
```

Treat this as a reasoning aid, not a required section order. Distinguish facts,
assumptions, judgments, and open questions when confusing them would weaken the
decision.

Use only the support the proposal needs:

- Explain the current behavior or workaround when it demonstrates the problem.
- Use examples when they clarify behavior, semantics, or user impact.
- Describe alternatives when they are real options or likely reviewer questions.
- Include implementation details when they establish feasibility or define a contract.
- Cover compatibility, migration, failure behavior, rollout, and testing when they materially affect acceptance or execution.

Do not manufacture examples, metrics, rejected alternatives, risks, or consensus
to make the proposal look complete.

## Let the Decision Shape the Document

Choose the most direct order for the target audience. A proposal may begin with a
problem, a concrete change, an example, a constraint, or a prior decision. Use
headings only when they help the reader navigate the argument.

A small proposal may be a few paragraphs. A consequential proposal may need a
long specification. Length should follow the number of decisions, the amount of
uncertainty, and the cost of being wrong, not the proposal category.

Consider scope, boundaries, alternatives, errors, compatibility, migration, and
tests internally. Put them in the document only when they help readers decide,
define the accepted contract, or reduce a material implementation or rollout
risk. Do not emit empty sections, placeholder tables, or `none` entries.

Use tables, diagrams, code, and examples only when they make a relationship or
behavior easier to evaluate than prose. Do not expose the internal checklist as
the document's structure.

## Apply Design Pressure Without Dictating the Design

Challenge unnecessary scope, mechanisms, special cases, and user burden. Prefer
existing concepts and simpler rules when they satisfy the same need.

Treat incremental and subtractive design as useful pressures, not universal
requirements. A sound proposal may add necessary complexity, replace a complete
system boundary, explore uncertainty, or coordinate a broad change. In those
cases, make the cost and reason visible instead of forcing the design into a
smaller shape.

State boundaries when ambiguity would change the decision. Separate future ideas
from the current decision when they distract from it, but do not add an
`Out of Scope` section merely to satisfy convention.

## Write for the Target Reader and Language

- Follow an explicitly requested artifact language.
- Otherwise follow existing repository documents, then the user's language.
- Write directly in the target language; do not translate English syntax or a generic template sentence by sentence.
- Match the target community's terminology, heading style, and level of formality.
- Preserve code identifiers and official technical terms while explaining them naturally.
- Prefer concrete subjects and verbs over abstract noun chains, filler, and ceremonial transitions.
- For Chinese, avoid mirroring English noun chains, passive constructions, and template headings; use compact, idiomatic technical prose.
- Rewrite anything that sounds translated, inflated, generic, or unlike the surrounding document.

Clarity does not require erasing the author's voice. Preserve deliberate brevity,
directness, informality, or first-person experience when it fits the audience.

## Review and Revise

Review the proposal in separate passes:

1. **Decision**: Is the requested decision clear and appropriately scoped?
2. **Reasoning**: Do the conclusions follow from the evidence and assumptions?
3. **Consequences**: Are decision-changing effects, risks, and unknowns visible?
4. **Reader**: Can the intended audience understand and evaluate the change?
5. **Structure**: Does each part advance the case without repetition or ceremony?
6. **Language**: Does the document sound natural, precise, and consistent with its context?

When revising, fix the reusable cause of a problem and preserve unaffected prose,
facts, citations, examples, terminology, and formatting. When reviewing, report
findings in order of consequence and distinguish blocking issues from optional
improvements.

## Deliver Adaptively

- For a draft, deliver the proposal or update the requested artifact.
- For a revision, summarize the material changes without narrating every edit.
- For a review, present findings first and keep any summary secondary.
- Keep a simple proposal simple; do not add sections to signal rigor.
- Follow an existing template only when the destination actually requires it.
- Keep internal reasoning and self-review internal unless a remaining uncertainty helps the user decide.

## Final Quality Gate

Before delivering, verify:

- The reader can identify the decision and why it matters.
- The proposal distinguishes evidence, interpretation, and recommendation where needed.
- The proposed change is precise enough for the current decision.
- Detail is proportional to uncertainty, impact, and review risk.
- Material consequences and unresolved questions are not hidden.
- The structure fits this proposal rather than a generic template.
- The target language sounds natural and the author's voice remains recognizable.
- The document contains no invented support or sections that exist only for completeness.
