import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Cpu, Search } from 'lucide-react';
import { search } from '../services/searchService';
import { filterReposOnly } from '../utils/repoDisplay';
import { useProfile } from '../hooks/useProfile';
import AIAdvisorPanel from '../features/ai/AIAdvisorPanel';
import SearchBar from '../features/search/SearchBar';
import RepoCard from '../features/search/RepoCard';
import EmptyState from '../components/ui/EmptyState';
import { SkeletonCard } from '../components/ui/Skeleton';
import './AdvisorPage.css';

export default function AdvisorPage() {
  const location = useLocation();
  const navigate = useNavigate();
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
    <div className="advisor-page page-enter">
      <div className="page-header">
        <Cpu size={20} className="page-header__icon page-header__icon--ai" />
        <div>
          <h1 className="page-header__title">AI Advisor</h1>
          <p className="page-header__subtitle">
            Ask AI-powered questions about any repository — not a chatbot, a repository intelligence system.
          </p>
        </div>
      </div>

      <div className="advisor-page__layout">
        <div className="advisor-page__left">
          <div className="advisor-page__search">
            <SearchBar
              value={query}
              onChange={setQuery}
              onSearch={handleSearch}
              loading={loading}
              placeholder="Search for a repository to advise on…"
            />
          </div>

          {loading && (
            <div className="advisor-page__results">
              {Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)}
            </div>
          )}

          {!loading && hasSearched && results.length === 0 && (
            <EmptyState icon={<Search size={24} />} title="No results" description="Try a different query." />
          )}

          {!loading && results.length > 0 && (
            <div className="advisor-page__results">
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

          {!hasSearched && !selectedRepo && (
            <EmptyState
              icon={<Cpu size={32} />}
              title="Search for a repository"
              description="Find a repository above to get AI-powered explanations, comparisons, and roadmaps."
            />
          )}
        </div>

        <div className="advisor-page__panel">
          <AIAdvisorPanel repo={selectedRepo} profile={profile} />
        </div>
      </div>
    </div>
  );
}
