import { Typography, List, ListItem, ListItemText } from "@mui/material";

export function ReasoningList({ reasoning }: { reasoning: string[] }) {
  if (!reasoning?.length) return null;
  return (
    <>
      <Typography variant="h6" sx={{ mt: 2 }}>
        Reasoning
      </Typography>
      <List dense data-testid="reasoning-list">
        {reasoning.map((step, i) => (
          <ListItem key={i}>
            <ListItemText primary={step} />
          </ListItem>
        ))}
      </List>
    </>
  );
}
