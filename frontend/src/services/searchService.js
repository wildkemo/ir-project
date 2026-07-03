import { api } from './api';

export async function search(payload) {
  const { data } = await api.post('/search/', payload);
  return data;
}

export async function explainSearchResult(payload) {
  const { data } = await api.post('/search/explain', payload);
  return data;
}

export async function recommend(payload) {
  const { data } = await api.post('/recommend/', payload);
  return data;
}

export async function getFilterOptions() {
  const { data } = await api.get('/repos/filters/options');
  return data;
}

export async function listRepos(limit = 20) {
  const { data } = await api.get('/repos/', { params: { limit } });
  return data;
}

export async function getRepoDetails(repoIdentifier) {
  const { data } = await api.get(`/repos/details/${encodeURIComponent(repoIdentifier)}`);
  return data;
}

export async function getProfileQuestions() {
  const { data } = await api.get('/profile/questions');
  return data;
}

export async function recommendFromProfile(profile) {
  const { data } = await api.post('/profile/recommend', {
    ...profile,
    top_k: profile.top_k ?? 10,
  });
  return data;
}

export async function checkHealth() {
  const { data } = await api.get('/health');
  return data;
}
