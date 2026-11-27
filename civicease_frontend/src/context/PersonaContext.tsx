'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

export interface PersonaProfile {
  id: 'asha' | 'ramesh';
  name: string;
  nameHi: string;
  phone: string;
  aadhaar: string;
  income: string;
  incomeNum: number;
  domicile: string;
  category: string;
  occupation: string;
  welfareValue: string;
  welfareValueNum: number;
  schemesMatchedCount: number;
  docHealth: number;
  status: 'clean' | 'broken';
  blockingIssuesCount: number;
  avatar: string;
}

export const PERSONAS: Record<'asha' | 'ramesh', PersonaProfile> = {
  asha: {
    id: 'asha',
    name: 'Asha Sharma',
    nameHi: 'आशा शर्मा',
    phone: '+91 98230 41092',
    aadhaar: '•••• •••• 8912',
    income: '₹1,80,000 / yr',
    incomeNum: 180000,
    domicile: 'Maharashtra (MahaDBT)',
    category: 'EWS / OBC',
    occupation: 'Micro-Vendor (Street Food)',
    welfareValue: '₹72,000 /yr',
    welfareValueNum: 72000,
    schemesMatchedCount: 18,
    docHealth: 85,
    status: 'clean',
    blockingIssuesCount: 0,
    avatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&q=80&w=150',
  },
  ramesh: {
    id: 'ramesh',
    name: 'Ramesh Kumar',
    nameHi: 'रमेश कुमार',
    phone: '+91 87002 91823',
    aadhaar: '•••• •••• 4921',
    income: '₹1,20,000 / yr',
    incomeNum: 120000,
    domicile: 'Uttar Pradesh (Tehsil Sadar)',
    category: 'General / EWS',
    occupation: 'Daily Wage Artisan',
    welfareValue: '₹35,000 /yr',
    welfareValueNum: 35000,
    schemesMatchedCount: 8,
    docHealth: 33,
    status: 'broken',
    blockingIssuesCount: 2,
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=150',
  },
};

interface PersonaContextType {
  activePersona: PersonaProfile;
  personaId: 'asha' | 'ramesh';
  language: 'en' | 'hi';
  isAffidavitOpen: boolean;
  affidavitSubmitted: boolean;
  isMobileSidebarOpen: boolean;
  toastMessage: string | null;
  savedSchemes: string[];
  setPersona: (id: 'asha' | 'ramesh') => void;
  togglePersona: () => void;
  setLanguage: (lang: 'en' | 'hi') => void;
  toggleLanguage: () => void;
  openAffidavit: () => void;
  closeAffidavit: () => void;
  submitAffidavit: () => void;
  openMobileSidebar: () => void;
  closeMobileSidebar: () => void;
  toggleMobileSidebar: () => void;
  showToast: (msg: string) => void;
  toggleSaveScheme: (id: string) => void;
}

const PersonaContext = createContext<PersonaContextType | undefined>(undefined);

export const PersonaProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [personaId, setPersonaId] = useState<'asha' | 'ramesh'>('asha');
  const [language, setLanguage] = useState<'en' | 'hi'>('en');
  const [isAffidavitOpen, setIsAffidavitOpen] = useState(false);
  const [affidavitSubmitted, setAffidavitSubmitted] = useState(false);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [savedSchemes, setSavedSchemes] = useState<string[]>(['svanidhi']);

  const showToast = (msg: string) => {
    setToastMessage(msg);
  };

  useEffect(() => {
    if (toastMessage) {
      const timer = setTimeout(() => {
        setToastMessage(null);
      }, 3500);
      return () => clearTimeout(timer);
    }
  }, [toastMessage]);

  const togglePersona = () => {
    const next = personaId === 'asha' ? 'ramesh' : 'asha';
    setPersonaId(next);
    showToast(`Switched Test Persona to ${PERSONAS[next].name} (${PERSONAS[next].status.toUpperCase()})`);
  };

  const handleSetPersona = (id: 'asha' | 'ramesh') => {
    setPersonaId(id);
    showToast(`Active Persona: ${PERSONAS[id].name}`);
  };

  const toggleLanguage = () => {
    const nextLang = language === 'en' ? 'hi' : 'en';
    setLanguage(nextLang);
    showToast(nextLang === 'hi' ? 'भाषा बदलकर हिंदी कर दी गई है' : 'Language switched to English');
  };

  const openAffidavit = () => setIsAffidavitOpen(true);
  const closeAffidavit = () => setIsAffidavitOpen(false);
  const submitAffidavit = () => {
    setAffidavitSubmitted(true);
    setIsAffidavitOpen(false);
    showToast('Form Annexure-B Affidavit digitally signed & bound to profile!');
  };

  const openMobileSidebar = () => setIsMobileSidebarOpen(true);
  const closeMobileSidebar = () => setIsMobileSidebarOpen(false);
  const toggleMobileSidebar = () => setIsMobileSidebarOpen((prev) => !prev);

  const toggleSaveScheme = (id: string) => {
    setSavedSchemes((prev) => {
      const exists = prev.includes(id);
      const next = exists ? prev.filter((s) => s !== id) : [...prev, id];
      showToast(exists ? 'Removed from Bookmarks' : 'Saved to Bookmarked Schemes');
      return next;
    });
  };

  // Dynamically reflect affidavit submission in Ramesh's profile
  const baseProfile = PERSONAS[personaId];
  const activePersona: PersonaProfile = {
    ...baseProfile,
    docHealth:
      personaId === 'ramesh' && affidavitSubmitted
        ? 80
        : baseProfile.docHealth,
    blockingIssuesCount:
      personaId === 'ramesh' && affidavitSubmitted
        ? 1
        : baseProfile.blockingIssuesCount,
    status:
      personaId === 'ramesh' && affidavitSubmitted
        ? 'clean'
        : baseProfile.status,
  };

  return (
    <PersonaContext.Provider
      value={{
        activePersona,
        personaId,
        language,
        isAffidavitOpen,
        affidavitSubmitted,
        isMobileSidebarOpen,
        toastMessage,
        savedSchemes,
        setPersona: handleSetPersona,
        togglePersona,
        setLanguage,
        toggleLanguage,
        openAffidavit,
        closeAffidavit,
        submitAffidavit,
        openMobileSidebar,
        closeMobileSidebar,
        toggleMobileSidebar,
        showToast,
        toggleSaveScheme,
      }}
    >
      {children}

      {/* Global Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 max-w-sm bg-primary-container text-white px-4 py-3 rounded-2xl shadow-2xl border border-secondary/40 flex items-center gap-3 animate-in fade-in slide-in-from-bottom-5 duration-300">
          <span className="material-symbols-outlined text-secondary-fixed text-xl">info</span>
          <span className="text-xs font-medium leading-snug">{toastMessage}</span>
          <button
            onClick={() => setToastMessage(null)}
            className="ml-auto text-white/60 hover:text-white"
          >
            <span className="material-symbols-outlined text-sm">close</span>
          </button>
        </div>
      )}
    </PersonaContext.Provider>
  );
};

export const usePersona = () => {
  const context = useContext(PersonaContext);
  if (!context) {
    throw new Error('usePersona must be used within a PersonaProvider');
  }
  return context;
};
