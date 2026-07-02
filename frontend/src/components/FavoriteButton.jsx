import { useEffect, useState } from 'react';
import { Heart } from 'lucide-react';
import { addFavorite, getApiErrorMessage, getFavorites, removeFavorite } from '../api/auth';
import { useAuth } from '../context/AuthContext';

export default function FavoriteButton({ repoIdentifier }) {
  const { isAuthenticated } = useAuth();
  const [isFavorite, setIsFavorite] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isAuthenticated || !repoIdentifier) return;

    getFavorites()
      .then((items) => {
        setIsFavorite(items.some((item) => item.repo_identifier === repoIdentifier));
      })
      .catch(() => {});
  }, [isAuthenticated, repoIdentifier]);

  if (!isAuthenticated || !repoIdentifier) return null;

  const toggle = async () => {
    setLoading(true);
    try {
      if (isFavorite) {
        await removeFavorite(repoIdentifier);
        setIsFavorite(false);
      } else {
        await addFavorite(repoIdentifier);
        setIsFavorite(true);
      }
    } catch (err) {
      console.error(getApiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      type="button"
      className={`btn btn--ghost btn--sm favorite-btn ${isFavorite ? 'favorite-btn--active' : ''}`}
      onClick={toggle}
      disabled={loading}
      aria-pressed={isFavorite}
      title={isFavorite ? 'Remove from favorites' : 'Save to favorites'}
    >
      <Heart size={14} aria-hidden fill={isFavorite ? 'currentColor' : 'none'} />
      {isFavorite ? 'Saved' : 'Save'}
    </button>
  );
}
