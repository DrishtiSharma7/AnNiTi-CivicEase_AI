'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Sidebar } from '@/components/Sidebar';
import { AppHeader } from '@/components/AppHeader';
import { usePersona } from '@/context/PersonaContext';

export function SchemesClient() {
  const { activePersona, language, savedSchemes, toggleSaveScheme, showToast } = usePersona();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [levelFilter, setLevelFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedSchemeForModal, setSelectedSchemeForModal] = useState<any | null>(null);

  const categories = [
    { id: 'all', label: 'All Schemes', count: 42 },
    { id: 'financial', label: 'Financial Assistance', count: 14 },
    { id: 'education', label: 'Education', count: 12 },
    { id: 'employment', label: 'Employment', count: 11 },
    { id: 'women', label: 'Women & Child Welfare', count: 9 },
    { id: 'healthcare', label: 'Healthcare', count: 8 },
    { id: 'agriculture', label: 'Agriculture', count: 6 },
    { id: 'housing', label: 'Housing', count: 5 },
  ];

  const handleExportPdf = () => {
    showToast('Generating official PDF digest for all qualified schemes...');
    setTimeout(() => {
      window.print();
    }, 600);
  };

  return (
    <div className="min-h-screen bg-[#f8f9ff] text-[#0b1c30] flex">
      <Sidebar />

      <div className="lg:pl-64 pl-0 flex-1 flex flex-col min-h-screen w-full">
        <AppHeader />

        <main className="pt-20 px-4 sm:px-6 lg:px-8 pb-12 flex-1 max-w-7xl w-full mx-auto space-y-6">
          {/* Top Headline / Intro Block */}
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
            <div className="flex flex-col">
              <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#86f2e4]/40 text-[#006f66] text-xs font-semibold tracking-wide uppercase">
                  <span className="material-symbols-outlined text-sm text-[#0D9488]">explore</span>
                  Public Welfare Intelligence
                </span>
                <span className="font-mono text-[#74777e] text-xs">DB v4.8 • Direct Benefit Transfer</span>
              </div>
              <h1 className="font-heading text-2xl sm:text-3xl text-[#001632] font-bold tracking-tight">
                Discover Benefits Made for You
              </h1>
              <p className="text-sm text-[#44474e] max-w-3xl mt-0.5">
                Search and explore 450+ verified Central & State government schemes tailored to your profile ({activePersona.name}, {activePersona.domicile}).
              </p>
            </div>

            {/* Quick Stats Ribbon */}
            <div className="flex items-center gap-3 bg-white px-4 py-2.5 rounded-xl shadow-sm border border-[#dce9ff] self-start md:self-auto">
              <div className="flex items-center gap-2 pr-3">
                <span className="w-2.5 h-2.5 rounded-full bg-[#0D9488] animate-pulse"></span>
                <div className="flex flex-col">
                  <span className="text-[11px] text-[#44474e]">Profile Sync</span>
                  <span className="text-sm text-[#001632] font-bold">18 Ready</span>
                </div>
              </div>
              <div className="w-px h-8 bg-[#dce9ff]"></div>
              <div className="flex items-center gap-2 pl-1">
                <span className="material-symbols-outlined text-[#0D9488] text-xl">savings</span>
                <div className="flex flex-col">
                  <span className="text-[11px] text-[#44474e]">Max Est. Benefit</span>
                  <span className="text-sm text-[#001632] font-bold">₹7,30,000+</span>
                </div>
              </div>
            </div>
          </div>

          {/* Preliminary AI Matching Notice (Statutory Advisory) */}
          <div className="bg-[#eff4ff] rounded-xl p-3.5 shadow-sm flex items-start gap-3 relative overflow-hidden border border-[#dce9ff]">
            <div className="absolute left-0 top-0 bottom-0 w-1 bg-[#0D9488]"></div>
            <div className="p-1.5 rounded-lg bg-white text-[#0D9488] mt-0.5 flex-shrink-0 shadow-sm">
              <span className="material-symbols-outlined text-lg leading-none">balance</span>
            </div>
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 w-full">
              <div className="flex flex-col">
                <span className="text-xs text-[#001632] font-bold flex items-center gap-1.5">
                  Preliminary AI Matching Notice
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#e9ddff] text-[#5516be] font-semibold">
                    Statutory Advisory
                  </span>
                </span>
                <p className="text-xs text-[#44474e] mt-0.5 leading-relaxed">
                  Compatibility scores are estimated based on your current profile data. Final verification and approval always rest with the competent Government authority.
                </p>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                <span className="font-mono text-[#74777e] text-xs">Gazette Ref: GSR-2024-B</span>
              </div>
            </div>
          </div>

          {/* Search & Filter Controls Surface */}
          <div className="bg-white rounded-2xl p-4 sm:p-5 shadow-sm border border-[#dce9ff] flex flex-col gap-4">
            {/* Primary Search Input with Autocomplete Assist */}
            <div className="relative w-full">
              <span className="material-symbols-outlined absolute left-3.5 top-1/2 -translate-y-1/2 text-[#74777e] text-xl">
                search
              </span>
              <input
                type="search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search schemes by keyword, department, or benefit (e.g. scholarship, vendor loan, housing)..."
                className="w-full h-12 pl-11 pr-24 bg-[#eff4ff] rounded-xl text-xs sm:text-sm text-[#0b1c30] placeholder:text-[#74777e] focus:outline-none focus:bg-white focus:ring-2 focus:ring-[#0D9488]/50 shadow-inner transition-all border border-transparent focus:border-[#0D9488]"
              />
              <div className="absolute right-2.5 top-1/2 -translate-y-1/2 flex items-center gap-1">
                {searchQuery ? (
                  <button
                    onClick={() => setSearchQuery('')}
                    className="p-1.5 text-[#74777e] hover:text-[#0b1c30] hover:bg-[#e5eeff] rounded-lg transition-colors"
                    title="Clear search"
                  >
                    <span className="material-symbols-outlined text-base">close</span>
                  </button>
                ) : (
                  <span className="hidden sm:inline-flex font-mono text-[11px] text-[#74777e] bg-[#e5eeff] px-2 py-0.5 rounded">
                    ⌘K
                  </span>
                )}
              </div>
            </div>

            {/* Category Pill Filters */}
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] sm:text-xs font-bold text-[#74777e] uppercase tracking-wider">
                  Category Sector
                </span>
                <span className="font-mono text-xs text-[#44474e]">Showing active classifications</span>
              </div>
              <div className="flex items-center gap-2 overflow-x-auto pb-1.5 text-xs sm:text-sm">
                {categories.map((cat) => {
                  const isActive = selectedCategory === cat.id;
                  return (
                    <button
                      key={cat.id}
                      type="button"
                      onClick={() => {
                        setSelectedCategory(cat.id);
                        showToast(`Filtered by Sector: ${cat.label}`);
                      }}
                      className={`whitespace-nowrap px-3.5 py-1.5 rounded-full font-semibold transition-all flex items-center gap-1.5 ${
                        isActive
                          ? 'bg-[#142B4A] text-white shadow-sm font-bold'
                          : 'bg-[#e5eeff] text-[#44474e] hover:bg-[#dce9ff] hover:text-[#0b1c30]'
                      }`}
                    >
                      <span>{cat.label}</span>
                      <span className={`text-[10px] font-mono px-1 rounded-full ${isActive ? 'bg-white/20 text-white' : 'text-[#74777e]'}`}>
                        {cat.count}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Micro-Divider */}
            <div className="w-full h-px bg-[#e5eeff]"></div>

            {/* Secondary Filter Selectors Row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {/* Level Dropdown */}
              <div className="flex flex-col gap-1">
                <label className="text-xs text-[#44474e] font-semibold flex items-center gap-1">
                  <span className="material-symbols-outlined text-sm text-[#74777e]">account_balance</span>
                  Government Level
                </label>
                <select
                  value={levelFilter}
                  onChange={(e) => setLevelFilter(e.target.value)}
                  className="w-full h-10 px-3 bg-[#eff4ff] rounded-xl text-xs text-[#0b1c30] focus:outline-none focus:ring-1 focus:ring-[#0D9488] border border-[#dce9ff] cursor-pointer"
                >
                  <option value="all">All (Central & State)</option>
                  <option value="central">Central Sector Only</option>
                  <option value="state">State Sponsored Only</option>
                </select>
              </div>

              {/* State Jurisdiction */}
              <div className="flex flex-col gap-1">
                <label className="text-xs text-[#44474e] font-semibold flex items-center gap-1">
                  <span className="material-symbols-outlined text-sm text-[#74777e]">location_on</span>
                  State Jurisdiction
                </label>
                <select className="w-full h-10 px-3 bg-[#eff4ff] rounded-xl text-xs text-[#0b1c30] focus:outline-none focus:ring-1 focus:ring-[#0D9488] border border-[#dce9ff] cursor-pointer">
                  <option>All India</option>
                  <option>Maharashtra (Citizen State)</option>
                  <option>Uttar Pradesh</option>
                  <option>Delhi</option>
                  <option>Karnataka</option>
                </select>
              </div>

              {/* Status Filter */}
              <div className="flex flex-col gap-1">
                <label className="text-xs text-[#44474e] font-semibold flex items-center gap-1">
                  <span className="material-symbols-outlined text-sm text-[#0D9488]">psychology</span>
                  Preliminary Status
                </label>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="w-full h-10 px-3 bg-[#eff4ff] rounded-xl text-xs text-[#0b1c30] focus:outline-none focus:ring-1 focus:ring-[#0D9488] border border-[#dce9ff] cursor-pointer"
                >
                  <option value="all">All Statuses (42)</option>
                  <option value="likely">Likely Matches (18)</option>
                  <option value="needs-info">Needs More Info (7)</option>
                  <option value="ineligible">Ineligible (17)</option>
                </select>
              </div>

              {/* Sort Order */}
              <div className="flex flex-col gap-1">
                <label className="text-xs text-[#44474e] font-semibold flex items-center gap-1">
                  <span className="material-symbols-outlined text-sm text-[#74777e]">sort</span>
                  Sort Order
                </label>
                <select className="w-full h-10 px-3 bg-[#eff4ff] rounded-xl text-xs text-[#0b1c30] focus:outline-none focus:ring-1 focus:ring-[#0D9488] border border-[#dce9ff] cursor-pointer">
                  <option>Match Relevance (High to Low)</option>
                  <option>Benefit Value (Financial Yield)</option>
                  <option>Application Deadline (Urgent First)</option>
                  <option>Recently Verified</option>
                </select>
              </div>
            </div>
          </div>

          {/* Schemes Data Grid Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-[#001632]">Recommended Schemes</span>
              <span className="px-2 py-0.5 rounded-full bg-[#dce9ff] font-mono text-xs font-semibold text-[#44474e]">
                4 Loaded
              </span>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => showToast('Search filter preset saved to your profile.')}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-[#dce9ff] text-[#44474e] hover:text-[#001632] text-xs font-semibold shadow-sm transition-colors"
              >
                <span className="material-symbols-outlined text-base text-[#0D9488]">bookmark_add</span>
                <span>Save Search Preset</span>
              </button>
            </div>
          </div>

          {/* Scheme Cards Stream (4 Exact Stitch Bespoke Cards) */}
          <div className="flex flex-col gap-4">
            {/* SCHEME 1: PM SVANidhi */}
            <article className="bg-white rounded-2xl p-5 sm:p-6 shadow-sm hover:shadow-md transition-all relative overflow-hidden border border-[#dce9ff]">
              {/* Top Glow Accent */}
              <div className="absolute top-0 left-0 right-0 h-1 bg-[#0D9488]"></div>

              <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4 pb-4">
                <div className="flex flex-col flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2 mb-2">
                    <span className="inline-flex items-center gap-1 text-xs text-[#001632] font-bold bg-[#e5eeff] px-2.5 py-0.5 rounded-md">
                      <span className="material-symbols-outlined text-xs text-[#0D9488]">assured_workload</span>
                      Central Sector
                    </span>
                    <span className="text-xs text-[#74777e]">•</span>
                    <span className="text-xs text-[#44474e] font-medium">Ministry of Housing and Urban Affairs</span>
                    <span className="text-xs text-[#74777e]">•</span>
                    <span className="font-mono text-[11px] text-[#74777e]">SCH-MOHUA-081</span>
                  </div>
                  <h2 className="font-heading text-lg sm:text-xl text-[#001632] font-bold tracking-tight hover:text-[#0D9488] cursor-pointer transition-colors">
                    PM Street Vendor's AtmaNirbhar Nidhi (PM SVANidhi)
                  </h2>
                  <p className="text-xs sm:text-sm text-[#44474e] mt-2 leading-relaxed">
                    Special micro-credit facility providing affordable collateral-free working capital loan to urban vendors to stimulate self-reliant enterprise resumption.
                  </p>
                </div>

                <div className="flex flex-col items-start lg:items-end gap-2 flex-shrink-0">
                  <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#0D9488]/10 text-[#0D9488] text-xs font-bold shadow-xs">
                    <span className="material-symbols-outlined text-base">verified</span>
                    <span>Likely matches (96% Match)</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-[#001632] font-heading text-lg font-bold bg-[#eff4ff] px-3 py-1 rounded-xl">
                    <span className="material-symbols-outlined text-[#0D9488] text-lg">currency_rupee</span>
                    <span>Up to ₹50,000 Loan</span>
                  </div>
                </div>
              </div>

              {/* Core Benefit Breakdown Strip */}
              <div className="bg-[#eff4ff]/70 rounded-xl p-3.5 mb-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 border border-[#dce9ff]/60">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-white flex items-center justify-center text-[#0D9488] shadow-xs">
                    <span className="material-symbols-outlined text-xl">payments</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-[10px] text-[#74777e] uppercase font-bold tracking-wider">
                      Key Financial Entitlement
                    </span>
                    <span className="text-xs text-[#001632] font-semibold">
                      Collateral-free working capital loan up to ₹50,000 with 7% annual interest subsidy & digital cashback up to ₹1,200/year.
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-1 text-[#0D9488] text-xs font-bold whitespace-nowrap bg-white px-2.5 py-1 rounded-lg shadow-sm border border-[#dce9ff]/40">
                  <span className="material-symbols-outlined text-sm">trending_up</span> 7% Interest Relief
                </div>
              </div>

              {/* Metadata & Eligibility Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1 mb-5">
                <div className="flex flex-col gap-1.5">
                  <span className="text-[11px] text-[#44474e] font-bold uppercase tracking-wider flex items-center gap-1">
                    <span className="material-symbols-outlined text-xs text-[#0D9488]">check_circle</span>
                    Matched Criteria (Your Profile)
                  </span>
                  <div className="flex flex-wrap gap-1.5 text-xs">
                    <span className="px-2.5 py-1 rounded-lg bg-[#e5eeff] text-[#0b1c30]">Age 18+</span>
                    <span className="px-2.5 py-1 rounded-lg bg-[#e5eeff] text-[#0b1c30]">Urban Vendor</span>
                    <span className="px-2.5 py-1 rounded-lg bg-[#e5eeff] text-[#0b1c30]">Possessing Vending ID</span>
                    <span className="px-2.5 py-1 rounded-lg bg-[#e5eeff] text-[#0b1c30]">Active Bank Account</span>
                  </div>
                </div>

                <div className="flex flex-col gap-1.5">
                  <span className="text-[11px] text-[#44474e] font-bold uppercase tracking-wider flex items-center gap-1">
                    <span className="material-symbols-outlined text-xs text-[#001632]">folder_open</span>
                    Required Verification Artifacts
                  </span>
                  <div className="flex flex-wrap items-center gap-2 text-xs">
                    <span className="inline-flex items-center gap-1 font-mono text-xs px-2.5 py-1 rounded-lg bg-white border border-[#dce9ff] text-[#001632] font-medium shadow-xs">
                      <span className="material-symbols-outlined text-xs text-[#0D9488]">task_alt</span> Aadhaar Card
                    </span>
                    <span className="inline-flex items-center gap-1 font-mono text-xs px-2.5 py-1 rounded-lg bg-white border border-[#dce9ff] text-[#001632] font-medium shadow-xs">
                      <span className="material-symbols-outlined text-xs text-[#0D9488]">task_alt</span> Vending Certificate
                    </span>
                    <span className="inline-flex items-center gap-1 font-mono text-xs px-2.5 py-1 rounded-lg bg-white border border-[#dce9ff] text-[#001632] font-medium shadow-xs">
                      <span className="material-symbols-outlined text-xs text-[#0D9488]">task_alt</span> Bank Passbook
                    </span>
                  </div>
                </div>
              </div>

              {/* Footer Action & Provenance Row */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-4 border-t border-[#dce9ff]/60">
                <div className="flex flex-wrap items-center gap-3 text-[#74777e] text-xs">
                  <span className="flex items-center gap-1 text-[#0b1c30] font-medium">
                    <span className="material-symbols-outlined text-base text-[#0D9488]">event</span>
                    Deadline: <span className="text-[#001632] font-bold">31 Dec 2025</span>
                  </span>
                  <span>•</span>
                  <a
                    className="flex items-center gap-1 text-[#44474e] hover:text-[#0D9488] transition-colors underline decoration-dotted font-mono"
                    href="https://pmsvanidhi.mohua.gov.in"
                    rel="noopener noreferrer"
                    target="_blank"
                  >
                    <span className="material-symbols-outlined text-sm">open_in_new</span>
                    pmsvanidhi.mohua.gov.in
                  </a>
                  <span>•</span>
                  <span className="flex items-center gap-1 text-[#74777e]">
                    <span className="material-symbols-outlined text-xs">verified</span>
                    Audited 2 days ago
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <Link
                    href="/assistant?q=Check%20PM%20SVANidhi%20detailed%20eligibility"
                    className="px-3.5 py-2 rounded-xl text-xs font-semibold text-[#0D9488] hover:bg-[#e5eeff] transition-colors"
                  >
                    Check Detailed Eligibility
                  </Link>
                  <Link
                    href="/assistant"
                    className="px-4 py-2 rounded-xl text-xs font-bold bg-[#001632] text-white hover:bg-[#142B4A] shadow-sm transition-all flex items-center gap-1.5"
                  >
                    <span>View Full Details</span>
                    <span className="material-symbols-outlined text-base">arrow_forward</span>
                  </Link>
                </div>
              </div>
            </article>

            {/* SCHEME 2: PMAY-Urban 2.0 */}
            <article className="bg-white rounded-2xl p-5 sm:p-6 shadow-sm hover:shadow-md transition-all relative overflow-hidden border border-[#dce9ff]">
              <div className="absolute top-0 left-0 right-0 h-1 bg-amber-500"></div>

              <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4 pb-4">
                <div className="flex flex-col flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2 mb-2">
                    <span className="inline-flex items-center gap-1 text-xs text-[#001632] font-bold bg-[#e5eeff] px-2.5 py-0.5 rounded-md">
                      <span className="material-symbols-outlined text-xs text-[#001632]">apartment</span>
                      Central Sponsor
                    </span>
                    <span className="text-xs text-[#74777e]">•</span>
                    <span className="text-xs text-[#44474e] font-medium">Ministry of Housing and Urban Affairs (MoHUA)</span>
                    <span className="text-xs text-[#74777e]">•</span>
                    <span className="font-mono text-[11px] text-[#74777e]">PMAY-U2-EXP</span>
                  </div>
                  <h2 className="font-heading text-lg sm:text-xl text-[#001632] font-bold tracking-tight hover:text-[#0D9488] cursor-pointer transition-colors">
                    Pradhan Mantri Awas Yojana (PMAY-Urban 2.0)
                  </h2>
                  <p className="text-xs sm:text-sm text-[#44474e] mt-2 leading-relaxed">
                    Affordable housing mission extending interest subsidies and direct financial assistance for pucca house acquisition or construction in statutory municipal zones.
                  </p>
                </div>

                <div className="flex flex-col items-start lg:items-end gap-2 flex-shrink-0">
                  <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-50 text-amber-800 text-xs font-bold shadow-xs border border-amber-200">
                    <span className="material-symbols-outlined text-base text-amber-600">error</span>
                    <span>Needs more information (Income proof requires refresh)</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-[#001632] font-heading text-lg font-bold bg-[#eff4ff] px-3 py-1 rounded-xl">
                    <span className="material-symbols-outlined text-[#0D9488] text-lg">currency_rupee</span>
                    <span>Up to ₹1.80 Lakh Subsidy</span>
                  </div>
                </div>
              </div>

              {/* Core Benefit Breakdown Strip */}
              <div className="bg-[#eff4ff]/70 rounded-xl p-3.5 mb-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 border border-[#dce9ff]/60">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-white flex items-center justify-center text-amber-600 shadow-xs">
                    <span className="material-symbols-outlined text-xl">real_estate_agent</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-[10px] text-[#74777e] uppercase font-bold tracking-wider">
                      Housing Subsidy Structure
                    </span>
                    <span className="text-xs text-[#001632] font-semibold">
                      Interest subsidy up to ₹1.80 Lakh on home loan for Economically Weaker Section (EWS) and Low Income Group (LIG) families.
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-1 text-[#001632] text-xs font-bold whitespace-nowrap bg-white px-2.5 py-1 rounded-lg shadow-sm border border-[#dce9ff]/40">
                  <span className="material-symbols-outlined text-sm text-[#0D9488]">check</span> Subsidized EMI Rate
                </div>
              </div>

              {/* Metadata & Eligibility Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1 mb-5">
                <div className="flex flex-col gap-1.5">
                  <span className="text-[11px] text-[#44474e] font-bold uppercase tracking-wider flex items-center gap-1">
                    <span className="material-symbols-outlined text-xs text-[#0D9488]">policy</span>
                    Eligibility Assessment Rules
                  </span>
                  <div className="flex flex-wrap gap-1.5 text-xs">
                    <span className="px-2.5 py-1 rounded-lg bg-amber-50 border border-amber-200 text-amber-900 font-medium flex items-center gap-1">
                      <span className="material-symbols-outlined text-xs">pending</span> Annual Income &lt; ₹3,00,000 (Verify)
                    </span>
                    <span className="px-2.5 py-1 rounded-lg bg-[#e5eeff] text-[#0b1c30]">Pucca house not owned anywhere in India</span>
                    <span className="px-2.5 py-1 rounded-lg bg-[#e5eeff] text-[#0b1c30]">Female Head Ownership (Preferred)</span>
                  </div>
                </div>

                <div className="flex flex-col gap-1.5">
                  <span className="text-[11px] text-[#44474e] font-bold uppercase tracking-wider flex items-center gap-1">
                    <span className="material-symbols-outlined text-xs text-[#001632]">folder_open</span>
                    Required Verification Artifacts
                  </span>
                  <div className="flex flex-wrap items-center gap-2 text-xs">
                    <span className="inline-flex items-center gap-1 font-mono text-xs px-2.5 py-1 rounded-lg bg-amber-100/60 text-amber-900 font-semibold border border-amber-300">
                      <span className="material-symbols-outlined text-xs text-amber-600">warning</span> Income Certificate (Expired)
                    </span>
                    <span className="inline-flex items-center gap-1 font-mono text-xs px-2.5 py-1 rounded-lg bg-white border border-[#dce9ff] text-[#001632] font-medium shadow-xs">
                      <span className="material-symbols-outlined text-xs text-[#0D9488]">task_alt</span> Aadhaar Card
                    </span>
                    <span className="inline-flex items-center gap-1 font-mono text-xs px-2.5 py-1 rounded-lg bg-white border border-[#dce9ff] text-[#74777e] font-medium shadow-xs">
                      <span className="material-symbols-outlined text-xs">pending</span> Affidavit of No Pucca House
                    </span>
                  </div>
                </div>
              </div>

              {/* Footer Action & Provenance Row */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-4 border-t border-[#dce9ff]/60">
                <div className="flex flex-wrap items-center gap-3 text-[#74777e] text-xs">
                  <span className="flex items-center gap-1 text-[#0b1c30] font-medium">
                    <span className="material-symbols-outlined text-base text-[#0D9488]">all_inclusive</span>
                    Deadline: <span className="text-[#001632] font-bold">Ongoing Rolling Application</span>
                  </span>
                  <span>•</span>
                  <a
                    className="flex items-center gap-1 text-[#44474e] hover:text-[#0D9488] transition-colors underline decoration-dotted font-mono"
                    href="https://pmay-urban.gov.in"
                    rel="noopener noreferrer"
                    target="_blank"
                  >
                    <span className="material-symbols-outlined text-sm">open_in_new</span>
                    pmay-urban.gov.in
                  </a>
                  <span>•</span>
                  <span className="flex items-center gap-1 text-[#74777e]">
                    <span className="material-symbols-outlined text-xs">verified</span>
                    Audited Yesterday
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <Link
                    href="/documents/audit"
                    className="px-4 py-2 rounded-xl text-xs font-bold bg-amber-600 text-white hover:bg-amber-700 shadow-sm transition-all flex items-center gap-1.5"
                  >
                    <span className="material-symbols-outlined text-base">cloud_upload</span>
                    <span>Resolve Missing Info</span>
                  </Link>
                </div>
              </div>
            </article>

            {/* SCHEME 3: Ayushman Bharat - PM-JAY */}
            <article className="bg-white rounded-2xl p-5 sm:p-6 shadow-sm hover:shadow-md transition-all relative overflow-hidden border border-[#dce9ff]">
              <div className="absolute top-0 left-0 right-0 h-1 bg-[#0D9488]"></div>

              <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4 pb-4">
                <div className="flex flex-col flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2 mb-2">
                    <span className="inline-flex items-center gap-1 text-xs text-[#001632] font-bold bg-[#e5eeff] px-2.5 py-0.5 rounded-md">
                      <span className="material-symbols-outlined text-xs text-[#0D9488]">local_hospital</span>
                      Central Scheme
                    </span>
                    <span className="text-xs text-[#74777e]">•</span>
                    <span className="text-xs text-[#44474e] font-medium">National Health Authority (NHA)</span>
                    <span className="text-xs text-[#74777e]">•</span>
                    <span className="font-mono text-[11px] text-[#74777e]">PMJAY-NHA-CORE</span>
                  </div>
                  <h2 className="font-heading text-lg sm:text-xl text-[#001632] font-bold tracking-tight hover:text-[#0D9488] cursor-pointer transition-colors">
                    Ayushman Bharat - PM-JAY (Pradhan Mantri Jan Arogya Yojana)
                  </h2>
                  <p className="text-xs sm:text-sm text-[#44474e] mt-2 leading-relaxed">
                    World’s largest government-funded healthcare assurance scheme offering complete cashless inpatient treatment across 29,000+ empaneled hospitals.
                  </p>
                </div>

                <div className="flex flex-col items-start lg:items-end gap-2 flex-shrink-0">
                  <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#0D9488]/10 text-[#0D9488] text-xs font-bold shadow-xs">
                    <span className="material-symbols-outlined text-base">verified</span>
                    <span>Likely matches (100% Match)</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-[#001632] font-heading text-lg font-bold bg-[#eff4ff] px-3 py-1 rounded-xl">
                    <span className="material-symbols-outlined text-[#0D9488] text-lg">currency_rupee</span>
                    <span>₹5,00,000 / Family / Year</span>
                  </div>
                </div>
              </div>

              {/* Core Benefit Breakdown Strip */}
              <div className="bg-[#eff4ff]/70 rounded-xl p-3.5 mb-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 border border-[#dce9ff]/60">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-white flex items-center justify-center text-[#0D9488] shadow-xs">
                    <span className="material-symbols-outlined text-xl">health_and_safety</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-[10px] text-[#74777e] uppercase font-bold tracking-wider">
                      Statutory Medical Coverage
                    </span>
                    <span className="text-xs text-[#001632] font-semibold">
                      Cashless health insurance up to ₹5,00,000 per family per year for secondary & tertiary hospital care, diagnostics, and medicines.
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-1 text-[#0D9488] text-xs font-bold whitespace-nowrap bg-white px-2.5 py-1 rounded-lg shadow-sm border border-[#dce9ff]/40">
                  <span className="material-symbols-outlined text-sm">domain_verification</span> Instant e-Card Eligible
                </div>
              </div>

              {/* Metadata & Eligibility Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1 mb-5">
                <div className="flex flex-col gap-1.5">
                  <span className="text-[11px] text-[#44474e] font-bold uppercase tracking-wider flex items-center gap-1">
                    <span className="material-symbols-outlined text-xs text-[#0D9488]">check_circle</span>
                    Matched Criteria (Your Profile)
                  </span>
                  <div className="flex flex-wrap gap-1.5 text-xs">
                    <span className="px-2.5 py-1 rounded-lg bg-[#e5eeff] text-[#0b1c30]">SECC 2011 Deprivation Verified</span>
                    <span className="px-2.5 py-1 rounded-lg bg-[#e5eeff] text-[#0b1c30]">Active Ration Card (NFSA)</span>
                    <span className="px-2.5 py-1 rounded-lg bg-[#e5eeff] text-[#0b1c30]">Family Composition Synced</span>
                  </div>
                </div>

                <div className="flex flex-col gap-1.5">
                  <span className="text-[11px] text-[#44474e] font-bold uppercase tracking-wider flex items-center gap-1">
                    <span className="material-symbols-outlined text-xs text-[#001632]">folder_open</span>
                    Required Verification Artifacts
                  </span>
                  <div className="flex flex-wrap items-center gap-2 text-xs">
                    <span className="inline-flex items-center gap-1 font-mono text-xs px-2.5 py-1 rounded-lg bg-white border border-[#dce9ff] text-[#001632] font-medium shadow-xs">
                      <span className="material-symbols-outlined text-xs text-[#0D9488]">task_alt</span> Ration Card (NFSA #89421)
                    </span>
                    <span className="inline-flex items-center gap-1 font-mono text-xs px-2.5 py-1 rounded-lg bg-white border border-[#dce9ff] text-[#001632] font-medium shadow-xs">
                      <span className="material-symbols-outlined text-xs text-[#0D9488]">task_alt</span> Aadhaar Card (Biometric Verified)
                    </span>
                  </div>
                </div>
              </div>

              {/* Footer Action & Provenance Row */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-4 border-t border-[#dce9ff]/60">
                <div className="flex flex-wrap items-center gap-3 text-[#74777e] text-xs">
                  <span className="flex items-center gap-1 text-[#0b1c30] font-medium">
                    <span className="material-symbols-outlined text-base text-[#0D9488]">all_inclusive</span>
                    Deadline: <span className="text-[#001632] font-bold">No deadline (Evergreen Benefit)</span>
                  </span>
                  <span>•</span>
                  <a
                    className="flex items-center gap-1 text-[#44474e] hover:text-[#0D9488] transition-colors underline decoration-dotted font-mono"
                    href="https://pmjay.gov.in"
                    rel="noopener noreferrer"
                    target="_blank"
                  >
                    <span className="material-symbols-outlined text-sm">open_in_new</span>
                    pmjay.gov.in
                  </a>
                  <span>•</span>
                  <span className="flex items-center gap-1 text-[#74777e]">
                    <span className="material-symbols-outlined text-xs">verified</span>
                    Audited 4 days ago
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => showToast('Downloading Ayushman Bharat e-Card Enrollment Guide...')}
                    className="px-4 py-2 rounded-xl text-xs font-bold bg-[#0D9488] text-white hover:bg-[#006f66] shadow-sm transition-all flex items-center gap-1.5"
                  >
                    <span className="material-symbols-outlined text-base">download_for_offline</span>
                    <span>Download e-Card Guide</span>
                  </button>
                </div>
              </div>
            </article>

            {/* SCHEME 4: Post-Matric Scholarship Scheme (Ineligible) */}
            <article className="bg-white/80 rounded-2xl p-5 sm:p-6 shadow-sm hover:shadow transition-all relative overflow-hidden opacity-90 hover:opacity-100 border border-[#dce9ff]">
              <div className="absolute top-0 left-0 right-0 h-1 bg-[#c4c6ce]"></div>

              <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4 pb-4">
                <div className="flex flex-col flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2 mb-2">
                    <span className="inline-flex items-center gap-1 text-xs text-[#44474e] font-bold bg-[#e5eeff] px-2.5 py-0.5 rounded-md">
                      <span className="material-symbols-outlined text-xs text-[#74777e]">school</span>
                      State & Central Joint
                    </span>
                    <span className="text-xs text-[#74777e]">•</span>
                    <span className="text-xs text-[#44474e] font-medium">Ministry of Social Justice & Empowerment</span>
                    <span className="text-xs text-[#74777e]">•</span>
                    <span className="font-mono text-[11px] text-[#74777e]">MSJE-SCH-2025</span>
                  </div>
                  <h2 className="font-heading text-lg sm:text-xl text-[#0b1c30] font-bold tracking-tight">
                    Post-Matric Scholarship Scheme for Minorities & OBCs
                  </h2>
                  <p className="text-xs sm:text-sm text-[#44474e] mt-2 leading-relaxed">
                    Educational scholarship to empower meritorious students from notified disadvantaged communities through higher secondary and undergraduate studies.
                  </p>
                </div>

                <div className="flex flex-col items-start lg:items-end gap-2 flex-shrink-0">
                  <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-red-50 text-red-800 text-xs font-bold border border-red-200">
                    <span className="material-symbols-outlined text-base text-red-600">block</span>
                    <span>Does not appear to match (Age limit exceeded)</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-[#44474e] font-heading text-lg font-semibold bg-[#eff4ff] px-3 py-1 rounded-xl">
                    <span className="material-symbols-outlined text-[#74777e] text-lg">currency_rupee</span>
                    <span>Up to ₹13,500/yr + Tuition</span>
                  </div>
                </div>
              </div>

              {/* Core Benefit Breakdown Strip (Muted Tone) */}
              <div className="bg-[#eff4ff]/50 rounded-xl p-3.5 mb-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 border border-[#dce9ff]/60">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-white flex items-center justify-center text-[#74777e] shadow-xs">
                    <span className="material-symbols-outlined text-xl">school</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-[10px] text-[#74777e] uppercase font-bold tracking-wider">
                      Academic Grant Structure
                    </span>
                    <span className="text-xs text-[#44474e] font-medium">
                      Full tuition fee reimbursement + monthly maintenance allowance up to ₹13,500/year for professional degree programs.
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-1 text-[#44474e] text-xs font-medium bg-white px-2.5 py-1 rounded-lg border border-[#dce9ff]/40">
                  <span className="material-symbols-outlined text-sm text-[#74777e]">history_edu</span> Direct DBT Transfer
                </div>
              </div>

              {/* Conflict / Ineligibility Rationale */}
              <div className="bg-red-50/80 rounded-xl p-3.5 mb-4 flex items-start gap-2.5 border border-red-200 text-red-900">
                <span className="material-symbols-outlined text-red-600 text-lg mt-0.5">info</span>
                <div className="flex flex-col text-xs">
                  <span className="font-bold">Ineligibility Diagnosis by CivicEase AI</span>
                  <p className="mt-0.5 leading-relaxed">
                    Asha Sharma is recorded as 32 years of age. Maximum age ceiling for entry-level Post-Matric Scholarship under MSJE criteria is 25 years. However, dependants or family members may qualify under a grouped Household File.
                  </p>
                </div>
              </div>

              {/* Footer */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-4 border-t border-[#dce9ff]/60">
                <div className="flex flex-wrap items-center gap-3 text-[#74777e] text-xs">
                  <span className="flex items-center gap-1 text-[#44474e]">
                    <span className="material-symbols-outlined text-base">event</span>
                    Next Academic Cycle: <span className="font-semibold">July 2025</span>
                  </span>
                  <span>•</span>
                  <a
                    className="flex items-center gap-1 text-[#74777e] hover:text-[#001632] transition-colors underline decoration-dotted font-mono"
                    href="https://scholarships.gov.in"
                    rel="noopener noreferrer"
                    target="_blank"
                  >
                    <span className="material-symbols-outlined text-sm">open_in_new</span>
                    scholarships.gov.in
                  </a>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => showToast('Opening MSJE statutory age ceiling guidelines...')}
                    className="px-4 py-2 rounded-xl text-xs font-bold bg-[#e5eeff] text-[#001632] hover:bg-[#dce9ff] transition-all flex items-center gap-1.5"
                  >
                    <span className="material-symbols-outlined text-base">rule</span>
                    <span>Criteria Breakdown</span>
                  </button>
                </div>
              </div>
            </article>
          </div>

          {/* Bottom Pagination, Record Count & Export Actions Bar */}
          <div className="bg-white rounded-2xl p-4 shadow-sm border border-[#dce9ff] flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3 flex-wrap justify-center sm:justify-start">
              <span className="text-xs sm:text-sm font-bold text-[#001632]">
                Showing 4 of 18 matched schemes
              </span>
              <span className="text-[#74777e] hidden sm:inline">•</span>
              <div className="flex items-center gap-2 text-xs">
                <span className="flex items-center gap-1 text-[#0D9488] font-semibold">
                  <span className="w-2 h-2 rounded-full bg-[#0D9488]"></span> 18 Likely
                </span>
                <span className="flex items-center gap-1 text-amber-600 font-semibold">
                  <span className="w-2 h-2 rounded-full bg-amber-500"></span> 7 Needs Info
                </span>
                <span className="flex items-center gap-1 text-[#74777e] font-semibold">
                  <span className="w-2 h-2 rounded-full bg-[#74777e]"></span> 17 Ineligible
                </span>
              </div>
            </div>

            {/* Pagination */}
            <div className="flex items-center gap-1">
              <span className="px-3 py-1 rounded-lg bg-[#142B4A] text-white text-xs font-bold shadow-sm">1</span>
              <button className="px-3 py-1 rounded-lg text-xs font-medium text-[#44474e] hover:bg-[#eff4ff] transition-colors">
                2
              </button>
              <button className="px-3 py-1 rounded-lg text-xs font-medium text-[#44474e] hover:bg-[#eff4ff] transition-colors">
                3
              </button>
              <span className="px-1 text-[#74777e] text-xs">...</span>
              <button className="px-3 py-1 rounded-lg text-xs font-medium text-[#44474e] hover:bg-[#eff4ff] transition-colors">
                5
              </button>
            </div>

            {/* Export PDF */}
            <button
              onClick={handleExportPdf}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#e5eeff] hover:bg-[#dce9ff] text-[#001632] text-xs font-bold transition-all shadow-xs"
            >
              <span className="material-symbols-outlined text-base text-[#0D9488]">picture_as_pdf</span>
              <span>Export Scheme Summary PDF</span>
            </button>
          </div>
        </main>
      </div>
    </div>
  );
}
