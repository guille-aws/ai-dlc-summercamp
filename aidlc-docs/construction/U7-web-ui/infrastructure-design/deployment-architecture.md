# CLAIRO U7 Web UI - Deployment Architecture

## Diagram (text)
```
[Reviewer browser] --HTTPS--> AWS Amplify Hosting (clairo-dev-web, static Next.js export)
        |                                   |
        | Amplify Auth (Cognito)            | env: CLAIRO_API_URL, USER_POOL_ID, CLIENT_ID, REGION
        v                                   v
   Cognito user pool                 API Gateway (U5 Claim API) --Bearer JWT-->
```

## Build & Deploy
- Build: `cd web && npm install && npm run build` (static export to `web/out`).
- Deploy: Amplify Hosting serves the build. Repo/branch connection or manual artifact upload is an operational step.
- Config: env vars provided by U0 web stack (Amplify app environment variables).

## Notes
- SPA calls the U5 API with the Cognito JWT; no server-side component for the UI.
