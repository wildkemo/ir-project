import { useState } from 'react';
import {
  ExternalLink,
  GitFork,
  GitBranch,
  Star,
  AlertCircle,
  Sparkles,
  HelpCircle,
} from 'lucide-react';

import ScoreBreakdown from './ScoreBreakdown';
import ProjectExplainButton from './ProjectExplainButton';

import { explainResult, getApiErrorMessage } from '../api/client';
import { formatCount, formatScore } from '../utils/format';
import { getRepoDisplayName } from '../utils/repoDisplay';

export default function RepoCard({
  repo,
  searchQuery,
  searchProfile,
  onSimilar,
  isSelected,
  recommendLoading,
}) {
  const [explain, setExplain] = useState(null);
  const [explainLoading, setExplainLoading] = useState(false);
  const [explainError, setExplainError] = useState(null);

  const handleExplain = async () => {
    const identifier = getRepoDisplayName(repo);

    if (!searchQuery?.trim() || !identifier) return;

    if (explain && !explainError) {
      setExplain(null);
      return;
    }

    setExplainLoading(true);
    setExplainError(null);

    try {
      const data = await explainResult({
        query: searchQuery.trim(),
        repo_identifier: identifier,
        profile: searchProfile
          ? {
              project_type: searchProfile.project_type ?? null,
              language: searchProfile.language ?? null,
              goal: searchProfile.goal ?? null,
              level: searchProfile.level ?? null,
              repo_kind: searchProfile.repo_kind ?? null,
              complexity: searchProfile.complexity ?? null,
            }
          : undefined,
      });

      setExplain(data);
    } catch (err) {
      setExplain(null);
      setExplainError(getApiErrorMessage(err));
    } finally {
      setExplainLoading(false);
    }
  };

  const name = getRepoDisplayName(repo);
  const description = repo?.description || 'No description available.';
  const topics = Array.isArray(repo?.topics) ? repo.topics : [];
  const url = repo?.url || repo?.html_url || '#';

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
        {repo?.language && (
          <span className="badge badge--lang">{repo.language}</span>
        )}

        {repo?.license && (
          <span className="badge badge--license">{repo.license}</span>
        )}
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
          <span className="repo-card__topics-label">Tags</span>

          {topics.slice(0, 6).map((topic) => (
            <span key={topic} className="topic-pill">
              {topic}
            </span>
          ))}
        </div>
      )}

      <ScoreBreakdown repo={repo} />

      {searchQuery?.trim() && (
        <div className="repo-card__explain">
          <button
            type="button"
            className="btn btn--ghost btn--sm"
            onClick={handleExplain}
            disabled={explainLoading}
          >
            <HelpCircle size={14} aria-hidden />
            {explainLoading
              ? 'Loading…'
              : explain
                ? 'Hide explanation'
                : 'Why this result?'}
          </button>

          {explainError && (
            <p className="repo-card__explain-error" role="alert">
              {explainError}
            </p>
          )}

          {explain && (
            <dl className="explain-details">
              <div>
                <dt>Final score</dt>
                <dd>{formatScore(explain.final_score)}</dd>
              </div>

              <div>
                <dt>BM25 contribution</dt>
                <dd>{formatScore(explain.bm25_contribution)}</dd>
              </div>

              <div>
                <dt>Semantic contribution</dt>
                <dd>{formatScore(explain.semantic_contribution)}</dd>
              </div>

              <div>
                <dt>Profile contribution</dt>
                <dd>
                  {formatScore(
                    explain.profile_contribution ?? explain.metadata_contribution,
                  )}
                </dd>
              </div>
            </dl>
          )}
        </div>
      )}

      <footer className="repo-card__actions">
        <ProjectExplainButton
          repo={repo}
          profile={searchProfile}
          query={searchQuery}
        />

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