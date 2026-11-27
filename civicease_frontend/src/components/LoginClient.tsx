'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { usePersona } from '@/context/PersonaContext';

export function LoginClient() {
  const router = useRouter();
  const { activePersona, setPersona, language, toggleLanguage, showToast } = usePersona();

  const [activeTab, setActiveTab] = useState<'otp' | 'password' | 'passkey'>('otp');
  const [credential, setCredential] = useState('');
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [isVerifying, setIsVerifying] = useState(false);
  const [resendTimer, setResendTimer] = useState(28);

  const otpInputRefs = useRef<(HTMLInputElement | null)[]>([]);

  // Ticking countdown timer
  useEffect(() => {
    if (resendTimer > 0) {
      const interval = setInterval(() => {
        setResendTimer((prev) => prev - 1);
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [resendTimer]);

  const handleSelectPersona = (id: 'asha' | 'ramesh') => {
    setPersona(id);
    if (id === 'asha') {
      setCredential('98230 41092');
      setOtp(['4', '8', '2', '9', '1', '2']);
    } else {
      setCredential('87002 91823');
      setOtp(['5', '1', '9', '4', '2', '1']);
    }
    showToast(`Loaded ${id === 'asha' ? 'Asha Sharma' : 'Ramesh Kumar'} sandbox credentials`);
  };

  const handleOtpChange = (index: number, value: string) => {
    if (value.length > 1) {
      // Handle paste
      const digits = value.replace(/\D/g, '').slice(0, 6).split('');
      const newOtp = [...otp];
      digits.forEach((d, i) => {
        if (i < 6) newOtp[i] = d;
      });
      setOtp(newOtp);
      otpInputRefs.current[Math.min(digits.length, 5)]?.focus();
      return;
    }

    const newOtp = [...otp];
    newOtp[index] = value.replace(/\D/g, '');
    setOtp(newOtp);

    if (value && index < 5) {
      otpInputRefs.current[index + 1]?.focus();
    }
  };

  const handleOtpKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      otpInputRefs.current[index - 1]?.focus();
    }
  };

  const handleLogin = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setIsVerifying(true);
    showToast('Decrypting on-device Sovereign Enclave...');
    setTimeout(() => {
      router.push('/dashboard');
    }, 1000);
  };

  const handleResend = () => {
    if (resendTimer === 0) {
      setResendTimer(30);
      showToast(`New Sovereign OTP dispatched to +91 ${credential}`);
    }
  };

  const handleVoiceCall = () => {
    showToast('Automated Sovereign Voice Call initiated. Please standby for audio challenge.');
  };

  return (
    <div className="min-h-screen bg-surface font-sans flex flex-col justify-center items-center p-4">
      <main className="w-full max-w-xl">
        {/* Top Sovereign Badging & Bilingual Bar */}
        <div className="flex items-center justify-between px-2 mb-3">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center justify-center w-2 h-2 rounded-full bg-secondary animate-pulse"></span>
            <span className="font-mono text-[11px] sm:text-xs text-on-surface-variant font-medium tracking-wide">
              SOVEREIGN ATTESTATION NODE · UIDAI 2.4
            </span>
          </div>

          <div className="flex items-center bg-surface-container rounded-full p-0.5 shadow-sm">
            <button
              type="button"
              onClick={() => language !== 'en' && toggleLanguage()}
              className={`px-3 py-0.5 rounded-full text-xs font-semibold transition-all ${
                language === 'en'
                  ? 'bg-surface-container-lowest text-primary shadow-sm'
                  : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              English
            </button>
            <button
              type="button"
              onClick={() => language !== 'hi' && toggleLanguage()}
              className={`px-3 py-0.5 rounded-full text-xs font-semibold transition-all ${
                language === 'hi'
                  ? 'bg-surface-container-lowest text-primary shadow-sm'
                  : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              हिंदी
            </button>
          </div>
        </div>

        {/* Main Authentication Card */}
        <div className="w-full bg-surface-container-lowest rounded-2xl shadow-xl border border-surface-container-high p-6 sm:p-8 relative overflow-hidden">
          {/* Subtle Ambient Aura */}
          <div className="absolute -top-24 left-1/2 -translate-x-1/2 w-80 h-36 bg-gradient-to-b from-secondary-container/30 via-surface-variant/20 to-transparent blur-2xl pointer-events-none rounded-full"></div>

          {/* Header & Crest */}
          <div className="flex flex-col items-center text-center relative z-10 mb-6">
            <Link href="/" className="relative mb-3 group">
              <div className="w-14 h-14 rounded-2xl bg-surface-container flex items-center justify-center shadow-sm text-secondary group-hover:scale-105 transition-transform">
                <svg className="w-8 h-8 text-secondary" fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                  <path d="M24 4L7 11V22C7 32.5 14.2 42.3 24 45C33.8 42.3 41 32.5 41 22V11L24 4Z" fill="currentColor" fillOpacity="0.12"></path>
                  <path d="M24 4L7 11V22C7 32.5 14.2 42.3 24 45C33.8 42.3 41 32.5 41 22V11L24 4Z" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5"></path>
                  <circle cx="24" cy="23" r="7" stroke="currentColor" strokeWidth="2"></circle>
                  <circle cx="24" cy="23" fill="currentColor" r="2"></circle>
                  <path d="M24 16V30M17 23H31M19 18L29 28M29 18L19 28" stroke="currentColor" strokeLinecap="round" strokeWidth="1.2"></path>
                </svg>
              </div>
              <span className="absolute -bottom-1 -right-1 flex h-4 w-4">
                <span className="relative inline-flex rounded-full h-4 w-4 bg-secondary text-white items-center justify-center">
                  <span className="material-symbols-outlined text-[10px]">verified</span>
                </span>
              </span>
            </Link>
            <h1 className="font-heading font-bold text-2xl text-on-surface tracking-tight">CivicEase AI</h1>
            <p className="text-xs text-on-surface-variant mt-0.5 font-medium">Secure Sovereign Citizen Gateway</p>
          </div>

          {/* Tri-Modal Auth Tabs */}
          <div className="grid grid-cols-3 gap-1 p-1 bg-surface-container rounded-xl mb-6 text-center">
            <button
              type="button"
              onClick={() => setActiveTab('otp')}
              className={`py-2 px-1 sm:px-2 rounded-lg text-xs font-semibold transition-all flex items-center justify-center gap-1.5 ${
                activeTab === 'otp'
                  ? 'bg-surface-container-lowest text-primary shadow-sm font-bold'
                  : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              <span className="material-symbols-outlined text-sm text-secondary">phonelink_lock</span>
              <span className="truncate">Mobile / Aadhaar</span>
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('password')}
              className={`py-2 px-1 sm:px-2 rounded-lg text-xs font-semibold transition-all flex items-center justify-center gap-1.5 ${
                activeTab === 'password'
                  ? 'bg-surface-container-lowest text-primary shadow-sm font-bold'
                  : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              <span className="material-symbols-outlined text-sm">lock</span>
              <span className="truncate">Password</span>
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('passkey')}
              className={`py-2 px-1 sm:px-2 rounded-lg text-xs font-semibold transition-all flex items-center justify-center gap-1.5 ${
                activeTab === 'passkey'
                  ? 'bg-surface-container-lowest text-primary shadow-sm font-bold'
                  : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              <span className="material-symbols-outlined text-sm">fingerprint</span>
              <span className="truncate">Passkey</span>
            </button>
          </div>

          {/* Form Content */}
          {activeTab === 'otp' ? (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-xs font-bold text-on-surface" htmlFor="id-input">
                    Identity Credential
                  </label>
                  <span className="text-[11px] text-secondary flex items-center gap-0.5 font-medium">
                    <span className="material-symbols-outlined text-[13px]">format_image_left</span>
                    eKYC Ready
                  </span>
                </div>
                <div className="relative flex items-center bg-surface-container-low rounded-xl border border-surface-container-high focus-within:border-secondary transition-all">
                  <div className="flex items-center gap-1 px-3 py-2.5 bg-surface-container text-on-surface-variant rounded-l-xl font-mono text-xs font-bold select-none border-r border-surface-container-high">
                    <span className="text-base leading-none">🇮🇳</span>
                    <span>+91</span>
                  </div>
                  <input
                    id="id-input"
                    type="text"
                    value={credential}
                    onChange={(e) => setCredential(e.target.value)}
                    placeholder="Enter 10-digit mobile or 12-digit Aadhaar"
                    className="w-full bg-transparent px-3 py-2.5 text-xs text-on-surface placeholder:text-outline focus:outline-none font-mono"
                  />
                  <button
                    type="button"
                    onClick={() => showToast('Credential verified against UIDAI ledger.')}
                    className="mr-2 px-3 py-1 rounded-lg bg-secondary text-white text-[11px] font-bold shadow-sm hover:opacity-95 transition-opacity"
                  >
                    Verify ID
                  </button>
                </div>
              </div>

              {/* Interactive 6-Digit OTP Box */}
              <div className="bg-surface-container-low p-4 rounded-xl border border-surface-container-high space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-base text-secondary animate-spin" style={{ animationDuration: '4s' }}>
                      verified_user
                    </span>
                    <span className="text-xs font-bold text-on-surface">Sovereign OTP Challenge</span>
                  </div>
                  <span className="text-[11px] text-on-surface-variant font-mono">
                    {credential ? `Sent to +91 ${credential}` : 'Enter identity to dispatch OTP'}
                  </span>
                </div>

                {/* 6 Digit Inputs */}
                <div className="grid grid-cols-6 gap-2">
                  {otp.map((digit, idx) => (
                    <input
                      key={idx}
                      ref={(el) => {
                        otpInputRefs.current[idx] = el;
                      }}
                      type="text"
                      inputMode="numeric"
                      maxLength={1}
                      value={digit}
                      onChange={(e) => handleOtpChange(idx, e.target.value)}
                      onKeyDown={(e) => handleOtpKeyDown(idx, e)}
                      className="h-12 w-full text-center bg-surface-container-lowest rounded-xl font-heading text-lg font-bold shadow-sm border border-surface-container-high focus:border-secondary focus:ring-1 focus:ring-secondary text-primary outline-none transition-all"
                    />
                  ))}
                </div>

                <div className="flex items-center justify-between text-[11px] text-on-surface-variant pt-1">
                  <button
                    type="button"
                    onClick={handleVoiceCall}
                    className="text-secondary font-semibold hover:underline flex items-center gap-1"
                  >
                    <span className="material-symbols-outlined text-xs">call</span> Voice OTP Call
                  </button>
                  <button
                    type="button"
                    disabled={resendTimer > 0}
                    onClick={handleResend}
                    className={`font-mono ${
                      resendTimer > 0 ? 'text-outline cursor-not-allowed' : 'text-primary font-bold hover:underline'
                    }`}
                  >
                    {resendTimer > 0 ? `Resend in 00:${resendTimer.toString().padStart(2, '0')}` : 'Resend OTP'}
                  </button>
                </div>
              </div>

              {/* Decrypt & Login Submit */}
              <button
                type="submit"
                disabled={isVerifying}
                className="w-full py-3 px-4 rounded-xl bg-primary hover:bg-primary-container text-white text-xs font-bold flex items-center justify-center gap-2 shadow-md transition-all disabled:opacity-50"
              >
                {isVerifying ? (
                  <>
                    <span className="material-symbols-outlined text-sm animate-spin">progress_activity</span>
                    <span>Decrypting Sovereign Enclave...</span>
                  </>
                ) : (
                  <>
                    <span>Decrypt Sovereign Vault & Login</span>
                    <span className="material-symbols-outlined text-sm">arrow_forward</span>
                  </>
                )}
              </button>
            </form>
          ) : activeTab === 'password' ? (
            <div className="space-y-4 py-2">
              <div>
                <label className="text-xs font-bold text-on-surface block mb-1">Account Password</label>
                <input
                  type="password"
                  placeholder="Enter your sovereign password"
                  className="w-full h-11 px-3 bg-surface-container-low rounded-xl text-xs text-on-surface border border-surface-container-high focus:outline-none focus:border-secondary"
                />
              </div>
              <button
                onClick={() => handleLogin()}
                className="w-full py-3 rounded-xl bg-primary text-white text-xs font-bold shadow-md hover:bg-primary-container"
              >
                Authenticate with Password
              </button>
            </div>
          ) : (
            <div className="py-6 text-center space-y-4">
              <div className="w-16 h-16 rounded-full bg-secondary-container/30 text-secondary mx-auto flex items-center justify-center animate-pulse">
                <span className="material-symbols-outlined text-3xl">fingerprint</span>
              </div>
              <div>
                <h3 className="font-heading font-bold text-sm text-primary">Touch ID / FIDO2 Passkey</h3>
                <p className="text-xs text-on-surface-variant mt-1 max-w-xs mx-auto">
                  Scan your hardware enclave fingerprint or face biometrics to decrypt your sovereign vault.
                </p>
              </div>
              <button
                onClick={() => handleLogin()}
                className="px-6 py-2.5 rounded-xl bg-secondary text-white text-xs font-bold shadow-md hover:opacity-90"
              >
                Activate Hardware Biometrics
              </button>
            </div>
          )}

          {/* Evaluator Sandbox Personas Bar */}
          <div className="mt-6 p-4 rounded-xl bg-surface-container-low border border-dashed border-secondary/40 space-y-2.5">
            <div className="flex items-center gap-1.5 text-xs font-bold text-primary">
              <span className="material-symbols-outlined text-sm text-secondary">bolt</span>
              <span>Evaluator Sandbox Personas · 1-Click Auto Fill</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => handleSelectPersona('asha')}
                className={`p-2.5 rounded-lg text-left text-xs border transition-all ${
                  activePersona.id === 'asha'
                    ? 'bg-secondary-container/40 border-secondary text-primary font-bold shadow-sm'
                    : 'bg-surface-container-lowest border-surface-container-high text-on-surface-variant hover:border-secondary/40'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-primary">Asha Sharma (Clean)</span>
                  <span className="text-[10px] font-mono text-secondary">3 Matches</span>
                </div>
                <p className="text-[11px] text-on-surface-variant mt-0.5 truncate">
                  +91 98230 41092 · Valid Proofs
                </p>
              </button>

              <button
                type="button"
                onClick={() => handleSelectPersona('ramesh')}
                className={`p-2.5 rounded-lg text-left text-xs border transition-all ${
                  activePersona.id === 'ramesh'
                    ? 'bg-amber-50 border-amber-400 text-amber-900 font-bold shadow-sm'
                    : 'bg-surface-container-lowest border-surface-container-high text-on-surface-variant hover:border-amber-400/40'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-amber-900">Ramesh Kumar (Issues)</span>
                  <span className="text-[10px] font-mono text-error font-bold">2 Errors</span>
                </div>
                <p className="text-[11px] text-on-surface-variant mt-0.5 truncate">
                  +91 87002 91823 · Name Mismatch
                </p>
              </button>
            </div>
          </div>

          {/* Statutory DPDP Notice */}
          <div className="mt-5 p-3 rounded-xl bg-surface-container text-[11px] text-on-surface-variant flex items-start gap-2 leading-relaxed">
            <span className="material-symbols-outlined text-xs text-secondary shrink-0 mt-0.5">verified_user</span>
            <p>
              By authenticating, you authorize CivicEase AI to decrypt your on-device sovereign vault under the{' '}
              <strong>Digital Personal Data Protection (DPDP) Act 2023</strong>. Zero raw credentials reside on cloud databases.
            </p>
          </div>

          {/* Links */}
          <div className="mt-5 flex items-center justify-between text-xs text-on-surface-variant font-medium pt-2">
            <Link href="/register" className="hover:text-primary transition-colors flex items-center gap-1">
              <span className="material-symbols-outlined text-sm">person_add</span>
              <span>Register New Profile</span>
            </Link>
            <Link href="/" className="hover:text-primary transition-colors flex items-center gap-1">
              <span className="material-symbols-outlined text-sm">support_agent</span>
              <span>Assisted Kendra (CSC) Help</span>
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
