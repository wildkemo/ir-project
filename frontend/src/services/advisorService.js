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

export async function advisorChat({ repo, message, profile, history = [] }) {
  const { data } = await api.post('/api/advisor/chat', {
    repo,
    message,
    profile,
    history,
  });
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

export async function ragChat({ repo, message, profile, history = [] }) {
  const { data } = await api.post('/api/rag/chat', {
    repo,
    message,
    profile,
    history,
  });
  return data;
}

/** Generate a repo-specific roadmap — RAG when available, rule-based fallback. */
export async function generateRepoRoadmap({ repo, profile, query }) {
  const focus = query || 'Create a personalized learning roadmap for this repository';
  try {
    return await ragRoadmap({ repo, profile, query: focus });
  } catch {
    return await advisorRoadmap({ repo, profile, query: focus });
  }
}

/** Extract display text from any advisor/RAG response shape. */
export function extractAnswerText(data) {
  if (!data) return '';
  if (typeof data.answer === 'string') return data.answer;
  if (typeof data.summary === 'string') return data.summary;
  if (data.roadmap?.steps) {
    const title = data.roadmap.title || data.title || 'Learning Roadmap';
    const steps = data.roadmap.steps.map((s, i) => {
      if (typeof s === 'string') return `${i + 1}. ${s}`;
      return `${i + 1}. ${s.title || s.name || s.description || JSON.stringify(s)}`;
    });
    return `${title}\n\n${steps.join('\n')}`;
  }
  if (Array.isArray(data.steps)) {
    return [data.title || 'Roadmap', '', ...data.steps.map((s, i) => `${i + 1}. ${s}`)].join('\n');
  }
  return JSON.stringify(data, null, 2);
}
