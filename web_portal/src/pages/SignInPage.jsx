import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { USERS } from '../data/mockData';

const SignInPage = () => {
  const { login } = useApp();
  const navigate = useNavigate();

  const [selectedRole, setSelectedRole] = useState('student');
  const [selectedAccountKey, setSelectedAccountKey] = useState('student');
  const [email, setEmail] = useState(USERS.student.email);
  const [password, setPassword] = useState('Curriculum2026!');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberDevice, setRememberDevice] = useState(true);
  const [showPolicy, setShowPolicy] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleRoleSelect = (roleKey) => {
    setSelectedRole(roleKey);
    setSelectedAccountKey(roleKey);
    setEmail(USERS[roleKey].email);
    setErrorMessage('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setErrorMessage('');
    setIsLoading(true);

    setTimeout(() => {
      try {
        // Authenticate with claimed role vs demo account key
        const authenticatedUser = login(selectedAccountKey, selectedRole);
        setIsLoading(false);

        // Route to the appropriate dashboard based on authenticated role
        if (authenticatedUser.role === 'student') {
          navigate('/dashboard');
        } else if (authenticatedUser.role === 'trainer') {
          navigate('/trainer');
        } else if (authenticatedUser.role === 'admin') {
          navigate('/admin');
        }
      } catch (err) {
        setIsLoading(false);
        setErrorMessage(err.message || 'Authentication failed. Please check credentials.');
      }
    }, 600);
  };

  return (
    <div className="w-full min-h-screen bg-surface flex flex-col justify-between">
      <div className="w-full min-h-[calc(100vh-2rem)] flex items-center justify-center p-4 md:p-8 lg:p-12">
        <div className="w-full max-w-[1240px] grid grid-cols-1 lg:grid-cols-12 rounded-xl bg-surface-container-lowest shadow-md overflow-hidden min-h-[680px] border border-surface-variant">
          
          {/* Left Editorial Panel */}
          <aside className="lg:col-span-5 bg-surface-container-low p-8 lg:p-12 flex flex-col justify-between relative overflow-hidden">
            <div className="space-y-8 relative z-10">
              {/* Brand and Cohort Marker */}
              <div className="space-y-3">
                <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-secondary-container/40 text-on-secondary-container">
                  <span className="material-symbols-outlined text-[16px] text-primary">school</span>
                  <span className="font-label-sm text-label-sm uppercase tracking-wider font-semibold">
                    PPS4027 Placement Portal
                  </span>
                </div>
                <p className="font-label-sm text-label-sm text-outline tracking-wide uppercase">
                  Academic Year 2024–25 • 15-Week Career Practicum
                </p>
              </div>

              {/* Editorial Headline and Narrative */}
              <div className="space-y-4">
                <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight leading-tight font-bold">
                  Prepare, practise, progress.
                </h1>
                <p className="font-body-md text-body-md text-on-surface-variant max-w-sm leading-relaxed">
                  An integrated 15-week placement preparation curriculum benchmarked against industry role standards, single-column ATS diagnostics, and rigorous faculty review.
                </p>
              </div>

              {/* Editorial Document Vignette */}
              <div className="p-4 bg-surface-container-lowest rounded-lg shadow-sm space-y-3 max-w-md border border-surface-variant/50">
                <div className="flex items-center justify-between pb-2">
                  <span className="font-label-sm text-label-sm text-tertiary font-semibold flex items-center gap-1.5">
                    <span className="material-symbols-outlined text-[15px]">verified</span>
                    Continuous Assessment & Coaching Desk
                  </span>
                  <span className="font-label-sm text-label-sm text-outline">Ref: AY24-Syllabus</span>
                </div>
                
                <div className="overflow-hidden rounded bg-surface-container p-3 flex items-center gap-3">
                  <div className="w-10 h-10 rounded bg-primary/10 flex items-center justify-center text-primary shrink-0">
                    <span className="material-symbols-outlined text-[22px]">description</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="font-label-md text-label-md text-on-surface font-semibold">Resume Diagnostic Spec v3.2</span>
                    <span className="font-body-sm text-body-sm text-outline">Single-Column Parse Verification</span>
                  </div>
                </div>

                <div className="flex items-center justify-between text-outline text-label-sm font-label-sm pt-1">
                  <span>Section 4: Technical Dossier</span>
                  <span className="text-tertiary font-medium">92% Baseline Met</span>
                </div>
              </div>
            </div>

            {/* Institutional Trust Micro-footer */}
            <div className="pt-8 relative z-10">
              <div className="h-[1px] w-12 bg-outline-variant mb-4"></div>
              <p className="font-body-sm text-body-sm text-outline leading-relaxed max-w-sm">
                Verified institutional access for registered candidates, faculty mentors, and academic governance.
              </p>
            </div>

            {/* Ambient decorative geometry */}
            <div className="absolute -bottom-16 -left-16 w-64 h-64 rounded-full bg-primary/5 pointer-events-none"></div>
          </aside>

          {/* Right Login Card Panel */}
          <section className="lg:col-span-7 bg-surface-container-lowest p-8 lg:p-14 flex flex-col justify-between">
            <div className="max-w-xl w-full mx-auto space-y-6">
              
              {/* Header block */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <h2 className="font-headline-md text-headline-md text-on-surface font-bold">
                    Welcome back
                  </h2>
                  <span className="font-label-sm text-label-sm px-2.5 py-0.5 rounded bg-surface-container text-on-surface-variant font-medium">
                    {selectedRole === 'student' ? 'Candidate Access' : selectedRole === 'trainer' ? 'Evaluator Access' : 'Governance Root'}
                  </span>
                </div>
                <p className="font-body-md text-body-md text-on-surface-variant">
                  Sign in to continue your placement-training journey.
                </p>
              </div>

              {/* Academic Notice Banner */}
              <div className="p-3.5 rounded-lg bg-surface-container-low flex items-start gap-3 border border-surface-variant/40">
                <span className="material-symbols-outlined text-secondary text-[20px] shrink-0 mt-0.5">
                  announcement
                </span>
                <div className="space-y-0.5">
                  <p className="font-label-md text-label-md text-on-surface font-medium">Notice for Cohort Candidates</p>
                  <p className="font-body-sm text-body-sm text-on-surface-variant">
                    AY 2024–25 Continuous Assessment CA1 locking soon. Ensure you authenticate with your designated university address.
                  </p>
                </div>
              </div>

              {/* Role Context Selector */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">
                    Select Demo Role Context
                  </label>
                  <span className="font-label-sm text-label-sm text-outline">
                    {selectedRole === 'student' && 'Student → Student Dashboard'}
                    {selectedRole === 'trainer' && 'Trainer → Evaluation Desk'}
                    {selectedRole === 'admin' && 'Admin → Governance Hub'}
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-1.5 p-1 rounded-lg bg-surface-container">
                  <button
                    type="button"
                    onClick={() => handleRoleSelect('student')}
                    className={`py-2 px-3 rounded text-center font-label-md text-label-md transition-colors duration-150 ${
                      selectedRole === 'student'
                        ? 'bg-primary-container text-on-primary font-semibold shadow-sm'
                        : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-lowest'
                    }`}
                  >
                    Student
                  </button>
                  <button
                    type="button"
                    onClick={() => handleRoleSelect('trainer')}
                    className={`py-2 px-3 rounded text-center font-label-md text-label-md transition-colors duration-150 ${
                      selectedRole === 'trainer'
                        ? 'bg-primary-container text-on-primary font-semibold shadow-sm'
                        : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-lowest'
                    }`}
                  >
                    Trainer
                  </button>
                  <button
                    type="button"
                    onClick={() => handleRoleSelect('admin')}
                    className={`py-2 px-3 rounded text-center font-label-md text-label-md transition-colors duration-150 ${
                      selectedRole === 'admin'
                        ? 'bg-primary-container text-on-primary font-semibold shadow-sm'
                        : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-lowest'
                    }`}
                  >
                    Admin
                  </button>
                </div>
              </div>

              {/* Error Message if Role Mismatch or Auth Failure */}
              {errorMessage && (
                <div className="p-3 rounded-lg bg-error-container text-on-error-container border border-error/20 flex items-center gap-2.5 animate-in fade-in">
                  <span className="material-symbols-outlined text-[20px] text-error">gpp_bad</span>
                  <span className="font-body-sm text-body-sm font-medium">{errorMessage}</span>
                </div>
              )}

              {/* Sign-In Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Email Field */}
                <div className="space-y-1.5">
                  <label className="font-label-sm text-label-sm text-on-surface font-medium block">
                    Institutional Email Address
                  </label>
                  <div className="relative">
                    <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[18px]">
                      alternate_email
                    </span>
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="e.g. aarav@example.edu"
                      className="w-full pl-10 pr-4 py-2.5 rounded bg-surface-container-lowest border border-outline-variant/60 font-body-md text-body-md text-on-surface placeholder:text-outline/70 focus:outline-none focus:border-primary shadow-sm"
                    />
                  </div>
                </div>

                {/* Password Field */}
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <label className="font-label-sm text-label-sm text-on-surface font-medium block">
                      Password
                    </label>
                    <button
                      type="button"
                      onClick={() => setShowPolicy(!showPolicy)}
                      className="font-body-sm text-body-sm text-secondary hover:text-primary transition-colors"
                    >
                      Forgot password?
                    </button>
                  </div>
                  <div className="relative">
                    <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[18px]">
                      lock
                    </span>
                    <input
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••••••"
                      className="w-full pl-10 pr-10 py-2.5 rounded bg-surface-container-lowest border border-outline-variant/60 font-body-md text-body-md text-on-surface placeholder:text-outline/70 focus:outline-none focus:border-primary shadow-sm"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      aria-label="Toggle password visibility"
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-outline hover:text-on-surface"
                    >
                      <span className="material-symbols-outlined text-[18px]">
                        {showPassword ? 'visibility_off' : 'visibility'}
                      </span>
                    </button>
                  </div>
                </div>

                {/* Auxiliary Row */}
                <div className="flex items-center justify-between pt-1">
                  <label className="inline-flex items-center gap-2 cursor-pointer select-none">
                    <input
                      type="checkbox"
                      checked={rememberDevice}
                      onChange={(e) => setRememberDevice(e.target.checked)}
                      className="w-4 h-4 rounded text-primary bg-surface-container focus:ring-0 cursor-pointer"
                    />
                    <span className="font-body-sm text-body-sm text-on-surface-variant">Remember device for 30 days</span>
                  </label>
                  <button
                    type="button"
                    onClick={() => setShowPolicy(!showPolicy)}
                    className="font-body-sm text-body-sm text-outline hover:text-on-surface inline-flex items-center gap-1"
                  >
                    <span className="material-symbols-outlined text-[15px]">shield_person</span>
                    Credential policy
                  </button>
                </div>

                {/* Primary Action Button */}
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full mt-2 py-3 px-4 rounded bg-primary-container text-on-primary hover:bg-primary transition duration-150 font-title-sm text-title-sm flex items-center justify-center gap-2 shadow-sm font-semibold disabled:opacity-75 cursor-pointer"
                >
                  {isLoading ? (
                    <>
                      <span className="material-symbols-outlined animate-spin text-[18px]">sync</span>
                      <span>Authenticating credentials...</span>
                    </>
                  ) : (
                    <>
                      <span>Sign in to Dashboard</span>
                      <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
                    </>
                  )}
                </button>
              </form>

              {/* Collapsible Policy Tray */}
              {showPolicy && (
                <div className="p-3.5 rounded bg-surface-container-low border border-surface-variant/60 space-y-2 animate-in fade-in">
                  <div className="flex items-center justify-between">
                    <span className="font-label-sm text-label-sm font-semibold text-on-surface uppercase tracking-wide">
                      Institutional Directory Policy
                    </span>
                    <button
                      type="button"
                      onClick={() => setShowPolicy(false)}
                      className="text-outline hover:text-on-surface"
                    >
                      <span className="material-symbols-outlined text-[16px]">close</span>
                    </button>
                  </div>
                  <p className="font-body-sm text-body-sm text-on-surface-variant leading-relaxed">
                    Candidate credentials are synchronized with university registrar archives. Active candidates authenticate with student domains (`aarav@example.edu`). Faculty and evaluators require designated faculty permissions.
                  </p>
                </div>
              )}

              {/* Routing & Permission chips */}
              <div className="pt-2 space-y-2 border-t border-surface-variant/60">
                <div className="flex flex-wrap gap-2 text-label-sm font-label-sm text-on-surface-variant">
                  <span className="px-2.5 py-1 rounded bg-surface-container">Student: Portfolio & ATS</span>
                  <span className="px-2.5 py-1 rounded bg-surface-container">Trainer: Rubrics & Evaluation Desk</span>
                  <span className="px-2.5 py-1 rounded bg-surface-container">Admin: Cohort Governance</span>
                </div>
                <p className="font-body-sm text-body-sm text-outline">
                  Your dashboard permissions are verified via backend RBAC token policies.
                </p>
              </div>

            </div>

            {/* Terminal Card Footer */}
            <footer className="pt-6 mt-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-body-sm font-body-sm text-outline border-t border-surface-variant/40">
              <div className="flex items-center gap-4">
                <span className="flex items-center gap-1">
                  <span className="material-symbols-outlined text-[16px]">key</span>
                  Campus SSO Enabled
                </span>
                <span>•</span>
                <span className="text-tertiary flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-tertiary"></span>
                  Server Status: Operational
                </span>
              </div>
              <div className="flex items-center gap-4">
                <button
                  type="button"
                  onClick={() => navigate('/privacy')}
                  className="hover:text-on-surface transition-colors"
                >
                  Privacy Notice
                </button>
                <span>•</span>
                <span>Placement Desk AY 2024–25</span>
              </div>
            </footer>
          </section>

        </div>
      </div>
    </div>
  );
};

export default SignInPage;
