import { Search } from 'lucide-react';

const EXAMPLE_QUERIES = [
  'python web framework for APIs',
  'machine learning projects for beginners',
  'react dashboard typescript',
  'natural language processing toolkit',
];

export default function SearchBar({
  query,
  onQueryChange,
  onSubmit,
  onExampleClick,
  disabled,
}) {
  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit?.();
  };

  return (
    <div className="search-bar">
      <form className="search-bar__form" onSubmit={handleSubmit}>
        <Search className="search-bar__icon" size={22} aria-hidden />
        <input
          type="search"
          className="search-bar__input"
          placeholder="Describe the project you're looking for…"
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          disabled={disabled}
          aria-label="Search query"
        />
        <button type="submit" className="btn btn--primary" disabled={disabled || !query.trim()}>
          Search
        </button>
      </form>
      <div className="search-bar__chips" role="list" aria-label="Example queries">
        {EXAMPLE_QUERIES.map((example) => (
          <button
            key={example}
            type="button"
            className="chip"
            onClick={() => onExampleClick(example)}
            disabled={disabled}
            role="listitem"
          >
            {example}
          </button>
        ))}
      </div>
    </div>
  );
}
