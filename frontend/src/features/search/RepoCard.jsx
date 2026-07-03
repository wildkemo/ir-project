import { useState } from 'react';
import {
  Star, GitFork, Eye, ExternalLink, Heart, Cpu, GitCompare, Map, Info, Zap, Brain,
} from 'lucide-react';
import Badge from '../../components/ui/Badge';
import Button from '../../components/ui/Button';
import { formatNumber, getLangColor, truncate } from '../../utils/format';
import { useAuthStore } from '../../stores/authStore';
import { loadAccessToken } from '../../utils/authStorage';
import { getRepoDisplayName, isGitHubRepo } from '../../utils/repoDisplay';
import './RepoCard.css';

/**
 * Universal repo card used in Search, Dashboard, Recommendations, etc.
 * mode: 'search' | 'profile' | 'compact'
 */
export default function RepoCard({
  repo,
  mode = 'search',
  isFavorite = false,
  onFavoriteToggle,
  onExplain,
  onCompare,
  onRoadmap,
  onSimilar,
  onSelect,
  selected = false,
}) {
  const user = useAuthStore((s) => s.user);
  const isAuthenticated = Boolean(user && loadAccessToken());
  const [favPending, setFavPending] = useState(false);

  if (!isGitHubRepo(repo)) return null;

  const name         = getRepoDisplayName(repo);
  const description  = repo.description || 'No description available.';
  const stars        = repo.stars ?? repo.stargazers_count ?? 0;
  const forks        = repo.forks ?? repo.forks_count ?? 0;
  const lang         = repo.language ?? repo.languages?.[0];
  const topics       = Array.isArray(repo.topics) ? repo.topics.slice(0, 4) : [];
  const score        = repo.score ?? repo.similarity ?? repo.final_score;
  const matchPct     = score != null ? Math.round((score <= 1 ? score * 100 : score)) : null;
  const engine       = repo.engine;
  const url          = repo.url || repo.html_url;

  const handleFav = async (e) => {
    e.stopPropagation();
    if (!onFavoriteToggle || favPending) return;
    setFavPending(true);
    try { await onFavoriteToggle(repo); }
    finally { setFavPending(false); }
  };

  return (
    <article
      className={`repo-card repo-card--${mode} ${selected ? 'repo-card--selected' : ''}`}
      onClick={() => onSelect?.(repo)}
      tabIndex={onSelect ? 0 : undefined}
      onKeyDown={(e) => e.key === 'Enter' && onSelect?.(repo)}
      role={onSelect ? 'button' : 'article'}
      aria-label={`Repository: ${name}`}
    >
      <div className="repo-card__header">
        <div className="repo-card__name-wrap">
          {lang && (
            <span
              className="repo-card__lang-dot"
              style={{ background: getLangColor(lang) }}
              title={lang}
            />
          )}
          <h3 className="repo-card__name">{name}</h3>
        </div>

        <div className="repo-card__header-right">
          {matchPct != null && (
            <span className={`repo-card__score ${matchPct >= 70 ? 'repo-card__score--high' : ''}`}>
              {matchPct}%
            </span>
          )}
          {engine === 'hybrid' && (
            <Badge variant="search" size="sm"><Zap size={10} />Hybrid</Badge>
          )}
          {engine === 'semantic' && (
            <Badge variant="semantic" size="sm"><Brain size={10} />Semantic</Badge>
          )}
        </div>
      </div>

      <p className="repo-card__desc">{truncate(description, 130)}</p>

      <div className="repo-card__meta">
        {lang && <span className="repo-card__lang">{lang}</span>}
        <span className="repo-card__stat"><Star size={12} />{formatNumber(stars)}</span>
        <span className="repo-card__stat"><GitFork size={12} />{formatNumber(forks)}</span>
      </div>

      {topics.length > 0 && (
        <div className="repo-card__topics">
          {topics.map((t) => (
            <Badge key={t} variant="default" size="sm">{t}</Badge>
          ))}
        </div>
      )}

      <div className="repo-card__actions" onClick={(e) => e.stopPropagation()}>
        {onExplain && (
          <Button size="sm" variant="ai" icon={<Cpu size={13} />} onClick={() => onExplain(repo)}>
            Explain
          </Button>
        )}
        {onRoadmap && (
          <Button size="sm" variant="roadmap" icon={<Map size={13} />} onClick={() => onRoadmap(repo)}>
            Roadmap
          </Button>
        )}
        {onCompare && (
          <Button size="sm" variant="ghost" icon={<GitCompare size={13} />} onClick={() => onCompare(repo)}>
            Compare
          </Button>
        )}
        {onSimilar && (
          <Button size="sm" variant="ghost" icon={<Info size={13} />} onClick={() => onSimilar(repo)}>
            Similar
          </Button>
        )}
        <div className="repo-card__actions-spacer" />
        {isAuthenticated && onFavoriteToggle && (
          <button
            className={`repo-card__fav-btn ${isFavorite ? 'repo-card__fav-btn--active' : ''}`}
            onClick={handleFav}
            disabled={favPending}
            aria-label={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
          >
            <Heart size={15} fill={isFavorite ? 'currentColor' : 'none'} />
          </button>
        )}
        {url && (
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="repo-card__github-link"
            aria-label="Open on GitHub"
            onClick={(e) => e.stopPropagation()}
          >
            <ExternalLink size={14} />
          </a>
        )}
      </div>
    </article>
  );
}
