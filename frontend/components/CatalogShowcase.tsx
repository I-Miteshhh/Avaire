"use client";

import { useState } from "react";
import type { CatalogItem, Recommendation } from "@/lib/types";
import { FilterPanel } from "@/components/FilterPanel";
import { RecommendationGrid } from "@/components/RecommendationGrid";

interface CatalogShowcaseProps {
  items: CatalogItem[];
  recommendations: Recommendation[];
}

export function CatalogShowcase({ items, recommendations }: CatalogShowcaseProps) {
  const [filtered, setFiltered] = useState<CatalogItem[]>(items);

  return (
    <section className="space-y-6">
      <FilterPanel items={items} onFilter={setFiltered} />
      <RecommendationGrid items={filtered} recommendations={recommendations} />
    </section>
  );
}
