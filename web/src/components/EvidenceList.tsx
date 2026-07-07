import { Typography, List, ListItem, ListItemText } from "@mui/material";
import type { Claim } from "../types";

/** Lists highlighted evidence snippets with page/bbox metadata (UI-4, Q4:A). */
export function EvidenceList({ claim }: { claim: Claim }) {
  const refs = claim.evidence_refs ?? [];
  if (!refs.length) {
    return (
      <Typography color="text.secondary" data-testid="evidence-list">
        No evidence captured.
      </Typography>
    );
  }
  return (
    <>
      <Typography variant="h6" sx={{ mt: 2 }}>
        Highlighted Evidence
      </Typography>
      <List dense data-testid="evidence-list">
        {refs.map((ev, i) => (
          <ListItem key={i}>
            <ListItemText
              primary={ev.document_ref?.key ?? "document"}
              secondary={`page ${ev.page ?? "?"}${
                ev.bbox ? ` · bbox [${ev.bbox.map((n) => n.toFixed(2)).join(", ")}]` : ""
              }`}
            />
          </ListItem>
        ))}
      </List>
    </>
  );
}
