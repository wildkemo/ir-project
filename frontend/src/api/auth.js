import axios from 'axios';
import {
  clearAuthStorage,
  loadAccessToken,
  loadRefreshToken,
  saveTokens,
  saveUser,
} from '../utils/authStorage';
import { getApiErrorMessage, API_BASE_URL } from './client';

const authApi = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

authApi.interceptors.request.use((config) => {
  const token = loadAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function registerUser(payload) {
  const { data } = await authApi.post('/auth/register', payload);
  return data;
}

export async function loginUser(payload) {
  const { data } = await authApi.post('/auth/login', payload);
  saveTokens(data);
  return data;
}

export async function logoutUser() {
  const refreshToken = loadRefreshToken();
  try {
    if (refreshToken) {
      await authApi.post('/auth/logout', { refresh_token: refreshToken });
    }
  } finally {
    clearAuthStorage();
  }
}

export async function fetchCurrentUser() {
  const { data } = await authApi.get('/auth/me');
  saveUser(data);
  return data;
}

export async function updateUserProfile(payload) {
  const { data } = await authApi.patch('/users/me', payload);
  saveUser(data);
  return data;
}

export async function getUserPreferences() {
  const { data } = await authApi.get('/users/preferences');
  return data;
}

export async function saveUserPreferences(payload) {
  const { data } = await authApi.put('/users/preferences', payload);
  return data;
}

export async function getFavorites() {
  const { data } = await authApi.get('/users/favorites');
  return data;
}

export async function addFavorite(repoIdentifier) {
  const { data } = await authApi.post('/users/favorites', { repo_identifier: repoIdentifier });
  return data;
}

export async function removeFavorite(repoIdentifier) {
  const { data } = await authApi.delete(
    `/users/favorites/${encodeURIComponent(repoIdentifier)}`,
  );
  return data;
}

export async function getSearchHistory(limit = 50) {
  const { data } = await authApi.get('/users/history/search', { params: { limit } });
  return data;
}

export async function getRecommendationHistory(limit = 50) {
  const { data } = await authApi.get('/users/history/recommendations', { params: { limit } });
  return data;
}

export async function getAiHistory(limit = 50) {
  const { data } = await authApi.get('/users/history/ai', { params: { limit } });
  return data;
}

export async function refreshAccessToken() {
  const refreshToken = loadRefreshToken();
  if (!refreshToken) throw new Error('No refresh token');

  const { data } = await authApi.post('/auth/refresh', { refresh_token: refreshToken });
  saveTokens(data);
  return data;
}

export { getApiErrorMessage };
