import { useEffect, useState } from 'react';
import { Cpu } from 'lucide-react';
import { getAdminAILogs } from '../../services/adminService';
import { getErrorMessage } from '../../services/api';
import { timeAgo } from '../../utils/format';
import { SkeletonText } from '../../components/ui/Skeleton';
import EmptyState from '../../components/ui/EmptyState';
import './AdminPage.css';

export default function AdminAIUsagePage() {
  const [logs, setLogs]     = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState(null);

  useEffect(() => {
    getAdminAILogs(50)
      .then((data) => setLogs(data?.logs ?? []))
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="admin-page page-enter">
      <div className="admin-page__header">
        <h1 className="admin-page__title">AI Usage</h1>
        <p className="admin-page__subtitle">Track AI Advisor and RAG endpoint usage across the platform.</p>
      </div>

      {loading && <SkeletonText lines={8} />}
      {error && <div className="admin-page__notice">{error}</div>}
      {!loading && !error && logs.length === 0 && (
        <EmptyState icon={<Cpu size={28} />} title="No AI activity yet" description="AI requests will appear here as users use the Advisor feature." />
      )}
      {!loading && !error && logs.length > 0 && (
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Request Type</th>
                <th>Repository</th>
                <th>Model</th>
                <th>Latency</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id}>
                  <td>
                    <span className="admin-badge admin-badge--ai">{log.request_type}</span>
                  </td>
                  <td className="admin-table__truncate">{log.repo_identifier ?? '—'}</td>
                  <td>{log.model ?? '—'}</td>
                  <td>{log.latency_ms != null ? `${Math.round(log.latency_ms)}ms` : '—'}</td>
                  <td className="admin-table__date">{timeAgo(log.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
