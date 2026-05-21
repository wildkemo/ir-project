import { Filter, RotateCcw } from 'lucide-react';

const TOP_K_OPTIONS = [5, 10, 15, 20, 25];

export default function Filters({
  filters,
  filterOptions,
  onChange,
  onReset,
  onApply,
  showApply,
  disabled,
}) {
  const { language, license_name, min_stars, top_k, topic } = filters;
  const languages = filterOptions?.languages ?? [];
  const licenses = filterOptions?.licenses ?? [];
  const topics = filterOptions?.topics ?? [];

  return (
    <div className="filters">
      <div className="filters__header">
        <Filter size={18} aria-hidden />
        <span>Filters</span>
      </div>
      <div className="filters__grid">
        <label className="filter-field">
          <span>Language</span>
          <select
            value={language ?? ''}
            onChange={(e) => onChange('language', e.target.value || null)}
            disabled={disabled}
          >
            <option value="">Any language</option>
            {languages.map((lang) => (
              <option key={lang} value={lang}>
                {lang}
              </option>
            ))}
          </select>
        </label>

        <label className="filter-field">
          <span>License</span>
          <select
            value={license_name ?? ''}
            onChange={(e) => onChange('license_name', e.target.value || null)}
            disabled={disabled}
          >
            <option value="">Any license</option>
            {licenses.map((lic) => (
              <option key={lic} value={lic}>
                {lic}
              </option>
            ))}
          </select>
        </label>

        <label className="filter-field">
          <span>Min stars</span>
          <input
            type="number"
            min="0"
            placeholder="e.g. 1000"
            value={min_stars ?? ''}
            onChange={(e) => {
              const v = e.target.value;
              onChange('min_stars', v === '' ? null : Number(v));
            }}
            disabled={disabled}
          />
        </label>

        <label className="filter-field">
          <span>Results (top K)</span>
          <select
            value={top_k ?? 10}
            onChange={(e) => onChange('top_k', Number(e.target.value))}
            disabled={disabled}
          >
            {TOP_K_OPTIONS.map((k) => (
              <option key={k} value={k}>
                {k}
              </option>
            ))}
          </select>
        </label>

        <label className="filter-field filter-field--wide">
          <span>Topic</span>
          <input
            type="text"
            list="topic-options"
            placeholder="e.g. machine-learning"
            value={topic ?? ''}
            onChange={(e) => onChange('topic', e.target.value.trim() || null)}
            disabled={disabled}
          />
          <datalist id="topic-options">
            {topics.map((t) => (
              <option key={t} value={t} />
            ))}
          </datalist>
        </label>

        <div className="filter-field filter-field--action">
          <span className="filter-field__spacer" aria-hidden>
            &nbsp;
          </span>
          <div className="filters__actions">
            {showApply && (
              <button
                type="button"
                className="btn btn--secondary"
                onClick={onApply}
                disabled={disabled}
              >
                Apply filters
              </button>
            )}
            <button
              type="button"
              className="btn btn--ghost"
              onClick={onReset}
              disabled={disabled}
            >
              <RotateCcw size={16} aria-hidden />
              Reset
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
