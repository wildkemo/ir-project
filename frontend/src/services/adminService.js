import { api } from './api';

export async function getAdminStats() {
  const { data } = await api.get('/admin/stats');
  return data;
}

export async function getAdminAnalytics() {
  const { data } = await api.get('/admin/analytics');
  return data;
}

export async function getAdminUsers(limit = 100) {
  const { data } = await api.get('/admin/users', { params: { limit } });
  return data;
}

export async function getAdminAILogs(limit = 50) {
  const { data } = await api.get('/admin/ai-logs', { params: { limit } });
  return data;
}
