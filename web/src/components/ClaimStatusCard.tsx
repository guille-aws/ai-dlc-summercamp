import { Card, CardContent, Typography, Divider } from "@mui/material";
import type { Claim } from "../types";
import { RecommendationCard } from "./RecommendationCard";
import { ReasoningList } from "./ReasoningList";

export function ClaimStatusCard({ claim }: { claim: Claim }) {
  return (
    <Card sx={{ mt: 2 }} data-testid="claim-status-card">
      <CardContent>
        <Typography variant="h6">Claim {claim.claim_id}</Typography>
        <Typography>Status: {claim.status}</Typography>
        <Typography>
          Claimant: {claim.claimant?.name} · {claim.total_amount} {claim.currency}
        </Typography>
        <Divider sx={{ my: 2 }} />
        <RecommendationCard decision={claim.adjudication_result} />
        <ReasoningList reasoning={claim.adjudication_result?.reasoning_chain ?? []} />
        {claim.compliance_result && (
          <Typography sx={{ mt: 2 }} color={claim.compliance_result.compliant ? "success.main" : "warning.main"}>
            Compliance: {claim.compliance_result.compliant ? "compliant" : "flags present"}
            {claim.compliance_result.gdpr_flags?.length
              ? ` (${claim.compliance_result.gdpr_flags.length} GDPR flag(s))`
              : ""}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}
