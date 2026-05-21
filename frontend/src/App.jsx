import { useCallback, useEffect, useRef, useState } from 'react';
import { ScanSearch, Zap, Sparkles, Layers, RotateCcw } from 'lucide-react';
import {
  searchRepos,
  recommendRepos,
  getFilterOptions,
  checkHealth,
  recommendFromProfile,
  getApiErrorMessage,
  API_BASE_URL,
} from './api/client';
import { useTheme } from './hooks/useTheme';
import { loadStoredProfile, saveStoredProfile, clearStoredProfile } from './utils/profileStorage';
import { filterReposOnly, getRepoDisplayName } from './utils/repoDisplay';
import SearchBar from './components/SearchBar';
import Filters from './components/Filters';
import RepoCard from './components/RepoCard';
import ProfileRepoCard from './components/ProfileRepoCard';
import ProfileWizard from './components/ProfileWizard';
import RecommendationPanel from './components/RecommendationPanel';
import LoadingState from './components/LoadingState';
import EmptyState from './components/EmptyState';
import ThemeToggle from './components/ThemeToggle';
import './App.css';

const DEFAULT_FILTERS = {
  language: null,
  license_name: null,
  min_stars: null,
  top_k: 10,
  topic: null,
};

const PROFILE_TOP_K = 10;

