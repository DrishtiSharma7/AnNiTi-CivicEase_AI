'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { usePersona } from '@/context/PersonaContext';

export const Navbar = () => {
  const pathname = usePathname();
  const { language, toggleLanguage, activePersona, togglePersona } = usePersona();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-surface/95 backdrop-blur-xl shadow-[0_1px_8px_rgba(20,43,74,0.06)] border-b border-surface-container-high/60">
      {/* Top DPDP Act Compliance Ribbon */}
      <div className="w-full bg-primary-container text-on-primary py-1 px-4 lg:px-8">
        <div className="max-w-7xl mx-auto flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-[14px] text-secondary-fixed">verified</span>
            <span className="font-medium tracking-wide truncate">
              {language === 'en'
                ? 'National Civic Welfare AI Initiative • In alignment with DPDP Act 2023'
                : 'राष्ट्रीय नागरिक कल्याण AI पहल • DPDP 2023'}
            </span>
          </div>
          <div className="flex items-center gap-3">
            <span className="hidden sm:flex items-center gap-1.5 text-secondary-fixed font-mono text-[11px]">
              <span className="w-1.5 h-1.5 rounded-full bg-secondary-fixed animate-pulse"></span>
              AES-256 Sovereign Vault Active
            </span>
            <button
              onClick={togglePersona}
              className="text-[11px] bg-surface-container/20 hover:bg-surface-container/40 text-secondary-fixed px-2 py-0.5 rounded border border-secondary-fixed/30 transition-colors flex items-center gap-1"
              title="Switch Persona"
            >
              <span className="material-symbols-outlined text-xs">switch_account</span>
              <span>Test: {activePersona.name.split(' ')[0]}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Navbar */}
      <div className="h-16 max-w-7xl mx-auto px-4 lg:px-8 flex items-center justify-between">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-primary-container flex items-center justify-center text-secondary-fixed shadow-md group-hover:scale-105 transition-transform">
            <span className="material-symbols-outlined text-[22px]">account_balance</span>
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-1.5">
              <span className="font-heading font-bold text-lg text-primary tracking-tight">CivicEase</span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-secondary-container text-on-secondary-container uppercase tracking-wider">
                AI
              </span>
            </div>
            <span className="text-[10px] text-on-surface-variant font-medium tracking-wider uppercase">
              National Civic Discovery
            </span>
          </div>
        </Link>

        {/* Desktop Navigation Links */}
        <nav className="hidden lg:flex items-center gap-6">
          <Link
            href="/"
            className={`text-sm font-medium transition-colors ${
              pathname === '/' ? 'text-primary font-bold' : 'text-on-surface-variant hover:text-primary'
            }`}
          >
            {language === 'en' ? 'Home' : 'मुख्य पृष्ठ'}
          </Link>
          <Link
            href="/dashboard"
            className={`text-sm font-medium transition-colors ${
              pathname.startsWith('/dashboard') ? 'text-primary font-bold' : 'text-on-surface-variant hover:text-primary'
            }`}
          >
            {language === 'en' ? 'Dashboard' : 'डैशबोर्ड'}
          </Link>
          <Link
            href="/schemes"
            className={`text-sm font-medium transition-colors ${
              pathname.startsWith('/schemes') ? 'text-primary font-bold' : 'text-on-surface-variant hover:text-primary'
            }`}
          >
            {language === 'en' ? 'Discover Schemes' : 'योजनाएं खोजें'}
          </Link>
          <Link
            href="/assistant"
            className={`text-sm font-medium transition-colors flex items-center gap-1 ${
              pathname.startsWith('/assistant') ? 'text-primary font-bold' : 'text-on-surface-variant hover:text-primary'
            }`}
          >
            <span className="material-symbols-outlined text-sm text-secondary">neurology</span>
            {language === 'en' ? 'AI Assistant' : 'AI सहायक'}
          </Link>
          <Link
            href="/documents/audit"
            className={`text-sm font-medium transition-colors flex items-center gap-1 ${
              pathname.startsWith('/documents') ? 'text-primary font-bold' : 'text-on-surface-variant hover:text-primary'
            }`}
          >
            <span className="material-symbols-outlined text-sm text-error">rule_folder</span>
            {language === 'en' ? 'Document Audit' : 'दस्तावेज़ ऑडिट'}
          </Link>
        </nav>

        {/* Right Action Controls */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Language Toggle */}
          <div className="flex items-center bg-surface-container p-0.5 rounded-lg text-xs font-semibold">
            <button
              onClick={() => language !== 'en' && toggleLanguage()}
              className={`px-2.5 py-1 rounded transition-all ${
                language === 'en'
                  ? 'bg-surface-container-lowest text-primary shadow-sm font-bold'
                  : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              English
            </button>
            <button
              onClick={() => language !== 'hi' && toggleLanguage()}
              className={`px-2.5 py-1 rounded transition-all ${
                language === 'hi'
                  ? 'bg-surface-container-lowest text-primary shadow-sm font-bold'
                  : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              हिंदी
            </button>
          </div>

          {/* Auth Actions (Desktop) */}
          <div className="hidden sm:flex items-center gap-2">
            <Link
              href="/login"
              className="text-xs font-semibold text-on-surface-variant hover:text-primary px-3 py-2 transition-colors"
            >
              {language === 'en' ? 'Sign In' : 'लॉग इन'}
            </Link>
            <Link
              href="/register"
              className="h-9 px-4 rounded-xl bg-primary hover:bg-primary-container text-on-primary text-xs font-semibold flex items-center justify-center transition-all shadow-sm"
            >
              {language === 'en' ? 'Get Started' : 'शुरू करें'}
            </Link>
          </div>

          {/* Mobile Hamburger Menu Toggle */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="lg:hidden p-2 rounded-xl text-primary hover:bg-surface-container transition-colors"
            aria-label="Toggle mobile menu"
          >
            <span className="material-symbols-outlined text-2xl">
              {isMobileMenuOpen ? 'close' : 'menu'}
            </span>
          </button>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {isMobileMenuOpen && (
        <div className="lg:hidden bg-surface-container-lowest border-b border-surface-container-high px-6 py-5 shadow-xl space-y-4 animate-in slide-in-from-top-3 duration-200">
          <nav className="flex flex-col gap-2.5">
            <Link
              href="/"
              onClick={() => setIsMobileMenuOpen(false)}
              className="text-sm font-semibold text-primary py-2 px-3 rounded-lg hover:bg-surface-container"
            >
              {language === 'en' ? 'Home' : 'मुख्य पृष्ठ'}
            </Link>
            <Link
              href="/dashboard"
              onClick={() => setIsMobileMenuOpen(false)}
              className="text-sm font-semibold text-primary py-2 px-3 rounded-lg hover:bg-surface-container flex items-center gap-2"
            >
              <span className="material-symbols-outlined text-base text-primary">dashboard</span>
              <span>{language === 'en' ? 'Citizen Dashboard' : 'नागरिक डैशबोर्ड'}</span>
            </Link>
            <Link
              href="/schemes"
              onClick={() => setIsMobileMenuOpen(false)}
              className="text-sm font-semibold text-primary py-2 px-3 rounded-lg hover:bg-surface-container flex items-center gap-2"
            >
              <span className="material-symbols-outlined text-base text-primary">travel_explore</span>
              <span>{language === 'en' ? 'Discover Schemes' : 'योजनाएं खोजें'}</span>
            </Link>
            <Link
              href="/assistant"
              onClick={() => setIsMobileMenuOpen(false)}
              className="text-sm font-semibold text-primary py-2 px-3 rounded-lg hover:bg-surface-container flex items-center gap-2"
            >
              <span className="material-symbols-outlined text-base text-secondary">neurology</span>
              <span>{language === 'en' ? 'Civic AI Assistant' : 'AI सहायक'}</span>
            </Link>
            <Link
              href="/documents/audit"
              onClick={() => setIsMobileMenuOpen(false)}
              className="text-sm font-semibold text-primary py-2 px-3 rounded-lg hover:bg-surface-container flex items-center gap-2"
            >
              <span className="material-symbols-outlined text-base text-error">rule_folder</span>
              <span>{language === 'en' ? 'Document Audit Engine' : 'दस्तावेज़ ऑडिट'}</span>
            </Link>
          </nav>

          <div className="pt-3 border-t border-surface-container-high flex flex-col gap-2">
            <Link
              href="/login"
              onClick={() => setIsMobileMenuOpen(false)}
              className="w-full py-2.5 rounded-xl border border-surface-container-high text-center text-xs font-bold text-primary"
            >
              Sign In with OTP
            </Link>
            <Link
              href="/register"
              onClick={() => setIsMobileMenuOpen(false)}
              className="w-full py-2.5 rounded-xl bg-primary text-white text-center text-xs font-bold shadow-sm"
            >
              Create Sovereign Profile
            </Link>
          </div>
        </div>
      )}
    </header>
  );
};
