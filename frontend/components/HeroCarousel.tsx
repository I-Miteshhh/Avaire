"use client";

import Image from "next/image";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { sampleHeroLooks } from "@/data/sampleCatalog";

export default function HeroCarousel() {
  const [activeIndex, setActiveIndex] = useState(0);
  const look = sampleHeroLooks[activeIndex];

  return (
    <section className="grid gap-8 rounded-3xl border border-slate-800 bg-slate-900/50 p-8 shadow-glow md:grid-cols-2">
      <div className="flex flex-col justify-between">
        <div>
          <span className="rounded-full bg-brand/20 px-3 py-1 text-xs font-semibold uppercase tracking-widest text-brand">
            curated for you
          </span>
          <h1 className="mt-6 text-4xl font-bold md:text-5xl">
            {look.title}
          </h1>
          <p className="mt-4 text-slate-300">{look.description}</p>
        </div>
        <div className="mt-6 flex gap-3">
          {sampleHeroLooks.map((item, index) => (
            <button
              key={item.id}
              onClick={() => setActiveIndex(index)}
              className={`h-10 w-10 rounded-full border transition ${
                index === activeIndex ? "border-brand" : "border-transparent opacity-60 hover:opacity-100"
              }`}
              aria-label={`Show look ${item.title}`}
            >
              <span className="sr-only">{item.title}</span>
            </button>
          ))}
        </div>
      </div>
      <div className="relative aspect-square w-full overflow-hidden rounded-2xl">
        <AnimatePresence mode="wait">
          <motion.div
            key={look.id}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.4 }}
            className="absolute inset-0"
          >
            <Image
              src={look.image}
              alt={look.title}
              fill
              className="object-cover"
              sizes="(min-width: 768px) 50vw, 100vw"
            />
          </motion.div>
        </AnimatePresence>
      </div>
    </section>
  );
}
