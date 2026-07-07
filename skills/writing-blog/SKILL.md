---
name: writing-blog
description: >
  Write high-quality technical or general blog posts by synthesizing proven writing philosophies
  from top practitioners (Paul Graham, Joel Spolsky, Phodal, etc.).
  Triggered when the user asks to write a blog post, article, essay, or technical content,
  or when asked to improve/draft/review blog content.
---

# Blog Writing Skill

A distilled, actionable writing framework synthesized from the practices of Paul Graham, Joel Spolsky/Sashko Stubailo, Phodal, and the broader technical writing community.

## Core Philosophy

> "Good writing should be convincing because you got the right answers, not because you did a good job of arguing."
> — Paul Graham

### The Four Pillars of Useful Writing (Graham)

Every post must score high on at least two of these:

| Pillar          | Meaning                                                    | Check                                                         |
| --------------- | ---------------------------------------------------------- | ------------------------------------------------------------- |
| **Importance**  | The topic matters to the reader.                           | Does this solve a real problem or answer a real question?     |
| **Novelty**     | The reader learns something they didn't know.              | Is there a surprise, anomaly, or non-obvious insight?         |
| **Correctness** | What you say is true and defensible.                       | Can you cite sources, show code, or provide evidence?         |
| **Strength**    | You state your position clearly without excessive hedging. | Are you saying something concrete, or just vaguely gesturing? |

### Write Simply, Write Like You Talk

- Use ordinary words. Complex sentences and fancy words give the writer the false impression they're saying more than they actually are.
- Read your draft out loud. Fix everything that doesn't sound like conversation. Fix phonetically awkward bits.
- Short sentences win. A five-sentence good argument beats a hundred-sentence ramble.
- Cut everything unnecessary. If a sentence, paragraph, or section doesn't directly serve the reader's goal, delete it.

### The Reader-First Mindset

- Define the audience before the first sentence. Beginner? Senior engineer? Non-technical stakeholder? The audience determines depth, jargon level, and assumed context.
- Write for a reader who won't read carefully. Structure must be scannable: headings, lists, code blocks, and bold key points.
- Start with the promise. The first paragraph must tell the reader exactly what they will get and why it's worth their time.

## Workflow: The 5-Step Method

### Step 1 — Find the Topic & Commit

- Write what you know. If you spent hours learning something and can explain it in minutes, you provide value.
- Fill a gap. Look for topics that are under-explained or where existing content is outdated/wrong.
- Start small. Installation guides, bug fixes, "how X works under the hood" — daily work is valid material.
- Don't wait for brilliance. Execution matters more than the idea. A mediocre idea with great execution beats a great idea with poor execution.

### Step 2 — Define Audience & Goal

Answer these two questions in one sentence each before writing:

1. Who is reading this? (e.g., "Junior frontend devs who have never touched Webpack")
2. What will they be able to do after reading? (e.g., "Configure a basic splitChunks strategy without copy-pasting")

Constraint: If a section doesn't serve this specific goal for this specific audience, remove it.

### Step 3 — Structure: Beginning, Middle, End

#### Introduction (The Hook)

- 1-2 paragraphs max.
- Context + Promise: what problem this solves and what the reader will learn.
- Never bury the lede. State the most important sentence first.

#### Middle (The Meat)

