import { FeaturePlaceholder } from "@/components/placeholders/feature-placeholder";

export default function CircuitDefinitionEditorPage() {
  return (
    <FeaturePlaceholder
      title="Circuit Definition Editor"
      summary="Placeholder route for canonical circuit editing, validation, and formatting."
      capabilities={[
        "Future editor logic should stay outside page components.",
        "Route boundary is ready for form state and schema validation.",
        "This page intentionally avoids carrying legacy NiceGUI workflow code.",
      ]}
    />
  );
}
