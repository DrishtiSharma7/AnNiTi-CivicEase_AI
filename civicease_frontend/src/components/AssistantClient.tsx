'use client';

import React, { useState, useEffect, useRef, Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { Sidebar } from '@/components/Sidebar';
import { AppHeader } from '@/components/AppHeader';
import { usePersona } from '@/context/PersonaContext';

interface Message {
  id: string;
  sender: 'ai' | 'user';
  text: string;
  time: string;
  structuredCard?: boolean;
}

function AssistantContent() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get('q');

  const { activePersona, personaId, language, showToast } = usePersona();

  const [ttsActive, setTtsActive] = useState(false);
  const [inputText, setInputText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [mobileTab, setMobileTab] = useState<'chat' | 'profile' | 'history'>('chat');
  const chatBottomRef = useRef<HTMLDivElement>(null);

  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'ai',
      text: `Namaste ${activePersona.name}! I am your CivicEase AI Copilot. I have synchronized your sovereign vault data (${activePersona.domicile}, ${activePersona.category}). How can I assist with welfare schemes, document audits, or eligibility cross-checks today?`,
      time: '10:42 AM',
    },
    {
      id: '2',
      sender: 'user',
      text: 'Can I apply for the PM SVANidhi scheme with my current documents? What documents are missing?',
      time: '10:43 AM',
    },
    {
      id: '3',
      sender: 'ai',
      text: 'I have audited your sovereign credentials against the latest Ministry of Housing & Urban Affairs (MoHUA) Gazette notification. Here is your deterministic readiness breakdown:',
      time: '10:43 AM',
      structuredCard: true,
    },
  ]);

  // Handle initial URL query if passed
  useEffect(() => {
    if (initialQuery && initialQuery.trim()) {
      const userMsg: Message = {
        id: Date.now().toString(),
        sender: 'user',
        text: initialQuery,
        time: 'Just now',
      };
      setMessages((prev) => [...prev, userMsg]);

      setTimeout(() => {
        const aiMsg: Message = {
          id: (Date.now() + 1).toString(),
          sender: 'ai',
          text: `Regarding "${initialQuery}": Based on your ${activePersona.domicile} domicile and annual income of ${activePersona.income}, I cross-checked the statutory eligibility criteria. Your profile qualifies for direct priority processing under Section 4 of the applicable Gazette notification.`,
          time: 'Just now',
        };
        setMessages((prev) => [...prev, aiMsg]);
        if (ttsActive && typeof window !== 'undefined' && 'speechSynthesis' in window) {
          const utterance = new SpeechSynthesisUtterance(aiMsg.text);
          window.speechSynthesis.speak(utterance);
        }
      }, 700);
    }
  }, [initialQuery]);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    const userText = inputText;
    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: userText,
      time: 'Just now',
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');

    setTimeout(() => {
      let reply = `Under ${activePersona.domicile} revenue rules, your household income of ${activePersona.income} comfortably qualifies for priority welfare processing. I have verified your UID (${activePersona.aadhaar}).`;
      if (userText.toLowerCase().includes('mismatch') || userText.toLowerCase().includes('name')) {
        reply =
          'To resolve your clerical name mismatch between your Aadhaar UID and Income Certificate, our synthetic engine can generate a legally binding Form Annexure-B Alias Affidavit. You can attach it in the Document Audit engine in 1 click.';
      } else if (userText.toLowerCase().includes('pmay') || userText.toLowerCase().includes('house')) {
        reply =
          'For PMAY-Urban 2.0, you are eligible for up to ₹1.80 Lakh interest subsidy! Please note your income certificate requires annual renewal before final submission.';
      }

      const aiReply: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        text: reply,
        time: 'Just now',
      };
      setMessages((prev) => [...prev, aiReply]);

      if (ttsActive && typeof window !== 'undefined' && 'speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(reply);
        window.speechSynthesis.speak(utterance);
      }
    }, 800);
  };

  const handlePromptClick = (prompt: string) => {
    setInputText(prompt);
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    if (!isRecording) {
      showToast('Listening in regional dialect (Hindi / English / Marathi)...');
      setTimeout(() => {
        setIsRecording(false);
        setInputText('Is my income certificate valid for the PMAY-U 2.0 housing grant?');
        showToast('Speech transcribed successfully!');
      }, 2500);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      showToast(`Uploading ${file.name} to local browser enclave...`);
      setTimeout(() => {
        const uploadMsg: Message = {
          id: Date.now().toString(),
          sender: 'user',
          text: `[Uploaded Document: ${file.name} (Size: ${(file.size / 1024).toFixed(1)} KB)]`,
          time: 'Just now',
        };
        const aiMsg: Message = {
          id: (Date.now() + 1).toString(),
          sender: 'ai',
          text: `Synthetic OCR analysis of "${file.name}" complete. Resolution: 300 DPI. OCR Confidence: 98.4%. Watermark authenticated. Document linked to your sovereign vault.`,
          time: 'Just now',
        };
        setMessages((prev) => [...prev, uploadMsg, aiMsg]);
        showToast('Document synthetic audit complete!');
      }, 1200);
    }
  };

  return (
    <div className="min-h-screen bg-background text-on-surface flex">
      <Sidebar />

      <div className="lg:pl-64 pl-0 flex-1 flex flex-col min-h-screen w-full">
        <AppHeader />

        <main className="pt-20 px-4 sm:px-6 lg:px-8 pb-12 flex-1 max-w-7xl w-full mx-auto space-y-4">
          {/* Top Consultation Control Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-surface-container-high">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-secondary text-2xl">neurology</span>
              <div>
                <h1 className="font-heading font-extrabold text-lg sm:text-xl text-primary">
                  Civic AI Scheme Assistant & Copilot
                </h1>
                <p className="text-xs text-on-surface-variant font-mono">
                  Civic Reasoning Engine 3.2 · 12 Central Datasets Synced
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => {
                  setTtsActive(!ttsActive);
                  showToast(!ttsActive ? 'Text-to-Speech active' : 'Text-to-Speech muted');
                }}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors ${
                  ttsActive
                    ? 'bg-secondary-container text-on-secondary-container font-bold'
                    : 'bg-surface-container text-on-surface-variant'
                }`}
              >
                <span className="material-symbols-outlined text-base">
                  {ttsActive ? 'volume_up' : 'volume_off'}
                </span>
                <span>{ttsActive ? 'TTS Active' : 'TTS Muted'}</span>
              </button>

              <button
                type="button"
                onClick={() => {
                  setMessages([
                    {
                      id: '1',
                      sender: 'ai',
                      text: `Session reset. How can I assist you with government schemes today, ${activePersona.name}?`,
                      time: 'Just now',
                    },
                  ]);
                  showToast('Consultation session cleared');
                }}
                className="p-1.5 rounded-xl hover:bg-surface-container text-outline hover:text-on-surface transition-colors"
                title="Clear Consultation"
              >
                <span className="material-symbols-outlined text-base">restart_alt</span>
              </button>
            </div>
          </div>

          {/* Mobile View Switcher */}
          <div className="flex xl:hidden bg-surface-container p-1 rounded-xl text-xs font-semibold">
            <button
              onClick={() => setMobileTab('chat')}
              className={`flex-1 py-1.5 rounded-lg text-center transition-all ${
                mobileTab === 'chat' ? 'bg-white text-primary font-bold shadow-sm' : 'text-on-surface-variant'
              }`}
            >
              Chat Consultation
            </button>
            <button
              onClick={() => setMobileTab('profile')}
              className={`flex-1 py-1.5 rounded-lg text-center transition-all ${
                mobileTab === 'profile' ? 'bg-white text-primary font-bold shadow-sm' : 'text-on-surface-variant'
              }`}
            >
              Citizen Profile
            </button>
            <button
              onClick={() => setMobileTab('history')}
              className={`flex-1 py-1.5 rounded-lg text-center transition-all ${
                mobileTab === 'history' ? 'bg-white text-primary font-bold shadow-sm' : 'text-on-surface-variant'
              }`}
            >
              Past Sessions
            </button>
          </div>

          {/* 3-Column Consultation Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            {/* Left 3 Cols: Past Consultations & Safety */}
            <div
              className={`lg:col-span-3 space-y-4 ${
                mobileTab === 'history' ? 'block' : 'hidden xl:block'
              }`}
            >
              <div className="p-4 rounded-2xl bg-surface-container-lowest border border-surface-container-high shadow-sm space-y-3">
                <button
                  type="button"
                  onClick={() => {
                    setMessages([
                      {
                        id: Date.now().toString(),
                        sender: 'ai',
                        text: `New consultation opened for ${activePersona.name}. How can I help?`,
                        time: 'Just now',
                      },
                    ]);
                    showToast('Started new consultation session');
                  }}
                  className="w-full py-2.5 rounded-xl bg-primary text-white text-xs font-bold flex items-center justify-center gap-1.5 shadow-sm hover:bg-primary-container"
                >
                  <span className="material-symbols-outlined text-sm">add</span>
                  <span>New Consultation</span>
                </button>

                <div className="pt-2">
                  <span className="text-[10px] font-bold text-outline uppercase tracking-wider block mb-2">
                    Recent Sessions
                  </span>
                  <div className="space-y-1.5 text-xs">
                    <div className="p-2.5 rounded-xl bg-surface-container text-primary font-bold cursor-pointer flex items-center justify-between">
                      <span className="truncate">PM SVANidhi Eligibility</span>
                      <span className="text-[10px] font-mono text-secondary">Active</span>
                    </div>
                    <div
                      onClick={() =>
                        setInputText('How do I fix the name mismatch on my Income Certificate?')
                      }
                      className="p-2.5 rounded-xl hover:bg-surface-container-low text-on-surface-variant cursor-pointer flex items-center justify-between transition-colors"
                    >
                      <span className="truncate">Income Cert Mismatch</span>
                      <span className="text-[10px] font-mono text-outline">1d ago</span>
                    </div>
                    <div
                      onClick={() => setInputText('What is the eligibility for PMAY 2.0?')}
                      className="p-2.5 rounded-xl hover:bg-surface-container-low text-on-surface-variant cursor-pointer flex items-center justify-between transition-colors"
                    >
                      <span className="truncate">Post-Matric Checklist</span>
                      <span className="text-[10px] font-mono text-outline">3d ago</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* MeitY Advisory Safeguard Card */}
              <div className="p-4 rounded-2xl bg-surface-container-low border border-surface-container-high text-xs text-on-surface-variant space-y-2">
                <div className="flex items-center gap-1.5 text-primary font-bold">
                  <span className="material-symbols-outlined text-secondary text-base">security</span>
                  <span>Statutory Safeguard</span>
                </div>
                <p className="text-[11px] leading-relaxed">
                  CivicEase AI complies with MeitY Advisory on Generative AI. All outputs cite verifiable official gazettes.
                </p>
              </div>
            </div>

            {/* Center 6 Cols: Chat Thread */}
            <div
              className={`lg:col-span-8 xl:col-span-6 space-y-4 ${
                mobileTab === 'chat' ? 'block' : 'hidden xl:block'
              }`}
            >
              <div className="bg-surface-container-lowest rounded-2xl border border-surface-container-high shadow-sm p-4 sm:p-5 min-h-[460px] max-h-[580px] overflow-y-auto space-y-4">
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
                  >
                    <div className="flex items-center gap-1.5 mb-1 px-1">
                      <span className="text-[10px] font-mono font-bold text-outline">
                        {msg.sender === 'ai' ? 'CivicEase AI Copilot' : activePersona.name}
                      </span>
                      <span className="text-[10px] font-mono text-outline">{msg.time}</span>
                    </div>

                    <div
                      className={`p-4 rounded-2xl text-xs leading-relaxed max-w-[95%] sm:max-w-[85%] ${
                        msg.sender === 'user'
                          ? 'bg-primary text-white rounded-tr-none shadow-sm'
                          : 'bg-surface-container-low border border-surface-container-high text-on-surface rounded-tl-none'
                      }`}
                    >
                      <p>{msg.text}</p>

                      {/* Structured Response Card from Stitch */}
                      {msg.structuredCard && (
                        <div className="mt-3 pt-3 border-t border-surface-container-high space-y-3">
                          <div className="p-3 rounded-xl bg-surface-container-lowest border border-surface-container-high">
                            <div className="flex items-center justify-between">
                              <span className="font-bold text-primary">PM SVANidhi Loan Scheme</span>
                              <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold">
                                98% Eligible
                              </span>
                            </div>
                            <div className="grid grid-cols-3 gap-2 mt-2 pt-2 border-t border-surface-container-high text-center">
                              <div className="p-1.5 rounded bg-surface-container-low">
                                <span className="text-[10px] text-outline block">1st Tranche</span>
                                <span className="font-bold text-primary">₹10,000</span>
                              </div>
                              <div className="p-1.5 rounded bg-surface-container-low">
                                <span className="text-[10px] text-outline block">2nd Tranche</span>
                                <span className="font-bold text-primary">₹20,000</span>
                              </div>
                              <div className="p-1.5 rounded bg-surface-container-low">
                                <span className="text-[10px] text-outline block">3rd Tranche</span>
                                <span className="font-bold text-primary">₹50,000</span>
                              </div>
                            </div>
                          </div>

                          <div className="space-y-1.5">
                            <span className="font-bold text-primary text-[11px] block">
                              Document Readiness: 2 of 3 Ready (66%)
                            </span>
                            <div className="space-y-1 text-[11px]">
                              <div className="flex items-center justify-between p-1.5 rounded bg-surface-container-lowest">
                                <span className="flex items-center gap-1.5">
                                  <span className="material-symbols-outlined text-secondary text-sm">verified</span>
                                  <span>Aadhaar-Linked Mobile</span>
                                </span>
                                <span className="text-secondary font-bold">Verified</span>
                              </div>
                              <div className="flex items-center justify-between p-1.5 rounded bg-surface-container-lowest">
                                <span className="flex items-center gap-1.5">
                                  <span className="material-symbols-outlined text-secondary text-sm">verified</span>
                                  <span>Vending Certificate / LOR</span>
                                </span>
                                <span className="text-secondary font-bold">BMC Reg #88219</span>
                              </div>
                              <div className="flex items-center justify-between p-1.5 rounded bg-amber-50 border border-amber-200">
                                <span className="flex items-center gap-1.5 text-amber-900">
                                  <span className="material-symbols-outlined text-amber-600 text-sm">warning</span>
                                  <span>Bank Passbook (Missing pages 3-4)</span>
                                </span>
                                <Link
                                  href="/documents/audit"
                                  className="text-amber-800 font-bold underline hover:text-amber-950"
                                >
                                  Fix Scan
                                </Link>
                              </div>
                            </div>
                          </div>

                          <div className="flex flex-wrap gap-2 pt-1">
                            <Link
                              href="/documents/audit"
                              className="px-3 py-1.5 rounded-lg bg-secondary text-white text-[11px] font-bold shadow-sm"
                            >
                              Audit Bank Passbook Now
                            </Link>
                            <a
                              href="https://pmsvanidhi.mohua.gov.in"
                              target="_blank"
                              rel="noreferrer"
                              className="px-3 py-1.5 rounded-lg bg-surface-container text-primary text-[11px] font-bold hover:bg-surface-container-high"
                            >
                              Official Portal
                            </a>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                <div ref={chatBottomRef} />
              </div>

              {/* Suggested Follow-up Chips */}
              <div className="flex items-center gap-2 overflow-x-auto pb-1 text-[11px]">
                {[
                  'How do I fix the name mismatch on my Income Certificate?',
                  'Can I apply for the PMAY-U 2.0 housing subsidy?',
                  'What is the interest rebate on PM SVANidhi 3rd tranche?',
                ].map((chip, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handlePromptClick(chip)}
                    className="px-3 py-1 rounded-full bg-surface-container-lowest border border-surface-container-high text-on-surface-variant hover:text-primary hover:border-secondary transition-colors whitespace-nowrap shadow-sm"
                  >
                    {chip}
                  </button>
                ))}
              </div>

              {/* Chat Input Bar */}
              <form onSubmit={handleSend} className="relative flex items-center gap-2">
                <label
                  className="p-2.5 rounded-xl bg-surface-container-lowest border border-surface-container-high text-outline hover:text-primary transition-colors shadow-sm cursor-pointer"
                  title="Upload Document for Synthetic OCR"
                >
                  <input type="file" onChange={handleFileUpload} className="hidden" />
                  <span className="material-symbols-outlined text-lg">attach_file</span>
                </label>

                <div className="relative flex-1 flex items-center">
                  <input
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Ask in Hindi, English, Marathi, Tamil... or upload document"
                    className="w-full h-11 pl-3 pr-12 bg-surface-container-lowest rounded-xl text-xs text-on-surface border border-surface-container-high focus:outline-none focus:border-secondary shadow-sm"
                  />
                  <button
                    type="button"
                    onClick={toggleRecording}
                    className={`absolute right-2 p-1.5 rounded-lg transition-colors ${
                      isRecording ? 'text-red-600 bg-red-100 animate-pulse' : 'text-outline hover:text-secondary'
                    }`}
                    title="Speak in your mother tongue"
                  >
                    <span className="material-symbols-outlined text-lg">mic</span>
                  </button>
                </div>

                <button
                  type="submit"
                  className="h-11 px-4 sm:px-5 rounded-xl bg-primary hover:bg-primary-container text-white text-xs font-bold flex items-center justify-center gap-1 shadow-sm transition-all"
                >
                  <span className="hidden sm:inline">Send</span>
                  <span className="material-symbols-outlined text-sm">send</span>
                </button>
              </form>
            </div>

            {/* Right 3 Cols: Citizen Context Summary */}
            <div
              className={`lg:col-span-4 xl:col-span-3 space-y-4 ${
                mobileTab === 'profile' ? 'block' : 'hidden xl:block'
              }`}
            >
              <div className="p-5 rounded-2xl bg-surface-container-lowest border border-surface-container-high shadow-sm space-y-4">
                <div className="flex items-center justify-between pb-2 border-b border-surface-container-high">
                  <span className="text-xs font-bold text-primary">Citizen Context Summary</span>
                  <span className="text-[10px] font-mono text-secondary font-bold">LIVE SYNC</span>
                </div>

                <div className="space-y-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-outline">Citizen</span>
                    <span className="font-bold text-primary">{activePersona.name}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-outline">Aadhaar UID</span>
                    <span className="font-mono text-on-surface">{activePersona.aadhaar}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-outline">Domicile</span>
                    <span className="text-on-surface">{activePersona.domicile}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-outline">Income Category</span>
                    <span className="font-bold text-primary">{activePersona.category}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-outline">Annual Income</span>
                    <span className="font-bold text-secondary">{activePersona.income}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-outline">Occupation</span>
                    <span className="text-on-surface">{activePersona.occupation}</span>
                  </div>
                </div>

                <div className="pt-3 border-t border-surface-container-high space-y-2">
                  <span className="text-[10px] font-bold text-outline uppercase block">High-Probability Schemes</span>
                  <div className="space-y-1.5 text-[11px]">
                    <div className="p-2 rounded-lg bg-surface-container-low flex items-center justify-between">
                      <span className="font-semibold text-primary">PM SVANidhi</span>
                      <span className="text-secondary font-bold">98% Match</span>
                    </div>
                    <div className="p-2 rounded-lg bg-surface-container-low flex items-center justify-between">
                      <span className="font-semibold text-primary">PMAY-Urban 2.0</span>
                      <span className="text-amber-600 font-bold">94% Match</span>
                    </div>
                    <div className="p-2 rounded-lg bg-surface-container-low flex items-center justify-between">
                      <span className="font-semibold text-primary">Ayushman Bharat</span>
                      <span className="text-secondary font-bold">100% Match</span>
                    </div>
                  </div>
                </div>

                {/* Upload Widget */}
                <label className="p-4 rounded-xl border border-dashed border-secondary/40 bg-secondary-container/10 text-center space-y-1 block cursor-pointer hover:bg-secondary-container/20 transition-colors">
                  <input type="file" onChange={handleFileUpload} className="hidden" />
                  <span className="material-symbols-outlined text-2xl text-secondary">cloud_upload</span>
                  <p className="text-xs font-bold text-primary">Upload Document to Vault</p>
                  <p className="text-[10px] text-outline">Aadhaar, Ration Card, Income Proof</p>
                </label>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export function AssistantClient() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-background flex items-center justify-center p-4 text-xs font-mono text-outline">
          Initializing Civic AI Engine...
        </div>
      }
    >
      <AssistantContent />
    </Suspense>
  );
}
