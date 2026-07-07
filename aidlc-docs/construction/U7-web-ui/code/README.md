# CLAIRO U7 Web UI - Code Summary

## Generated Files (workspace root)
```
web/
├── package.json            # Next.js + React + MUI + aws-amplify
├── next.config.js          # output: 'export' (static SPA)
├── tsconfig.json
├── .env.example
└── src/
    ├── types.ts            # Claim/decision TS types
    ├── lib/
    │   ├── amplify.ts      # Amplify Auth config + getIdToken
    │   └── apiClient.ts    # typed fetch client w/ Cognito JWT
    ├── components/
    │   ├── AppLayout.tsx        # shell + auth guard + nav
    │   ├── RecommendationCard.tsx
    │   ├── ReasoningList.tsx
    │   ├── EvidenceList.tsx     # highlighted evidence snippets (page/bbox)
    │   ├── DecisionForm.tsx     # approve/deny/override + rationale
    │   └── ClaimStatusCard.tsx
    └── pages/
        ├── _app.tsx
        ├── index.tsx       # Review Queue (US-06)
        ├── review.tsx      # Review Detail + decide/override (US-06/07), ?id= query
        └── status.tsx      # Claim Status lookup (US-09)
```

## Decisions Applied
- Next.js static export (SPA); MUI components; Amplify Auth (Cognito); typed fetch client with JWT.
- 4 screens: Login (via AppLayout guard), Review Queue, Review Detail, Claim Status.
- Evidence shown as snippets with page/bbox (no document render).
- Rationale required on override; `data-testid` on interactive elements.
- Dynamic review route uses `?id=` query (static-export friendly) rather than `[id]`.

## Verification Performed
- `npm install` succeeded (note: Next.js 14.2.5 flagged a security advisory — see below).
- `npm run build` succeeded: typecheck passed; all routes (`/`, `/review`, `/status`, `/404`) prerendered as static content.
- Build artifacts (`.next`, `out`, `node_modules`) cleaned and gitignored.

## Follow-ups / Notes
- **Security advisory**: `next@14.2.5` reported a vulnerability during install. Recommend bumping to a patched Next.js version before any real deployment. (Security extension was OFF for this MVP; flagged for awareness.)
- No automated frontend tests (NFR Q4:A); manual + integration in Build & Test.
- Config (API URL, Cognito ids, region) injected via env vars from U0 Amplify web stack.
- Amplify hosted-UI sign-in requires the Cognito app client to have a hosted UI domain + callback URLs configured (operational step).
