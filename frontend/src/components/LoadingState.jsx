import { Loader2 } from 'lucide-react';

export default function LoadingState({ message = 'Searching repositories…' }) {
  return (
    <div className="loading-state" role="status" aria-live="polite">
      <Loader2 className="loading-state__spinner" size={36} aria-hidden />
      <p>{message}</p>
    </div>
  );
}
