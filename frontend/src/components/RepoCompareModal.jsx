import React from "react";

export default function RepoCompareModal({ comparison, onClose }) {
  if (!comparison) return null;

  return (
    <div className="compare-modal">
      <div className="compare-header">
        <h2>Repository Comparison</h2>
        {onClose && <button onClick={onClose}>Close</button>}
      </div>

      <p><strong>Winner:</strong> {comparison.winner}</p>
      <p>{comparison.recommendation}</p>

      <table>
        <thead>
          <tr>
            <th>Feature</th>
            <th>{comparison.repo_a}</th>
            <th>{comparison.repo_b}</th>
          </tr>
        </thead>
        <tbody>
          {(comparison.comparison_table || []).map((row) => (
            <tr key={row.feature}>
              <td>{row.feature}</td>
              <td>{row.repo_a}</td>
              <td>{row.repo_b}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
