/** Only real GitHub owner/repo pages — not /topics/ or /sponsors/ URLs. */
export function isGitHubRepo(repo) {
  const url = (repo?.url || '').toLowerCase();
  const fullName = (repo?.full_name || '').toLowerCase();

  if (url.includes('/topics/') || fullName.startsWith('topics/')) return false;
  if (url.includes('/sponsors/') || fullName.startsWith('sponsors/')) return false;

  const match = url.match(/github\.com\/([^/?#]+\/[^/?#]+)/i);
  if (match) {
    const owner = match[1].split('/')[0].toLowerCase();
    if (owner === 'topics' || owner === 'sponsors') return false;
    return true;
  }

  return Boolean(fullName && fullName.includes('/') && !fullName.startsWith('topics/'));
}

/** Display name: owner/repo (e.g. Datalux/Osintgram), never topics/foo. */
export function getRepoDisplayName(repo) {
  const fullName = repo?.full_name;
  if (fullName) {
    const lower = fullName.toLowerCase();
    if (!lower.startsWith('topics/') && !lower.startsWith('sponsors/') && fullName.includes('/')) {
      return fullName;
    }
  }

  const match = repo?.url?.match(/github\.com\/([^/?#]+\/[^/?#]+)/i);
  if (match) {
    const owner = match[1].split('/')[0].toLowerCase();
    if (owner !== 'topics' && owner !== 'sponsors') {
      return match[1];
    }
  }

  return repo?.title || 'Unknown repository';
}

export function filterReposOnly(list) {
  return (Array.isArray(list) ? list : []).filter(isGitHubRepo);
}
