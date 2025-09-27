import { TryOnStudio } from "@/components/TryOnStudio";
import { sampleCatalog, sampleTryOnHistory } from "@/data/sampleCatalog";

export default function TryOnPage() {
  return (
    <div className="space-y-6">
      <TryOnStudio catalog={sampleCatalog} history={sampleTryOnHistory} />
    </div>
  );
}
