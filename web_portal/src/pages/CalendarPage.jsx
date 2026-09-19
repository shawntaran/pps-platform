import React from 'react';
import { useApp } from '../context/AppContext';

const CalendarPage = () => {
  const { calendarEvents } = useApp();

  return (
    <div className="flex flex-col w-full pb-16 space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-2 border-b border-surface-variant">
        <div>
          <div className="flex items-center gap-2 text-on-surface-variant font-label-sm text-label-sm uppercase tracking-wider mb-1">
            <span>PPS4027</span>
            <span className="text-outline">/</span>
            <span>Academic Schedule</span>
            <span className="text-outline">/</span>
            <span className="text-primary font-semibold">Semester Calendar</span>
          </div>
          <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight font-bold">
            Academic Calendar & Key Dates
          </h1>
          <p className="font-body-md text-body-md text-on-surface-variant max-w-3xl mt-1">
            Keep track of weekly content drops, mentor Q&A office hours, MCQ assessments, and CA lock deadlines.
          </p>
        </div>
      </div>

      <div className="p-6 rounded-xl bg-surface-container-lowest border border-surface-variant shadow-sm space-y-4">
        <h3 className="font-title-md text-title-md text-on-surface font-bold">
          September 2026 Practicum Timeline
        </h3>

        <div className="divide-y divide-surface-variant">
          {calendarEvents.map((evt, idx) => (
            <div key={idx} className="py-4 flex items-start gap-4 hover:bg-surface-bright p-2 rounded-lg transition-colors">
              <div className="w-16 py-2 rounded-xl bg-primary text-on-primary text-center shrink-0 shadow-sm">
                <span className="font-label-sm text-label-sm uppercase block font-medium opacity-80">{evt.day}</span>
                <span className="font-headline-sm text-headline-sm font-bold block">{evt.date.split(' ')[0]}</span>
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h4 className="font-title-sm text-title-sm text-on-surface font-bold">{evt.event}</h4>
                  <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-surface-container text-primary">
                    {evt.type}
                  </span>
                </div>
                <p className="font-body-sm text-body-sm text-on-surface-variant mt-1 flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-[16px] text-outline">schedule</span>
                  <span>{evt.time}</span>
                  <span className="text-outline">•</span>
                  <span className="material-symbols-outlined text-[16px] text-outline">location_on</span>
                  <span>{evt.location}</span>
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CalendarPage;
