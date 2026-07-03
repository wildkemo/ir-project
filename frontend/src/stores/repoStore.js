import { create } from 'zustand';

export const useRepoStore = create((set, get) => ({
  selectedRepo: null,
  compareRepos: [],      // up to 2 repos for comparison
  compareResult: null,
  roadmapRepo: null,
  roadmapResult: null,

  selectRepo(repo)  { set({ selectedRepo: repo }); },
  clearSelected()   { set({ selectedRepo: null }); },

  // Compare
  addToCompare(repo) {
    const { compareRepos } = get();
    if (compareRepos.find((r) => r.full_name === repo.full_name)) return;
    if (compareRepos.length >= 2) {
      set({ compareRepos: [compareRepos[1], repo] });
    } else {
      set({ compareRepos: [...compareRepos, repo] });
    }
  },
  removeFromCompare(fullName) {
    set({ compareRepos: get().compareRepos.filter((r) => r.full_name !== fullName) });
  },
  clearCompare() { set({ compareRepos: [], compareResult: null }); },
  setCompareResult(result) { set({ compareResult: result }); },

  // Roadmap
  setRoadmapRepo(repo)     { set({ roadmapRepo: repo }); },
  setRoadmapResult(result) { set({ roadmapResult: result }); },
  clearRoadmap()           { set({ roadmapRepo: null, roadmapResult: null }); },
}));
