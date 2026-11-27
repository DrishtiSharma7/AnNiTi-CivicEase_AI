import type { Metadata } from 'next';
import { LoginClient } from '@/components/LoginClient';

export const metadata: Metadata = {
  title: 'Citizen Login & Sovereign Attestation | CivicEase AI',
  description:
    'Secure tri-modal citizen login via OTP, Password, or Passkey with UIDAI 2.4 compliant on-device Sovereign Enclave.',
  alternates: {
    canonical: 'https://civicease.gov.in/login',
  },
};

export default function LoginPage() {
  return <LoginClient />;
}
