import React from "react";

export default function AdvisorSummaryPanel({ advisor }) {
  if (!advisor) return null;

  return (
    <div className="advisor-summary-panel">
      <h2>AI Advisor Summary</h2>
      <p>{advisor.summary}</p>

      <h3>Recommended Repo</h3>
      <p>{advisor.recommended_repo || "No recommendation available"}</p>

      <h3>Recommended Order</h3>
      <ol>
        {(advisor.recommended_order || []).map((repo) => (
          <li key={repo}>{repo}</li>
        ))}
      </ol>

      {advisor.roadmap_for_recommended_repo && (
        <>
          <h3>{advisor.roadmap_for_recommended_repo.title}</h3>
          <ol>
            {(advisor.roadmap_for_recommended_repo.steps || []).map((step, idx) => (
              <li key={idx}>{step}</li>
            ))}
          </ol>
        </>
      )}
    </div>
  );
}
