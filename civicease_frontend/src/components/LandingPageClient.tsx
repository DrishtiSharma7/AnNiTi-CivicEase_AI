'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Navbar } from '@/components/Navbar';
import { usePersona } from '@/context/PersonaContext';

export function LandingPageClient() {
  const { language, activePersona, personaId, togglePersona, showToast } = usePersona();
  const [activeFaq, setActiveFaq] = useState<number | null>(0);

  const faqs = [
    {
      q: 'How does CivicEase AI guarantee zero document rejections?',
      a: 'Our deterministic synthetic OCR Diff Engine cross-matches names, addresses, and family rosters against Aadhaar and official revenue ledger standards before you apply. If an abbreviation or clerical error is detected (e.g., Ramesh Kr. vs Ramesh Kumar), it automatically generates an Annexure-B Alias Affidavit to prevent rejection.',
    },
    {
      q: 'Is my Aadhaar or personal data uploaded to a central AI cloud?',
      a: 'Strictly No. Under Section 8 of the DPDP Act 2023, CivicEase AI utilizes an On-Device Sovereign Vault with AES-256 GCM encryption. Your raw identity credentials are decrypted locally in your browser enclave, and only masked tokens (•••• •••• 8912) are transmitted for official eligibility verification.',
    },
    {
      q: 'Can the AI apply on my behalf without my knowledge?',
      a: 'Never. CivicEase AI enforces a mandatory Human-in-the-Loop (HITL) Sovereign Gateway. While the engine prepares verified dossiers, it is legally and technically prohibited from submitting without explicit citizen biometric or OTP authorization.',
    },
    {
      q: 'Which languages are supported for voice consultation?',
      a: 'We support 22 official Indian languages, including Hindi, Marathi, Bengali, Tamil, Telugu, Kannada, Gujarati, and English, with localized vernacular dialect processing.',
    },
  ];

  return (
    <div className="min-h-screen bg-surface flex flex-col font-sans">
      <Navbar />

      <main className="w-full pt-24 pb-16 flex-1">
        {/* Sovereign Trust Announcement Ribbon */}
        <section className="w-full bg-surface-container-high py-2 px-4 lg:px-8 border-b border-surface-container-highest">
          <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3 text-xs font-mono text-on-surface-variant">
            <div className="flex items-center gap-2">
              <span className="inline-flex w-2 h-2 rounded-full bg-secondary animate-pulse"></span>
              <span className="text-primary font-bold">GAZETTE FEED v24.8.2 ACTIVE</span>
              <span className="text-outline-variant">|</span>
              <span>450+ Verified Central & State Schemes Indexed in Real-Time</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1 text-on-secondary-container bg-secondary-container px-2 py-0.5 rounded-full text-[11px] font-bold">
                <span className="material-symbols-outlined text-[13px]">verified_user</span> DPDP ACT 2023 SOVEREIGN COMPLIANT
              </span>
              <span className="hidden md:inline text-on-surface-variant font-medium">Zero-Retention Vault Active</span>
            </div>
          </div>
        </section>

        {/* Hero Section */}
        <section className="relative w-full overflow-hidden bg-gradient-to-b from-surface via-surface-container-low to-surface py-12 sm:py-16 px-4 lg:px-8">
          <div className="absolute -top-32 right-1/4 w-96 h-96 bg-secondary-fixed/20 rounded-full blur-3xl pointer-events-none"></div>
          <div className="absolute top-1/2 -left-20 w-80 h-80 bg-primary-fixed/25 rounded-full blur-3xl pointer-events-none"></div>

          <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center relative z-10">
            {/* Left Narrative Column */}
            <div className="lg:col-span-6 flex flex-col gap-5 sm:gap-6">
              <div className="inline-flex items-center gap-2 self-start px-3.5 py-1.5 rounded-full bg-surface-container text-primary text-xs font-semibold shadow-sm border border-surface-container-high">
                <span className="material-symbols-outlined text-secondary text-sm">neurology</span>
                <span>Next-Gen Autonomous Welfare Navigation</span>
                <span className="w-1 h-1 rounded-full bg-secondary"></span>
                <span className="text-secondary font-bold">100% Explainable AI</span>
              </div>

              <h1 className="font-heading font-extrabold text-3xl sm:text-5xl lg:text-6xl text-primary tracking-tight leading-tight">
                Know Your Benefits. <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-secondary to-primary-container">
                  Fix Your Documents.
                </span>{' '}
                <br />
                Apply with Confidence.
              </h1>

              <p className="text-sm sm:text-base lg:text-lg text-on-surface-variant max-w-xl leading-relaxed">
                Your personal AI-powered assistant for discovering government schemes, checking precise eligibility, and preparing bulletproof dossiers in your own language.
              </p>

              {/* CTAs */}
              <div className="flex flex-wrap items-center gap-3 sm:gap-4 pt-2">
                <Link
                  href="/register"
                  className="h-12 px-6 sm:px-7 rounded-xl bg-primary-container text-on-primary text-sm font-bold flex items-center justify-center gap-2 shadow-md transition-all hover:bg-primary hover:shadow-lg"
                >
                  <span>Get Started</span>
                  <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
                </Link>
                <a
                  href="#how-it-works"
                  className="h-12 px-5 sm:px-6 rounded-xl bg-surface-container text-primary text-sm font-semibold flex items-center justify-center gap-2 transition-colors hover:bg-surface-container-high border border-surface-container-high"
                >
                  <span className="material-symbols-outlined text-lg text-secondary">explore</span>
                  <span>Explore How It Works</span>
                </a>
              </div>

              {/* Trust Badges */}
              <div className="flex flex-wrap items-center gap-4 sm:gap-6 pt-4 text-xs font-mono text-on-surface-variant border-t border-surface-container-high">
                <div className="flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-secondary text-base">lock</span>
                  <span>AES-256 On-Device</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-secondary text-base">privacy_tip</span>
                  <span>DPDP Section 8 Zero Retention</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-secondary text-base">translate</span>
                  <span>22 Indian Languages</span>
                </div>
              </div>
            </div>

            {/* Right Product Mockup / Interactive Preview */}
            <div className="lg:col-span-6">
              <div className="bg-surface-container-lowest rounded-2xl p-5 sm:p-6 shadow-[0_20px_50px_rgba(20,43,74,0.1)] border border-surface-container-high relative">
                {/* Window Header */}
                <div className="flex items-center justify-between pb-4 border-b border-surface-container-high mb-4">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-400"></div>
                    <div className="w-3 h-3 rounded-full bg-amber-400"></div>
                    <div className="w-3 h-3 rounded-full bg-emerald-400"></div>
                    <span className="ml-2 font-mono text-xs text-on-surface-variant">CivicEase Terminal v2.4</span>
                  </div>
                  <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-surface-container text-secondary font-bold">
                    Profile: {activePersona.name}
                  </span>
                </div>

                {/* Simulated Scenario */}
                <div className="space-y-4 text-xs">
                  <div className="p-3.5 rounded-xl bg-surface-container-low border border-surface-container-high flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-secondary-container flex items-center justify-center text-on-secondary-container font-bold text-sm">
                        ₹
                      </div>
                      <div>
                        <div className="font-heading font-bold text-primary text-sm">PM SVANidhi Micro-Credit</div>
                        <div className="text-on-surface-variant text-[11px]">Working Capital for Urban Micro-Vendors</div>
                      </div>
                    </div>
                    <span className="px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 font-bold text-[11px]">
                      98% Matched
                    </span>
                  </div>

                  {/* Synthetic OCR Diff Simulation */}
                  <div className="p-3.5 rounded-xl bg-surface-container-low border border-surface-container-high space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-primary flex items-center gap-1.5">
                        <span className="material-symbols-outlined text-sm text-secondary">difference</span>
                        Synthetic OCR Diff Analysis
                      </span>
                      <span className="text-[10px] font-mono text-outline">Deterministic Match</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 font-mono text-[11px]">
                      <div className="p-2 bg-surface-container-lowest rounded-lg border border-surface-container-high">
                        <span className="text-[10px] text-outline block">Aadhaar Record</span>
                        <span className="text-primary font-bold">Ramesh Kumar</span>
                      </div>
                      <div className="p-2 bg-surface-container-lowest rounded-lg border border-amber-300">
                        <span className="text-[10px] text-amber-600 block">UP Tehsil Ledger</span>
                        <span className="text-primary font-bold">Ramesh Kr.</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between text-[11px] pt-1 text-secondary font-medium">
                      <span>✓ Annexure-B Alias Affidavit Auto-Drafted</span>
                      <span className="font-bold cursor-pointer hover:underline" onClick={() => showToast('Opening preview...')}>
                        Preview PDF
                      </span>
                    </div>
                  </div>

                  {/* Interactive Persona Trigger Banner */}
                  <div className="pt-2 flex items-center justify-between text-xs text-on-surface-variant">
                    <span>Try live test persona:</span>
                    <button
                      onClick={togglePersona}
                      className="px-3 py-1 rounded-lg bg-primary-container text-on-primary text-xs font-semibold hover:bg-primary transition-colors flex items-center gap-1"
                    >
                      <span>Switch to {personaId === 'asha' ? 'Ramesh Kumar' : 'Asha Sharma'}</span>
                      <span className="material-symbols-outlined text-xs">sync</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Administrative Gap Feature Section */}
        <section className="py-16 px-4 lg:px-8 max-w-7xl mx-auto">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <span className="text-xs font-mono font-bold text-secondary tracking-widest uppercase bg-secondary-container/40 px-3 py-1 rounded-full">
              The Administrative Welfare Gap
            </span>
            <h2 className="font-heading font-extrabold text-2xl sm:text-4xl text-primary mt-3">
              ₹1.8 Lakh Crore in Welfare Goes Unclaimed Every Year
            </h2>
            <p className="text-xs sm:text-sm text-on-surface-variant mt-2 leading-relaxed">
              Citizens qualify for hundreds of state and central schemes, but drop out due to fragmented gazette notifications, cryptic criteria, and clerical document rejections. CivicEase AI closes the gap.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8">
            <div className="bg-surface-container-lowest p-6 rounded-2xl border border-surface-container-high shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 rounded-xl bg-primary-container text-secondary-fixed flex items-center justify-center mb-4">
                <span className="material-symbols-outlined text-2xl">search_insights</span>
              </div>
              <h3 className="font-heading font-bold text-base text-primary">Dynamic Discovery</h3>
              <p className="text-xs text-on-surface-variant mt-2 leading-relaxed">
                Indexes 450+ central ministries and state portals daily. Matches schemes to your profile with zero manual reading of Gazette PDFs.
              </p>
            </div>

            <div className="bg-surface-container-lowest p-6 rounded-2xl border border-surface-container-high shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 rounded-xl bg-secondary-container text-on-secondary-container flex items-center justify-center mb-4">
                <span className="material-symbols-outlined text-2xl">verified</span>
              </div>
              <h3 className="font-heading font-bold text-base text-primary">Deterministic Eligibility</h3>
              <p className="text-xs text-on-surface-variant mt-2 leading-relaxed">
                Rules engines with statutory citations. No AI hallucinations: each qualification cites the official Gazette number and Section.
              </p>
            </div>

            <div className="bg-surface-container-lowest p-6 rounded-2xl border border-surface-container-high shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 rounded-xl bg-tertiary-container text-tertiary-fixed flex items-center justify-center mb-4">
                <span className="material-symbols-outlined text-2xl">document_scanner</span>
              </div>
              <h3 className="font-heading font-bold text-base text-primary">Synthetic OCR Audit</h3>
              <p className="text-xs text-on-surface-variant mt-2 leading-relaxed">
                Audits certificates against Aadhaar. Discrepancies generate automated legal Annexure-B Affidavits before submitting.
              </p>
            </div>
          </div>
        </section>

        {/* 6-Step Autonomous Welfare Journey */}
        <section id="how-it-works" className="py-16 px-4 lg:px-8 bg-surface-container-low border-y border-surface-container-high">
          <div className="max-w-7xl mx-auto">
            <div className="text-center max-w-3xl mx-auto mb-12">
              <h2 className="font-heading font-extrabold text-2xl sm:text-4xl text-primary">
                The 6-Step Autonomous Welfare Journey
              </h2>
              <p className="text-xs sm:text-sm text-on-surface-variant mt-2">
                From initial profile setup to direct bank disbursement — guaranteed zero document rejection.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                {
                  step: '01',
                  title: 'Discover Schemes',
                  desc: 'Multi-lingual query matching against real-time central & state gazette indexes.',
                  icon: 'travel_explore',
                },
                {
                  step: '02',
                  title: 'Deterministic Qualify',
                  desc: 'Legal rules engine tests your age, domicile, income, and category with zero guessing.',
                  icon: 'rule',
                },
                {
                  step: '03',
                  title: 'Document Audit',
                  desc: 'Synthetic OCR scans certificates to flag spelling errors, expired validity, and missing seals.',
                  icon: 'fact_check',
                },
                {
                  step: '04',
                  title: 'Auto-Remediate',
                  desc: 'Instant generation of statutory affidavits (Annexure-B) and correction guidance.',
                  icon: 'draw',
                },
                {
                  step: '05',
                  title: 'Human-in-the-Loop Gateway',
                  desc: 'Mandatory citizen biometric or OTP sign-off before official submission.',
                  icon: 'fingerprint',
                },
                {
                  step: '06',
                  title: 'DBT Disbursement',
                  desc: 'Real-time tracking of Direct Benefit Transfers into your Aadhaar-seeded bank account.',
                  icon: 'account_balance_wallet',
                },
              ].map((item) => (
                <div
                  key={item.step}
                  className="bg-surface-container-lowest p-6 rounded-2xl border border-surface-container-high flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <span className="font-mono text-xs font-bold text-secondary bg-secondary-container/30 px-2 py-0.5 rounded">
                        STEP {item.step}
                      </span>
                      <span className="material-symbols-outlined text-xl text-primary">{item.icon}</span>
                    </div>
                    <h3 className="font-heading font-bold text-base text-primary mb-2">{item.title}</h3>
                    <p className="text-xs text-on-surface-variant leading-relaxed">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* FAQ Accordion Section */}
        <section className="py-16 px-4 lg:px-8 max-w-4xl mx-auto">
          <div className="text-center mb-10">
            <h2 className="font-heading font-extrabold text-2xl sm:text-3xl text-primary">
              Frequently Asked Questions
            </h2>
            <p className="text-xs text-on-surface-variant mt-1">
              Everything you need to know about CivicEase AI sovereign security and privacy
            </p>
          </div>

          <div className="space-y-3">
            {faqs.map((faq, idx) => (
              <div
                key={idx}
                className="bg-surface-container-lowest rounded-2xl border border-surface-container-high overflow-hidden transition-all"
              >
                <button
                  onClick={() => setActiveFaq(activeFaq === idx ? null : idx)}
                  className="w-full p-4 sm:p-5 text-left flex items-center justify-between gap-4 font-semibold text-xs sm:text-sm text-primary hover:bg-surface-container-low transition-colors"
                >
                  <span>{faq.q}</span>
                  <span className="material-symbols-outlined text-lg transition-transform duration-200">
                    {activeFaq === idx ? 'expand_less' : 'expand_more'}
                  </span>
                </button>
                {activeFaq === idx && (
                  <div className="p-4 sm:p-5 pt-0 text-xs text-on-surface-variant leading-relaxed border-t border-surface-container-high/60 bg-surface-container-low/40">
                    {faq.a}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="w-full bg-primary-container text-on-primary py-8 px-4 lg:px-8 border-t border-surface-container-high">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 text-xs">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-secondary-fixed">account_balance</span>
            <span className="font-heading font-bold text-sm">CivicEase AI</span>
            <span className="text-on-primary-container">| Sovereign GovTech Architecture</span>
          </div>
          <p className="text-on-primary-container text-[11px] text-center md:text-left">
            In compliance with Digital Personal Data Protection Act 2023. Zero centralized cloud storage.
          </p>
          <div className="flex items-center gap-4 text-secondary-fixed">
            <Link href="/schemes" className="hover:underline">
              Discover Schemes
            </Link>
            <Link href="/dashboard" className="hover:underline">
              Dashboard
            </Link>
            <Link href="/login" className="hover:underline">
              Citizen Login
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
