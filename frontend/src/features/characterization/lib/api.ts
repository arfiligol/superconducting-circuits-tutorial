import { apiRequest, apiRequestEnvelope } from "@/lib/api/client";

import type {
  CharacterizationArtifactRef,
  CharacterizationAppliedTag,
  CharacterizationDesignatedMetricOption,
  CharacterizationDiagnostic,
  CharacterizationIdentifySurface,
  CharacterizationPagedRows,
  CharacterizationResultDetail,
  CharacterizationResultStatus,
  CharacterizationResultSummary,
  CharacterizationSourceParameterOption,
  CharacterizationTaggingInput,
  CharacterizationTaggingResult,
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
  identify_surface: Readonly<{
    source_parameters: readonly CharacterizationSourceParameterResponse[];
    designated_metrics: readonly CharacterizationDesignatedMetricOptionResponse[];
    applied_tags: readonly CharacterizationAppliedTagResponse[];
  }>;
}>;

type CharacterizationSourceParameterResponse = Readonly<{
  artifact_id: string;
  source_parameter: string;
  label: string;
  artifact_title: string;
  current_designated_metric: string | null;
}>;

type CharacterizationDesignatedMetricOptionResponse = Readonly<{
  metric_key: string;
  label: string;
}>;

type CharacterizationAppliedTagResponse = Readonly<{
  artifact_id: string;
  source_parameter: string;
  designated_metric: string;
  designated_metric_label: string;
  tagged_at: string;
}>;

type CharacterizationTaggingResultResponse = Readonly<{
  tagging_status: CharacterizationTaggingResult["taggingStatus"];
  dataset_id: string;
  design_id: string;
  result_id: string;
  artifact_id: string;
  source_parameter: string;
  designated_metric: string;
  tagged_metric: Readonly<{
    metric_id: string;
    label: string;
    source_parameter: string;
    designated_metric: string;
    tagged_at: string;
  }>;
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

export function characterizationTaggingsKey(
  datasetId: string,
  designId: string,
  resultId: string,
) {
  return `${characterizationResultDetailKey(datasetId, designId, resultId)}/taggings`;
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

function mapCharacterizationSourceParameterOption(
  payload: CharacterizationSourceParameterResponse,
): CharacterizationSourceParameterOption {
  return {
    artifactId: payload.artifact_id,
    sourceParameter: payload.source_parameter,
    label: payload.label,
    artifactTitle: payload.artifact_title,
    currentDesignatedMetric: payload.current_designated_metric,
  };
}

function mapCharacterizationDesignatedMetricOption(
  payload: CharacterizationDesignatedMetricOptionResponse,
): CharacterizationDesignatedMetricOption {
  return {
    metricKey: payload.metric_key,
    label: payload.label,
  };
}

function mapCharacterizationAppliedTag(
  payload: CharacterizationAppliedTagResponse,
): CharacterizationAppliedTag {
  return {
    artifactId: payload.artifact_id,
    sourceParameter: payload.source_parameter,
    designatedMetric: payload.designated_metric,
    designatedMetricLabel: payload.designated_metric_label,
    taggedAt: payload.tagged_at,
  };
}

function mapCharacterizationIdentifySurface(
  payload: CharacterizationResultDetailResponse["identify_surface"],
): CharacterizationIdentifySurface {
  return {
    sourceParameters: payload.source_parameters.map(mapCharacterizationSourceParameterOption),
    designatedMetrics: payload.designated_metrics.map(
      mapCharacterizationDesignatedMetricOption,
    ),
    appliedTags: payload.applied_tags.map(mapCharacterizationAppliedTag),
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
    identifySurface: mapCharacterizationIdentifySurface(payload.identify_surface),
  };
}

function mapCharacterizationTaggingResult(
  payload: CharacterizationTaggingResultResponse,
): CharacterizationTaggingResult {
  return {
    taggingStatus: payload.tagging_status,
    datasetId: payload.dataset_id,
    designId: payload.design_id,
    resultId: payload.result_id,
    artifactId: payload.artifact_id,
    sourceParameter: payload.source_parameter,
    designatedMetric: payload.designated_metric,
    taggedMetric: {
      metricId: payload.tagged_metric.metric_id,
      label: payload.tagged_metric.label,
      sourceParameter: payload.tagged_metric.source_parameter,
      designatedMetric: payload.tagged_metric.designated_metric,
      taggedAt: payload.tagged_metric.tagged_at,
    },
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

export async function applyCharacterizationTagging(
  datasetId: string,
  designId: string,
  resultId: string,
  payload: CharacterizationTaggingInput,
) {
  const response = await apiRequest<CharacterizationTaggingResultResponse>(
    characterizationTaggingsKey(datasetId, designId, resultId),
    {
      method: "POST",
      body: {
        artifact_id: payload.artifactId,
        source_parameter: payload.sourceParameter,
        designated_metric: payload.designatedMetric,
      },
    },
  );
  return mapCharacterizationTaggingResult(response);
}
