'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Sidebar } from '@/components/Sidebar';
import { AppHeader } from '@/components/AppHeader';
import { usePersona } from '@/context/PersonaContext';

export function ApplicationsClient() {
  const { activePersona, language, showToast } = usePersona();

  const [applications, setApplications] = useState([
    {
      id: 'APP-MOHUA-2026-9921',
      scheme: "PM Street Vendor's AtmaNirbhar Nidhi (PM SVANidhi)",
      portal: 'pmsvanidhi.mohua.gov.in',
      date: '16 Nov 2026',
      amount: '₹10,000 (1st Tranche)',
      status: 'Awaiting Human Gate',
      statusColor: 'bg-purple-100 text-purple-800 border-purple-200',
      action: 'Biometric Sign-Off Required',
      progress: 85,
    },
    {
      id: 'APP-MAHA-DBT-88219',
      scheme: 'Post-Matric Scholarship Scheme',
      portal: 'mahadbt.maharashtra.gov.in',
      date: '10 Nov 2026',
      amount: '₹13,500 / Year',
      status: 'Submitted to State Portal',
      statusColor: 'bg-emerald-100 text-emerald-800 border-emerald-200',
      action: 'Under Scrutiny by Welfare Officer',
      progress: 60,
    },
  ]);

  const handleSignOff = (appId: string) => {
    showToast('Citizen OTP Sign-Off Complete. Application submitted to official portal!');
    setApplications((prev) =>
      prev.map((app) =>
        app.id === appId
          ? {
              ...app,
              status: 'Direct Benefit Transfer (DBT) In Flight',
              statusColor: 'bg-emerald-100 text-emerald-800 border-emerald-200',
              action: 'Disbursement Scheduled to Bank Account',
              progress: 95,
            }
          : app
      )
    );
  };

  return (
    <div className="min-h-screen bg-background text-on-surface flex">
      <Sidebar />

      <div className="lg:pl-64 pl-0 flex-1 flex flex-col min-h-screen w-full">
        <AppHeader />

        <main className="pt-20 px-4 sm:px-6 lg:px-8 pb-12 flex-1 max-w-7xl w-full mx-auto space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h1 className="font-heading font-extrabold text-xl sm:text-2xl text-primary">
                Citizen Welfare Applications Tracking
              </h1>
              <p className="text-xs text-on-surface-variant mt-1">
                Real-time DBT milestones & statutory non-hallucinatory tracking for {activePersona.name}
              </p>
            </div>
            <Link
              href="/schemes"
              className="px-4 py-2 rounded-xl bg-primary text-white text-xs font-bold shadow-sm hover:bg-primary-container self-start sm:self-auto"
            >
              + New Application
            </Link>
          </div>

          <div className="space-y-4">
            {applications.map((app) => (
              <div
                key={app.id}
                className="p-5 sm:p-6 rounded-2xl bg-surface-container-lowest border border-surface-container-high shadow-sm space-y-4"
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                  <div>
                    <span className="font-mono text-[10px] text-outline font-bold block">{app.id}</span>
                    <h2 className="font-heading font-bold text-base text-primary mt-0.5">{app.scheme}</h2>
                    <span className="text-xs text-on-surface-variant font-mono">Official Portal: {app.portal}</span>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-bold border ${app.statusColor} self-start`}
                  >
                    {app.status}
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-3.5 rounded-xl bg-surface-container-low text-xs border border-surface-container-high">
                  <div>
                    <span className="text-outline text-[10px] uppercase block">Grant / Sanction</span>
                    <span className="font-bold text-secondary text-sm">{app.amount}</span>
                  </div>
                  <div>
                    <span className="text-outline text-[10px] uppercase block">Filing Timestamp</span>
                    <span className="font-bold text-primary">{app.date}</span>
                  </div>
                  <div>
                    <span className="text-outline text-[10px] uppercase block">Current Next Step</span>
                    <span className="font-bold text-purple-700">{app.action}</span>
                  </div>
                </div>

                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-on-surface-variant font-medium">Application Completion Progress</span>
                    <span className="font-mono font-bold text-secondary">{app.progress}%</span>
                  </div>
                  <div className="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-secondary h-full rounded-full transition-all duration-700"
                      style={{ width: `${app.progress}%` }}
                    ></div>
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row sm:items-center justify-between pt-2 border-t border-surface-container-high text-xs gap-3">
                  <span className="text-outline text-[11px] font-mono">
                    Cryptographic Attestation Hash: 9f8a...34e1
                  </span>
                  {app.progress < 90 ? (
                    <button
                      type="button"
                      onClick={() => handleSignOff(app.id)}
                      className="px-4 py-2 rounded-xl bg-purple-700 hover:bg-purple-800 text-white font-bold text-xs flex items-center justify-center gap-1.5 shadow-sm transition-colors self-start sm:self-auto"
                    >
                      <span className="material-symbols-outlined text-sm">fingerprint</span>
                      <span>Sign-Off via Citizen OTP</span>
                    </button>
                  ) : (
                    <span className="text-secondary font-bold flex items-center gap-1 text-xs">
                      <span className="material-symbols-outlined text-sm">check_circle</span>
                      <span>Authorized by Citizen</span>
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </main>
      </div>
    </div>
  );
}
