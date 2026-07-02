import axios from 'axios';
import { loadAccessToken } from '../utils/authStorage';

const API_BASE_URL =
  import.meta.env.VITE_API_URL?.replace(/\/$/, '') ||
  (import.meta.env.DEV ? '/api' : 'http://127.0.0.1:8000');

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 120000,
});

api.interceptors.request.use((config) => {
  const token = loadAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export function getApiErrorMessage(error) {
  if (!error) return 'An unexpected error occurred.';

  if (error.code === 'ERR_NETWORK' || !error.response) {
    return `Cannot reach the API at ${API_BASE_URL}. Start the backend: uvicorn backend.main:app --reload --port 8000`;
  }

  const detail = error.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail.map((d) => d.msg || JSON.stringify(d)).join(', ');
  }
  if (detail && typeof detail === 'object') {
    return detail.message || JSON.stringify(detail);
  }

  return error.response?.data?.message || error.message || 'Request failed.';
}

export async function checkHealth() {
  const { data } = await api.get('/health');
  return data;
}

export async function searchRepos(payload) {
  const { data } = await api.post('/search/', payload);
  return data;
}

export async function explainResult(payload) {
  const { data } = await api.post('/search/explain', payload);
  return data;
}

export async function recommendRepos(payload) {
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

export { API_BASE_URL };
