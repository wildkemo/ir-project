const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export async function explainProject({ repo, profile = null, query = null }) {
  const response = await fetch(`${API_BASE_URL}/api/project-explainer/explain`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      repo,
      profile,
      query,
    }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || 'Failed to explain project');
  }

  return response.json();
}