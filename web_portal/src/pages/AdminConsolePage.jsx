import React, { useState } from 'react';
import { useApp } from '../context/AppContext';

const AdminConsolePage = () => {
  const { auditLogs, systemConfig, setSystemConfig, showToast } = useApp();
  const [activeTab, setActiveTab] = useState('overview');
  const [searchDirectory, setSearchDirectory] = useState('');
  const [searchAudit, setSearchAudit] = useState('');
  const [auditCategory, setAuditCategory] = useState('all');

  // Policy weights state
  const [parseWeight, setParseWeight] = useState(systemConfig.ats_weights.parseability);
  const [kwWeight, setKwWeight] = useState(systemConfig.ats_weights.keyword_match);
  const [structWeight, setStructWeight] = useState(systemConfig.ats_weights.section_structure);
  const [retentionDays, setRetentionDays] = useState(systemConfig.retention_days);

  const usersList = [
    { id: 'stu_014', name: 'Aarav Mehta', email: 'aarav@example.edu', role: 'Student', cohort: 'PPS4027 A', status: 'Active' },
    { id: 'stu_015', name: 'Nisha Rao', email: 'nisha@example.edu', role: 'Student', cohort: 'PPS4027 A', status: 'Active' },
    { id: 'stu_016', name: 'Sana Ali', email: 'sana@example.edu', role: 'Student', cohort: 'PPS4027 A', status: 'Active' },
    { id: 'trn_007', name: 'Dr. Kavya Shah', email: 'kavya@example.edu', role: 'Trainer', cohort: 'PPS4027 A Lead', status: 'Verified' },
    { id: 'trn_008', name: 'Dr. Nandita Roy', email: 'nandita@faculty.edu', role: 'Trainer', cohort: 'Lead Faculty', status: 'Verified' },
    { id: 'adm_001', name: 'Prof. K. V. Ramanathan', email: 'admin@example.edu', role: 'Admin', cohort: 'All Batches', status: 'Root Token' },
  ];

  const filteredUsers = usersList.filter(u => 
    u.name.toLowerCase().includes(searchDirectory.toLowerCase()) ||
    u.email.toLowerCase().includes(searchDirectory.toLowerCase()) ||
    u.role.toLowerCase().includes(searchDirectory.toLowerCase())
  );

  const filteredAuditLogs = auditLogs.filter(log => {
    const matchesSearch = log.event.toLowerCase().includes(searchAudit.toLowerCase()) ||
      log.actor.toLowerCase().includes(searchAudit.toLowerCase());
    const matchesCategory = auditCategory === 'all' || log.category?.toLowerCase() === auditCategory.toLowerCase();
    return matchesSearch && matchesCategory;
  });

  const handleSavePolicies = (e) => {
    e.preventDefault();
    setSystemConfig({
      ...systemConfig,
      retention_days: Number(retentionDays),
      ats_weights: {
        parseability: Number(parseWeight),
        keyword_match: Number(kwWeight),
        section_structure: Number(structWeight)
      }
    });
    showToast('System governance policies and ATS weights updated successfully.');
  };

  return (
    <div className="flex flex-col w-full pb-16 space-y-6">
      
      {/* Page Header & Academic Governance Action Bar */}
      <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-4 pb-2 border-b border-surface-variant">
        <div className="space-y-1 max-w-3xl">
          <div className="flex items-center gap-2 font-label-sm text-label-sm tracking-wider uppercase text-on-surface-variant">
            <span>Administration Desk</span>
            <span className="text-outline">/</span>
            <span>System Governance</span>
            <span className="text-outline">/</span>
            <span className="text-primary font-semibold">Cohort AY 2024–25</span>
          </div>
          <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight font-bold">
            System Administration & Governance
          </h1>
          <p className="font-body-md text-body-md text-on-surface-variant leading-relaxed">
            Operational controls for course cohort permissions, continuous assessment deadlines, evaluation weighting schemes, and immutable forensic audit logs.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => showToast('Forensic audit report exported.')}
            className="inline-flex items-center gap-1.5 px-3 py-2 bg-surface-container-lowest text-on-surface hover:bg-surface-container font-label-md text-label-md rounded shadow-sm transition-colors border border-surface-variant"
          >
            <span className="material-symbols-outlined text-[18px] text-outline">download</span>
            <span>Export Forensic Audit</span>
          </button>
          <button
            type="button"
            onClick={() => showToast('All policy updates synchronized.')}
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-primary text-on-primary font-label-md text-label-md rounded shadow-sm hover:bg-primary-container transition-colors font-semibold"
          >
            <span className="material-symbols-outlined text-[18px]">policy</span>
            <span>Deploy Policy Changes</span>
          </button>
        </div>
      </div>

      {/* 4 Top Operational KPI Summary Grid */}
      <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {/* KPI 1 */}
        <div className="bg-surface-container-lowest p-5 rounded-xl border border-surface-variant shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
              Active System Users
            </span>
            <span className="material-symbols-outlined text-primary text-[20px]">group</span>
          </div>
          <div className="my-2">
            <div className="font-metric-display text-metric-display text-on-surface font-bold">
              1,248 <span className="font-body-sm text-body-sm text-on-surface-variant font-normal">Total</span>
            </div>
            <p className="font-body-sm text-body-sm text-on-surface-variant mt-0.5">
              1,180 Candidates · 42 Evaluators · 6 Admins
            </p>
          </div>
          <div className="space-y-1 pt-1 border-t border-surface-variant">
            <div className="h-1.5 w-full bg-surface-container rounded-full overflow-hidden flex">
              <div className="h-full bg-primary" style={{ width: '94.5%' }} title="Students (94.5%)"></div>
              <div className="h-full bg-tertiary" style={{ width: '3.4%' }} title="Evaluators (3.4%)"></div>
              <div className="h-full bg-secondary" style={{ width: '2.1%' }} title="Admins (2.1%)"></div>
            </div>
            <div className="flex justify-between font-label-sm text-[11px] text-on-surface-variant">
              <span>94.5% Students</span>
              <span>5.5% Staff</span>
            </div>
          </div>
        </div>

        {/* KPI 2 */}
        <div className="bg-surface-container-lowest p-5 rounded-xl border border-surface-variant shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
              Continuous Assessment
            </span>
            <span className="px-2 py-0.5 text-[11px] font-label-sm font-semibold rounded bg-surface-container text-primary">
              AY 24-25 Q2
            </span>
          </div>
          <div className="my-2">
            <div className="font-metric-display text-metric-display text-on-surface font-bold">
              CA1 Active <span className="font-body-sm text-body-sm text-on-surface-variant font-normal">(30% wt.)</span>
            </div>
            <p className="font-body-sm text-body-sm text-on-surface-variant mt-0.5">
              Hard lock: Sep 24, 2026 · 23:59 IST
            </p>
          </div>
          <div className="space-y-1 pt-1 border-t border-surface-variant">
            <div className="flex items-center justify-between font-label-sm text-[11px]">
              <span className="text-on-surface font-medium">Batch Progress</span>
              <span className="text-tertiary font-bold">94% Submitted</span>
            </div>
            <div className="h-1.5 w-full bg-surface-container rounded-full overflow-hidden">
              <div className="h-full bg-tertiary" style={{ width: '94%' }}></div>
            </div>
          </div>
        </div>

        {/* KPI 3 */}
        <div className="bg-surface-container-lowest p-5 rounded-xl border border-surface-variant shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
              Compliance & Consent
            </span>
            <span className="inline-flex items-center gap-1 font-label-sm text-xs text-tertiary bg-tertiary-fixed/30 px-2 py-0.5 rounded font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-tertiary"></span> Verified
            </span>
          </div>
          <div className="my-2">
            <div className="font-metric-display text-metric-display text-on-surface font-bold">99.4%</div>
            <p className="font-body-sm text-body-sm text-on-surface-variant mt-0.5">
              1,173/1,180 Signed Digital Processing Consent
            </p>
          </div>
          <div className="flex items-center justify-between text-xs text-on-surface-variant pt-1 border-t border-surface-variant">
            <span className="text-outline">7 Pending Reminders</span>
            <span className="font-label-sm text-[11px] text-tertiary font-semibold">FERPA / ISO Compliant</span>
          </div>
        </div>

        {/* KPI 4 */}
        <div className="bg-surface-container-lowest p-5 rounded-xl border border-surface-variant shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
              ATS Engine Ingestion
            </span>
            <span className="font-label-sm text-[11px] px-2 py-0.5 rounded bg-surface-container text-on-surface-variant font-medium">
              v4.2 Active
            </span>
          </div>
          <div className="my-2">
            <div className="font-metric-display text-metric-display text-on-surface font-bold flex items-baseline gap-2">
              <span>Healthy</span>
              <span className="font-body-sm text-body-sm text-on-surface-variant font-normal">1.4s Latency</span>
            </div>
            <p className="font-body-sm text-body-sm text-on-surface-variant mt-0.5">
              Zero parsing queue backlog
            </p>
          </div>
          <div className="flex items-center justify-between text-xs text-on-surface-variant pt-1 border-t border-surface-variant">
            <span>Worker Pool: 8 Cores</span>
            <span className="text-outline">Sync: Operational</span>
          </div>
        </div>
      </section>

      {/* Main Bento Architecture: Left (Directory & Policy) + Right (Audit Trail) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        {/* Left 7 Cols: User Directory & ATS Weights */}
        <div className="lg:col-span-7 space-y-6">
          
          {/* User Directory & Roles */}
          <section className="bg-surface-container-lowest rounded-xl border border-surface-variant shadow-sm overflow-hidden p-6 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h2 className="font-headline-sm text-headline-sm text-on-surface font-bold">Directory & Role Delegation</h2>
                <p className="font-body-sm text-body-sm text-on-surface-variant">
                  Verify RBAC access roles and cohort allocations.
                </p>
              </div>
              <input
                type="text"
                value={searchDirectory}
                onChange={(e) => setSearchDirectory(e.target.value)}
                placeholder="Search user or email..."
                className="px-3 py-1.5 rounded-lg bg-surface-container-low border border-surface-variant text-body-sm focus:outline-none focus:border-primary w-full sm:w-56"
              />
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-body-sm">
                <thead>
                  <tr className="border-b border-surface-variant font-label-sm text-label-sm text-outline uppercase">
                    <th className="py-2.5 px-3">Name</th>
                    <th className="py-2.5 px-3">Role</th>
                    <th className="py-2.5 px-3">Cohort</th>
                    <th className="py-2.5 px-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-surface-variant">
                  {filteredUsers.map((u) => (
                    <tr key={u.id} className="hover:bg-surface-bright">
                      <td className="py-2.5 px-3 font-semibold text-on-surface">
                        {u.name}
                        <span className="block text-outline font-normal text-xs">{u.email}</span>
                      </td>
                      <td className="py-2.5 px-3">
                        <span className="px-2 py-0.5 rounded text-xs font-semibold bg-surface-container text-primary">
                          {u.role}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-on-surface-variant">{u.cohort}</td>
                      <td className="py-2.5 px-3 text-tertiary font-medium">{u.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {/* ATS Engine Scoring Weights & Retention Policy Form */}
          <section className="bg-surface-container-lowest rounded-xl border border-surface-variant shadow-sm p-6 space-y-4">
            <div>
              <h2 className="font-headline-sm text-headline-sm text-on-surface font-bold">ATS Weighting Scheme & Retention Policy</h2>
              <p className="font-body-sm text-body-sm text-on-surface-variant">
                Configure parsing algorithm weights and institutional document lifecycle limits.
              </p>
            </div>

            <form onSubmit={handleSavePolicies} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 bg-surface-container-low p-4 rounded-xl border border-surface-variant">
                <div>
                  <label className="font-label-sm text-label-sm font-semibold text-on-surface block mb-1">
                    Parseability Weight (%)
                  </label>
                  <input
                    type="number"
                    min="10"
                    max="80"
                    value={parseWeight}
                    onChange={(e) => setParseWeight(Number(e.target.value))}
                    className="w-full px-3 py-1.5 rounded bg-surface-container-lowest border border-surface-variant font-bold text-primary"
                  />
                </div>
                <div>
                  <label className="font-label-sm text-label-sm font-semibold text-on-surface block mb-1">
                    Keywords Weight (%)
                  </label>
                  <input
                    type="number"
                    min="10"
                    max="80"
                    value={kwWeight}
                    onChange={(e) => setKwWeight(Number(e.target.value))}
                    className="w-full px-3 py-1.5 rounded bg-surface-container-lowest border border-surface-variant font-bold text-primary"
                  />
                </div>
                <div>
                  <label className="font-label-sm text-label-sm font-semibold text-on-surface block mb-1">
                    Structure Weight (%)
                  </label>
                  <input
                    type="number"
                    min="10"
                    max="80"
                    value={structWeight}
                    onChange={(e) => setStructWeight(Number(e.target.value))}
                    className="w-full px-3 py-1.5 rounded bg-surface-container-lowest border border-surface-variant font-bold text-primary"
                  />
                </div>
              </div>

              <div>
                <label className="font-label-sm text-label-sm font-semibold text-on-surface block mb-1">
                  Document Data Retention Period (Days)
                </label>
                <input
                  type="number"
                  min="30"
                  max="365"
                  value={retentionDays}
                  onChange={(e) => setRetentionDays(Number(e.target.value))}
                  className="w-full sm:w-48 px-3 py-1.5 rounded bg-surface-container-low border border-surface-variant font-bold text-on-surface"
                />
                <span className="font-body-sm text-body-sm text-outline block mt-1">
                  Resumes are auto-purged from server scratch after this duration.
                </span>
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  className="px-5 py-2 rounded bg-primary text-on-primary hover:bg-primary-container font-label-md text-label-md font-semibold transition-colors shadow-sm"
                >
                  Save Policy Configuration
                </button>
              </div>
            </form>
          </section>

        </div>

        {/* Right 5 Cols: Forensic Audit Trail */}
        <div className="lg:col-span-5 space-y-4">
          <section className="bg-surface-container-lowest rounded-xl border border-surface-variant shadow-sm p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-title-md text-title-md text-on-surface font-bold flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary text-[20px]">history_edu</span>
                  <span>Forensic Audit Trail</span>
                </h3>
                <p className="font-body-sm text-body-sm text-on-surface-variant">Immutable activity ledger.</p>
              </div>
            </div>

            <div className="flex gap-2">
              <input
                type="text"
                value={searchAudit}
                onChange={(e) => setSearchAudit(e.target.value)}
                placeholder="Search audit events..."
                className="w-full px-3 py-1.5 rounded-lg bg-surface-container-low border border-surface-variant text-body-sm"
              />
            </div>

            <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
              {filteredAuditLogs.map((log, idx) => (
                <div key={idx} className="p-3.5 rounded-lg bg-surface-container-low border border-surface-variant/60 space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-label-sm text-label-sm font-semibold text-primary">{log.category}</span>
                    <span className="text-outline">{log.time}</span>
                  </div>
                  <p className="font-body-sm text-body-sm text-on-surface font-medium">{log.event}</p>
                  <div className="flex items-center justify-between text-xs text-on-surface-variant pt-1">
                    <span>Actor: {log.actor}</span>
                    <span className="text-tertiary font-semibold">{log.result}</span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>

      </div>

    </div>
  );
};

export default AdminConsolePage;
