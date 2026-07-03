import { getUserPreferences, updateUserPreferences } from './authService';
import { loadStoredProfile, saveStoredProfile } from '../utils/profileStorage';
import { loadAccessToken } from '../utils/authStorage';

/** Map wizard/session profile → backend preferences payload. */
export function profileToPreferences(profile) {
  if (!profile) return {};
  const language = profile.language && profile.language !== 'any' ? profile.language : null;
  return {
    experience_level: profile.level ?? profile.experience_level ?? null,
    project_type: profile.project_type ?? null,
    goal: profile.goal ?? null,
    repo_kind: profile.repo_kind ?? null,
    complexity: profile.complexity ?? null,
    languages: language ? [language] : [],
    topics: profile.topics ?? [],
    frameworks: profile.frameworks ?? [],
    preferred_license: profile.preferred_license ?? null,
  };
}

/** Map backend preferences → wizard/session profile. */
export function preferencesToProfile(prefs) {
  if (!prefs) return null;
  const hasValues = [
    prefs.experience_level,
    prefs.project_type,
    prefs.goal,
    prefs.complexity,
    prefs.repo_kind,
    ...(prefs.languages ?? []),
  ].some(Boolean);
  if (!hasValues) return null;

  const language = prefs.languages?.[0] ?? 'any';
  return {
    level: prefs.experience_level ?? null,
    project_type: prefs.project_type ?? null,
    goal: prefs.goal ?? null,
    repo_kind: prefs.repo_kind ?? null,
    complexity: prefs.complexity ?? null,
    language: language || 'any',
    topics: prefs.topics ?? [],
    frameworks: prefs.frameworks ?? [],
    preferred_license: prefs.preferred_license ?? null,
  };
}

/** Load profile from sessionStorage, optionally hydrating from the API. */
export async function loadProfile({ syncBackend = false } = {}) {
  const cached = loadStoredProfile();
  if (!syncBackend || !loadAccessToken()) return cached;

  try {
    const prefs = await getUserPreferences();
    const fromApi = preferencesToProfile(prefs);
    if (fromApi) {
      saveStoredProfile(fromApi);
      return fromApi;
    }
  } catch {
    // fall back to session cache
  }
  return cached;
}

/** Persist profile to sessionStorage and backend (when authenticated). */
export async function persistProfile(profile) {
  saveStoredProfile(profile);
  if (!loadAccessToken()) return profile;

  try {
    await updateUserPreferences(profileToPreferences(profile));
  } catch {
    // session copy is still saved for anonymous-style flows
  }
  return profile;
}
