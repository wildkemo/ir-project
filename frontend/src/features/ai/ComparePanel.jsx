import { useState } from 'react';
import { GitCompare, X, Loader2, AlertCircle, Plus } from 'lucide-react';
import Button from '../../components/ui/Button';
import Badge from '../../components/ui/Badge';
import { advisorCompare } from '../../services/advisorService';
import { getErrorMessage } from '../../services/api';
import { getRepoDisplayName } from '../../utils/repoDisplay';
import { formatNumber } from '../../utils/format';
import './ComparePanel.css';

export default function ComparePanel({ repoA, repoB, onAddRepo, onRemoveRepo, profile }) {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const canCompare = repoA && repoB;

  const handleCompare = async () => {
    if (!canCompare) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await advisorCompare({ repo_a: repoA, repo_b: repoB, profile });
      setResult(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="compare-panel">
      <div className="compare-panel__header">
        <GitCompare size={16} className="compare-panel__icon" />
        <span className="compare-panel__title">Compare Repositories</span>
      </div>

      <div className="compare-panel__repos">
        <RepoSlot
          label="Repository A"
          repo={repoA}
          onRemove={() => onRemoveRepo?.(repoA?.full_name)}
          onAdd={onAddRepo}
        />
        <div className="compare-panel__vs">VS</div>
        <RepoSlot
          label="Repository B"
          repo={repoB}
          onRemove={() => onRemoveRepo?.(repoB?.full_name)}
          onAdd={onAddRepo}
        />
      </div>

      <Button
        variant="secondary"
        icon={<GitCompare size={15} />}
        onClick={handleCompare}
        loading={loading}
        disabled={!canCompare || loading}
        fullWidth
      >
        Compare with AI
      </Button>

      {error && (
        <div className="compare-panel__error">
          <AlertCircle size={14} />
          {error}
        </div>
      )}

      {loading && (
        <div className="compare-panel__loading">
          <Loader2 size={18} className="spin-icon" />
          Analyzing repositories…
        </div>
      )}

      {result && !loading && (
        <div className="compare-panel__result animate-fade-in">
          <CompareResult result={result} repoA={repoA} repoB={repoB} />
        </div>
      )}
    </div>
  );
}

function RepoSlot({ label, repo, onRemove, onAdd }) {
  if (!repo) {
    return (
      <div className="repo-slot repo-slot--empty">
        <span className="repo-slot__label">{label}</span>
        <button className="repo-slot__add-btn" onClick={onAdd} aria-label="Add repository">
          <Plus size={20} />
          <span>Search and add a repo</span>
        </button>
      </div>
    );
  }

  return (
    <div className="repo-slot repo-slot--filled">
      <span className="repo-slot__label">{label}</span>
      <div className="repo-slot__content">
        <span className="repo-slot__name">{getRepoDisplayName(repo)}</span>
        <button className="repo-slot__remove" onClick={onRemove} aria-label="Remove">
          <X size={14} />
        </button>
      </div>
      <div className="repo-slot__meta">
        {repo.language && <Badge variant="default" size="sm">{repo.language}</Badge>}
        <span className="repo-slot__stars">⭐ {formatNumber(repo.stars ?? repo.stargazers_count)}</span>
      </div>
    </div>
  );
}

function CompareResult({ result, repoA, repoB }) {
  const winner = result.winner;
  const recommendation = result.recommendation;
  const table = result.comparison_table;

  return (
    <div className="compare-result">
      <div className="compare-result__header">
        <span className="compare-result__repo">{getRepoDisplayName(repoA)}</span>
        <span className="compare-result__vs">vs</span>
        <span className="compare-result__repo">{getRepoDisplayName(repoB)}</span>
      </div>

      {winner && (
        <p className="compare-result__winner"><strong>Winner:</strong> {winner}</p>
      )}

      {recommendation && (
        <div className="compare-result__text">
          {typeof recommendation === 'string'
            ? recommendation.split('\n').filter(Boolean).map((line, i) => <p key={i}>{line}</p>)
            : <pre>{JSON.stringify(recommendation, null, 2)}</pre>
          }
        </div>
      )}

      {Array.isArray(table) && table.length > 0 && (
        <div className="compare-result__table-wrap">
          <table className="compare-result__table">
            <thead>
              <tr>
                <th>Criteria</th>
                <th>{getRepoDisplayName(repoA)}</th>
                <th>{getRepoDisplayName(repoB)}</th>
              </tr>
            </thead>
            <tbody>
              {table.map((row, i) => (
                <tr key={i}>
                  <td>{row.criterion ?? row.label ?? row.aspect}</td>
                  <td>{row.repo_a ?? row.a ?? '—'}</td>
                  <td>{row.repo_b ?? row.b ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!winner && !recommendation && !table && (
        <div className="compare-result__text">
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
