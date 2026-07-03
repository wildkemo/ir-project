import { useEffect, useState } from 'react';
import { Activity, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { checkHealth } from '../../services/searchService';
import { api } from '../../services/api';
import './AdminPage.css';

function StatusRow({ label, status, detail }) {
  const Icon = status === 'ok'      ? CheckCircle
             : status === 'warning' ? AlertTriangle
             :                        XCircle;
  const cls  = status === 'ok' ? 'green' : status === 'warning' ? 'yellow' : 'red';

  return (
    <div className="admin-system-row">
      <Icon size={16} className={`admin-system-row__icon admin-system-row__icon--${cls}`} />
      <span className="admin-system-row__label">{label}</span>
      <span className={`admin-system-row__status admin-system-row__status--${cls}`}>
        {status === 'ok' ? 'Healthy' : status === 'warning' ? 'Warning' : 'Error'}
      </span>
      {detail && <span className="admin-system-row__detail">{detail}</span>}
    </div>
  );
}

export default function AdminSystemPage() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkHealth()
      .then(setHealth)
      .catch(() => setHealth({ status: 'error' }))
      .finally(() => setLoading(false));
  }, []);

  const isOk = health?.status === 'ok';
  const dbOk = health?.database === 'ok';

  return (
    <div className="admin-page page-enter">
      <div className="admin-page__header">
        <h1 className="admin-page__title">System Health</h1>
        <p className="admin-page__subtitle">Real-time status of all platform services.</p>
      </div>

      {loading && <div className="admin-page__notice">Checking system health…</div>}

      {health && (
        <div className="admin-card admin-card--system">
          <div className="admin-card__title-row">
            <h3 className="admin-card__title">Service Status</h3>
            <span className={`admin-badge admin-badge--${isOk ? 'success' : 'error'}`}>
              {isOk ? 'All systems operational' : 'Issues detected'}
            </span>
          </div>

          <div className="admin-system-list">
            <StatusRow
              label="Backend API"
              status={isOk ? 'ok' : 'error'}
              detail={health?.version ? `v${health.version}` : undefined}
            />
            <StatusRow
              label="Search Engine (BM25 + Semantic)"
              status={health?.search_ready !== false ? 'ok' : 'warning'}
            />
            <StatusRow
              label="PostgreSQL"
              status={dbOk ? 'ok' : 'error'}
              detail={health?.database}
            />
            <StatusRow
              label="Qdrant Vector DB"
              status={health?.qdrant_connected ? 'ok' : 'warning'}
              detail="Optional — RAG and semantic search"
            />
            <StatusRow
              label="Ollama (Local LLM)"
              status={health?.ollama_connected ? 'ok' : 'warning'}
              detail="Optional — required for RAG endpoints"
            />
          </div>

          {health && Object.keys(health).length > 0 && (
            <details className="admin-health-raw">
              <summary>Raw health response</summary>
              <pre>{JSON.stringify(health, null, 2)}</pre>
            </details>
          )}
        </div>
      )}
    </div>
  );
}
