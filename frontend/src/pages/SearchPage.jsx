import { useEffect, useState, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Search as SearchIcon, SlidersHorizontal } from 'lucide-react';
import { useSearchStore } from '../stores/searchStore';
import { useRepoStore } from '../stores/repoStore';
import { search, getFilterOptions } from '../services/searchService';
import { addFavorite, removeFavorite, getFavorites } from '../services/userService';
import { useProfile } from '../hooks/useProfile';
import { filterReposOnly } from '../utils/repoDisplay';
import { getErrorMessage } from '../services/api';
import { useAuthStore } from '../stores/authStore';
import { loadAccessToken } from '../utils/authStorage';
import SearchBar from '../features/search/SearchBar';
import SearchFilters from '../features/search/SearchFilters';
import RepoCard from '../features/search/RepoCard';
import AIAdvisorPanel from '../features/ai/AIAdvisorPanel';
import { SkeletonCard } from '../components/ui/Skeleton';
import EmptyState from '../components/ui/EmptyState';
import './SearchPage.css';

export default function SearchPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const isAuthenticated = Boolean(user && loadAccessToken());

  const {
    query, filters, filterOptions,
    results, resultCount, hasSearched, loading, error, searchEngine,
    setQuery, setFilterOptions, setResults, setLoading, setError, clearResults,
  } = useSearchStore();

  const { addToCompare } = useRepoStore();

  const [showFilters, setShowFilters] = useState(false);
  const [selectedRepo, setSelectedRepo] = useState(null);
  const [favorites, setFavorites] = useState(new Set());

  const { profile } = useProfile();

  // Restore query from navigation state
  useEffect(() => {
    if (location.state?.query && location.state.query !== query) {
      setQuery(location.state.query);
    }
  }, []);

  // Load filter options + favorites
  useEffect(() => {
    getFilterOptions().then(setFilterOptions).catch(() => {});
    if (isAuthenticated) {
      getFavorites()
        .then((favs) => setFavorites(new Set(favs.map((f) => f.repo_identifier))))
        .catch(() => {});
    }
  }, [isAuthenticated]);

  const handleSearch = useCallback(async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      // Backend SearchRequest expects filter fields at the TOP LEVEL (not nested under "filters")
      const payload = {
        query:        query.trim(),
        top_k:        filters.top_k ?? 10,
        candidate_pool: 100,
        language:     filters.language     || undefined,
        license_name: filters.license_name || undefined,
        min_stars:    filters.min_stars    || undefined,
        topic:        filters.topic        || undefined,
        profile:      profile ?? undefined,
      };
      const data = await search(payload);
      setResults({
        results: filterReposOnly(data?.results ?? []),
        count: data?.count ?? 0,
        engine: data?.engine,
      });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [query, filters, profile]);

  const toggleFavorite = async (repo) => {
    const id = repo.full_name ?? repo.title;
    if (favorites.has(id)) {
      await removeFavorite(id);
      setFavorites((prev) => { const s = new Set(prev); s.delete(id); return s; });
    } else {
      await addFavorite(id);
      setFavorites((prev) => new Set(prev).add(id));
    }
  };

  return (
    <div className="search-page page-enter">
      {/* Search bar */}
      <div className="search-page__bar-wrap">
        <SearchBar
          value={query}
          onChange={setQuery}
          onSearch={handleSearch}
          loading={loading}
          showFilters={showFilters}
          onToggleFilters={() => setShowFilters((v) => !v)}
          engine={searchEngine}
        />
        {showFilters && <SearchFilters filterOptions={filterOptions} />}
      </div>

      <div className={`search-page__body ${selectedRepo ? 'search-page__body--split' : ''}`}>
        {/* Results */}
        <div className="search-page__results">
          {!hasSearched && !loading && (
            <EmptyState
              icon={<SearchIcon size={32} />}
              title="Search for repositories"
              description="Enter a query above to discover open-source projects. Try 'FastAPI authentication', 'React state management', or 'machine learning NLP'."
            />
          )}

          {loading && (
            <div className="search-page__grid">
              {Array.from({ length: filters.top_k ?? 10 }).map((_, i) => (
                <SkeletonCard key={i} />
              ))}
            </div>
          )}

          {!loading && error && (
            <div className="search-page__error">
              <p>{error}</p>
            </div>
          )}

          {!loading && hasSearched && !error && (
            <>
              <div className="search-page__results-header">
                <span className="search-page__count">
                  {resultCount} result{resultCount !== 1 ? 's' : ''} for
                  <strong> "{query}"</strong>
                </span>
                {searchEngine && (
                  <span className="search-page__engine-label">
                    Engine: {searchEngine}
                  </span>
                )}
              </div>

              {results.length === 0 ? (
                <EmptyState
                  icon={<SearchIcon size={28} />}
                  title="No results found"
                  description="Try different keywords, remove filters, or broaden your search."
                />
              ) : (
                <div className="search-page__grid">
                  {results.map((repo) => (
                    <RepoCard
                      key={repo.full_name ?? repo.title}
                      repo={repo}
                      mode="search"
                      selected={selectedRepo?.full_name === repo.full_name}
                      isFavorite={favorites.has(repo.full_name ?? repo.title)}
                      onFavoriteToggle={isAuthenticated ? toggleFavorite : undefined}
                      onSelect={(r) => {
                        const id = r.full_name ?? r.title;
                        if (id?.includes('/')) {
                          const [owner, name] = id.split('/');
                          navigate(`/repository/${owner}/${name}`);
                        } else {
                          setSelectedRepo((prev) => prev?.full_name === r.full_name ? null : r);
                        }
                      }}
                      onExplain={(r) => navigate('/advisor', { state: { repo: r } })}
                      onRoadmap={(r) => navigate('/roadmap', { state: { repo: r } })}
                      onCompare={addToCompare}
                      onSimilar={(r) => navigate('/recommendations', { state: { repo: r } })}
                    />
                  ))}
                </div>
              )}
            </>
          )}
        </div>

        {/* AI panel (shown when a repo is selected) */}
        {selectedRepo && (
          <div className="search-page__ai-panel animate-slide-in-right">
            <AIAdvisorPanel repo={selectedRepo} profile={profile} />
          </div>
        )}
      </div>
    </div>
  );
}
