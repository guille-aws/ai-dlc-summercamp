# CLAIRO U7 Web UI - Infrastructure Design

**Summary**: No new AWS resource types. U7 is hosted on the AWS Amplify app already declared in U0's `web_stack.py`. The web build artifact (static export) is deployed to Amplify; environment variables (API URL, Cognito ids, region) are provided by the web stack.

No infra questions required — hosting decided in U0.

## Component → Infrastructure Mapping
| U7 Element | Infrastructure (U0) | Notes |
|---|---|---|
| Reviewer web app (static SPA) | AWS Amplify Hosting app `clairo-dev-web` | serves the built Next.js export |
| Auth | Cognito user pool + web client | via Amplify env vars |
| API calls | API Gateway (U5) | CLAIRO_API_URL env |

## Environment Variables (from U0 web_stack)
- `CLAIRO_API_URL`, `CLAIRO_USER_POOL_ID`, `CLAIRO_USER_POOL_CLIENT_ID`, `CLAIRO_REGION`.

## Changes to Apply in Code Generation
- None to CDK (web stack exists). The `web/` project builds to a static export that Amplify serves. Repo/branch connection to Amplify is an operational step (kept out of CDK to avoid committing tokens).

## Prerequisite
- The API (U5), Cognito (U0) must be deployed; their values populate the Amplify env vars.
