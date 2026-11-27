'use client';

import React from 'react';
import { Sidebar } from '@/components/Sidebar';
import { AppHeader } from '@/components/AppHeader';
import { usePersona } from '@/context/PersonaContext';

export function SettingsClient() {
  const { activePersona, personaId, togglePersona, language, showToast } = usePersona();

  return (
    <div className="min-h-screen bg-background text-on-surface flex">
      <Sidebar />

      <div className="lg:pl-64 pl-0 flex-1 flex flex-col min-h-screen w-full">
        <AppHeader />

        <main className="pt-20 px-4 sm:px-6 lg:px-8 pb-12 flex-1 max-w-4xl w-full mx-auto space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h1 className="font-heading font-extrabold text-xl sm:text-2xl text-primary">
                Sovereign Profile & Security Settings
              </h1>
              <p className="text-xs text-on-surface-variant mt-1">
                Manage your on-device encrypted vault, eKYC credentials, and DPDP privacy settings
              </p>
            </div>
            <button
              onClick={togglePersona}
              className="px-4 py-2 rounded-xl bg-surface-container-low border border-surface-container-high text-xs font-bold text-secondary hover:bg-secondary-container/30 self-start sm:self-auto transition-colors"
            >
              Toggle Test Persona
            </button>
          </div>

          {/* Profile Card */}
          <div className="p-5 sm:p-6 rounded-2xl bg-surface-container-lowest border border-surface-container-high shadow-sm space-y-4">
            <h2 className="font-heading font-bold text-sm text-primary uppercase tracking-wider">
              Citizen Identity Records
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="p-3.5 bg-surface-container-low rounded-xl">
                <span className="text-outline text-[10px] uppercase block">Full Legal Name</span>
                <span className="font-bold text-primary text-sm mt-0.5 block">{activePersona.name}</span>
              </div>

              <div className="p-3.5 bg-surface-container-low rounded-xl">
                <span className="text-outline text-[10px] uppercase block">Aadhaar UID</span>
                <span className="font-mono font-bold text-primary text-sm mt-0.5 block">{activePersona.aadhaar}</span>
              </div>

              <div className="p-3.5 bg-surface-container-low rounded-xl">
                <span className="text-outline text-[10px] uppercase block">State Domicile</span>
                <span className="font-bold text-primary mt-0.5 block">{activePersona.domicile}</span>
              </div>

              <div className="p-3.5 bg-surface-container-low rounded-xl">
                <span className="text-outline text-[10px] uppercase block">Income Tier</span>
                <span className="font-bold text-secondary text-sm mt-0.5 block">{activePersona.income}</span>
              </div>
            </div>
          </div>

          {/* Security & Cryptography */}
          <div className="p-5 sm:p-6 rounded-2xl bg-surface-container-lowest border border-surface-container-high shadow-sm space-y-4">
            <h2 className="font-heading font-bold text-sm text-primary uppercase tracking-wider">
              Cryptographic Enclave & Privacy
            </h2>

            <div className="space-y-3 text-xs leading-relaxed">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between p-3.5 bg-surface-container-low rounded-xl gap-3">
                <div className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-secondary text-xl">key</span>
                  <div>
                    <span className="font-bold text-primary block">On-Device Sovereign Key</span>
                    <span className="text-on-surface-variant text-[11px]">
                      AES-256 GCM client-side encryption. Zero central cloud storage.
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => showToast('Regenerating 256-bit client-side keypair in browser enclave...')}
                  className="px-3 py-1.5 rounded-lg bg-surface-container-lowest border border-surface-container-high text-xs font-bold text-primary hover:bg-surface-container self-start sm:self-auto"
                >
                  Rotate Key
                </button>
              </div>

              <div className="flex flex-col sm:flex-row sm:items-center justify-between p-3.5 bg-surface-container-low rounded-xl gap-3">
                <div className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-purple-700 text-xl">lock_person</span>
                  <div>
                    <span className="font-bold text-primary block">Human-in-the-Loop Gateway</span>
                    <span className="text-on-surface-variant text-[11px]">
                      Mandatory OTP/Biometric confirmation prior to any departmental submission.
                    </span>
                  </div>
                </div>
                <span className="px-2 py-1 rounded bg-purple-100 text-purple-800 text-[10px] font-bold font-mono self-start sm:self-auto">
                  ENFORCED
                </span>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
