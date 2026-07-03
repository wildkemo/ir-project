import { create } from 'zustand';

const DEFAULT_FILTERS = {
  language: null,
  license_name: null,
  min_stars: null,
  top_k: 10,
  topic: null,
};

export const useSearchStore = create((set, get) => ({
  query: '',
  filters: { ...DEFAULT_FILTERS },
  filterOptions: { languages: [], licenses: [], topics: [] },
  results: [],
  resultCount: 0,
  hasSearched: false,
  loading: false,
  error: null,
  searchEngine: null,

  setQuery(query) { set({ query }); },
  setFilters(filters) { set({ filters: { ...get().filters, ...filters } }); },
  resetFilters()  { set({ filters: { ...DEFAULT_FILTERS } }); },
  setFilterOptions(opts) { set({ filterOptions: opts }); },

  setResults({ results, count, engine }) {
    set({
      results,
      resultCount: count ?? results.length,
      hasSearched: true,
      searchEngine: engine ?? null,
    });
  },

  setLoading(loading) { set({ loading }); },
  setError(error)     { set({ error }); },
  clearError()        { set({ error: null }); },

  clearResults() {
    set({
      results: [],
      resultCount: 0,
      hasSearched: false,
      error: null,
      searchEngine: null,
    });
  },
}));
