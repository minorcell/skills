---
name: web-performance
description: >
  Optimize web performance through code-level, locally actionable strategies.
  Focuses on asset loading, JavaScript execution, rendering stability, and framework-level optimizations
  that developers can implement in their local codebase without touching infrastructure or deployment.
  Triggered when the user asks to optimize website speed, fix Core Web Vitals, improve page load time / interactivity / visual stability,
  or audit a codebase for performance issues.
---

# Web Performance Optimization Skill (Local-First)

A code-level, locally actionable performance optimization framework. This skill focuses on what you can change in your source code, build configuration, and component structure — not on infrastructure, CDN, or server architecture.

## Core Principle

> The highest-impact performance wins are usually in your code, not your servers. Optimize locally first.

Every optimization decision must answer three questions before implementation:

1. **Which metric does this improve?** (LCP, INP, CLS, TTFB, FCP)
2. **Can I implement this by changing code or build config?** (If it requires DevOps/Infra, it belongs in the "Beyond Local" section)
3. **How will I verify the improvement?** (Lighthouse, DevTools, RUM, or build output analysis)

---

## Target Thresholds (2026)

| Metric                              | Good    | Needs Improvement | Poor    | Primary Dimension |
| ----------------------------------- | ------- | ----------------- | ------- | ----------------- |
| **LCP** (Largest Contentful Paint)  | ≤ 2.5s  | 2.5–4.0s          | > 4.0s  | Loading           |
| **INP** (Interaction to Next Paint) | ≤ 200ms | 200–500ms         | > 500ms | Interactivity     |
| **CLS** (Cumulative Layout Shift)   | < 0.1   | 0.1–0.25          | > 0.25  | Visual Stability  |
| **TTFB** (Time to First Byte)       | < 200ms | 200–600ms         | > 600ms | Network / Server  |
| **FCP** (First Contentful Paint)    | ≤ 1.8s  | 1.8–3.0s          | > 3.0s  | Loading           |

> **Rule of Thumb:** Every 0.1s load improvement lifts conversions by ~8% (retail) to ~10% (travel).

---

## Dimension 1: JavaScript Loading & Execution Strategy

_Highest impact, fully local. Most performance issues start here._

### 1.1 Code Splitting & Lazy Loading

- [ ] **Check:** Is the JavaScript bundle split so that each route or page only loads the code it actually executes?
  - **Why:** Loading the entire application upfront blocks the main thread, delays interactivity, and wastes bandwidth on unused code. This is the single biggest cause of poor INP and inflated LCP on SPAs.
  - **Strategy:** Split by route (each page loads independently) and by component (below-fold, modal, tab content loads on demand). Use dynamic imports for heavy components (charts, editors, maps, video players). Ensure the initial bundle contains only the framework runtime, router, and above-fold components.
  - **Verify:** Analyze the bundle for a single route. If it contains code for unrelated routes or components that are not rendered initially, splitting is insufficient.

- [ ] **Check:** Are heavy third-party libraries loaded only when needed?
  - **Why:** Analytics, charting libraries, rich text editors, and mapping SDKs can add 100KB–500KB to the initial bundle. If they are not needed for the first paint, they should not be in the initial chunk.
  - **Strategy:** Move heavy library imports behind user interactions or viewport entry. Load a chart library only when the user scrolls to the chart section. Load a chat widget only when the user clicks the chat button. Use dynamic imports with loading states (skeletons or spinners) to mask the delay.
  - **Verify:** Check the initial bundle composition. If heavy third-party libraries appear in the first chunk despite not being needed immediately, defer them.

### 1.2 Script Loading Attributes

