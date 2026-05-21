import { ExternalLink, X, Star, GitFork, Sparkles } from 'lucide-react';
import { formatCount, formatScore } from '../utils/format';
import { filterReposOnly, getRepoDisplayName } from '../utils/repoDisplay';
import LoadingState from './LoadingState';
import EmptyState from './EmptyState';

export default function RecommendationPanel({
  selectedRepo,
  recommendations,
  loading,
  error,
  onClose,
}) {
  if (!selectedRepo && !loading) return null;

  const repoName = getRepoDisplayName(selectedRepo);
  const results = filterReposOnly(recommendations?.results);

  return (
    <aside className="recommend-panel" aria-label="Similar projects">
      <header className="recommend-panel__header">
        <div>
          <p className="recommend-panel__eyebrow">Similar to</p>
          <h2>{repoName}</h2>
        </div>
        <button
          type="button"
          className="btn btn--icon"
          onClick={onClose}
          aria-label="Close recommendations"
        >
          <X size={20} />
        </button>
      </header>

      <div className="recommend-panel__body">
        {loading && <LoadingState message="Finding similar projects…" />}

        {!loading && error && <EmptyState variant="error" message={error} />}

        {!loading && !error && results.length === 0 && (
          <EmptyState
            variant="noResults"
            message="No similar repositories were returned for this project."
          />
        )}

        {!loading && !error && results.length > 0 && (
          <ul className="recommend-list">
            {results.map((repo) => (
              <li key={repo?.full_name || repo?.id || repo?.rank} className="recommend-card">
                <div className="recommend-card__top">
                  <span className="recommend-card__rank">#{repo?.rank ?? '—'}</span>
                  <span className="recommend-card__similarity" title="Similarity score">
                    <Sparkles size={12} aria-hidden />
                    {formatScore(repo?.similarity)}
                  </span>
                </div>
                <h3>{getRepoDisplayName(repo)}</h3>
                <p>{repo?.description || 'No description.'}</p>
                <div className="recommend-card__meta">
                  {repo?.language && <span className="badge badge--lang">{repo.language}</span>}
                  <span>
                    <Star size={14} aria-hidden />
                    {formatCount(repo?.stars)}
                  </span>
                  <span>
                    <GitFork size={14} aria-hidden />
                    {formatCount(repo?.forks)}
                  </span>
                </div>
                {Array.isArray(repo?.topics) && repo.topics.length > 0 && (
                  <div className="recommend-card__topics">
                    {repo.topics.slice(0, 5).map((t) => (
                      <span key={t} className="topic-pill topic-pill--sm">
                        {t}
                      </span>
                    ))}
                  </div>
                )}
                {repo?.url && (
                  <a
                    href={repo.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn--outline btn--sm"
                  >
                    <ExternalLink size={14} aria-hidden />
                    GitHub
                  </a>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </aside>
  );
}
