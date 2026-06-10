import React, { useState } from "react";
import { explainRepo, generateRoadmap, compareRepos, advisorSummary } from "../api/advisor";

export default function AdvisorButtons({
  repo,
  profile,
  query,
  score_breakdown,
  selectedCompareRepo,
  searchResults,
  onExplain,
  onRoadmap,
  onCompare,
  onAdvisor,
}) {
  const [loading, setLoading] = useState(false);

  async function handleExplain() {
    setLoading(true);
    try {
      const data = await explainRepo({ repo, profile, query, score_breakdown });
      onExplain?.(data);
    } finally {
      setLoading(false);
    }
  }

  async function handleRoadmap() {
    setLoading(true);
    try {
      const data = await generateRoadmap({ repo, profile });
      onRoadmap?.(data);
    } finally {
      setLoading(false);
    }
  }

  async function handleCompare() {
    if (!selectedCompareRepo) return;
    setLoading(true);
    try {
      const data = await compareRepos({
        repo_a: repo,
        repo_b: selectedCompareRepo,
        profile,
        query,
      });
      onCompare?.(data);
    } finally {
      setLoading(false);
    }
  }

  async function handleAdvisorSummary() {
    setLoading(true);
    try {
      const data = await advisorSummary({
        query,
        profile,
        results: searchResults || [],
        top_k: 5,
      });
      onAdvisor?.(data);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="advisor-buttons">
      <button onClick={handleExplain} disabled={loading}>Explain</button>
      <button onClick={handleRoadmap} disabled={loading}>Roadmap</button>
      <button onClick={handleCompare} disabled={loading || !selectedCompareRepo}>Compare</button>
      <button onClick={handleAdvisorSummary} disabled={loading || !searchResults?.length}>
        Advisor Summary
      </button>
    </div>
  );
}
