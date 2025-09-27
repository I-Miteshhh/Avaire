import { CatalogItem, Recommendation, StyleDNAProfile, TryOnSession } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchJSON<T>(endpoint: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${endpoint}`, {
    headers: {
      "Content-Type": "application/json"
    },
    cache: "no-store",
    ...init
  });

  if (!res.ok) {
    const message = await res.text();
    throw new Error(`API request failed: ${res.status} ${message}`);
  }

  return res.json();
}

export const Api = {
  catalog(): Promise<{ items: CatalogItem[] }> {
    return fetchJSON("/api/catalog");
  },
  recommendations(userId: number): Promise<{ recommendations: Recommendation[] }> {
    return fetchJSON(`/api/recommend/${userId}`);
  },
  styleDNA(userId: number): Promise<StyleDNAProfile> {
    return fetchJSON(`/api/users/${userId}/style-dna`);
  },
  tryOnHistory(): Promise<{ tryon_history: TryOnSession[] }> {
    return fetchJSON("/api/tryon/history");
  },
  submitStyleDNA(data: Partial<StyleDNAProfile>) {
    return fetchJSON("/api/onboard_style_dna", {
      method: "POST",
      body: JSON.stringify(data)
    });
  }
};
