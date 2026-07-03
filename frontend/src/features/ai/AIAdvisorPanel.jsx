import { useState } from 'react';
import {
  Cpu, Loader2, AlertCircle, BookOpen, Map, GitCompare, HelpCircle, Brain, FileText,
} from 'lucide-react';
import Button from '../../components/ui/Button';
import Badge from '../../components/ui/Badge';
import {
  advisorExplain, advisorRoadmap, explainProject, ragExplain, ragRoadmap,
} from '../../services/advisorService';
import { getErrorMessage } from '../../services/api';
import { getRepoDisplayName } from '../../utils/repoDisplay';
import './AIAdvisorPanel.css';

const QUICK_QUESTIONS = [
  { icon: HelpCircle,  label: 'Is it beginner-friendly?',        type: 'explain' },
  { icon: BookOpen,    label: 'What can I learn from this?',      type: 'explain' },
  { icon: GitCompare,  label: 'What makes this unique?',          type: 'explain' },
  { icon: Map,         label: 'Generate a learning roadmap',      type: 'roadmap' },
];

const MODES = [
  { id: 'advisor',   label: 'Advisor',   icon: Cpu },
  { id: 'explainer', label: 'Explainer', icon: FileText },
  { id: 'rag',       label: 'RAG (AI)',  icon: Brain },
];

