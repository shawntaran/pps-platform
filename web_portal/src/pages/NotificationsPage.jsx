import React from 'react';
import { useApp } from '../context/AppContext';

const NotificationsPage = () => {
  const notices = [
    {
      title: "CA1 Single-Column ATS Format Compliance Mandatory",
      date: "19 Sep 2026",
      sender: "Prof. K. V. Ramanathan (Program Administrator)",
      content: "All candidates in Batch 2025 must upload their single-column ATS CV before September 24, 2026. Submissions with complex graphic sidebars will receive parseability warnings.",
      badge: "Urgent Deadline",
      badgeColor: "bg-error-container text-on-error-container"
    },
    {
      title: "Module 1 Live Q&A Session Scheduled",
      date: "18 Sep 2026",
      sender: "Dr. Kavya Shah (Faculty Lead)",
      content: "Join the live interactive mentor room on Wednesday at 4:00 PM IST on MS Teams. We will review resume action verbs, impact metrics, and rubric standards.",
      badge: "Office Hours",
      badgeColor: "bg-secondary-container text-on-secondary-container"
    },
    {
      title: "Data Privacy & FERPA Compliance Notice",
      date: "15 Sep 2026",
      sender: "Placement Governance Desk",
      content: "Please ensure your digital processing consent is confirmed under the Privacy & Data tab so our automated parser can verify your technical dossier.",
      badge: "Compliance",
      badgeColor: "bg-tertiary-fixed text-on-tertiary-fixed-variant"
    }
  ];

  return (
    <div className="flex flex-col w-full pb-16 space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-2 border-b border-surface-variant">
        <div>
          <div className="flex items-center gap-2 text-on-surface-variant font-label-sm text-label-sm uppercase tracking-wider mb-1">
            <span>PPS4027</span>
            <span className="text-outline">/</span>
            <span>Announcements</span>
            <span className="text-outline">/</span>
            <span className="text-primary font-semibold">Cohort Notices</span>
          </div>
          <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight font-bold">
            Cohort Notices & Circulars
          </h1>
          <p className="font-body-md text-body-md text-on-surface-variant max-w-3xl mt-1">
            Official announcements from faculty evaluators and placement cell administration.
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {notices.map((n, idx) => (
          <div
            key={idx}
            className="p-6 rounded-xl bg-surface-container-lowest border border-surface-variant shadow-sm space-y-2"
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="flex items-center gap-2.5">
                <span className={`px-2.5 py-0.5 rounded font-label-sm text-label-sm font-semibold ${n.badgeColor}`}>
                  {n.badge}
                </span>
                <h3 className="font-title-md text-title-md text-on-surface font-bold">{n.title}</h3>
              </div>
              <span className="font-body-sm text-body-sm text-outline">{n.date}</span>
            </div>
            <p className="font-label-sm text-label-sm text-primary font-medium">{n.sender}</p>
            <p className="font-body-md text-body-md text-on-surface-variant leading-relaxed">{n.content}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default NotificationsPage;
