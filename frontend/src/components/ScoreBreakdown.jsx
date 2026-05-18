import { formatScore } from '../utils/format';

const SCORES = [
  { key: 'bm25_score', label: 'BM25' },
  { key: 'semantic_score', label: 'Semantic' },
  { key: 'phrase_score', label: 'Phrase' },
  { key: 'metadata_score', label: 'Metadata' },
];

export default function ScoreBreakdown({ repo }) {
  return (
    <div className="score-breakdown">
      {SCORES.map(({ key, label }) => {
        const raw = repo?.[key];
        const value = Number(raw);
        const pct = Number.isFinite(value) ? Math.min(100, Math.max(0, value * 100)) : 0;

        return (
          <div className="score-breakdown__row" key={key}>
            <div className="score-breakdown__label">
              <span>{label}</span>
              <span className="score-breakdown__value">{formatScore(raw)}</span>
            </div>
            <div className="score-breakdown__track" aria-hidden>
              <div
                className="score-breakdown__fill"
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
