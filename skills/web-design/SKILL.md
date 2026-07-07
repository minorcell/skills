---
name: web-design
description: >
  Design and implement high-quality web interfaces by synthesizing proven design philosophies
  from Dieter Rams, Brad Frost (Atomic Design), Google Material Design, and modern web best practices.
  Triggered when the user asks to design a web page, UI component, design system, layout,
  or when asked to review/improve existing web design.
---

# Web Design Skill

A comprehensive web design framework synthesizing Dieter Rams' timeless principles, Brad Frost's Atomic Design methodology, Google Material Design patterns, and modern web best practices (2026).

## Core Philosophy

> "Less, but better."
> — Dieter Rams

### The Ten Principles of Good Design (Rams, adapted for Web)

| Principle          | Meaning                                                      | Web Application                                                                                  |
| ------------------ | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------ |
| **Innovative**     | Design must evolve with technology, never arbitrary novelty. | Leverage new CSS features (container queries, `clamp()`, subgrid) to solve real layout problems. |
| **Useful**         | The product serves its purpose; design enhances utility.     | Every element must serve a user goal. Decoration that hinders functionality is bad design.       |
| **Aesthetic**      | Beauty emerges from clarity and purpose, not ornament.       | Clean typography, purposeful whitespace, and consistent spacing create visual harmony.           |
| **Understandable** | The design explains itself without instruction.              | Intuitive navigation, clear affordances, self-describing labels. No manual needed.               |
| **Unobtrusive**    | Design is a tool, not art; it serves the user quietly.       | Neutral, restrained UI that lets content shine. No ego-driven flourishes.                        |
| **Honest**         | Don't manipulate or over-promise.                            | No dark patterns. Accurate labels. Performance claims match reality.                             |
| **Long-lasting**   | Avoid trends; aim for timelessness.                          | Use semantic HTML, standard patterns, and stable design tokens rather than fad aesthetics.       |
| **Thorough**       | Precision in every detail shows respect for the user.        | Consistent 8dp spacing, aligned baselines, accessible contrast, valid markup.                    |
| **Eco-friendly**   | Minimize resource waste and visual pollution.                | Optimize images, lazy-load, reduce JS, prefer system fonts, minimize carbon footprint.           |
| **Minimal**        | As little design as possible.                                | Strip away the unnecessary. One primary action per view. No decorative noise.                    |

### The Web Design Trinity

Every design decision must balance three forces:

1. **User Needs** — Can the user complete their task without confusion?
2. **Business Goals** — Does the design drive the intended conversion or action?
3. **Technical Reality** — Is it implementable, performant, and maintainable?

If a decision fails any one of these, it is a bad decision.

## Design System Architecture: Atomic Design (Brad Frost)

Build interfaces from the bottom up. Each layer composes the layer below it.

```
Pages      ← Real content in templates
Templates  ← Layout structures (wireframes)
Organisms  ← Complex sections (header, product card, hero)
Molecules  ← Functional units (search bar, form field, nav item)
Atoms      ← Primitives (color, type, spacing, border, shadow)
```

### Design Tokens (The Single Source of Truth)

Tokens are the bridge between design and code. Define them once, use everywhere.

| Token Category | Examples                                                  | Naming Convention                                                            |
| -------------- | --------------------------------------------------------- | ---------------------------------------------------------------------------- |
| **Color**      | `--color-primary-500`, `--color-surface-default`          | `{property}-{role}-{scale}` or semantic `{property}-{context}`               |
| **Typography** | `--font-body`, `--text-heading-1`, `--line-height-normal` | `{property}-{role}` or `{property}-{element}-{level}`                        |
| **Spacing**    | `--space-4`, `--space-lg`, `--gap-component`              | T-shirt scale (xs, sm, md, lg, xl) or numeric (4, 8, 12, 16, 24, 32, 48, 64) |
| **Border**     | `--radius-sm`, `--radius-pill`, `--border-default`        | `{property}-{role}`                                                          |
| **Shadow**     | `--shadow-sm`, `--shadow-elevation-2`                     | `{property}-{level}`                                                         |
| **Motion**     | `--duration-fast`, `--ease-out`                           | `{property}-{quality}`                                                       |

**Token Hierarchy:**

- **Core/Primitive:** Raw values (hex codes, base spacing units)
- **Semantic:** Purpose-driven (primary color, error color, surface color)
- **Component:** Applied to specific components (button-primary-bg, input-border)

## Workflow: The 6-Step Design Method

### Step 1 — Define the Problem & Audience

Before touching color or layout, answer:

1. **What is the primary user goal?** (e.g., "Complete a purchase in under 3 clicks")
2. **Who is the user?** (device, skill level, accessibility needs)
3. **What is the one action this page must drive?** (One primary CTA per page)

