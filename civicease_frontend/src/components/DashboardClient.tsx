'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Sidebar } from '@/components/Sidebar';
import { AppHeader } from '@/components/AppHeader';
import { usePersona } from '@/context/PersonaContext';

export function DashboardClient() {
  const router = useRouter();
  const { activePersona, personaId, togglePersona, language, openAffidavit, affidavitSubmitted, showToast } =
    usePersona();
  const [copilotInput, setCopilotInput] = useState('');
  const [isScanning, setIsScanning] = useState(false);

  const handleReScan = () => {
    setIsScanning(true);
    showToast('Connecting to Central Gazette API v24.8.2 & MahaDBT endpoints...');
    setTimeout(() => {
      setIsScanning(false);
      showToast('Gazette sync complete! 3 New Schemes indexed for Maharashtra/UP.');
    }, 1500);
  };

  const handleCopilotSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!copilotInput.trim()) return;
    router.push(`/assistant?q=${encodeURIComponent(copilotInput)}`);
  };

  return (
    <div className="min-h-screen bg-background text-on-surface flex">
      <Sidebar />

      <div className="lg:pl-64 pl-0 flex-1 flex flex-col min-h-screen w-full">
        <AppHeader />

        <main className="pt-20 px-4 sm:px-6 lg:px-8 pb-12 flex-1 max-w-7xl w-full mx-auto space-y-6">
          {/* Greeting & Persona Switcher */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-surface-container-low p-4 sm:p-5 rounded-2xl border border-surface-container-high shadow-sm">
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-heading font-extrabold text-xl sm:text-2xl text-primary">
                  {language === 'en'
                    ? `Namaste, ${activePersona.name.split(' ')[0]}! 👋`
                    : `नमस्ते, ${activePersona.nameHi}! 👋`}
                </h1>
                <span className="px-2 py-0.5 rounded-full bg-secondary-fixed text-on-secondary-fixed text-[10px] font-mono font-bold">
                  SOVEREIGN VAULT LIVE
                </span>
              </div>
              <p className="text-xs text-on-surface-variant mt-1">
                {activePersona.domicile} · {activePersona.occupation} · UIDAI {activePersona.aadhaar}
              </p>
            </div>

            {/* Persona Switcher Banner */}
            <div className="flex items-center gap-2 bg-white p-1 rounded-xl border border-surface-container-high shadow-sm self-start md:self-auto">
              <span className="text-[11px] font-semibold text-outline px-1.5 hidden sm:inline">
                Test Scenario:
              </span>
              <button
                onClick={togglePersona}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
                  personaId === 'asha'
                    ? 'bg-secondary text-white shadow-sm'
                    : 'bg-surface-container-low text-on-surface hover:bg-surface-container'
                }`}
              >
                <span>Asha (Clean)</span>
                {personaId === 'asha' && <span className="material-symbols-outlined text-xs">check</span>}
              </button>
              <button
                onClick={togglePersona}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
                  personaId === 'ramesh'
                    ? 'bg-amber-600 text-white shadow-sm'
                    : 'bg-surface-container-low text-on-surface hover:bg-surface-container'
                }`}
              >
                <span>Ramesh (Edge Case)</span>
                {personaId === 'ramesh' && <span className="material-symbols-outlined text-xs">check</span>}
              </button>
            </div>
          </div>

          {/* Autonomous Onboarding Track (5 Stages) */}
          <div className="p-4 rounded-2xl bg-surface-container-lowest border border-surface-container-high shadow-sm overflow-x-auto">
            <div className="flex items-center justify-between min-w-[700px] gap-2">
              {[
                { stage: '01 / DISCOVER', status: 'Completed', detail: '18 Matches', icon: 'check_circle', color: 'text-secondary' },
                { stage: '02 / QUALIFY', status: 'Completed', detail: '98% Deterministic', icon: 'check_circle', color: 'text-secondary' },
                {
                  stage: '03 / AUDIT',
                  status: activePersona.status === 'clean' ? 'Action Needed' : 'Discrepancy Block',
                  detail:
                    activePersona.status === 'clean'
                      ? 'Income Cert Expiring'
                      : affidavitSubmitted
                      ? 'Affidavit Attached'
                      : 'Name Mismatch',
                  icon: 'warning',
                  color: 'text-amber-500',
                  active: true,
                },
                { stage: '04 / PREPARE', status: 'In Progress', detail: 'PM SVANidhi Drafted', icon: 'sync', color: 'text-primary' },
                { stage: '05 / TRACK', status: 'Awaiting Human Gate', detail: '1 Ready to Sign', icon: 'fingerprint', color: 'text-purple-600' },
              ].map((step, idx) => (
                <div
                  key={idx}
                  className={`flex-1 p-2.5 rounded-xl border flex items-center gap-2.5 transition-all ${
                    step.active
                      ? 'bg-amber-50/60 border-amber-300 ring-1 ring-amber-200'
                      : 'bg-surface-container-low/40 border-surface-container-high'
                  }`}
                >
                  <span className={`material-symbols-outlined text-xl ${step.color}`}>{step.icon}</span>
                  <div className="flex flex-col min-w-0">
                    <span className="text-[10px] font-mono font-bold text-outline">{step.stage}</span>
                    <span className="text-xs font-bold text-primary truncate">{step.detail}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 4 Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-5 rounded-2xl bg-surface-container-lowest border border-surface-container-high shadow-sm flex flex-col justify-between">
              <div className="flex items-center justify-between text-secondary">
                <span className="text-xs font-bold uppercase tracking-wider text-outline">Potential Welfare Value</span>
                <span className="material-symbols-outlined text-xl">payments</span>
              </div>
              <div className="mt-3">
                <span className="font-heading font-extrabold text-2xl text-primary">{activePersona.welfareValue}</span>
                <p className="text-[11px] text-secondary font-semibold mt-1 flex items-center gap-1">
                  <span className="material-symbols-outlined text-xs">trending_up</span> 3 Grants Available
                </p>
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-surface-container-lowest border border-surface-container-high shadow-sm flex flex-col justify-between">
              <div className="flex items-center justify-between text-primary">
                <span className="text-xs font-bold uppercase tracking-wider text-outline">Schemes Matched</span>
                <span className="material-symbols-outlined text-xl">travel_explore</span>
              </div>
              <div className="mt-3">
                <span className="font-heading font-extrabold text-2xl text-primary">{activePersona.schemesMatchedCount}</span>
                <p className="text-[11px] text-on-surface-variant font-medium mt-1">
                  4 Ready to Apply · 8 Likely
                </p>
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-surface-container-lowest border border-surface-container-high shadow-sm flex flex-col justify-between">
              <div className="flex items-center justify-between text-amber-600">
                <span className="text-xs font-bold uppercase tracking-wider text-outline">Document Health</span>
                <span className="material-symbols-outlined text-xl">fact_check</span>
              </div>
              <div className="mt-3">
                <div className="flex items-baseline gap-2">
                  <span className="font-heading font-extrabold text-2xl text-primary">{activePersona.docHealth}%</span>
                  <span className="text-xs font-bold text-amber-600">
                    {activePersona.status === 'clean' ? '1 Warning' : '2 Errors'}
                  </span>
                </div>
                <div className="w-full bg-surface-container-high h-1.5 rounded-full mt-2 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ${
                      activePersona.docHealth > 70 ? 'bg-secondary' : 'bg-red-500'
                    }`}
                    style={{ width: `${activePersona.docHealth}%` }}
                  ></div>
                </div>
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-surface-container-lowest border border-surface-container-high shadow-sm flex flex-col justify-between">
              <div className="flex items-center justify-between text-purple-700">
                <span className="text-xs font-bold uppercase tracking-wider text-outline">Active Applications</span>
                <span className="material-symbols-outlined text-xl">assignment_turned_in</span>
              </div>
              <div className="mt-3">
                <span className="font-heading font-extrabold text-2xl text-primary">2 Active</span>
                <p className="text-[11px] text-purple-700 font-semibold mt-1 flex items-center gap-1">
                  <span className="material-symbols-outlined text-xs">lock_person</span> 1 Awaiting Citizen OTP
                </p>
              </div>
            </div>
          </div>

          {/* Urgent Notification Banner */}
          {activePersona.status === 'clean' ? (
            <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-amber-900 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-amber-200/60 text-amber-800">
                  <span className="material-symbols-outlined text-xl">warning</span>
                </div>
                <div>
                  <h4 className="text-xs font-bold">State Income Certificate Expiring in 18 Days</h4>
                  <p className="text-[11px] text-amber-800 mt-0.5">
                    Your income proof issued on 14-Oct-2023 requires annual renewal for PMAY-Urban 2.0 eligibility.
                  </p>
                </div>
              </div>
              <Link
                href="/documents/audit"
                className="px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold flex items-center justify-center gap-1 shadow-sm transition-colors whitespace-nowrap"
              >
                <span>Audit & Fix Scan</span>
                <span className="material-symbols-outlined text-sm">arrow_forward</span>
              </Link>
            </div>
          ) : (
            <div className="p-4 rounded-2xl bg-red-50 border border-red-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-red-900 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-red-200/60 text-red-700">
                  <span className="material-symbols-outlined text-xl">error</span>
                </div>
                <div>
                  <h4 className="text-xs font-bold">Blocking Clerical Mismatch Detected (#AUD-7729)</h4>
                  <p className="text-[11px] text-red-800 mt-0.5">
                    Name appears as <strong>Ramesh Kr.</strong> on Income Certificate vs <strong>Ramesh Kumar</strong> on Aadhaar. 68% chance of automated portal rejection.
                  </p>
                </div>
              </div>
              <button
                onClick={openAffidavit}
                className="px-4 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white text-xs font-bold flex items-center justify-center gap-1 shadow-sm transition-colors whitespace-nowrap"
              >
                <span>Generate Annexure-B Affidavit</span>
                <span className="material-symbols-outlined text-sm">gavel</span>
              </button>
            </div>
          )}

          {/* Main 2-Column Dashboard Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            {/* Left 8 Cols: Recommended Schemes & Gazette Feed */}
            <div className="lg:col-span-8 space-y-6">
              {/* Sovereign Entitlement Engine Header */}
              <div className="bg-surface-container-lowest p-5 sm:p-6 rounded-2xl border border-surface-container-high shadow-sm space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-secondary text-xl">auto_awesome</span>
                    <h2 className="font-heading font-bold text-lg text-primary">Sovereign Entitlement Engine</h2>
                  </div>
                  <Link href="/schemes" className="text-xs font-bold text-secondary hover:underline flex items-center gap-0.5">
                    <span>View All 18</span>
                    <span className="material-symbols-outlined text-sm">chevron_right</span>
                  </Link>
                </div>

                <div className="space-y-3">
                  {/* Scheme 1 */}
                  <div className="p-4 rounded-xl bg-surface-container-low border border-surface-container-high hover:border-secondary/40 transition-all">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold text-primary">PM SVANidhi (Street Vendor Loan)</span>
                          <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold">
                            98% Match
                          </span>
                        </div>
                        <p className="text-xs text-on-surface-variant">
                          Ministry of Housing & Urban Affairs · Up to ₹50,000 credit with 7% interest rebate.
                        </p>
                        <div className="flex items-center gap-3 text-[11px] text-outline pt-1">
                          <span className="text-secondary font-semibold flex items-center gap-1">
                            <span className="material-symbols-outlined text-xs">check_circle</span> 3 of 3 Docs Ready
                          </span>
                          <span>•</span>
                          <span>Direct DBT to Bank</span>
                        </div>
                      </div>
                      <Link
                        href="/assistant"
                        className="px-4 py-2 rounded-xl bg-primary hover:bg-primary-container text-white text-xs font-bold whitespace-nowrap self-start sm:self-center shadow-sm"
                      >
                        Prepare Dossier
                      </Link>
                    </div>
                  </div>

                  {/* Scheme 2 */}
                  <div className="p-4 rounded-xl bg-surface-container-low border border-surface-container-high hover:border-secondary/40 transition-all">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold text-primary">Pradhan Mantri Awas Yojana (PMAY-U 2.0)</span>
                          <span className="px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 text-[10px] font-bold">
                            94% Match
                          </span>
                        </div>
                        <p className="text-xs text-on-surface-variant">
                          Urban housing interest subsidy up to ₹1,80,000 for EWS income category.
                        </p>
                        <div className="flex items-center gap-3 text-[11px] text-outline pt-1">
                          <span className="text-amber-600 font-semibold flex items-center gap-1">
                            <span className="material-symbols-outlined text-xs">warning</span> Income Proof Needs Refresh
                          </span>
                        </div>
                      </div>
                      <Link
                        href="/documents/audit"
                        className="px-4 py-2 rounded-xl bg-surface-container-lowest text-primary border border-surface-container-high hover:bg-surface-container text-xs font-bold whitespace-nowrap self-start sm:self-center"
                      >
                        Audit Document
                      </Link>
                    </div>
                  </div>

                  {/* Scheme 3 */}
                  <div className="p-4 rounded-xl bg-surface-container-low border border-surface-container-high hover:border-secondary/40 transition-all">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold text-primary">Ayushman Bharat - PM-JAY</span>
                          <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold">
                            100% Match
                          </span>
                        </div>
                        <p className="text-xs text-on-surface-variant">
                          ₹5,00,000 annual secondary & tertiary health cover per family. SECC 2011 mapped.
                        </p>
                        <div className="flex items-center gap-3 text-[11px] text-outline pt-1">
                          <span className="text-secondary font-semibold flex items-center gap-1">
                            <span className="material-symbols-outlined text-xs">check_circle</span> Instant e-Card Eligible
                          </span>
                        </div>
                      </div>
                      <Link
                        href="/schemes"
                        className="px-4 py-2 rounded-xl bg-surface-container-lowest text-primary border border-surface-container-high hover:bg-surface-container text-xs font-bold whitespace-nowrap self-start sm:self-center"
                      >
                        View Details
                      </Link>
                    </div>
                  </div>
                </div>
              </div>

              {/* Real-Time Gazette Ingestion Widget */}
              <div className="bg-surface-container-lowest p-5 rounded-2xl border border-surface-container-high shadow-sm space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-secondary text-base">rss_feed</span>
                    <h3 className="text-xs font-bold text-primary uppercase tracking-wider">
                      Real-Time Gazette Ingestion Feed (v24.8.2)
                    </h3>
                  </div>
                  <button
                    onClick={handleReScan}
                    disabled={isScanning}
                    className="text-[11px] font-bold text-secondary hover:underline flex items-center gap-1 disabled:opacity-50"
                  >
                    <span className={`material-symbols-outlined text-xs ${isScanning ? 'animate-spin' : ''}`}>
                      refresh
                    </span>
                    <span>{isScanning ? 'Scanning...' : 'Re-Scan'}</span>
                  </button>
                </div>

                <div className="space-y-2 text-xs">
                  <div className="p-3 rounded-xl bg-surface-container-low flex items-start justify-between gap-3">
                    <div>
                      <span className="font-bold text-primary block">MoHUA Gazette Ext. 882/2026</span>
                      <span className="text-on-surface-variant text-[11px]">
                        PM SVANidhi 3rd Tranche loan ceiling increased to ₹50,000 with 7% rebate.
                      </span>
                    </div>
                    <span className="text-[10px] font-mono text-outline whitespace-nowrap">2h ago</span>
                  </div>
                  <div className="p-3 rounded-xl bg-surface-container-low flex items-start justify-between gap-3">
                    <div>
                      <span className="font-bold text-primary block">Maharashtra GR #MHD-901</span>
                      <span className="text-on-surface-variant text-[11px]">
                        MahaDBT income threshold updated to ₹2,50,000 for non-creamy layer OBC.
                      </span>
                    </div>
                    <span className="text-[10px] font-mono text-outline whitespace-nowrap">5h ago</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Right 4 Cols: Copilot & Deadlines */}
            <div className="lg:col-span-4 space-y-6">
              {/* Civic AI Copilot Mini-Card */}
              <div className="bg-primary-container text-on-primary p-5 rounded-2xl shadow-lg border border-primary-container space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-secondary-fixed/20 flex items-center justify-center text-secondary-fixed">
                      <span className="material-symbols-outlined text-lg">smart_toy</span>
                    </div>
                    <div>
                      <h3 className="text-xs font-bold text-white">Civic AI Copilot</h3>
                      <span className="text-[10px] text-secondary-fixed font-mono">Vernacular Reasoning Active</span>
                    </div>
                  </div>
                  <span className="w-2 h-2 rounded-full bg-secondary-fixed animate-pulse"></span>
                </div>

                <p className="text-xs text-on-primary-container leading-relaxed">
                  "Ask me about any central or state subsidy, upload a blurry passbook to audit, or verify your caste certificate."
                </p>

                {/* Copilot Input */}
                <form onSubmit={handleCopilotSubmit} className="relative">
                  <input
                    type="text"
                    value={copilotInput}
                    onChange={(e) => setCopilotInput(e.target.value)}
                    placeholder="Ask in Hindi, English, Marathi..."
                    className="w-full h-10 pl-3 pr-9 bg-white/10 rounded-xl text-xs text-white placeholder:text-white/50 border border-white/20 focus:outline-none focus:ring-1 focus:ring-secondary-fixed"
                  />
                  <button
                    type="submit"
                    className="absolute right-1.5 top-1.5 w-7 h-7 rounded-lg bg-secondary text-white flex items-center justify-center hover:opacity-90"
                  >
                    <span className="material-symbols-outlined text-sm">arrow_forward</span>
                  </button>
                </form>

                {/* Quick Prompts */}
                <div className="flex flex-col gap-1.5 pt-1">
                  <Link
                    href="/assistant?q=Check%20PM%20SVANidhi%20eligibility"
                    className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-[11px] text-white/90 border border-white/10 transition-colors flex items-center justify-between"
                  >
                    <span>Check PM SVANidhi eligibility</span>
                    <span className="material-symbols-outlined text-xs text-secondary-fixed">arrow_forward</span>
                  </Link>
                  <Link
                    href="/documents/audit"
                    className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-[11px] text-white/90 border border-white/10 transition-colors flex items-center justify-between"
                  >
                    <span>Audit Income Certificate OCR</span>
                    <span className="material-symbols-outlined text-xs text-secondary-fixed">arrow_forward</span>
                  </Link>
                </div>
              </div>

              {/* Upcoming Deadlines Widget */}
              <div className="bg-surface-container-lowest p-5 rounded-2xl border border-surface-container-high shadow-sm space-y-3">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary text-base">event</span>
                  <h3 className="text-xs font-bold text-primary uppercase tracking-wider">Upcoming Deadlines</h3>
                </div>

                <div className="space-y-3 text-xs">
                  <div className="p-3 rounded-xl bg-surface-container-low border-l-4 border-l-amber-500 flex flex-col gap-1">
                    <span className="font-bold text-primary">National Means-cum-Merit Scholarship</span>
                    <span className="text-[11px] text-outline">State Education Dept · Closes 30 Oct</span>
                    <span className="text-[10px] font-mono font-bold text-amber-700">9 Days Left</span>
                  </div>

                  <div className="p-3 rounded-xl bg-surface-container-low border-l-4 border-l-secondary flex flex-col gap-1">
                    <span className="font-bold text-primary">Ayushman Bharat e-KYC Verification</span>
                    <span className="text-[11px] text-outline">NHA Portal · Closes 15 Nov</span>
                    <span className="text-[10px] font-mono font-bold text-secondary">25 Days Left</span>
                  </div>
                </div>
              </div>

              {/* Human Safeguard Charter Notice */}
              <div className="p-4 rounded-2xl bg-purple-50 border border-purple-200 text-purple-900 text-xs leading-relaxed space-y-2">
                <div className="flex items-center gap-1.5 font-bold">
                  <span className="material-symbols-outlined text-base text-purple-700">security</span>
                  <span>Human-in-the-Loop Safeguard</span>
                </div>
                <p className="text-[11px]">
                  CivicEase AI operates strictly as your preparatory assistant. Autonomous submission without citizen biometric or OTP sign-off is technically and legally prohibited (§4.2 Sovereign Protocol).
                </p>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
