import { useSearchStore } from '../../stores/searchStore';
import './SearchFilters.css';

const STAR_OPTIONS = [
  { label: 'Any', value: null },
  { label: '100+', value: 100 },
  { label: '500+', value: 500 },
  { label: '1k+', value: 1000 },
  { label: '5k+', value: 5000 },
  { label: '10k+', value: 10000 },
];

const TOP_K_OPTIONS = [5, 10, 20, 50];

export default function SearchFilters({ filterOptions = {} }) {
  const { filters, setFilters, resetFilters } = useSearchStore();
  const { languages = [], licenses = [], topics = [] } = filterOptions;

  const hasActive = Object.entries(filters).some(([k, v]) => {
    if (k === 'top_k') return v !== 10;
    return v != null;
  });

  return (
    <div className="search-filters">
      <div className="search-filters__header">
        <span className="search-filters__title">Filters</span>
        {hasActive && (
          <button className="search-filters__reset" onClick={resetFilters}>
            Reset all
          </button>
        )}
      </div>

      <div className="search-filters__grid">
        {/* Language */}
        <div className="search-filters__group">
          <label className="search-filters__label">Language</label>
          <select
            className="search-filters__select"
            value={filters.language ?? ''}
            onChange={(e) => setFilters({ language: e.target.value || null })}
          >
            <option value="">Any language</option>
            {languages.map((l) => <option key={l} value={l}>{l}</option>)}
          </select>
        </div>

        {/* Min Stars */}
        <div className="search-filters__group">
          <label className="search-filters__label">Minimum Stars</label>
          <div className="search-filters__chips">
            {STAR_OPTIONS.map(({ label, value }) => (
              <button
                key={label}
                className={`search-filters__chip ${filters.min_stars === value ? 'search-filters__chip--active' : ''}`}
                onClick={() => setFilters({ min_stars: value })}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Topic */}
        {topics.length > 0 && (
          <div className="search-filters__group">
            <label className="search-filters__label">Topic</label>
            <select
              className="search-filters__select"
              value={filters.topic ?? ''}
              onChange={(e) => setFilters({ topic: e.target.value || null })}
            >
              <option value="">Any topic</option>
              {topics.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
        )}

        {/* License */}
        {licenses.length > 0 && (
          <div className="search-filters__group">
            <label className="search-filters__label">License</label>
            <select
              className="search-filters__select"
              value={filters.license_name ?? ''}
              onChange={(e) => setFilters({ license_name: e.target.value || null })}
            >
              <option value="">Any license</option>
              {licenses.map((l) => <option key={l} value={l}>{l}</option>)}
            </select>
          </div>
        )}

        {/* Result count */}
        <div className="search-filters__group">
          <label className="search-filters__label">Results</label>
          <div className="search-filters__chips">
            {TOP_K_OPTIONS.map((k) => (
              <button
                key={k}
                className={`search-filters__chip ${filters.top_k === k ? 'search-filters__chip--active' : ''}`}
                onClick={() => setFilters({ top_k: k })}
              >
                {k}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
