import { StyleDNAForm } from "@/components/StyleDNAForm";
import { sampleStyleDNA } from "@/data/sampleCatalog";
import { Api } from "@/lib/api";

export default async function StyleDNAOnboarding() {
  // TODO: Replace with server call once authentication is wired
  const profile = sampleStyleDNA;

  async function submitStyleDNA(payload: Parameters<typeof Api.submitStyleDNA>[0]) {
    "use server";
    await Api.submitStyleDNA(payload);
  }

  return (
    <div className="space-y-6">
      <StyleDNAForm initialProfile={profile} onSubmit={submitStyleDNA} />
    </div>
  );
}
