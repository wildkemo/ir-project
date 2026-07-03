import { useEffect, useRef, useState, useCallback } from 'react';
import {
  Cpu, Loader2, AlertCircle, BookOpen, Map, HelpCircle, Send, Sparkles,
} from 'lucide-react';
import Button from '../../components/ui/Button';
import Badge from '../../components/ui/Badge';
import {
  advisorChat, generateRepoRoadmap, extractAnswerText,
} from '../../services/advisorService';
import { getRepoDetails } from '../../services/searchService';
import { getErrorMessage } from '../../services/api';
import { getRepoDisplayName, normalizeRepoRecord } from '../../utils/repoDisplay';
import './AIAdvisorPanel.css';

const QUICK_PROMPTS = [
  { icon: HelpCircle, label: 'Is it beginner-friendly?' },
  { icon: BookOpen,   label: 'What can I learn from this?' },
  { icon: Sparkles,   label: 'What makes this repo unique?' },
  { icon: Map,        label: 'How should I get started?' },
];

let messageId = 0;
function nextId() {
  messageId += 1;
  return `msg-${messageId}`;
}

function formatMessageContent(text) {
  if (!text) return null;
  return text.split('\n').map((line, i) => {
    if (!line.trim()) return null;
    const bold = line.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    return (
      <p
        key={i}
        className={/^\d+[\.\)]/.test(line.trim()) ? 'chat-bubble__step' : undefined}
        dangerouslySetInnerHTML={{ __html: bold }}
      />
    );
  });
}

export default function AIAdvisorPanel({ repo, profile }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeRepo, setActiveRepo] = useState(null);
  const chatEndRef = useRef(null);
  const repoId = repo?.full_name ?? repo?.title;

  const scrollToBottom = useCallback(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    if (!repoId) {
      setMessages([]);
      setActiveRepo(null);
      return;
    }

    const name = getRepoDisplayName(repo);
    setMessages([
      {
        id: nextId(),
        role: 'assistant',
        content: `Hi! I'm your AI advisor for **${name}**. Ask me anything about this repository — architecture, difficulty, how to learn it, or click **Generate Roadmap** for a step-by-step plan tailored to this repo.`,
        kind: 'welcome',
      },
    ]);
    setError(null);
    setInput('');
    setActiveRepo(repo);

    let cancelled = false;
    getRepoDetails(repoId)
      .then((data) => {
        if (!cancelled) {
          setActiveRepo(normalizeRepoRecord(data, repoId));
        }
      })
      .catch(() => {
        if (!cancelled) {
          setActiveRepo(repo);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [repoId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading, scrollToBottom]);

  const buildHistory = (currentMessages) =>
    currentMessages
      .filter((m) => m.role === 'user' || m.role === 'assistant')
      .filter((m) => m.kind !== 'welcome')
      .slice(-10)
      .map((m) => ({ role: m.role, content: m.content }));

  const sendMessage = async (text, { isRoadmap = false } = {}) => {
    const trimmed = text?.trim();
    const repoPayload = activeRepo || repo;
    if (!trimmed || !repoPayload || loading) return;

    const userMsg = {
      id: nextId(),
      role: 'user',
      content: trimmed,
      kind: isRoadmap ? 'roadmap-request' : 'question',
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      let data;
      if (isRoadmap) {
        data = await generateRepoRoadmap({
          repo: repoPayload,
          profile,
          query: trimmed,
        });
      } else {
        data = await advisorChat({
          repo: repoPayload,
          message: trimmed,
          profile,
          history: buildHistory([...messages, userMsg]),
        });
      }

      const answer = extractAnswerText(data);
      setMessages((prev) => [
        ...prev,
        {
          id: nextId(),
          role: 'assistant',
          content: answer,
          kind: isRoadmap ? 'roadmap' : 'answer',
          meta: data.mode || data.roadmap_type,
          model: data.model,
        },
      ]);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleRoadmap = () => {
    const name = getRepoDisplayName(activeRepo || repo);
    sendMessage(
      `Generate a detailed learning roadmap for ${name}. Include setup, core concepts, practice tasks, and next steps tailored to this repository's language, topics, and documentation.`,
      { isRoadmap: true },
    );
  };

  if (!repo) {
    return (
      <div className="ai-panel ai-panel--empty">
        <Cpu size={32} className="ai-panel__empty-icon" />
        <p>Select a repository to start chatting with the AI Advisor.</p>
      </div>
    );
  }

  const name = getRepoDisplayName(activeRepo || repo);

  return (
    <div className="ai-panel ai-panel--chat">
      <div className="ai-panel__header">
        <Cpu size={16} className="ai-panel__header-icon" />
        <span className="ai-panel__header-title">AI Chat</span>
        <span className="ai-panel__header-repo">{name}</span>
      </div>

      <div className="ai-chat__messages">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`chat-bubble chat-bubble--${msg.role} ${msg.kind ? `chat-bubble--${msg.kind}` : ''}`}
          >
            {msg.role === 'assistant' && (
              <div className="chat-bubble__avatar">
                <Cpu size={14} />
              </div>
            )}
            <div className="chat-bubble__body">
              {(msg.model || msg.meta) && (
                <div className="chat-bubble__meta">
                  {msg.model && <Badge variant="ai" size="sm">{msg.model}</Badge>}
                  {msg.meta && !msg.model && (
                    <Badge variant="default" size="sm">{msg.meta}</Badge>
                  )}
                </div>
              )}
              <div className="chat-bubble__content">
                {formatMessageContent(msg.content)}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="chat-bubble chat-bubble--assistant chat-bubble--typing">
            <div className="chat-bubble__avatar"><Loader2 size={14} className="ai-panel__loading-icon" /></div>
            <div className="chat-bubble__body">
              <span className="chat-bubble__typing-text">Thinking about {name}…</span>
            </div>
          </div>
        )}

        {error && (
          <div className="ai-panel__error">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      <div className="ai-chat__quick">
        {QUICK_PROMPTS.map(({ icon: Icon, label }) => (
          <button
            key={label}
            type="button"
            className="ai-panel__quick-btn"
            onClick={() => sendMessage(label)}
            disabled={loading}
          >
            <Icon size={14} />
            {label}
          </button>
        ))}
      </div>

      <div className="ai-chat__roadmap-row">
        <Button
          variant="roadmap"
          size="sm"
          icon={<Map size={14} />}
          loading={loading}
          onClick={handleRoadmap}
          disabled={loading}
        >
          Generate Roadmap
        </Button>
        <span className="ai-chat__roadmap-hint">Creates a step-by-step plan for {name.split('/').pop()}</span>
      </div>

      <form className="ai-chat__input-row" onSubmit={handleSubmit}>
        <input
          className="ai-panel__custom-input"
          type="text"
          placeholder={`Ask about ${name}…`}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />
        <Button
          type="submit"
          variant="ai"
          size="sm"
          icon={<Send size={14} />}
          disabled={!input.trim() || loading}
          aria-label="Send message"
        >
          Send
        </Button>
      </form>
    </div>
  );
}
