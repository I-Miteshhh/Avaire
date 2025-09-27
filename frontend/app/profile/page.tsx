import { ProfileDashboard } from "@/components/ProfileDashboard";
import { sampleStyleDNA, sampleRecommendations, sampleTryOnHistory } from "@/data/sampleCatalog";

export default function ProfilePage() {
  return (
    <div className="space-y-6">
      <ProfileDashboard
        profile={sampleStyleDNA}
        recommendations={sampleRecommendations}
        history={sampleTryOnHistory}
      />
    </div>
  );
}
