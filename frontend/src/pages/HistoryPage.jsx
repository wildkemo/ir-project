import { useEffect, useState } from 'react';
import { Clock, Search, Cpu, Sparkles, ChevronDown, ChevronUp, Map, MessageSquare } from 'lucide-react';
import { getSearchHistory, getRecommendationHistory, getAIHistory } from '../services/userService';
import { getErrorMessage } from '../services/api';
import { SkeletonText } from '../components/ui/Skeleton';
import EmptyState from '../components/ui/EmptyState';
import Badge from '../components/ui/Badge';
import { timeAgo, formatScore } from '../utils/format';
import { aiTypeLabel } from '../utils/aiHistory';
import './HistoryPage.css';

const TABS = [
  { id: 'search',          label: 'Search',          icon: Search },
  { id: 'recommendations', label: 'Recommendations', icon: Sparkles },
  { id: 'ai',              label: 'AI Chats',        icon: Cpu },
];

function formatResponseText(text) {
  if (!text) return null;
  return text.split('\n').map((line, i) => {
    if (!line.trim()) return null;
    const html = line.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    return (
      <p
        key={i}
        className={/^\d+[\.\)]/.test(line.trim()) ? 'ai-history-item__step' : undefined}
        dangerouslySetInnerHTML={{ __html: html }}
      />
    );
  });
}

export default function HistoryPage() {
  const [tab, setTab] = useState('ai');
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
          <p className="page-header__subtitle">Your searches, recommendations, and full AI conversations</p>
        </div>
      </div>

      <div className="history-page__tabs">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            type="button"
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
          description="Chat with the AI Advisor or generate roadmaps — your conversations will appear here when you're signed in."
        />
      )}

      {!loading && current.length > 0 && (
        <div className="history-list">
          {tab === 'search' && current.map((item) => (
            <SearchHistoryItem key={item.id} item={item} />
          ))}
          {tab === 'recommendations' && current.map((item) => (
            <RecommendHistoryItem key={item.id} item={item} />
          ))}
          {tab === 'ai' && current.map((item) => (
            <AIHistoryItem key={item.id} item={item} />
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
  const [expanded, setExpanded] = useState(false);
  const isRoadmap = item.request_type === 'learning_roadmap';
  const TypeIcon = isRoadmap ? Map : MessageSquare;
  const hasContent = item.user_message || item.ai_response;

  return (
    <div className={`ai-history-item ${expanded ? 'ai-history-item--expanded' : ''}`}>
      <button
        type="button"
        className="ai-history-item__header"
        onClick={() => hasContent && setExpanded((v) => !v)}
        aria-expanded={expanded}
      >
        <TypeIcon size={14} className="ai-history-item__icon" />
        <div className="ai-history-item__summary">
          <div className="ai-history-item__title-row">
            <span className="ai-history-item__type">{aiTypeLabel(item.request_type)}</span>
            {item.repo_identifier && (
              <span className="ai-history-item__repo">{item.repo_identifier}</span>
            )}
          </div>
          {item.user_message && (
            <p className="ai-history-item__preview">
              {item.user_message.length > 140
                ? `${item.user_message.slice(0, 140)}…`
                : item.user_message}
            </p>
          )}
          {!item.user_message && item.ai_response && (
            <p className="ai-history-item__preview ai-history-item__preview--muted">
              {item.ai_response.slice(0, 140)}{item.ai_response.length > 140 ? '…' : ''}
            </p>
          )}
          <div className="ai-history-item__meta">
            {item.response_mode && <Badge variant="default" size="sm">{item.response_mode}</Badge>}
            {item.model && <Badge variant="ai" size="sm">{item.model}</Badge>}
            {item.latency_ms != null && <span>{Math.round(item.latency_ms)}ms</span>}
          </div>
        </div>
        <div className="ai-history-item__aside">
          {item.created_at && <span className="ai-history-item__time">{timeAgo(item.created_at)}</span>}
          {hasContent && (
            expanded
              ? <ChevronUp size={16} className="ai-history-item__chevron" />
              : <ChevronDown size={16} className="ai-history-item__chevron" />
          )}
        </div>
      </button>

      {expanded && hasContent && (
        <div className="ai-history-item__body">
          {item.user_message && (
            <div className="ai-history-item__block ai-history-item__block--user">
              <span className="ai-history-item__label">Your question</span>
              <div className="ai-history-item__text">{item.user_message}</div>
            </div>
          )}
          {item.ai_response && (
            <div className="ai-history-item__block ai-history-item__block--ai">
              <span className="ai-history-item__label">AI response</span>
              <div className="ai-history-item__text">
                {formatResponseText(item.ai_response)}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
