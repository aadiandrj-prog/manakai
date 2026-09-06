# Phase 3A UX audit

Audit date: 6 September 2026

This audit covers every public route in the ManakAI staging interface. It combines a manual browser walkthrough of the deployed Vercel application, a source review, and automated desktop/mobile interaction tests. Severity describes the effect on a first-time user: `CRITICAL` blocks a core task, `HIGH` causes likely failure or a materially misleading impression, `MEDIUM` adds friction, and `LOW` is polish.

## Findings and resolutions

| ID | Route | Severity | Type | Finding | Phase 3A resolution |
| --- | --- | --- | --- | --- | --- |
| UX-01 | Navigation, `/compliance` | CRITICAL | Broken interaction | “Compliance journey” always opened the seeded `demo-emergency-lamp` profile. It failed in authoritative staging because that profile does not exist there. | Added a real compliance landing page, removed the hard-coded demo ID, and offers the most recent browser-local result when one exists. |
| UX-02 | `/`, `/product` | HIGH | Flow | A dashboard product query appeared to carry forward but the product screen ignored it. | Product analysis now reads the `q` parameter, pre-fills the form, and keeps the original wording visible. |
| UX-03 | `/` | HIGH | Hierarchy | Six similar entry points and technical status panels competed for attention. | Established one primary “Check my product” action and three secondary intents: Ask a standard question, Find testing, and Consumer help. |
| UX-04 | `/product` | HIGH | Content | Results led with implementation detail instead of the decision a manufacturer needs. | Supported results now lead with Product identified, What applies, Status, When, and What to do next. |
| UX-05 | `/product` | HIGH | Trust | Partial and unsupported coverage could look like a failed analysis or a complete answer. | Partial results explicitly separate verified facts from facts still needing confirmation. Unsupported results decline to guess and give useful next routes. |
| UX-06 | `/product`, `/compliance/:id` | HIGH | Information architecture | Provenance, warnings, and the explanation chain were mixed into the first viewport. | Preserved decision-critical warnings, while moving deep regulatory basis, lab detail, and source evidence into labelled progressive disclosures. |
| UX-07 | `/compliance/:id` | HIGH | Incorrect state | Journey progress was presented as a fixed six-stage, 33% timeline even when the backend returned a different set of steps. | Progress and counts are calculated from returned steps. Each stage now shows its state, explanation, and next action. |
| UX-08 | `/ask` | HIGH | Trust | Every successful HTTP response looked like a successful Gemini answer, even when deterministic fallback text was used. | Added an explicit “AI explanation” or “Rules-based fallback” result label and explains that evidence validation is distinct from answer quality. |
| UX-09 | `/standards` | HIGH | Content | Authoritative staging displayed “0 demo records”, creating a false impression about mode and coverage. | Replaced mode-specific copy with accurate “available records” language and kept per-record source labels. |
| UX-10 | `/standards/:id` | HIGH | Broken interaction | A question field looked usable but its value was not carried to Ask ManakAI. Some copy also described current records as fixtures. | Replaced it with a proper pre-filled Ask link and source-aware record labels. |
| UX-11 | Global header | HIGH | Broken interaction | “EN / हिं” looked like a language switch but did not perform any action. | Replaced it with a non-interactive “EN · हिं · Hinglish” capability label. |
| UX-12 | Loading screens | HIGH | Performance perception | Render free-tier cold starts looked indistinguishable from a frozen application. | Loading states show a calm cold-start explanation after 3.5 seconds and remain non-blocking. |
| UX-13 | API-backed routes | HIGH | Recovery | Generic technical failures did not explain what a user could do next. | Common error messages now distinguish not-found, rate-limit, connection, and server problems. Core screens provide Retry and a safe next action. |
| UX-14 | `/compliance/:id` | HIGH | Mobile/accessibility | A wide evidence table was hard to read and navigate on a phone. | Replaced it with responsive evidence cards and accessible disclosure controls. |
| UX-15 | Cross-route actions | HIGH | Accessibility | A styled navigation action could be exposed to assistive technology as a button without a link destination. | Added a semantic link component and verified every tested primary action has a real destination. |
| UX-16 | `/consumer` | HIGH | Broken interaction | The three introductory help cards appeared actionable but did not lead anywhere. | Cards now link to the matching guidance section; HUID messaging clearly says ManakAI does not perform live verification. |
| UX-17 | `/about` | MEDIUM | Content | The headline could imply that AI performs regulatory reasoning, conflicting with the system’s deterministic decision boundary. | Reframed the page around rules and evidence as the regulatory core and AI as an optional explanation layer. |
| UX-18 | `/ask` | MEDIUM | Observability | The API reports whether final answer generation used fallback, but does not separately expose whether interpretation/classification fell back. | Deferred: extend the API telemetry contract without exposing provider secrets or changing regulatory authority. |
| UX-19 | `/product` | MEDIUM | Content | Missing backend attributes can still contain developer-style identifiers such as `rated_voltage_v`. | Deferred: add a shared, translated display-label map as coverage attributes expand. |
| UX-20 | Feedback | MEDIUM | Inclusion | Lightweight page feedback uses a pre-filled GitHub issue and therefore requires a GitHub account. | Accepted for this staging phase; evaluate an anonymous, privacy-reviewed channel before a public pilot. |
| UX-21 | Product-wide | MEDIUM | Measurement | No first-party behavioural analytics store or consent policy exists. | Intentionally deferred. Phase 3A adds no third-party tracker; use moderated testing and privacy-conscious deployment telemetry first. |
| UX-22 | Product-wide | MEDIUM | Continuity | The latest compliance result is remembered only in the current browser. | Accepted until identity/account work is authorised; the UI states this boundary. |
| UX-23 | External evidence | MEDIUM | Reliability | Live BIS links and Render may be slow or temporarily unavailable. | Added source/error warnings and retry paths. Canonical stored evidence remains independent of frontend scraping. |
| UX-24 | `/about` | LOW | Audience | This route remains more technical than task routes. | Retained intentionally as a team/judge architecture explainer; everyday workflows use plain language. |

