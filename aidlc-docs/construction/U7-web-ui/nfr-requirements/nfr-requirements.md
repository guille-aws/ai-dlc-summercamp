# CLAIRO U7 Web UI - NFR Requirements

> Extensions OFF. MVP defaults only.

## Rendering / Hosting
- **NFR-U7-1**: Static export / client-side rendering (SPA-style) (Q1:A) — deploys cleanly to AWS Amplify Hosting.
- **NFR-U7-2**: Config (API URL, Cognito pool/client, region) injected via Amplify environment variables (from U0 web stack).

## UI / Styling
- **NFR-U7-3**: Component library for fast, accessible components (Q2:A). Concrete choice: **MUI (Material UI)** — mainstream, accessible, good Next.js support. (Cloudscape is an acceptable alternative; noted.)

## Accessibility
- **NFR-U7-4**: Semantic HTML, form labels, keyboard navigation as sensible defaults (Q3:A). Not a formal WCAG 2.1 AA audit — full compliance would require manual testing with assistive tech and expert review.

## Performance
- **NFR-U7-5**: Lightweight SPA; data fetched on demand from the U5 API. No heavy client compute.

## Security
- **NFR-U7-6**: Cognito JWT attached to API calls; no secrets in client code; public SPA client (no client secret).
- **NFR-U7-7**: Synthetic data only.

## Testing
- **NFR-U7-8**: No automated frontend tests (Q4:A); manual + integration validation in Build & Test.
