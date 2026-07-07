// Typed fetch client for the CLAIRO API. Attaches the Cognito JWT (NFR-U7 Q5:A).
import { getIdToken } from "./amplify";
import type { Claim, ReviewSubmission } from "../types";

const API_URL = process.env.NEXT_PUBLIC_CLAIRO_API_URL ?? "";

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = await getIdToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string> | undefined),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_URL}${path}`, { ...init, headers });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new ApiError(res.status, text || res.statusText);
  }
  // Some endpoints may return empty bodies.
  const body = await res.text();
  return (body ? JSON.parse(body) : {}) as T;
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

export const apiClient = {
  listReviews(): Promise<{ tasks: string[] }> {
    return request("/reviews", { method: "GET" });
  },
  getClaim(id: string): Promise<Claim> {
    return request(`/claims/${encodeURIComponent(id)}`, { method: "GET" });
  },
  submitReview(
    id: string,
    submission: ReviewSubmission
  ): Promise<{ claim_id: string; status: string }> {
    return request(`/reviews/${encodeURIComponent(id)}`, {
      method: "POST",
      body: JSON.stringify(submission),
    });
  },
};
