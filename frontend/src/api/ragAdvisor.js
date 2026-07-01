const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

async function postJson(path, body) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || 'RAG request failed');
  }

  return response.json();
}

export function explainRepoWithAI({ repo, query = null, profile = null }) {
  return postJson('/api/rag/explain', {
    repo,
    query,
    profile,
  });
}

export function generateRoadmapWithAI({ repo, query = null, profile = null }) {
  return postJson('/api/rag/roadmap', {
    repo,
    query,
    profile,
  });
}