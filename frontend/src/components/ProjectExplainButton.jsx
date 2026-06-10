import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import {
  Sparkles,
  X,
  Star,
  GitFork,
  Users,
  BadgeCheck,
  BookOpen,
  Wrench,
  AlertTriangle,
  PlayCircle,
  Lightbulb,
  Code2,
  Activity,
} from 'lucide-react';

import { explainProject } from '../api/projectExplainer';

function MetricCard({ icon, label, value }) {
  return (
    <div className="project-explainer__metric">
      <div className="project-explainer__metric-icon">{icon}</div>
      <div>
        <span>{label}</span>
        <strong>{value ?? 'N/A'}</strong>
      </div>
    </div>
  );
}

function Section({ icon, title, children }) {
  return (
    <section className="project-explainer__section">
      <h4>
        {icon}
        {title}
      </h4>
      {children}
    </section>
  );
}

function List({ items }) {
  if (!items || items.length === 0) {
    return <p className="project-explainer__muted">Not available.</p>;
  }

  return (
    <ul className="project-explainer__list">
      {items.map((item, index) => (
        <li key={`${index}-${item}`}>{item}</li>
      ))}
    </ul>
  );
}

function ScorePill({ label, value }) {
  return (
    <div className="project-explainer__score-pill">
      <span>{label}</span>
      <strong>{value ?? 'N/A'}</strong>
    </div>
  );
}

function ProjectExplainerModal({ explanation, loading, error, onClose }) {
  const repoIdentity = explanation?.repo_identity || {};
  const metrics = explanation?.metrics || {};
  const readme = explanation?.readme_analysis || {};
  const sections = readme.detected_sections || {};
  const scoreLabels = explanation?.scores_interpretation || {};

  return createPortal(
    <div className="project-explainer__overlay" onClick={onClose}>
      <div
        className="project-explainer__modal"
        onClick={(event) => event.stopPropagation()}
      >
        <header className="project-explainer__header">
          <div>
            <p className="project-explainer__eyebrow">
              OpenSeek Project Explainer
            </p>
            <h2>{repoIdentity.full_name || repoIdentity.name || 'Repository Summary'}</h2>
            <p>
              Understand this repository using README, stars, forks,
              contributors, technologies, and quality signals.
            </p>
          </div>

          <button
            type="button"
            className="project-explainer__close"
            onClick={onClose}
            aria-label="Close project explainer"
          >
            <X size={20} />
          </button>
        </header>

        <div className="project-explainer__body">
          {loading && (
            <div className="project-explainer__loading">
              <Sparkles size={22} />
              Generating project explanation...
            </div>
          )}

          {error && (
            <div className="project-explainer__error">
              <AlertTriangle size={18} />
              {error}
            </div>
          )}

          {!loading && !error && explanation && (
            <>
              <div className="project-explainer__summary-card">
                <div>
                  <h3>Project Summary</h3>
                  <p>{explanation.project_summary}</p>
                </div>

                <div className="project-explainer__best-for">
                  <span>Best For</span>
                  <strong>{explanation.best_for}</strong>
                  <small>Difficulty: {explanation.difficulty || 'Unknown'}</small>
                </div>
              </div>

              <div className="project-explainer__metrics-grid">
                <MetricCard icon={<Star size={17} />} label="Stars" value={metrics.stars} />
                <MetricCard icon={<GitFork size={17} />} label="Forks" value={metrics.forks} />
                <MetricCard icon={<Users size={17} />} label="Contributors" value={metrics.contributors_count} />
                <MetricCard icon={<BadgeCheck size={17} />} label="License" value={metrics.license} />
                <MetricCard
                  icon={<Activity size={17} />}
                  label="Health"
                  value={
                    typeof metrics.health_score === 'number'
                      ? `${Math.round(metrics.health_score * 100)}%`
                      : metrics.health_score
                  }
                />
                <MetricCard
                  icon={<BookOpen size={17} />}
                  label="Docs"
                  value={
                    typeof metrics.documentation_score === 'number'
                      ? `${Math.round(metrics.documentation_score * 100)}%`
                      : metrics.documentation_score
                  }
                />
              </div>

              <div className="project-explainer__two-col">
                <Section icon={<Code2 size={17} />} title="Technologies">
                  {repoIdentity.technologies?.length > 0 ? (
                    <div className="project-explainer__chips">
                      {repoIdentity.technologies.map((tech) => (
                        <span key={tech}>{tech}</span>
                      ))}
                    </div>
                  ) : (
                    <p className="project-explainer__muted">
                      No technologies detected from the available data.
                    </p>
                  )}
                </Section>

                <Section icon={<BookOpen size={17} />} title="README Sections">
                  <div className="project-explainer__section-tags">
                    {Object.entries(sections).map(([name, exists]) => (
                      <span
                        key={name}
                        className={exists ? 'is-found' : 'is-missing'}
                      >
                        {exists ? '✓' : '–'} {name}
                      </span>
                    ))}
                  </div>
                </Section>
              </div>

              <div className="project-explainer__scores">
                <ScorePill label="Documentation" value={scoreLabels.documentation} />
                <ScorePill label="Contribution" value={scoreLabels.contribution} />
                <ScorePill label="Health" value={scoreLabels.health} />
                <ScorePill label="Activity" value={scoreLabels.activity} />
                <ScorePill label="Popularity" value={scoreLabels.popularity} />
              </div>

              <Section icon={<Lightbulb size={17} />} title="Why this project is useful">
                <List items={explanation.why_it_matches} />
              </Section>

              <div className="project-explainer__two-col">
                <Section icon={<BadgeCheck size={17} />} title="Strengths">
                  <List items={explanation.strengths} />
                </Section>

                <Section icon={<AlertTriangle size={17} />} title="Limitations / Missing Signals">
                  <List items={explanation.limitations} />
                </Section>
              </div>

              <Section icon={<PlayCircle size={17} />} title="How to start with it">
                <List items={explanation.how_to_use_it} />
              </Section>

              <Section icon={<Wrench size={17} />} title="Contribution guidance">
                <List items={explanation.contribution_guidance} />
              </Section>

              <Section icon={<BookOpen size={17} />} title="README Preview">
                <p className="project-explainer__readme">
                  {readme.preview || 'README content is not available in the dataset.'}
                </p>
              </Section>
            </>
          )}
        </div>
      </div>
    </div>,
    document.body,
  );
}

export default function ProjectExplainButton({ repo, profile = null, query = null }) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [explanation, setExplanation] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!open) return;

    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        setOpen(false);
      }
    };

    window.addEventListener('keydown', handleEscape);

    return () => {
      document.body.style.overflow = originalOverflow;
      window.removeEventListener('keydown', handleEscape);
    };
  }, [open]);

  const handleOpen = async () => {
    setOpen(true);

    if (explanation) return;

    setLoading(true);
    setError(null);

    try {
      const data = await explainProject({ repo, profile, query });
      setExplanation(data);
    } catch (err) {
      setError(err?.message || 'Failed to explain project');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        type="button"
        className="btn btn--secondary"
        onClick={handleOpen}
      >
        <Sparkles size={16} aria-hidden />
        Explain Project
      </button>

      {open && (
        <ProjectExplainerModal
          explanation={explanation}
          loading={loading}
          error={error}
          onClose={() => setOpen(false)}
        />
      )}
    </>
  );
}