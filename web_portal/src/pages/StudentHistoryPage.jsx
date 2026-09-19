import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';

const StudentHistoryPage = () => {
  const { currentUser, submissions, assignments } = useApp();
  const navigate = useNavigate();
  const [filterType, setFilterType] = useState('all');

  const studentSubmissions = submissions.filter(
    (s) => s.student_id === currentUser?.id || currentUser?.role !== 'student'
  );

  return (
    <div className="flex flex-col w-full pb-16 space-y-6">
      
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-2 border-b border-surface-variant">
        <div>
          <div className="flex items-center gap-2 text-on-surface-variant font-label-sm text-label-sm uppercase tracking-wider mb-1">
            <span>PPS4027</span>
            <span className="text-outline">/</span>
            <span>Continuous Assessment Tracker</span>
            <span className="text-outline">/</span>
            <span className="text-primary font-semibold">Submissions & History</span>
          </div>
          <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight font-bold">
            My Progress & Submission History
          </h1>
          <p className="font-body-md text-body-md text-on-surface-variant max-w-3xl mt-1">
            Track all uploaded CV iterations, ATS scoring progressions, and faculty mentor review evaluations.
          </p>
        </div>

        <button
          type="button"
          onClick={() => navigate('/resume-review')}
          className="inline-flex items-center gap-2 bg-primary text-on-primary px-5 py-2.5 rounded font-label-md text-label-md font-semibold hover:bg-primary-container transition-colors shadow-sm self-start md:self-auto"
        >
          <span className="material-symbols-outlined text-[18px]">add</span>
          <span>Submit New Draft</span>
        </button>
      </div>

      {/* 3 Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <div className="p-5 rounded-xl bg-surface-container-lowest border border-surface-variant shadow-sm">
          <span className="font-label-sm text-label-sm uppercase tracking-wider text-outline font-semibold">Total Scans Performed</span>
          <div className="font-metric-display text-metric-display text-on-surface font-bold mt-1">{studentSubmissions.length}</div>
          <span className="font-body-sm text-body-sm text-tertiary font-medium">Continuous iterations recorded</span>
        </div>

        <div className="p-5 rounded-xl bg-surface-container-lowest border border-surface-variant shadow-sm">
          <span className="font-label-sm text-label-sm uppercase tracking-wider text-outline font-semibold">Latest ATS Score</span>
          <div className="font-metric-display text-metric-display text-primary font-bold mt-1">
            {studentSubmissions[0]?.ats_score || 76} / 100
          </div>
          <span className="font-body-sm text-body-sm text-on-surface-variant">Benchmark threshold: 70+</span>
        </div>

        <div className="p-5 rounded-xl bg-surface-container-lowest border border-surface-variant shadow-sm">
          <span className="font-label-sm text-label-sm uppercase tracking-wider text-outline font-semibold">CA1 Assessment Status</span>
          <div className="font-metric-display text-metric-display text-tertiary font-bold mt-1">Completed</div>
          <span className="font-body-sm text-body-sm text-outline">Locks Sep 24, 2026</span>
        </div>
      </div>

      {/* Submissions Table Section */}
      <div className="p-6 rounded-xl bg-surface-container-lowest border border-surface-variant shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <h3 className="font-title-md text-title-md text-on-surface font-bold">
            Submission Dossiers
          </h3>
          <div className="flex items-center gap-2">
            <span className="font-label-sm text-label-sm text-outline">Filter:</span>
            <div className="flex rounded-lg bg-surface-container p-0.5 border border-surface-variant">
              <button
                type="button"
                onClick={() => setFilterType('all')}
                className={`px-3 py-1 rounded text-label-sm font-label-sm ${
                  filterType === 'all' ? 'bg-primary text-on-primary font-semibold' : 'text-on-surface-variant'
                }`}
              >
                All Submissions
              </button>
              <button
                type="button"
                onClick={() => setFilterType('ca1')}
                className={`px-3 py-1 rounded text-label-sm font-label-sm ${
                  filterType === 'ca1' ? 'bg-primary text-on-primary font-semibold' : 'text-on-surface-variant'
                }`}
              >
                CA1 Only
              </button>
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-surface-variant font-label-sm text-label-sm text-outline uppercase tracking-wider">
                <th className="py-3 px-4">Artifact / Filename</th>
                <th className="py-3 px-4">Target Role & Track</th>
                <th className="py-3 px-4">Submitted Date</th>
                <th className="py-3 px-4">ATS Score</th>
                <th className="py-3 px-4">Mentor Review</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-variant text-body-sm font-body-sm">
              {studentSubmissions.map((sub) => (
                <tr key={sub.id} className="hover:bg-surface-bright transition-colors">
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2.5">
                      <span className="material-symbols-outlined text-primary text-[20px]">description</span>
                      <span className="font-semibold text-on-surface">{sub.filename}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-on-surface-variant">
                    {sub.target_role}
                  </td>
                  <td className="py-3 px-4 text-outline">
                    {sub.submitted_date}
                  </td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full font-label-sm text-label-sm font-bold bg-secondary-container text-on-secondary-container">
                      {sub.ats_score ? `${sub.ats_score} / 100` : 'Pending'}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-0.5 rounded text-[11px] font-semibold ${
                      sub.review_status === 'Graded'
                        ? 'bg-tertiary-fixed text-on-tertiary-fixed-variant'
                        : sub.review_status === 'Needs review'
                        ? 'bg-secondary-container text-on-secondary-container'
                        : 'bg-surface-container text-outline'
                    }`}>
                      {sub.review_status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      type="button"
                      onClick={() => navigate('/resume-review')}
                      className="font-label-md text-label-md text-primary hover:underline font-semibold"
                    >
                      View Report
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};

export default StudentHistoryPage;
