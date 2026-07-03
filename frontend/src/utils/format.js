/** Format large numbers: 1234 → "1.2k", 1234567 → "1.2m" */
export function formatNumber(n) {
  if (!n && n !== 0) return '—';
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}m`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}k`;
  return String(n);
}

/** Format ISO date string → "Jun 12, 2024" */
export function formatDate(iso) {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleDateString('en-US', {
      year: 'numeric', month: 'short', day: 'numeric',
    });
  } catch {
    return iso;
  }
}

/** Relative time: "2 hours ago" */
export function timeAgo(iso) {
  if (!iso) return '';
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 1)   return 'just now';
  if (mins < 60)  return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24)   return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  if (days < 30)  return `${days}d ago`;
  return formatDate(iso);
}

/** Score (0–1 or 0–100) → percentage string */
export function formatScore(score) {
  if (score == null) return '—';
  const pct = score <= 1 ? score * 100 : score;
  return `${Math.round(pct)}%`;
}

/** Capitalise first letter */
export function capitalize(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/** Truncate string to maxLength chars, appending ellipsis */
export function truncate(str, maxLength = 120) {
  if (!str) return '';
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength).trimEnd() + '…';
}

/** Convert snake_case or kebab-case to Title Case */
export function toTitleCase(str) {
  if (!str) return '';
  return str
    .replace(/[-_]/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

/** Get language colour dot (basic, GitHub-ish) */
const LANG_COLORS = {
  python: '#3572A5', javascript: '#F1E05A', typescript: '#2B7489',
  go: '#00ADD8', rust: '#DEA584', java: '#B07219', kotlin: '#A97BFF',
  cpp: '#F34B7D', 'c++': '#F34B7D', c: '#555555', csharp: '#178600',
  ruby: '#701516', swift: '#FA7343', php: '#4F5D95', html: '#E34C26',
  css: '#563D7C', shell: '#89E051', r: '#198CE7', scala: '#DC322F',
  vue: '#41B883', dart: '#00B4AB',
};
export function getLangColor(lang) {
  if (!lang) return '#94A3B8';
  return LANG_COLORS[lang.toLowerCase()] ?? '#94A3B8';
}
