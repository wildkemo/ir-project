import { useEffect, useState } from 'react';
import { Clock } from 'lucide-react';
import {
  getAiHistory,
  getApiErrorMessage,
  getRecommendationHistory,
  getSearchHistory,
} from '../api/auth';

const TABS = [
  { id: 'search', label: 'Search' },
  { id: 'recommendations', label: 'Recommendations' },
  { id: 'ai', label: 'AI usage' },
];

export default function HistoryPanel() {
  const [activeTab, setActiveTab] = useState('search');
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    const loader =
      activeTab === 'search'
        ? getSearchHistory
        : activeTab === 'recommendations'
          ? getRecommendationHistory
          : getAiHistory;

    loader()
      .then(setItems)
      .catch((err) => setError(getApiErrorMessage(err)))
      .finally(() => setLoading(false));
  }, [activeTab]);

  return (
    <section className="user-panel">
      <header className="user-panel__header">
        <Clock size={22} aria-hidden />
        <div>
          <h2>History</h2>
          <p className="user-panel__meta">Search, recommendations, and AI feature usage.</p>
        </div>
      </header>

      <div className="history-tabs">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={`btn btn--sm ${activeTab === tab.id ? 'btn--primary' : 'btn--secondary'}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {error && (
        <div className="alert alert--error" role="alert">
          {error}
        </div>
      )}

      {loading && <p className="panel-note">Loading history…</p>}

      {!loading && items.length === 0 && <p className="panel-note">No history recorded yet.</p>}

      <ul className="history-list">
        {activeTab === 'search' &&
          items.map((item) => (
            <li key={item.id} className="history-list__item">
              <div>
                <strong>{item.query}</strong>
                <span className="history-list__meta">
                  {item.search_type} · {item.result_count} results ·{' '}
                  {new Date(item.created_at).toLocaleString()}
                </span>
              </div>
            </li>
          ))}

        {activeTab === 'recommendations' &&
          items.map((item) => (
            <li key={item.id} className="history-list__item">
              <div>
                <strong>{item.repo_identifier}</strong>
                <span className="history-list__meta">
                  score {item.recommendation_score ?? '—'} ·{' '}
                  {new Date(item.created_at).toLocaleString()}
                </span>
                {item.recommendation_reason && (
                  <p className="history-list__reason">{item.recommendation_reason}</p>
                )}
              </div>
            </li>
          ))}

        {activeTab === 'ai' &&
          items.map((item) => (
            <li key={item.id} className="history-list__item">
              <div>
                <strong>{item.request_type}</strong>
                <span className="history-list__meta">
                  {item.repo_identifier || '—'} · {item.model || 'rule-based'} ·{' '}
                  {item.latency_ms != null ? `${Math.round(item.latency_ms)}ms` : '—'} ·{' '}
                  {new Date(item.created_at).toLocaleString()}
                </span>
              </div>
            </li>
          ))}
      </ul>
    </section>
  );
}
