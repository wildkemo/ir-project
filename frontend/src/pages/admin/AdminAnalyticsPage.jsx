import { useEffect, useState } from 'react';
import { BarChart2, TrendingUp, Search, Sparkles, Cpu } from 'lucide-react';
import { getAdminAnalytics } from '../../services/adminService';
import { getErrorMessage } from '../../services/api';
import { SkeletonText } from '../../components/ui/Skeleton';
import './AdminPage.css';

export default function AdminAnalyticsPage() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getAdminAnalytics()
      .then(setAnalytics)
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="admin-page page-enter">
      <div className="admin-page__header">
        <h1 className="admin-page__title">Analytics</h1>
        <p className="admin-page__subtitle">Search behaviour, recommendation quality, and usage trends.</p>
      </div>

      {loading && <SkeletonText lines={6} />}
      {error && <div className="admin-page__notice">{error}</div>}

      {!loading && !error && analytics && (
        <div className="admin-page__grid">
          <div className="admin-card">
            <h3 className="admin-card__title"><Search size={15} /> Top Search Queries</h3>
            {analytics.top_search_queries?.length ? (
              <ul className="admin-analytics-list">
                {analytics.top_search_queries.map((item) => (
                  <li key={item.query}>
                    <span>{item.query}</span>
                    <strong>{item.count}</strong>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="admin-card__placeholder">No search activity recorded yet.</p>
            )}
          </div>

          <div className="admin-card">
            <h3 className="admin-card__title"><Sparkles size={15} /> Recommendation Metrics</h3>
            <div className="admin-analytics-metrics">
              <div><span>Total searches</span><strong>{analytics.total_searches}</strong></div>
              <div><span>Total recommendations</span><strong>{analytics.total_recommendations}</strong></div>
            </div>
          </div>

          <div className="admin-card">
            <h3 className="admin-card__title"><TrendingUp size={15} /> AI Request Types</h3>
            {Object.keys(analytics.ai_request_types ?? {}).length ? (
              <ul className="admin-analytics-list">
                {Object.entries(analytics.ai_request_types).map(([type, count]) => (
                  <li key={type}>
                    <span>{type}</span>
                    <strong>{count}</strong>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="admin-card__placeholder">No AI usage recorded yet.</p>
            )}
            <div className="admin-analytics-metrics">
              <div><span><Cpu size={13} /> Total AI requests</span><strong>{analytics.total_ai_requests}</strong></div>
            </div>
          </div>
        </div>
      )}

      {!loading && !error && !analytics && (
        <div className="admin-page__notice admin-page__notice--info">
          <BarChart2 size={16} />
          Analytics data is not available yet.
        </div>
      )}
    </div>
  );
}
