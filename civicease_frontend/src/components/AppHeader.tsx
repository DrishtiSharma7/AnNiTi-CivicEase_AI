'use client';

import React from 'react';
import Link from 'next/link';
import { usePersona } from '@/context/PersonaContext';

export const AppHeader = () => {
  const { activePersona, personaId, togglePersona, language, toggleLanguage, toggleMobileSidebar, showToast } =
    usePersona();

  return (
    <header className="fixed top-0 left-0 lg:left-64 right-0 h-16 bg-surface-container-lowest/95 backdrop-blur-md shadow-[0_1px_8px_rgba(20,43,74,0.04)] border-b border-surface-container-high/60 z-30 flex items-center justify-between px-4 sm:px-6 lg:px-8">
      {/* Left: Mobile Hamburger Toggle + Search */}
      <div className="flex items-center gap-3 flex-1 max-w-xl">
        <button
          onClick={toggleMobileSidebar}
          className="lg:hidden p-2 rounded-xl text-primary hover:bg-surface-container transition-colors flex items-center justify-center"
          aria-label="Open navigation menu"
        >
          <span className="material-symbols-outlined text-2xl">menu</span>
        </button>

        <div className="relative flex items-center w-full">
          <span className="material-symbols-outlined absolute left-3 text-outline text-lg">search</span>
          <input
            type="search"
            placeholder={
              language === 'en'
                ? 'Search schemes, documents, subsidies...'
                : 'योजनाएं, दस्तावेज़, सब्सिडी खोजें...'
            }
            className="w-full h-10 pl-10 pr-4 bg-surface-container-low rounded-xl text-xs text-on-surface placeholder:text-outline focus:outline-none focus:bg-surface-container-lowest focus:ring-1 focus:ring-secondary transition-all border border-transparent focus:border-secondary/30"
          />
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-2 sm:gap-3 ml-3 sm:ml-6">
        {/* Persona Quick Toggle Badge */}
        <button
          onClick={togglePersona}
          className="flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-xl border border-secondary/30 bg-secondary-container/20 hover:bg-secondary-container/40 text-on-secondary-container text-xs transition-colors"
          title="Click to toggle between Asha Sharma (Clean) and Ramesh Kumar (Broken)"
        >
          <span className="material-symbols-outlined text-sm text-secondary">tune</span>
          <span className="font-semibold hidden sm:inline">
            Persona: <span className="underline">{activePersona.name}</span>
          </span>
          <span className="font-bold sm:hidden">{activePersona.name.split(' ')[0]}</span>
        </button>

        {/* Language Switcher */}
        <div className="flex items-center bg-surface-container-low p-0.5 sm:p-1 rounded-lg text-xs font-semibold">
          <button
            onClick={() => language !== 'en' && toggleLanguage()}
            className={`px-2 sm:px-2.5 py-1 rounded transition-colors ${
              language === 'en'
                ? 'bg-surface-container-lowest text-primary font-bold shadow-sm'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            EN
          </button>
          <button
            onClick={() => language !== 'hi' && toggleLanguage()}
            className={`px-2 sm:px-2.5 py-1 rounded transition-colors ${
              language === 'hi'
                ? 'bg-surface-container-lowest text-primary font-bold shadow-sm'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            हिं
          </button>
        </div>

        {/* Notifications with interactive toast */}
        <button
          onClick={() =>
            showToast(
              activePersona.status === 'clean'
                ? '3 New Gazette Notifications indexed today'
                : 'Urgent: Discrepancy affidavit pending submission'
            )
          }
          aria-label="Notifications"
          className="relative p-2 text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low rounded-xl transition-colors"
        >
          <span className="material-symbols-outlined text-xl">notifications</span>
          <span className="absolute top-1.5 right-1.5 w-4 h-4 bg-error text-white rounded-full flex items-center justify-center text-[10px] font-bold">
            3
          </span>
        </button>

        <div className="h-6 w-px bg-surface-container-high hidden sm:block"></div>

        {/* Citizen Profile Avatar */}
        <Link href="/settings" className="flex items-center gap-2 pl-1 hover:opacity-90 transition-opacity">
          <div className="w-8 h-8 rounded-full overflow-hidden bg-primary-container text-secondary-fixed flex items-center justify-center font-bold text-xs border border-secondary-fixed/30 shadow-sm">
            {activePersona.name
              .split(' ')
              .map((n) => n[0])
              .join('')}
          </div>
          <div className="hidden md:flex flex-col text-left">
            <span className="text-xs text-on-surface leading-tight font-bold">
              {language === 'en' ? activePersona.name : activePersona.nameHi}
            </span>
            <span className="text-[10px] text-secondary font-semibold leading-none">
              {activePersona.status === 'clean' ? 'Verified Citizen' : 'Discrepancy Pending'}
            </span>
          </div>
        </Link>
      </div>
    </header>
  );
};
