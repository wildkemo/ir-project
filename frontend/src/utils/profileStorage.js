const PROFILE_KEY = 'openseek-profile';

export function loadStoredProfile() {
  try {
    const raw = sessionStorage.getItem(PROFILE_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function saveStoredProfile(profile) {
  sessionStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
}

export function clearStoredProfile() {
  sessionStorage.removeItem(PROFILE_KEY);
}
