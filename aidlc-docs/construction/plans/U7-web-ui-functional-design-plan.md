# CLAIRO U7 Web UI - Functional Design Plan

**Unit**: U7 Web UI (TypeScript reviewer web application)
**Responsibility**: Reviewer-facing UI — Cognito login, review queue, review task detail (recommendation + confidence + highlighted evidence), decide/override; claim status views.
**Stories**: US-06 (UI), US-07 (UI), US-09 (UI), US-12 (login).
**Depends on**: U5 Claim API (contract), U0 (Cognito, Amplify hosting).

---

## Part A: Functional Design Questions

Answer each with the letter after `[Answer]:`. Choose **X) Other** if none fit. Let me know when done.

### Question 1: Frontend Framework
Which TypeScript framework for the reviewer UI?

A) React (with Vite)

B) Next.js

C) Angular

X) Other (please describe after [Answer]: tag below)

[Answer]: B) Next.js

### Question 2: Auth Integration
How should the UI integrate Cognito login?

A) AWS Amplify Auth library (hosted UI or built-in components)

B) amazon-cognito-identity-js directly with a custom login form

X) Other (please describe after [Answer]: tag below)

[Answer]: A) AWS Amplify Auth library (hosted UI or built-in components)

### Question 3: Screens / Scope for MVP
Which screens should the MVP UI include?

A) Login, Review Queue (list), Review Detail (recommendation + confidence + highlighted evidence + approve/deny/override), Claim Status lookup

B) The above plus a Supervisor admin screen (threshold config + audit trail viewer)

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Login, Review Queue (list), Review Detail (recommendation + confidence + highlighted evidence + approve/deny/override), Claim Status lookup

### Question 4: Evidence Highlighting Display
How should highlighted evidence be shown in the Review Detail screen?

A) List the highlighted text snippets with page/bbox metadata (no document render) — simplest for MVP

B) Render the document image/PDF with bbox overlays

X) Other (please describe after [Answer]: tag below)

[Answer]: A) List the highlighted text snippets with page/bbox metadata (no document render) — simplest for MVP

### Question 5: API Client
How should the UI call the U5 Claim API?

A) A typed API client module (fetch-based) with the Cognito JWT attached to requests

B) A generated client from an OpenAPI spec

X) Other (please describe after [Answer]: tag below)

[Answer]: A) A typed API client module (fetch-based) with the Cognito JWT attached to requests

---

## Part B: Execution Checklist (executed after plan approval)

- [x] Generate `aidlc-docs/construction/U7-web-ui/functional-design/frontend-components.md`
- [x] Generate `aidlc-docs/construction/U7-web-ui/functional-design/business-logic-model.md`
- [x] Generate `aidlc-docs/construction/U7-web-ui/functional-design/business-rules.md`
- [x] Update aidlc-state.md and audit.md
