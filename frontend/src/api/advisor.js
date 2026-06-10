// Advisor API client for OpenSeek frontend.
// Adjust API_BASE if your existing client.js already centralizes Axios.

import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function explainRepo({ repo, profile, query, score_breakdown, include_roadmap = true }) {
  const { data } = await axios.post(`${API_BASE}/api/advisor/explain`, {
    repo,
    profile,
    query,
    score_breakdown,
    include_roadmap,
  });
  return data;
}

export async function generateRoadmap({ repo, profile }) {
  const { data } = await axios.post(`${API_BASE}/api/advisor/roadmap`, {
    repo,
    profile,
  });
  return data;
}

export async function compareRepos({ repo_a, repo_b, profile, query }) {
  const { data } = await axios.post(`${API_BASE}/api/advisor/compare`, {
    repo_a,
    repo_b,
    profile,
    query,
  });
  return data;
}

export async function advisorSummary({ query, profile, results, top_k = 5 }) {
  const { data } = await axios.post(`${API_BASE}/api/advisor/summary`, {
    query,
    profile,
    results,
    top_k,
  });
  return data;
}
