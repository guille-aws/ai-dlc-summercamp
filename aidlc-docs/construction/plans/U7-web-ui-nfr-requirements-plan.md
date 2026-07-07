# CLAIRO U7 Web UI - NFR Requirements Plan

**Unit**: U7 Web UI (Next.js/TypeScript)

**Already established**: Next.js + TypeScript; AWS Amplify Auth (Cognito); typed fetch API client; hosted on AWS Amplify Hosting; extensions OFF; synthetic data.

Open UI-specific NFR questions below.

---

## Part A: NFR Questions

Answer each with the letter after `[Answer]:`. Choose **X) Other** if none fit. Let me know when done.

### Question 1: Rendering Mode
How should the Next.js app render for this MVP?

A) Static export / client-side rendering (SPA-style) — simplest for Amplify Hosting

B) Server-side rendering (SSR)

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Static export / client-side rendering (SPA-style) — simplest for Amplify Hosting

### Question 2: Styling Approach
What styling approach?

A) A component library (e.g., AWS Cloudscape or MUI) for fast, accessible components

B) Tailwind CSS

C) Plain CSS modules

X) Other (please describe after [Answer]: tag below)

[Answer]: A) A component library (e.g., AWS Cloudscape or MUI) for fast, accessible components


### Question 3: Accessibility Baseline
What accessibility baseline for the MVP?

A) Semantic HTML + labels + keyboard nav (sensible defaults; not formally WCAG-audited)

B) Formal WCAG 2.1 AA target

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Semantic HTML + labels + keyboard nav (sensible defaults; not formally WCAG-audited)

### Question 4: Frontend Testing
Testing approach for U7?

A) No automated tests (consistent with other units); manual + integration in Build & Test

B) Component tests (e.g., React Testing Library)

X) Other (please describe after [Answer]: tag below)

[Answer]: A) No automated tests (consistent with other units); manual + integration in Build & Test

---

## Part B: Execution Checklist (executed after plan approval)

- [x] Generate `aidlc-docs/construction/U7-web-ui/nfr-requirements/nfr-requirements.md`
- [x] Generate `aidlc-docs/construction/U7-web-ui/nfr-requirements/tech-stack-decisions.md`
- [x] Update aidlc-state.md and audit.md
