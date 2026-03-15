import { apiRequest, apiRequestEnvelope } from "@/lib/api/client";

import type {
  CircuitDefinitionCatalogMeta,
  CircuitDefinitionCatalogResponse,
  CircuitDefinitionCloneDraft,
  CircuitDefinitionCompatibilityValidationStatus,
  CircuitDefinitionCreateDraft,
  CircuitDefinitionDeleteResponse,
  CircuitDefinitionDetail,
  CircuitDefinitionMutationResponse,
  CircuitDefinitionSummary,
  CircuitDefinitionUpdateDraft,
  DefinitionValidationNotice,
} from "@/features/circuit-definition-editor/lib/contracts";
import { parseCircuitNetlistSource } from "@/features/circuit-definition-editor/lib/netlist";

type CircuitDefinitionAllowedActionsResponse = Readonly<{
  update: boolean;
  delete: boolean;
  publish: boolean;
  clone: boolean;
}>;

type DefinitionValidationNoticeResponse = Readonly<{
  severity: "error" | "warning" | "info";
  code: string;
  message: string;
  source: string;
  blocking: boolean;
}>;

type CircuitDefinitionSummaryResponse = Readonly<{
  definition_id: number;
  name: string;
  created_at: string;
  visibility_scope: "private" | "workspace";
  owner_display_name: string;
  allowed_actions: CircuitDefinitionAllowedActionsResponse;
}>;

type CircuitDefinitionDetailResponse = CircuitDefinitionSummaryResponse &
  Readonly<{
    workspace_id: string;
    lifecycle_state: "active" | "archived" | "deleted";
    owner_user_id: string;
    updated_at: string;
    concurrency_token: string;
    source_hash: string;
    source_text: string;
    normalized_output: string;
    validation_notices: readonly DefinitionValidationNoticeResponse[];
    validation_summary: Readonly<{
      status: "valid" | "warning" | "invalid";
      notice_count: number;
      warning_count: number;
      blocking_notice_count: number;
    }>;
    preview_artifacts: readonly string[];
    lineage_parent_id: number | null;
  }>;

type CircuitDefinitionMutationEnvelope = Readonly<{
  operation: "created" | "updated" | "published" | "cloned";
  definition: CircuitDefinitionDetailResponse;
}>;

type CircuitDefinitionCatalogEnvelope = Readonly<{
  rows: readonly CircuitDefinitionSummaryResponse[];
  total_count: number;
}>;

function toCompatibilityValidationStatus(
  status: "valid" | "warning" | "invalid",
): CircuitDefinitionCompatibilityValidationStatus {
  return status === "valid" ? "ok" : "warning";
}

function mapValidationNotice(
  notice: DefinitionValidationNoticeResponse,
): DefinitionValidationNotice {
  return {
    severity: notice.severity,
    level: notice.severity === "warning" || notice.severity === "error" ? "warning" : "ok",
    code: notice.code,
    message: notice.message,
    source: notice.source,
    blocking: notice.blocking,
  };
}

function inferDefinitionElementCount(sourceText: string) {
  const parsed = parseCircuitNetlistSource(sourceText);
  return parsed.document?.components.length ?? 0;
}

function mapDefinitionSummaryResponse(
  response: CircuitDefinitionSummaryResponse,
): CircuitDefinitionSummary {
  return {
    definition_id: response.definition_id,
    name: response.name,
    created_at: response.created_at,
    visibility_scope: response.visibility_scope,
    owner_display_name: response.owner_display_name,
    allowed_actions: {
      update: response.allowed_actions.update,
      delete: response.allowed_actions.delete,
      publish: response.allowed_actions.publish,
      clone: response.allowed_actions.clone,
    },
    // Compatibility placeholders for older read-only consumers. Detail reads provide real values.
    element_count: 0,
    validation_status: "ok",
    preview_artifact_count: 0,
  };
}