export default function AIAdvisorPanel({ repo, profile }) {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeType, setActiveType] = useState(null);
  const [mode, setMode] = useState('advisor');
  const [customQuery, setCustomQuery] = useState('');

  if (!repo) {
    return (
      <div className="ai-panel ai-panel--empty">
        <Cpu size={32} className="ai-panel__empty-icon" />
        <p>Select a repository to activate the AI Advisor.</p>
      </div>
    );
  }

  const name = getRepoDisplayName(repo);

  const runQuery = async (type, query = null) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setActiveType(type);

    try {
      let data;
      if (mode === 'rag') {
        data = type === 'roadmap'
          ? await ragRoadmap({ repo, profile, query: query || null })
          : await ragExplain({ repo, profile, query: query || null });
      } else if (mode === 'explainer') {
        data = await explainProject({ repo, profile, query: query || null });
      } else if (type === 'roadmap') {
        data = await advisorRoadmap({ repo, profile });
      } else {
        data = await advisorExplain({
          repo,
          profile,
          query: query || null,
          include_roadmap: false,
        });
      }
      setResult({ type, data, mode });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleCustomQuery = (e) => {
    e.preventDefault();
    if (!customQuery.trim()) return;
    runQuery(mode === 'explainer' ? 'explainer' : 'explain', customQuery.trim());
    setCustomQuery('');
  };

  return (
    <div className="ai-panel">
      <div className="ai-panel__header">
        <Cpu size={16} className="ai-panel__header-icon" />
        <span className="ai-panel__header-title">AI Advisor</span>
        <span className="ai-panel__header-repo">{name}</span>
      </div>

      <div className="ai-panel__modes">
        {MODES.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            type="button"
            className={`ai-panel__mode-btn ${mode === id ? 'ai-panel__mode-btn--active' : ''}`}
            onClick={() => { setMode(id); setResult(null); setError(null); }}
          >
            <Icon size={13} />
            {label}
          </button>
        ))}
      </div>

      {mode === 'advisor' && (
        <div className="ai-panel__quick-actions">
          {QUICK_QUESTIONS.map(({ icon: Icon, label, type }) => (
            <button
              key={label}
              className="ai-panel__quick-btn"
              onClick={() => runQuery(type, type === 'explain' ? label : null)}
              disabled={loading}
            >
              <Icon size={14} />
              {label}
            </button>
          ))}
        </div>
      )}

      {mode === 'explainer' && (
        <p className="ai-panel__mode-hint">
          Structured project analysis with README insights, metrics, and usage guidance.
        </p>
      )}

      {mode === 'rag' && (
        <p className="ai-panel__mode-hint">
          Ollama-powered explanations. Requires a running local Ollama instance.
        </p>
      )}

      <form className="ai-panel__custom" onSubmit={handleCustomQuery}>
        <input
          className="ai-panel__custom-input"
          type="text"
          placeholder={
            mode === 'explainer'
              ? 'Ask about this project…'
              : mode === 'rag'
                ? 'Ask the RAG model…'
                : 'Ask anything about this repo…'
          }
          value={customQuery}
          onChange={(e) => setCustomQuery(e.target.value)}
          disabled={loading}
        />
        <Button type="submit" variant="ai" size="sm" disabled={!customQuery.trim() || loading}>
          Ask
        </Button>
      </form>

      {mode !== 'advisor' && (
        <div className="ai-panel__mode-actions">
          <Button
            variant="secondary"
            size="sm"
            icon={<FileText size={13} />}
            loading={loading && activeType === 'explainer'}
            onClick={() => runQuery('explainer')}
          >
            {mode === 'explainer' ? 'Explain project' : 'Quick explain'}
          </Button>
          <Button
            variant="roadmap"
            size="sm"
            icon={<Map size={13} />}
            loading={loading && activeType === 'roadmap'}
            onClick={() => runQuery('roadmap')}
          >
            Roadmap
          </Button>
        </div>
      )}

      <div className="ai-panel__output">
        {loading && (
          <div className="ai-panel__loading">
            <Loader2 size={20} className="ai-panel__loading-icon" />
            <span>Analyzing repository…</span>
          </div>
        )}

        {error && !loading && (
          <div className="ai-panel__error">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        {result && !loading && (
          <div className="ai-panel__result animate-fade-in">
            {result.mode === 'rag' && <RagResult data={result.data} />}
            {result.mode === 'explainer' && <ProjectExplainerResult data={result.data} />}
            {result.mode === 'advisor' && result.type === 'explain' && (
              <ExplainResult data={result.data} />
            )}
            {result.mode === 'advisor' && result.type === 'roadmap' && (
              <RoadmapResult data={result.data} />
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function ExplainResult({ data }) {
  const explanation = data.explanation || data.summary || data.result || JSON.stringify(data, null, 2);
  const scoreBreakdown = data.score_breakdown || data.scores;

  return (
    <div className="ai-result">
      {data.title && <h4 className="ai-result__title">{data.title}</h4>}
      <div className="ai-result__text">
        {typeof explanation === 'string'
          ? explanation.split('\n').map((line, i) => <p key={i}>{line}</p>)
          : <pre>{JSON.stringify(explanation, null, 2)}</pre>
        }
      </div>

      {scoreBreakdown && (
        <div className="ai-result__scores">
          {Object.entries(scoreBreakdown).map(([key, val]) => (
            <div key={key} className="ai-result__score-item">
              <span className="ai-result__score-label">{key.replace(/_/g, ' ')}</span>
              <div className="ai-result__score-bar">
                <div
                  className="ai-result__score-fill"
                  style={{ width: `${Math.round((val <= 1 ? val * 100 : val))}%` }}
                />
              </div>
              <span className="ai-result__score-value">
                {Math.round(val <= 1 ? val * 100 : val)}%
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function RoadmapResult({ data }) {
  const steps = data.steps;
  const text = data.roadmap || data.result || data.content;

  return (
    <div className="ai-result">
      <h4 className="ai-result__title">{data.title || 'Learning Roadmap'}</h4>
      {Array.isArray(steps) ? (
        <ol className="ai-result__steps">
          {steps.map((step, i) => (
            <li key={i}>
              <strong>{step.title || step.name || `Step ${i + 1}`}</strong>
              {step.description && <p>{step.description}</p>}
            </li>
          ))}
        </ol>
      ) : (
        <div className="ai-result__text roadmap-text">
          {typeof text === 'string'
            ? text.split('\n').map((line, i) => {
                if (!line.trim()) return null;
                const isStep = /^\d+[\.\)]/.test(line.trim()) || /^[-•*]/.test(line.trim());
                return (
                  <p key={i} className={isStep ? 'roadmap-step' : ''}>
                    {line}
                  </p>
                );
              })
            : <pre>{JSON.stringify(text, null, 2)}</pre>
          }
        </div>
      )}
    </div>
  );
}

function RagResult({ data }) {
  return (
    <div className="ai-result">
      <div className="ai-result__meta">
        {data.model && <Badge variant="ai" size="sm">{data.model}</Badge>}
        {data.mode && <Badge variant="default" size="sm">{data.mode}</Badge>}
      </div>
      <div className="ai-result__text">
        {(data.answer || '').split('\n').map((line, i) => (
          line.trim() ? <p key={i}>{line}</p> : null
        ))}
      </div>
    </div>
  );
}

function ProjectExplainerResult({ data }) {
  const sections = [
    ['Summary', data.project_summary],
    ['Best for', data.best_for],
    ['Difficulty', data.difficulty],
    ['Strengths', data.strengths],
    ['Limitations', data.limitations],
    ['How to use', data.how_to_use_it],
    ['Why it matches', data.why_it_matches],
  ].filter(([, value]) => value);

  return (
    <div className="ai-result">
      {data.repo_identity?.full_name && (
        <h4 className="ai-result__title">{data.repo_identity.full_name}</h4>
      )}
      {sections.map(([label, value]) => (
        <div key={label} className="ai-result__section">
          <h5>{label}</h5>
          {Array.isArray(value) ? (
            <ul>
              {value.map((item, i) => <li key={i}>{typeof item === 'string' ? item : JSON.stringify(item)}</li>)}
            </ul>
          ) : typeof value === 'object' ? (
            <pre>{JSON.stringify(value, null, 2)}</pre>
          ) : (
            <p>{String(value)}</p>
          )}
        </div>
      ))}
    </div>
  );
}
