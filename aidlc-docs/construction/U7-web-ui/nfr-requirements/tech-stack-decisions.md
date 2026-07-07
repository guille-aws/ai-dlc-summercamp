# CLAIRO U7 Web UI - Tech Stack Decisions

| Concern | Decision | Rationale |
|---|---|---|
| Framework | Next.js (TypeScript) | From FD Q1 |
| Rendering | Static export / CSR (SPA) (Q1:A) | Simplest for Amplify Hosting |
| Auth | AWS Amplify Auth (Cognito) | From FD Q2 |
| Styling / components | MUI (Material UI) (Q2:A) | Accessible, mainstream, Next.js-friendly |
| API client | Typed fetch wrapper + Cognito JWT | From FD Q5 |
| Accessibility | Semantic HTML + labels + keyboard nav (Q3:A) | Sensible MVP defaults |
| Testing | None automated (Q4:A) | Manual + integration in Build & Test |
| Hosting | AWS Amplify Hosting | From U0 |

## Dependencies
- `next`, `react`, `react-dom`, `typescript`
- `@mui/material`, `@emotion/react`, `@emotion/styled`
- `aws-amplify` (Auth)

## Module Layout (Code Generation)
```
web/
├── package.json
├── next.config.js            # output: 'export' for static
├── tsconfig.json
├── src/
│   ├── lib/
│   │   ├── amplify.ts        # Amplify Auth config
│   │   └── apiClient.ts      # typed fetch client w/ JWT
│   ├── types.ts
│   ├── components/           # RecommendationCard, EvidenceList, DecisionForm, ...
│   └── pages/                # index (queue), review/[id], status, _app
└── .env.example
```

## Notes
- Config values (API URL, Cognito ids, region) come from Amplify env vars set by U0's web stack.
