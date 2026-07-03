import { useEffect, useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import {
  ArrowLeft, ExternalLink, Star, GitFork, Cpu, Map, Sparkles, AlertCircle,
} from 'lucide-react';
import { getRepoDetails } from '../services/searchService';
import { recommend } from '../services/searchService';
import { addFavorite, removeFavorite, getFavorites } from '../services/userService';
import { getErrorMessage } from '../services/api';
import { normalizeRepoRecord, filterReposOnly } from '../utils/repoDisplay';
import { formatNumber } from '../utils/format';
import { useAuthStore } from '../stores/authStore';
import { loadAccessToken } from '../utils/authStorage';
import { useProfile } from '../hooks/useProfile';
import RepoCard from '../features/search/RepoCard';
import AIAdvisorPanel from '../features/ai/AIAdvisorPanel';
import Badge from '../components/ui/Badge';
import Button from '../components/ui/Button';
import { SkeletonCard } from '../components/ui/Skeleton';
import EmptyState from '../components/ui/EmptyState';
import Spinner from '../components/ui/Spinner';
import './RepositoryDetailsPage.css';

export default function RepositoryDetailsPage() {
  const { owner, repo: repoName } = useParams();
  const identifier = owner && repoName ? `${owner}/${repoName}` : null;
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const isAuthenticated = Boolean(user && loadAccessToken());
  const { profile } = useProfile();

  const [repo, setRepo] = useState(null);
  const [similar, setSimilar] = useState([]);
  const [loading, setLoading] = useState(true);
  const [similarLoading, setSimilarLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isFavorite, setIsFavorite] = useState(false);
  const [favPending, setFavPending] = useState(false);

  useEffect(() => {
    if (!identifier) {
      setError('Invalid repository identifier.');
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    getRepoDetails(identifier)
      .then((data) => setRepo(normalizeRepoRecord(data, identifier)))
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }, [identifier]);

  useEffect(() => {
    if (!identifier || !isAuthenticated) return;
    getFavorites()
      .then((favs) => setIsFavorite(favs.some((f) => f.repo_identifier === identifier)))
      .catch(() => {});
  }, [identifier, isAuthenticated]);

  useEffect(() => {
    if (!identifier || !repo) return;
    setSimilarLoading(true);
    recommend({ repo_identifier: identifier, top_k: 6 })
      .then((data) => setSimilar(filterReposOnly(data?.results ?? [])))
      .catch(() => setSimilar([]))
      .finally(() => setSimilarLoading(false));
  }, [identifier, repo]);

  const toggleFavorite = async () => {
    if (!identifier || favPending) return;
    setFavPending(true);
    try {
      if (isFavorite) {
        await removeFavorite(identifier);
        setIsFavorite(false);
      } else {
        await addFavorite(identifier);
        setIsFavorite(true);
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setFavPending(false);
    }
  };

  if (loading) {
    return (
      <div className="repo-details page-enter">
        <div className="repo-details__loading">
          <Spinner size="lg" />
          <p>Loading repository details…</p>
        </div>
      </div>
    );
  }

  if (error || !repo) {
    return (
      <div className="repo-details page-enter">
        <Button variant="ghost" icon={<ArrowLeft size={15} />} onClick={() => navigate(-1)}>
          Back
        </Button>
        <EmptyState
          icon={<AlertCircle size={28} />}
          title="Repository not found"
          description={error || 'This repository could not be loaded from the index.'}
          action={<Button variant="primary" onClick={() => navigate('/search')}>Go to search</Button>}
        />
      </div>
    );
  }

  return (
    <div className="repo-details page-enter">
      <div className="repo-details__top">
        <Button variant="ghost" size="sm" icon={<ArrowLeft size={15} />} onClick={() => navigate(-1)}>
          Back
        </Button>
        <div className="repo-details__actions">
          {isAuthenticated && (
            <Button variant="secondary" size="sm" loading={favPending} onClick={toggleFavorite}>
              {isFavorite ? 'Remove favorite' : 'Save favorite'}
            </Button>
          )}
          {repo.url && (
            <a href={repo.url} target="_blank" rel="noopener noreferrer" className="repo-details__github">
              <ExternalLink size={14} /> GitHub
            </a>
          )}
        </div>
      </div>

      <header className="repo-details__header">
        <h1 className="repo-details__title">{repo.full_name}</h1>
        <p className="repo-details__desc">{repo.description || 'No description available.'}</p>
        <div className="repo-details__meta">
          {repo.language && <Badge variant="default">{repo.language}</Badge>}
          <span><Star size={13} /> {formatNumber(repo.stars)} stars</span>
          <span><GitFork size={13} /> {formatNumber(repo.forks)} forks</span>
        </div>
        {repo.topics?.length > 0 && (
          <div className="repo-details__topics">
            {repo.topics.slice(0, 8).map((t) => (
              <Badge key={t} variant="default" size="sm">{t}</Badge>
            ))}
          </div>
        )}
      </header>

      <div className="repo-details__layout">
        <section className="repo-details__panel">
          <div className="repo-details__panel-header">
            <Cpu size={16} />
            <h2>AI Advisor</h2>
          </div>
          <AIAdvisorPanel repo={repo} profile={profile} />
        </section>

        <section className="repo-details__similar">
          <div className="repo-details__panel-header">
            <Sparkles size={16} />
            <h2>Similar Projects</h2>
          </div>

          {similarLoading && (
            <div className="repo-details__similar-grid">
              {Array.from({ length: 3 }).map((_, i) => <SkeletonCard key={i} />)}
            </div>
          )}

          {!similarLoading && similar.length === 0 && (
            <EmptyState
              icon={<Sparkles size={24} />}
              title="No similar repositories"
              description="Similar projects will appear when the recommendation engine has indexed this repo."
            />
          )}

          {!similarLoading && similar.length > 0 && (
            <div className="repo-details__similar-grid">
              {similar.map((item) => (
                <RepoCard
                  key={item.full_name ?? item.title}
                  repo={item}
                  mode="compact"
                  onSelect={(r) => navigate(`/repository/${r.full_name}`)}
                  onRoadmap={(r) => navigate('/roadmap', { state: { repo: r } })}
                  onExplain={(r) => navigate('/advisor', { state: { repo: r } })}
                />
              ))}
            </div>
          )}

          <Link to="/recommendations" state={{ repo }} className="repo-details__similar-link">
            <Map size={14} /> View all similar projects
          </Link>
        </section>
      </div>
    </div>
  );
}
