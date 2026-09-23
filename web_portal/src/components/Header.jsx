import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useApp } from '../context/AppContext';

const Header = ({ onToggleMobileMenu }) => {
  const { currentUser, activeRoleView, switchRoleView, logout } = useApp();
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  const handleRoleClick = (role) => {
    switchRoleView(role);
    if (role === 'student') navigate('/dashboard');
    else if (role === 'trainer') navigate('/trainer');
    else if (role === 'admin') navigate('/admin');
  };

  return (
    <header className="fixed top-0 left-0 lg:left-72 right-0 h-16 bg-surface-container-lowest/90 backdrop-blur-xl border-b border-surface-variant z-40 flex items-center justify-between px-4 lg:px-6 shadow-[0_1px_8px_rgba(0,0,0,0.04)]">
      {/* Left: Mobile burger & Greeting / Breadcrumb */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onToggleMobileMenu}
          className="lg:hidden p-2 rounded-lg text-on-surface-variant hover:bg-surface-container-low transition-colors"
          aria-label="Toggle navigation menu"
        >
          <span className="material-symbols-outlined text-[24px]">menu</span>
        </button>

        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className="font-headline-sm text-headline-sm text-on-surface font-semibold truncate">
              {currentUser?.role === 'student' && `Good morning, ${currentUser?.name?.split(' ')[0] || 'Aarav'}`}
              {currentUser?.role === 'trainer' && `Evaluation Desk · ${currentUser?.name}`}
              {currentUser?.role === 'admin' && `Institutional Governance Hub`}
            </span>
            <span className="hidden sm:inline-flex items-center px-2 py-0.5 rounded-lg bg-surface-container font-label-sm text-label-sm text-secondary">
              {currentUser?.cohort || 'AY 2024–25'}
            </span>
          </div>
          <span className="font-body-sm text-body-sm text-on-surface-variant hidden md:block">
            {currentUser?.role === 'student' && 'Placement Preparation Practicum · Week 4 of 15'}
            {currentUser?.role === 'trainer' && 'Batch 2025 · Cohort B (Data & Analytics) · 64 Candidates'}
            {currentUser?.role === 'admin' && 'Continuous Assessment & Compliance Governance'}
          </span>
        </div>
      </div>

      {/* Right Controls: Search, Role View Switcher, Notifications, Profile */}
      <div className="flex items-center gap-2 sm:gap-4">
        {/* Search Box */}
        <div className="relative hidden xl:flex items-center w-64">
          <span className="material-symbols-outlined absolute left-3 text-[18px] text-outline pointer-events-none">
            search
          </span>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search modules, rubrics, students..."
            className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-surface-container-low font-body-sm text-body-sm text-on-surface placeholder:text-outline focus:bg-surface-container-lowest focus:outline-none focus:ring-1 focus:ring-primary transition-all"
          />
        </div>

        {/* Role View Switcher Pill */}
        <div className="hidden sm:flex items-center rounded-lg bg-surface-container p-1 gap-1 border border-surface-variant">
          <button
            type="button"
            onClick={() => handleRoleClick('student')}
            className={`px-2.5 py-1 rounded text-label-sm font-label-sm transition-all ${
              currentUser?.role === 'student'
                ? 'bg-primary text-on-primary font-semibold shadow-sm'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low'
            }`}
          >
            Student View
          </button>
          <button
            type="button"
            onClick={() => handleRoleClick('trainer')}
            className={`px-2.5 py-1 rounded text-label-sm font-label-sm transition-all ${
              currentUser?.role === 'trainer'
                ? 'bg-primary text-on-primary font-semibold shadow-sm'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low'
            }`}
          >
            Trainer View
          </button>
          <button
            type="button"
            onClick={() => handleRoleClick('admin')}
            className={`px-2.5 py-1 rounded text-label-sm font-label-sm transition-all ${
              currentUser?.role === 'admin'
                ? 'bg-primary text-on-primary font-semibold shadow-sm'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low'
            }`}
          >
            Admin View
          </button>
        </div>

        {/* Notification Bell with Dropdown */}
        <div className="relative">
          <button
            type="button"
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 rounded-lg text-on-surface-variant hover:bg-surface-container-low hover:text-on-surface transition-colors"
            aria-label="Notifications"
          >
            <span className="material-symbols-outlined text-[22px]">notifications</span>
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-error ring-2 ring-surface-container-lowest"></span>
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-xl bg-surface-container-lowest border border-outline-variant/50 shadow-lg py-3 px-4 z-50 animate-in fade-in slide-in-from-top-2">
              <div className="flex items-center justify-between pb-2 border-b border-surface-variant">
                <span className="font-title-sm text-title-sm text-on-surface font-semibold">Notifications</span>
                <span className="font-label-sm text-label-sm text-tertiary font-medium bg-tertiary-fixed/40 px-2 py-0.5 rounded">3 New</span>
              </div>
              <div className="divide-y divide-surface-variant max-h-72 overflow-y-auto py-1">
                <div className="py-2.5 flex items-start gap-3">
                  <span className="material-symbols-outlined text-primary text-[20px] mt-0.5">announcement</span>
                  <div>
                    <p className="font-label-md text-label-md text-on-surface font-medium">CA1 Window Locks in 4 Days</p>
                    <p className="font-body-sm text-body-sm text-on-surface-variant">Upload single-column resume format before Sep 24, 11:59 PM.</p>
                  </div>
                </div>
                <div className="py-2.5 flex items-start gap-3">
                  <span className="material-symbols-outlined text-tertiary text-[20px] mt-0.5">verified</span>
                  <div>
                    <p className="font-label-md text-label-md text-on-surface font-medium">Diagnostic Report Ready</p>
                    <p className="font-body-sm text-body-sm text-on-surface-variant">Your latest resume scored 76/100 against Data Analyst JD.</p>
                  </div>
                </div>
                <div className="py-2.5 flex items-start gap-3">
                  <span className="material-symbols-outlined text-secondary text-[20px] mt-0.5">event</span>
                  <div>
                    <p className="font-label-md text-label-md text-on-surface font-medium">Live Q&A Tomorrow at 4:00 PM</p>
                    <p className="font-body-sm text-body-sm text-on-surface-variant">MS Teams mentor session on technical project descriptions.</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* User Profile avatar + Popover */}
        <div className="relative">
          <button
            type="button"
            onClick={() => setShowProfileMenu(!showProfileMenu)}
            className="flex items-center gap-2 p-1 rounded-lg hover:bg-surface-container-low transition-colors"
          >
            <img
              src={currentUser?.avatar}
              alt={currentUser?.name}
              className="w-8 h-8 rounded-full object-cover ring-1 ring-outline-variant/60"
            />
            <div className="hidden md:flex flex-col text-left">
              <span className="font-label-md text-label-md text-on-surface leading-tight font-medium">
                {currentUser?.name}
              </span>
              <span className="font-label-sm text-label-sm text-outline capitalize leading-tight">
                {currentUser?.role}
              </span>
            </div>
            <span className="material-symbols-outlined text-[16px] text-outline hidden md:inline">
              expand_more
            </span>
          </button>

          {showProfileMenu && (
            <div className="absolute right-0 mt-2 w-64 rounded-xl bg-surface-container-lowest border border-outline-variant/50 shadow-lg py-2 z-50">
              <div className="px-4 py-2 border-b border-surface-variant">
                <p className="font-title-sm text-title-sm text-on-surface font-semibold">{currentUser?.name}</p>
                <p className="font-body-sm text-body-sm text-on-surface-variant">{currentUser?.email}</p>
                <span className="inline-block mt-1 px-2 py-0.5 rounded bg-surface-container text-primary font-label-sm text-label-sm uppercase font-semibold">
                  {currentUser?.role} Account
                </span>
              </div>
              <div className="py-1">
                <button
                  type="button"
                  onClick={() => {
                    setShowProfileMenu(false);
                    navigate('/privacy');
                  }}
                  className="w-full px-4 py-2 text-left font-body-sm text-body-sm text-on-surface-variant hover:bg-surface-container-low hover:text-on-surface flex items-center gap-2"
                >
                  <span className="material-symbols-outlined text-[18px]">verified_user</span>
                  Privacy & Data Rights
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowProfileMenu(false);
                    navigate('/login');
                  }}
                  className="w-full px-4 py-2 text-left font-body-sm text-body-sm text-on-surface-variant hover:bg-surface-container-low hover:text-on-surface flex items-center gap-2"
                >
                  <span className="material-symbols-outlined text-[18px]">swap_horiz</span>
                  Switch Demo Account
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowProfileMenu(false);
                    logout();
                    navigate('/login');
                  }}
                  className="w-full px-4 py-2 text-left font-body-sm text-body-sm text-error hover:bg-error-container/30 flex items-center gap-2"
                >
                  <span className="material-symbols-outlined text-[18px]">logout</span>
                  Sign Out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
