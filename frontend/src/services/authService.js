import { api } from './api';
import { saveTokens, saveUser, clearAuthStorage, loadRefreshToken } from '../utils/authStorage';

export async function register(payload) {
  const { data } = await api.post('/auth/register', payload);
  return data;
}

export async function login(payload) {
  const { data } = await api.post('/auth/login', payload);
  saveTokens(data);
  return data;
}

export async function logout() {
  const refresh = loadRefreshToken();
  try {
    if (refresh) await api.post('/auth/logout', { refresh_token: refresh });
  } finally {
    clearAuthStorage();
  }
}

export async function getMe() {
  const { data } = await api.get('/auth/me');
  saveUser(data);
  return data;
}

export async function updateProfile(payload) {
  const { data } = await api.patch('/users/me', payload);
  saveUser(data);
  return data;
}

export async function getUserPreferences() {
  const { data } = await api.get('/users/preferences');
  return data;
}

export async function updateUserPreferences(payload) {
  const { data } = await api.put('/users/preferences', payload);
  return data;
}
