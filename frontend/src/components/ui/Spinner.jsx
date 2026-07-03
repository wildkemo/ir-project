import './Spinner.css';

export default function Spinner({ size = 'md', label = 'Loading…', center = false }) {
  return (
    <div className={`spinner-wrap ${center ? 'spinner-wrap--center' : ''}`} role="status">
      <div className={`spinner spinner--${size}`} aria-hidden="true" />
      {label && <span className="sr-only">{label}</span>}
    </div>
  );
}
