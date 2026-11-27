import type { Metadata } from 'next';
import { RegisterClient } from '@/components/RegisterClient';

export const metadata: Metadata = {
  title: 'Create Sovereign Citizen Profile | CivicEase AI',
  description:
    'Generate an on-device encrypted welfare profile under DPDP Act 2023. Zero cloud retention with client-side AES-256 GCM vault generation.',
  alternates: {
    canonical: 'https://civicease.gov.in/register',
  },
};

export default function RegisterPage() {
  return <RegisterClient />;
}
