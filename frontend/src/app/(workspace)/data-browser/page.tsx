import { FeaturePlaceholder } from "@/components/placeholders/feature-placeholder";

export default function DataBrowserPage() {
  return (
    <FeaturePlaceholder
      title="Data Browser"
      summary="Placeholder surface for trace catalogs, metadata summaries, and lineage navigation."
      capabilities={[
        "Master-detail layout reserved for summary rows and detail inspection.",
        "Server-state hooks will land here once API contracts are ready.",
        "Navigation shell is stable for later migration work.",
      ]}
    />
  );
}
