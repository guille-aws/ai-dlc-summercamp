# CLAIRO U7 Web UI - Business Rules

## Authentication (US-12)
- **UI-1**: Unauthenticated users are redirected to Login; protected routes are guarded.
- **UI-2**: Every API request includes the Cognito JWT (Authorization header).

## Review Flow (US-06, US-07)
- **UI-3**: The Review Queue lists claims returned by GET /reviews (pending review).
- **UI-4**: Review Detail displays the recommended outcome, confidence, reasoning chain, and highlighted evidence snippets (page/bbox) (Q4:A).
- **UI-5**: The DecisionForm requires an outcome (approve/deny/partial/needs_more_info); a rationale is required when the outcome differs from the recommendation (override).
- **UI-6**: On successful submit, the UI reflects the finalized status and returns to the queue.

## Claim Status (US-09)
- **UI-7**: Claim Status shows status, decision, reasoning, and the explanation reference for a looked-up claim id.

## Error Handling
- **UI-8**: API errors (401/403/404/5xx) are surfaced as user-friendly messages; 401 triggers re-authentication.

## Scope (MVP)
- **UI-9**: MVP screens are Login, Review Queue, Review Detail, Claim Status (Q3:A). Supervisor admin (threshold/audit) is deferred (those APIs exist and can be added later).
- **UI-10**: Evidence is shown as text snippets with page/bbox metadata; no document rendering for MVP (Q4:A).

## Authorization (defense-in-depth)
- **UI-11**: UI hides reviewer actions from users lacking the role, but the backend remains the authoritative enforcer (OR-15).
