import { useState, useEffect } from 'react';
import { Map, Loader2, AlertCircle, Download, BookOpen, ChevronRight } from 'lucide-react';
import Button from '../../components/ui/Button';
import { generateRepoRoadmap, extractAnswerText } from '../../services/advisorService';
import { getErrorMessage } from '../../services/api';
import { getRepoDisplayName } from '../../utils/repoDisplay';
import './RoadmapView.css';

export default function RoadmapView({ repo, profile, savedRoadmap, onSave }) {
  const [result, setResult] = useState(savedRoadmap ?? null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [focus, setFocus] = useState('');
  const repoId = repo?.full_name ?? repo?.title;

  useEffect(() => {
    setResult(savedRoadmap ?? null);
    setError(null);
    setFocus('');
  }, [repoId, savedRoadmap]);

  if (!repo) {
    return (
      <div className="roadmap-view roadmap-view--empty">
        <Map size={32} className="roadmap-view__empty-icon" />
        <p>Select a repository to generate a learning roadmap.</p>
      </div>
    );
  }

  const name = getRepoDisplayName(repo);

  const generate = async () => {
    setLoading(true);
    setError(null);
    try {
      const query = focus.trim()
        ? `Create a learning roadmap for ${name} with this focus: ${focus.trim()}`
        : `Create a personalized step-by-step learning roadmap for ${name}`;
      const data = await generateRepoRoadmap({ repo, profile, query });
      setResult(data);
      onSave?.(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!result) return;
    const text = extractAnswerText(result);
    const blob = new Blob([`# Learning Roadmap: ${name}\n\n${text}`], { type: 'text/markdown' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href = url;
    a.download = `${name.replace('/', '-')}-roadmap.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="roadmap-view">
      <div className="roadmap-view__header">
        <Map size={16} className="roadmap-view__icon" />
        <div className="roadmap-view__header-text">
          <span className="roadmap-view__label">Learning Roadmap</span>
          <span className="roadmap-view__repo-name">{name}</span>
        </div>
        <div className="roadmap-view__header-actions">
          {result && (
            <Button
              variant="ghost"
              size="sm"
              icon={<Download size={13} />}
              onClick={handleDownload}
              aria-label="Download roadmap"
            >
              Export
            </Button>
          )}
          <Button
            variant="roadmap"
            size="sm"
            loading={loading}
            icon={<Map size={13} />}
            onClick={generate}
          >
            {result ? 'Regenerate' : 'Generate Roadmap'}
          </Button>
        </div>
      </div>

      <div className="roadmap-view__focus">
        <input
          type="text"
          className="roadmap-view__focus-input"
          placeholder={`Optional focus for ${name.split('/').pop()} (e.g. contribution, deployment, beginners)…`}
          value={focus}
          onChange={(e) => setFocus(e.target.value)}
          disabled={loading}
        />
      </div>

      {error && (
        <div className="roadmap-view__error">
          <AlertCircle size={14} />
          {error}
        </div>
      )}

      {loading && (
        <div className="roadmap-view__loading">
          <Loader2 size={20} className="roadmap-view__spin" />
          <div>
            <p className="roadmap-view__loading-title">Generating roadmap for {name}…</p>
            <p className="roadmap-view__loading-sub">Analyzing repository context and your profile.</p>
          </div>
        </div>
      )}

      {result && !loading && (
        <div className="roadmap-view__content animate-fade-in">
          <RoadmapContent data={result} repoName={name} />
        </div>
      )}

      {!result && !loading && !error && (
        <div className="roadmap-view__prompt">
          <BookOpen size={24} className="roadmap-view__prompt-icon" />
          <p>Click &quot;Generate Roadmap&quot; to get a personalized step-by-step learning plan for <strong>{name}</strong>.</p>
        </div>
      )}
    </div>
  );
}

function RoadmapContent({ data, repoName }) {
  const text = extractAnswerText(data);
  const steps = data?.roadmap?.steps || data?.steps;

  if (Array.isArray(steps) && steps.length > 0) {
    return (
      <div className="roadmap-sections">
        <h4 className="roadmap-content__title">{data.roadmap?.title || data.title || `Roadmap for ${repoName}`}</h4>
        <ol className="roadmap-structured-steps">
          {steps.map((step, i) => (
            <li key={i}>
              <strong>{typeof step === 'string' ? step : step.title || step.name || `Step ${i + 1}`}</strong>
              {typeof step === 'object' && step.description && <p>{step.description}</p>}
            </li>
          ))}
        </ol>
      </div>
    );
  }

  if (!text) {
    return <pre className="roadmap-raw">{JSON.stringify(data, null, 2)}</pre>;
  }

  const lines = text.split('\n').filter((l) => l.trim());
  const sections = [];
  let currentSection = null;

  lines.forEach((line) => {
    const trimmed = line.trim();
    if (/^#+\s/.test(trimmed) || /^(phase|step|stage|level|week)\s*\d*/i.test(trimmed)) {
      currentSection = { title: trimmed.replace(/^#+\s*/, ''), items: [] };
      sections.push(currentSection);
    } else if (currentSection) {
      currentSection.items.push(trimmed);
    } else {
      if (sections.length === 0) {
        currentSection = { title: 'Getting Started', items: [] };
        sections.push(currentSection);
      }
      currentSection.items.push(trimmed);
    }
  });

  if (sections.length === 0) {
    return (
      <div className="roadmap-plain">
        {lines.map((l, i) => <p key={i}>{l}</p>)}
      </div>
    );
  }

  return (
    <div className="roadmap-sections">
      {sections.map((section, idx) => (
        <div key={idx} className="roadmap-section">
          <div className="roadmap-section__header">
            <div className="roadmap-section__number">{idx + 1}</div>
            <h4 className="roadmap-section__title">{section.title}</h4>
          </div>
          <ul className="roadmap-section__items">
            {section.items.filter(Boolean).map((item, i) => (
              <li key={i} className="roadmap-section__item">
                <ChevronRight size={13} className="roadmap-section__item-icon" />
                <span>{item.replace(/^[-•*]\s*/, '')}</span>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
