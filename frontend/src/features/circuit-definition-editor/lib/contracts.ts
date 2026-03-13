import { components } from "@/lib/api/generated/schema";

export type DefinitionValidationNotice = components["schemas"]["ValidationNoticeResponse"];

export type CircuitDefinitionValidationSummary =
  components["schemas"]["CircuitDefinitionValidationSummaryResponse"];

export type CircuitDefinitionSummary = components["schemas"]["CircuitDefinitionSummaryResponse"];

export type CircuitDefinitionDetail = components["schemas"]["CircuitDefinitionDetailResponse"];

export type CircuitDefinitionMutationResponse =
  components["schemas"]["CircuitDefinitionMutationResponse"];

export type CircuitDefinitionDraft = components["schemas"]["CircuitDefinitionCreateRequest"];
