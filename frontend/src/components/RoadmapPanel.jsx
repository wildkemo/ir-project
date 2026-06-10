import React from "react";

export default function RoadmapPanel({ roadmap }) {
  if (!roadmap) return null;

  return (
    <div className="roadmap-panel">
      <h2>{roadmap.title}</h2>
      <p>Type: {roadmap.roadmap_type}</p>
      <ol>
        {(roadmap.steps || []).map((step, idx) => (
          <li key={idx}>{step}</li>
        ))}
      </ol>
    </div>
  );
}
