export const AI_TYPE_LABELS = {
  ai_chat: 'AI Chat',
  rag_explain: 'AI Explanation',
  learning_roadmap: 'Roadmap',
  explain_repository: 'Repo Explanation',
  compare_repositories: 'Comparison',
  repository_summary: 'Summary',
};

export function aiTypeLabel(type) {
  return AI_TYPE_LABELS[type] || type?.replace(/_/g, ' ') || 'AI';
}
