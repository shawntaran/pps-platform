import React from 'react';
import { useApp } from '../context/AppContext';

const LearningPage = () => {
  const { contentLibrary, showToast } = useApp();

  return (
    <div className="flex flex-col w-full pb-16 space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-2 border-b border-surface-variant">
        <div>
          <div className="flex items-center gap-2 text-on-surface-variant font-label-sm text-label-sm uppercase tracking-wider mb-1">
            <span>PPS4027</span>
            <span className="text-outline">/</span>
            <span>Courseware</span>
            <span className="text-outline">/</span>
            <span className="text-primary font-semibold">Content Library</span>
          </div>
          <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight font-bold">
            Module Learning Materials
          </h1>
          <p className="font-body-md text-body-md text-on-surface-variant max-w-3xl mt-1">
            Readings, worksheets, masterclasses, and diagnostic guides for Module 1: Resume Building.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {contentLibrary.map((item, idx) => (
          <div
            key={idx}
            className="p-6 rounded-xl bg-surface-container-lowest border border-surface-variant shadow-sm flex flex-col justify-between space-y-4"
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="px-2.5 py-0.5 rounded bg-secondary-container text-on-secondary-container font-label-sm text-label-sm font-semibold">
                  {item.week} · {item.module}
                </span>
                <span className="font-label-sm text-label-sm text-outline">{item.duration}</span>
              </div>
              <h3 className="font-title-md text-title-md text-on-surface font-bold mb-1">{item.title}</h3>
              <p className="font-body-sm text-body-sm text-on-surface-variant">{item.type}</p>
            </div>

            <div className="pt-2 border-t border-surface-variant flex items-center justify-between">
              <span className={`font-label-sm text-label-sm font-semibold ${
                item.released ? 'text-tertiary' : 'text-outline'
              }`}>
                {item.released ? '✓ Available Now' : 'Scheduled Release'}
              </span>

              <button
                type="button"
                disabled={!item.released}
                onClick={() => showToast(`Opening resource: ${item.title}`)}
                className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded bg-primary text-on-primary hover:bg-primary-container font-label-md text-label-md font-semibold disabled:opacity-40 transition-colors shadow-sm"
              >
                <span className="material-symbols-outlined text-[16px]">visibility</span>
                <span>Open Resource</span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LearningPage;
