import HeroCarousel from "@/components/HeroCarousel";
import { CatalogShowcase } from "@/components/CatalogShowcase";
import { sampleCatalog, sampleRecommendations } from "@/data/sampleCatalog";

export default function CatalogPage() {
  return (
    <div className="space-y-10">
      <HeroCarousel />
      <CatalogShowcase items={sampleCatalog} recommendations={sampleRecommendations} />
    </div>
  );
}
