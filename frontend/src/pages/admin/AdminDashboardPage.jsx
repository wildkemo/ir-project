import { useEffect, useState } from 'react';
import { Users, BarChart2, Cpu, Activity, TrendingUp, Search } from 'lucide-react';
import { getAdminStats } from '../../services/adminService';
import { getErrorMessage } from '../../services/api';
import { SkeletonCard } from '../../components/ui/Skeleton';
import './AdminPage.css';

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className={`admin-stat admin-stat--${color}`}>
      <Icon size={20} className="admin-stat__icon" />
      <div>
        <div className="admin-stat__value">{value ?? '—'}</div>
        <div className="admin-stat__label">{label}</div>
      </div>
    </div>
  );
}

export default function AdminDashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getAdminStats()
      .then(setStats)
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="admin-page page-enter">
      <div className="admin-page__header">
        <h1 className="admin-page__title">Admin Overview</h1>
        <p className="admin-page__subtitle">Platform health, usage statistics, and system status.</p>
      </div>

      <div className="admin-stats-grid">
        <StatCard icon={Users}    label="Total Users"       value={stats?.total_users}         color="search" />
        <StatCard icon={Search}   label="Total Searches"    value={stats?.total_searches}      color="semantic" />
        <StatCard icon={Cpu}      label="AI Requests"       value={stats?.total_ai_requests}   color="ai" />
        <StatCard icon={TrendingUp} label="Recommendations" value={stats?.total_recommendations} color="rec" />
      </div>

      {loading && (
        <div className="admin-page__grid">
          {Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      )}

      {error && (
        <div className="admin-page__notice">
          <Activity size={16} />
          {error}
        </div>
      )}

      {!loading && !error && stats && (
        <div className="admin-page__grid">
          <div className="admin-card">
            <h3 className="admin-card__title">System Status</h3>
            <div className="admin-status-list">
              <div className="admin-status-item">
                <span className="admin-status-dot admin-status-dot--green" />
                <span>Backend API</span>
                <span className="admin-status-value">Online</span>
              </div>
              <div className="admin-status-item">
                <span className="admin-status-dot admin-status-dot--green" />
                <span>Search Engine</span>
                <span className="admin-status-value">Active</span>
              </div>
              <div className="admin-status-item">
                <span className={`admin-status-dot admin-status-dot--${stats?.qdrant_connected ? 'green' : 'yellow'}`} />
                <span>Qdrant (Vector DB)</span>
                <span className="admin-status-value">{stats?.qdrant_connected ? 'Connected' : 'Optional'}</span>
              </div>
              <div className="admin-status-item">
                <span className={`admin-status-dot admin-status-dot--${stats?.ollama_connected ? 'green' : 'yellow'}`} />
                <span>Ollama (RAG)</span>
                <span className="admin-status-value">{stats?.ollama_connected ? 'Connected' : 'Optional'}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
