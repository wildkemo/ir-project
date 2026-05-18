import axios from 'axios';

const API_BASE_URL =
  import.meta.env.VITE_API_URL?.replace(/\/$/, '') || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 60000,
});

export function getApiErrorMessage(error) {
  if (!error) return 'An unexpected error occurred.';

  if (error.code === 'ERR_NETWORK' || !error.response) {
    return `Cannot reach the API at ${API_BASE_URL}. Make sure the backend is running and CORS is enabled.`;
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

export async function searchRepos(payload) {
  const { data } = await api.post('/search/', payload);
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

export { API_BASE_URL };
