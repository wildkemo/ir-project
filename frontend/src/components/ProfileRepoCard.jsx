import { ExternalLink, GitFork, Star, Sparkles } from 'lucide-react';
import { formatCount, formatScore } from '../utils/format';
import { getRepoDisplayName } from '../utils/repoDisplay';

export default function ProfileRepoCard({
  repo,
  onSimilar,
  isSelected,
  recommendLoading,
}) {
  const name = getRepoDisplayName(repo);
  const description = repo?.description || 'No description available.';
  const topics = Array.isArray(repo?.topics) ? repo.topics : [];
  const url = repo?.url || '#';
  const reasons = Array.isArray(repo?.why_recommended) ? repo.why_recommended : [];
  const breakdown = repo?.score_breakdown || {};

  return (
    <article className={`repo-card profile-repo-card ${isSelected ? 'repo-card--selected' : ''}`}>
      <header className="repo-card__header">
        <div className="repo-card__title-block">
          <span className="repo-card__rank">#{repo?.rank ?? '—'}</span>
          <h3>{name}</h3>
        </div>
        <div className="repo-card__score-badge" title="Profile match score">
          <Sparkles size={14} aria-hidden />
          {formatScore(repo?.score)}
        </div>
      </header>

      <p className="repo-card__description">{description}</p>

      <div className="repo-card__badges">
        {repo?.language && <span className="badge badge--lang">{repo.language}</span>}
        <span className="badge badge--profile">Profile match</span>
      </div>

      <div className="repo-card__stats">
        <span title="Stars">
          <Star size={15} aria-hidden />
          {formatCount(repo?.stars)}
        </span>
        <span title="Forks">
          <GitFork size={15} aria-hidden />
          {formatCount(repo?.forks)}
        </span>
      </div>

      {topics.length > 0 && (
        <div className="repo-card__topics">
          {topics.slice(0, 6).map((topic) => (
            <span key={topic} className="topic-pill">
              {topic}
            </span>
          ))}
        </div>
      )}

      {reasons.length > 0 && (
        <div className="profile-why">
          <p className="profile-why__title">Why recommended</p>
          <ul>
            {reasons.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
        </div>
      )}

      {Object.keys(breakdown).length > 0 && (
        <div className="profile-breakdown">
          {Object.entries(breakdown)
            .filter(([, v]) => Number(v) > 0)
            .slice(0, 4)
            .map(([key, value]) => (
              <span key={key} className="profile-breakdown__chip">
                {key.replace(/_/g, ' ')}: {formatScore(value)}
              </span>
            ))}
        </div>
      )}

      <footer className="repo-card__actions">
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn--outline"
        >
          <ExternalLink size={16} aria-hidden />
          GitHub
        </a>
        <button
          type="button"
          className="btn btn--secondary"
          onClick={() => onSimilar?.(repo)}
          disabled={recommendLoading}
        >
          Similar Projects
        </button>
      </footer>
    </article>
  );
}
