'use client';

import React from 'react';
import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-[#f8f9ff] text-[#0b1c30] flex flex-col items-center justify-center p-6 text-center font-sans">
      <div className="w-16 h-16 rounded-2xl bg-[#e5eeff] text-[#001632] flex items-center justify-center mb-4 shadow-sm">
        <span className="material-symbols-outlined text-3xl">travel_explore</span>
      </div>
      <h1 className="text-3xl font-extrabold font-heading text-[#001632] mb-2">404 — Page Not Found</h1>
      <p className="text-sm text-[#44474e] max-w-md mb-6 leading-relaxed">
        The welfare directory record or route you requested could not be found or has moved under latest gazette updates.
      </p>
      <div className="flex items-center gap-3">
        <Link
          href="/dashboard"
          className="px-5 py-2.5 bg-[#001632] text-white rounded-xl text-xs font-bold hover:bg-[#142B4A] transition-colors shadow-sm"
        >
          Go to Dashboard
        </Link>
        <Link
          href="/schemes"
          className="px-5 py-2.5 bg-[#0D9488] text-white rounded-xl text-xs font-bold hover:bg-[#006f66] transition-colors shadow-sm"
        >
          Discover Schemes
        </Link>
      </div>
    </div>
  );
}
