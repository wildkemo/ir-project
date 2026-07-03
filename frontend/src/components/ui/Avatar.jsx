import './Avatar.css';

const SIZE_MAP = { xs: 24, sm: 32, md: 40, lg: 56, xl: 80 };

export default function Avatar({ user, size = 'md', className = '' }) {
  const px = SIZE_MAP[size] ?? SIZE_MAP.md;
  const initials = user
    ? (user.username ?? user.email ?? '?')
        .slice(0, 2)
        .toUpperCase()
    : '?';

  return (
    <div
      className={`avatar avatar--${size} ${className}`}
      style={{ width: px, height: px, fontSize: px * 0.38 }}
      aria-label={user?.username ?? 'User avatar'}
    >
      {user?.avatar ? (
        <img src={user.avatar} alt={initials} className="avatar__img" />
      ) : (
        <span className="avatar__initials">{initials}</span>
      )}
    </div>
  );
}
