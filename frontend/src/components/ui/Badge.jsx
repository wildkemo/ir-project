import './Badge.css';

/**
 * variant: 'default' | 'search' | 'semantic' | 'ai' | 'roadmap' | 'compare' | 'rec' | 'fav'
 *          | 'success' | 'warning' | 'error' | 'info'
 * size:    'sm' | 'md'
 */
export default function Badge({ children, variant = 'default', size = 'sm', dot = false, className = '' }) {
  return (
    <span className={`badge badge--${variant} badge--${size} ${className}`}>
      {dot && <span className="badge__dot" />}
      {children}
    </span>
  );
}
