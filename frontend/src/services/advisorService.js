import { api } from './api';

/* ── Rule-based advisor (fast) ──────────────────────────── */

export async function advisorExplain(payload) {
  const { data } = await api.post('/api/advisor/explain', payload);
  return data;
}

export async function advisorRoadmap(payload) {
  const { data } = await api.post('/api/advisor/roadmap', payload);
  return data;
}

export async function advisorCompare(payload) {
  const { data } = await api.post('/api/advisor/compare', payload);
  return data;
}

export async function advisorSummary(payload) {
  const { data } = await api.post('/api/advisor/summary', payload);
  return data;
}

/* ── Project explainer (rule-based, structured metrics) ─── */

export async function explainProject(payload) {
  const { data } = await api.post('/api/project-explainer/explain', payload);
  return data;
}

/* ── RAG / Ollama (requires local Ollama) ───────────────── */

export async function ragExplain(payload) {
  const { data } = await api.post('/api/rag/explain', payload);
  return data;
}

export async function ragRoadmap(payload) {
  const { data } = await api.post('/api/rag/roadmap', payload);
  return data;
}
