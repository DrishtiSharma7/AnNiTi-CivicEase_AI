import type { Metadata } from 'next';
import { SchemesClient } from '@/components/SchemesClient';

export const metadata: Metadata = {
  title: 'Discover 450+ Verified Central & State Welfare Schemes | CivicEase AI',
  description:
    'Search and explore 450+ verified Central & State government schemes tailored to your profile. Check instant eligibility for PM SVANidhi, PMAY-Urban 2.0, Ayushman Bharat PM-JAY, and DBT scholarships.',
  alternates: {
    canonical: 'https://civicease.gov.in/schemes',
  },
  openGraph: {
    title: 'Discover 450+ Verified Government Schemes | CivicEase AI',
    description:
      'Search schemes by category, ministry, state jurisdiction, and deterministic eligibility score. Includes official gazette citations and required document checklists.',
    url: 'https://civicease.gov.in/schemes',
    type: 'website',
  },
};

export default function DiscoverSchemesPage() {
  return <SchemesClient />;
}
