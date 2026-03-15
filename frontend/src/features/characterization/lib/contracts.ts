import type { DesignBrowseRow } from "@/lib/api/datasets";

export type CharacterizationResultStatus = "completed" | "failed" | "blocked";

export type CharacterizationResultSummary = Readonly<{
  resultId: string;
  datasetId: string;
  designId: string;
  analysisId: string;
  title: string;
  status: CharacterizationResultStatus;
  freshnessSummary: string;
  provenanceSummary: string;
  traceCount: number;
  artifactCount: number;
  updatedAt: string;
}>;

export type CharacterizationDiagnostic = Readonly<{
  severity: "error" | "warning" | "info";
  code: string;
  message: string;
  blocking: boolean;
}>;

export type CharacterizationArtifactRef = Readonly<{
  artifactId: string;
  category: string;
  viewKind: "table" | "plot" | "text" | "json";
  title: string;
  payloadFormat: "json" | "markdown" | "svg" | "csv";
  payloadLocator: string | null;
}>;

export type CharacterizationResultDetail = Readonly<{
  resultId: string;
  datasetId: string;
  designId: string;
  analysisId: string;
  title: string;
  status: CharacterizationResultStatus;
  freshnessSummary: string;
  provenanceSummary: string;
  traceCount: number;
  updatedAt: string;
  inputTraceIds: readonly string[];
  payload: Readonly<Record<string, unknown>>;
  diagnostics: readonly CharacterizationDiagnostic[];
  artifactRefs: readonly CharacterizationArtifactRef[];
  identifySurface: CharacterizationIdentifySurface;
}>;

export type CharacterizationSourceParameterOption = Readonly<{
  artifactId: string;
  sourceParameter: string;
  label: string;
  artifactTitle: string;
  currentDesignatedMetric: string | null;
}>;

export type CharacterizationDesignatedMetricOption = Readonly<{
  metricKey: string;
  label: string;
}>;

export type CharacterizationAppliedTag = Readonly<{
  artifactId: string;
  sourceParameter: string;
  designatedMetric: string;
  designatedMetricLabel: string;
  taggedAt: string;
}>;

export type CharacterizationIdentifySurface = Readonly<{
  sourceParameters: readonly CharacterizationSourceParameterOption[];
  designatedMetrics: readonly CharacterizationDesignatedMetricOption[];
  appliedTags: readonly CharacterizationAppliedTag[];
}>;

export type CharacterizationTaggingInput = Readonly<{
  artifactId: string;
  sourceParameter: string;
  designatedMetric: string;
}>;

export type CharacterizationTaggingResult = Readonly<{
  taggingStatus: "applied" | "already_applied";
  datasetId: string;
  designId: string;
  resultId: string;
  artifactId: string;
  sourceParameter: string;
  designatedMetric: string;
  taggedMetric: Readonly<{
    metricId: string;
    label: string;
    sourceParameter: string;
    designatedMetric: string;
    taggedAt: string;
  }>;
}>;

export type CharacterizationPagedRows<T> = Readonly<{
  rows: readonly T[];
  meta: Readonly<{
    generatedAt: string;
    limit: number;
    nextCursor: string | null;
    prevCursor: string | null;
    hasMore: boolean;
    filterEcho: Readonly<Record<string, unknown>>;
  }>;
}>;

export type CharacterizationDesignBrowseRow = DesignBrowseRow;
