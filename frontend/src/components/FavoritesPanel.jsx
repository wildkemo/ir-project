import { useEffect, useState } from 'react';
import { Heart, Trash2 } from 'lucide-react';
import { addFavorite, getApiErrorMessage, getFavorites, removeFavorite } from '../api/auth';

export default function FavoritesPanel() {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [repoInput, setRepoInput] = useState('');

  const loadFavorites = () => {
    setLoading(true);
    getFavorites()
      .then(setFavorites)
      .catch((err) => setError(getApiErrorMessage(err)))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadFavorites();
  }, []);

  const handleAdd = async (event) => {
    event.preventDefault();
    if (!repoInput.trim()) return;

    try {
      await addFavorite(repoInput.trim());
      setRepoInput('');
      loadFavorites();
    } catch (err) {
      setError(getApiErrorMessage(err));
    }
  };

  const handleRemove = async (repoIdentifier) => {
    try {
      await removeFavorite(repoIdentifier);
      setFavorites((prev) => prev.filter((f) => f.repo_identifier !== repoIdentifier));
    } catch (err) {
      setError(getApiErrorMessage(err));
    }
  };

  return (
    <section className="user-panel">
      <header className="user-panel__header">
        <Heart size={22} aria-hidden />
        <div>
          <h2>Favorites</h2>
          <p className="user-panel__meta">Saved repository identifiers only — no duplicated metadata.</p>
        </div>
      </header>

      {error && (
        <div className="alert alert--error" role="alert">
          {error}
        </div>
      )}

      <form className="favorites-add" onSubmit={handleAdd}>
        <input
          value={repoInput}
          onChange={(e) => setRepoInput(e.target.value)}
          placeholder="owner/repository"
          aria-label="Repository identifier"
        />
        <button type="submit" className="btn btn--secondary btn--sm">
          Add
        </button>
      </form>

      {loading && <p className="panel-note">Loading favorites…</p>}

      {!loading && favorites.length === 0 && (
        <p className="panel-note">No favorites yet. Save repos from search results or add one above.</p>
      )}

      <ul className="history-list">
        {favorites.map((item) => (
          <li key={item.id} className="history-list__item">
            <div>
              <strong>{item.repo_identifier}</strong>
              <span className="history-list__meta">
                {new Date(item.created_at).toLocaleString()}
              </span>
            </div>
            <button
              type="button"
              className="btn btn--ghost btn--sm"
              onClick={() => handleRemove(item.repo_identifier)}
              aria-label={`Remove ${item.repo_identifier}`}
            >
              <Trash2 size={14} aria-hidden />
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
