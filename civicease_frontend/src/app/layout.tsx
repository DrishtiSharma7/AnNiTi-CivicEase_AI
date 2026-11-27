import './globals.css';
import type { Metadata, Viewport } from 'next';
import { PersonaProvider } from '@/context/PersonaContext';
import { AffidavitModal } from '@/components/AffidavitModal';

const siteUrl = 'https://civicease.gov.in';

export const viewport: Viewport = {
  themeColor: '#001632',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
};

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: 'CivicEase AI — Sovereign GovTech Platform | Welfare Benefits & Document Audit',
    template: '%s | CivicEase AI',
  },
  description:
    'AI-powered Sovereign GovTech platform for discovering 450+ Central & State government schemes, deterministic eligibility checking, synthetic document OCR audit, and Human-in-the-Loop sovereign execution under DPDP Act 2023.',
  keywords: [
    'CivicEase AI',
    'Government Schemes India',
    'PM SVANidhi',
    'PMAY Urban',
    'Ayushman Bharat PMJAY',
    'Direct Benefit Transfer DBT',
    'Welfare Scheme Eligibility',
    'Document OCR Audit',
    'DPDP Act 2023',
    'Sovereign AI GovTech',
    'MahaDBT',
    'UP eDistrict',
  ],
  authors: [{ name: 'CivicEase AI National GovTech Initiative' }],
  creator: 'National Civic Welfare AI Initiative',
  publisher: 'Government Digital Welfare Infrastructure',
  alternates: {
    canonical: siteUrl,
    languages: {
      'en-IN': siteUrl,
      'hi-IN': `${siteUrl}?lang=hi`,
    },
  },
  openGraph: {
    type: 'website',
    locale: 'en_IN',
    url: siteUrl,
    siteName: 'CivicEase AI',
    title: 'CivicEase AI — Sovereign GovTech Platform for Welfare Benefits',
    description:
      'Search 450+ verified Central & State government schemes, audit welfare documents with synthetic OCR, and prepare rejection-proof applications with DPDP Act 2023 compliance.',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'CivicEase AI — Citizen Welfare Discovery & Document Audit Platform',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'CivicEase AI — Sovereign GovTech Platform',
    description:
      'Discover government schemes, check deterministic eligibility, and audit citizen welfare documents with zero cloud retention.',
    images: ['/og-image.png'],
    creator: '@CivicEaseAI',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

const structuredData = {
  '@context': 'https://schema.org',
  '@graph': [
    {
      '@type': 'WebSite',
      '@id': `${siteUrl}/#website`,
      url: siteUrl,
      name: 'CivicEase AI',
      description: 'Sovereign GovTech Platform for Welfare Benefits & Document Audit',
      inLanguage: ['en-IN', 'hi-IN'],
      potentialAction: {
        '@type': 'SearchAction',
        target: `${siteUrl}/schemes?q={search_term_string}`,
        'query-input': 'required name=search_term_string',
      },
    },
    {
      '@type': 'GovernmentOrganization',
      '@id': `${siteUrl}/#organization`,
      name: 'CivicEase AI GovTech Initiative',
      url: siteUrl,
      logo: `${siteUrl}/logo.png`,
      sameAs: [
        'https://india.gov.in',
        'https://mygov.in',
      ],
      areaServed: {
        '@type': 'Country',
        name: 'India',
      },
    },
    {
      '@type': 'GovernmentService',
      '@id': `${siteUrl}/#service`,
      name: 'Public Welfare Intelligence & Eligibility Verification Service',
      serviceType: 'Public Welfare & Social Security Navigation',
      provider: {
        '@id': `${siteUrl}/#organization`,
      },
      areaServed: {
        '@type': 'Country',
        name: 'India',
      },
      audience: {
        '@type': 'Audience',
        audienceType: 'Indian Citizens, EWS, Street Vendors, Farmers, Students, Artisans',
      },
    },
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <head>
        {/* Resource Hints & Font Preconnects */}
        <link rel="dns-prefetch" href="https://fonts.googleapis.com" />
        <link rel="dns-prefetch" href="https://fonts.gstatic.com" />
        <link rel="preconnect" href="https://fonts.googleapis.com" crossOrigin="" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        
        {/* Optimized Fonts Loading */}
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap"
          rel="stylesheet"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200"
          rel="stylesheet"
        />

        {/* JSON-LD Structured Data for Google Rich Snippets */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
        />
      </head>
      <body className="bg-surface text-on-surface antialiased min-h-screen selection:bg-[#0D9488]/20 selection:text-[#001632]">
        <PersonaProvider>
          {children}
          <AffidavitModal />
        </PersonaProvider>
      </body>
    </html>
  );
}
