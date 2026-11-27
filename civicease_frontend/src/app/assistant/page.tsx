import type { Metadata } from 'next';
import { AssistantClient } from '@/components/AssistantClient';

export const metadata: Metadata = {
  title: 'Civic AI Copilot & Voice Assistant | CivicEase AI',
  description:
    'Consult CivicEase AI in 22 official Indian languages for scheme qualification, tranche breakdown, synthetic OCR verification, and Human-in-the-Loop submission guidance.',
  alternates: {
    canonical: 'https://civicease.gov.in/assistant',
  },
  openGraph: {
    title: 'Civic AI Copilot — Multi-Lingual Welfare Assistant | CivicEase AI',
    description:
      'Ask questions about welfare eligibility, interest subsidies, and document requirements. Fully compliant with DPDP Act 2023 on-device encryption.',
    url: 'https://civicease.gov.in/assistant',
  },
};

export default function AssistantPage() {
  return <AssistantClient />;
}
