// frontend/src/components/CandidateCard.jsx
import React from "react";

export default function CandidateCard({ r }) {
  return (
    <div style={{ border: "1px solid #ddd", padding: 8, marginBottom: 8 }}>
      <div><strong>{r.candidate_name}</strong> (ID: {r.candidate_id})</div>
      <div>Score: {r.score.toFixed(3)}</div>
    </div>
  );
}