export default function App() {
  const { theme, toggleTheme } = useTheme();
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [filterOptions, setFilterOptions] = useState({
    languages: [],
    licenses: [],
    topics: [],
  });

  const [profileAnswers, setProfileAnswers] = useState(() => loadStoredProfile());
  const [profileComplete, setProfileComplete] = useState(false);
  const [showProfileWizard, setShowProfileWizard] = useState(() => !loadStoredProfile());
  const [profileResults, setProfileResults] = useState([]);
  const [profileLoading, setProfileLoading] = useState(false);
  const [profileError, setProfileError] = useState(null);

  const [results, setResults] = useState([]);
  const [resultCount, setResultCount] = useState(0);
  const [hasSearched, setHasSearched] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState(null);

  const [selectedRepo, setSelectedRepo] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [recommendLoading, setRecommendLoading] = useState(false);
  const [recommendError, setRecommendError] = useState(null);
  const [apiOnline, setApiOnline] = useState(null);
  const didRestoreProfile = useRef(false);

  const runProfileRecommend = useCallback(async (answers) => {
    setProfileLoading(true);
    setProfileError(null);

    try {
      const data = await recommendFromProfile({ ...answers, top_k: PROFILE_TOP_K });
        setProfileResults(filterReposOnly(data?.results));
      setProfileAnswers(answers);
      setProfileComplete(true);
      setShowProfileWizard(false);
      saveStoredProfile(answers);
    } catch (err) {
      setProfileResults([]);
      setProfileError(getApiErrorMessage(err));
    } finally {
      setProfileLoading(false);
    }
  }, []);

  useEffect(() => {
    checkHealth()
      .then(() => setApiOnline(true))
      .catch(() => setApiOnline(false));

    getFilterOptions()
      .then(setFilterOptions)
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (didRestoreProfile.current) return;
    const stored = loadStoredProfile();
    if (!stored) return;
    didRestoreProfile.current = true;
    queueMicrotask(() => {
      runProfileRecommend(stored);
    });
  }, [runProfileRecommend]);

  const buildSearchPayload = useCallback(
    (searchQuery) => {
      const payload = {
        query: searchQuery.trim(),
        top_k: filters.top_k ?? 10,
        candidate_pool: 200,
        language: filters.language || null,
        license_name: filters.license_name || null,
        min_stars: filters.min_stars ?? null,
        topic: filters.topic || null,
      };

      if (profileAnswers) {
        payload.profile = {
          project_type: profileAnswers.project_type ?? null,
          language: profileAnswers.language ?? null,
          goal: profileAnswers.goal ?? null,
          level: profileAnswers.level ?? null,
          repo_kind: profileAnswers.repo_kind ?? null,
          complexity: profileAnswers.complexity ?? null,
        };
      }

      return payload;
    },
    [filters, profileAnswers],
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
        const repos = filterReposOnly(data?.results);
        setResults(repos);
        setResultCount(repos.length);
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

  const handleProfileSubmit = (answers) => {
    runProfileRecommend(answers);
  };

  const handleRetakeProfile = () => {
    clearStoredProfile();
    setProfileComplete(false);
    setShowProfileWizard(true);
    setProfileResults([]);
    setProfileError(null);
    setProfileAnswers(null);
  };

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

  const handleApplyFilters = () => {
    if (hasSearched && query.trim()) {
      runSearch(query);
    }
  };

  const handleSimilar = async (repo) => {
    const identifier = getRepoDisplayName(repo);
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
      <div className="top-bar">
        <div className="top-bar__brand-mini">
          <ScanSearch size={18} aria-hidden />
          Repo<span>Mind</span>
        </div>
        <div className="top-bar__actions">
          {apiOnline === true && (
            <span className="status-pill status-pill--online" title="API connected">
              <span className="status-pill__dot" aria-hidden />
              Live
            </span>
          )}
          {apiOnline === false && (
            <span className="status-pill status-pill--offline" title="API offline">
              <span className="status-pill__dot" aria-hidden />
              Offline
            </span>
          )}
          <ThemeToggle theme={theme} onToggle={toggleTheme} />
        </div>
      </div>

      <header className="hero">
        <div className="hero__brand">
          <div className="hero__logo" aria-hidden>
            <ScanSearch size={32} />
          </div>
          <div>
            <h1 className="hero__title">
              Repo<span className="hero__accent">Mind</span>
            </h1>
            <p className="hero__subtitle">
              Get personalized repo picks, then search the full hybrid engine anytime.
            </p>
          </div>
        </div>
        <div className="hero__badges">
          <span className="hero__badge">
            <Zap size={14} aria-hidden />
            Profile recommendations
          </span>
          <span className="hero__badge hero__badge--muted">
            <Sparkles size={14} aria-hidden />
            Hybrid BM25 + semantic search
          </span>
          <span className="hero__badge hero__badge--muted">
            <Layers size={14} aria-hidden />
            Similar repos
          </span>
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
      </div>

      <div className="filters-bar">
        <Filters
          filters={filters}
          filterOptions={filterOptions}
          onChange={handleFilterChange}
          onReset={handleResetFilters}
          onApply={handleApplyFilters}
          showApply={hasSearched}
          disabled={searchLoading}
        />
      </div>

      {apiOnline === false && (
        <div className="alert alert--error" role="alert">
          Backend is not reachable at {API_BASE_URL}. Run:{' '}
          <code>uvicorn backend.main:app --reload --port 8000</code>
        </div>
      )}

      {profileError && (
        <div className="alert alert--error" role="alert">
          {profileError}
        </div>
      )}

      {searchError && (
        <div className="alert alert--error" role="alert">
          {searchError}
        </div>
      )}

      <main className={`main-layout ${showPanel ? 'main-layout--with-panel' : ''}`}>
        <section className="results-section" aria-live="polite">
          {showProfileWizard && !profileComplete && (
            <ProfileWizard
              initialAnswers={profileAnswers}
              onSubmit={handleProfileSubmit}
              loading={profileLoading}
              disabled={profileLoading}
            />
          )}

          {profileLoading && profileComplete && !hasSearched && (
            <LoadingState message="Refreshing your recommendations…" />
          )}

          {profileComplete && profileResults.length > 0 && !hasSearched && (
            <section className="profile-results" aria-labelledby="profile-results-title">
              <header className="profile-results__header">
                <div>
                  <h2 id="profile-results-title">
                    Your top {profileResults.length} recommendation
                    {profileResults.length === 1 ? '' : 's'}
                  </h2>
                  <p className="profile-results__subtitle">
                    Up to {PROFILE_TOP_K} repos ranked by your profile — project type, language,
                    goals, and more.
                  </p>
                </div>
                <button
                  type="button"
                  className="btn btn--ghost btn--sm"
                  onClick={handleRetakeProfile}
                >
                  <RotateCcw size={14} aria-hidden />
                  Retake quiz
                </button>
              </header>
              <div className="results-grid">
                {profileResults.map((repo) => (
                  <ProfileRepoCard
                    key={`profile-${repo?.doc_id ?? repo?.rank}-${repo?.url}`}
                    repo={repo}
                    onSimilar={handleSimilar}
                    isSelected={
                      selectedRepo?.full_name === repo?.full_name ||
                      selectedRepo?.url === repo?.url
                    }
                    recommendLoading={recommendLoading}
                  />
                ))}
              </div>
            </section>
          )}

          {profileComplete &&
            !showProfileWizard &&
            profileResults.length === 0 &&
            !profileLoading &&
            !hasSearched && (
            <EmptyState
              variant="noResults"
              message="No profile matches found. Try retaking the quiz with different preferences."
            />
          )}

          {hasSearched && (
            <section className="search-results" aria-labelledby="search-results-title">
              <h2 id="search-results-title" className="section-divider__title">
                Search results
              </h2>
              {searchLoading && <LoadingState />}

              {!searchLoading && !searchError && results.length === 0 && (
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
                        searchQuery={query}
                        searchProfile={profileAnswers}
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
          )}

          {!profileComplete && !showProfileWizard && !hasSearched && !profileLoading && (
            <EmptyState variant="initial" />
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
        <p>
          <strong>OpenSeek</strong> — Information Retrieval · CS313
        </p>
      </footer>
    </div>
  );
}
