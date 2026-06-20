# AEGIS — Strength in Order

## Brand
- **Name**: AEGIS
- **Tagline**: Strength in Order
- **Hero copy**: "Built through adversity. Forged through leadership."
- **Origin tag**: "Built by the line. For the line."
- **Mission**: More than a brand. It's a mindset. It's a way of life. Identity, belonging, earning your place.

## Architecture
- **Frontend**: React 19 + Tailwind + Shadcn UI, react-router-dom 7, framer-motion-style CSS animations
- **Backend**: FastAPI + Motor (MongoDB) + emergentintegrations Stripe Checkout
- **Auth**: None — guest checkout only (no accounts in v1)
- **Payments**: Stripe live (test key `sk_test_emergent` for dev) + manual "Reserve" flow
- **Seed system**: SEED_VERSION bump drops + reseeds products & campaigns

## Divisions (data model)
1. **CORE** — public, purchasable, steel-blue accent (#4A7FC1)
   - Tactical White Tee · Tactical Black Tee · CORE Hoodie · CORE Flexfit Cap
2. **LEGACY** — award-only, gold accent (#D4AF37)
   - Foundation Piece (numbered) · Dumpster Fire Patch · Mental Health Patch · A-Yard Legacy Sticker · Mental Health Legacy Sticker
   - Unlocked via redeem codes (`AYARD-MCSP-2024`, `MHT-CLINICIAN-2024`, `FOUNDATION-001`, `BUILT-ON-DISCIPLINE`)

## Campaigns (mission files)
- **001 A-YARD** — Mule Creek Five Buildings / One Mission (active, gold)
- **002 EOP** — Mental Health × Custody (active, red)
- **003 BUILDING 5** — The Standard Lives Here (active, green)
- **004 LOCKED** — coming soon
- **005 CLASSIFIED** — redacted

## Routes
- `/` — Splash gate (video-game boot sequence + ENTER button)
- `/home` — main landing
- `/core` — Core Division catalog
- `/legacy` — Legacy Division manifest + redeem + petition
- `/campaigns` / `/campaigns/:slug` — mission files
- `/product/:slug` — product detail (with legacy unlock flow if award-only)
- `/checkout`, `/success`
- `/logbook` — field records
- `/contact` — comms form

## Implemented (Feb 2026 — v1)
- Splash gate with boot sequence + animated ENTER button
- AEGIS rebrand: Cinzel display font, etched gold + steel-blue theme, antique HUD aesthetic
- Two-division architecture (CORE / LEGACY) with separate visuals & data
- Legacy redeem code system (POST /api/legacy/redeem) with localStorage persistence + petition form
- Campaigns system with 5 cards (active / locked / classified states)
- Product detail with size/color/qty, award-only gating, redeem inline
- Cart + Stripe + Manual order checkout (re-themed gold)
- Logbook + Contact form
- 5 pillars footer (Discipline / Unity / Hold the Line / Earned Never Issued / Strength in Order)
- Newsletter "Join the Order"
- **100% E2E tests passing** (19/19 backend, all frontend flows)

## Pending / Backlog
- **P1**: Push to user's repo `mrnickrushing/A-Yard-Apparel.git` (or rename to `AEGIS-Apparel`)
- **P1**: Real Stripe live key (when launching)
- **P1**: More CORE products (Tactical Black Hoodie, beanies, etc.)
- **P2**: Admin order dashboard + redeem-code management UI
- **P2**: Customer accounts (track legacy unlocks across devices)
- **P2**: Bulk / unit-order request flow (10+ for crews)
- **P2**: Sound design on splash gate (optional ambient hum on enter)
- **P3**: Email transactional templates (order confirmation, petition received)
- **P3**: Real apparel mockup imagery for hoodies & hats
