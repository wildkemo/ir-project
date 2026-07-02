import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import {
  fetchCurrentUser,
  getApiErrorMessage,
  loginUser,
  logoutUser,
  registerUser,
} from '../api/auth';
import { loadAccessToken, loadUser, saveUser } from '../utils/authStorage';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => loadUser());
  const [loading, setLoading] = useState(Boolean(loadAccessToken()));
  const [error, setError] = useState(null);

  const refreshUser = useCallback(async () => {
    if (!loadAccessToken()) {
      setUser(null);
      setLoading(false);
      return null;
    }

    try {
      const data = await fetchCurrentUser();
      setUser(data);
      setError(null);
      return data;
    } catch (err) {
      setUser(null);
      setError(getApiErrorMessage(err));
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (loadAccessToken()) {
      refreshUser();
    } else {
      setLoading(false);
    }
  }, [refreshUser]);

  const login = useCallback(async (credentials) => {
    setError(null);
    await loginUser(credentials);
    const data = await fetchCurrentUser();
    setUser(data);
    return data;
  }, []);

  const register = useCallback(async (payload) => {
    setError(null);
    const data = await registerUser(payload);
    saveUser(data);
    setUser(data);
    return data;
  }, []);

  const logout = useCallback(async () => {
    await logoutUser();
    setUser(null);
    setError(null);
  }, []);

  const value = useMemo(
    () => ({
      user,
      loading,
      error,
      isAuthenticated: Boolean(user && loadAccessToken()),
      login,
      register,
      logout,
      refreshUser,
      setError,
    }),
    [user, loading, error, login, register, logout, refreshUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
