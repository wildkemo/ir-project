import { useNavigate } from 'react-router-dom';
import AuthLayout from '../../layouts/AuthLayout';
import ProfileWizard from '../../features/auth/ProfileWizard';
import { recommendFromProfile } from '../../services/searchService';
import { useProfile } from '../../hooks/useProfile';
import './AuthPage.css';
import './OnboardingPage.css';

export default function OnboardingPage() {
  const navigate = useNavigate();
  const { saveProfile } = useProfile();

  const handleComplete = async (answers) => {
    await saveProfile(answers);
    try {
      await recommendFromProfile({ ...answers, top_k: 10 });
    } catch {
      // non-blocking
    }
    navigate('/dashboard', { replace: true });
  };

  const handleSkip = () => {
    navigate('/dashboard', { replace: true });
  };

  return (
    <AuthLayout>
      <div className="onboarding-card">
        <div className="onboarding-card__intro">
          <span className="onboarding-card__badge">Almost there!</span>
          <h1 className="onboarding-card__title">Set up your profile</h1>
          <p className="onboarding-card__desc">
            Answer a few quick questions so RepoMind AI can personalise your discovery experience.
          </p>
        </div>
        <ProfileWizard onComplete={handleComplete} onSkip={handleSkip} />
      </div>
    </AuthLayout>
  );
}
