# CivicEase AI — Sovereign GovTech Platform (Frontend)

CivicEase AI is an AI-powered GovTech sovereign platform built with **Next.js (App Router)**, **TypeScript**, and **Tailwind CSS**. It is engineered to help citizens discover government welfare schemes, check deterministic eligibility, audit physical documents with synthetic OCR, and prepare official dossiers with a mandatory **Human-in-the-Loop (HITL)** safeguard under India's **Digital Personal Data Protection (DPDP) Act 2023**.

Designed in alignment with the Google Stitch project: `https://stitch.google.com/projects/10667625160279114455`.

---

## 🚀 Key Features & Screens

1. **Public Landing Page (`/`)**:
   - Institutional banner with DPDP Act 2023 compliance notice.
   - Hero section featuring live audited citizen profile preview (Asha Kumari).
   - "The Administrative Gap" section explaining why ₹3.4 Lakh Crores goes unclaimed.
   - 6-Step Autonomous Welfare Journey (Discover, Qualify, Audit, Prepare, Human Gate, Track).
   - Vernacular AI capabilities & Universal scheme coverage (450+ schemes).
   - FAQ accordion & multi-lingual start prompt.

2. **Citizen Login & Sovereign OTP (`/login`)**:
   - Sovereign Attestation Node UIDAI 2.4.
   - Tri-modal authentication: Mobile / Aadhaar OTP, Password, and FIDO2/Touch ID Passkey.
   - **Evaluator Sandbox Personas (1-Click Auto Fill)**:
     - **Asha Sharma (Clean Profile)**: 3 schemes auto-matched, valid documents, ₹72,000/yr benefit.
     - **Ramesh Kumar (Edge Case)**: Name mismatch (`Ramesh Kr.` vs `Ramesh Kumar`) and expired income certificate.
   - DPDP Act 2023 zero-retention disclosure.

3. **Citizen Registration & Domicile Vault (`/register`)**:
   - 3-step registration flow: Credentials -> Language & Domicile -> Privacy Vault.
   - Integrated state registries (MahaDBT Maharashtra, Kutumba Karnataka, etc.).
   - Multi-lingual selection (Hindi, Marathi, English, Tamil, Bengali, Telugu).
   - Client-side AES-256 GCM vault key generation.

4. **Citizen Dashboard (`/dashboard`)**:
   - Global GovTech sidebar with Digital ID sync status and 256-bit encryption indicator.
   - Reactive persona switcher (Asha Sharma vs Ramesh Kumar).
   - 5-stage Autonomous Onboarding Track (Discover, Qualify, Audit, Prepare, Track).
   - 4 metric cards: Potential Welfare Value, Schemes Matched, Document Health, Active Applications.
   - Urgent notifications for expiring certificates or name discrepancies.
   - Sovereign Entitlement Engine with high-probability schemes (PM SVANidhi, PMAY-Urban 2.0, Ayushman Bharat).
   - Real-time Gazette Ingestion widget (v24.8.2).
   - Inline Civic AI Copilot.

5. **Discover Schemes (`/schemes`)**:
   - Search with keyboard shortcuts (⌘K).
   - Sector category pills (Financial, Education, Employment, Healthcare, Housing, Agriculture).
   - Faceted filters (Central/State sector, state jurisdiction, match probability).
   - Comprehensive scheme breakdown with eligibility criteria, required documents, and official portal deep-links.

6. **Conversational AI Assistant (`/assistant`)**:
   - Multi-lingual reasoning engine with audio TTS toggle.
   - Chat consultation thread with rich GovTech cards (loan tranches, document readiness checklists).
   - Interactive voice input and file attachment simulation.
   - Live citizen context summary & drag-and-drop cloud vault upload widget.

7. **AI Document Audit & Synthetic OCR Engine (`/documents/audit`)**:
   - High-resolution split-view canvas (50% / 50%).
   - Interactive UP Revenue Council Income Certificate replica with zoom, rotate, and bounding box toggles.
   - Synthetic OCR overlays highlighting:
     - **Red Bounding Box**: Name mismatch (`Ramesh Kr.` vs `Ramesh Kumar`).
     - **Amber Bounding Box**: Expired certificate validity.
     - **Green Bounding Box**: Verified income below EWS ceiling & digital signature.
   - **1-Click Legal Remediation Modal (Form Annexure-B Alias Affidavit)**.

8. **Citizen Applications Tracker (`/applications`)**:
   - Milestone tracking for direct benefit transfers (DBT).
   - Mandatory Human Gate sign-off via citizen OTP/biometrics.

---

## 🛠️ Tech Stack & Design Tokens

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + Custom GovTech Design Tokens:
  - Deep Institutional Navy (`#142B4A`)
  - Secondary Public Trust Teal (`#0D9488`)
  - AI Action Cyan (`#22D3EE`)
  - Human Safeguard Purple (`#8B5CF6`)
  - Surface Off-White (`#F8FAFC`)
- **Typography**: Manrope (Headings & Numeric Entitlements) + Inter (Interface & Reading)
- **Icons**: Material Symbols Outlined + Lucide React

---

## 🏃 Running the Application

```bash
# Install dependencies
npm install

# Run the development server
npm run dev

# Open in browser
http://localhost:3000
```
