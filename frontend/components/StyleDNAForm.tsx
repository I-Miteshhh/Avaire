"use client";

import { useState, type ChangeEvent } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/Button";
import type { StyleDNAProfile } from "@/lib/types";

interface StyleDNAFormProps {
  initialProfile?: StyleDNAProfile | null;
  onSubmit?: (payload: Partial<StyleDNAProfile>) => Promise<void> | void;
}

type StepKey = "vibe" | "fit" | "budget";

const steps: StepKey[] = ["vibe", "fit", "budget"];

export function StyleDNAForm({ initialProfile, onSubmit }: StyleDNAFormProps) {
  const [currentStep, setCurrentStep] = useState<StepKey>("vibe");
  const [form, setForm] = useState<Partial<StyleDNAProfile>>({
    preferred_colors: initialProfile?.preferred_colors ?? [],
    preferred_styles: initialProfile?.preferred_styles ?? [],
    preferred_occasions: initialProfile?.preferred_occasions ?? [],
    lifestyle: initialProfile?.lifestyle ?? "student",
    age_group: initialProfile?.age_group ?? "23-27"
  });
  const [isSubmitting, setSubmitting] = useState(false);

  async function handleSubmit() {
    try {
      setSubmitting(true);
      await onSubmit?.(form);
    } finally {
      setSubmitting(false);
    }
  }

  const stepIndex = steps.indexOf(currentStep);
  const progress = ((stepIndex + 1) / steps.length) * 100;

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-8">
      <header className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Tune your Style DNA</h2>
          <p className="text-sm text-slate-400">Tell us your vibe and we’ll personalise the drop.</p>
        </div>
        <span className="text-sm text-slate-400">{Math.round(progress)}% synced</span>
      </header>
      <div className="mt-6 h-2 w-full overflow-hidden rounded-full bg-slate-800">
        <div className="h-full rounded-full bg-brand" style={{ width: `${progress}%` }} />
      </div>

      <motion.div
        key={currentStep}
        initial={{ opacity: 0, x: 12 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.25 }}
        className="mt-8 grid gap-6 md:grid-cols-2"
      >
        {currentStep === "vibe" && (
          <VibeStep
            form={form}
            onChange={(update) => setForm((prev: Partial<StyleDNAProfile>) => ({ ...prev, ...update }))}
            onContinue={() => setCurrentStep("fit")}
          />
        )}
        {currentStep === "fit" && (
          <FitStep
            form={form}
            onChange={(update) => setForm((prev: Partial<StyleDNAProfile>) => ({ ...prev, ...update }))}
            onContinue={() => setCurrentStep("budget")}
            onBack={() => setCurrentStep("vibe")}
          />
        )}
        {currentStep === "budget" && (
          <BudgetStep
            form={form}
            onChange={(update) => setForm((prev: Partial<StyleDNAProfile>) => ({ ...prev, ...update }))}
            onBack={() => setCurrentStep("fit")}
            onSubmit={handleSubmit}
            isSubmitting={isSubmitting}
          />
        )}
      </motion.div>
    </div>
  );
}

interface StepProps {
  form: Partial<StyleDNAProfile>;
  onChange: (next: Partial<StyleDNAProfile>) => void;
}

function VibeStep({ form, onChange, onContinue }: StepProps & { onContinue: () => void }) {
  const vibes = ["minimal", "street", "festive", "power", "boho"] as const;
  const occasions = ["casual", "party", "date_night", "wedding", "brunch"] as const;

  function toggle(key: "preferred_styles" | "preferred_occasions", value: string) {
    onChange({
      [key]: form[key]?.includes(value)
        ? form[key]?.filter((item) => item !== value)
        : [...(form[key] ?? []), value]
    });
  }

  return (
    <div className="space-y-6">
      <section>
        <h3 className="text-lg font-semibold">Select your go-to aesthetics</h3>
        <div className="mt-4 flex flex-wrap gap-2">
          {vibes.map((vibe) => (
            <button
              key={vibe}
              type="button"
              onClick={() => toggle("preferred_styles", vibe)}
              className={`rounded-full px-4 py-2 text-sm transition ${
                form.preferred_styles?.includes(vibe)
                  ? "bg-brand text-white"
                  : "bg-slate-800 text-slate-200 hover:bg-slate-800/70"
              }`}
            >
              #{vibe}
            </button>
          ))}
        </div>
      </section>
      <section>
        <h3 className="text-lg font-semibold">Occasions you’re shopping for</h3>
        <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
          {occasions.map((occasion) => (
            <label
              key={occasion}
              className={`flex items-center justify-between rounded-2xl border px-3 py-2 capitalize transition ${
                form.preferred_occasions?.includes(occasion)
                  ? "border-brand/50 bg-brand/20"
                  : "border-slate-800 hover:border-slate-700"
              }`}
            >
              <span>{occasion.replace("_", " ")}</span>
              <input
                type="checkbox"
                checked={form.preferred_occasions?.includes(occasion) ?? false}
                onChange={() => toggle("preferred_occasions", occasion)}
                className="accent-brand"
              />
            </label>
          ))}
        </div>
      </section>
      <Button onClick={onContinue}>Next</Button>
    </div>
  );
}