- [ ] **Check:** Are non-critical scripts loaded with `defer` or `async` rather than blocking the parser?
  - **Why:** Synchronous scripts in the `<head>` halt HTML parsing and delay the first paint. Every blocking script directly inflates FCP and LCP.
  - **Strategy:** Use `defer` for scripts that need the DOM but are not critical for the initial render (e.g., analytics initialization, non-essential UI enhancements). Use `async` for independent scripts that can run anytime (e.g., third-party widgets that don't depend on DOM). Only synchronous scripts in the head should be those absolutely required for the first paint (ideally, none).
  - **Verify:** Check the loading attribute of each script. If non-critical scripts lack `defer` or `async`, they are blocking the parser.

- [ ] **Check:** Are critical above-the-fold resources prioritized over non-critical ones?
  - **Why:** The browser has limited concurrent connections. Without prioritization, a large non-critical script may consume bandwidth that should go to the LCP image or critical CSS.
  - **Strategy:** Use resource hints (`preload`, `prefetch`) for critical assets. Preload the LCP image, the critical font, and the critical CSS. Ensure these hints are in the initial HTML, not injected by JavaScript. Use `fetchpriority="high"` on the LCP image element.
  - **Verify:** Check the network waterfall. The LCP image and critical font should begin downloading before non-critical scripts of similar size.

### 1.3 Tree-Shaking & Dead Code Elimination

- [ ] **Check:** Is the production bundle free of unused code?
  - **Why:** Dead code increases download time, parse time, and compile time. A single unused import of a large library (e.g., importing all of lodash instead of specific functions) can bloat the bundle by tens of kilobytes.
  - **Strategy:** Audit imports. Use named imports instead of default imports for tree-shakeable libraries. Remove unused components, utilities, and styles. Ensure the build tool is configured for tree-shaking (ES modules, sideEffects flag). Regularly run bundle analysis to identify large or unused modules.
  - **Verify:** Use bundle analysis to visualize the dependency graph. If large modules are included but only a fraction is used, tree-shaking is broken or the import pattern is wrong.

- [ ] **Check:** Are polyfills and legacy bundles served only to browsers that need them?
  - **Why:** Transpiling modern syntax (ES2020+) to ES5 for all users bloats the bundle for the majority who run modern browsers.
  - **Strategy:** Serve modern, slimmer bundles to browsers that support modern syntax. Serve legacy polyfilled bundles only to older browsers. This is typically done via module/nomodule pattern or user-agent-based serving. Modernize the browser support matrix to reduce unnecessary polyfills.
  - **Verify:** Compare the modern vs. legacy bundle sizes. If all users receive the legacy bundle, modern users are paying a penalty.

### 1.4 Main Thread & Interactivity

- [ ] **Check:** Are long-running JavaScript tasks broken into smaller chunks?
  - **Why:** Tasks that occupy the main thread for more than 50ms block user input. The browser cannot respond to clicks, taps, or keystrokes until the task yields. This is the primary cause of poor INP.
  - **Strategy:** Break large computations (data sorting, image processing, complex algorithm runs) into smaller units that yield control back to the browser. Use cooperative scheduling patterns. Move heavy computation off the main thread where possible.
  - **Verify:** Profile the main thread. Look for tasks exceeding 50ms. If they exist, they need to be chunked or moved off-thread.

- [ ] **Check:** Are high-frequency events (resize, scroll, input) debounced or throttled?
  - **Why:** Unthrottled resize or scroll handlers can fire hundreds of times per second, overwhelming the main thread and causing jank.
  - **Strategy:** Limit execution frequency. Debounce for actions that should only fire after the event stops (e.g., search input). Throttle for actions that need periodic updates during the event (e.g., scroll position tracking). Consider using passive listeners for scroll/touch events where `preventDefault` is not needed.
  - **Verify:** Profile during scroll or resize. If handlers consume significant main-thread time, they are unthrottled.

- [ ] **Check:** Is layout thrashing avoided?
  - **Why:** Reading layout properties (offset, dimensions, position) immediately after writing to the DOM forces the browser to recalculate layout synchronously — an expensive operation that kills interactivity.
  - **Strategy:** Batch all DOM reads together, then batch all DOM writes together. Never interleave reads and writes in the same frame. Use `requestAnimationFrame` for visual updates.
  - **Verify:** Profile layout costs. If layout recalculation spikes after DOM mutations, check for interleaved read/write patterns.

---

## Dimension 2: Resource Loading Strategy

_What you load, when you load it, and how you tell the browser to prioritize._

### 2.1 Image Strategy

- [ ] **Check:** Are images served in the most efficient format for their visual characteristics?
  - **Why:** Modern formats (AVIF, WebP, JPEG XL) offer 30–50% better compression than legacy formats (JPEG, PNG) at equivalent quality. This is one of the fastest LCP wins.
  - **Strategy:** Generate and serve modern formats with automatic fallback to legacy formats for older browsers. Use `<picture>` or build-pipeline transformations. For photographs, use lossy modern formats; for graphics with transparency, evaluate the best format for the specific use case.
  - **Verify:** Audit image formats across the site. If the majority of images are still in legacy formats, this is a high-impact optimization.

- [ ] **Check:** Is each image delivered at a resolution appropriate for its display size?
  - **Why:** Serving a 2000px-wide image to a 375px viewport wastes bandwidth, memory, and decoding time.
  - **Strategy:** Implement responsive image delivery. The browser should receive an image whose intrinsic size matches (or slightly exceeds) the rendered size. Use `srcset` + `sizes` or dynamic resizing at build time.
  - **Verify:** Compare intrinsic image dimensions against rendered dimensions across common viewports. Large discrepancies indicate waste.

- [ ] **Check:** Do all images have explicit sizing information?
  - **Why:** Without explicit dimensions, the browser cannot reserve space during layout. When the image loads, it pushes surrounding content, causing layout shifts (CLS).
  - **Strategy:** Ensure every image has width/height attributes or CSS-based aspect-ratio constraints. This allows the browser to allocate the correct space before the asset loads.
  - **Verify:** Run layout shift diagnostics. If images are a top contributor to CLS, explicit sizing is missing.

- [ ] **Check:** Is lazy loading applied correctly — only to below-the-fold images?
  - **Why:** Lazy-loading an above-the-fold image delays its discovery and download, directly inflating LCP.
  - **Strategy:** Apply lazy loading only to images that appear outside the initial viewport. For the largest above-the-fold image (the LCP candidate), ensure it is eagerly loaded and potentially prioritized with `fetchpriority="high"`.
  - **Verify:** Identify the LCP element. If it is an image with lazy loading enabled, this is a critical bug.

- [ ] **Check:** Is the LCP image discoverable by the browser as early as possible?
  - **Why:** The browser's preload scanner may not discover an image if it is injected by JavaScript or referenced deep in external stylesheets.
  - **Strategy:** Ensure the LCP image is referenced in the initial HTML document (not injected by JS) and is preloaded so the browser begins downloading it before non-critical resources.
  - **Verify:** Check the network waterfall. The LCP image request should start early in the sequence, ideally before non-critical CSS and JS.

### 2.2 Font Loading Strategy

- [ ] **Check:** Does the font loading strategy prevent invisible text during the initial render?
  - **Why:** If fonts block rendering, users see blank or invisible text until the font downloads. This inflates both LCP and FCP.
  - **Strategy:** Use a font-display strategy that renders fallback text immediately and swaps to the custom font when ready. Ensure the fallback font metrics are adjusted to minimize layout shift during the swap.
  - **Verify:** Use visual testing. If text appears invisible and then "pops in" with the custom font, the loading strategy is blocking.

- [ ] **Check:** Are only the font files needed for above-the-fold content loaded early?
  - **Why:** Loading entire font families (multiple weights, styles, character sets) synchronously blocks rendering and wastes bandwidth.
  - **Strategy:** Split font loading by priority. Only preload the specific font files required for the first visible text. Load additional weights and styles asynchronously or on demand. Subset fonts to only the characters used in your content.
  - **Verify:** Check which font files are loaded in the first request sequence. If non-essential weights are loaded before the first paint, loading is over-eager.

### 2.3 CSS Delivery

- [ ] **Check:** Is the CSS required for above-the-fold rendering delivered without blocking the parser?
  - **Why:** External CSS files in the head block rendering until they are downloaded and parsed. If the CSS file is large, the user stares at a blank screen.
  - **Strategy:** Separate critical CSS (needed for the first viewport) from non-critical CSS. Deliver critical CSS inline or in a way that doesn't require an external round-trip. Defer non-critical styles so they load after the initial render. Avoid `@import` in CSS which creates serial request chains.
  - **Verify:** Check the render-blocking resource audit. If CSS files are flagged as blocking and are not needed for the first paint, they should be deferred.

- [ ] **Check:** Is CSS minified and free of unused rules?
  - **Why:** Dead CSS increases download and parse time. Every unused selector adds to the stylesheet size.
  - **Strategy:** Audit stylesheets for rules that match no elements in the rendered page. Remove unused CSS from the production build. Ensure minification removes whitespace and comments without altering semantics.
  - **Verify:** Use coverage analysis to identify the percentage of CSS that is never applied.

- [ ] **Check:** Is CSS containment used to limit layout and paint scope for isolated components?
  - **Why:** Without containment, a style change in one component can trigger layout recalculation across the entire document.
  - **Strategy:** Apply containment boundaries to isolated, self-contained components (ads, embeds, widgets, third-party content) so their internal changes do not propagate to the rest of the page.
  - **Verify:** Profile layout recalculation costs. If small component updates trigger full-document layout, containment is missing.

### 2.4 Video & Media

- [ ] **Check:** Are below-the-fold videos prevented from downloading until they enter the viewport?
  - **Why:** Video files are large. Autoloading videos the user may never see wastes bandwidth and blocks the network for critical resources.
  - **Strategy:** Use lazy loading or preload-none strategies for non-hero videos. Only load the video metadata or poster image initially; fetch the full video on intersection or user intent.
  - **Verify:** Check network requests on initial load. If video files are downloaded before the user scrolls to them, lazy loading is missing.

- [ ] **Check:** Do video elements have poster images with explicit dimensions?
  - **Why:** A video without a poster or dimensions causes layout shift when the video frame loads.
  - **Strategy:** Provide a lightweight poster image and explicit sizing for every video element, just as with images.
  - **Verify:** Check CLS contributions from video elements.

---

## Dimension 3: Rendering & Layout Stability (CLS)

_Visual stability is entirely within your control. Zero infrastructure required._

### 3.1 Media & Embed Dimensions

- [ ] **Check:** Do all images, videos, and embeds have reserved space before they load?
  - **Why:** Without reserved space, the element expands after loading and pushes surrounding content downward, causing layout shifts.
  - **Strategy:** Every media element and embed must have explicit dimensions or aspect-ratio constraints in the HTML or CSS before the resource loads. This includes iframes, maps, and social widgets. Use CSS `aspect-ratio` or intrinsic ratio padding techniques.
  - **Verify:** Check CLS attribution reports. If media or embeds are top contributors, explicit sizing is missing.

### 3.2 Dynamic Content

- [ ] **Check:** Is space reserved for content that loads asynchronously (ads, recommendations, notifications, comments)?
  - **Why:** Ads and dynamic content are classic CLS culprits. If the container has no minimum size, the ad expands and shifts everything below it.
  - **Strategy:** Define minimum dimensions or aspect ratios for ad containers and dynamic content slots before the content arrives. If the content is smaller than the reserved space, center it; do not collapse the container. Use skeleton screens that match the expected content dimensions.
  - **Verify:** Check CLS during ad loading or dynamic content injection. If shifts occur, reserved space is insufficient.

- [ ] **Check:** Does new content append below existing content rather than above?
  - **Why:** Inserting content above the current viewport (e.g., banners, cookie notices, "new message" alerts) pushes the user's reading position down, creating a severe layout shift.
  - **Strategy:** Append new content below the fold or in dedicated non-intrusive areas. If a top banner is necessary, reserve its space in the initial layout rather than injecting it dynamically.
  - **Verify:** Check CLS timing. If shifts occur after initial load and the user's viewport content moves, insertion position is wrong.

### 3.3 Font & Animation

- [ ] **Check:** Does font loading cause minimal layout shift when swapping from fallback to custom font?
  - **Why:** If the fallback font and custom font have different metrics, text reflows when the swap happens, causing CLS.
  - **Strategy:** Adjust fallback font metrics so that the fallback occupies approximately the same space as the custom font. This minimizes the visual difference during the swap. Use `size-adjust` or `font-size-adjust` where supported.
  - **Verify:** Check CLS during font loading. If text blocks shift when the custom font appears, metric matching is needed.

- [ ] **Check:** Do animations use properties that do not trigger layout recalculation?
  - **Why:** Animating width, height, top, left, or margin forces the browser to recalculate layout on every frame — expensive and janky.
  - **Strategy:** Animate only `transform` and `opacity`. These properties can be handled by the compositor thread without touching layout or paint. Never animate layout properties for performance-critical transitions.
  - **Verify:** Profile animation frames. If layout or paint costs appear during animation, the wrong properties are being animated.

---

## Dimension 4: Framework & Rendering Mode

_The architectural decisions in your framework configuration have massive performance implications._

### 4.1 Server-Side vs. Client-Side Rendering

- [ ] **Check:** Is the initial HTML generated server-side or at build time rather than purely client-side rendered?
  - **Why:** Client-side rendering requires downloading, parsing, and executing JavaScript before any content appears. This inflates LCP and FCP significantly and hurts SEO.
  - **Strategy:** For content-heavy pages, generate HTML on the server (SSR) or at build time (SSG/Prerender). The browser should receive meaningful HTML in the first response, not an empty shell that JavaScript fills later. Use client-side rendering only for highly interactive, non-content-critical applications.
  - **Verify:** Disable JavaScript and load the page. If no content appears, the page relies entirely on client-side rendering.

- [ ] **Check:** Is non-interactive content rendered on the server to reduce client-side JavaScript?
  - **Why:** Much of a page's content (text, images, static sections) does not need client-side interactivity. Rendering it on the server eliminates corresponding JS bundle size.
  - **Strategy:** Separate interactive components from static content. Render static content server-side; hydrate only the components that need client-side behavior. Use React Server Components, Astro Islands, or Qwik resumability to minimize hydration cost.
  - **Verify:** Compare the JS bundle size against the amount of interactivity on the page. If the bundle is large but interactivity is limited, too much is being client-rendered.

### 4.2 Streaming & Progressive Rendering

- [ ] **Check:** Is HTML streamed to the browser rather than buffered until fully generated?
  - **Why:** Buffering the entire page server-side delays the first byte. Streaming sends the head and critical content immediately while the rest generates.
  - **Strategy:** Use streaming response patterns so the browser can begin parsing and requesting sub-resources before the server finishes generating the full page. This improves perceived performance and allows progressive rendering.
  - **Verify:** Check TTFB vs. the time when the first HTML bytes arrive. If they are identical, the response is likely buffered.

- [ ] **Check:** Are Suspense boundaries used to stream non-critical components progressively?
  - **Why:** Without streaming boundaries, the entire page waits for the slowest data source before rendering anything.
  - **Strategy:** Wrap slow or non-critical components (comments, recommendations, related content) in Suspense boundaries. Let the shell render immediately while slow components stream in when ready. Show fallback UI (skeletons) during the wait.
  - **Verify:** Check if the initial HTML contains the page shell and critical content before slow data resolves. If the page is blank until all data loads, streaming is not utilized.

---

## Dimension 5: Code Quality & Bundle Health

_Clean code is fast code. These are low-effort, high-confidence wins._

### 5.1 Dependency Hygiene

- [ ] **Check:** Are dependencies audited for size and necessity?
  - **Why:** A single unused or bloated dependency can add hundreds of kilobytes to your bundle. Many projects accumulate dependencies that are no longer used.
  - **Strategy:** Regularly audit `package.json`. Remove unused dependencies. Replace large libraries with lighter alternatives (e.g., date-fns instead of moment, native fetch instead of axios where appropriate). Evaluate whether a dependency's full feature set is needed or if a subset suffices.
  - **Verify:** Run bundle analysis. Identify the largest dependencies and assess whether they are all necessary and used.

- [ ] **Check:** Are duplicate dependencies or multiple versions of the same library present?
  - **Why:** Different packages depending on different versions of the same library (e.g., lodash 3.x and 4.x) can result in multiple copies in the bundle.
  - **Strategy:** Use dependency resolution tools to identify duplicates. Align versions where possible. Use webpack/vite resolution aliases to force a single version if compatible.
  - **Verify:** Check the bundle for multiple copies of the same library. If found, deduplicate them.

### 5.2 Asset Compression & Minification

- [ ] **Check:** Are production assets (JS, CSS, HTML) minified?
  - **Why:** Unminified code includes whitespace, comments, and long variable names that inflate transfer size.
  - **Strategy:** Ensure the build pipeline minifies all production assets. Verify that source maps are generated for debugging but not served to end users by default.
  - **Verify:** Inspect production assets. If they contain readable whitespace and comments, minification is not enabled.

- [ ] **Check:** Are images compressed without visible quality loss?
  - **Why:** Even in modern formats, excessive quality settings waste bytes. Images often comprise 60–80% of page weight.
  - **Strategy:** Establish quality thresholds per image category (hero, thumbnail, icon, background). Automate compression in the build or deployment pipeline rather than relying on manual optimization. Use responsive images to serve appropriate resolutions.
  - **Verify:** Compare file sizes against visual quality. If an image is significantly larger than similar images on comparable sites, compression is likely insufficient.

---

## Beyond Local: Infrastructure & Deployment

_The following items significantly impact performance but typically require DevOps, backend, or platform-level changes. They are listed here for awareness, not as local code tasks._

- **CDN & Geographic Distribution** — Serve static assets from edge locations close to users. Reduces TTFB and LCP globally.
- **HTTP/2 or HTTP/3** — Modern protocols reduce connection overhead and head-of-line blocking.
- **Brotli or Gzip Compression** — Compress text-based assets at the server or edge level.
- **Connection Pre-warming** — Use `preconnect` and `dns-prefetch` for critical third-party origins.
- **Server Response Time** — Optimize database queries, add caching layers, and use connection pooling to keep TTFB under 200ms.
- **Edge Computing** — Run dynamic logic close to the user for personalized or geolocated content.
- **Caching Strategy** — Use long-term cache headers with hashed filenames for static assets. Implement runtime caching (Service Worker) for repeat visits.
- **Real User Monitoring (RUM)** — Collect Core Web Vitals from real users to identify issues lab data misses.

> **Note:** If the user has control over these areas, refer to the `web-performance` infrastructure skill or consult with the DevOps/backend team. Do not let infrastructure block local optimizations — the code-level wins above usually provide 70–80% of the performance improvement.

---

## Quick Reference: Local Optimization by Impact

| Strategy                          | LCP | INP | CLS | Effort | Confidence |
| --------------------------------- | --- | --- | --- | ------ | ---------- |
| Route-based code splitting        | ★   | ★★★ | —   | Medium | High       |
| Defer non-critical scripts        | ★★  | ★★  | —   | Low    | High       |
| Tree-shake unused code            | ★   | ★★  | —   | Low    | High       |
| Preload LCP image                 | ★★★ | —   | —   | Low    | High       |
| Set explicit image dimensions     | —   | —   | ★★★ | Low    | High       |
| Adopt modern image formats        | ★★★ | —   | —   | Low    | Medium     |
| Use `font-display: swap`          | ★   | —   | ★   | Low    | High       |
| Inline critical CSS               | ★★  | —   | —   | Medium | High       |
| Reserve space for dynamic content | —   | —   | ★★★ | Low    | High       |
| Break up long tasks (>50ms)       | —   | ★★★ | —   | Medium | High       |
| Use `transform` for animations    | —   | ★   | ★★★ | Low    | High       |
| SSR / SSG for content pages       | ★★★ | ★★  | —   | High   | High       |
| Use Suspense for streaming        | ★★  | —   | —   | Medium | High       |
| Remove unused dependencies        | ★   | ★★  | —   | Low    | High       |

---

## Diagnostic Toolkit (Local-First)

| Tool                         | Type        | Best For                                                                          |
| ---------------------------- | ----------- | --------------------------------------------------------------------------------- |
| **Chrome DevTools**          | Lab         | Network waterfall, Performance profiling, Coverage analysis, Layout shift regions |
| **Lighthouse**               | Lab         | Automated audits, Core Web Vitals, actionable suggestions                         |
| **Bundle Analyzers**         | Build       | JS dependency graph, size visualization, duplicate detection                      |
| **Coverage Tool (DevTools)** | Lab         | Unused CSS/JS identification                                                      |
| **PageSpeed Insights**       | Lab + Field | Quick diagnosis with CrUX field data                                              |
| **WebPageTest**              | Lab         | Filmstrip, waterfall, device emulation, geographic testing                        |
| **web-vitals library**       | Field       | Custom RUM instrumentation (if user deploys)                                      |

---

## Output Format

When asked to audit or optimize performance, determine data availability and proceed along the appropriate path:

### Path A: User provides runtime data (Lighthouse report, PSI link, DevTools profile, or RUM data)

1. **Baseline Report** — Parse the provided data. Extract LCP, INP, CLS, TTFB, FCP. Note device segments and worst-performing pages.
2. **Priority Matrix** — Cross-reference findings against the checklist above. Focus exclusively on Dimensions 1–5 (local code changes). Sort by:
   - **Impact:** Which metric is most degraded?
   - **Effort:** Low-effort fixes first.
   - **Confidence:** Can the fix be verified statically, or does it require runtime validation?
3. **Action Plan** — Group recommendations by dimension. For each:
   - State the specific check that failed.
   - Explain the optimization strategy (code-level change, not infrastructure).
   - Define the expected metric improvement.
   - Specify how to verify (DevTools panel, Lighthouse audit, bundle analysis).
4. **Quick Wins** — List the top 3–5 changes that can be implemented in under 30 minutes with high confidence.
5. **Infrastructure Flag** — If the data reveals infrastructure issues (TTFB > 600ms, no CDN, poor caching), flag them in the "Beyond Local" section with a brief note. Do not dive into implementation details.

### Path B: User provides code only (no runtime data)

1. **Static Audit** — Scan the provided code for checklist items that do not require runtime measurement:
   - Script loading attributes (defer, async, module/nomodule).
   - Dynamic imports and code splitting patterns.
   - Image dimensions, lazy loading, format hints.
   - CSS delivery method (inline vs. external, import chains, containment).
   - Font loading strategy and font-display settings.
   - Animation properties (transform vs. layout).
   - Framework rendering mode (SSR vs. CSR, Suspense usage).
   - Dependency tree and bundle composition.
2. **Quick Wins** — List optimizations that can be implemented with high confidence based on static analysis alone.
3. **Runtime Verification List** — Clearly mark items that require actual measurement to confirm (e.g., real LCP element, actual CLS from dynamic content, true INP from user interactions).
4. **Diagnostic Recommendation** — Provide a general approach for obtaining runtime data (e.g., run a Lighthouse audit in Chrome DevTools, deploy to staging with RUM). Do not assume specific tool availability.

### Path C: No data and no code provided

1. **Information Request** — Ask the user for:
   - The codebase or specific files to audit, or
   - Existing performance reports or Lighthouse scores, or
   - The framework / tech stack in use.
2. **Universal Top 10 (Local-First)** — If the user cannot provide data immediately, output the 10 highest-impact, lowest-effort code-level optimizations:
   - Split code by route and lazy-load below-fold components.
   - Defer all non-critical scripts.
   - Preload the LCP image and critical font.
   - Set explicit width/height on all images and embeds.
   - Use modern image formats (WebP/AVIF) with fallbacks.
   - Use `font-display: swap` with metric-adjusted fallbacks.
   - Inline critical CSS; defer non-critical styles.
   - Reserve space for ads and dynamic content.
   - Break up long main-thread tasks (>50ms).
   - Animate only `transform` and `opacity`.
3. **Next Steps** — Explain how the user can gather baseline data to move from Path C to Path A or B.
