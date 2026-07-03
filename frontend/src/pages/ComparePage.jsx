import { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { GitCompare, Search } from 'lucide-react';
import { useRepoStore } from '../stores/repoStore';
import { search } from '../services/searchService';
import { filterReposOnly } from '../utils/repoDisplay';
import { useProfile } from '../hooks/useProfile';
import ComparePanel from '../features/ai/ComparePanel';
import SearchBar from '../features/search/SearchBar';
import RepoCard from '../features/search/RepoCard';
import EmptyState from '../components/ui/EmptyState';
import { SkeletonCard } from '../components/ui/Skeleton';
import './ComparePage.css';

export default function ComparePage() {
  const location = useLocation();
  const { compareRepos, addToCompare, removeFromCompare } = useRepoStore();
  const { profile } = useProfile();

  const repoA = compareRepos[0] ?? null;
  const repoB = compareRepos[1] ?? null;

  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setHasSearched(true);
    try {
      const data = await search({ query: query.trim(), top_k: 10, profile });
      setResults(filterReposOnly(data?.results ?? []));
    } catch { setResults([]); }
    finally { setLoading(false); }
  };

  return (
    <div className="compare-page page-enter">
      <div className="page-header">
        <GitCompare size={20} className="page-header__icon page-header__icon--compare" />
        <div>
          <h1 className="page-header__title">Compare Repositories</h1>
          <p className="page-header__subtitle">
            Side-by-side AI comparison of technologies, community, difficulty, and use cases.
          </p>
        </div>
      </div>

      <div className="compare-page__layout">
        <div className="compare-page__panel">
          <ComparePanel
            repoA={repoA}
            repoB={repoB}
            onRemoveRepo={removeFromCompare}
            onAddRepo={() => {}}
            profile={profile}
          />
        </div>

        <div className="compare-page__search">
          <p className="compare-page__search-hint">
            Search repositories below and click a card to add it to the comparison (max 2).
          </p>
          <SearchBar
            value={query}
            onChange={setQuery}
            onSearch={handleSearch}
            loading={loading}
            placeholder="Search repositories to compare…"
          />

          {loading && (
            <div className="compare-page__results">
              {Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)}
            </div>
          )}

          {!loading && hasSearched && results.length === 0 && (
            <EmptyState icon={<Search size={24} />} title="No results" description="Try a different query." />
          )}

          {!loading && results.length > 0 && (
            <div className="compare-page__results">
              {results.map((repo) => (
                <RepoCard
                  key={repo.full_name}
                  repo={repo}
                  mode="compact"
                  selected={compareRepos.some((r) => r.full_name === repo.full_name)}
                  onSelect={addToCompare}
                />
              ))}
            </div>
          )}

          {!hasSearched && (
            <EmptyState
              icon={<GitCompare size={28} />}
              title="Search to find repositories"
              description="Select up to 2 repositories to compare them side by side."
            />
          )}
        </div>
      </div>
    </div>
  );
}
