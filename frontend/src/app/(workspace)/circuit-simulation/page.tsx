import { FeaturePlaceholder } from "@/components/placeholders/feature-placeholder";

export default function CircuitSimulationPage() {
  return (
    <FeaturePlaceholder
      title="Circuit Simulation"
      summary="Placeholder route for simulation runs, sweep configuration, and result status."
      capabilities={[
        "Prepared for workflow orchestration through typed hooks and services.",
        "Layout supports future control panels and result panes.",
        "Simulation execution remains outside the React page layer.",
      ]}
    />
  );
}
