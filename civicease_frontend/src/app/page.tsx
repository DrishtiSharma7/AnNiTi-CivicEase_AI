import type { Metadata } from 'next';
import { LandingPageClient } from '@/components/LandingPageClient';

export const metadata: Metadata = {
  title: 'CivicEase AI — Sovereign GovTech Platform | Welfare Benefits & Document Audit',
  description:
    'Discover 450+ verified Central & State government schemes, audit welfare documents with synthetic OCR diff, and apply with zero rejection under the DPDP Act 2023.',
  alternates: {
    canonical: 'https://civicease.gov.in',
  },
  openGraph: {
    title: 'CivicEase AI — Sovereign GovTech Welfare Navigator',
    description:
      'Know Your Benefits. Fix Your Documents. Apply with Confidence. Your AI-powered assistant for government schemes in 22 languages.',
    url: 'https://civicease.gov.in',
    type: 'website',
  },
};

const faqStructuredData = {
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: [
    {
      '@type': 'Question',
      name: 'How does CivicEase AI guarantee zero document rejections?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'Our deterministic synthetic OCR Diff Engine cross-matches names, addresses, and family rosters against Aadhaar and official revenue ledger standards before you apply. If an abbreviation or clerical error is detected, it automatically generates an Annexure-B Alias Affidavit to prevent rejection.',
      },
    },
    {
      '@type': 'Question',
      name: 'Is my Aadhaar or personal data uploaded to a central AI cloud?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'Strictly No. Under Section 8 of the DPDP Act 2023, CivicEase AI utilizes an On-Device Sovereign Vault with AES-256 GCM encryption. Raw identity credentials are decrypted locally in your browser enclave with zero retention.',
      },
    },
    {
      '@type': 'Question',
      name: 'Can the AI apply on my behalf without my knowledge?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'Never. CivicEase AI enforces a mandatory Human-in-the-Loop (HITL) Sovereign Gateway. While the engine prepares verified dossiers, it is legally and technically prohibited from submitting without explicit citizen biometric or OTP authorization.',
      },
    },
    {
      '@type': 'Question',
      name: 'Which languages are supported for voice consultation?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'We support 22 official Indian languages, including Hindi, Marathi, Bengali, Tamil, Telugu, Kannada, Gujarati, and English, with localized vernacular dialect processing.',
      },
    },
  ],
};

export default function LandingPage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqStructuredData) }}
      />
      <LandingPageClient />
    </>
  );
}
