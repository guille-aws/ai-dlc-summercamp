import { Card, CardContent, Typography, Chip, Stack } from "@mui/material";
import type { PreliminaryDecision } from "../types";

export function RecommendationCard({ decision }: { decision?: PreliminaryDecision }) {
  if (!decision) {
    return (
      <Card data-testid="recommendation-card">
        <CardContent>
          <Typography color="text.secondary">No recommendation available.</Typography>
        </CardContent>
      </Card>
    );
  }
  return (
    <Card data-testid="recommendation-card">
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Recommendation
        </Typography>
        <Stack direction="row" spacing={2} alignItems="center">
          <Chip label={decision.outcome} color="primary" />
          <Typography>
            Confidence: {(decision.confidence * 100).toFixed(0)}%
          </Typography>
        </Stack>
      </CardContent>
    </Card>
  );
}
