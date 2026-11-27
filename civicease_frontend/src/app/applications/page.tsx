import type { Metadata } from 'next';
import { ApplicationsClient } from '@/components/ApplicationsClient';

export const metadata: Metadata = {
  title: 'Citizen Welfare Applications & DBT Tracking | CivicEase AI',
  description:
    'Track Direct Benefit Transfer (DBT) milestones, biometric sign-offs, and official departmental submissions in real-time under DPDP Act 2023.',
  alternates: {
    canonical: 'https://civicease.gov.in/applications',
  },
};

export default function ApplicationsPage() {
  return <ApplicationsClient />;
}
