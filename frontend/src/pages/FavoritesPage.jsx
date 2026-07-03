import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Heart, Trash2 } from 'lucide-react';
import { getFavorites, removeFavorite } from '../services/userService';
import { getRepoDetails } from '../services/searchService';
import { normalizeRepoRecord } from '../utils/repoDisplay';
import { getErrorMessage } from '../services/api';
import RepoCard from '../features/search/RepoCard';
import { SkeletonCard } from '../components/ui/Skeleton';
import EmptyState from '../components/ui/EmptyState';
import Button from '../components/ui/Button';
import './FavoritesPage.css';

export default function FavoritesPage() {
  const navigate = useNavigate();
  const [repos, setRepos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const favs = await getFavorites();
        const results = await Promise.allSettled(
          favs.map(async (fav) => {
            const details = await getRepoDetails(fav.repo_identifier);
            return normalizeRepoRecord(details, fav.repo_identifier);
          }),
        );

        if (cancelled) return;

        const loaded = results
          .map((res, i) => {
            if (res.status === 'fulfilled' && res.value) return res.value;
            const id = favs[i]?.repo_identifier;
            return id ? normalizeRepoRecord({ full_name: id, description: 'Details unavailable in index.' }, id) : null;
          })
          .filter(Boolean);

        setRepos(loaded);
      } catch (err) {
        if (!cancelled) setError(getErrorMessage(err));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => { cancelled = true; };
  }, []);

  const handleRemove = async (repoId) => {
    await removeFavorite(repoId);
    setRepos((prev) => prev.filter((r) => (r.full_name ?? r.title) !== repoId));
  };

  const openDetails = (repo) => {
    const id = repo.full_name ?? repo.title;
    if (!id?.includes('/')) return;
    const [owner, name] = id.split('/');
    navigate(`/repository/${owner}/${name}`);
  };

  return (
    <div className="favorites-page page-enter">
      <div className="page-header">
        <Heart size={20} className="page-header__icon page-header__icon--fav" />
        <div>
          <h1 className="page-header__title">Favorites</h1>
          <p className="page-header__subtitle">{repos.length} saved repositories</p>
        </div>
      </div>

      {loading && (
        <div className="favorites-page__grid">
          {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      )}

      {error && <div className="page-error">{error}</div>}

      {!loading && repos.length === 0 && (
        <EmptyState
          icon={<Heart size={32} />}
          title="No favorites yet"
          description="Save repositories from your search results or recommendations to find them quickly later."
          action={<Button variant="primary" onClick={() => navigate('/search')}>Start searching</Button>}
        />
      )}

      {!loading && repos.length > 0 && (
        <div className="favorites-page__grid">
          {repos.map((repo) => {
            const id = repo.full_name ?? repo.title;
            return (
              <div key={id} className="favorites-page__item">
                <RepoCard
                  repo={repo}
                  mode="profile"
                  isFavorite
                  onSelect={() => openDetails(repo)}
                  onExplain={(r) => navigate('/advisor', { state: { repo: r } })}
                  onRoadmap={(r) => navigate('/roadmap', { state: { repo: r } })}
                  onSimilar={(r) => navigate('/recommendations', { state: { repo: r } })}
                />
                <button
                  className="favorites-page__remove-btn"
                  onClick={() => handleRemove(id)}
                  aria-label="Remove from favorites"
                >
                  <Trash2 size={14} />
                  Remove
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
