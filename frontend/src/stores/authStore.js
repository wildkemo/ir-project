import { create } from 'zustand';
import * as authService from '../services/authService';
import { loadProfile } from '../services/profileService';
import { loadAccessToken, loadUser, clearAuthStorage } from '../utils/authStorage';

export const useAuthStore = create((set, get) => ({
  user: loadUser(),
  loading: Boolean(loadAccessToken()),
  error: null,

  get isAuthenticated() {
    return Boolean(get().user && loadAccessToken());
  },

  async init() {
    if (!loadAccessToken()) {
      set({ loading: false });
      return;
    }
    try {
      const user = await authService.getMe();
      await loadProfile({ syncBackend: true });
      set({ user, loading: false, error: null });
    } catch {
      clearAuthStorage();
      set({ user: null, loading: false, error: null });
    }
  },

  async login(credentials) {
    set({ error: null });
    await authService.login(credentials);
    const user = await authService.getMe();
    await loadProfile({ syncBackend: true });
    set({ user, error: null });
    return user;
  },

  async register(payload) {
    set({ error: null });
    await authService.register(payload);
    await authService.login({ email: payload.email, password: payload.password });
    const user = await authService.getMe();
    set({ user, error: null });
    return user;
  },

  async logout() {
    await authService.logout();
    set({ user: null, error: null });
  },

  async refreshUser() {
    try {
      const user = await authService.getMe();
      set({ user, error: null });
      return user;
    } catch {
      set({ user: null });
      return null;
    }
  },

  setError(error) { set({ error }); },
  clearError()    { set({ error: null }); },
}));
