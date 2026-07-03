import { useEffect, useState } from 'react';
import { Users, Search } from 'lucide-react';
import { getAdminUsers } from '../../services/adminService';
import { getErrorMessage } from '../../services/api';
import { formatDate } from '../../utils/format';
import { formatRoleLabel } from '../../utils/userRole';
import { SkeletonText } from '../../components/ui/Skeleton';
import EmptyState from '../../components/ui/EmptyState';
import './AdminPage.css';

export default function AdminUsersPage() {
  const [users, setUsers]   = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState(null);
  const [query, setQuery]   = useState('');

  useEffect(() => {
    getAdminUsers(100)
      .then((data) => setUsers(data?.users ?? []))
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  const filtered = users.filter(
    (u) =>
      !query ||
      u.username?.toLowerCase().includes(query.toLowerCase()) ||
      u.email?.toLowerCase().includes(query.toLowerCase()),
  );

  return (
    <div className="admin-page page-enter">
      <div className="admin-page__header">
        <h1 className="admin-page__title">Users</h1>
        <p className="admin-page__subtitle">Manage platform users and their roles.</p>
      </div>

      <div className="admin-search-wrap">
        <Search size={15} className="admin-search-icon" />
        <input
          className="admin-search-input"
          type="text"
          placeholder="Search users by name or email…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>

      {loading && <SkeletonText lines={8} />}
      {error && <div className="admin-page__notice">{error}</div>}

      {!loading && !error && filtered.length === 0 && (
        <EmptyState icon={<Users size={28} />} title="No users found" description="Try a different search." />
      )}

      {!loading && !error && filtered.length > 0 && (
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>User</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Joined</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((u) => (
                <tr key={u.id}>
                  <td className="admin-table__user">
                    <div className="admin-table__avatar">{u.username?.[0]?.toUpperCase()}</div>
                    <span>{u.username}</span>
                  </td>
                  <td>{u.email}</td>
                  <td>
                    <span className={`admin-badge admin-badge--${formatRoleLabel(u) === 'Admin' ? 'ai' : 'default'}`}>
                      {formatRoleLabel(u)}
                    </span>
                  </td>
                  <td>
                    <span className={`admin-badge admin-badge--${u.is_active !== false ? 'success' : 'error'}`}>
                      {u.is_active !== false ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="admin-table__date">{formatDate(u.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
