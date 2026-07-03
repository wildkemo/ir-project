import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Search, Sparkles, Star, Clock, Cpu, TrendingUp, ArrowRight, AlertTriangle,
} from 'lucide-react';
import { useAuthStore } from '../stores/authStore';
import { recommendFromProfile } from '../services/searchService';
import { getFavorites, getSearchHistory, getAIHistory } from '../services/userService';
import { useProfile } from '../hooks/useProfile';
import { filterReposOnly } from '../utils/repoDisplay';
import RepoCard from '../features/search/RepoCard';
import { SkeletonCard } from '../components/ui/Skeleton';
import Button from '../components/ui/Button';
import EmptyState from '../components/ui/EmptyState';
import './DashboardPage.css';

function SectionHeader({ title, icon: Icon, color, to }) {
  return (
    <div className="dashboard-section__header">
      <div className={`dashboard-section__header-left dashboard-section__header-left--${color}`}>
        <Icon size={16} />
        <h2 className="dashboard-section__title">{title}</h2>
      </div>
      {to && (
        <Link to={to} className="dashboard-section__see-all">
          See all <ArrowRight size={13} />
        </Link>
      )}
    </div>
  );
}

export default function DashboardPage() {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const { profile } = useProfile();

  const [recommendations, setRecommendations] = useState([]);
  const [recLoading, setRecLoading] = useState(false);

  const [favorites, setFavorites] = useState([]);
  const [searchHistory, setSearchHistory] = useState([]);
  const [aiHistory, setAIHistory] = useState([]);
  const [histLoading, setHistLoading] = useState(false);

  useEffect(() => {
    if (profile) {
      setRecLoading(true);
      recommendFromProfile({ ...profile, top_k: 6 })
        .then((data) => setRecommendations(filterReposOnly(data?.results)))
        .catch(() => {})
        .finally(() => setRecLoading(false));
    }

    setHistLoading(true);
    Promise.allSettled([getFavorites(), getSearchHistory(), getAIHistory()])
      .then(([favRes, searchRes, aiRes]) => {
        setFavorites(favRes.status === 'fulfilled' ? (favRes.value ?? []) : []);
        setSearchHistory(searchRes.status === 'fulfilled' ? (searchRes.value ?? []) : []);
        setAIHistory(aiRes.status === 'fulfilled' ? (aiRes.value ?? []) : []);
      })
      .finally(() => setHistLoading(false));
  }, [profile]);

  const greeting = () => {
    const h = new Date().getHours();
    if (h < 12) return 'Good morning';
    if (h < 17) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <div className="dashboard page-enter">
      {/* Hero greeting */}
      <div className="dashboard__hero">
        <div>
          <h1 className="dashboard__greeting">
            {greeting()}, {user?.username ?? 'developer'} 👋
          </h1>
          <p className="dashboard__subline">
            {profile
              ? `Showing personalised recommendations for ${profile.level ?? ''} ${profile.project_type ?? 'all'} developers.`
              : 'Complete your profile to get personalised recommendations.'}
          </p>
        </div>
        <div className="dashboard__hero-actions">
          <Button
            variant="primary"
            icon={<Search size={15} />}
            onClick={() => navigate('/search')}
          >
            Start searching
          </Button>
          {!profile && (
            <Button
              variant="secondary"
              icon={<Sparkles size={15} />}
              onClick={() => navigate('/onboarding')}
            >
              Set up profile
            </Button>
          )}
        </div>
      </div>

      {/* Quick stats */}
      <div className="dashboard__quick-stats">
        <QuickStat icon={Star} color="fav" value={favorites.length} label="Favorites" to="/favorites" />
        <QuickStat icon={Clock} color="search" value={searchHistory.length} label="Searches" to="/history" />
        <QuickStat icon={Cpu} color="ai" value={aiHistory.length} label="AI queries" to="/history" />
        <QuickStat
          icon={Sparkles}
          color="rec"
          value={recommendations.length}
          label="Recommendations"
          to="/recommendations"
        />
      </div>

      {/* Profile warning */}
      {!profile && (
        <div className="dashboard__profile-banner">
          <AlertTriangle size={18} className="dashboard__profile-banner-icon" />
          <div>
            <p className="dashboard__profile-banner-title">Complete your developer profile</p>
            <p className="dashboard__profile-banner-desc">
              Answer 5 quick questions to unlock personalised recommendations.
            </p>
          </div>
          <Button variant="roadmap" size="sm" onClick={() => navigate('/onboarding')}>
            Set up now
          </Button>
        </div>
      )}

      {/* Recommendations */}
      <section className="dashboard-section">
        <SectionHeader title="Personalised Recommendations" icon={Sparkles} color="rec" to="/recommendations" />
        {recLoading ? (
          <div className="dashboard-section__grid">
            {Array.from({ length: 3 }).map((_, i) => <SkeletonCard key={i} />)}
          </div>
        ) : recommendations.length > 0 ? (
          <div className="dashboard-section__grid">
            {recommendations.slice(0, 3).map((repo) => (
              <RepoCard
                key={repo.full_name ?? repo.title}
                repo={repo}
                mode="profile"
                onSelect={() => navigate('/search', { state: { selectedRepo: repo } })}
                onRoadmap={() => navigate('/roadmap', { state: { repo } })}
                onExplain={() => navigate('/advisor', { state: { repo } })}
              />
            ))}
          </div>
        ) : (
          <EmptyState
            icon={<Sparkles size={28} />}
            title={profile ? 'No recommendations yet' : 'Profile not set up'}
            description={profile
              ? 'Try adjusting your profile preferences.'
              : 'Complete your developer profile to get personalised recommendations.'
            }
            action={
              !profile
                ? <Button variant="primary" size="sm" onClick={() => navigate('/onboarding')}>Set up profile</Button>
                : null
            }
          />
        )}
      </section>

      {/* Recent searches */}
      {searchHistory.length > 0 && (
        <section className="dashboard-section">
          <SectionHeader title="Recent Searches" icon={Clock} color="search" to="/history" />
          <div className="dashboard__search-history">
            {searchHistory.slice(0, 6).map((h, i) => (
              <button
                key={i}
                className="dashboard__history-pill"
                onClick={() => navigate('/search', { state: { query: h.query } })}
              >
                <Search size={12} />
                {h.query}
              </button>
            ))}
          </div>
        </section>
      )}

      {/* AI activity */}
      {aiHistory.length > 0 && (
        <section className="dashboard-section">
          <SectionHeader title="AI Activity" icon={Cpu} color="ai" to="/history" />
          <div className="dashboard__ai-history">
            {aiHistory.slice(0, 5).map((h, i) => (
              <div key={i} className="dashboard__ai-entry">
                <Cpu size={13} className="dashboard__ai-entry-icon" />
                <span className="dashboard__ai-entry-type">{h.request_type}</span>
                <span className="dashboard__ai-entry-repo">{h.repo_identifier}</span>
                {h.latency_ms != null && <span className="dashboard__ai-entry-lat">{Math.round(h.latency_ms)}ms</span>}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Trending CTA */}
      <section className="dashboard-section">
        <div className="dashboard__trending-cta">
          <TrendingUp size={20} />
          <div>
            <h3>Discover trending repositories</h3>
            <p>Use hybrid search to find what's popular in your stack right now.</p>
          </div>
          <Button variant="primary" size="sm" onClick={() => navigate('/search')}>
            Explore <ArrowRight size={13} />
          </Button>
        </div>
      </section>
    </div>
  );
}

function QuickStat({ icon: Icon, color, value, label, to }) {
  const navigate = useNavigate();
  return (
    <button className={`quick-stat quick-stat--${color}`} onClick={() => navigate(to)}>
      <Icon size={18} className="quick-stat__icon" />
      <span className="quick-stat__value">{value}</span>
      <span className="quick-stat__label">{label}</span>
    </button>
  );
}