**Constraint:** If a design element doesn't serve the primary goal, remove it.

### Step 2 — Establish the Design System (Atoms & Tokens)

- Define **color palette**: primary, secondary, neutral (grays), semantic (success, warning, error), surface (background, card, overlay).
- Define **typography scale**: use modular scale (1.25x or 1.5x ratio). Minimum 16px body on mobile. Line-height 1.5–1.7 for body, 1.2–1.3 for headings.
- Define **spacing scale**: base 4px or 8px grid. All spacing values must be multiples of the base unit.
- Define **border & shadow**: consistent radius values, elevation system (0–5 levels).
- Define **breakpoints**: content-first, not device-first. Use `min-width` with logical names (`sm`, `md`, `lg`, `xl`) tied to content reflow points.

### Step 3 — Build Components (Molecules & Organisms)

- **Mobile-first:** Design the smallest screen first, then scale up. Forces prioritization.
- **Component, not page:** Build reusable molecules (button, input, card) and organisms (header, footer, hero) before assembling pages.
- **Touch targets:** Minimum 44×44px (48dp on Android). Never go below.
- **States:** Every interactive element needs default, hover, focus, active, disabled, and loading states.
- **Dark mode:** Design for `prefers-color-scheme` from day one using semantic tokens.

### Step 4 — Compose Layouts (Templates & Pages)

- **Visual hierarchy:** Guide the eye with size, color, contrast, and position. The most important element must be the most visually dominant.
- **Whitespace is not empty space:** It's strategic negative space that improves comprehension by up to 20%. Use generous padding between sections and line-height within text.
- **F-pattern & Z-pattern:** For content-heavy pages, users scan in an F. For landing pages, a Z guides attention to CTA.
- **Grid system:** Use CSS Grid for macro layouts, Flexbox for component-level alignment. Prefer container queries over media queries for component responsiveness.
- **Above the fold:** Identity, problem, and value must be unmistakable in the first viewport. If bounce rate > 60%, fix this first.

### Step 5 — Ensure Accessibility (WCAG 2.2+)

- **Contrast:** Minimum 4.5:1 for normal text, 3:1 for large text (18px+ or 14px+ bold). Use tools to verify.
- **Semantic HTML:** One H1 per page. Logical heading hierarchy (no skips). Use `<nav>`, `<main>`, `<section>`, `<article>` appropriately.
- **Alt text:** Every meaningful image gets descriptive alt text. Decorative images get empty alt (`alt=""`).
- **Keyboard navigation:** All interactive elements must be reachable and operable via Tab/Enter/Space.
- **ARIA:** Use ARIA labels only when HTML semantics are insufficient. Never overuse.
- **Focus indicators:** Visible, high-contrast focus rings on all interactive elements.
- **Motion:** Respect `prefers-reduced-motion`. No auto-playing content without pause controls.

### Step 6 — Optimize & Deliver

- **Performance is a design decision:**
  - Serve images in WebP/AVIF with `srcset` and sizes.
  - Lazy-load below-the-fold images and videos.
  - Keep critical CSS/JS minimal; defer the rest.
  - Target Core Web Vitals: LCP < 2.5s, INP < 200ms, CLS < 0.1.
- **SEO-friendly structure:**
  - Clean URL structure, descriptive `<title>` and `<meta name="description">`.
  - Structured data (JSON-LD) for articles, products, FAQs.
  - Semantic markup and internal linking.
- **Trust signals:** Client logos, testimonials, case studies, security badges, clear contact info.
- **Design-to-code handoff:**
  - Export design tokens as JSON/CSS variables.
  - Provide component specs with spacing, typography, and color annotations.
  - Use Figma Dev Mode or equivalent for developer inspection.

## Typography Rules

| Rule          | Good Practice                                              | Bad Practice                         |
| ------------- | ---------------------------------------------------------- | ------------------------------------ |
| Font families | 1–2 max (sans-serif for UI, serif for editorial if needed) | 3+ decorative fonts                  |
| Body size     | ≥ 16px on mobile, 18px on desktop                          | 12px body text                       |
| Line length   | 45–75 characters per line                                  | > 100 characters (hard to track)     |
| Line height   | 1.5–1.7 body, 1.2–1.3 headings                             | 1.0 (cramped) or 2.0 (too loose)     |
| Font weight   | 400–700 for UI; avoid 100/900                              | Extreme weights for body text        |
| Scale         | Modular scale (1.25x or 1.5x)                              | Arbitrary jumps (14px → 36px → 18px) |

## Color Rules

