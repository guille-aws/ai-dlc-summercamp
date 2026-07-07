import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { Typography, Alert, Snackbar } from "@mui/material";
import { apiClient, ApiError } from "../lib/apiClient";
import type { Claim, ReviewSubmission } from "../types";
import { RecommendationCard } from "../components/RecommendationCard";
import { ReasoningList } from "../components/ReasoningList";
import { EvidenceList } from "../components/EvidenceList";
import { DecisionForm } from "../components/DecisionForm";

/** Review Detail (US-06/US-07). Claim id read from ?id= query (static-export friendly). */
export default function ReviewDetailPage() {
  const router = useRouter();
  const id = typeof router.query.id === "string" ? router.query.id : "";
  const [claim, setClaim] = useState<Claim | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);

  useEffect(() => {
    if (!id) return;
    apiClient
      .getClaim(id)
      .then(setClaim)
      .catch((e: ApiError) => setError(e.message));
  }, [id]);

  const handleSubmit = (submission: ReviewSubmission) => {
    setSubmitting(true);
    apiClient
      .submitReview(id, submission)
      .then(() => {
        setDone(true);
        setTimeout(() => router.push("/"), 1200);
      })
      .catch((e: ApiError) => setError(e.message))
      .finally(() => setSubmitting(false));
  };

  if (error) return <Alert severity="error">{error}</Alert>;
  if (!claim) return <Typography>Loading…</Typography>;

  return (
    <>
      <Typography variant="h5" gutterBottom>
        Review Claim {claim.claim_id}
      </Typography>
      <RecommendationCard decision={claim.adjudication_result} />
      <ReasoningList reasoning={claim.adjudication_result?.reasoning_chain ?? []} />
      <EvidenceList claim={claim} />
      <DecisionForm
        recommendation={claim.adjudication_result}
        onSubmit={handleSubmit}
        submitting={submitting}
      />
      <Snackbar open={done} message="Decision submitted" />
    </>
  );
}
