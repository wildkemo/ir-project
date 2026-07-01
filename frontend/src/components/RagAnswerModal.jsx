import { createPortal } from 'react-dom';
import { X, Sparkles, AlertTriangle } from 'lucide-react';

export default function RagAnswerModal({
  open,
  title,
  loading,
  error,
  answer,
  onClose,
}) {
  if (!open) return null;

  return createPortal(
    <div className="rag-modal__overlay" onClick={onClose}>
      <div
        className="rag-modal__box"
        onClick={(event) => event.stopPropagation()}
      >
        <header className="rag-modal__header">
          <div>
            <p className="rag-modal__eyebrow">OpenSeek AI Advisor</p>
            <h2>{title || 'AI Answer'}</h2>
          </div>

          <button
            type="button"
            className="rag-modal__close"
            onClick={onClose}
            aria-label="Close AI answer"
          >
            <X size={20} />
          </button>
        </header>

        <div className="rag-modal__body">
          {loading && (
            <div className="rag-modal__loading">
              <Sparkles size={20} />
              Generating grounded answer using local Ollama model...
            </div>
          )}

          {error && (
            <div className="rag-modal__error">
              <AlertTriangle size={18} />
              {error}
            </div>
          )}

          {!loading && !error && answer && (
            <div className="rag-modal__answer">
              {answer.split('\n').map((line, index) => {
                const text = line.trim();

                if (!text) {
                  return <br key={index} />;
                }

                const isHeading =
                  text.length < 80 &&
                  !text.endsWith('.') &&
                  !text.startsWith('-') &&
                  !/^\d+\./.test(text);

                if (isHeading) {
                  return <h3 key={index}>{text}</h3>;
                }

                return <p key={index}>{text}</p>;
              })}
            </div>
          )}
        </div>
      </div>
    </div>,
    document.body,
  );
}