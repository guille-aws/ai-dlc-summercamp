# CLAIRO U7 Web UI - Frontend Components

**Framework**: Next.js (TypeScript) · **Auth**: AWS Amplify Auth · **API**: typed fetch client with Cognito JWT.

## Screens (Q3:A)
1. **Login** — Amplify Auth (hosted UI / Authenticator). Redirects to Review Queue on success.
2. **Review Queue** — lists pending-review claims (GET /reviews). Reviewer/Supervisor only.
3. **Review Detail** — shows recommendation, confidence, reasoning, highlighted evidence (snippets + page/bbox); approve/deny/override actions (POST /reviews/{id}).
4. **Claim Status** — lookup a claim by id (GET /claims/{id}); shows status, decision, reasoning, explanation ref.

## Component Hierarchy
```
AppLayout (auth guard, nav)
├── LoginPage
├── ReviewQueuePage
│   └── ReviewTaskList
│       └── ReviewTaskRow (claim_id, status)  [data-testid="review-task-row"]
├── ReviewDetailPage
│   ├── RecommendationCard (outcome, confidence)  [data-testid="recommendation-card"]
│   ├── ReasoningList
│   ├── EvidenceList (snippet + page/bbox)  [data-testid="evidence-list"]
│   └── DecisionForm (approve/deny/override + rationale)  [data-testid="decision-form"]
└── ClaimStatusPage
    ├── ClaimSearchInput  [data-testid="claim-search-input"]
    └── ClaimStatusCard
```

## Props / State (summary)
- **ReviewQueuePage**: state `tasks: string[]` (claim ids); loads on mount.
- **ReviewDetailPage**: props `claimId`; state `claim`, `decisionResult`, `submitting`.
- **DecisionForm**: state `outcome`, `rationale`, `isOverride`; on submit → API.
- **ClaimStatusPage**: state `claimId`, `claim`, `error`.

## Automation-Friendly Attributes
- `data-testid` on interactive elements: `review-task-row`, `decision-form-submit`, `decision-outcome-select`, `rationale-input`, `claim-search-input`, `claim-search-submit`.

## API Integration Points
| Component | API |
|---|---|
| ReviewQueuePage | GET /reviews |
| ReviewDetailPage | GET /claims/{id}, POST /reviews/{id} |
| ClaimStatusPage | GET /claims/{id} |
| (all) | Cognito JWT attached via API client |
