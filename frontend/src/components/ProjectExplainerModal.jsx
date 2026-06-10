import React from "react";

function ScoreBadge({ label, value }) {
  const display =
    typeof value === "number" ? `${Math.round(value * 100)}%` : value ?? "N/A";

  return (
    <div className="px-3 py-2 rounded-xl border border-slate-700 bg-slate-900/60">
      <div className="text-xs text-slate-400">{label}</div>
      <div className="text-sm font-semibold text-white">{display}</div>
    </div>
  );
}

function ListBlock({ title, items }) {
  if (!items || items.length === 0) return null;

  return (
    <div className="mt-4">
      <h4 className="text-sm font-semibold text-white mb-2">{title}</h4>
      <ul className="list-disc list-inside space-y-1 text-sm text-slate-300">
        {items.map((item, idx) => (
          <li key={idx}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export default function ProjectExplainerModal({ open, onClose, explanation, loading, error }) {
  if (!open) return null;

  const repo = explanation?.repo_identity || {};
  const metrics = explanation?.metrics || {};
  const readme = explanation?.readme_analysis || {};
  const detectedSections = readme.detected_sections || {};
  const snippets = readme.section_snippets || {};
  const scores = explanation?.scores_interpretation || {};

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
      <div className="w-full max-w-5xl max-h-[90vh] overflow-y-auto rounded-2xl bg-slate-950 border border-slate-700 shadow-2xl">
        <div className="sticky top-0 bg-slate-950 border-b border-slate-800 px-6 py-4 flex items-start justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-white">
              Project Explainer
            </h2>
            <p className="text-sm text-slate-400">
              Understand the repository without opening GitHub
            </p>
          </div>
          <button
            onClick={onClose}
            className="px-3 py-1 rounded-lg bg-slate-800 text-slate-200 hover:bg-slate-700"
          >
            Close
          </button>
        </div>

        <div className="p-6">
          {loading && (
            <div className="text-slate-300">Generating project explanation...</div>
          )}

          {error && (
            <div className="text-red-400">
              Failed to load project explanation: {String(error)}
            </div>
          )}

          {!loading && !error && explanation && (
            <>
              <div className="mb-5">
                <h3 className="text-2xl font-bold text-white">
                  {repo.full_name || repo.name}
                </h3>
                <p className="text-slate-400 mt-1">{repo.description}</p>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
                <ScoreBadge label="Stars" value={metrics.stars} />
                <ScoreBadge label="Forks" value={metrics.forks} />
                <ScoreBadge label="Contributors" value={metrics.contributors_count} />
                <ScoreBadge label="License" value={metrics.license} />
                <ScoreBadge label="Documentation" value={metrics.documentation_score} />
                <ScoreBadge label="Contribution" value={metrics.contribution_score} />
                <ScoreBadge label="Health" value={metrics.health_score} />
                <ScoreBadge label="Activity" value={metrics.activity_score} />
              </div>

              <section className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
                <h4 className="text-sm font-semibold text-violet-300 mb-2">
                  Summary
                </h4>
                <p className="text-slate-200 leading-relaxed">
                  {explanation.project_summary}
                </p>
              </section>

              <div className="grid md:grid-cols-2 gap-4 mt-4">
                <section className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
                  <h4 className="text-sm font-semibold text-violet-300 mb-2">
                    Best For
                  </h4>
                  <p className="text-slate-200">{explanation.best_for}</p>
                  <p className="text-sm text-slate-400 mt-2">
                    Difficulty: {explanation.difficulty}
                  </p>
                </section>

                <section className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
                  <h4 className="text-sm font-semibold text-violet-300 mb-2">
                    Technologies
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {(repo.technologies || []).length > 0 ? (
                      repo.technologies.map((tech) => (
                        <span
                          key={tech}
                          className="text-xs px-2 py-1 rounded-full bg-violet-900/50 text-violet-100 border border-violet-700"
                        >
                          {tech}
                        </span>
                      ))
                    ) : (
                      <span className="text-slate-400 text-sm">No technologies detected.</span>
                    )}
                  </div>
                </section>
              </div>

              <ListBlock title="Why this repo matches" items={explanation.why_it_matches} />
              <ListBlock title="Strengths" items={explanation.strengths} />
              <ListBlock title="Limitations / Missing Signals" items={explanation.limitations} />
              <ListBlock title="How to use it" items={explanation.how_to_use_it} />
              <ListBlock title="Contribution guidance" items={explanation.contribution_guidance} />

              <section className="mt-5 rounded-xl border border-slate-800 bg-slate-900/50 p-4">
                <h4 className="text-sm font-semibold text-violet-300 mb-2">
                  README Preview
                </h4>
                <p className="text-sm text-slate-300 leading-relaxed">
                  {readme.preview}
                </p>
              </section>

              <section className="mt-5 rounded-xl border border-slate-800 bg-slate-900/50 p-4">
                <h4 className="text-sm font-semibold text-violet-300 mb-3">
                  Detected README Sections
                </h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {Object.entries(detectedSections).map(([key, value]) => (
                    <div
                      key={key}
                      className={`text-xs rounded-lg px-2 py-2 border ${
                        value
                          ? "bg-emerald-900/30 border-emerald-700 text-emerald-200"
                          : "bg-slate-900 border-slate-700 text-slate-400"
                      }`}
                    >
                      {value ? "✓" : "–"} {key}
                    </div>
                  ))}
                </div>

                {Object.keys(snippets).length > 0 && (
                  <div className="mt-4 space-y-3">
                    {Object.entries(snippets).map(([section, text]) => (
                      <div key={section}>
                        <div className="text-xs uppercase text-slate-500 mb-1">{section}</div>
                        <p className="text-sm text-slate-300">{text}</p>
                      </div>
                    ))}
                  </div>
                )}
              </section>

              <section className="mt-5 rounded-xl border border-slate-800 bg-slate-900/50 p-4">
                <h4 className="text-sm font-semibold text-violet-300 mb-2">
                  Score Interpretation
                </h4>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
                  {Object.entries(scores).map(([key, value]) => (
                    <ScoreBadge key={key} label={key} value={value} />
                  ))}
                </div>
              </section>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
