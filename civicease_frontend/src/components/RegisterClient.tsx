'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { usePersona } from '@/context/PersonaContext';

export function RegisterClient() {
  const router = useRouter();
  const { language, showToast } = usePersona();

  const [step, setStep] = useState(1);
  const [fullName, setFullName] = useState('');
  const [mobile, setMobile] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('English');
  const [domicile, setDomicile] = useState('Maharashtra - MahaDBT');
  const [category, setCategory] = useState('EWS');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const languages = [
    { name: 'English (Default)', native: 'English' },
    { name: 'मराठी', native: 'Marathi' },
    { name: 'हिंदी', native: 'Hindi' },
    { name: 'தமிழ்', native: 'Tamil' },
    { name: 'বাংলা', native: 'Bengali' },
    { name: 'తెలుగు', native: 'Telugu' },
  ];

  const categories = ['General', 'EWS', 'OBC', 'SC', 'ST', 'Minority'];

  const handleNextStep = (next: number) => {
    setStep(next);
    showToast(`Step ${next} of 3: ${next === 2 ? 'Domicile & Language' : 'Privacy Vault'}`);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    showToast('Generating AES-256 GCM client-side vault keys...');
    setTimeout(() => {
      router.push('/dashboard');
    }, 1200);
  };

  return (
    <div className="min-h-screen bg-surface font-sans flex flex-col justify-center items-center p-4">
      <main className="w-full max-w-2xl">
        {/* Header Badge */}
        <div className="text-center mb-6">
          <Link href="/" className="inline-flex items-center gap-2 mb-3 group">
            <div className="w-10 h-10 rounded-xl bg-primary-container text-secondary-fixed flex items-center justify-center shadow-md group-hover:scale-105 transition-transform">
              <span className="material-symbols-outlined text-2xl">account_balance</span>
            </div>
            <span className="font-heading font-bold text-xl text-primary">CivicEase AI</span>
          </Link>
          <h1 className="font-heading font-extrabold text-2xl sm:text-3xl text-primary">
            Create Your Sovereign Citizen Profile
          </h1>
          <p className="text-xs text-on-surface-variant mt-1">
            Zero cloud retention · Client-side AES-256 Vault Generation · DPDP Act 2023 Compliant
          </p>
        </div>

        {/* 3-Step Stepper */}
        <div className="grid grid-cols-3 gap-2 mb-6">
          {[
            { num: 1, label: 'Credentials' },
            { num: 2, label: 'Domicile & Lang' },
            { num: 3, label: 'Privacy Vault' },
          ].map((item) => (
            <div
              key={item.num}
              onClick={() => setStep(item.num)}
              className={`p-2.5 sm:p-3 rounded-xl border cursor-pointer transition-all ${
                step === item.num
                  ? 'bg-primary-container text-white border-primary-container shadow-sm'
                  : step > item.num
                  ? 'bg-secondary-container/30 border-secondary text-primary'
                  : 'bg-surface-container-lowest border-surface-container-high text-on-surface-variant'
              }`}
            >
              <div className="flex items-center gap-1.5 sm:gap-2">
                <span
                  className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                    step === item.num ? 'bg-secondary text-white' : 'bg-surface-container text-on-surface'
                  }`}
                >
                  {item.num}
                </span>
                <span className="text-[11px] sm:text-xs font-semibold truncate">{item.label}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Card Form */}
        <form
          onSubmit={handleSubmit}
          className="bg-surface-container-lowest rounded-2xl shadow-xl border border-surface-container-high p-5 sm:p-8 space-y-6"
        >
          {step === 1 && (
            <div className="space-y-4">
              <h2 className="font-heading font-bold text-sm sm:text-base text-primary pb-2 border-b border-surface-container-high">
                Section 1 · Citizen Identity & Attestation
              </h2>

              <div>
                <label className="text-xs font-bold text-on-surface block mb-1">Full Legal Name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="As printed on your Aadhaar card"
                  className="w-full h-11 px-3 bg-surface-container-low rounded-xl text-xs text-on-surface border border-surface-container-high focus:border-secondary focus:outline-none"
                  required
                />
                <span className="text-[10px] text-on-surface-variant mt-1 block">
                  Must match spelling on your Aadhaar UID to avoid automated clerical rejection.
                </span>
              </div>

              <div>
                <label className="text-xs font-bold text-on-surface block mb-1">Aadhaar-Linked Mobile Number</label>
                <div className="relative flex items-center bg-surface-container-low rounded-xl border border-surface-container-high focus-within:border-secondary">
                  <span className="px-3 py-2.5 bg-surface-container text-on-surface-variant text-xs font-bold border-r border-surface-container-high">
                    🇮🇳 +91
                  </span>
                  <input
                    type="tel"
                    value={mobile}
                    onChange={(e) => setMobile(e.target.value)}
                    placeholder="Enter 10-digit mobile"
                    className="w-full bg-transparent px-3 py-2.5 text-xs text-on-surface focus:outline-none font-mono"
                    required
                  />
                  <span className="mr-3 text-secondary text-[11px] font-bold flex items-center gap-1">
                    <span className="material-symbols-outlined text-xs">verified</span> Ready
                  </span>
                </div>
              </div>

              <div>
                <label className="text-xs font-bold text-on-surface block mb-1">Email Address (Optional)</label>
                <input
                  type="email"
                  placeholder="For gazette release updates"
                  className="w-full h-11 px-3 bg-surface-container-low rounded-xl text-xs text-on-surface border border-surface-container-high focus:border-secondary focus:outline-none"
                />
              </div>

              <div className="pt-2">
                <button
                  type="button"
                  onClick={() => handleNextStep(2)}
                  className="w-full py-3 rounded-xl bg-primary text-white text-xs font-bold flex items-center justify-center gap-2 shadow-md hover:bg-primary-container transition-all"
                >
                  <span>Continue to Domicile & Language</span>
                  <span className="material-symbols-outlined text-sm">arrow_forward</span>
                </button>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <h2 className="font-heading font-bold text-sm sm:text-base text-primary pb-2 border-b border-surface-container-high">
                Section 2 · Regional Domicile & Preferred Tongue
              </h2>

              <div>
                <label className="text-xs font-bold text-on-surface block mb-2">Preferred Consultation Language</label>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  {languages.map((lang) => (
                    <button
                      key={lang.name}
                      type="button"
                      onClick={() => setSelectedLanguage(lang.name)}
                      className={`p-2.5 rounded-xl text-xs text-left border transition-all ${
                        selectedLanguage === lang.name
                          ? 'bg-secondary-container/40 border-secondary text-primary font-bold shadow-sm'
                          : 'bg-surface-container-low border-surface-container-high text-on-surface-variant hover:border-secondary/30'
                      }`}
                    >
                      <span className="block font-bold truncate">{lang.name}</span>
                      <span className="text-[10px] text-outline">{lang.native}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-xs font-bold text-on-surface block mb-1">State Domicile Registry</label>
                <select
                  value={domicile}
                  onChange={(e) => setDomicile(e.target.value)}
                  className="w-full h-11 px-3 bg-surface-container-low rounded-xl text-xs text-on-surface border border-surface-container-high focus:border-secondary focus:outline-none"
                >
                  <option value="Maharashtra - MahaDBT">Maharashtra (MahaDBT Integrated)</option>
                  <option value="Karnataka - Kutumba">Karnataka (Kutumba Family ID)</option>
                  <option value="Uttar Pradesh - Tehsil Sadar">Uttar Pradesh (e-District / Sadar)</option>
                  <option value="Madhya Pradesh - Samagra">Madhya Pradesh (Samagra Portal)</option>
                  <option value="Delhi - e-District">NCT of Delhi (e-District)</option>
                  <option value="Tamil Nadu - TNPDS">Tamil Nadu (TNeGA Portal)</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-bold text-on-surface block mb-2">
                  Social Category / Reservation Status
                </label>
                <div className="flex flex-wrap gap-2">
                  {categories.map((cat) => (
                    <button
                      key={cat}
                      type="button"
                      onClick={() => setCategory(cat)}
                      className={`px-3 py-1.5 rounded-full text-xs font-semibold border transition-all ${
                        category === cat
                          ? 'bg-primary text-white border-primary shadow-sm font-bold'
                          : 'bg-surface-container-low border-surface-container-high text-on-surface-variant hover:bg-surface-container'
                      }`}
                    >
                      {cat}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="w-1/3 py-3 rounded-xl bg-surface-container text-on-surface text-xs font-bold hover:bg-surface-container-high transition-colors"
                >
                  Back
                </button>
                <button
                  type="button"
                  onClick={() => handleNextStep(3)}
                  className="w-2/3 py-3 rounded-xl bg-primary text-white text-xs font-bold flex items-center justify-center gap-2 shadow-md hover:bg-primary-container transition-all"
                >
                  <span>Continue to Privacy Vault</span>
                  <span className="material-symbols-outlined text-sm">arrow_forward</span>
                </button>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-4">
              <h2 className="font-heading font-bold text-sm sm:text-base text-primary pb-2 border-b border-surface-container-high">
                Section 3 · Statutory DPDP Consent & Vault Keys
              </h2>

              <div className="p-4 rounded-xl bg-secondary-container/20 border border-secondary-container space-y-3 text-xs leading-relaxed">
                <div className="flex items-start gap-2.5">
                  <input
                    type="checkbox"
                    id="consent-ocr"
                    defaultChecked
                    className="mt-0.5 rounded text-secondary focus:ring-secondary"
                    required
                  />
                  <label htmlFor="consent-ocr" className="text-on-surface">
                    <strong>Synthetic OCR & Cross-Referencing:</strong> I consent to client-side synthetic OCR parsing of my uploaded documents solely for determining scheme eligibility under Section 6 of DPDP Act 2023.
                  </label>
                </div>

                <div className="flex items-start gap-2.5">
                  <input
                    type="checkbox"
                    id="consent-hitl"
                    defaultChecked
                    className="mt-0.5 rounded text-secondary focus:ring-secondary"
                    required
                  />
                  <label htmlFor="consent-hitl" className="text-on-surface">
                    <strong>Autonomous Submission Prohibition:</strong> I understand that CivicEase AI prepares verified dossiers but is statutorily prohibited from submitting any application without my explicit biometric or OTP confirmation.
                  </label>
                </div>
              </div>

              {/* Encryption Key Simulation */}
              <div className="p-3.5 rounded-xl bg-surface-container-low border border-surface-container-high font-mono text-[11px] text-on-surface-variant flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-secondary text-base">key</span>
                  <span>AES-256 GCM Key: 9f8a...34e1 (On-Device Local)</span>
                </div>
                <span className="text-secondary font-bold">READY</span>
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setStep(2)}
                  className="w-1/3 py-3 rounded-xl bg-surface-container text-on-surface text-xs font-bold hover:bg-surface-container-high transition-colors"
                >
                  Back
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-2/3 py-3 rounded-xl bg-secondary hover:bg-secondary/90 text-white text-xs font-bold flex items-center justify-center gap-2 shadow-lg transition-all disabled:opacity-50"
                >
                  {isSubmitting ? (
                    <>
                      <span className="material-symbols-outlined text-sm animate-spin">progress_activity</span>
                      <span>Creating Encrypted Enclave...</span>
                    </>
                  ) : (
                    <>
                      <span className="material-symbols-outlined text-sm">lock</span>
                      <span>Create Account & Generate Vault</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {/* Bottom link */}
          <div className="text-center pt-2 text-xs text-on-surface-variant">
            Already registered?{' '}
            <Link href="/login" className="text-secondary font-bold hover:underline">
              Sign In with OTP or Biometrics
            </Link>
          </div>
        </form>
      </main>
    </div>
  );
}
