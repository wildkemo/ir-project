import { useCallback, useEffect, useState } from 'react';
import { ScanSearch, Zap } from 'lucide-react';
import {
  searchRepos,
  recommendRepos,
  getFilterOptions,
  getApiErrorMessage,
} from './api/client';
import SearchBar from './components/SearchBar';
import Filters from './components/Filters';
import RepoCard from './components/RepoCard';
import RecommendationPanel from './components/RecommendationPanel';
import LoadingState from './components/LoadingState';
import EmptyState from './components/EmptyState';
import './App.css';

const DEFAULT_FILTERS = {
  language: null,
  license_name: null,
  min_stars: null,
  top_k: 10,
  topic: null,
};

export default function App() {
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [filterOptions, setFilterOptions] = useState({
    languages: [],
    licenses: [],
    topics: [],
  });

  const [results, setResults] = useState([]);
  const [resultCount, setResultCount] = useState(0);
  const [hasSearched, setHasSearched] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState(null);

  const [selectedRepo, setSelectedRepo] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [recommendLoading, setRecommendLoading] = useState(false);
  const [recommendError, setRecommendError] = useState(null);

  useEffect(() => {
    getFilterOptions()
      .then(setFilterOptions)
      .catch(() => {
        /* filters still work manually if options fail */
      });
  }, []);

  const buildSearchPayload = useCallback(
    (searchQuery) => ({
      query: searchQuery.trim(),
      top_k: filters.top_k ?? 10,
      candidate_pool: 200,
      language: filters.language || null,
      license_name: filters.license_name || null,
      min_stars: filters.min_stars ?? null,
      topic: filters.topic || null,
    }),
    [filters],
  );

  const runSearch = useCallback(
    async (searchQuery) => {
      const q = (searchQuery ?? query).trim();
      if (!q) return;

      setQuery(q);
      setSearchLoading(true);
      setSearchError(null);
      setHasSearched(true);
      setSelectedRepo(null);
      setRecommendations(null);
      setRecommendError(null);

      try {
        const data = await searchRepos(buildSearchPayload(q));
        setResults(Array.isArray(data?.results) ? data.results : []);
        setResultCount(data?.count ?? 0);
      } catch (err) {
        setResults([]);
        setResultCount(0);
        setSearchError(getApiErrorMessage(err));
      } finally {
        setSearchLoading(false);
      }
    },
    [query, buildSearchPayload],
  );

  const handleExampleClick = (example) => {
    setQuery(example);
    runSearch(example);
  };

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const handleResetFilters = () => {
    setFilters(DEFAULT_FILTERS);
  };

  const handleSimilar = async (repo) => {
    const identifier = repo?.full_name || repo?.title;
    if (!identifier) return;

    setSelectedRepo(repo);
    setRecommendations(null);
    setRecommendLoading(true);
    setRecommendError(null);

    try {
      const data = await recommendRepos({
        repo_identifier: identifier,
        top_k: 6,
        same_language_only: false,
      });
      setRecommendations(data);
    } catch (err) {
      setRecommendations(null);
      setRecommendError(getApiErrorMessage(err));
    } finally {
      setRecommendLoading(false);
    }
  };

  const closeRecommendations = () => {
    setSelectedRepo(null);
    setRecommendations(null);
    setRecommendError(null);
  };

  const showPanel = selectedRepo || recommendLoading;

  return (
    <div className="app">
      <header className="hero">
        <div className="hero__brand">
          <div className="hero__logo" aria-hidden>
            <ScanSearch size={28} />
          </div>
          <div>
            <h1 className="hero__title">
              Open<span className="hero__accent">Seek</span>
            </h1>
            <p className="hero__subtitle">
              Hybrid search and recommendation engine for open-source GitHub projects
            </p>
          </div>
        </div>
        <div className="hero__badge">
          <Zap size={14} aria-hidden />
          BM25 + Semantic + Phrase + Metadata
        </div>
      </header>

      <div className="sticky-bar">
        <SearchBar
          query={query}
          onQueryChange={setQuery}
          onSubmit={() => runSearch()}
          onExampleClick={handleExampleClick}
          disabled={searchLoading}
        />
        <Filters
          filters={filters}
          filterOptions={filterOptions}
          onChange={handleFilterChange}
          onReset={handleResetFilters}
          disabled={searchLoading}
        />
      </div>

      {searchError && (
        <div className="alert alert--error" role="alert">
          {searchError}
        </div>
      )}

      <main className={`main-layout ${showPanel ? 'main-layout--with-panel' : ''}`}>
        <section className="results-section" aria-live="polite">
          {searchLoading && <LoadingState />}

          {!searchLoading && !hasSearched && <EmptyState variant="initial" />}

          {!searchLoading && hasSearched && !searchError && results.length === 0 && (
            <EmptyState variant="noResults" />
          )}

          {!searchLoading && results.length > 0 && (
            <>
              <p className="results-summary">
                Found <strong>{resultCount}</strong> repositories for &ldquo;{query}&rdquo;
              </p>
              <div className="results-grid">
                {results.map((repo) => (
                  <RepoCard
                    key={repo?.id || repo?.full_name || repo?.rank}
                    repo={repo}
                    onSimilar={handleSimilar}
                    isSelected={
                      selectedRepo?.full_name === repo?.full_name ||
                      selectedRepo?.id === repo?.id
                    }
                    recommendLoading={recommendLoading}
                  />
                ))}
              </div>
            </>
          )}
        </section>

        {showPanel && (
          <RecommendationPanel
            selectedRepo={selectedRepo}
            recommendations={recommendations}
            loading={recommendLoading}
            error={recommendError}
            onClose={closeRecommendations}
          />
        )}
      </main>

      <footer className="footer">
        <p>OpenSeek — Information Retrieval project · CS313</p>
      </footer>
    </div>
  );
}
