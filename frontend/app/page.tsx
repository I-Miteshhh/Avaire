import HeroCarousel from "@/components/HeroCarousel";
import { CatalogShowcase } from "@/components/CatalogShowcase";
import { sampleCatalog, sampleRecommendations } from "@/data/sampleCatalog";
import { Suspense } from "react";

export default function HomePage() {
  return (
    <div className="space-y-10">
      <HeroCarousel />
      <Suspense fallback={<div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6">Loading catalog…</div>}>
        <LandingCatalog />
      </Suspense>
    </div>
  );
}

async function LandingCatalog() {
  const items = sampleCatalog;

  return (
    <CatalogShowcase items={items} recommendations={sampleRecommendations} />
  );
}
