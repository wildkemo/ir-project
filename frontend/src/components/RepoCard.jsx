import { ExternalLink, GitFork, GitBranch, Star, AlertCircle, Sparkles } from 'lucide-react';
import ScoreBreakdown from './ScoreBreakdown';
import { formatCount, formatScore } from '../utils/format';

export default function RepoCard({ repo, onSimilar, isSelected, recommendLoading }) {
  const name = repo?.full_name || repo?.title || 'Unknown repository';
  const description = repo?.description || 'No description available.';
  const topics = Array.isArray(repo?.topics) ? repo.topics : [];
  const url = repo?.url || '#';

  return (
    <article className={`repo-card ${isSelected ? 'repo-card--selected' : ''}`}>
      <header className="repo-card__header">
        <div className="repo-card__title-block">
          <span className="repo-card__rank">#{repo?.rank ?? '—'}</span>
          <h3>{name}</h3>
          {repo?.title && repo.title !== repo?.full_name && (
            <p className="repo-card__subtitle">{repo.title}</p>
          )}
        </div>
        <div className="repo-card__score-badge" title="Final relevance score">
          <Sparkles size={14} aria-hidden />
          {formatScore(repo?.score)}
        </div>
      </header>

      <p className="repo-card__description">{description}</p>

      <div className="repo-card__badges">
        {repo?.language && <span className="badge badge--lang">{repo.language}</span>}
        {repo?.license && <span className="badge badge--license">{repo.license}</span>}
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
        <span title="Open issues">
          <AlertCircle size={15} aria-hidden />
          {formatCount(repo?.issues)}
        </span>
        {repo?.watchers != null && (
          <span title="Watchers">
            <GitBranch size={15} aria-hidden />
            {formatCount(repo.watchers)}
          </span>
        )}
      </div>

      {topics.length > 0 && (
        <div className="repo-card__topics">
          {topics.slice(0, 8).map((topic) => (
            <span key={topic} className="topic-pill">
              {topic}
            </span>
          ))}
        </div>
      )}

      <ScoreBreakdown repo={repo} />

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
