import React, { useState } from 'react';
import { useApp } from '../context/AppContext';

const PrivacyDataPage = () => {
  const { currentUser, consentActive, setConsentActive, purgeStudentData, showToast } = useApp();
  const [showPurgeModal, setShowPurgeModal] = useState(false);
  const [showAgreementModal, setShowAgreementModal] = useState(false);

  const handleDownloadArchive = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify({
      user: currentUser,
      timestamp: new Date().toISOString(),
      policy: "FERPA / Institutional Placement Policy 2024-25",
      records: "Continuous Assessment CA1 ATS Diagnostic Transcripts"
    }, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `PPS4027_Student_Data_${currentUser?.id || 'export'}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
    showToast('Student data archive exported (JSON).');
  };

  return (
    <div className="flex flex-col w-full pb-16 space-y-6">
      
      {/* Page Editorial Header */}
      <header className="flex flex-col lg:flex-row lg:items-end justify-between gap-4 pb-2 border-b border-surface-variant">
        <div className="flex flex-col max-w-2xl">
          <div className="flex items-center gap-2 mb-1 text-on-surface-variant font-label-sm text-label-sm uppercase tracking-wider">
            <span>Semester V · PPS4027 Placement Preparation</span>
            <span className="w-1 h-1 rounded-full bg-outline"></span>
            <span className="text-primary font-semibold">Student Rights & Records</span>
          </div>
          <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight font-bold">
            Privacy & Personal Data
          </h1>
          <p className="font-body-md text-body-md text-on-surface-variant mt-1">
            Clear, transparent information about how your resume drafts, skill assessments, and career coaching records are handled within the PPS4027 curriculum.
          </p>
        </div>

        {/* Live Consent Standing Pill */}
        <div className="flex items-center self-start lg:self-auto gap-2 px-3 py-1.5 rounded-full bg-tertiary-fixed text-on-tertiary-fixed-variant shadow-sm border border-tertiary/20">
          <span className="material-symbols-outlined text-[18px] text-tertiary">check_circle</span>
          <span className="font-label-md text-label-md font-semibold">
            {consentActive ? 'Consent Active & In Good Standing' : 'Consent Suspended'}
          </span>
        </div>
      </header>

      {/* Prominent Current Consent Overview */}
      <section className="bg-surface-container-lowest rounded-xl shadow-sm p-6 lg:p-8 border border-surface-variant relative overflow-hidden">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-lg bg-surface-container-low flex items-center justify-center shrink-0 text-primary border border-surface-variant/60">
              <span className="material-symbols-outlined text-[28px]">verified_user</span>
            </div>
            <div className="flex flex-col">
              <div className="flex flex-wrap items-center gap-2 mb-1">
                <h2 className="font-title-md text-title-md text-on-surface font-bold">Resume-Processing Consent</h2>
                <span className={`px-2 py-0.5 rounded font-label-sm text-label-sm font-semibold ${
                  consentActive ? 'bg-tertiary-fixed text-on-tertiary-fixed-variant' : 'bg-surface-container text-outline'
                }`}>
                  {consentActive ? 'Active' : 'Revoked'}
                </span>
                <span className="font-body-sm text-body-sm text-outline">
                  · Signed for Cohort AY 2024–25
                </span>
              </div>
              <p className="font-body-md text-body-md text-on-surface-variant max-w-3xl leading-relaxed">
                You have authorized PPS4027 placement faculty, allocated academic mentors, and internal diagnostic tools to review your resume drafts against course benchmarks and industry standards.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 self-start lg:self-auto">
            <button
              type="button"
              onClick={() => setShowAgreementModal(true)}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-surface-container-low hover:bg-surface-container-high text-on-surface font-label-md text-label-md transition-colors border border-surface-variant font-semibold"
            >
              <span className="material-symbols-outlined text-[18px]">description</span>
              <span>View Signed Agreement</span>
            </button>
            <button
              type="button"
              onClick={() => {
                setConsentActive(!consentActive);
                showToast(consentActive ? 'Consent revoked.' : 'Consent re-enabled.');
              }}
              className="px-3 py-2 rounded-lg text-label-md font-label-md text-primary hover:bg-surface-container-low font-semibold"
            >
              {consentActive ? 'Revoke Consent' : 'Grant Consent'}
            </button>
          </div>
        </div>

        {/* Trust Indicators Grid */}
        <div className="mt-6 pt-5 grid grid-cols-1 md:grid-cols-3 gap-3 bg-surface-container-low/60 rounded-lg p-4 border border-surface-variant/40">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-[20px] text-tertiary">lock</span>
            <span className="font-body-sm text-body-sm text-on-surface font-medium">Stored on university institutional servers</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-[20px] text-tertiary">visibility_off</span>
            <span className="font-body-sm text-body-sm text-on-surface font-medium">Never sold or shared without student opt-in</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-[20px] text-tertiary">history</span>
            <span className="font-body-sm text-body-sm text-on-surface font-medium">Automated deletion after placement cycle</span>
          </div>
        </div>
      </section>

      {/* Main Content Split Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left 7 Columns: What Data We Process */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-headline-sm text-headline-sm text-on-surface font-bold">What Data We Process</h3>
            <span className="font-label-sm text-label-sm text-outline">4 Academic Categories</span>
          </div>

          <div className="space-y-3">
            {/* Item 1: Resume Content */}
            <div className="bg-surface-container-lowest rounded-xl p-4 shadow-sm border border-surface-variant flex items-start gap-3">
              <div className="w-10 h-10 rounded-lg bg-surface-container-low flex items-center justify-center shrink-0 text-primary">
                <span className="material-symbols-outlined text-[22px]">badge</span>
              </div>
              <div className="flex flex-col flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-title-sm text-title-sm text-on-surface font-semibold">Resume Content & History</span>
                  <span className="font-label-sm text-label-sm text-on-surface-variant bg-surface-container-high px-2 py-0.5 rounded">Continuous Assessment</span>
                </div>
                <p className="font-body-sm text-body-sm text-on-surface-variant leading-relaxed">
                  Text of your education, projects, technical skills, and internship history. Processed solely to generate structural formatting guidance, keyword alignment, and rubric scoring for CA1.
                </p>
              </div>
            </div>

            {/* Item 2: Contact Details */}
            <div className="bg-surface-container-lowest rounded-xl p-4 shadow-sm border border-surface-variant flex items-start gap-3">
              <div className="w-10 h-10 rounded-lg bg-surface-container-low flex items-center justify-center shrink-0 text-primary">
                <span className="material-symbols-outlined text-[22px]">contact_mail</span>
              </div>
              <div className="flex flex-col flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-title-sm text-title-sm text-on-surface font-semibold">Contact & Header Information</span>
                  <span className="font-label-sm text-label-sm text-tertiary bg-tertiary-fixed px-2 py-0.5 rounded font-semibold">Never Shared Outward</span>
                </div>
                <p className="font-body-sm text-body-sm text-on-surface-variant leading-relaxed">
                  Institutional email address, contact telephone, and LinkedIn profile URLs. Parsed strictly to verify professional header completeness.
                </p>
              </div>
            </div>

            {/* Item 3: Target JDs */}
            <div className="bg-surface-container-lowest rounded-xl p-4 shadow-sm border border-surface-variant flex items-start gap-3">
              <div className="w-10 h-10 rounded-lg bg-surface-container-low flex items-center justify-center shrink-0 text-primary">
                <span className="material-symbols-outlined text-[22px]">work_outline</span>
              </div>
              <div className="flex flex-col flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-title-sm text-title-sm text-on-surface font-semibold">Target Job Descriptions</span>
                  <span className="font-label-sm text-label-sm text-on-surface-variant bg-surface-container-high px-2 py-0.5 rounded">Benchmarking</span>
                </div>
                <p className="font-body-sm text-body-sm text-on-surface-variant leading-relaxed">
                  The job roles, responsibilities, and qualification texts you paste into Module 1 workshops to evaluate profile calibration.
                </p>
              </div>
            </div>

            {/* Item 4: Diagnostic Feedback */}
            <div className="bg-surface-container-lowest rounded-xl p-4 shadow-sm border border-surface-variant flex items-start gap-3">
              <div className="w-10 h-10 rounded-lg bg-surface-container-low flex items-center justify-center shrink-0 text-primary">
                <span className="material-symbols-outlined text-[22px]">insights</span>
              </div>
              <div className="flex flex-col flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-title-sm text-title-sm text-on-surface font-semibold">Analysis & Diagnostic Feedback</span>
                  <span className="font-label-sm text-label-sm text-on-surface-variant bg-surface-container-high px-2 py-0.5 rounded">Formative Only</span>
                </div>
                <p className="font-body-sm text-body-sm text-on-surface-variant leading-relaxed">
                  Quantitative and qualitative scores generated by faculty mentors so you can address gaps ahead of formal campus recruitment drives.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Right 5 Columns: Student Data Rights & Controls */}
        <div className="lg:col-span-5 space-y-6">
          <div className="p-6 rounded-xl bg-surface-container-lowest border border-surface-variant shadow-sm space-y-4">
            <h3 className="font-title-md text-title-md text-on-surface font-bold flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-[20px]">manage_accounts</span>
              <span>Data Rights & Management</span>
            </h3>

            <p className="font-body-sm text-body-sm text-on-surface-variant leading-relaxed">
              Under university policy, you have full ownership of your placement submissions. You can download your complete portfolio or request data erasure at any time.
            </p>

            <div className="space-y-3 pt-2">
              <button
                type="button"
                onClick={handleDownloadArchive}
                className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded bg-surface-container-low hover:bg-surface-container-high text-on-surface font-label-md text-label-md transition-colors border border-surface-variant font-semibold"
              >
                <span className="material-symbols-outlined text-[18px]">download</span>
                <span>Download My Data Dossier (JSON)</span>
              </button>

              <button
                type="button"
                onClick={() => setShowPurgeModal(true)}
                className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded bg-error-container/30 hover:bg-error-container/50 text-error font-label-md text-label-md transition-colors border border-error/20 font-semibold"
              >
                <span className="material-symbols-outlined text-[18px]">delete_forever</span>
                <span>Purge Stored Resume Records</span>
              </button>
            </div>
          </div>

          <div className="p-6 rounded-xl bg-surface-container-lowest border border-surface-variant shadow-sm space-y-2">
            <span className="font-label-sm text-label-sm text-outline uppercase tracking-wider font-semibold">Institutional Compliance</span>
            <p className="font-body-sm text-body-sm text-on-surface-variant">
              System operates under ISO/IEC 27001 data protection protocols and educational record privacy standards (AY 2024–25).
            </p>
          </div>
        </div>

      </div>

      {/* Confirmation Modal for Purge Data */}
      {showPurgeModal && (
        <div className="fixed inset-0 bg-on-surface/50 z-50 flex items-center justify-center p-4 backdrop-blur-xs">
          <div className="bg-surface-container-lowest rounded-2xl max-w-md w-full p-6 shadow-xl border border-surface-variant space-y-4">
            <div className="w-12 h-12 rounded-full bg-error-container text-error flex items-center justify-center mx-auto">
              <span className="material-symbols-outlined text-[28px]">warning</span>
            </div>
            <div className="text-center space-y-1">
              <h4 className="font-headline-sm text-headline-sm text-on-surface font-bold">Purge All Resume Records?</h4>
              <p className="font-body-sm text-body-sm text-on-surface-variant">
                This will permanently delete all uploaded drafts, keyword parsing logs, and CA1 diagnostic transcripts for your account.
              </p>
            </div>
            <div className="flex items-center justify-end gap-3 pt-4 border-t border-surface-variant">
              <button
                type="button"
                onClick={() => setShowPurgeModal(false)}
                className="px-4 py-2 rounded text-label-md font-label-md text-on-surface-variant hover:bg-surface-container-low"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => {
                  purgeStudentData();
                  setShowPurgeModal(false);
                }}
                className="px-5 py-2 rounded bg-error text-on-error font-label-md text-label-md font-semibold hover:opacity-90"
              >
                Yes, Purge Data
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Agreement Modal */}
      {showAgreementModal && (
        <div className="fixed inset-0 bg-on-surface/50 z-50 flex items-center justify-center p-4 backdrop-blur-xs">
          <div className="bg-surface-container-lowest rounded-2xl max-w-lg w-full p-6 shadow-xl border border-surface-variant space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-surface-variant">
              <h4 className="font-title-md text-title-md text-on-surface font-bold">Signed Digital Processing Agreement</h4>
              <button onClick={() => setShowAgreementModal(false)} className="text-outline hover:text-on-surface">
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>
            <div className="text-body-sm text-on-surface-variant space-y-2 max-h-80 overflow-y-auto pr-2">
              <p><strong>Candidate ID:</strong> {currentUser?.id} ({currentUser?.name})</p>
              <p><strong>Curriculum:</strong> PPS4027 Career Preparation Practicum</p>
              <p><strong>Term:</strong> Academic Year 2024–25 (15 Weeks)</p>
              <p><strong>Scope:</strong> Automated single-column ATS verification, keyword density alignment against industry job profiles, continuous assessment formative scoring by assigned faculty mentors.</p>
              <p><strong>Security Protocols:</strong> Role-based access control (RBAC), TLS 1.3 in-transit encryption, local institutional data residency.</p>
            </div>
            <div className="flex justify-end pt-2 border-t border-surface-variant">
              <button
                type="button"
                onClick={() => setShowAgreementModal(false)}
                className="px-4 py-2 rounded bg-primary text-on-primary font-label-md text-label-md font-semibold"
              >
                Close Agreement
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default PrivacyDataPage;