## Route and interaction checklist

| Route | Primary task checked | Empty/loading/error checked | Mobile checked | Outcome |
| --- | --- | --- | --- | --- |
| `/` | Start product analysis; open the other three intents | N/A | Yes | Pass |
| `/product` | Supported, partial, ambiguous and unsupported analysis | Yes | Yes | Pass |
| `/compliance` | Explain prerequisite; resume recent result | Yes | Yes | Pass |
| `/compliance/:id` | Read decision, follow journey, expand why/evidence | Yes | Yes | Pass |
| `/standards` | Browse/search available standards | Yes | Yes | Pass |
| `/standards/:id` | Read metadata/relationships; ask a scoped question | Yes | Yes | Pass |
| `/labs` | Filter labs and inspect scope/validity | Yes | Yes | Pass |
| `/ask` | Ask, clarify, distinguish AI from fallback, inspect evidence | Yes | Yes | Pass |
| `/consumer` | Understand HUID boundary and open official guidance | Yes | Yes | Pass |
| `/about` | Understand system layers and decision boundary | N/A | Yes | Pass |

## Functional integrity checks

- No navigation item points to a synthetic profile identifier.
- The dashboard’s entered product wording reaches Product Analyser.
- Supported analysis can open the exact returned compliance profile.
- Partial and unsupported states never invent a standard.
- Ask results disclose whether the final explanation came from the configured AI provider or deterministic fallback.
- Standards-detail questions carry their context into Ask ManakAI.
- Consumer help never claims to verify an HUID.
- All primary actions tested on desktop and Pixel 7 viewports have real link or button semantics.
- Automated accessibility scans cover the dashboard, supported result and chat result with no serious/critical violations in the controlled test fixtures.

## Remaining validation boundary

This audit improves usability; it does not certify regulatory correctness. The authoritative corpus remains deliberately bounded, source changes require human review, laboratory scopes remain selective, and official linked services can change independently. The next usability milestone is moderated testing with people unfamiliar with the implementation, using `USER_TESTING.md`, followed by evidence-based changes rather than adding more dashboard features.
