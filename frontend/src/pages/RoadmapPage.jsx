import { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Map, Search } from 'lucide-react';
import { search } from '../services/searchService';
import { filterReposOnly } from '../utils/repoDisplay';
import { useProfile } from '../hooks/useProfile';
import RoadmapView from '../features/ai/RoadmapView';
import SearchBar from '../features/search/SearchBar';
import RepoCard from '../features/search/RepoCard';
import EmptyState from '../components/ui/EmptyState';
import { SkeletonCard } from '../components/ui/Skeleton';
import './RoadmapPage.css';

export default function RoadmapPage() {
  const location = useLocation();
  const { profile } = useProfile();

  const [selectedRepo, setSelectedRepo] = useState(location.state?.repo ?? null);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setHasSearched(true);
    try {
      const data = await search({ query: query.trim(), top_k: 8, profile });
      setResults(filterReposOnly(data?.results ?? []));
    } catch { setResults([]); }
    finally { setLoading(false); }
  };

  return (
    <div className="roadmap-page page-enter">
      <div className="page-header">
        <Map size={20} className="page-header__icon page-header__icon--roadmap" />
        <div>
          <h1 className="page-header__title">Learning Roadmaps</h1>
          <p className="page-header__subtitle">
            Generate a personalised step-by-step learning path for any open-source repository.
          </p>
        </div>
      </div>

      <div className="roadmap-page__layout">
        <div className="roadmap-page__left">
          <SearchBar
            value={query}
            onChange={setQuery}
            onSearch={handleSearch}
            loading={loading}
            placeholder="Find a repository to learn…"
          />

          {loading && (
            <div className="roadmap-page__results">
              {Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)}
            </div>
          )}

          {!loading && results.length > 0 && (
            <div className="roadmap-page__results">
              {results.map((repo) => (
                <RepoCard
                  key={repo.full_name}
                  repo={repo}
                  mode="compact"
                  selected={selectedRepo?.full_name === repo.full_name}
                  onSelect={(r) => setSelectedRepo((prev) => prev?.full_name === r.full_name ? null : r)}
                />
              ))}
            </div>
          )}

          {!hasSearched && (
            <EmptyState
              icon={<Map size={28} />}
              title="Find a repository"
              description="Search above to find a repository, then generate your personalised learning roadmap."
            />
          )}
        </div>

        <div className="roadmap-page__view">
          <div className="roadmap-page__view-card">
            <RoadmapView repo={selectedRepo} profile={profile} />
          </div>
        </div>
      </div>
    </div>
  );
}
