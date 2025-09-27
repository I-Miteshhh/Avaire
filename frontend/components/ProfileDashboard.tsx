"use client";

import Image from "next/image";
import { motion } from "framer-motion";
import type { Recommendation, StyleDNAProfile, TryOnSession } from "@/lib/types";

interface ProfileDashboardProps {
  profile: StyleDNAProfile | null;
  recommendations: Recommendation[];
  history: TryOnSession[];
}

export function ProfileDashboard({ profile, recommendations, history }: ProfileDashboardProps) {
  return (
    <section className="grid gap-6 lg:grid-cols-[2fr,1fr]">
      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold">Style blueprint</h2>
            <p className="text-sm text-slate-400">Last synced {new Date().toLocaleDateString()}</p>
          </div>
        </div>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <Card title="Skin tone" value={profile?.skin_tone ?? "—"} />
          <Card title="Body type" value={profile?.body_type ?? "—"} />
          <Card title="Lifestyle" value={profile?.lifestyle ?? "—"} />
          <Card
            title="Vibe tags"
            value={profile?.preferred_styles?.map((tag) => `#${tag}`).join("  ") ?? "Update to unlock"}
          />
        </div>
      </div>
      <div className="space-y-4">
        <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
          <h3 className="text-lg font-semibold">Moodboard picks</h3>
          <div className="mt-4 space-y-3">
            {recommendations.slice(0, 3).map((recommendation) => (
              <motion.div
                key={recommendation.outfit_id}
                className="flex items-center gap-3 rounded-2xl border border-slate-800/80 p-3"
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
              >
                <div className="relative h-12 w-12 overflow-hidden rounded-xl">
                  <Image
                    src={recommendation.outfit.primary_image_url}
                    alt={recommendation.outfit.name}
                    fill
                    className="object-cover"
                  />
                </div>
                <div className="flex-1 text-sm">
                  <p className="font-semibold text-slate-200">{recommendation.outfit.name}</p>
                  <p className="text-xs text-slate-400">{recommendation.reason}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
        <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
          <h3 className="text-lg font-semibold">Recent try-ons</h3>
          <div className="mt-4 space-y-3">
            {history.slice(0, 3).map((session) => (
              <div key={session.session_id} className="flex items-center justify-between text-sm">
                <span className="text-slate-300">Session {session.session_id.split("-").at(-1)}</span>
                <span className="text-slate-500">{new Date(session.created_at).toLocaleDateString()}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function Card({ title, value }: { title: string; value: string }) {
  return (
    <div className="rounded-2xl border border-slate-800/80 bg-slate-950/80 p-4 text-sm text-slate-300">
      <p className="text-xs uppercase tracking-widest text-slate-500">{title}</p>
      <p className="mt-2 text-base font-semibold text-slate-100">{value}</p>
    </div>
  );
}
