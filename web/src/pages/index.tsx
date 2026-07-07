import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Typography,
  List,
  ListItemButton,
  ListItemText,
  Alert,
} from "@mui/material";
import { apiClient, ApiError } from "../lib/apiClient";

/** Review Queue (US-06). Lists pending-review claim ids. */
export default function ReviewQueuePage() {
  const [tasks, setTasks] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient
      .listReviews()
      .then((r) => setTasks(r.tasks ?? []))
      .catch((e: ApiError) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <>
      <Typography variant="h5" gutterBottom>
        Review Queue
      </Typography>
      {error && <Alert severity="error">{error}</Alert>}
      {loading ? (
        <Typography>Loading…</Typography>
      ) : tasks.length === 0 ? (
        <Typography color="text.secondary">No claims pending review.</Typography>
      ) : (
        <List>
          {tasks.map((id) => (
            <ListItemButton
              key={id}
              component={Link}
              href={`/review?id=${encodeURIComponent(id)}`}
              data-testid="review-task-row"
            >
              <ListItemText primary={id} secondary="Pending review" />
            </ListItemButton>
          ))}
        </List>
      )}
    </>
  );
}
