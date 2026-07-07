# CLAIRO U7 Web UI - Business Logic Model

The UI is a thin presentation layer over the U5 Claim API. Business logic lives in the backend; the UI handles auth, data fetching, form state, and display.

## Modules
- **auth**: Amplify Auth configuration + session/JWT retrieval; route guard redirecting unauthenticated users to Login.
- **apiClient**: typed fetch wrapper. Attaches `Authorization: Bearer <jwt>` from the Amplify session. Methods:
  - `listReviews() -> string[]`
  - `getClaim(id) -> Claim`
  - `submitReview(id, {outcome, rationale, isOverride}) -> result`
- **types**: TypeScript interfaces mirroring the canonical claim/decision shapes.

## Flows
### Login (US-12)
Amplify Authenticator → on success, store session; guarded routes become accessible. Role (Cognito group) available from the token for UI gating.

### Review Queue (US-06)
On mount → `listReviews()` → render task list. Click row → navigate to Review Detail.

### Review Detail + Decide/Override (US-07)
Load `getClaim(id)` → render recommendation (adjudication_result), confidence, reasoning, highlighted evidence. Reviewer submits DecisionForm → `submitReview(...)`. On override, backend emits the feedback event (transparent to UI).

### Claim Status (US-09)
Enter claim id → `getClaim(id)` → render status, decision, reasoning, explanation reference.

## Role Gating (UI-side, defense-in-depth)
- Review Queue / Detail actions shown for Reviewer/Supervisor. (Backend enforces authoritative checks; UI gating is UX only.)
