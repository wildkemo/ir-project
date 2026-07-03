import './Input.css';

export default function Input({
  label,
  error,
  hint,
  icon,
  iconRight,
  className = '',
  wrapperClass = '',
  textarea = false,
  rows = 4,
  ...props
}) {
  const Tag = textarea ? 'textarea' : 'input';
  return (
    <div className={`input-wrap ${wrapperClass}`}>
      {label && <label className="input-label">{label}</label>}
      <div className={`input-field-wrap ${icon ? 'input-field-wrap--icon-left' : ''} ${iconRight ? 'input-field-wrap--icon-right' : ''}`}>
        {icon && <span className="input-icon input-icon--left">{icon}</span>}
        <Tag
          className={`input-field ${textarea ? 'input-field--textarea' : ''} ${error ? 'input-field--error' : ''} ${className}`}
          rows={textarea ? rows : undefined}
          {...props}
        />
        {iconRight && <span className="input-icon input-icon--right">{iconRight}</span>}
      </div>
      {error && <p className="input-error">{error}</p>}
      {hint && !error && <p className="input-hint">{hint}</p>}
    </div>
  );
}
