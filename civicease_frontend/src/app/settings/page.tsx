import type { Metadata } from 'next';
import { SettingsClient } from '@/components/SettingsClient';

export const metadata: Metadata = {
  title: 'Profile & Security Enclave Settings | CivicEase AI',
  description:
    'Manage on-device encrypted keys, cryptographic enclave settings, and Human-in-the-Loop authorization policies.',
  robots: {
    index: false,
    follow: true,
  },
};

export default function SettingsPage() {
  return <SettingsClient />;
}
