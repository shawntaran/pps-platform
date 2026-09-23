import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';

const AssignmentsPage = () => {
  const { assignments } = useApp();
  const navigate = useNavigate();

  return (
    <div className="flex flex-col w-full pb-16 space-y-6">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-2 border-b border-surface-variant">
        <div>
          <div className="flex items-center gap-2 text-on-surface-variant font-label-sm text-label-sm uppercase tracking-wider mb-1">
            <span>PPS4027</span>
            <span className="text-outline">/</span>
            <span>Academic Curriculum</span>
            <span className="text-outline">/</span>
            <span className="text-primary font-semibold">Continuous Assessment</span>
          </div>
          <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight font-bold">
            Continuous Assessment (CA1–CA3)
          </h1>
          <p className="font-body-md text-body-md text-on-surface-variant max-w-3xl mt-1">
            Continuous assessment rubrics, submission deadlines, and evaluation criteria for AY 2024–25.
          </p>
        </div>
      </div>

      {/* Cards for CA1, CA2, CA3 */}
      <div className="space-y-6">
        {assignments.map((item) => (
          <div
            key={item.assessment}
            className="p-6 rounded-xl bg-surface-container-lowest border border-surface-variant shadow-sm space-y-4"
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-surface-variant">
              <div className="flex items-center gap-3">
                <span className="px-3 py-1 rounded bg-primary-container text-on-primary font-headline-sm font-bold">
                  {item.assessment}
                </span>
                <div>
                  <h3 className="font-title-md text-title-md text-on-surface font-bold">{item.title}</h3>
                  <span className="font-body-sm text-body-sm text-outline">Due: {item.due} · Course Weight: {item.weight}</span>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <span className={`px-3 py-1 rounded-full font-label-md text-label-md font-semibold ${
                  item.status === 'Complete'
                    ? 'bg-tertiary-fixed text-on-tertiary-fixed-variant'
                    : 'bg-surface-container text-outline'
                }`}>
                  Status: {item.status}
                </span>
              </div>
            </div>

            <p className="font-body-md text-body-md text-on-surface-variant">
              {item.description}
            </p>

            <div className="flex flex-wrap items-center justify-between gap-4 pt-2">
              <div className="flex items-center gap-4 text-body-sm">
                <div>
                  <span className="font-label-sm text-label-sm text-outline block">Your Score</span>
                  <span className="font-title-sm text-title-sm text-on-surface font-bold">{item.score}</span>
                </div>
                <div>
                  <span className="font-label-sm text-label-sm text-outline block">Passing Benchmark</span>
                  <span className="font-title-sm text-title-sm text-tertiary font-bold">60% Met</span>
                </div>
              </div>

              {item.assessment === 'CA1' ? (
                <button
                  type="button"
                  onClick={() => navigate('/resume-review')}
                  className="inline-flex items-center gap-2 bg-primary hover:bg-primary-container text-on-primary px-5 py-2 rounded font-label-md text-label-md font-semibold transition-colors shadow-sm"
                >
                  <span className="material-symbols-outlined text-[18px]">find_in_page</span>
                  <span>Open CA1 Resume Desk</span>
                </button>
              ) : (
                <span className="font-label-sm text-label-sm text-outline px-3 py-1 rounded bg-surface-container">
                  Opens later in semester
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

    </div>
  );
};

export default AssignmentsPage;
