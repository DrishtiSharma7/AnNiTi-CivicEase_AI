'use client';

import React, { useState } from 'react';
import { usePersona } from '@/context/PersonaContext';

export const AffidavitModal = () => {
  const { isAffidavitOpen, closeAffidavit, submitAffidavit, activePersona, language } = usePersona();
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isAffidavitOpen) return null;

  const handleGenerate = () => {
    setIsSubmitting(true);
    setTimeout(() => {
      setIsSubmitting(false);
      submitAffidavit();
    }, 1200);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="relative w-full max-w-2xl bg-surface-container-lowest rounded-2xl shadow-2xl border border-surface-container-high overflow-hidden">
        {/* Header */}
        <div className="bg-primary-container text-on-primary p-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-secondary-container/20 flex items-center justify-center text-secondary-fixed">
              <span className="material-symbols-outlined text-2xl">gavel</span>
            </div>
            <div>
              <h3 className="font-heading font-bold text-base text-white">
                Statutory Affidavit Generator (Form Annexure-B)
              </h3>
              <p className="text-xs text-secondary-fixed">
                Sovereign Discrepancy Remediation Under Gazette Notification §14-A
              </p>
            </div>
          </div>
          <button
            onClick={closeAffidavit}
            className="p-1 rounded-lg text-white/70 hover:text-white hover:bg-white/10 transition-colors"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4 max-h-[70vh] overflow-y-auto text-xs leading-relaxed">
          <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 flex items-start gap-3">
            <span className="material-symbols-outlined text-amber-600 text-xl mt-0.5">warning</span>
            <div>
              <p className="font-bold">Detected Clerical Variance</p>
              <p className="mt-0.5 text-[11px]">
                Income Certificate records name as <span className="font-mono font-bold bg-white px-1 py-0.5 rounded border border-amber-300">Ramesh Kr.</span> whereas Aadhaar registry records <span className="font-mono font-bold bg-white px-1 py-0.5 rounded border border-amber-300">Ramesh Kumar</span>.
              </p>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-surface-container-low border border-surface-container-high font-mono text-[11px] leading-normal text-on-surface space-y-2">
            <div className="text-center font-bold pb-2 border-b border-surface-container-high uppercase tracking-wide">
              BEFORE THE EXECUTIVE MAGISTRATE / NOTARY PUBLIC, TEHSIL SADAR
            </div>
            <p>
              I, <strong>RAMESH KUMAR</strong>, S/o Shri Ram Lal, residing at Tehsil Sadar, District Lucknow, Uttar Pradesh, do hereby solemnly affirm and declare on oath:
            </p>
            <p>
              1. That my true and legal name as enrolled in Aadhaar UID <strong>•••• •••• 4921</strong> is <strong>RAMESH KUMAR</strong>.
            </p>
            <p>
              2. That in my Income Certificate No. <strong>UP-REV/2022/94821</strong>, my name was abbreviated as <strong>RAMESH KR.</strong> due to clerical shorthand by revenue officials.
            </p>
            <p>
              3. That <strong>RAMESH KUMAR</strong> and <strong>RAMESH KR.</strong> refer to one and the same identical individual.
            </p>
            <p className="text-secondary font-bold pt-2">
              ✓ Digital SHA-256 Hash Generated: 8c4f92a11b6...d29
            </p>
          </div>

          <div className="flex items-center gap-2 p-3 bg-secondary-container/20 border border-secondary-container rounded-xl text-on-surface">
            <input type="checkbox" id="consent-affidavit" defaultChecked className="rounded text-secondary focus:ring-secondary" />
            <label htmlFor="consent-affidavit" className="text-[11px]">
              I confirm that the facts stated above are true to my knowledge and authorize synthetic electronic filing under DPDP Act 2023.
            </label>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-4 bg-surface-container-low border-t border-surface-container-high flex items-center justify-between">
          <button
            onClick={closeAffidavit}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-on-surface-variant hover:bg-surface-container transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleGenerate}
            disabled={isSubmitting}
            className="px-5 py-2.5 rounded-xl bg-secondary hover:bg-secondary/90 text-white font-semibold text-xs flex items-center gap-2 shadow-md transition-all disabled:opacity-50"
          >
            {isSubmitting ? (
              <>
                <span className="material-symbols-outlined text-sm animate-spin">progress_activity</span>
                <span>Digitally Signing & Binding...</span>
              </>
            ) : (
              <>
                <span className="material-symbols-outlined text-sm">verified</span>
                <span>Sign & Attach Form Annexure-B</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