function FitStep({ form, onChange, onContinue, onBack }: StepProps & { onContinue: () => void; onBack: () => void }) {
  const heights = ["155", "160", "165", "170"];
  const sizes = ["XS", "S", "M", "L", "XL", "XXL"];

  return (
    <div className="space-y-6">
      <section>
        <h3 className="text-lg font-semibold">Select your size preferences</h3>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          <label className="space-y-2 text-sm">
            Bust Size
            <select
              value={form.bust_size ?? "M"}
              onChange={(event: ChangeEvent<HTMLSelectElement>) =>
                onChange({ bust_size: event.target.value })
              }
              className="w-full rounded-2xl border border-slate-800 bg-slate-950 px-3 py-2"
            >
              {sizes.map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
          </label>
          <label className="space-y-2 text-sm">
            Waist Size
            <select
              value={form.waist_size ?? "M"}
              onChange={(event: ChangeEvent<HTMLSelectElement>) =>
                onChange({ waist_size: event.target.value })
              }
              className="w-full rounded-2xl border border-slate-800 bg-slate-950 px-3 py-2"
            >
              {sizes.map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
          </label>
          <label className="space-y-2 text-sm">
            Hip Size
            <select
              value={form.hip_size ?? "M"}
              onChange={(event: ChangeEvent<HTMLSelectElement>) =>
                onChange({ hip_size: event.target.value })
              }
              className="w-full rounded-2xl border border-slate-800 bg-slate-950 px-3 py-2"
            >
              {sizes.map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
          </label>
        </div>
      </section>
      <section className="grid gap-4 md:grid-cols-2">
        <label className="space-y-2 text-sm">
          Height (cm)
          <input
            type="number"
            defaultValue={form.height_cm ?? heights[1]}
            onChange={(event: ChangeEvent<HTMLInputElement>) =>
              onChange({ height_cm: Number(event.target.value) })
            }
            className="w-full rounded-2xl border border-slate-800 bg-slate-950 px-3 py-2"
          />
        </label>
        <label className="space-y-2 text-sm">
          Weight (kg)
          <input
            type="number"
            defaultValue={form.weight_kg ?? 58}
            onChange={(event: ChangeEvent<HTMLInputElement>) =>
              onChange({ weight_kg: Number(event.target.value) })
            }
            className="w-full rounded-2xl border border-slate-800 bg-slate-950 px-3 py-2"
          />
        </label>
      </section>
      <div className="flex gap-3">
        <Button variant="ghost" onClick={onBack}>
          Back
        </Button>
        <Button onClick={onContinue}>Next</Button>
      </div>
    </div>
  );
}

function BudgetStep({
  form,
  onChange,
  onBack,
  onSubmit,
  isSubmitting
}: StepProps & { onBack: () => void; onSubmit: () => Promise<void>; isSubmitting: boolean }) {
  const budget = form.budget_range ?? { min: 2500, max: 5500 };
  const min = budget.min;
  const max = budget.max;

  return (
    <div className="space-y-6">
      <section className="space-y-2">
        <h3 className="text-lg font-semibold">What’s your splurge window?</h3>
        <p className="text-sm text-slate-400">We’ll only suggest looks within your sweet spot.</p>
        <div className="flex gap-3">
          <label className="flex flex-1 flex-col text-sm">
            Min (₹)
            <input
              type="number"
              defaultValue={min ?? 2500}
              onChange={(event: ChangeEvent<HTMLInputElement>) =>
                onChange({ budget_range: { min: Number(event.target.value), max: max ?? 5500 } })
              }
              className="rounded-2xl border border-slate-800 bg-slate-950 px-3 py-2"
            />
          </label>
          <label className="flex flex-1 flex-col text-sm">
            Max (₹)
            <input
              type="number"
              defaultValue={max ?? 5500}
              onChange={(event: ChangeEvent<HTMLInputElement>) =>
                onChange({ budget_range: { min: min ?? 2500, max: Number(event.target.value) } })
              }
              className="rounded-2xl border border-slate-800 bg-slate-950 px-3 py-2"
            />
          </label>
        </div>
      </section>
      <div className="flex gap-3">
        <Button variant="ghost" onClick={onBack}>
          Back
        </Button>
        <Button onClick={onSubmit} disabled={isSubmitting}>
          {isSubmitting ? "Saving" : "Save my DNA"}
        </Button>
      </div>
    </div>
  );
}
