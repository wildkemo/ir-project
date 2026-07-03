import { api } from './api';

/* ── Favorites ──────────────────────────────────────────── */

export async function getFavorites() {
  const { data } = await api.get('/users/favorites');
  return data;
}

export async function addFavorite(repoIdentifier) {
  const { data } = await api.post('/users/favorites', { repo_identifier: repoIdentifier });
  return data;
}

export async function removeFavorite(repoIdentifier) {
  const { data } = await api.delete(`/users/favorites/${encodeURIComponent(repoIdentifier)}`);
  return data;
}

/* ── History ────────────────────────────────────────────── */

export async function getSearchHistory() {
  const { data } = await api.get('/users/history/search');
  return data;
}

export async function getRecommendationHistory() {
  const { data } = await api.get('/users/history/recommendations');
  return data;
}

export async function getAIHistory() {
  const { data } = await api.get('/users/history/ai');
  return data;
}
