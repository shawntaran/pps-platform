import React, { useState } from 'react';
import { useApp } from '../context/AppContext';

const TrainerDashboardPage = () => {
  const { currentUser, submissions, updateSubmissionReview, showToast } = useApp();
  const [activeTab, setActiveTab] = useState('ca1');
  const [filterReview, setFilterReview] = useState('all');
  const [selectedSub, setSelectedSub] = useState(null);
  const [feedbackText, setFeedbackText] = useState('');
  const [adjustedScore, setAdjustedScore] = useState(80);
  const [rubricParse, setRubricParse] = useState(85);
  const [rubricKw, setRubricKw] = useState(78);
  const [rubricStruct, setRubricStruct] = useState(80);

  const filteredSubmissions = submissions.filter((s) => {
    if (filterReview === 'all') return true;
    if (filterReview === 'needs_review') return s.review_status === 'Needs review';
    if (filterReview === 'graded') return s.review_status === 'Graded';
    return true;
  });

  const handleOpenReview = (sub) => {
    setSelectedSub(sub);
    setFeedbackText(sub.trainer_notes || 'Good structural baseline. Enhance project quantitative metrics.');
    setAdjustedScore(sub.ats_score || 78);
  };

  const handlePublishGrade = (e) => {
    e.preventDefault();
    if (!selectedSub) return;
    updateSubmissionReview(selectedSub.id, 'Graded', feedbackText, Number(adjustedScore));
    setSelectedSub(null);
  };

  return (
    <div className="flex flex-col w-full pb-16 space-y-6">
      
      {/* Editorial Masthead / Header Controls */}
      <div className="flex flex-col xl:flex-row xl:items-end justify-between gap-4 pb-2 border-b border-surface-variant">
        <div className="space-y-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="px-2.5 py-0.5 bg-secondary-container text-on-secondary-container rounded font-label-sm text-label-sm font-semibold tracking-wider uppercase">
              Evaluator Desk
            </span>
            <span className="text-outline text-body-sm">•</span>
            <span className="font-body-sm text-body-sm text-on-surface-variant font-medium">
              {currentUser?.name || 'Dr. Kavya Shah'} · {currentUser?.title || 'Lead Faculty'}
            </span>
            <span className="text-outline text-body-sm">•</span>
            <span className="font-body-sm text-body-sm text-on-surface-variant">Weightage: 30% Course Total</span>
          </div>
          <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight font-bold">
            Batch 2025 · Cohort B (Data & Analytics)
          </h1>
          <p className="font-body-md text-body-md text-on-surface-variant">
            CA1 Submission & Evaluation Desk — Module 1: Resume Engineering, ATS Parsing & Industry Alignment
          </p>
        </div>

        {/* Actions & Cohort Switcher */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            className="flex items-center gap-1.5 px-3 py-2 bg-surface-container-lowest border border-outline-variant rounded font-label-md text-label-md text-on-surface hover:bg-surface-container-low transition-colors shadow-sm font-semibold"
          >
            <span className="material-symbols-outlined text-[18px] text-primary">groups</span>
            <span>Batch 2025 · Section B (64 Students)</span>
          </button>
          
          <button
            type="button"
            onClick={() => showToast('Exporting Batch CA1 Evaluation Gradebook (CSV)...')}
            className="flex items-center gap-1.5 px-3 py-2 bg-surface-container-lowest border border-outline-variant text-on-surface hover:bg-surface-container-low transition-colors rounded font-label-md text-label-md shadow-sm"
          >
            <span className="material-symbols-outlined text-[18px] text-outline">download</span>
            <span>Export CSV</span>
          </button>

          <button
            type="button"
            onClick={() => showToast('Bulk feedback notifications sent to cohort candidates.')}
            className="flex items-center gap-1.5 px-4 py-2 bg-primary text-on-primary hover:bg-primary-container rounded font-label-md text-label-md transition-colors shadow-sm font-semibold"
          >
            <span className="material-symbols-outlined text-[18px]">published_with_changes</span>
            <span>Bulk Publish</span>
          </button>
        </div>
      </div>

      {/* Milestone Filter Pill Tabs */}
      <div className="flex items-center justify-between gap-4 overflow-x-auto border-b border-surface-variant pb-1">
        <div className="flex items-center gap-1 shrink-0">
          <button
            type="button"
            onClick={() => setActiveTab('ca1')}
            className={`flex items-center gap-2 px-4 py-2 rounded-t font-title-sm text-title-sm transition-colors ${
              activeTab === 'ca1'
                ? 'bg-surface-container-lowest border-b-2 border-primary text-primary font-bold shadow-sm'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low'
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">task_alt</span>
            <span>CA1: Resume Building & ATS</span>
            <span className="ml-1 px-1.5 py-0.5 rounded-full bg-error-container text-on-error-container text-label-sm font-bold">
              Active Deadline
            </span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('ca2')}
            className={`flex items-center gap-2 px-4 py-2 rounded-t font-title-sm text-title-sm transition-colors ${
              activeTab === 'ca2'
                ? 'bg-surface-container-lowest border-b-2 border-primary text-primary font-bold shadow-sm'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low'
            }`}
          >
            <span className="material-symbols-outlined text-[18px] text-outline">forum</span>
            <span>CA2: Group Discussion</span>
            <span className="ml-1 px-1.5 py-0.5 rounded-full bg-surface-container-high text-on-surface-variant text-label-sm font-medium">
              Nov 12
            </span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('ca3')}
            className={`flex items-center gap-2 px-4 py-2 rounded-t font-title-sm text-title-sm transition-colors ${
              activeTab === 'ca3'
                ? 'bg-surface-container-lowest border-b-2 border-primary text-primary font-bold shadow-sm'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low'
            }`}
          >
            <span className="material-symbols-outlined text-[18px] text-outline">psychology</span>
            <span>CA3: Technical Mock & HR</span>
            <span className="ml-1 px-1.5 py-0.5 rounded-full bg-surface-container-high text-on-surface-variant text-label-sm font-medium">
              Dec 04
            </span>
          </button>
        </div>

        <div className="hidden md:flex items-center gap-2 text-on-surface-variant font-label-sm text-label-sm font-medium">
          <span className="w-2 h-2 rounded-full bg-tertiary"></span>
          <span>Rubric v3.2 Active · Auto-Calculated 100-pt Scale</span>
        </div>
      </div>

      {/* 4 Batch KPI Metric Cards */}
      <section className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {/* KPI 1 */}
        <div className="bg-surface-container-lowest p-5 rounded-xl border border-surface-variant shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-on-surface-variant mb-2">
            <span className="font-label-sm text-label-sm tracking-wider uppercase font-semibold text-outline">
              Cohort Enrolled
            </span>
            <span className="material-symbols-outlined text-[20px] text-outline">group</span>
          </div>
          <div>
            <div className="font-metric-display text-metric-display text-on-surface font-bold">
              64 <span className="font-title-sm text-title-sm font-normal text-on-surface-variant">Candidates</span>
            </div>
            <div className="mt-1 flex items-center gap-1.5 text-body-sm text-tertiary font-medium">
              <span className="w-2 h-2 rounded-full bg-tertiary"></span>
              <span>100% Onboarded to LMS</span>
            </div>
          </div>
          <div className="mt-3 pt-2 border-t border-surface-variant flex justify-between items-center text-label-sm font-label-sm text-on-surface-variant">
            <span>Section B Track</span>
            <span className="font-semibold text-on-surface">Data & Analytics</span>
          </div>
        </div>

        {/* KPI 2 */}
        <div className="bg-surface-container-lowest p-5 rounded-xl border border-surface-variant shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-on-surface-variant mb-2">
            <span className="font-label-sm text-label-sm tracking-wider uppercase font-semibold text-outline">
              Submissions Received
            </span>
            <span className="material-symbols-outlined text-[20px] text-tertiary">upload_file</span>
          </div>
          <div>
            <div className="font-metric-display text-metric-display text-on-surface font-bold">
              56 <span className="font-title-sm text-title-sm font-normal text-on-surface-variant">/ 64</span>
            </div>
            <div className="mt-1 flex items-center gap-1.5">
              <span className="px-1.5 py-0.5 rounded bg-tertiary-fixed text-on-tertiary-fixed font-label-sm text-label-sm font-semibold">
                +12 today
              </span>
              <span className="font-body-sm text-body-sm text-on-surface-variant">87.5% submitted</span>
            </div>
          </div>
          <div className="mt-3 pt-2 border-t border-surface-variant">
            <div className="w-full bg-surface-container h-1.5 rounded-full overflow-hidden">
              <div className="bg-tertiary h-full rounded-full" style={{ width: '87.5%' }}></div>
            </div>
          </div>
        </div>

        {/* KPI 3 */}
        <div className="bg-surface-container-lowest p-5 rounded-xl border border-surface-variant shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-on-surface-variant mb-2">
            <span className="font-label-sm text-label-sm tracking-wider uppercase font-semibold text-outline">
              Pending Review
            </span>
            <span className="material-symbols-outlined text-[20px] text-secondary">pending_actions</span>
          </div>
          <div>
            <div className="font-metric-display text-metric-display text-on-surface font-bold">
              14 <span className="font-title-sm text-title-sm font-normal text-on-surface-variant">Remaining</span>
            </div>
            <div className="mt-1 flex items-center gap-1.5">
              <span className="px-1.5 py-0.5 rounded bg-secondary-container text-on-secondary-container font-label-sm text-label-sm font-semibold">
                Due in 2 days
              </span>
              <span className="font-body-sm text-body-sm text-on-surface-variant">42 graded</span>
            </div>
          </div>
          <div className="mt-3 pt-2 border-t border-surface-variant flex justify-between items-center text-label-sm font-label-sm text-on-surface-variant">
            <span>Evaluator Pace</span>
            <span className="font-semibold text-primary">~8 reviews / hour</span>
          </div>
        </div>

        {/* KPI 4 */}
        <div className="bg-surface-container-lowest p-5 rounded-xl border border-surface-variant shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-on-surface-variant mb-2">
            <span className="font-label-sm text-label-sm tracking-wider uppercase font-semibold text-outline">
              Batch ATS Benchmark
            </span>
            <span className="material-symbols-outlined text-[20px] text-primary">analytics</span>
          </div>
          <div>
            <div className="font-metric-display text-metric-display text-on-surface font-bold">
              81.4 <span className="font-title-sm text-title-sm font-normal text-on-surface-variant">/ 100</span>
            </div>
            <div className="mt-1 flex items-center gap-1.5 text-body-sm text-tertiary font-medium">
              <span className="material-symbols-outlined text-[16px]">trending_up</span>
              <span>+6.2% vs previous cohort</span>
            </div>
          </div>
          <div className="mt-3 pt-2 border-t border-surface-variant flex justify-between items-center text-label-sm font-label-sm text-on-surface-variant">
            <span>Standard Deviation</span>
            <span className="font-semibold text-on-surface">± 4.8 pts</span>
          </div>
        </div>
      </section>

      {/* Submissions & Evaluation Queue Table */}
      <section className="p-6 rounded-xl bg-surface-container-lowest border border-surface-variant shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="font-headline-sm text-headline-sm text-on-surface font-bold">Candidate Evaluation Queue</h3>
            <p className="font-body-sm text-body-sm text-on-surface-variant">
              Review ATS diagnostics, evaluate single-column formatting, and publish rubric feedback.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex rounded-lg bg-surface-container p-0.5 border border-surface-variant">
              <button
                type="button"
                onClick={() => setFilterReview('all')}
                className={`px-3 py-1 rounded text-label-sm font-label-sm ${
                  filterReview === 'all' ? 'bg-primary text-on-primary font-semibold' : 'text-on-surface-variant'
                }`}
              >
                All ({submissions.length})
              </button>
              <button
                type="button"
                onClick={() => setFilterReview('needs_review')}
                className={`px-3 py-1 rounded text-label-sm font-label-sm ${
                  filterReview === 'needs_review' ? 'bg-primary text-on-primary font-semibold' : 'text-on-surface-variant'
                }`}
              >
                Needs Review
              </button>
              <button
                type="button"
                onClick={() => setFilterReview('graded')}
                className={`px-3 py-1 rounded text-label-sm font-label-sm ${
                  filterReview === 'graded' ? 'bg-primary text-on-primary font-semibold' : 'text-on-surface-variant'
                }`}
              >
                Graded
              </button>
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-surface-variant font-label-sm text-label-sm text-outline uppercase tracking-wider">
                <th className="py-3 px-4">Student & Roll No</th>
                <th className="py-3 px-4">Artifact / Track</th>
                <th className="py-3 px-4">Submission Status</th>
                <th className="py-3 px-4">ATS Score</th>
                <th className="py-3 px-4">Evaluation State</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-variant text-body-sm font-body-sm">
              {filteredSubmissions.map((sub) => (
                <tr key={sub.id} className="hover:bg-surface-bright transition-colors">
                  <td className="py-3 px-4">
                    <div>
                      <p className="font-semibold text-on-surface">{sub.student}</p>
                      <p className="font-label-sm text-label-sm text-outline">{sub.rollNo || 'PPS-2024-4027'}</p>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <div>
                      <p className="text-on-surface font-medium">{sub.filename}</p>
                      <p className="font-body-sm text-body-sm text-on-surface-variant truncate max-w-xs">{sub.target_role}</p>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-tertiary-fixed text-on-tertiary-fixed">
                      {sub.status}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="font-bold text-primary">
                      {sub.ats_score ? `${sub.ats_score} / 100` : '—'}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`px-2.5 py-1 rounded text-label-sm font-label-sm font-semibold ${
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
                      onClick={() => handleOpenReview(sub)}
                      className="inline-flex items-center gap-1 px-3 py-1.5 rounded bg-primary text-on-primary hover:bg-primary-container font-label-md text-label-md font-semibold transition-colors"
                    >
                      <span className="material-symbols-outlined text-[16px]">rate_review</span>
                      <span>Review / Grade</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Evaluation & Grading Modal / Drawer */}
      {selectedSub && (
        <div className="fixed inset-0 bg-on-surface/50 z-50 flex items-center justify-center p-4 backdrop-blur-xs">
          <div className="bg-surface-container-lowest rounded-2xl max-w-2xl w-full p-6 sm:p-8 shadow-2xl border border-surface-variant space-y-6 max-h-[90vh] overflow-y-auto animate-in zoom-in-95">
            <div className="flex items-start justify-between pb-4 border-b border-surface-variant">
              <div>
                <span className="font-label-sm text-label-sm text-primary uppercase font-bold tracking-wider">
                  Continuous Assessment CA1 Evaluation
                </span>
                <h3 className="font-headline-sm text-headline-sm text-on-surface font-bold">
                  {selectedSub.student} · {selectedSub.filename}
                </h3>
                <p className="font-body-sm text-body-sm text-on-surface-variant">
                  Target Role: {selectedSub.target_role}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setSelectedSub(null)}
                className="p-1 rounded text-outline hover:text-on-surface"
              >
                <span className="material-symbols-outlined text-[24px]">close</span>
              </button>
            </div>

            <form onSubmit={handlePublishGrade} className="space-y-5">
              
              {/* Rubric Criteria Evaluation */}
              <div className="space-y-4">
                <span className="font-title-sm text-title-sm text-on-surface font-bold block">
                  Rubric Criteria Scoring (v3.2)
                </span>

                <div className="space-y-3 bg-surface-container-low p-4 rounded-xl border border-surface-variant/60">
                  <div>
                    <div className="flex justify-between font-label-sm text-label-sm mb-1">
                      <span className="font-semibold text-on-surface">1. Single-Column Parseability (40% wt)</span>
                      <span className="font-bold text-primary">{rubricParse}%</span>
                    </div>
                    <input
                      type="range"
                      min="50"
                      max="100"
                      value={rubricParse}
                      onChange={(e) => setRubricParse(Number(e.target.value))}
                      className="w-full accent-primary"
                    />
                  </div>

                  <div>
                    <div className="flex justify-between font-label-sm text-label-sm mb-1">
                      <span className="font-semibold text-on-surface">2. Job Description Keyword Alignment (40% wt)</span>
                      <span className="font-bold text-primary">{rubricKw}%</span>
                    </div>
                    <input
                      type="range"
                      min="50"
                      max="100"
                      value={rubricKw}
                      onChange={(e) => setRubricKw(Number(e.target.value))}
                      className="w-full accent-primary"
                    />
                  </div>

                  <div>
                    <div className="flex justify-between font-label-sm text-label-sm mb-1">
                      <span className="font-semibold text-on-surface">3. Section Architecture & Metrics (20% wt)</span>
                      <span className="font-bold text-primary">{rubricStruct}%</span>
                    </div>
                    <input
                      type="range"
                      min="50"
                      max="100"
                      value={rubricStruct}
                      onChange={(e) => setRubricStruct(Number(e.target.value))}
                      className="w-full accent-primary"
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between p-3 rounded-lg bg-secondary-container/40 border border-secondary/20">
                  <span className="font-title-sm text-title-sm text-on-surface font-semibold">Calculated Composite ATS Score:</span>
                  <span className="font-headline-sm text-headline-sm text-primary font-bold">
                    {Math.round(rubricParse * 0.4 + rubricKw * 0.4 + rubricStruct * 0.2)} / 100
                  </span>
                </div>
              </div>

              {/* Qualitative Mentor Feedback */}
              <div className="space-y-1.5">
                <label className="font-label-sm text-label-sm text-on-surface font-semibold block">
                  Evaluator Feedback & Recommendation Notes
                </label>
                <textarea
                  rows={4}
                  required
                  value={feedbackText}
                  onChange={(e) => setFeedbackText(e.target.value)}
                  placeholder="Provide qualitative guidance on ATS keywords, project bullets, and formatting..."
                  className="w-full p-3 rounded-lg bg-surface-container-low border border-surface-variant font-body-sm text-body-sm text-on-surface focus:outline-none focus:border-primary"
                />
              </div>

              {/* Submit buttons */}
              <div className="flex items-center justify-end gap-3 pt-4 border-t border-surface-variant">
                <button
                  type="button"
                  onClick={() => setSelectedSub(null)}
                  className="px-4 py-2 rounded text-label-md font-label-md text-on-surface-variant hover:bg-surface-container-low font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-6 py-2.5 rounded bg-primary text-on-primary hover:bg-primary-container font-label-md text-label-md font-semibold transition-colors shadow-sm"
                >
                  Publish Grade & Feedback
                </button>
              </div>

            </form>
          </div>
        </div>
      )}

    </div>
  );
};

export default TrainerDashboardPage;
