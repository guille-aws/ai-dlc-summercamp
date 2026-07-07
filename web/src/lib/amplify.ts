// Amplify Auth (Cognito) configuration (NFR-U7 Q2:A).
import { Amplify } from "aws-amplify";
import { fetchAuthSession } from "aws-amplify/auth";

let configured = false;

export function configureAmplify(): void {
  if (configured) return;
  Amplify.configure({
    Auth: {
      Cognito: {
        userPoolId: process.env.NEXT_PUBLIC_CLAIRO_USER_POOL_ID ?? "",
        userPoolClientId: process.env.NEXT_PUBLIC_CLAIRO_USER_POOL_CLIENT_ID ?? "",
      },
    },
  });
  configured = true;
}

/** Return the current Cognito ID token (JWT) or null if unauthenticated. */
export async function getIdToken(): Promise<string | null> {
  try {
    const session = await fetchAuthSession();
    return session.tokens?.idToken?.toString() ?? null;
  } catch {
    return null;
  }
}
