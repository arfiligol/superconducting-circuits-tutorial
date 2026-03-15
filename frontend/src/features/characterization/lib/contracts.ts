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
