import type { Metadata } from 'next';
import { DashboardClient } from '@/components/DashboardClient';

export const metadata: Metadata = {
  title: 'Citizen Welfare Dashboard | Sovereign Enclave | CivicEase AI',
  description:
    'Real-time sovereign welfare dashboard. Track 5-stage autonomous onboarding, document health index, expiring certificates, and synchronized Gazette updates.',
  robots: {
    index: false, // Protected citizen vault, keep indexed off for dashboard personal data
    follow: true,
  },
};

export default function DashboardPage() {
  return <DashboardClient />;
}
