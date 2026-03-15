import { apiRequest, apiRequestEnvelope } from "@/lib/api/client";

import type {
  CharacterizationArtifactRef,
  CharacterizationDiagnostic,
  CharacterizationPagedRows,
  CharacterizationResultDetail,
  CharacterizationResultStatus,
  CharacterizationResultSummary,
} from "@/features/characterization/lib/contracts";

type CharacterizationResultSummaryResponse = Readonly<{
  result_id: string;
  dataset_id: string;
  design_id: string;
  analysis_id: string;
  title: string;
  status: CharacterizationResultStatus;
  freshness_summary: string;
  provenance_summary: string;
  trace_count: number;
  artifact_count: number;
  updated_at: string;
}>;

type CharacterizationDiagnosticResponse = Readonly<{
  severity: CharacterizationDiagnostic["severity"];
  code: string;
  message: string;
  blocking: boolean;
}>;

type CharacterizationArtifactRefResponse = Readonly<{
  artifact_id: string;
  category: string;
  view_kind: CharacterizationArtifactRef["viewKind"];
  title: string;
  payload_format: CharacterizationArtifactRef["payloadFormat"];
  payload_locator: string | null;
}>;

type CharacterizationResultDetailResponse = Readonly<{
  result_id: string;
  dataset_id: string;
  design_id: string;
  analysis_id: string;
  title: string;
  status: CharacterizationResultStatus;
  freshness_summary: string;
  provenance_summary: string;
  trace_count: number;
  updated_at: string;
  input_trace_ids: readonly string[];
  payload: Readonly<Record<string, unknown>>;
  diagnostics: readonly CharacterizationDiagnosticResponse[];
  artifact_refs: readonly CharacterizationArtifactRefResponse[];
}>;

type CharacterizationCursorMeta = Readonly<{
  generated_at: string;
  limit: number;
  next_cursor: string | null;
  prev_cursor: string | null;
  has_more: boolean;
  filter_echo: Readonly<Record<string, unknown>>;
}>;

type CharacterizationResultsListQuery = Readonly<{
  search?: string | null;
  status?: CharacterizationResultStatus | null;
  analysisId?: string | null;
}>;

export function characterizationResultsListKey(datasetId: string, designId: string) {
  return `/api/backend/datasets/${encodeURIComponent(datasetId)}/designs/${encodeURIComponent(
    designId,
  )}/characterization-results`;
}

export function characterizationResultDetailKey(
  datasetId: string,
  designId: string,
  resultId: string,
) {
  return `${characterizationResultsListKey(datasetId, designId)}/${encodeURIComponent(resultId)}`;
}

function mapCharacterizationResultSummary(
  payload: CharacterizationResultSummaryResponse,
): CharacterizationResultSummary {
  return {
    resultId: payload.result_id,
    datasetId: payload.dataset_id,
    designId: payload.design_id,
    analysisId: payload.analysis_id,
    title: payload.title,
    status: payload.status,
    freshnessSummary: payload.freshness_summary,
    provenanceSummary: payload.provenance_summary,
    traceCount: payload.trace_count,
    artifactCount: payload.artifact_count,
    updatedAt: payload.updated_at,
  };
}

function mapCharacterizationDiagnostic(
  payload: CharacterizationDiagnosticResponse,
): CharacterizationDiagnostic {
  return {
    severity: payload.severity,
    code: payload.code,
    message: payload.message,
    blocking: payload.blocking,
  };
}

function mapCharacterizationArtifactRef(
  payload: CharacterizationArtifactRefResponse,
): CharacterizationArtifactRef {
  return {
    artifactId: payload.artifact_id,
    category: payload.category,
    viewKind: payload.view_kind,
    title: payload.title,
    payloadFormat: payload.payload_format,
    payloadLocator: payload.payload_locator,
  };
}

function mapCharacterizationResultDetail(
  payload: CharacterizationResultDetailResponse,
): CharacterizationResultDetail {
  return {
    resultId: payload.result_id,
    datasetId: payload.dataset_id,
    designId: payload.design_id,
    analysisId: payload.analysis_id,
    title: payload.title,
    status: payload.status,
    freshnessSummary: payload.freshness_summary,
    provenanceSummary: payload.provenance_summary,
    traceCount: payload.trace_count,
    updatedAt: payload.updated_at,
    inputTraceIds: [...payload.input_trace_ids],
    payload: payload.payload,
    diagnostics: payload.diagnostics.map(mapCharacterizationDiagnostic),
    artifactRefs: payload.artifact_refs.map(mapCharacterizationArtifactRef),
  };
}

export async function listCharacterizationResults(
  datasetId: string,
  designId: string,
  query?: CharacterizationResultsListQuery,
): Promise<CharacterizationPagedRows<CharacterizationResultSummary>> {
  const params = new URLSearchParams();
  if (query?.search) {
    params.set("search", query.search);
  }
  if (query?.status) {
    params.set("status", query.status);
  }
  if (query?.analysisId) {
    params.set("analysis_id", query.analysisId);
  }

  const search = params.toString();
  const response = await apiRequestEnvelope<
    { rows: readonly CharacterizationResultSummaryResponse[] },
    CharacterizationCursorMeta
  >(
    search
      ? `${characterizationResultsListKey(datasetId, designId)}?${search}`
      : characterizationResultsListKey(datasetId, designId),
  );

  return {
    rows: response.data.rows.map(mapCharacterizationResultSummary),
    meta: {
      generatedAt: response.meta?.generated_at ?? "",
      limit: response.meta?.limit ?? response.data.rows.length,
      nextCursor: response.meta?.next_cursor ?? null,
      prevCursor: response.meta?.prev_cursor ?? null,
      hasMore: response.meta?.has_more ?? false,
      filterEcho: response.meta?.filter_echo ?? {},
    },
  };
}

export async function getCharacterizationResult(
  datasetId: string,
  designId: string,
  resultId: string,
) {
  const response = await apiRequest<CharacterizationResultDetailResponse>(
    characterizationResultDetailKey(datasetId, designId, resultId),
  );
  return mapCharacterizationResultDetail(response);
}
