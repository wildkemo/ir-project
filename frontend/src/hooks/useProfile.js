import { useCallback, useEffect, useState } from 'react';
import { useAuthStore } from '../stores/authStore';
import { loadProfile, persistProfile } from '../services/profileService';
import { loadStoredProfile } from '../utils/profileStorage';

export function useProfile() {
  const user = useAuthStore((s) => s.user);
  const [profile, setProfile] = useState(() => loadStoredProfile());
  const [loading, setLoading] = useState(Boolean(user));

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const next = await loadProfile({ syncBackend: Boolean(user) });
      setProfile(next);
      return next;
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const saveProfile = useCallback(async (nextProfile) => {
    const saved = await persistProfile(nextProfile);
    setProfile(saved);
    return saved;
  }, []);

  return { profile, loading, refresh, saveProfile };
}
