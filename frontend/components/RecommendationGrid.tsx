"use client";

import Image from "next/image";
import { motion } from "framer-motion";
import type { CatalogItem, Recommendation } from "@/lib/types";
import { Button } from "@/components/ui/Button";

interface RecommendationGridProps {
  items: CatalogItem[];
  recommendations: Recommendation[];
}

export function RecommendationGrid({ items, recommendations }: RecommendationGridProps) {
  const catalogMap = new Map(items.map((item) => [item.id, item]));

  return (
    <section className="mt-10">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Your curated lineup</h2>
        <Button variant="ghost">View all</Button>
      </div>
      <div className="mt-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {recommendations.map((recommendation) => {
          const outfit = catalogMap.get(recommendation.outfit_id) ?? recommendation.outfit;
          return (
            <motion.article
              key={recommendation.outfit_id}
              initial={{ opacity: 0, translateY: 16 }}
              animate={{ opacity: 1, translateY: 0 }}
              transition={{ duration: 0.35 }}
              className="rounded-3xl border border-slate-800 bg-slate-900/60 p-4"
            >
              <div className="relative aspect-square w-full overflow-hidden rounded-2xl">
                <Image
                  src={outfit.primary_image_url}
                  alt={outfit.name}
                  fill
                  className="object-cover"
                  sizes="(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw"
                />
              </div>
              <div className="mt-4 space-y-2">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-lg font-semibold">{outfit.name}</h3>
                    <p className="text-sm text-slate-400">{outfit.brand}</p>
                  </div>
                  <span className="rounded-full bg-brand/20 px-3 py-1 text-xs font-semibold text-brand">
                    {Math.round(recommendation.score * 100)}% match
                  </span>
                </div>
                <p className="text-sm text-slate-300">{recommendation.reason}</p>
                <div className="flex items-center justify-between pt-2">
                  <span className="text-base font-semibold text-white">
                    ₹{outfit.price.toLocaleString("en-IN")}
                  </span>
                  <Button variant="secondary">Try it on</Button>
                </div>
              </div>
            </motion.article>
          );
        })}
      </div>
    </section>
  );
}
