import { useState } from 'react';
import { User, Save, AlertCircle } from 'lucide-react';
import { useAuthStore } from '../stores/authStore';
import { updateProfile } from '../services/authService';
import { getErrorMessage } from '../services/api';
import { useToast } from '../context/ToastContext';
import Avatar from '../components/ui/Avatar';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import ProfileWizard from '../features/auth/ProfileWizard';
import { useProfile } from '../hooks/useProfile';
import './ProfilePage.css';

export default function ProfilePage() {
  const { user, refreshUser } = useAuthStore();
  const { success, error: toastError } = useToast();
  const { profile, saveProfile } = useProfile();

  const [form, setForm] = useState({
    username: user?.username ?? '',
    bio: user?.bio ?? '',
  });
  const [saving, setSaving] = useState(false);
  const [showWizard, setShowWizard] = useState(false);

  const set = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }));

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await updateProfile(form);
      await refreshUser();
      success('Profile updated successfully!');
    } catch (err) {
      toastError(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const handleWizardComplete = async (answers) => {
    await saveProfile(answers);
    setShowWizard(false);
    success('Developer profile updated!');
  };

  return (
    <div className="profile-page page-enter">
      <div className="page-header">
        <User size={20} className="page-header__icon page-header__icon--search" />
        <div>
          <h1 className="page-header__title">Profile</h1>
          <p className="page-header__subtitle">Manage your account information and developer preferences</p>
        </div>
      </div>

      <div className="profile-page__grid">
        {/* Account info */}
        <section className="profile-section">
          <h2 className="profile-section__title">Account</h2>

          <div className="profile-section__avatar-row">
            <Avatar user={user} size="lg" />
            <div>
              <p className="profile-section__avatar-name">{user?.username}</p>
              <p className="profile-section__avatar-email">{user?.email}</p>
              <span className="profile-section__role-badge">{user?.role?.name ?? user?.role ?? 'user'}</span>
            </div>
          </div>

          <form className="profile-form" onSubmit={handleSave}>
            <Input
              label="Username"
              value={form.username}
              onChange={set('username')}
              placeholder="your-username"
            />
            <Input
              label="Bio"
              value={form.bio}
              onChange={set('bio')}
              placeholder="Tell us a little about yourself…"
              textarea
              rows={3}
            />
            <Button type="submit" variant="primary" loading={saving} icon={<Save size={15} />}>
              Save changes
            </Button>
          </form>
        </section>

        {/* Developer profile */}
        <section className="profile-section">
          <div className="profile-section__header-row">
            <h2 className="profile-section__title">Developer Profile</h2>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowWizard((v) => !v)}
            >
              {showWizard ? 'Cancel' : profile ? 'Edit' : 'Set up'}
            </Button>
          </div>

          {!showWizard && profile && (
            <div className="profile-section__profile-summary">
              {Object.entries(profile).map(([key, value]) => (
                value && (
                  <div key={key} className="profile-summary__item">
                    <span className="profile-summary__key">{key.replace(/_/g, ' ')}</span>
                    <span className="profile-summary__value">{String(value)}</span>
                  </div>
                )
              ))}
            </div>
          )}

          {!showWizard && !profile && (
            <div className="profile-section__no-profile">
              <AlertCircle size={18} />
              <div>
                <p className="profile-section__no-profile-title">Profile not configured</p>
                <p className="profile-section__no-profile-desc">
                  Set up your developer profile to get personalised recommendations.
                </p>
              </div>
            </div>
          )}

          {showWizard && (
            <div className="profile-section__wizard">
              <ProfileWizard
                onComplete={handleWizardComplete}
                onSkip={() => setShowWizard(false)}
                initialAnswers={profile ?? {}}
              />
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
