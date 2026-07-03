/**
 * RepoMind AI — Core API client
 * Single Axios instance with auth interceptors.
 */
import axios from 'axios';
import { loadAccessToken, loadRefreshToken, saveTokens, clearAuthStorage } from '../utils/authStorage';

// In dev, Vite proxies /api → http://127.0.0.1:8000
// In prod, set VITE_API_URL to the backend base URL (no trailing slash)
export const API_BASE_URL =
  import.meta.env.VITE_API_URL?.replace(/\/$/, '') ||
  (import.meta.env.DEV ? '' : 'http://127.0.0.1:8000');

// Prefix used by the Vite proxy rewrite rule
const PROXY_PREFIX = import.meta.env.DEV ? '/api' : API_BASE_URL;

// Direct backend URL (bypasses proxy) — used for /api/* backend routes
export const DIRECT_URL =
  import.meta.env.VITE_DIRECT_URL?.replace(/\/$/, '') || 'http://127.0.0.1:8000';

export const api = axios.create({
  baseURL: PROXY_PREFIX,
  headers: { 'Content-Type': 'application/json' },
  timeout: 120_000,
});

// Attach access token to every request
api.interceptors.request.use((config) => {
  const token = loadAccessToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// On 401 try to refresh once, then redirect to login
let isRefreshing = false;
let failedQueue = [];

function processQueue(error, token = null) {
  failedQueue.forEach((prom) => (error ? prom.reject(error) : prom.resolve(token)));
  failedQueue = [];
}

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            original.headers.Authorization = `Bearer ${token}`;
            return api(original);
          })
          .catch(Promise.reject);
      }

      original._retry = true;
      isRefreshing = true;

      const refresh = loadRefreshToken();
      if (!refresh) {
        clearAuthStorage();
        isRefreshing = false;
        return Promise.reject(error);
      }

      try {
        const { data } = await axios.post(`${PROXY_PREFIX}/auth/refresh`, {
          refresh_token: refresh,
        });
        saveTokens(data);
        processQueue(null, data.access_token);
        original.headers.Authorization = `Bearer ${data.access_token}`;
        return api(original);
      } catch (err) {
        processQueue(err, null);
        clearAuthStorage();
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  },
);

/** Normalise any axios / fetch error into a human-readable string. */
export function getErrorMessage(error) {
  if (!error) return 'An unexpected error occurred.';
  if (error.code === 'ERR_NETWORK' || !error.response) {
    return 'Cannot reach the API server. Make sure the backend is running on port 8000.';
  }
  const detail = error.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (error.response?.status === 503) {
    return detail ?? 'Database is unavailable. Start PostgreSQL with: docker compose up -d postgres';
  }
  if (error.response?.status >= 500 && !detail) {
    return 'Server error. If sign-in fails, ensure PostgreSQL is running (docker compose up -d postgres).';
  }
  if (Array.isArray(detail)) return detail.map((d) => d.msg ?? JSON.stringify(d)).join(', ');
  if (detail && typeof detail === 'object') return detail.message ?? JSON.stringify(detail);
  return error.response?.data?.message ?? error.message ?? 'Request failed.';
}

/** POST to a /api/* backend route directly (Ollama / RAG endpoints). */
export async function directPost(path, body) {
  const res = await fetch(`${DIRECT_URL}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(loadAccessToken() ? { Authorization: `Bearer ${loadAccessToken()}` } : {}),
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request to ${path} failed`);
  }
  return res.json();
}
