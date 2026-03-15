export type CircuitDefinitionAllowedActions = Readonly<{
  update: boolean;
  delete: boolean;
  publish: boolean;
  clone: boolean;
}>;

export type CircuitDefinitionVisibilityScope = "private" | "workspace";
export type CircuitDefinitionLifecycleState = "active" | "archived" | "deleted";
export type CircuitDefinitionValidationStatus = "valid" | "warning" | "invalid" | "ok";
export type CircuitDefinitionCompatibilityValidationStatus = "ok" | "warning";

export type DefinitionValidationNotice = Readonly<{
  severity?: "error" | "warning" | "info";
  level?: "ok" | "warning";
  code?: string;
  message: string;
  source?: string;
  blocking?: boolean;
}>;

export type CircuitDefinitionValidationSummary = Readonly<{
  status: CircuitDefinitionValidationStatus;
  notice_count: number;
  warning_count: number;
  blocking_notice_count?: number;
}>;

export type CircuitDefinitionSummary = Readonly<{
  definition_id: number;
  name: string;
  created_at: string;
  visibility_scope?: CircuitDefinitionVisibilityScope;
  owner_display_name?: string;
  allowed_actions?: CircuitDefinitionAllowedActions;
  // Compatibility fields used by existing read-first consumers that still depend on the
  // older summary contract. Catalog/editor surfaces should prefer canonical fields above.
  element_count: number;
  validation_status: CircuitDefinitionCompatibilityValidationStatus;
  preview_artifact_count: number;
}>;

export type CircuitDefinitionDetail = CircuitDefinitionSummary &
  Readonly<{
    workspace_id?: string;
    lifecycle_state?: CircuitDefinitionLifecycleState;
    owner_user_id?: string;
    updated_at?: string;
    concurrency_token?: string;
    source_hash?: string;
    source_text: string;
    normalized_output: string;
    validation_notices: readonly DefinitionValidationNotice[];
    validation_summary: CircuitDefinitionValidationSummary;
    preview_artifacts: readonly string[];
    lineage_parent_id?: number | null;
  }>;

export type CircuitDefinitionCreateDraft = Readonly<{
  name: string;
  source_text: string;
  visibility_scope?: CircuitDefinitionVisibilityScope;
}>;

export type CircuitDefinitionUpdateDraft = Readonly<{
  name?: string;
  source_text: string;
  concurrency_token?: string;
}>;

export type CircuitDefinitionCloneDraft = Readonly<{
  name?: string;
}>;

export type CircuitDefinitionDraft = CircuitDefinitionCreateDraft;

export type CircuitDefinitionMutationOperation =
  | "created"
  | "updated"
  | "published"
  | "cloned";

export type CircuitDefinitionMutationResponse = Readonly<{
  operation: CircuitDefinitionMutationOperation;
  definition: CircuitDefinitionDetail;
}>;

export type CircuitDefinitionDeleteResponse = Readonly<{
  operation: "deleted";
  definition_id: number;
}>;

export type CircuitDefinitionCatalogResponse = Readonly<{
  rows: readonly CircuitDefinitionSummary[];
  total_count: number;
}>;

export type CircuitDefinitionCatalogMeta = Readonly<{
  generated_at?: string;
  limit?: number;
  next_cursor?: string | null;
  prev_cursor?: string | null;
  has_more?: boolean;
  filter_echo?: Readonly<Record<string, unknown>>;
}>;
