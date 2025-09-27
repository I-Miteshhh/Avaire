"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { CatalogItem, Recommendation, StyleDNAProfile, TryOnSession } from "@/lib/types";

interface AppContextValue {
  catalog: CatalogItem[];
  setCatalog: (items: CatalogItem[]) => void;
  recommendations: Recommendation[];
  setRecommendations: (items: Recommendation[]) => void;
  styleDNA: StyleDNAProfile | null;
  setStyleDNA: (profile: StyleDNAProfile | null) => void;
  tryOnHistory: TryOnSession[];
  setTryOnHistory: (history: TryOnSession[]) => void;
  isHydrated: boolean;
}

const AppContext = createContext<AppContextValue | undefined>(undefined);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [catalog, setCatalog] = useState<CatalogItem[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [styleDNA, setStyleDNA] = useState<StyleDNAProfile | null>(null);
  const [tryOnHistory, setTryOnHistory] = useState<TryOnSession[]>([]);
  const [isHydrated, setHydrated] = useState(false);

  const value = useMemo<AppContextValue>(
    () => ({
      catalog,
      setCatalog,
      recommendations,
      setRecommendations,
      styleDNA,
      setStyleDNA,
      tryOnHistory,
      setTryOnHistory,
      isHydrated
    }),
    [catalog, recommendations, styleDNA, tryOnHistory, isHydrated]
  );

  return (
    <AppContext.Provider value={value}>
      <Hydrator onHydrated={() => setHydrated(true)}>{children}</Hydrator>
    </AppContext.Provider>
  );
}

export function useAppContext() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error("useAppContext must be used within an AppProvider");
  }
  return context;
}

function Hydrator({ children, onHydrated }: { children: React.ReactNode; onHydrated: () => void }) {
  useEffect(() => {
    onHydrated();
  }, [onHydrated]);

  return <>{children}</>;
}
