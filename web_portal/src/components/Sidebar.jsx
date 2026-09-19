import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';

const Sidebar = ({ isMobileOpen, onCloseMobile }) => {
  const { currentUser } = useApp();
  const navigate = useNavigate();

  const role = currentUser?.role || 'student';

  const studentCurriculumNav = [
    { to: '/dashboard', label: 'Dashboard', icon: 'grid_view' },
    { to: '/resume-review', label: 'Resume Review', icon: 'find_in_page' },
    { to: '/history', label: 'My Progress & History', icon: 'trending_up' },
    { to: '/assignments', label: 'Assignments (CA1-3)', icon: 'assignment' },
    { to: '/learning', label: 'Learning Modules', icon: 'menu_book' },
    { to: '/calendar', label: 'Academic Calendar', icon: 'calendar_today' },
  ];

  const studentSystemNav = [
    { to: '/privacy', label: 'Privacy & Data', icon: 'verified_user' },
    { to: '/notifications', label: 'Cohort Notices', icon: 'notifications' },
  ];

  const trainerNav = [
    { to: '/trainer', label: 'Submissions & Grading', icon: 'assignment_turned_in' },
    { to: '/trainer/directory', label: 'Student Directory & ATS', icon: 'school' },
    { to: '/trainer/rubrics', label: 'Rubrics & Scoring Keys', icon: 'rule' },
    { to: '/trainer/mentorship', label: 'Live Mentorship Desk', icon: 'support_agent' },
  ];

  const adminNav = [
    { to: '/admin', label: 'System Governance', icon: 'account_balance' },
    { to: '/admin/directory', label: 'User Directory & Roles', icon: 'badge' },
    { to: '/admin/audit', label: 'Audit & Forensic Logs', icon: 'history_edu' },
    { to: '/admin/policies', label: 'Data Retention & Policy', icon: 'policy' },
    { to: '/admin/engine', label: 'ATS Engine Weights', icon: 'tune' },
  ];

  const getNavClass = ({ isActive }) =>
    `flex items-center gap-3 px-3 py-2 rounded-lg font-label-md text-label-md transition-colors ${
      isActive
        ? 'bg-secondary-container text-on-secondary-container font-semibold shadow-sm'
        : 'text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface'
    }`;

  return (
    <>
      {/* Mobile Backdrop */}
      {isMobileOpen && (
        <div
          onClick={onCloseMobile}
          className="fixed inset-0 bg-on-surface/40 z-40 lg:hidden backdrop-blur-xs"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed left-0 top-0 h-full w-72 bg-surface-container-lowest border-r border-surface-variant z-50 flex flex-col justify-between shadow-[0_1px_8px_rgba(0,0,0,0.04)] transition-transform duration-200 lg:translate-x-0 ${
          isMobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex flex-col flex-1 overflow-y-auto px-4 pt-5">
          {/* Brand Logo & Header */}
          <div className="flex items-center justify-between pb-5 mb-2 border-b border-surface-variant">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-primary flex items-center justify-center text-on-primary font-headline-sm font-bold shadow-sm">
                P
              </div>
              <div className="flex flex-col">
                <span className="font-headline-sm text-headline-sm text-primary tracking-tight font-bold">
                  PPS4027
                </span>
                <span className="font-label-sm text-label-sm text-outline tracking-normal uppercase">
                  {role === 'trainer' ? 'Trainer Portal' : role === 'admin' ? 'Registry & Admin' : 'Placement Portal'}
                </span>
              </div>
            </div>

            <button
              type="button"
              onClick={onCloseMobile}
              className="lg:hidden text-outline hover:text-on-surface p-1"
            >
              <span className="material-symbols-outlined text-[20px]">close</span>
            </button>
          </div>

          {/* Navigation Menu Links */}
          {role === 'student' && (
            <>
              <div className="mb-4">
                <p className="px-3 mb-2 font-label-sm text-label-sm text-outline uppercase tracking-wider font-semibold">
                  Curriculum & Work
                </p>
                <nav className="flex flex-col gap-1">
                  {studentCurriculumNav.map((item) => (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      onClick={onCloseMobile}
                      className={getNavClass}
                    >
                      <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
                      <span>{item.label}</span>
                    </NavLink>
                  ))}
                </nav>
              </div>

              <div className="mb-4">
                <p className="px-3 mb-2 font-label-sm text-label-sm text-outline uppercase tracking-wider font-semibold">
                  Account & System
                </p>
                <nav className="flex flex-col gap-1">
                  {studentSystemNav.map((item) => (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      onClick={onCloseMobile}
                      className={getNavClass}
                    >
                      <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
                      <span>{item.label}</span>
                    </NavLink>
                  ))}
                </nav>
              </div>
            </>
          )}

          {role === 'trainer' && (
            <div className="mb-4">
              <p className="px-3 mb-2 font-label-sm text-label-sm text-outline uppercase tracking-wider font-semibold">
                Cohort Evaluation
              </p>
              <nav className="flex flex-col gap-1">
                {trainerNav.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    onClick={onCloseMobile}
                    className={getNavClass}
                  >
                    <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
                    <span>{item.label}</span>
                  </NavLink>
                ))}
              </nav>
            </div>
          )}

          {role === 'admin' && (
            <div className="mb-4">
              <p className="px-3 mb-2 font-label-sm text-label-sm text-outline uppercase tracking-wider font-semibold">
                Governance & Control
              </p>
              <nav className="flex flex-col gap-1">
                {adminNav.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    onClick={onCloseMobile}
                    className={getNavClass}
                  >
                    <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
                    <span>{item.label}</span>
                  </NavLink>
                ))}
              </nav>
            </div>
          )}
        </div>

        {/* User Card at bottom of sidebar */}
        <div className="p-3 m-3 rounded-xl bg-surface-container-low border border-surface-variant">
          <div className="flex items-center gap-3">
            <img
              src={currentUser?.avatar}
              alt={currentUser?.name}
              className="w-9 h-9 rounded-full object-cover ring-1 ring-outline-variant/60 shrink-0"
            />
            <div className="flex flex-col min-w-0 flex-1">
              <span className="font-label-md text-label-md text-on-surface truncate font-semibold">
                {currentUser?.name}
              </span>
              <span className="font-label-sm text-label-sm text-on-surface-variant truncate">
                {currentUser?.rollNo || currentUser?.title || currentUser?.email}
              </span>
              <span className="font-label-sm text-label-sm text-primary truncate font-medium">
                {currentUser?.track || 'Placement 2025'}
              </span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
