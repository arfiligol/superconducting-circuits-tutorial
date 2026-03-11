export type DefinitionValidationNotice = Readonly<{
  level: "ok" | "warning";
  message: string;
}>;

export type CircuitDefinitionSummary = Readonly<{
  definition_id: number;
  name: string;
  created_at: string;
  element_count: number;
}>;

export type CircuitDefinitionDetail = CircuitDefinitionSummary &
  Readonly<{
    source_text: string;
    normalized_output: string;
    validation_notices: readonly DefinitionValidationNotice[];
    preview_artifacts: readonly string[];
  }>;

export type CircuitDefinitionDraft = Readonly<{
  name: string;
  source_text: string;
}>;
