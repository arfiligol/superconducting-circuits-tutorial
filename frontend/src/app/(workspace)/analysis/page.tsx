import { FeaturePlaceholder } from "@/components/placeholders/feature-placeholder";

export default function AnalysisPage() {
  return (
    <FeaturePlaceholder
      title="Analysis"
      summary="Placeholder route for fitting, comparisons, and downstream post-processing."
      capabilities={[
        "Prepared for result summaries, charts, and parameter extraction flows.",
        "App-level providers are already wired for theme and cache configuration.",
        "Migration can now proceed feature by feature without reshaping routes.",
      ]}
    />
  );
}
