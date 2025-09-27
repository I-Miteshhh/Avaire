"use client";

import { useState, type ChangeEvent } from "react";
import Image from "next/image";
import { motion } from "framer-motion";
import type { CatalogItem, TryOnSession } from "@/lib/types";
import { Button } from "@/components/ui/Button";

interface TryOnStudioProps {
  catalog: CatalogItem[];
  history: TryOnSession[];
  onUpload?: (file: File, outfitId: number) => Promise<void> | void;
}

export function TryOnStudio({ catalog, history, onUpload }: TryOnStudioProps) {
  const [selectedOutfit, setSelectedOutfit] = useState<CatalogItem | null>(catalog[0] ?? null);
  const [isProcessing, setProcessing] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);

  async function handleUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file || !selectedOutfit) return;

    setPreview(URL.createObjectURL(file));

    try {
      setProcessing(true);
      await onUpload?.(file, selectedOutfit.id);
    } finally {
      setProcessing(false);
    }
  }

  return (
    <section className="grid gap-6 lg:grid-cols-3">
      <div className="space-y-4 rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
        <header className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold">Try-On Studio</h2>
            <p className="text-sm text-slate-400">Upload a selfie and preview any look instantly.</p>
          </div>
        </header>
        <label className="grid h-48 place-items-center rounded-2xl border border-dashed border-slate-700 bg-slate-900/60 text-center text-sm text-slate-400 transition hover:border-brand/60">
          <input type="file" accept="image/*" className="hidden" onChange={handleUpload} />
          {isProcessing ? "Processing your look..." : "Drop your photo or tap to upload"}
        </label>
        <div className="flex gap-2 overflow-x-auto pb-2">
          {catalog.slice(0, 8).map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => setSelectedOutfit(item)}
              className={`h-20 w-16 flex-shrink-0 overflow-hidden rounded-2xl border transition ${
                selectedOutfit?.id === item.id ? "border-brand" : "border-transparent"
              }`}
            >
              <Image src={item.primary_image_url} alt={item.name} width={64} height={80} className="h-full w-full object-cover" />
            </button>
          ))}
        </div>
      </div>
      <motion.div
        layout
        className="relative aspect-square overflow-hidden rounded-3xl border border-slate-800 bg-slate-900/60"
      >
        {preview ? (
          <Image src={preview} alt="Upload preview" fill className="object-cover" />
        ) : (
          <div className="flex h-full flex-col items-center justify-center text-center text-slate-500">
            <span className="text-sm">Upload a selfie to preview your vibe</span>
          </div>
        )}
        <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-slate-950/80 via-slate-950/20 to-transparent p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-300">{selectedOutfit?.name ?? "Select an outfit"}</p>
              {selectedOutfit && <p className="text-xs text-slate-500">₹{selectedOutfit.price.toLocaleString("en-IN")}</p>}
            </div>
            <Button disabled={isProcessing || !preview}>{isProcessing ? "Processing" : "Generate"}</Button>
          </div>
        </div>
      </motion.div>
      <div className="space-y-4 rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Recent sessions</h3>
          <Button variant="ghost">View all</Button>
        </div>
        <div className="space-y-3">
          {history.map((session) => (
            <div key={session.session_id} className="flex items-center gap-3 rounded-2xl border border-slate-800/80 p-3">
              <div className="relative h-12 w-12 overflow-hidden rounded-xl">
                <Image src={session.result_image_url} alt="Result" fill className="object-cover" />
              </div>
              <div className="flex-1 text-xs text-slate-400">
                <p className="font-semibold text-slate-200">Session {session.session_id.split("-").at(-1)}</p>
                <p>{new Date(session.created_at).toLocaleDateString()}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
