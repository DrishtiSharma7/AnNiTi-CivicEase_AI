import type { Metadata } from 'next';
import { DocumentAuditClient } from '@/components/DocumentAuditClient';

export const metadata: Metadata = {
  title: 'AI Document Audit & Synthetic OCR Diff Engine | CivicEase AI',
  description:
    'Synthetic OCR Diff engine for income certificates, Aadhaar cards, and vending licenses. Automatically flags clerical variances and drafts Form Annexure-B Alias Affidavits.',
  alternates: {
    canonical: 'https://civicease.gov.in/documents/audit',
  },
  openGraph: {
    title: 'AI Document Audit & Synthetic OCR Diff Engine | CivicEase AI',
    description:
      'Zero-rejection welfare document verification. Audit certificates against official revenue ledgers before applying.',
    url: 'https://civicease.gov.in/documents/audit',
  },
};

export default function DocumentAuditPage() {
  return <DocumentAuditClient />;
}