export function mapCircuitDefinitionDetailResponse(
  response: CircuitDefinitionDetailResponse,
): CircuitDefinitionDetail {
  return {
    ...mapDefinitionSummaryResponse(response),
    workspace_id: response.workspace_id,
    lifecycle_state: response.lifecycle_state,
    owner_user_id: response.owner_user_id,
    updated_at: response.updated_at,
    concurrency_token: response.concurrency_token,
    source_hash: response.source_hash,
    source_text: response.source_text,
    normalized_output: response.normalized_output,
    validation_notices: response.validation_notices.map(mapValidationNotice),
    validation_summary: {
      status: response.validation_summary.status,
      notice_count: response.validation_summary.notice_count,
      warning_count: response.validation_summary.warning_count,
      blocking_notice_count: response.validation_summary.blocking_notice_count,
    },
    preview_artifacts: [...response.preview_artifacts],
    lineage_parent_id: response.lineage_parent_id,
    element_count: inferDefinitionElementCount(response.source_text),
    validation_status: toCompatibilityValidationStatus(response.validation_summary.status),
    preview_artifact_count: response.preview_artifacts.length,
  };
}

export const circuitDefinitionsListKey = "/api/backend/circuit-definitions";
export const circuitDefinitionsCatalogKey = `${circuitDefinitionsListKey}?view=authoring-catalog`;

export function circuitDefinitionDetailKey(definitionId: number) {
  return `/api/backend/circuit-definitions/${definitionId}`;
}

export function circuitDefinitionPublishKey(definitionId: number) {
  return `${circuitDefinitionDetailKey(definitionId)}/publish`;
}

export function circuitDefinitionCloneKey(definitionId: number) {
  return `${circuitDefinitionDetailKey(definitionId)}/clone`;
}

export function unwrapCircuitDefinitionMutation(
  response: CircuitDefinitionMutationResponse,
): CircuitDefinitionDetail {
  return response.definition;
}

export async function listCircuitDefinitionsCatalog(): Promise<
  Readonly<{
    catalog: CircuitDefinitionCatalogResponse;
    meta: CircuitDefinitionCatalogMeta | undefined;
  }>
> {
  const response = await apiRequestEnvelope<
    CircuitDefinitionCatalogEnvelope,
    CircuitDefinitionCatalogMeta
  >(circuitDefinitionsListKey);

  return {
    catalog: {
      rows: response.data.rows.map(mapDefinitionSummaryResponse),
      total_count: response.data.total_count,
    },
    meta: response.meta,
  };
}

export async function listCircuitDefinitions(): Promise<readonly CircuitDefinitionSummary[]> {
  const response = await listCircuitDefinitionsCatalog();
  return response.catalog.rows;
}

export async function getCircuitDefinition(definitionId: number) {
  const response = await apiRequest<CircuitDefinitionDetailResponse>(
    circuitDefinitionDetailKey(definitionId),
  );
  return mapCircuitDefinitionDetailResponse(response);
}

export async function createCircuitDefinition(payload: CircuitDefinitionCreateDraft) {
  const response = await apiRequest<CircuitDefinitionMutationEnvelope>(circuitDefinitionsListKey, {
    method: "POST",
    body: payload,
  });

  return unwrapCircuitDefinitionMutation({
    operation: response.operation,
    definition: mapCircuitDefinitionDetailResponse(response.definition),
  });
}

export async function updateCircuitDefinition(
  definitionId: number,
  payload: CircuitDefinitionUpdateDraft,
) {
  const response = await apiRequest<CircuitDefinitionMutationEnvelope>(
    circuitDefinitionDetailKey(definitionId),
    {
      method: "PUT",
      body: payload,
    },
  );

  return unwrapCircuitDefinitionMutation({
    operation: response.operation,
    definition: mapCircuitDefinitionDetailResponse(response.definition),
  });
}

export async function publishCircuitDefinition(definitionId: number) {
  const response = await apiRequest<CircuitDefinitionMutationEnvelope>(
    circuitDefinitionPublishKey(definitionId),
    {
      method: "POST",
    },
  );

  return unwrapCircuitDefinitionMutation({
    operation: response.operation,
    definition: mapCircuitDefinitionDetailResponse(response.definition),
  });
}

export async function cloneCircuitDefinition(
  definitionId: number,
  payload?: CircuitDefinitionCloneDraft,
) {
  const response = await apiRequest<CircuitDefinitionMutationEnvelope>(
    circuitDefinitionCloneKey(definitionId),
    {
      method: "POST",
      body: payload ?? null,
    },
  );

  return unwrapCircuitDefinitionMutation({
    operation: response.operation,
    definition: mapCircuitDefinitionDetailResponse(response.definition),
  });
}

export async function deleteCircuitDefinition(definitionId: number) {
  return apiRequest<CircuitDefinitionDeleteResponse>(circuitDefinitionDetailKey(definitionId), {
    method: "DELETE",
  });
}