- Use hierarchical headings (##, ###) as a map. Readers should be able to navigate by headings alone.
- Alternate between storytelling (relatable scenario, pain point) and demonstration (code, data, steps).
- One idea per paragraph. One concept per code block.
- Use lists for sequential steps, tables for comparisons, diagrams for architecture.

#### Conclusion (The Payoff)

- Summarize what was learned in 2-3 sentences.
- Provide a call to action: try the code, read the source, leave a comment, check the repo.
- End decisively. Don't taper off.

### Step 4 — Get Feedback & Iterate

- Share the draft cold. Don't explain what you meant. Hand it over and ask: "What did you get out of this?"
- Validate the goal. Did the reader achieve the intended outcome, or did they get lost?
- Revise ruthlessly. 80% of the ideas in an essay happen after you start writing; 50% of what you started with will be wrong. Be confident enough to cut.

### Step 5 — Polish: Packaging, Publication, Promotion

- Title is a promise, not a trick. Good titles are specific and contain keywords the reader would search for. Bad titles are vague or pure clickbait.
- One strong image or diagram beats a thousand words of explanation. Ensure diagrams are high-contrast and color-coded.
- Code blocks must be copy-paste ready. Include file names, language tags, and brief comments.
- Link generously. Cite sources, link to docs, reference related posts. It builds trust and SEO.
- Proofread twice. Once for logic/flow, once for typos and formatting.

## Article Type Strategies

| Type             | Strategy                                                     | Example Title Pattern                               |
| ---------------- | ------------------------------------------------------------ | --------------------------------------------------- |
| Tutorial/Guide   | Step-by-step, goal-oriented, code-first.                     | "How to set up X with Y in 10 minutes"              |
| Deep Dive/Survey | Anatomy of a system, trade-off analysis, historical context. | "How X works under the hood" / "A deep dive into Y" |
| Problem/Solution | Start with the error, show debugging, end with fix.          | "Fixing the dreaded X error: a complete guide"      |
| List/Comparison  | Bite-sized, scannable, opinionated ranking.                  | "5 ways to do X (and which to choose)"              |
| Opinion/Essay    | One strong thesis, evidence, clear stance.                   | "Why X is not the answer" / "The case for Y"        |
| News/Release     | What changed, why it matters, migration path.                | "X 2.0: what you need to know"                      |

## Hard Rules (Never Break)

1. One job per post. A tutorial should not also be a manifesto. If you have two ideas, write two posts.
2. No jargon without definition. Every acronym must be expanded on first use. Every technical term must be explained or linked.
3. Show your work. If you claim a fact, provide a source, a code snippet, or a benchmark. "Show, don't tell."
4. No walls of text. Break paragraphs before they exceed 5 lines. Use visual anchors (headings, lists, code) every 2-3 paragraphs.
5. Code must run. Every code example must be syntactically valid and ideally tested. Include setup steps if needed.
6. Respect the reader's time. If the reader can get the answer in 3 minutes, don't stretch it to 15.

## Quality Checklist (Before Publishing)

- [ ] Title contains a keyword or clearly states the topic
- [ ] First paragraph states the promise (what the reader gets)
- [ ] Headings form a readable outline on their own
- [ ] Every code block has a language tag and a file path/context
- [ ] All acronyms defined on first use
- [ ] At least one visual element (diagram, table, or screenshot)
- [ ] Conclusion summarizes the key takeaway and has a CTA
- [ ] Read out loud once; no awkward or overly complex sentences
- [ ] Spell-checked and grammar-checked
- [ ] All links verified (not 404)

## Reference: The Masters' Heuristics

- Paul Graham: Write simply. Cut mercilessly. Novelty comes from anomalies. Good essays have importance + novelty + correctness + strength. Write like you talk.
- Sashko Stubailo (Apollo/Meteor): Commit to a topic. Make the audience and goal specific. Have a beginning, middle, and end. Get feedback cold. Polish packaging.
- Phodal: Titles are class names (must be clear). Headings are method names (must describe action). Content is the function body (keep it focused). Images are UI (make them high-contrast).
- Simple Talk Anonymous: Tell stories to draw readers in. Demonstrate concepts with authentic examples. Moderate jargon. Show sources. Be clear, never dull.
- JavaGuide/Chinese Community: Short sentences. Determine the reader first. Good articles are revised, not written once. Visuals matter. Output倒逼输入 (output drives input).

## Output Format

When asked to write or draft a blog post, produce:

1. A proposed title and audience/goal statement for confirmation.
2. Upon approval, a full draft in Markdown with:
   - YAML frontmatter (title, date, tags, description)
   - Structured body following the 5-step workflow above
   - All code blocks syntax-highlighted and runnable
   - At least one visual suggestion (diagram description or ASCII art)
3. A self-review covering the four pillars (importance, novelty, correctness, strength) and the quality checklist.
