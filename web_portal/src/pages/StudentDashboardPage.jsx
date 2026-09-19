import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useApp } from '../context/AppContext';

const StudentDashboardPage = () => {
  const { currentUser, currentReport, assignments, contentLibrary, calendarEvents } = useApp();
  const navigate = useNavigate();

  return (
    <div className="flex flex-col w-full pb-12 space-y-6">
      
      {/* Top Academic Context Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-surface-variant">
        <div>
          <div className="flex items-center gap-1.5 text-on-surface-variant font-label-sm text-label-sm uppercase tracking-wider mb-1">
            <span>PPS4027</span>
            <span className="text-outline">/</span>
            <span>Vocational Guidance</span>
            <span className="text-outline">/</span>
            <span className="text-primary font-semibold">Student Portfolio</span>
          </div>
          <div className="flex items-baseline gap-3">
            <h1 className="font-headline-md text-headline-md text-on-surface tracking-tight font-bold">
              Placement Preparation Workspace
            </h1>
            <span className="font-label-sm text-label-sm text-secondary bg-surface-container-high px-2 py-0.5 rounded">
              Continuous Assessment CA1
            </span>
          </div>
        </div>

        {/* Quick Cohort Snapshot Tag */}
        <div className="flex items-center gap-3 self-start md:self-auto bg-surface-container-lowest p-2 px-4 rounded-xl shadow-sm border border-surface-variant">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-tertiary animate-pulse"></span>
            <span className="font-label-sm text-label-sm text-on-surface font-semibold">CA1 Window Open</span>
          </div>
          <span className="text-outline-variant font-light">|</span>
          <span className="font-label-sm text-label-sm text-on-surface-variant font-medium">4 Days Remaining (Sep 24)</span>
        </div>
      </div>

      {/* 1. Hero Next-Step Card */}
      <section className="relative overflow-hidden bg-surface-container-lowest rounded-xl shadow-sm border border-surface-variant">
        <div className="grid grid-cols-1 lg:grid-cols-12 items-center p-6 md:p-8 gap-6 relative z-10">
          <div className="lg:col-span-8 flex flex-col items-start">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded bg-secondary-container text-on-secondary-container font-label-sm text-label-sm mb-3">
              <span className="material-symbols-outlined text-[16px]">auto_stories</span>
              <span className="font-semibold">Week 4 · Module 1: Resume Building</span>
            </div>
            
            <h2 className="font-headline-lg text-headline-lg text-on-surface tracking-tight mb-2 max-w-2xl font-bold">
              Build a resume that gets noticed.
            </h2>
            
            <p className="font-body-lg text-body-lg text-on-surface-variant max-w-xl mb-6 leading-relaxed">
              Benchmark your draft against industry role requirements with clear, explainable feedback before CA1 locking.
            </p>

            <div className="flex flex-wrap items-center gap-3">
              <button
                type="button"
                onClick={() => navigate('/resume-review')}
                className="inline-flex items-center gap-2 bg-primary hover:bg-primary-container text-on-primary px-5 py-2.5 rounded font-label-md text-label-md shadow-sm transition-colors font-semibold"
              >
                <span>Start Resume Review</span>
                <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
              </button>

              <button
                type="button"
                onClick={() => navigate('/history')}
                className="inline-flex items-center gap-2 text-primary hover:text-on-surface font-label-md text-label-md px-4 py-2.5 rounded hover:bg-surface-container-low transition-colors font-medium border border-outline-variant/50"
              >
                <span className="material-symbols-outlined text-[18px] text-secondary">history</span>
                <span>View Latest ATS Report ({currentReport.ats_score}/100)</span>
              </button>
            </div>
          </div>

          <div className="lg:col-span-4 flex justify-center lg:justify-end">
            <div className="relative w-full max-w-xs aspect-square flex flex-col items-center justify-center p-5 bg-surface-container-low rounded-xl border border-surface-variant/60 text-center">
              <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center text-primary mb-3">
                <span className="material-symbols-outlined text-[32px]">fact_check</span>
              </div>
              <span className="font-headline-sm text-headline-sm text-on-surface font-bold">
                {currentReport.ats_score} / 100
              </span>
              <span className="font-label-sm text-label-sm text-tertiary font-semibold mt-0.5">
                Baseline Requirements Met
              </span>
              <p className="font-body-sm text-body-sm text-outline mt-2">
                Single-column parse verified for {currentReport.filename}
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 2. At-A-Glance Priority Cards (3 Columns) */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        
        {/* Card 1: Next Best Action */}
        <div className="bg-surface-container-lowest p-6 rounded-xl shadow-sm flex flex-col justify-between relative overflow-hidden border border-surface-variant group">
          <div className="absolute top-0 left-0 right-0 h-1 bg-primary"></div>
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="font-label-sm text-label-sm uppercase tracking-wider text-primary font-semibold">
                Priority Action
              </span>
              <span className="px-2 py-0.5 rounded bg-surface-container-high text-on-surface-variant font-label-sm text-label-sm font-medium">
                Due Sep 24
              </span>
            </div>
            <h3 className="font-title-md text-title-md text-on-surface mb-2 font-bold">
              Upload Single-Column CV Draft
            </h3>
            <p className="font-body-sm text-body-sm text-on-surface-variant mb-4 leading-relaxed">
              Mandatory compliance for CA1 grading. Upload the updated ATS-parseable format before review locks.
            </p>
          </div>
          <div className="pt-2 flex items-center justify-between mt-auto">
            <button
              type="button"
              onClick={() => navigate('/resume-review')}
              className="inline-flex items-center gap-1.5 bg-primary text-on-primary px-4 py-2 rounded font-label-md text-label-md hover:bg-primary-container transition-colors w-full justify-center font-semibold"
            >
              <span>Go to CA1 Submission</span>
              <span className="material-symbols-outlined text-[18px]">arrow_right_alt</span>
            </button>
          </div>
        </div>

        {/* Card 2: This Week's Learning */}
        <div className="bg-surface-container-lowest p-6 rounded-xl shadow-sm flex flex-col justify-between border border-surface-variant">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
                Module Checklist
              </span>
              <span className="font-label-sm text-label-sm text-tertiary font-semibold bg-tertiary-fixed/30 px-2 py-0.5 rounded">
                2 of 3 Done
              </span>
            </div>
            <h3 className="font-title-md text-title-md text-on-surface mb-3 font-bold">
              This Week's Learning
            </h3>
            <div className="flex flex-col gap-2.5 mb-4">
              <div className="flex items-center justify-between text-body-sm">
                <span className="inline-flex items-center gap-2 text-on-surface font-body-sm text-body-sm">
                  <span className="material-symbols-outlined text-[18px] text-tertiary">check_circle</span>
                  <span className="line-through text-on-surface-variant">Tuesday Content Lecture</span>
                </span>
                <span className="font-label-sm text-label-sm text-outline">Done</span>
              </div>
              <div className="flex items-center justify-between text-body-sm">
                <span className="inline-flex items-center gap-2 text-on-surface font-body-sm text-body-sm">
                  <span className="material-symbols-outlined text-[18px] text-tertiary">check_circle</span>
                  <span className="line-through text-on-surface-variant">Wed Live Q&A w/ Mentors</span>
                </span>
                <span className="font-label-sm text-label-sm text-outline">Done</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded bg-surface-container-low border border-surface-variant/40">
                <span className="inline-flex items-center gap-2 text-on-surface font-body-sm text-body-sm font-medium">
                  <span className="material-symbols-outlined text-[18px] text-primary">radio_button_unchecked</span>
                  <span>Thursday MCQ 4</span>
                </span>
                <span className="font-label-sm text-label-sm text-error font-semibold">Due Tonight</span>
              </div>
            </div>
          </div>
          <div className="pt-1">
            <button
              type="button"
              onClick={() => navigate('/learning')}
              className="inline-flex items-center justify-between w-full font-label-md text-label-md text-primary hover:text-on-surface transition-colors py-1 font-semibold"
            >
              <span>Open Week 4 Learning Modules</span>
              <span className="material-symbols-outlined text-[18px]">launch</span>
            </button>
          </div>
        </div>

        {/* Card 3: Continuous Assessment Progress */}
        <div className="bg-surface-container-lowest p-6 rounded-xl shadow-sm flex flex-col justify-between border border-surface-variant">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
                Continuous Assessment
              </span>
              <span className="font-label-sm text-label-sm text-secondary font-medium">Semester Track</span>
            </div>
            <h3 className="font-title-md text-title-md text-on-surface mb-1 font-bold">
              Curriculum Momentum
            </h3>
            <p className="font-body-sm text-body-sm text-on-surface-variant mb-4">
              Week 4 of 15 completed across placement tracks.
            </p>
            {/* Progress Bar */}
            <div className="space-y-1.5 mb-4">
              <div className="flex justify-between font-label-sm text-label-sm">
                <span className="text-on-surface font-semibold">Overall Course Progress</span>
                <span className="text-primary font-bold">62%</span>
              </div>
              <div className="w-full bg-surface-container-high h-2.5 rounded-full overflow-hidden">
                <div className="bg-primary h-full rounded-full transition-all duration-500" style={{ width: '62%' }}></div>
              </div>
            </div>
          </div>
          <div className="pt-1 flex items-center justify-between text-body-sm">
            <span className="text-outline text-label-sm">CA1 (30%) · CA2 (30%) · CA3 (40%)</span>
            <button
              type="button"
              onClick={() => navigate('/assignments')}
              className="font-label-md text-label-md text-primary hover:underline font-semibold"
            >
              View Rubric
            </button>
          </div>
        </div>

      </section>

      {/* 3. Lower 2-Column Section: Continuous Assessment Modules & Calendar */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 pt-2">
        
        {/* Left 8 Cols: CA Milestones */}
        <div className="lg:col-span-8 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-title-md text-title-md text-on-surface font-bold">
              Continuous Assessment Milestones
            </h3>
            <button
              type="button"
              onClick={() => navigate('/assignments')}
              className="font-label-sm text-label-sm text-primary hover:underline font-semibold"
            >
              View Full Syllabus Details
            </button>
          </div>

          <div className="space-y-3">
            {assignments.map((item, idx) => (
              <div
                key={item.assessment}
                className="p-4 rounded-xl bg-surface-container-lowest border border-surface-variant shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-surface-bright transition-colors"
              >
                <div className="flex items-start gap-3">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center font-bold text-sm shrink-0 ${
                    item.status === 'Complete'
                      ? 'bg-tertiary-fixed text-on-tertiary-fixed-variant'
                      : 'bg-surface-container text-outline'
                  }`}>
                    {item.assessment}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-title-sm text-title-sm text-on-surface font-semibold">{item.title}</h4>
                      <span className={`px-2 py-0.5 rounded text-[11px] font-medium ${
                        item.status === 'Complete'
                          ? 'bg-tertiary-fixed/60 text-tertiary'
                          : 'bg-surface-container text-outline'
                      }`}>
                        {item.status}
                      </span>
                    </div>
                    <p className="font-body-sm text-body-sm text-on-surface-variant mt-0.5">{item.description}</p>
                  </div>
                </div>

                <div className="flex items-center justify-between sm:justify-end gap-4 border-t sm:border-t-0 pt-2 sm:pt-0 border-surface-variant">
                  <div className="text-left sm:text-right">
                    <span className="font-label-sm text-label-sm text-outline block">Score</span>
                    <span className="font-label-md text-label-md text-on-surface font-semibold">{item.score}</span>
                  </div>
                  <div className="text-left sm:text-right">
                    <span className="font-label-sm text-label-sm text-outline block">Weight</span>
                    <span className="font-label-md text-label-md text-primary font-semibold">{item.weight}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right 4 Cols: Upcoming Events & Drop Schedule */}
        <div className="lg:col-span-4 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-title-md text-title-md text-on-surface font-bold">
              Upcoming Schedule
            </h3>
            <span className="font-label-sm text-label-sm text-outline">AY 24–25</span>
          </div>

          <div className="p-4 rounded-xl bg-surface-container-lowest border border-surface-variant shadow-sm space-y-3">
            {calendarEvents.map((evt, idx) => (
              <div key={idx} className="flex items-start gap-3 pb-3 border-b border-surface-variant/60 last:border-0 last:pb-0">
                <div className="w-12 py-1 rounded bg-surface-container-low text-center shrink-0 border border-surface-variant/40">
                  <span className="font-label-sm text-label-sm text-outline uppercase block leading-none">{evt.day}</span>
                  <span className="font-label-md text-label-md text-on-surface font-bold">{evt.date.split(' ')[0]}</span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-label-md text-label-md text-on-surface font-semibold truncate">{evt.event}</p>
                  <p className="font-body-sm text-body-sm text-on-surface-variant flex items-center gap-1 mt-0.5">
                    <span className="material-symbols-outlined text-[14px] text-outline">location_on</span>
                    <span className="truncate">{evt.location} · {evt.time}</span>
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
};

export default StudentDashboardPage;
