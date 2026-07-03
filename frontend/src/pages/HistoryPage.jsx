import { useEffect, useState } from 'react';
import { Clock, Search, Cpu, Sparkles } from 'lucide-react';
import { getSearchHistory, getRecommendationHistory, getAIHistory } from '../services/userService';
import { getErrorMessage } from '../services/api';
import { SkeletonText } from '../components/ui/Skeleton';
import EmptyState from '../components/ui/EmptyState';
import { timeAgo, formatScore } from '../utils/format';
import './HistoryPage.css';

const TABS = [
  { id: 'search',         label: 'Search',         icon: Search },
  { id: 'recommendations',label: 'Recommendations', icon: Sparkles },
  { id: 'ai',             label: 'AI Activity',     icon: Cpu },
];

export default function HistoryPage() {
  const [tab, setTab] = useState('search');
  const [data, setData] = useState({ search: [], recommendations: [], ai: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    Promise.allSettled([
      getSearchHistory(),
      getRecommendationHistory(),
      getAIHistory(),
    ]).then(([searchRes, recRes, aiRes]) => {
      setData({
        search:          searchRes.status === 'fulfilled' ? (searchRes.value ?? []) : [],
        recommendations: recRes.status   === 'fulfilled' ? (recRes.value   ?? []) : [],
        ai:              aiRes.status    === 'fulfilled' ? (aiRes.value    ?? []) : [],
      });
    }).catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  const current = data[tab] ?? [];

  return (
    <div className="history-page page-enter">
      <div className="page-header">
        <Clock size={20} className="page-header__icon page-header__icon--search" />
        <div>
          <h1 className="page-header__title">History</h1>
          <p className="page-header__subtitle">Your activity log across all features</p>
        </div>
      </div>

      <div className="history-page__tabs">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            className={`history-tab ${tab === id ? 'history-tab--active' : ''}`}
            onClick={() => setTab(id)}
          >
            <Icon size={15} />
            {label}
            <span className="history-tab__count">{data[id]?.length ?? 0}</span>
          </button>
        ))}
      </div>

      {loading && <SkeletonText lines={6} />}
      {error && <div className="page-error">{error}</div>}

      {!loading && current.length === 0 && (
        <EmptyState
          icon={<Clock size={28} />}
          title="No history yet"
          description="Your activity will appear here as you use RepoMind AI."
        />
      )}

      {!loading && current.length > 0 && (
        <div className="history-list">
          {tab === 'search' && current.map((item, i) => (
            <SearchHistoryItem key={i} item={item} />
          ))}
          {tab === 'recommendations' && current.map((item, i) => (
            <RecommendHistoryItem key={i} item={item} />
          ))}
          {tab === 'ai' && current.map((item, i) => (
            <AIHistoryItem key={i} item={item} />
          ))}
        </div>
      )}
    </div>
  );
}

function SearchHistoryItem({ item }) {
  return (
    <div className="history-item">
      <Search size={14} className="history-item__icon" />
      <div className="history-item__content">
        <span className="history-item__primary">{item.query}</span>
        <div className="history-item__meta">
          <span>{item.search_type ?? 'hybrid'}</span>
          <span>·</span>
          <span>{item.result_count ?? 0} results</span>
        </div>
      </div>
      {item.created_at && <span className="history-item__time">{timeAgo(item.created_at)}</span>}
    </div>
  );
}

function RecommendHistoryItem({ item }) {
  return (
    <div className="history-item">
      <Sparkles size={14} className="history-item__icon history-item__icon--rec" />
      <div className="history-item__content">
        <span className="history-item__primary">{item.repo_identifier}</span>
        <div className="history-item__meta">
          {item.recommendation_score != null && <span>Score: {formatScore(item.recommendation_score)}</span>}
          {item.recommendation_reason && <span>· {item.recommendation_reason}</span>}
        </div>
      </div>
      {item.created_at && <span className="history-item__time">{timeAgo(item.created_at)}</span>}
    </div>
  );
}

function AIHistoryItem({ item }) {
  return (
    <div className="history-item">
      <Cpu size={14} className="history-item__icon history-item__icon--ai" />
      <div className="history-item__content">
        <span className="history-item__primary">{item.request_type}</span>
        <div className="history-item__meta">
          <span>{item.repo_identifier}</span>
          {item.model && <><span>·</span><span>{item.model}</span></>}
          {item.latency_ms != null && <><span>·</span><span>{Math.round(item.latency_ms)}ms</span></>}
        </div>
      </div>
      {item.created_at && <span className="history-item__time">{timeAgo(item.created_at)}</span>}
    </div>
  );
}
