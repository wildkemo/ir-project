import { useState, useRef, useEffect } from 'react';
import { Search, X, Zap, Brain, SlidersHorizontal } from 'lucide-react';
import Button from '../../components/ui/Button';
import './SearchBar.css';

export default function SearchBar({
  value,
  onChange,
  onSearch,
  loading = false,
  placeholder = 'Search repositories… (e.g. "FastAPI authentication JWT")',
  showFilters = false,
  onToggleFilters,
  engine,
}) {
  const inputRef = useRef(null);

  // ⌘K shortcut
  useEffect(() => {
    const handler = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && value.trim()) onSearch?.();
  };

  return (
    <div className="search-bar">
      <div className="search-bar__input-wrap">
        <Search size={18} className="search-bar__icon" aria-hidden="true" />
        <input
          ref={inputRef}
          className="search-bar__input"
          type="search"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          aria-label="Search repositories"
          autoComplete="off"
          autoCorrect="off"
          autoCapitalize="off"
          spellCheck="false"
        />
        {value && (
          <button
            className="search-bar__clear"
            onClick={() => onChange('')}
            aria-label="Clear search"
          >
            <X size={16} />
          </button>
        )}

        {engine && (
          <span className={`search-bar__engine search-bar__engine--${engine}`}>
            {engine === 'hybrid'   && <><Zap  size={12} />Hybrid</>}
            {engine === 'semantic' && <><Brain size={12} />Semantic</>}
            {engine === 'bm25'     && <><Search size={12} />BM25</>}
          </span>
        )}

        <Button
          variant="primary"
          size="md"
          onClick={onSearch}
          loading={loading}
          disabled={!value.trim() || loading}
          className="search-bar__submit"
        >
          Search
        </Button>
      </div>

      {onToggleFilters && (
        <button
          className={`search-bar__filter-btn ${showFilters ? 'search-bar__filter-btn--active' : ''}`}
          onClick={onToggleFilters}
          aria-label="Toggle filters"
          aria-expanded={showFilters}
        >
          <SlidersHorizontal size={15} />
          Filters
        </button>
      )}
    </div>
  );
}
