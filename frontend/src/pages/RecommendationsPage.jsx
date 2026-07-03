import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Sparkles, Settings2 } from 'lucide-react';
import { recommend, recommendFromProfile } from '../services/searchService';
import { filterReposOnly } from '../utils/repoDisplay';
import { useProfile } from '../hooks/useProfile';
import { getErrorMessage } from '../services/api';
import RepoCard from '../features/search/RepoCard';
import ProfileWizard from '../features/auth/ProfileWizard';
import { SkeletonCard } from '../components/ui/Skeleton';
import EmptyState from '../components/ui/EmptyState';
import Button from '../components/ui/Button';
import './RecommendationsPage.css';

export default function RecommendationsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { profile, saveProfile } = useProfile();

  const seedRepo = location.state?.repo;

  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showWizard, setShowWizard] = useState(false);

  const load = async (prof = profile) => {
    setLoading(true);
    setError(null);
    try {
      let data;
      if (seedRepo) {
        data = await recommend({ repo_identifier: seedRepo.full_name ?? seedRepo.title, top_k: 12 });
      } else if (prof) {
        data = await recommendFromProfile({ ...prof, top_k: 12 });
      }
      setResults(filterReposOnly(data?.results ?? []));
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleWizardComplete = async (answers) => {
    await saveProfile(answers);
    setShowWizard(false);
    await load(answers);
  };

  return (
    <div className="recommendations-page page-enter">
      <div className="page-header">
        <Sparkles size={20} className="page-header__icon page-header__icon--rec" />
        <div>
          <h1 className="page-header__title">
            {seedRepo ? `Similar to ${seedRepo.full_name?.split('/')[1] ?? 'this repo'}` : 'Recommendations'}
          </h1>
          <p className="page-header__subtitle">
            {seedRepo
              ? 'Semantically similar repositories based on vector embeddings.'
              : 'Personalised recommendations based on your developer profile.'}
          </p>
        </div>
        <Button
          variant="ghost"
          size="sm"
          icon={<Settings2 size={15} />}
          onClick={() => setShowWizard((v) => !v)}
        >
          {showWizard ? 'Hide' : 'Update profile'}
        </Button>
      </div>

      {showWizard && (
        <div className="recommendations-page__wizard">
          <ProfileWizard onComplete={handleWizardComplete} onSkip={() => setShowWizard(false)} initialAnswers={profile ?? {}} />
        </div>
      )}

      {!profile && !seedRepo && !showWizard && (
        <div className="recommendations-page__no-profile">
          <Sparkles size={24} />
          <div>
            <h3>Set up your profile for personalised recommendations</h3>
            <p>Tell us your goals, language preferences, and experience level.</p>
          </div>
          <Button variant="primary" onClick={() => setShowWizard(true)}>Set up profile</Button>
        </div>
      )}

      {loading && (
        <div className="recommendations-page__grid">
          {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      )}

      {error && <div className="page-error">{error}</div>}

      {!loading && results.length === 0 && (profile || seedRepo) && !error && (
        <EmptyState
          icon={<Sparkles size={28} />}
          title="No recommendations yet"
          description="Try updating your profile or searching for a seed repository."
        />
      )}

      {!loading && results.length > 0 && (
        <>
          <p className="recommendations-page__count">{results.length} repositories found</p>
          <div className="recommendations-page__grid">
            {results.map((repo) => (
              <RepoCard
                key={repo.full_name ?? repo.title}
                repo={repo}
                mode="profile"
                onExplain={(r) => navigate('/advisor', { state: { repo: r } })}
                onRoadmap={(r) => navigate('/roadmap',  { state: { repo: r } })}
                onSimilar={(r) => navigate('/recommendations', { state: { repo: r } })}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
