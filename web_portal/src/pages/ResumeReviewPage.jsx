import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import confetti from 'canvas-confetti';
import { useApp } from '../context/AppContext';

const ResumeReviewPage = () => {
  const { currentUser, currentReport, consentActive, setConsentActive, submitNewResume, showToast } = useApp();
  const navigate = useNavigate();

  // Stepper state: 1 (Upload), 2 (Target Role), 3 (Consent), 4 (Analyzing), 5 (Report)
  const [currentStep, setCurrentStep] = useState(5); // Default to viewing current active report, but allow going back to re-run
  const [selectedFile, setSelectedFile] = useState({ name: currentReport.filename || 'Aarav_Mehta_CV_v2.4.pdf', size: '342 KB' });
  const [targetRoleTitle, setTargetRoleTitle] = useState('Thoughtworks · Graduate Data Analyst');
  const [targetJdText, setTargetJdText] = useState(
    `Role Overview: Graduate Data Analyst at Thoughtworks.\nKey Requirements: Strong foundation in Python, SQL querying, Data Modelling, and exploratory data analysis. Familiarity with BI tooling (Power BI/Tableau) and ETL pipeline workflows. Excellent communication skills and problem-solving mindset.`
  );
  const [isScanning, setIsScanning] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);
  const [scanStageText, setScanStageText] = useState('Initializing parser...');

  const presetJDs = [
    {
      title: 'Thoughtworks · Graduate Data Analyst',
      text: 'Role: Graduate Data Analyst. Required skills: Python, SQL, Data Modelling, ETL pipelines, Power BI, Statistics, data cleaning.'
    },
    {
      title: 'TCS · Associate Software Engineer',
      text: 'Role: Associate Software Engineer. Required: Java/Python, DSA, SQL, Git, REST APIs, Agile methodologies, cloud fundamentals.'
    },
    {
      title: 'Deloitte · Business Technology Analyst',
      text: 'Role: Business Technology Analyst. Required: Business analysis, SQL, Excel, PowerPoint, stakeholder management, analytics dashboarding.'
    }
  ];

  const handleSelectPreset = (preset) => {
    setTargetRoleTitle(preset.title);
    setTargetJdText(preset.text);
    showToast(`Loaded template for ${preset.title}`, 'info');
  };

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile({
        name: file.name,
        size: `${(file.size / 1024).toFixed(1)} KB`
      });
      showToast(`Uploaded: ${file.name}`);
    }
  };

  const triggerAnalysis = () => {
    setCurrentStep(4);
    setIsScanning(true);
    setScanProgress(15);
    setScanStageText('Extracting single-column text layer & encoding...');

    setTimeout(() => {
      setScanProgress(45);
      setScanStageText('Evaluating section headings & parseability...');
    }, 700);

    setTimeout(() => {
      setScanProgress(75);
      setScanStageText('Comparing semantic keywords against target JD...');
    }, 1400);

    setTimeout(() => {
      setScanProgress(95);
      setScanStageText('Computing ATS compatibility & rubric scoring...');
    }, 2000);

    setTimeout(() => {
      setIsScanning(false);
      setScanProgress(100);
      const generated = submitNewResume(selectedFile, targetJdText, targetRoleTitle);
      setCurrentStep(5);
      confetti({
        particleCount: 70,
        spread: 60,
        origin: { y: 0.6 }
      });
      showToast('ATS Diagnostic Report successfully generated!');
    }, 2500);
  };

  return (
    <div className="flex flex-col w-full pb-16 space-y-6">
      
      {/* Top Academic Dossier Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-2 border-b border-surface-variant">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center px-2 py-0.5 rounded-lg bg-surface-container font-label-sm text-label-sm text-secondary tracking-wide uppercase font-semibold">
              Continuous Assessment 1
            </span>
            <span className="text-outline text-label-sm">/</span>
            <span className="font-label-sm text-label-sm text-outline">Guided Verification Flow</span>
          </div>
          <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight font-bold">
            Resume Review & Diagnostic Desk
          </h1>
          <p className="font-body-md text-body-md text-on-surface-variant max-w-3xl leading-relaxed">
            Submit your single-column CV for automated formatting, section parseability, and role keyword calibration against target industry job descriptions.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start md:self-auto">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-tertiary-fixed text-on-tertiary-fixed-variant font-label-sm text-label-sm font-semibold">
            <span className="w-2 h-2 rounded-full bg-tertiary"></span>
            Rubric Active: CA1 v3.2
          </span>
          <span className="font-label-sm text-label-sm text-outline px-1">Course Weight: 30%</span>
        </div>
      </div>

      {/* Editorial 5-Step Linear Stepper */}
      <div className="p-4 rounded-xl bg-surface-container-lowest border border-surface-variant shadow-sm">
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          
          {/* Step 1 */}
          <button
            type="button"
            onClick={() => setCurrentStep(1)}
            className={`flex items-center gap-3 p-2 rounded-lg transition-colors text-left ${
              currentStep === 1
                ? 'bg-secondary-container/50 border border-primary/30'
                : currentStep > 1
                ? 'hover:bg-surface-container-low'
                : 'opacity-60'
            }`}
          >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 font-label-md text-label-md font-bold ${
              currentStep > 1 ? 'bg-tertiary/15 text-tertiary' : currentStep === 1 ? 'bg-primary text-on-primary' : 'bg-surface-container-high text-outline'
            }`}>
              {currentStep > 1 ? <span className="material-symbols-outlined text-[18px]">check</span> : '1'}
            </div>
            <div className="flex flex-col min-w-0">
              <span className="font-label-sm text-label-sm uppercase tracking-wider font-semibold text-outline">Step 01</span>
              <span className="font-title-sm text-title-sm text-on-surface truncate">Upload Resume</span>
            </div>
          </button>

          {/* Step 2 */}
          <button
            type="button"
            onClick={() => setCurrentStep(2)}
            className={`flex items-center gap-3 p-2 rounded-lg transition-colors text-left ${
              currentStep === 2
                ? 'bg-secondary-container/50 border border-primary/30'
                : currentStep > 2
                ? 'hover:bg-surface-container-low'
                : 'opacity-60'
            }`}
          >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 font-label-md text-label-md font-bold ${
              currentStep > 2 ? 'bg-tertiary/15 text-tertiary' : currentStep === 2 ? 'bg-primary text-on-primary' : 'bg-surface-container-high text-outline'
            }`}>
              {currentStep > 2 ? <span className="material-symbols-outlined text-[18px]">check</span> : '2'}
            </div>
            <div className="flex flex-col min-w-0">
              <span className="font-label-sm text-label-sm uppercase tracking-wider font-semibold text-outline">Step 02</span>
              <span className="font-title-sm text-title-sm text-on-surface truncate">Target Role & JD</span>
            </div>
          </button>

          {/* Step 3 */}
          <button
            type="button"
            onClick={() => setCurrentStep(3)}
            className={`flex items-center gap-3 p-2 rounded-lg transition-colors text-left ${
              currentStep === 3
                ? 'bg-secondary-container/50 border border-primary/30'
                : currentStep > 3
                ? 'hover:bg-surface-container-low'
                : 'opacity-60'
            }`}
          >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 font-label-md text-label-md font-bold ${
              currentStep > 3 ? 'bg-tertiary/15 text-tertiary' : currentStep === 3 ? 'bg-primary text-on-primary' : 'bg-surface-container-high text-outline'
            }`}>
              {currentStep > 3 ? <span className="material-symbols-outlined text-[18px]">check</span> : '3'}
            </div>
            <div className="flex flex-col min-w-0">
              <span className="font-label-sm text-label-sm uppercase tracking-wider font-semibold text-outline">Step 03</span>
              <span className="font-title-sm text-title-sm text-on-surface truncate">Privacy & Consent</span>
            </div>
          </button>

          {/* Step 4 */}
          <button
            type="button"
            onClick={() => setCurrentStep(4)}
            className={`flex items-center gap-3 p-2 rounded-lg transition-colors text-left ${
              currentStep === 4
                ? 'bg-secondary-container/50 border border-primary/30'
                : currentStep > 4
                ? 'hover:bg-surface-container-low'
                : 'opacity-60'
            }`}
          >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 font-label-md text-label-md font-bold ${
              currentStep > 4 ? 'bg-tertiary/15 text-tertiary' : currentStep === 4 ? 'bg-primary text-on-primary' : 'bg-surface-container-high text-outline'
            }`}>
              {currentStep > 4 ? <span className="material-symbols-outlined text-[18px]">check</span> : '4'}
            </div>
            <div className="flex flex-col min-w-0">
              <span className="font-label-sm text-label-sm uppercase tracking-wider font-semibold text-outline">Step 04</span>
              <span className="font-title-sm text-title-sm text-on-surface truncate">Auto Analysis</span>
            </div>
          </button>

          {/* Step 5 */}
          <button
            type="button"
            onClick={() => setCurrentStep(5)}
            className={`flex items-center gap-3 p-2 rounded-lg transition-colors text-left ${
              currentStep === 5
                ? 'bg-secondary-container/50 border border-primary/30'
                : 'hover:bg-surface-container-low'
            }`}
          >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 font-label-md text-label-md font-bold ${
              currentStep === 5 ? 'bg-tertiary text-on-tertiary' : 'bg-surface-container-high text-outline'
            }`}>
              5
            </div>
            <div className="flex flex-col min-w-0">
              <span className="font-label-sm text-label-sm uppercase tracking-wider font-semibold text-tertiary">Step 05</span>
              <span className="font-title-sm text-title-sm text-on-surface truncate">Diagnostic Report</span>
            </div>
          </button>

        </div>
      </div>

      {/* STEP 1: UPLOAD RESUME */}
      {currentStep === 1 && (
        <div className="p-8 rounded-xl bg-surface-container-lowest border border-surface-variant shadow-sm space-y-6 animate-in fade-in">
          <div>
            <h2 className="font-headline-sm text-headline-sm text-on-surface font-bold">Step 1: Upload Your Single-Column Resume Draft</h2>
            <p className="font-body-md text-body-md text-on-surface-variant mt-1">
              Select your ATS-compliant PDF or DOCX file (Max 5MB). Multi-column templates will trigger formatting warnings.
            </p>
          </div>

          <div className="border-2 border-dashed border-outline-variant rounded-2xl p-8 text-center bg-surface-container-low/40 hover:bg-surface-container-low transition-colors">
            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center text-primary mx-auto mb-4">
              <span className="material-symbols-outlined text-[32px]">upload_file</span>
            </div>
            <p className="font-title-sm text-title-sm text-on-surface font-semibold mb-1">
              Drag and drop your resume file here, or browse
            </p>
            <p className="font-body-sm text-body-sm text-outline mb-4">
              Supports .PDF, .DOCX, and plain .TXT
            </p>
            
            <label className="inline-flex items-center gap-2 bg-primary hover:bg-primary-container text-on-primary px-5 py-2.5 rounded font-label-md text-label-md font-semibold cursor-pointer shadow-sm">
              <span className="material-symbols-outlined text-[18px]">folder_open</span>
              <span>Choose Local File</span>
              <input type="file" accept=".pdf,.docx,.txt" onChange={handleFileUpload} className="hidden" />
            </label>

            {selectedFile && (
              <div className="mt-6 p-4 rounded-xl bg-surface-container-lowest border border-surface-variant inline-flex items-center gap-4 text-left shadow-sm">
                <span className="material-symbols-outlined text-primary text-[28px]">description</span>
                <div>
                  <p className="font-label-md text-label-md text-on-surface font-bold">{selectedFile.name}</p>
                  <p className="font-body-sm text-body-sm text-outline">{selectedFile.size} · Ready for parse verification</p>
                </div>
                <span className="material-symbols-outlined text-tertiary text-[22px]">check_circle</span>
              </div>
            )}
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-surface-variant">
            <button
              type="button"
              onClick={() => setCurrentStep(2)}
              className="inline-flex items-center gap-2 bg-primary text-on-primary px-6 py-2.5 rounded font-label-md text-label-md font-semibold hover:bg-primary-container transition-colors shadow-sm"
            >
              <span>Next: Set Target Role & JD</span>
              <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
            </button>
          </div>
        </div>
      )}

      {/* STEP 2: TARGET ROLE & JD */}
      {currentStep === 2 && (
        <div className="p-8 rounded-xl bg-surface-container-lowest border border-surface-variant shadow-sm space-y-6 animate-in fade-in">
          <div>
            <h2 className="font-headline-sm text-headline-sm text-on-surface font-bold">Step 2: Define Target Role & Job Description</h2>
            <p className="font-body-md text-body-md text-on-surface-variant mt-1">
              Provide the job role or paste the recruiter requirements to calibrate ATS keyword scoring and semantic alignment.
            </p>
          </div>

          {/* Quick presets */}
          <div>
            <span className="font-label-sm text-label-sm text-outline uppercase tracking-wider block mb-2 font-semibold">
              Or Choose from Active Campus Recruitment Tracks:
            </span>
            <div className="flex flex-wrap gap-2">
              {presetJDs.map((p, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleSelectPreset(p)}
                  className={`px-3 py-1.5 rounded-lg border text-label-md font-label-md transition-colors ${
                    targetRoleTitle === p.title
                      ? 'bg-secondary-container border-primary text-on-secondary-container font-semibold'
                      : 'border-surface-variant bg-surface-container-low hover:bg-surface-container-high text-on-surface'
                  }`}
                >
                  {p.title}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="font-label-sm text-label-sm text-on-surface font-semibold block mb-1.5">
                Target Role & Company Name
              </label>
              <input
                type="text"
                value={targetRoleTitle}
                onChange={(e) => setTargetRoleTitle(e.target.value)}
                placeholder="e.g. Thoughtworks · Graduate Data Analyst"
                className="w-full px-4 py-2.5 rounded-lg bg-surface-container-low border border-surface-variant font-body-md text-body-md text-on-surface focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="font-label-sm text-label-sm text-on-surface font-semibold block mb-1.5">
                Full Job Description & Keyword Corpus
              </label>
              <textarea
                rows={5}
                value={targetJdText}
                onChange={(e) => setTargetJdText(e.target.value)}
                placeholder="Paste the requirements, technical competencies, and qualifications from the placement brochure..."
                className="w-full px-4 py-2.5 rounded-lg bg-surface-container-low border border-surface-variant font-body-md text-body-md text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          <div className="flex justify-between gap-3 pt-4 border-t border-surface-variant">
            <button
              type="button"
              onClick={() => setCurrentStep(1)}
              className="inline-flex items-center gap-1.5 text-on-surface-variant hover:text-on-surface px-4 py-2.5 rounded font-label-md text-label-md"
            >
              <span className="material-symbols-outlined text-[18px]">arrow_back</span>
              <span>Back</span>
            </button>
            <button
              type="button"
              onClick={() => setCurrentStep(3)}
              className="inline-flex items-center gap-2 bg-primary text-on-primary px-6 py-2.5 rounded font-label-md text-label-md font-semibold hover:bg-primary-container transition-colors shadow-sm"
            >
              <span>Next: Privacy Consent</span>
              <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
            </button>
          </div>
        </div>
      )}

      {/* STEP 3: PRIVACY & CONSENT */}
      {currentStep === 3 && (
        <div className="p-8 rounded-xl bg-surface-container-lowest border border-surface-variant shadow-sm space-y-6 animate-in fade-in">
          <div>
            <h2 className="font-headline-sm text-headline-sm text-on-surface font-bold">Step 3: Confirm Privacy & Processing Consent</h2>
            <p className="font-body-md text-body-md text-on-surface-variant mt-1">
              Your resume text is processed locally and privately on institutional servers for continuous assessment grading.
            </p>
          </div>

          <div className="p-5 rounded-xl bg-surface-container-low border border-surface-variant space-y-3">
            <div className="flex items-center gap-2 text-tertiary font-semibold">
              <span className="material-symbols-outlined text-[20px]">security</span>
              <span>Data Protection & Placement Policy Guarantee</span>
            </div>
            <ul className="text-body-sm font-body-sm text-on-surface-variant space-y-2 list-disc pl-5">
              <li>Processed strictly for CA1 rubric evaluation and internal feedback.</li>
              <li>Never transmitted to third-party recruiters without your explicit permission.</li>
              <li>Auto-purged at the end of the academic placement cycle (180 days).</li>
            </ul>

            <label className="flex items-center gap-3 pt-3 cursor-pointer select-none border-t border-surface-variant">
              <input
                type="checkbox"
                checked={consentActive}
                onChange={(e) => setConsentActive(e.target.checked)}
                className="w-5 h-5 rounded text-primary focus:ring-0 cursor-pointer"
              />
              <span className="font-label-md text-label-md text-on-surface font-semibold">
                I authorize the PPS4027 diagnostic parser to evaluate my CV and generate my diagnostic report.
              </span>
            </label>
          </div>

          <div className="flex justify-between gap-3 pt-4 border-t border-surface-variant">
            <button
              type="button"
              onClick={() => setCurrentStep(2)}
              className="inline-flex items-center gap-1.5 text-on-surface-variant hover:text-on-surface px-4 py-2.5 rounded font-label-md text-label-md"
            >
              <span className="material-symbols-outlined text-[18px]">arrow_back</span>
              <span>Back</span>
            </button>
            <button
              type="button"
              disabled={!consentActive}
              onClick={triggerAnalysis}
              className="inline-flex items-center gap-2 bg-primary text-on-primary px-6 py-2.5 rounded font-label-md text-label-md font-semibold hover:bg-primary-container transition-colors shadow-sm disabled:opacity-50"
            >
              <span className="material-symbols-outlined text-[18px]">play_arrow</span>
              <span>Launch Automated ATS Analysis</span>
            </button>
          </div>
        </div>
      )}

      {/* STEP 4: SCANNING / ANALYZING IN PROGRESS */}
      {currentStep === 4 && (
        <div className="p-12 rounded-xl bg-surface-container-lowest border border-surface-variant shadow-sm text-center space-y-6 animate-in fade-in">
          <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center text-primary mx-auto relative">
            <span className="material-symbols-outlined text-[40px] animate-spin">sync</span>
          </div>

          <div className="max-w-md mx-auto space-y-2">
            <h3 className="font-headline-sm text-headline-sm text-on-surface font-bold">
              Automated Parsing & Diagnostic in Progress
            </h3>
            <p className="font-body-md text-body-md text-on-surface-variant">
              {scanStageText}
            </p>
          </div>

          <div className="max-w-lg mx-auto space-y-2">
            <div className="flex justify-between font-label-sm text-label-sm text-on-surface">
              <span>Diagnostic Pipeline</span>
              <span className="text-primary font-bold">{scanProgress}%</span>
            </div>
            <div className="w-full bg-surface-container-high h-3 rounded-full overflow-hidden">
              <div
                className="bg-primary h-full rounded-full transition-all duration-300"
                style={{ width: `${scanProgress}%` }}
              ></div>
            </div>
          </div>
        </div>
      )}

      {/* STEP 5: COMPREHENSIVE DIAGNOSTIC REPORT (EXACT STITCH STRUCTURE) */}
      {currentStep === 5 && (
        <div className="space-y-6 animate-in fade-in">
          
          {/* Top Artifact Summary Bar */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* File card */}
            <div className="p-4 rounded-xl bg-surface-container-lowest border border-surface-variant shadow-sm flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-surface-container-high flex items-center justify-center text-primary shrink-0">
                  <span className="material-symbols-outlined text-[24px]">description</span>
                </div>
                <div>
                  <p className="font-title-sm text-title-sm text-on-surface font-semibold truncate">{currentReport.filename}</p>
                  <p className="font-body-sm text-body-sm text-outline">Analysed: {currentReport.analysed_on}</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setCurrentStep(1)}
                className="font-label-sm text-label-sm text-primary hover:underline px-2 py-1 rounded bg-surface-container-low font-semibold"
              >
                Re-upload / Scan Again
              </button>
            </div>

            {/* Target Role card */}
            <div className="p-4 rounded-xl bg-surface-container-lowest border border-surface-variant shadow-sm flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-secondary-container/60 flex items-center justify-center text-on-secondary-container shrink-0">
                  <span className="material-symbols-outlined text-[24px]">apartment</span>
                </div>
                <div>
                  <p className="font-title-sm text-title-sm text-on-surface font-semibold truncate">{currentReport.target_role}</p>
                  <p className="font-body-sm text-body-sm text-tertiary font-medium">CA1 Alignment Benchmark</p>
                </div>
              </div>
              <span className="font-label-sm text-label-sm px-2.5 py-1 rounded bg-tertiary-fixed text-on-tertiary-fixed-variant font-bold">
                Active Rubric
              </span>
            </div>
          </div>

          {/* Core Score Banner */}
          <div className="p-6 md:p-8 rounded-xl bg-surface-container-lowest border border-surface-variant shadow-sm">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-6 border-b border-surface-variant">
              <div className="flex items-center gap-5">
                <div className="w-20 h-20 rounded-2xl bg-primary text-on-primary flex flex-col items-center justify-center shrink-0 shadow-md">
                  <span className="font-metric-display text-metric-display font-bold leading-none">{currentReport.ats_score}</span>
                  <span className="text-[10px] uppercase tracking-wider font-semibold opacity-80 mt-1">/ 100 ATS</span>
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-headline-sm text-headline-sm text-on-surface font-bold">Overall ATS Diagnostics Score</h3>
                    <span className="px-2 py-0.5 rounded bg-tertiary-fixed text-on-tertiary-fixed-variant font-label-sm text-label-sm font-bold">
                      {currentReport.grade || 'Pass (Benchmark Met)'}
                    </span>
                  </div>
                  <p className="font-body-md text-body-md text-on-surface-variant mt-1 max-w-2xl">
                    Your single-column format parses well across automated applicant tracking systems. Address keyword gaps to elevate into top quartile placement screening.
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => {
                    window.print();
                  }}
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded bg-surface-container-low hover:bg-surface-container-high text-on-surface font-label-md text-label-md transition-colors border border-surface-variant"
                >
                  <span className="material-symbols-outlined text-[18px]">print</span>
                  <span>Print Report</span>
                </button>
                <button
                  type="button"
                  onClick={() => navigate('/history')}
                  className="inline-flex items-center gap-1.5 bg-primary hover:bg-primary-container text-on-primary px-4 py-2 rounded font-label-md text-label-md transition-colors shadow-sm font-semibold"
                >
                  <span className="material-symbols-outlined text-[18px]">history</span>
                  <span>All Submissions</span>
                </button>
              </div>
            </div>

            {/* 3 Diagnostic Sub-Score Pillars */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6">
              
              {/* Pillar 1: Parseability */}
              <div className="p-4 rounded-xl bg-surface-container-low/60 border border-surface-variant/70 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-label-sm text-label-sm uppercase tracking-wider text-outline font-semibold">Format & Parseability</span>
                  <span className="font-title-sm text-title-sm text-tertiary font-bold">{currentReport.parseability.score}%</span>
                </div>
                <div className="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
                  <div className="bg-tertiary h-full rounded-full" style={{ width: `${currentReport.parseability.score}%` }}></div>
                </div>
                <p className="font-body-sm text-body-sm text-on-surface-variant pt-1 leading-snug">
                  {currentReport.parseability.summary}
                </p>
              </div>

              {/* Pillar 2: Keyword Match */}
              <div className="p-4 rounded-xl bg-surface-container-low/60 border border-surface-variant/70 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-label-sm text-label-sm uppercase tracking-wider text-outline font-semibold">Keyword Match</span>
                  <span className="font-title-sm text-title-sm text-primary font-bold">{currentReport.keyword_match.score}%</span>
                </div>
                <div className="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
                  <div className="bg-primary h-full rounded-full" style={{ width: `${currentReport.keyword_match.score}%` }}></div>
                </div>
                <p className="font-body-sm text-body-sm text-on-surface-variant pt-1 leading-snug">
                  {currentReport.keyword_match.summary}
                </p>
              </div>

              {/* Pillar 3: Section Structure */}
              <div className="p-4 rounded-xl bg-surface-container-low/60 border border-surface-variant/70 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-label-sm text-label-sm uppercase tracking-wider text-outline font-semibold">Section Structure</span>
                  <span className="font-title-sm text-title-sm text-secondary font-bold">{currentReport.section_structure.score}%</span>
                </div>
                <div className="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
                  <div className="bg-secondary h-full rounded-full" style={{ width: `${currentReport.section_structure.score}%` }}></div>
                </div>
                <p className="font-body-sm text-body-sm text-on-surface-variant pt-1 leading-snug">
                  {currentReport.section_structure.summary}
                </p>
              </div>

            </div>
          </div>

          {/* Deep Competency Breakdown: Skills & Recommendations */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            {/* Left 7 Cols: Skills & Detected Sections */}
            <div className="lg:col-span-7 space-y-6">
              
              {/* Skills Analysis */}
              <div className="p-6 rounded-xl bg-surface-container-lowest border border-surface-variant shadow-sm space-y-4">
                <h4 className="font-title-md text-title-md text-on-surface font-bold flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary text-[20px]">psychology</span>
                  <span>Target Role Skills Calibration</span>
                </h4>

                <div>
                  <span className="font-label-sm text-label-sm text-tertiary uppercase tracking-wider font-semibold block mb-2">
                    ✓ Matched Key Competencies ({currentReport.matched_skills.length})
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {currentReport.matched_skills.map((skill, idx) => (
                      <span key={idx} className="px-3 py-1 rounded bg-tertiary-fixed/40 text-on-tertiary-fixed-variant font-label-md text-label-md font-semibold flex items-center gap-1 border border-tertiary/20">
                        <span className="material-symbols-outlined text-[16px] text-tertiary">check</span>
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <span className="font-label-sm text-label-sm text-error uppercase tracking-wider font-semibold block mb-2">
                    ⚠ Recommended Missing Keywords ({currentReport.missing_skills.length})
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {currentReport.missing_skills.map((skill, idx) => (
                      <span key={idx} className="px-3 py-1 rounded bg-error-container/40 text-on-error-container font-label-md text-label-md font-semibold flex items-center gap-1 border border-error/20">
                        <span className="material-symbols-outlined text-[16px] text-error">add</span>
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Detected Sections */}
              <div className="p-6 rounded-xl bg-surface-container-lowest border border-surface-variant shadow-sm space-y-3">
                <h4 className="font-title-md text-title-md text-on-surface font-bold flex items-center gap-2">
                  <span className="material-symbols-outlined text-secondary text-[20px]">format_list_bulleted</span>
                  <span>Detected Resume Sections</span>
                </h4>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 pt-1">
                  {currentReport.detected_sections.map((sec, idx) => (
                    <div key={idx} className="p-2.5 rounded bg-surface-container-low border border-surface-variant/40 flex items-center gap-2">
                      <span className="material-symbols-outlined text-tertiary text-[18px]">task_alt</span>
                      <span className="font-body-sm text-body-sm text-on-surface font-medium truncate">{sec}</span>
                    </div>
                  ))}
                </div>
              </div>

            </div>

            {/* Right 5 Cols: Actionable Recommendations & Trainer Feedback */}
            <div className="lg:col-span-5 space-y-6">
              
              {/* Recommendations Box */}
              <div className="p-6 rounded-xl bg-surface-container-lowest border border-surface-variant shadow-sm space-y-4">
                <h4 className="font-title-md text-title-md text-on-surface font-bold flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary text-[20px]">lightbulb</span>
                  <span>Actionable Improvements for CA1</span>
                </h4>

                <div className="space-y-3">
                  {currentReport.recommendations.map((rec, idx) => (
                    <div key={idx} className="p-3 rounded-lg bg-surface-container-low border border-surface-variant/50 flex items-start gap-3">
                      <span className="w-5 h-5 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
                        {idx + 1}
                      </span>
                      <p className="font-body-sm text-body-sm text-on-surface leading-snug">{rec}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Trainer / Faculty Feedback Desk Note */}
              <div className="p-6 rounded-xl bg-surface-container-lowest border border-surface-variant shadow-sm space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-title-md text-title-md text-on-surface font-bold flex items-center gap-2">
                    <span className="material-symbols-outlined text-secondary text-[20px]">rate_review</span>
                    <span>Mentor Evaluation Note</span>
                  </h4>
                  <span className="font-label-sm text-label-sm text-outline">Dr. Kavya Shah</span>
                </div>
                <div className="p-3.5 rounded-lg bg-secondary-container/30 border border-secondary/20">
                  <p className="font-body-md text-body-md text-on-surface italic leading-relaxed">
                    "{currentReport.trainer_feedback || 'Good structural foundation. Enhance the metrics in your project descriptions before CA1 locking.'}"
                  </p>
                </div>
              </div>

            </div>

          </div>

        </div>
      )}

    </div>
  );
};

export default ResumeReviewPage;
