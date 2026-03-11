import { FeaturePlaceholder } from "@/components/placeholders/feature-placeholder";

export default function CharacterizationPage() {
  return (
    <FeaturePlaceholder
      title="Characterization"
      summary="Placeholder route for measurement, layout, and simulation characterization workflows."
      capabilities={[
        "Reserved for source-agnostic analysis pipelines.",
        "Future forms should use schema-backed validation inside feature modules.",
        "Current scaffold exists only to anchor information architecture.",
      ]}
    />
  );
}
