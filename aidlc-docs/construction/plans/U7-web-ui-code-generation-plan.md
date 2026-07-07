# CLAIRO U7 Web UI - Code Generation Plan

**Unit**: U7 Web UI (Next.js/TypeScript)
**Code location**: `web/`
**Depends on**: U5 Claim API, U0 (Cognito, Amplify hosting).
**Stories**: US-06, US-07, US-09, US-12 (UI aspects).

## Decisions Applied
- Next.js static export (SPA); Amplify Auth (Cognito); MUI; typed fetch client + JWT; core 4 screens; evidence snippet list; no automated tests.

## Generation Steps

- [x] **Step 1: Project scaffolding** — package.json, next.config.js (export), tsconfig.json, .env.example, .gitignore.
- [x] **Step 2: Types + API client** — types.ts, lib/apiClient.ts, lib/amplify.ts.
- [x] **Step 3: App shell + auth guard** — _app.tsx, AppLayout.tsx.
- [x] **Step 4: Components** — RecommendationCard, ReasoningList, EvidenceList, DecisionForm, ClaimStatusCard.
- [x] **Step 5: Pages** — index (queue), review (detail via ?id=), status.
- [x] **Step 6: Verify** — npm install + npm run build succeeded (typecheck + static export of all routes).
- [x] **Step 7: Documentation** — code/README.md (incl. Next.js security-advisory follow-up).

## Notes
- No automated tests (NFR Q4:A). Verification = build/typecheck passes.
- Config via env vars from U0 web stack.
