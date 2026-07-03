import './Skeleton.css';

export function Skeleton({ width, height, className = '', style }) {
  return (
    <div
      className={`skeleton ${className}`}
      style={{ width, height, ...style }}
      aria-hidden="true"
    />
  );
}

export function SkeletonCard({ className = '' }) {
  return (
    <div className={`skeleton-card ${className}`} aria-hidden="true">
      <div className="skeleton-card__header">
        <Skeleton width="60%" height="1.125rem" />
        <Skeleton width="80px" height="1.25rem" style={{ borderRadius: '999px' }} />
      </div>
      <Skeleton height="0.875rem" style={{ marginTop: '0.5rem' }} />
      <Skeleton width="85%" height="0.875rem" style={{ marginTop: '0.35rem' }} />
      <div className="skeleton-card__footer">
        <Skeleton width="60px" height="1.25rem" style={{ borderRadius: '999px' }} />
        <Skeleton width="60px" height="1.25rem" style={{ borderRadius: '999px' }} />
        <Skeleton width="60px" height="1.25rem" style={{ borderRadius: '999px' }} />
      </div>
    </div>
  );
}

export function SkeletonText({ lines = 3, className = '' }) {
  return (
    <div className={`skeleton-text ${className}`} aria-hidden="true">
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          height="0.875rem"
          width={i === lines - 1 ? '70%' : '100%'}
          style={{ marginBottom: '0.5rem' }}
        />
      ))}
    </div>
  );
}
