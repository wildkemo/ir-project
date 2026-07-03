import { Link } from 'react-router-dom';
import { Search, Cpu, GitCompare, Map, Star, ArrowRight, Zap, Brain, Shield } from 'lucide-react';
import Button from '../components/ui/Button';
import './LandingPage.css';

const FEATURES = [
  { icon: Search,     color: 'search',   title: 'Hybrid Search',         desc: 'BM25 lexical precision combined with semantic embeddings for the most relevant results.' },
  { icon: Cpu,        color: 'ai',       title: 'AI Advisor',            desc: 'Ask natural language questions about any repository. Get instant, explainable answers.' },
  { icon: GitCompare, color: 'compare',  title: 'Repository Comparison', desc: 'Side-by-side AI-powered comparison of any two repositories across every dimension.' },
  { icon: Map,        color: 'roadmap',  title: 'Learning Roadmaps',     desc: 'Personalized step-by-step paths to master any open-source project or technology.' },
  { icon: Star,       color: 'fav',      title: 'Smart Discovery',       desc: 'Profile-based recommendations tailored to your skill level, language, and goals.' },
  { icon: Brain,      color: 'semantic', title: 'Semantic Understanding', desc: 'The engine understands technical context — search for "AI" finds ML and Deep Learning too.' },
];

const STATS = [
  { value: '200+', label: 'Curated Repositories' },
  { value: 'BM25',  label: 'Lexical Engine' },
  { value: 'RAG',   label: 'AI Architecture' },
  { value: '100%',  label: 'Open Source' },
];

export default function LandingPage() {
  return (
    <div className="landing">
      {/* Hero */}
      <section className="landing__hero">
        <div className="landing__hero-glow" aria-hidden="true" />
        <div className="landing__hero-content">
          <div className="landing__hero-badge">
            <Zap size={12} />
            Developer Intelligence Platform
          </div>
          <h1 className="landing__hero-title">
            Discover. Understand.<br />
            <span className="landing__hero-title-accent">Learn.</span>
          </h1>
          <p className="landing__hero-desc">
            RepoMind AI goes beyond search. It understands your goals, your skill level, and your
            preferred stack — then guides you through open-source discovery with AI-powered
            explanations, comparisons, and personalized learning roadmaps.
          </p>
          <div className="landing__hero-cta">
            <Link to="/register">
              <Button variant="primary" size="lg" iconRight={<ArrowRight size={17} />}>
                Get started free
              </Button>
            </Link>
            <Link to="/search">
              <Button variant="secondary" size="lg" icon={<Search size={16} />}>
                Try search
              </Button>
            </Link>
          </div>

          <div className="landing__hero-hint">
            No credit card required · No setup · Works immediately
          </div>
        </div>

        {/* Demo card */}
        <div className="landing__hero-demo">
          <div className="landing__demo-search">
            <Search size={16} className="landing__demo-search-icon" />
            <span>FastAPI authentication JWT REST API</span>
            <span className="landing__demo-badge">Hybrid</span>
          </div>
          <div className="landing__demo-results">
            {['tiangolo/fastapi', 'encode/starlette', 'mpdavis/python-jose'].map((name, i) => (
              <div key={name} className="landing__demo-result" style={{ animationDelay: `${i * 0.1}s` }}>
                <div className="landing__demo-result-left">
                  <div className="landing__demo-result-lang" />
                  <div>
                    <div className="landing__demo-result-name">{name}</div>
                    <div className="landing__demo-result-desc">High performance web framework…</div>
                  </div>
                </div>
                <div className="landing__demo-result-score">{98 - i * 12}%</div>
              </div>
            ))}
          </div>
          <div className="landing__demo-ai-badge">
            <Cpu size={12} />
            AI Advisor active
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="landing__stats">
        {STATS.map(({ value, label }) => (
          <div key={label} className="landing__stat">
            <span className="landing__stat-value">{value}</span>
            <span className="landing__stat-label">{label}</span>
          </div>
        ))}
      </section>

      {/* Features */}
      <section className="landing__features">
        <div className="landing__section-header">
          <h2>Everything you need to master open source</h2>
          <p>Not just a search engine. A full intelligence platform for developers.</p>
        </div>
        <div className="landing__features-grid">
          {FEATURES.map(({ icon: Icon, color, title, desc }) => (
            <div key={title} className={`landing__feature landing__feature--${color}`}>
              <div className="landing__feature-icon">
                <Icon size={20} />
              </div>
              <h3 className="landing__feature-title">{title}</h3>
              <p className="landing__feature-desc">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Flow */}
      <section className="landing__flow">
        <div className="landing__section-header">
          <h2>Guided Discovery, not just a list</h2>
          <p>Every step is designed to deepen understanding.</p>
        </div>
        <div className="landing__flow-steps">
          {['Search', 'Understand', 'Compare', 'Learn', 'Save', 'Personalize'].map((step, i) => (
            <div key={step} className="landing__flow-step">
              <div className="landing__flow-step-num">{i + 1}</div>
              <span className="landing__flow-step-label">{step}</span>
              {i < 5 && <ArrowRight size={14} className="landing__flow-arrow" />}
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="landing__cta-section">
        <Shield size={28} className="landing__cta-icon" />
        <h2 className="landing__cta-title">Built for serious developers</h2>
        <p className="landing__cta-desc">
          RepoMind AI is your copilot for open-source exploration. Join thousands of developers
          who use it to learn faster, contribute smarter, and build better.
        </p>
        <Link to="/register">
          <Button variant="primary" size="lg" iconRight={<ArrowRight size={17} />}>
            Start discovering
          </Button>
        </Link>
      </section>

      {/* Footer */}
      <footer className="landing__footer">
        <div className="landing__footer-brand">
          <span className="landing__footer-icon">⬡</span>
          <span>RepoMind AI</span>
        </div>
        <p className="landing__footer-copy">
          © {new Date().getFullYear()} RepoMind AI · Developer Intelligence Platform
        </p>
      </footer>
    </div>
  );
}
