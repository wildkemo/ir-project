/** Normalize backend role (string or { name }) to a lowercase slug. */
export function getUserRole(user) {
  if (!user?.role) return 'user';
  if (typeof user.role === 'string') return user.role.toLowerCase();
  return user.role.name?.toLowerCase() ?? 'user';
}

export function isAdmin(user) {
  return getUserRole(user) === 'admin';
}

export function formatRoleLabel(user) {
  const role = getUserRole(user);
  return role.charAt(0).toUpperCase() + role.slice(1);
}
