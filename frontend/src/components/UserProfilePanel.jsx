import { useEffect, useState } from 'react';
import { Save, User } from 'lucide-react';
import {
  getApiErrorMessage,
  getUserPreferences,
  saveUserPreferences,
  updateUserProfile,
} from '../api/auth';
import { useAuth } from '../context/AuthContext';

const LEVEL_OPTIONS = ['beginner', 'intermediate', 'advanced'];
const GOAL_OPTIONS = ['learning', 'contribution', 'use', 'production', 'portfolio'];
const COMPLEXITY_OPTIONS = ['small', 'medium', 'large', 'any'];

export default function UserProfilePanel() {
  const { user, refreshUser } = useAuth();
  const [username, setUsername] = useState(user?.username || '');
  const [avatar, setAvatar] = useState(user?.avatar || '');
  const [bio, setBio] = useState(user?.bio || '');
  const [prefs, setPrefs] = useState({
    experience_level: '',
    preferred_license: '',
    project_type: '',
    goal: '',
    repo_kind: '',
    complexity: '',
    languages: '',
    topics: '',
    frameworks: '',
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    setUsername(user?.username || '');
    setAvatar(user?.avatar || '');
    setBio(user?.bio || '');
  }, [user]);

  useEffect(() => {
    getUserPreferences()
      .then((data) => {
        setPrefs({
          experience_level: data.experience_level || '',
          preferred_license: data.preferred_license || '',
          project_type: data.project_type || '',
          goal: data.goal || '',
          repo_kind: data.repo_kind || '',
          complexity: data.complexity || '',
          languages: (data.languages || []).join(', '),
          topics: (data.topics || []).join(', '),
          frameworks: (data.frameworks || []).join(', '),
        });
      })
      .catch((err) => setError(getApiErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  const splitList = (value) =>
    value
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean);

  const handleSave = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError(null);
    setMessage(null);

    try {
      await updateUserProfile({ username, avatar: avatar || null, bio: bio || null });
      await saveUserPreferences({
        experience_level: prefs.experience_level || null,
        preferred_license: prefs.preferred_license || null,
        project_type: prefs.project_type || null,
        goal: prefs.goal || null,
        repo_kind: prefs.repo_kind || null,
        complexity: prefs.complexity || null,
        languages: splitList(prefs.languages),
        topics: splitList(prefs.topics),
        frameworks: splitList(prefs.frameworks),
      });
      await refreshUser();
      setMessage('Profile saved successfully.');
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <p className="panel-note">Loading profile…</p>;
  }

  return (
    <section className="user-panel">
      <header className="user-panel__header">
        <User size={22} aria-hidden />
        <div>
          <h2>Your profile</h2>
          <p className="user-panel__meta">
            {user?.email} · {user?.role?.name}
          </p>
        </div>
      </header>

      {error && (
        <div className="alert alert--error" role="alert">
          {error}
        </div>
      )}
      {message && (
        <div className="alert alert--success" role="status">
          {message}
        </div>
      )}

      <form className="user-form" onSubmit={handleSave}>
        <div className="user-form__grid">
          <label className="auth-form__field">
            <span>Username</span>
            <input value={username} onChange={(e) => setUsername(e.target.value)} required />
          </label>

          <label className="auth-form__field">
            <span>Avatar URL</span>
            <input value={avatar} onChange={(e) => setAvatar(e.target.value)} placeholder="https://…" />
          </label>
        </div>

        <label className="auth-form__field">
          <span>Bio</span>
          <textarea value={bio} onChange={(e) => setBio(e.target.value)} rows={3} />
        </label>

        <h3 className="user-form__section-title">Recommendation preferences</h3>
        <p className="panel-note">
          These sync with the recommendation engine when you are signed in.
        </p>

        <div className="user-form__grid">
          <label className="auth-form__field">
            <span>Experience level</span>
            <select
              value={prefs.experience_level}
              onChange={(e) => setPrefs((p) => ({ ...p, experience_level: e.target.value }))}
            >
              <option value="">—</option>
              {LEVEL_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          </label>

          <label className="auth-form__field">
            <span>Goal</span>
            <select
              value={prefs.goal}
              onChange={(e) => setPrefs((p) => ({ ...p, goal: e.target.value }))}
            >
              <option value="">—</option>
              {GOAL_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          </label>

          <label className="auth-form__field">
            <span>Complexity</span>
            <select
              value={prefs.complexity}
              onChange={(e) => setPrefs((p) => ({ ...p, complexity: e.target.value }))}
            >
              <option value="">—</option>
              {COMPLEXITY_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          </label>

          <label className="auth-form__field">
            <span>Preferred license</span>
            <input
              value={prefs.preferred_license}
              onChange={(e) => setPrefs((p) => ({ ...p, preferred_license: e.target.value }))}
              placeholder="MIT"
            />
          </label>
        </div>

        <label className="auth-form__field">
          <span>Languages (comma-separated)</span>
          <input
            value={prefs.languages}
            onChange={(e) => setPrefs((p) => ({ ...p, languages: e.target.value }))}
            placeholder="Python, TypeScript"
          />
        </label>

        <label className="auth-form__field">
          <span>Topics (comma-separated)</span>
          <input
            value={prefs.topics}
            onChange={(e) => setPrefs((p) => ({ ...p, topics: e.target.value }))}
            placeholder="machine-learning, web"
          />
        </label>

        <label className="auth-form__field">
          <span>Frameworks (comma-separated)</span>
          <input
            value={prefs.frameworks}
            onChange={(e) => setPrefs((p) => ({ ...p, frameworks: e.target.value }))}
            placeholder="React, FastAPI"
          />
        </label>

        <button type="submit" className="btn btn--primary" disabled={saving}>
          <Save size={14} aria-hidden />
          {saving ? 'Saving…' : 'Save profile'}
        </button>
      </form>
    </section>
  );
}
