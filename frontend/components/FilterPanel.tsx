"use client";

import { useEffect, useMemo, useState, type ChangeEvent } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { CatalogItem, FilterState } from "@/lib/types";
import { Button } from "@/components/ui/Button";

const categories = [
  { label: "All", value: null },
  { label: "Indian Wear", value: "indian_wear" },
  { label: "Western", value: "western_wear" },
  { label: "Fusion", value: "fusion" }
] as const;

interface FilterPanelProps {
  items: CatalogItem[];
  onFilter: (filtered: CatalogItem[]) => void;
}

export function FilterPanel({ items, onFilter }: FilterPanelProps) {
  const [state, setState] = useState<FilterState>({
    search: "",
    category: null,
    occasion: null,
    priceRange: [1500, 8000],
    colors: [],
    sizes: [],
    tags: []
  });

  const filtered = useMemo(() => {
  return items.filter((item) => {
      const matchesSearch = state.search
        ? item.name.toLowerCase().includes(state.search.toLowerCase()) ||
          item.description.toLowerCase().includes(state.search.toLowerCase())
        : true;
      const matchesCategory = state.category ? item.category === state.category : true;
      const matchesOccasion = state.occasion ? item.occasion === state.occasion : true;
      const matchesPrice = item.price >= state.priceRange[0] && item.price <= state.priceRange[1];
      const matchesColor = state.colors.length
        ? state.colors.some((color: string) => item.colors.includes(color))
        : true;
      const matchesSize = state.sizes.length
        ? state.sizes.some((size: string) => item.sizes.includes(size))
        : true;
      const matchesTag = state.tags.length
        ? state.tags.some((tag: string) => item.tags.includes(tag))
        : true;

      return matchesSearch && matchesCategory && matchesOccasion && matchesPrice && matchesColor && matchesSize && matchesTag;
    });
  }, [items, state]);

  useEffect(() => onFilter(filtered), [filtered, onFilter]);

  return (
    <section className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <input
          type="search"
          placeholder="Search outfits, colors, vibes"
          className="w-full rounded-full border border-slate-700 bg-slate-950 px-4 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/50 md:w-1/2"
          value={state.search}
          onChange={(event: ChangeEvent<HTMLInputElement>) =>
            setState((prev: FilterState) => ({
              ...prev,
              search: event.target.value
            }))
          }
        />
        <div className="flex gap-2">
          {categories.map((category) => (
            <span key={category.label}>
              <Button
                variant={state.category === category.value ? "primary" : "ghost"}
                onClick={() =>
                  setState((prev: FilterState) => ({
                    ...prev,
                    category: category.value
                  }))
                }
              >
                {category.label}
              </Button>
            </span>
          ))}
        </div>
      </div>
      <AnimatePresence initial={false}>
        <motion.div
          key="filters"
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.24 }}
          className="grid gap-4 pt-4 md:grid-cols-3"
        >
          <label className="flex flex-col text-xs uppercase tracking-widest text-slate-400">
            Occasion
            <select
              className="mt-2 rounded-full border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-200"
              value={state.occasion ?? ""}
              onChange={(event: ChangeEvent<HTMLSelectElement>) =>
                setState((prev: FilterState) => ({
                  ...prev,
                  occasion: event.target.value || null
                }))
              }
            >
              <option value="">Any vibe</option>
              <option value="casual">Casual</option>
              <option value="party">Party</option>
              <option value="formal">Formal</option>
              <option value="wedding">Wedding</option>
              <option value="brunch">Brunch</option>
            </select>
          </label>
          <label className="flex flex-col text-xs uppercase tracking-widest text-slate-400">
            Max Budget (₹)
            <input
              type="range"
              min={1000}
              max={10000}
              step={250}
              value={state.priceRange[1]}
              onChange={(event: ChangeEvent<HTMLInputElement>) =>
                setState((prev: FilterState) => ({
                  ...prev,
                  priceRange: [prev.priceRange[0], Number(event.target.value)]
                }))
              }
            />
            <span className="text-sm text-slate-200">Up to ₹{state.priceRange[1].toLocaleString()}</span>
          </label>
          <div className="flex flex-col gap-2 text-xs uppercase tracking-widest text-slate-400">
            Quick Tags
            <div className="flex flex-wrap gap-2 text-sm normal-case">
              {["minimal", "street", "festive", "power"].map((tag) => (
                <span key={tag}>
                  <Button
                    variant={state.tags.includes(tag) ? "secondary" : "ghost"}
                    onClick={() =>
                      setState((prev: FilterState) => ({
                        ...prev,
                        tags: prev.tags.includes(tag)
                          ? prev.tags.filter((item) => item !== tag)
                          : [...prev.tags, tag]
                      }))
                    }
                  >
                    #{tag}
                  </Button>
                </span>
              ))}
            </div>
          </div>
        </motion.div>
      </AnimatePresence>
    </section>
  );
}
