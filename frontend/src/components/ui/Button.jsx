import './Button.css';

/**
 * variant: 'primary' | 'secondary' | 'ghost' | 'danger' | 'ai' | 'roadmap'
 * size:    'sm' | 'md' | 'lg'
 */
export default function Button({
  children,
  variant = 'secondary',
  size = 'md',
  loading = false,
  disabled = false,
  icon,
  iconRight,
  fullWidth = false,
  className = '',
  ...props
}) {
  return (
    <button
      className={`btn btn--${variant} btn--${size} ${fullWidth ? 'btn--full' : ''} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <span className="btn__spinner" aria-hidden="true" />
      ) : icon ? (
        <span className="btn__icon btn__icon--left">{icon}</span>
      ) : null}
      {children && <span className="btn__label">{children}</span>}
      {iconRight && !loading && (
        <span className="btn__icon btn__icon--right">{iconRight}</span>
      )}
    </button>
  );
}