- **60-30-10 rule:** 60% dominant (neutral/background), 30% secondary, 10% accent (CTA).
- **Never rely on color alone** to convey meaning. Always pair with icon, text, or pattern.
- **Dark mode:** Don't just invert. Reduce saturation, elevate shadows, adjust contrast for OLED screens.
- **System preference:** Always support `prefers-color-scheme` and `prefers-contrast`.

## Spacing & Layout Rules

- **8px base grid:** All spacing values (padding, margin, gap) should be multiples of 8 (or 4 for fine-tuning).
- **Consistent rhythm:** Vertical rhythm between sections should follow the scale (e.g., 64px, 96px, 128px).
- **Container max-width:** Content containers should cap at 1200px–1400px with responsive padding (16px mobile, 24px tablet, 32px+ desktop).
- **Avoid horizontal scroll:** Content must reflow naturally; never force horizontal scrolling on mobile.

## Interaction & Motion Rules

- **Purpose-driven motion:** Every animation must serve clarity, feedback, or emphasis. No decorative motion.
- **Speed:** Micro-interactions 150–300ms. Page transitions 300–500ms. Use `ease-out` for enter, `ease-in-out` for exit.
- **Feedback:** Buttons press down. Forms validate inline. Loading states are explicit (skeleton > spinner > blank).
- **Hover is not a feature:** Never hide critical functionality behind hover. Mobile has no hover.

## Hard Rules (Never Break)

1. **One primary action per screen.** If there are two competing CTAs, the user won't know what to do.
2. **No walls of text.** Break content into scannable chunks: headings, lists, bullets, and code blocks.
3. **No jargon without definition.** Every acronym expanded on first use. Every technical term explained or linked.
4. **No placeholder as label.** Form fields must have persistent labels, not placeholder text that disappears.
5. **No broken accessibility.** Every interactive element must be keyboard-navigable and screen-reader-friendly.
6. **No unoptimized images.** Every image must have dimensions, alt text, and modern format (WebP/AVIF).
7. **No layout shift.** All images and embeds must reserve space to prevent CLS.
8. **No decorative motion without reduced-motion support.** Respect `prefers-reduced-motion`.

## Quality Checklist (Before Handoff / Publish)

- [ ] Mobile-first design verified on real devices (not just emulators)
- [ ] Visual hierarchy is clear: the most important element dominates
- [ ] One H1 per page; heading hierarchy is logical (no skipped levels)
- [ ] All text contrast ratios meet WCAG AA (4.5:1 normal, 3:1 large)
- [ ] All interactive elements have visible focus states
- [ ] All images have alt text; decorative images have empty alt
- [ ] All touch targets ≥ 44×44px (ideally 48×48px)
- [ ] Keyboard navigation works for entire page flow
- [ ] Dark mode tokens defined and tested
- [ ] `prefers-reduced-motion` respected for all animations
- [ ] Core Web Vitals targets met (LCP, INP, CLS)
- [ ] Design tokens exported and documented
- [ ] No horizontal scroll on any viewport
- [ ] Primary CTA is unmistakable and above the fold on mobile
- [ ] Forms have persistent labels, error states, and helper text
- [ ] No placeholder text used as the sole label
- [ ] Favicon, OG image, and meta tags configured
- [ ] All links and buttons have descriptive text (no "click here")

## Reference: The Masters' Heuristics

- **Dieter Rams:** Less but better. Design is a tool, not art. Honest, unobtrusive, thorough, minimal. Every detail matters.
- **Brad Frost (Atomic Design):** Build from atoms upward. Components compose. Design systems scale. Tokens bridge design and code.
- **Google Material Design:** 8dp spacing grid. Consistent type scale. Color contrast > 4.5:1. Motion provides meaning. Elevation communicates hierarchy.
- **Modern Web Best Practices (2026):** Mobile-first is default. Container queries > media queries. Fluid typography with `clamp()`. Core Web Vitals are ranking signals. Accessibility is not a feature—it's a foundation.
- **Figma-to-Code Workflow:** Design tokens are the single source of truth. Semantic naming enables theming. AI code generation needs token constraints to match design intent.

## Output Format

When asked to design a web page, UI, or component, produce:

1. **Design Brief** — Problem statement, audience definition, primary goal, and success metrics.
2. **Design System Spec** — Token definitions (color, typography, spacing, border, shadow) in a structured table or CSS variable block.
3. **Component Inventory** — List of atoms, molecules, and organisms needed, with state definitions.
4. **Layout Specification** — Wireframe-level structure with visual hierarchy notes, responsive breakpoints, and content placement.
5. **Accessibility Notes** — Contrast ratios, keyboard flow, ARIA usage, and reduced-motion plan.
6. **Implementation Notes** — Recommended tech stack (CSS framework, component library), token export format, and performance considerations.
7. **Self-Review** — Check against the Quality Checklist and the Ten Principles of Good Design.
