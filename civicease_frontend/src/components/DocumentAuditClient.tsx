'use client';

import React, { useState } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { AppHeader } from '@/components/AppHeader';
import { usePersona } from '@/context/PersonaContext';

export function DocumentAuditClient() {
  const { activePersona, personaId, togglePersona, openAffidavit, affidavitSubmitted, language, showToast } =
    usePersona();

  const [zoomLevel, setZoomLevel] = useState(100);
  const [rotation, setRotation] = useState(0);
  const [showOcrBounds, setShowOcrBounds] = useState(true);

  const handleZoomIn = () => setZoomLevel((prev) => Math.min(prev + 15, 150));
  const handleZoomOut = () => setZoomLevel((prev) => Math.max(prev - 15, 75));
  const handleResetZoom = () => setZoomLevel(100);
  const handleRotate = () => setRotation((prev) => (prev + 90) % 360);

  const handleBoxClick = (type: 'name' | 'validity' | 'income') => {
    if (type === 'name' && personaId === 'ramesh' && !affidavitSubmitted) {
      showToast('Opening Form Annexure-B Alias Affidavit Generator...');
      openAffidavit();
    } else if (type === 'validity') {
      showToast('Certificate validity requires renewal through UP e-District portal.');
    } else {
      showToast('Income threshold verified: Below ₹3,00,000 EWS ceiling.');
    }
  };

  const handleExportReport = () => {
    showToast('Preparing Cryptographic Audit Receipt (PDF)...');
    setTimeout(() => {
      window.print();
    }, 600);
  };

  return (
    <div className="min-h-screen bg-background text-on-surface flex">
      <Sidebar />

      <div className="lg:pl-64 pl-0 flex-1 flex flex-col min-h-screen w-full">
        <AppHeader />

        <main className="pt-20 px-4 sm:px-6 lg:px-8 pb-12 flex-1 max-w-7xl w-full mx-auto space-y-6">
          {/* Breadcrumbs & Control Header */}
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-2">
            <div className="flex flex-col gap-1">
              <nav className="flex items-center gap-2 text-xs text-on-surface-variant font-mono flex-wrap">
                <span className="hover:text-primary cursor-pointer">My Documents</span>
                <span className="material-symbols-outlined text-xs">chevron_right</span>
                <span className="hover:text-primary cursor-pointer">Income Certificate</span>
                <span className="material-symbols-outlined text-xs">chevron_right</span>
                <span className="text-secondary font-bold bg-surface-container-low px-2 py-0.5 rounded">
                  AI Audit Report #AUD-7729
                </span>
              </nav>

              <div className="flex flex-wrap items-center gap-3 mt-1">
                <h1 className="font-heading font-extrabold text-xl sm:text-2xl text-primary tracking-tight">
                  AI Document Audit & Synthetic OCR Engine
                </h1>
                {activePersona.status === 'clean' && !affidavitSubmitted ? (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
                    Audit Passed
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-error-container text-on-error-container text-xs font-bold">
                    <span className="w-1.5 h-1.5 rounded-full bg-error animate-pulse"></span>
                    {affidavitSubmitted ? 'Remediation Attached' : 'Action Required'}
                  </span>
                )}
              </div>
            </div>

            {/* Top Action Ribbon */}
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => showToast('Audit history ledger synced: 4 prior scans on record.')}
                className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-surface-container-lowest border border-surface-container-high text-on-surface-variant text-xs font-bold shadow-sm hover:bg-surface-container"
              >
                <span className="material-symbols-outlined text-base">history</span>
                <span>Audit Log</span>
              </button>
              <button
                type="button"
                onClick={handleExportReport}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-primary text-white text-xs font-bold shadow-sm hover:bg-primary-container"
              >
                <span className="material-symbols-outlined text-base">download</span>
                <span>Export Report</span>
              </button>
            </div>
          </div>

          {/* Active Test Scenario Simulation Bar */}
          <div className="p-4 rounded-2xl bg-surface-container-low border border-surface-container-high shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-start md:items-center gap-3">
              <div
                className={`p-2.5 rounded-xl flex items-center justify-center ${
                  personaId === 'ramesh' ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700'
                }`}
              >
                <span className="material-symbols-outlined text-xl">
                  {personaId === 'ramesh' ? 'warning' : 'verified'}
                </span>
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-bold text-outline uppercase tracking-wider">
                    Active Test Scenario
                  </span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-surface-container-highest text-primary">
                    {personaId === 'ramesh' ? 'STRESS TEST #2' : 'OPTIMAL PATH #1'}
                  </span>
                </div>
                <p className="text-xs text-on-surface mt-0.5">
                  <strong className="font-bold text-primary">{activePersona.name}</strong> –{' '}
                  {personaId === 'ramesh'
                    ? 'Broken Case (Name Mismatch & Expired Certificate)'
                    : 'Clean Profile (All certificates valid & clean OCR)'}
                </p>
              </div>
            </div>

            <button
              onClick={togglePersona}
              className="px-4 py-2 rounded-xl bg-surface-container-lowest border border-surface-container-high text-secondary hover:bg-secondary-container/30 text-xs font-bold shadow-sm flex items-center gap-2 self-start md:self-auto transition-colors"
            >
              <span className="material-symbols-outlined text-base">swap_horiz</span>
              <span>Switch to {personaId === 'ramesh' ? 'Asha Sharma (Clean)' : 'Ramesh Kumar (Issues)'}</span>
            </button>
          </div>

          {/* Main 2-Column Split Workspace (50% / 50%) */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            {/* LEFT PANE: Document Inspector (50%) */}
            <div className="lg:col-span-6 flex flex-col gap-4">
              <div className="bg-surface-container-lowest rounded-2xl border border-surface-container-high shadow-sm overflow-hidden">
                {/* Viewer Header */}
                <div className="p-3.5 bg-surface-container-low border-b border-surface-container-high flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-2.5 min-w-0">
                    <span className="material-symbols-outlined text-error text-2xl">picture_as_pdf</span>
                    <div className="flex flex-col min-w-0">
                      <span className="text-xs font-bold text-primary truncate">
                        {personaId === 'ramesh' ? 'income_certificate_ramesh_2022.pdf' : 'income_certificate_asha_2024.pdf'}
                      </span>
                      <span className="font-mono text-[10px] text-on-surface-variant">
                        1.8 MB · 300 DPI High-Res · UID {activePersona.aadhaar}
                      </span>
                    </div>
                  </div>

                  {/* Viewer Toolbar */}
                  <div className="flex items-center gap-1 bg-surface-container-lowest p-1 rounded-xl shadow-sm border border-surface-container-high">
                    <button
                      onClick={handleZoomOut}
                      className="p-1 rounded-lg hover:bg-surface-container text-on-surface-variant"
                      title="Zoom Out"
                    >
                      <span className="material-symbols-outlined text-base">remove</span>
                    </button>
                    <button
                      onClick={handleResetZoom}
                      className="font-mono text-xs text-on-surface px-1.5 font-bold hover:underline"
                      title="Reset Zoom to 100%"
                    >
                      {zoomLevel}%
                    </button>
                    <button
                      onClick={handleZoomIn}
                      className="p-1 rounded-lg hover:bg-surface-container text-on-surface-variant"
                      title="Zoom In"
                    >
                      <span className="material-symbols-outlined text-base">add</span>
                    </button>
                    <div className="h-4 w-px bg-surface-container-high mx-0.5"></div>
                    <button
                      onClick={handleRotate}
                      className="p-1 rounded-lg hover:bg-surface-container text-on-surface-variant"
                      title="Rotate 90 degrees"
                    >
                      <span className="material-symbols-outlined text-base">rotate_right</span>
                    </button>
                    <button
                      onClick={() => setShowOcrBounds(!showOcrBounds)}
                      className={`px-2 py-1 rounded-lg text-[10px] font-bold flex items-center gap-1 transition-colors ${
                        showOcrBounds
                          ? 'bg-secondary text-white shadow-sm'
                          : 'bg-surface-container text-on-surface-variant'
                      }`}
                    >
                      <span className="material-symbols-outlined text-xs">select_all</span>
                      <span>OCR Bounds</span>
                    </button>
                  </div>
                </div>

                {/* Document Viewport Canvas Area */}
                <div className="relative bg-surface-container-high/30 p-4 sm:p-6 flex items-center justify-center overflow-auto min-h-[520px]">
                  {/* Government Form Replica Sheet */}
                  <div
                    style={{
                      transform: `scale(${zoomLevel / 100}) rotate(${rotation}deg)`,
                      transformOrigin: 'center center',
                    }}
                    className="relative w-full max-w-[460px] bg-white rounded-xl shadow-xl p-6 transition-transform duration-300 text-slate-800 border border-slate-200"
                  >
                    {/* Watermark */}
                    <div className="absolute inset-0 flex items-center justify-center opacity-5 pointer-events-none select-none">
                      <span className="font-heading text-4xl sm:text-5xl font-extrabold tracking-widest text-primary rotate-45">
                        REVENUE DEPT
                      </span>
                    </div>

                    {/* Certificate Header */}
                    <div className="text-center pb-3 mb-3 border-b border-slate-200 relative">
                      <div className="flex items-center justify-center gap-2 mb-1.5">
                        <span className="material-symbols-outlined text-2xl text-primary">account_balance</span>
                        <span className="material-symbols-outlined text-2xl text-secondary">verified</span>
                      </div>
                      <p className="text-[9px] uppercase tracking-wider text-slate-500 font-semibold">
                        Government of Uttar Pradesh / उत्तर प्रदेश शासन
                      </p>
                      <h2 className="font-heading font-bold text-xs uppercase text-primary tracking-tight">
                        Office of the Tehsildar, Revenue Council
                      </h2>
                      <p className="text-[10px] font-semibold text-secondary mt-0.5">
                        CERTIFICATE OF ANNUAL HOUSEHOLD INCOME / आय प्रमाण पत्र
                      </p>
                      <div className="flex items-center justify-between text-[9px] font-mono text-slate-600 mt-2 px-2 py-1 bg-slate-50 rounded">
                        <span>Application No: UP-REV/2022/94821</span>
                        <span>Date of Issue: 12-04-2022</span>
                      </div>
                    </div>

                    {/* Certificate Body & Interactive OCR Overlays */}
                    <div className="space-y-3 text-[11px] leading-relaxed">
                      <p className="text-justify text-slate-600 text-[10px]">
                        This is to certify that the individual named below has been verified as a statutory resident under Tehsil Sadar administrative jurisdiction.
                      </p>

                      {/* Field 1: Name (Red Box on Ramesh, Green on Asha) */}
                      <div
                        onClick={() => handleBoxClick('name')}
                        className={`p-2 rounded-lg border-2 transition-all relative cursor-pointer ${
                          showOcrBounds && personaId === 'ramesh' && !affidavitSubmitted
                            ? 'border-red-500 bg-red-50/70 hover:bg-red-100/70 shadow-sm'
                            : 'border-emerald-500 bg-emerald-50/70'
                        }`}
                        title="Click to view details or generate affidavit"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-semibold text-slate-500">1. Legal Citizen Name:</span>
                          {showOcrBounds && (
                            <span
                              className={`text-[9px] font-mono font-bold px-1.5 py-0.2 rounded ${
                                personaId === 'ramesh' && !affidavitSubmitted
                                  ? 'bg-red-600 text-white'
                                  : 'bg-emerald-600 text-white'
                              }`}
                            >
                              {personaId === 'ramesh' && !affidavitSubmitted
                                ? 'Name Mismatch [FAIL - CLICK TO FIX]'
                                : 'Name Verified [PASS]'}
                            </span>
                          )}
                        </div>
                        <p className="font-bold text-xs text-slate-900 mt-0.5">
                          {personaId === 'ramesh' ? 'Ramesh Kr.' : 'Asha Sharma'}
                        </p>
                      </div>

                      {/* Field 2: Expiration Date (Amber on Ramesh, Green on Asha) */}
                      <div
                        onClick={() => handleBoxClick('validity')}
                        className={`p-2 rounded-lg border-2 transition-all relative cursor-pointer ${
                          showOcrBounds && personaId === 'ramesh'
                            ? 'border-amber-500 bg-amber-50/70 hover:bg-amber-100/70'
                            : 'border-emerald-500 bg-emerald-50/70'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-semibold text-slate-500">2. Certificate Validity:</span>
                          {showOcrBounds && (
                            <span
                              className={`text-[9px] font-mono font-bold px-1.5 py-0.2 rounded ${
                                personaId === 'ramesh' ? 'bg-amber-600 text-white' : 'bg-emerald-600 text-white'
                              }`}
                            >
                              {personaId === 'ramesh' ? 'Expired 31-03-2024 [WARN]' : 'Valid FY 2024-25 [PASS]'}
                            </span>
                          )}
                        </div>
                        <p className="font-bold text-xs text-slate-900 mt-0.5">
                          {personaId === 'ramesh' ? 'Valid until: 31-03-2024' : 'Valid until: 31-03-2025'}
                        </p>
                      </div>

                      {/* Field 3: Declared Income (Green) */}
                      <div
                        onClick={() => handleBoxClick('income')}
                        className={`p-2 rounded-lg border-2 transition-all relative cursor-pointer ${
                          showOcrBounds ? 'border-emerald-500 bg-emerald-50/70' : 'border-slate-200'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-semibold text-slate-500">3. Verified Annual Income:</span>
                          {showOcrBounds && (
                            <span className="text-[9px] font-mono font-bold px-1.5 py-0.2 rounded bg-emerald-600 text-white">
                              Income Below EWS Cap [PASS]
                            </span>
                          )}
                        </div>
                        <p className="font-bold text-xs text-slate-900 mt-0.5">
                          {personaId === 'ramesh'
                            ? '₹ 1,20,000 (Rupees One Lakh Twenty Thousand Only)'
                            : '₹ 1,80,000 (Rupees One Lakh Eighty Thousand Only)'}
                        </p>
                      </div>

                      {/* Seal & Signature */}
                      <div className="pt-3 flex items-center justify-between border-t border-slate-200">
                        <div className="flex items-center gap-1.5 text-[9px] text-slate-500">
                          <span className="material-symbols-outlined text-secondary text-sm">verified</span>
                          <span>Digital Signature Verified (Tehsildar V.K. Saxena)</span>
                        </div>
                        <span className="text-[9px] font-mono text-slate-400">SHA-256: 9f8a...34e1</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* RIGHT PANE: Automated Audit Assessment (50%) */}
            <div className="lg:col-span-6 space-y-5">
              {/* Metric Gauges */}
              <div className="grid grid-cols-3 gap-3">
                <div className="p-3.5 rounded-2xl bg-surface-container-lowest border border-surface-container-high shadow-sm text-center">
                  <span className="text-[10px] font-bold text-outline uppercase block">Clarity Score</span>
                  <span className="font-heading font-extrabold text-xl text-primary mt-1 block">94%</span>
                  <span className="text-[10px] text-secondary font-semibold">High Resolution</span>
                </div>
                <div className="p-3.5 rounded-2xl bg-surface-container-lowest border border-surface-container-high shadow-sm text-center">
                  <span className="text-[10px] font-bold text-outline uppercase block">OCR Confidence</span>
                  <span className="font-heading font-extrabold text-xl text-primary mt-1 block">98.2%</span>
                  <span className="text-[10px] text-secondary font-semibold">Sub-mm Alignment</span>
                </div>
                <div className="p-3.5 rounded-2xl bg-surface-container-lowest border border-surface-container-high shadow-sm text-center">
                  <span className="text-[10px] font-bold text-outline uppercase block">Scheme Readiness</span>
                  <span
                    className={`font-heading font-extrabold text-xl mt-1 block ${
                      activePersona.status === 'clean' ? 'text-secondary' : 'text-error'
                    }`}
                  >
                    {activePersona.status === 'clean' ? '85%' : '33%'}
                  </span>
                  <span className="text-[10px] text-outline font-semibold">
                    {activePersona.status === 'clean' ? '1 Minor Warning' : 'Disqualified in 4'}
                  </span>
                </div>
              </div>

              {/* Structured Findings */}
              <div className="p-5 rounded-2xl bg-surface-container-lowest border border-surface-container-high shadow-sm space-y-4">
                <h3 className="font-heading font-bold text-sm text-primary">
                  Structured Verification Findings (4 Evaluated)
                </h3>

                {personaId === 'ramesh' && !affidavitSubmitted ? (
                  <div className="space-y-3 text-xs">
                    {/* Error 1 */}
                    <div className="p-3.5 rounded-xl bg-red-50 border border-red-200 text-red-900 space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="font-bold flex items-center gap-1.5">
                          <span className="material-symbols-outlined text-red-600 text-base">error</span>
                          Blocking Error 1: Citizen Name Abbreviation Mismatch
                        </span>
                        <span className="px-2 py-0.5 rounded bg-red-200 text-red-900 text-[10px] font-bold font-mono">
                          BLOCKING
                        </span>
                      </div>
                      <p className="text-[11px] text-red-800 leading-relaxed">
                        Detected abbreviation <strong>Ramesh Kr.</strong> on revenue record vs <strong>Ramesh Kumar</strong> on UIDAI Aadhaar registry.
                      </p>
                      <div className="p-2.5 bg-white rounded-lg border border-red-200 text-[11px] text-slate-800 space-y-1">
                        <p>
                          <strong>Why it matters:</strong> Automated portal scrutiny flags initials as distinct identities, causing 68% of automated welfare rejections.
                        </p>
                        <p className="text-secondary font-bold">
                          <strong>AI Resolution:</strong> Generate and attach Form Annexure-B Alias Affidavit (1-Click available below).
                        </p>
                      </div>
                    </div>

                    {/* Warning 2 */}
                    <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="font-bold flex items-center gap-1.5">
                          <span className="material-symbols-outlined text-amber-600 text-base">warning</span>
                          Warning 2: Certificate Validity Exceeded
                        </span>
                        <span className="px-2 py-0.5 rounded bg-amber-200 text-amber-900 text-[10px] font-bold font-mono">
                          LAPSED
                        </span>
                      </div>
                      <p className="text-[11px] text-amber-800 leading-relaxed">
                        Certificate validity expired on <strong>31-03-2024</strong> (~6 months ago). PMAY-U 2.0 requires active FY 2024-25 proof.
                      </p>
                    </div>

                    {/* Passed Checks */}
                    <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-[11px] space-y-1">
                      <span className="font-bold flex items-center gap-1">
                        <span className="material-symbols-outlined text-emerald-600 text-sm">verified</span>
                        Passed Integrity Checks:
                      </span>
                      <ul className="list-disc pl-4 space-y-0.5 text-emerald-800">
                        <li>Official Tehsildar Digital Seal and Hologram Authenticated</li>
                        <li>Household income (₹1,20,000) within EWS threshold (&lt; ₹3,00,000)</li>
                      </ul>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3 text-xs">
                    <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 space-y-1">
                      <span className="font-bold flex items-center gap-1.5">
                        <span className="material-symbols-outlined text-emerald-600 text-base">verified</span>
                        {affidavitSubmitted
                          ? 'Annexure-B Affidavit Bound: Name Variance Resolved'
                          : '100% Name & Credential Match Passed'}
                      </span>
                      <p className="text-[11px] text-emerald-800 leading-relaxed">
                        {affidavitSubmitted
                          ? 'Cryptographic Form Annexure-B alias declaration successfully authenticated. Rejection probability reduced from 68% to 0%.'
                          : 'Full legal name matches Aadhaar UID without discrepancies. High-confidence synthetic OCR pass.'}
                      </p>
                    </div>

                    <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 space-y-1">
                      <span className="font-bold flex items-center gap-1.5">
                        <span className="material-symbols-outlined text-amber-600 text-base">schedule</span>
                        Expiring Soon (18 Days Left)
                      </span>
                      <p className="text-[11px] text-amber-800 leading-relaxed">
                        Income certificate is valid through 31-Oct-2024. Eligible for immediate PM SVANidhi submission.
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {/* Sovereign Human Safeguard Gate Actions */}
              <div className="p-5 rounded-2xl bg-surface-container-lowest border border-surface-container-high shadow-sm space-y-3">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-purple-700 text-lg">gavel</span>
                  <h3 className="font-heading font-bold text-xs uppercase tracking-wider text-purple-900">
                    Sovereign Human Safeguard Gate
                  </h3>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  <button
                    onClick={openAffidavit}
                    className="p-3 rounded-xl bg-secondary hover:bg-secondary/90 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-sm transition-all"
                  >
                    <span className="material-symbols-outlined text-sm">gavel</span>
                    <span>Attach Annexure-B Affidavit</span>
                  </button>

                  <button
                    onClick={() => showToast('Opening Document Upload Enclave for renewed proof...')}
                    className="p-3 rounded-xl bg-surface-container-low hover:bg-surface-container text-primary font-bold text-xs flex items-center justify-center gap-2 border border-surface-container-high transition-colors"
                  >
                    <span className="material-symbols-outlined text-sm">cloud_upload</span>
                    <span>Upload Renewed Document</span>
                  </button>

                  <button
                    onClick={() => showToast('CSC Kendra volunteer officer flagged for physical verification.')}
                    className="p-3 rounded-xl bg-surface-container-low hover:bg-surface-container text-on-surface-variant font-medium text-xs flex items-center justify-center gap-2 border border-surface-container-high transition-colors"
                  >
                    <span className="material-symbols-outlined text-sm">support_agent</span>
                    <span>Request Officer Review</span>
                  </button>

                  <button
                    onClick={handleExportReport}
                    className="p-3 rounded-xl bg-surface-container-low hover:bg-surface-container text-on-surface-variant font-medium text-xs flex items-center justify-center gap-2 border border-surface-container-high transition-colors"
                  >
                    <span className="material-symbols-outlined text-sm">receipt_long</span>
                    <span>Download Audit PDF</span>
                  </button>
                </div>

                {/* Audit Hash */}
                <div className="pt-2 text-center text-[10px] font-mono text-outline">
                  SHA-256 Non-repudiation Guaranteed · Audit Hash: 9f8a42b109c8e1
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
