'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { usePersona } from '@/context/PersonaContext';

export const Sidebar = () => {
  const pathname = usePathname();
  const { activePersona, personaId, togglePersona, language, isMobileSidebarOpen, closeMobileSidebar } = usePersona();

  const navItems = [
    { href: '/dashboard', icon: 'dashboard', label: language === 'en' ? 'Dashboard' : 'डैशबोर्ड' },
    { href: '/assistant', icon: 'neurology', label: language === 'en' ? 'AI Assistant' : 'AI सहायक', highlight: true },
    { href: '/schemes', icon: 'travel_explore', label: language === 'en' ? 'Discover Schemes' : 'योजनाएं खोजें' },
    {
      href: '/documents/audit',
      icon: 'rule_folder',
      label: language === 'en' ? 'Document Audit' : 'दस्तावेज़ ऑडिट',
      badge: activePersona.blockingIssuesCount > 0 ? activePersona.blockingIssuesCount : undefined,
    },
    { href: '/applications', icon: 'assignment_turned_in', label: language === 'en' ? 'Applications' : 'आवेदन' },
    { href: '/settings', icon: 'settings', label: language === 'en' ? 'Profile & Settings' : 'सेटिंग्स' },
  ];

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {isMobileSidebarOpen && (
        <div
          onClick={closeMobileSidebar}
          className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm lg:hidden transition-opacity"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed left-0 top-0 h-full w-64 bg-surface-container-lowest shadow-[0_1px_8px_rgba(20,43,74,0.06)] border-r border-surface-container-high/60 z-50 flex flex-col justify-between pt-5 pb-6 transition-transform duration-300 ease-in-out ${
          isMobileSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        <div className="flex flex-col">
          {/* Brand Header */}
          <div className="px-5 pb-5 flex items-center justify-between">
            <Link href="/" onClick={closeMobileSidebar} className="flex items-center gap-3 group">
              <div className="w-9 h-9 rounded-xl bg-primary-container flex items-center justify-center text-secondary-fixed shadow-sm">
                <span className="material-symbols-outlined text-[20px]">account_balance</span>
              </div>
              <div className="flex flex-col">
                <span className="font-heading text-base text-primary font-bold leading-tight">CivicEase AI</span>
                <span className="text-[10px] text-secondary font-semibold tracking-wider uppercase">
                  Citizen Navigator
                </span>
              </div>
            </Link>

            {/* Mobile Close Button */}
            <button
              onClick={closeMobileSidebar}
              className="lg:hidden p-1.5 rounded-lg text-outline hover:text-on-surface hover:bg-surface-container"
              aria-label="Close sidebar"
            >
              <span className="material-symbols-outlined text-lg">close</span>
            </button>
          </div>

          {/* Digital ID Linked Card */}
          <div className="px-4 py-2 mb-3">
            <div className="flex items-center justify-between bg-surface-container-low px-3 py-2.5 rounded-xl border border-surface-container-high">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-secondary text-base">verified_user</span>
                <div className="flex flex-col">
                  <span className="text-xs font-semibold text-on-surface">Digital ID Linked</span>
                  <span className="font-mono text-[10px] text-on-surface-variant font-medium">
                    Aadhaar {activePersona.aadhaar}
                  </span>
                </div>
              </div>
              <button
                onClick={togglePersona}
                className="text-[10px] bg-white border border-surface-container-high px-2 py-0.5 rounded text-primary hover:bg-secondary-container font-semibold transition-colors"
                title="Switch between Asha Sharma & Ramesh Kumar"
              >
                Switch
              </button>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex flex-col gap-1 px-3">
            {navItems.map((item) => {
              const isActive = pathname === item.href || (item.href !== '/dashboard' && pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={closeMobileSidebar}
                  className={`flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-primary-container text-on-primary font-bold shadow-sm'
                      : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span
                      className={`material-symbols-outlined text-lg ${
                        isActive ? 'text-secondary-fixed' : item.highlight ? 'text-secondary' : ''
                      }`}
                    >
                      {item.icon}
                    </span>
                    <span>{item.label}</span>
                  </div>
                  {item.badge !== undefined && (
                    <span className="px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-error text-white">
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Sovereign Vault Footer Widget */}
        <div className="px-4 flex flex-col gap-3">
          <div className="bg-surface-container p-3 rounded-xl border border-surface-container-high">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-medium text-on-surface-variant">Sovereign Vault</span>
              <span className="text-xs font-bold text-secondary">Active</span>
            </div>
            <div className="w-full bg-surface-container-highest h-1.5 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  activePersona.status === 'clean' ? 'bg-secondary w-4/5' : 'bg-amber-500 w-2/5'
                }`}
              ></div>
            </div>
            <p className="text-[11px] text-on-surface-variant mt-1.5 font-medium">
              {activePersona.status === 'clean' ? '8 of 10 Credentials Synced' : '4 of 10 Synced (Audit Needed)'}
            </p>
          </div>

          <div className="flex items-center justify-between px-2 text-outline text-[11px]">
            <span className="flex items-center gap-1">
              <span className="material-symbols-outlined text-xs">security</span> 256-bit Encrypted
            </span>
            <span className="text-secondary font-semibold">v2.4 UIDAI</span>
          </div>
        </div>
      </aside>
    </>
  );
};
