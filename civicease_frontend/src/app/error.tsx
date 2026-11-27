'use client';

import React, { useEffect } from 'react';
import Link from 'next/link';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('CivicEase AI Runtime Exception:', error);
  }, [error]);

  return (
    <div className="min-h-screen bg-[#f8f9ff] text-[#0b1c30] flex flex-col items-center justify-center p-6 text-center font-sans">
      <div className="w-16 h-16 rounded-2xl bg-red-100 text-red-600 flex items-center justify-center mb-4 shadow-sm">
        <span className="material-symbols-outlined text-3xl">warning</span>
      </div>
      <h2 className="text-2xl font-bold font-heading text-[#001632] mb-2">Something went wrong</h2>
      <p className="text-sm text-[#44474e] max-w-md mb-6 leading-relaxed">
        An unexpected runtime issue occurred. Click below to retry rendering or safely return to your sovereign dashboard.
      </p>
      <div className="flex items-center gap-3">
        <button
          onClick={() => reset()}
          className="px-5 py-2.5 bg-[#0D9488] text-white rounded-xl text-xs font-bold hover:bg-[#006f66] transition-colors shadow-sm"
        >
          Try Again
        </button>
        <Link
          href="/dashboard"
          className="px-5 py-2.5 bg-[#eff4ff] border border-[#dce9ff] text-[#001632] rounded-xl text-xs font-bold hover:bg-[#dce9ff] transition-colors shadow-sm"
        >
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
}
