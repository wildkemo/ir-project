import React from "react";

export default function RepoExplainerPanel({ explanation, onClose }) {
  if (!explanation) return null;

  const scores = explanation.scores || {};
  const roadmap = explanation.roadmap;

  return (
    <div className="advisor-panel">
      <div className="advisor-header">
        <h2>{explanation.repo_name}</h2>
        {onClose && <button onClick={onClose}>Close</button>}
      </div>

      <p>{explanation.summary}</p>

      <h3>Best For</h3>
      <p>{explanation.best_for}</p>

      <h3>Technologies</h3>
      <div className="tag-row">
        {(explanation.technologies || []).map((t) => (
          <span className="tag" key={t}>{t}</span>
        ))}
      </div>

      <h3>Scores</h3>
      <ul>
        <li>Documentation: {scores.documentation_score}</li>
        <li>Contribution: {scores.contribution_score}</li>
        <li>Health: {scores.health_score}</li>
        <li>Difficulty: {explanation.difficulty}</li>
      </ul>

      <h3>Why Recommended</h3>
      <ul>
        {(explanation.why_recommended || []).map((r, idx) => (
          <li key={idx}>{r}</li>
        ))}
      </ul>

      <h3>Strengths</h3>
      <ul>
        {(explanation.strengths || []).map((r, idx) => (
          <li key={idx}>{r}</li>
        ))}
      </ul>

      <h3>Weaknesses</h3>
      <ul>
        {(explanation.weaknesses || []).map((r, idx) => (
          <li key={idx}>{r}</li>
        ))}
      </ul>

      {roadmap && (
        <>
          <h3>{roadmap.title}</h3>
          <ol>
            {(roadmap.steps || []).map((step, idx) => (
              <li key={idx}>{step}</li>
            ))}
          </ol>
        </>
      )}
    </div>
  );
}
