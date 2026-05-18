import { Search, Inbox, AlertCircle } from 'lucide-react';

const VARIANTS = {
  initial: {
    icon: Search,
    title: 'Discover open-source projects',
    description:
      'Search by intent — frameworks, ML toolkits, dashboards, and more. Try an example query below or type your own.',
  },
  noResults: {
    icon: Inbox,
    title: 'No repositories found',
    description:
      'Try broadening your query or resetting filters. Different keywords often surface better matches.',
  },
  error: {
    icon: AlertCircle,
    title: 'Something went wrong',
    description: null,
  },
};

export default function EmptyState({ variant = 'initial', message }) {
  const config = VARIANTS[variant] ?? VARIANTS.initial;
  const Icon = config.icon;

  return (
    <div className={`empty-state empty-state--${variant}`}>
      <div className="empty-state__icon-wrap">
        <Icon size={32} aria-hidden />
      </div>
      <h3>{config.title}</h3>
      <p>{message || config.description}</p>
    </div>
  );
}
