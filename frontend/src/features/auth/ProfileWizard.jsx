import { useState } from 'react';
import { ChevronRight, ChevronLeft, Sparkles, Check } from 'lucide-react';
import Button from '../../components/ui/Button';
import './ProfileWizard.css';

const STEPS = [
  {
    id: 'goal',
    title: "What's your primary goal?",
    subtitle: 'This helps us personalize your recommendations.',
    field: 'goal',
    options: [
      { value: 'learning',     label: 'Learning',     desc: 'I want to study code and learn concepts.' },
      { value: 'contributing', label: 'Contributing',  desc: 'I want to contribute to open source.' },
      { value: 'using',        label: 'Using',         desc: 'I need libraries for my projects.' },
      { value: 'research',     label: 'Research',      desc: 'I\'m doing academic or professional research.' },
    ],
  },
  {
    id: 'level',
    title: 'What is your experience level?',
    subtitle: 'Be honest — we tailor complexity accordingly.',
    field: 'level',
    options: [
      { value: 'beginner',      label: 'Beginner',      desc: 'New to programming or this domain.' },
      { value: 'intermediate',  label: 'Intermediate',   desc: '1–3 years of hands-on experience.' },
      { value: 'advanced',      label: 'Advanced',       desc: '3+ years, comfortable with complex codebases.' },
    ],
  },
  {
    id: 'language',
    title: 'Preferred programming language?',
    subtitle: 'We\'ll prioritise repositories in your language.',
    field: 'language',
    options: [
      { value: 'python',     label: 'Python' },
      { value: 'javascript', label: 'JavaScript' },
      { value: 'typescript', label: 'TypeScript' },
      { value: 'rust',       label: 'Rust' },
      { value: 'go',         label: 'Go' },
      { value: 'java',       label: 'Java' },
      { value: 'cpp',        label: 'C++' },
      { value: 'any',        label: 'No preference' },
    ],
  },
  {
    id: 'project_type',
    title: 'What kind of projects interest you?',
    subtitle: 'Pick the domain that excites you most.',
    field: 'project_type',
    options: [
      { value: 'web',          label: 'Web Development' },
      { value: 'ai',           label: 'AI & Machine Learning' },
      { value: 'data',         label: 'Data Science' },
      { value: 'devtools',     label: 'Developer Tools' },
      { value: 'systems',      label: 'Systems & Infrastructure' },
      { value: 'mobile',       label: 'Mobile' },
      { value: 'security',     label: 'Security' },
      { value: 'any',          label: 'All types' },
    ],
  },
  {
    id: 'complexity',
    title: 'Preferred codebase complexity?',
    subtitle: 'How large and complex should the projects be?',
    field: 'complexity',
    options: [
      { value: 'simple',  label: 'Simple',  desc: 'Small, focused, easy to understand.' },
      { value: 'medium',  label: 'Medium',  desc: 'Moderate size, some architecture.' },
      { value: 'complex', label: 'Complex', desc: 'Large, production-grade codebases.' },
    ],
  },
];

export default function ProfileWizard({ onComplete, onSkip, initialAnswers = {} }) {
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState(initialAnswers);
  const [loading, setLoading] = useState(false);

  const current = STEPS[step];
  const isLast = step === STEPS.length - 1;
  const progress = ((step + 1) / STEPS.length) * 100;

  const handleSelect = (value) => {
    const updated = { ...answers, [current.field]: value };
    setAnswers(updated);
    if (!isLast) {
      setTimeout(() => setStep((s) => s + 1), 220);
    }
  };

  const handleComplete = async () => {
    setLoading(true);
    try {
      await onComplete(answers);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="profile-wizard">
      <div className="profile-wizard__progress-bar">
        <div
          className="profile-wizard__progress-fill"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="profile-wizard__header">
        <div className="profile-wizard__step-badge">
          Step {step + 1} of {STEPS.length}
        </div>
        <h2 className="profile-wizard__title">{current.title}</h2>
        <p className="profile-wizard__subtitle">{current.subtitle}</p>
      </div>

      <div className="profile-wizard__options">
        {current.options.map((opt) => {
          const selected = answers[current.field] === opt.value;
          return (
            <button
              key={opt.value}
              className={`profile-wizard__option ${selected ? 'profile-wizard__option--selected' : ''}`}
              onClick={() => handleSelect(opt.value)}
            >
              <div className="profile-wizard__option-content">
                <span className="profile-wizard__option-label">{opt.label}</span>
                {opt.desc && <span className="profile-wizard__option-desc">{opt.desc}</span>}
              </div>
              <div className="profile-wizard__option-check">
                {selected ? <Check size={14} /> : <ChevronRight size={14} />}
              </div>
            </button>
          );
        })}
      </div>

      <div className="profile-wizard__footer">
        {step > 0 && (
          <Button variant="ghost" icon={<ChevronLeft size={15} />} onClick={() => setStep((s) => s - 1)}>
            Back
          </Button>
        )}
        <div className="profile-wizard__footer-spacer" />
        {onSkip && (
          <Button variant="ghost" onClick={onSkip}>
            Skip for now
          </Button>
        )}
        {isLast && answers[current.field] && (
          <Button
            variant="primary"
            loading={loading}
            icon={<Sparkles size={15} />}
            onClick={handleComplete}
          >
            Get Recommendations
          </Button>
        )}
      </div>
    </div>
  );
}
