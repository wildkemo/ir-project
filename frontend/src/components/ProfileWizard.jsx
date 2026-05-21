import { useEffect, useState } from 'react';
import { ClipboardList, Sparkles } from 'lucide-react';
import { getProfileQuestions, getApiErrorMessage } from '../api/client';
import LoadingState from './LoadingState';

const EMPTY_ANSWERS = {
  project_type: null,
  language: null,
  goal: null,
  level: null,
  repo_kind: null,
  complexity: null,
};

export default function ProfileWizard({ initialAnswers, onSubmit, loading, disabled }) {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState(initialAnswers ?? EMPTY_ANSWERS);
  const [loadError, setLoadError] = useState(null);
  const [questionsLoading, setQuestionsLoading] = useState(true);

  useEffect(() => {
    setAnswers(initialAnswers ?? EMPTY_ANSWERS);
  }, [initialAnswers]);

  useEffect(() => {
    setQuestionsLoading(true);
    getProfileQuestions()
      .then((data) => {
        setQuestions(Array.isArray(data?.questions) ? data.questions : []);
        setLoadError(null);
      })
      .catch((err) => setLoadError(getApiErrorMessage(err)))
      .finally(() => setQuestionsLoading(false));
  }, []);

  const handleChange = (id, value) => {
    setAnswers((prev) => ({ ...prev, [id]: value || null }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit?.(answers);
  };

  if (questionsLoading) {
    return (
      <section className="profile-wizard">
        <LoadingState message="Loading personalization questions…" />
      </section>
    );
  }

  if (loadError) {
    return (
      <section className="profile-wizard profile-wizard--error">
        <p role="alert">{loadError}</p>
      </section>
    );
  }

  return (
    <section className="profile-wizard" aria-labelledby="profile-wizard-title">
      <header className="profile-wizard__header">
        <div className="profile-wizard__icon" aria-hidden>
          <ClipboardList size={26} />
        </div>
        <div>
          <h2 id="profile-wizard-title">Personalize your recommendations</h2>
          <p>
            Answer a few questions so we can rank the best open-source projects for you.
            You can skip any question.
          </p>
        </div>
      </header>

      <form className="profile-wizard__form" onSubmit={handleSubmit}>
        <ol className="profile-wizard__questions">
          {questions.map((q, index) => (
            <li key={q.id} className="profile-question">
              <label htmlFor={`profile-${q.id}`}>
                <span className="profile-question__num">Q{index + 1}</span>
                {q.title}
              </label>
              <select
                id={`profile-${q.id}`}
                value={answers[q.id] ?? ''}
                onChange={(e) => handleChange(q.id, e.target.value || null)}
                disabled={disabled || loading}
              >
                {q.allow_skip !== false && (
                  <option value="">No preference / Skip</option>
                )}
                {(q.options ?? []).map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                    {opt.count != null ? ` (${opt.count} repos)` : ''}
                  </option>
                ))}
              </select>
            </li>
          ))}
        </ol>

        <button
          type="submit"
          className="btn btn--primary profile-wizard__submit"
          disabled={disabled || loading}
        >
          <Sparkles size={18} aria-hidden />
          {loading ? 'Finding your top 10…' : 'Get my 10 recommendations'}
        </button>
      </form>
    </section>
  );
}
