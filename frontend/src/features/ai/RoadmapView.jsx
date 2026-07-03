import { useState } from 'react';
import { Map, Loader2, AlertCircle, Download, BookOpen, ChevronRight } from 'lucide-react';
import Button from '../../components/ui/Button';
import { advisorRoadmap } from '../../services/advisorService';
import { getErrorMessage } from '../../services/api';
import { getRepoDisplayName } from '../../utils/repoDisplay';
import './RoadmapView.css';

export default function RoadmapView({ repo, profile, savedRoadmap, onSave }) {
  const [result, setResult] = useState(savedRoadmap ?? null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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
      const data = await advisorRoadmap({ repo, profile });
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
    const text = result.roadmap || result.result || JSON.stringify(result, null, 2);
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
            <p className="roadmap-view__loading-title">Generating your roadmap…</p>
            <p className="roadmap-view__loading-sub">This may take a moment.</p>
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
          <p>Click "Generate Roadmap" to get a personalized step-by-step learning plan for <strong>{name}</strong>.</p>
        </div>
      )}
    </div>
  );
}

function RoadmapContent({ data, repoName }) {
  const text = data.roadmap || data.result || data.content || '';

  if (!text) {
    return <pre className="roadmap-raw">{JSON.stringify(data, null, 2)}</pre>;
  }

  // Parse sections from the roadmap text
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
