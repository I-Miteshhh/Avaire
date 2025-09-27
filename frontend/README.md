# Avaire Frontend

Next.js 14 app-router project styled with Tailwind CSS for the Avaire MVP.

## Scripts

```powershell
npm install
npm run dev
npm run build
npm run lint
```

## Structure

```
frontend/
├── app/
│   ├── layout.tsx         # Root layout with global providers
│   ├── page.tsx           # Landing page (hero + recommendations)
│   ├── catalog/           # Catalog browsing experience
│   ├── style-dna/         # Style DNA onboarding flow
│   ├── try-on/            # Virtual try-on studio
│   └── profile/           # Profile dashboard
├── components/            # UI building blocks
├── data/                  # Sample data used during local dev
├── lib/                   # Shared utilities and context
└── public/                # Static assets served by Next.js
```

### Key Components

- `HeroCarousel` – marketing hero with animated transitions.
- `FilterPanel` – responsive filtering for catalog items.
- `CatalogShowcase` – combines filters + recommendation grid.
- `StyleDNAForm` – multi-step onboarding wizard.
- `TryOnStudio` – upload workflow wired to backend try-on route.
- `ProfileDashboard` – summarises the user's Style DNA and history.

### Environment Variables

Set `NEXT_PUBLIC_API_URL` to point to the FastAPI backend (defaults to `http://localhost:8000`).

## Styling

Tailwind configuration (`tailwind.config.ts`) exposes:

- `brand` color scale (orange gradient used across CTAs)
- `shadow-glow` helper for CTA emphasis

Global styles defined in `app/globals.css` apply the dark theme.

## Data Fetching

During local development the app consumes sample data from `frontend/data/sampleCatalog.ts`. When your backend endpoints are ready, replace those imports with real API calls using the helper functions in `lib/api.ts`.
