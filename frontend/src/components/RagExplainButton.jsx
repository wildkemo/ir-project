import { useState } from 'react';
import { Sparkles, Route } from 'lucide-react';

import {
  explainRepoWithAI,
  generateRoadmapWithAI,
} from '../api/ragAdvisor';

import RagAnswerModal from './RagAnswerModal';

export default function RagExplainButton({
  repo,
  query = null,
  profile = null,
  mode = 'explain',
}) {
  const [open, setOpen] = useState(false);
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const isRoadmap = mode === 'roadmap';

  const title = isRoadmap
    ? 'AI Roadmap'
    : 'AI Project Explanation';

  const label = isRoadmap
    ? 'AI Roadmap'
    : 'Explain with AI';

  const Icon = isRoadmap ? Route : Sparkles;

  async function handleClick() {
    setOpen(true);
    setLoading(true);
    setError('');
    setAnswer('');

    try {
      const data = isRoadmap
        ? await generateRoadmapWithAI({ repo, query, profile })
        : await explainRepoWithAI({ repo, query, profile });

      setAnswer(data.answer || 'No answer returned from the AI advisor.');
    } catch (err) {
      setError(err?.message || 'Failed to generate AI answer.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <button
        type="button"
        className="btn btn--secondary"
        onClick={handleClick}
      >
        <Icon size={16} aria-hidden />
        {label}
      </button>

      <RagAnswerModal
        open={open}
        title={title}
        loading={loading}
        error={error}
        answer={answer}
        onClose={() => setOpen(false)}
      />
    </>
  );
}