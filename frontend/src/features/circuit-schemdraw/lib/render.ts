import { ApiError } from "@/lib/api/client";
import type { CircuitDefinitionDetail } from "@/features/circuit-definition-editor/lib/contracts";
import type {
  SchemdrawDiagnostic,
  SchemdrawLinkedSchemaSnapshot,
  SchemdrawRenderRequest,
  SchemdrawRenderResponse,
} from "@/features/circuit-schemdraw/lib/api";

export type SchemdrawEditorDraft = Readonly<{
  sourceText: string;
  relationText: string;
  documentVersion: number;
}>;

export type SchemdrawRenderPhase =
  | "idle"
  | "stale"
  | "validating"
  | "rendered"
  | "syntax_error"
  | "runtime_error"
  | "request_error";

export type SchemdrawRenderSurface = Readonly<{
  phase: SchemdrawRenderPhase;
  statusLabel: string;
  diagnostics: readonly SchemdrawDiagnostic[];
  svg: string | null;
  previewMetadata: SchemdrawRenderResponse["preview_metadata"] | null;
  requestId: string | null;
  appliedDocumentVersion: number | null;
  isStale: boolean;
}>;

type BuildRequestInput = Readonly<{
  activeDefinition: CircuitDefinitionDetail | undefined;
  draft: SchemdrawEditorDraft;
  renderMode: "debounced" | "manual";
  requestId: string;
}>;

export function createSchemdrawSourceTemplate(definitionName: string | null) {
  const safeName = definitionName ?? "linked_schema";
  return [
    "import schemdraw",
    "import schemdraw.elements as elm",
    "",
    "def build_drawing(relation):",
    `    title = relation.get("title", "${safeName}")`,
    "    drawing = schemdraw.Drawing()",
    "    drawing += elm.SourceSin().label(title)",
    "    drawing += elm.Line().right()",
    "    drawing += elm.Resistor().label(relation.get(\"primary_element\", \"R1\"))",
    "    drawing += elm.Line().right()",
    "    drawing += elm.Capacitor().down().label(relation.get(\"secondary_element\", \"C1\"))",
    "    return drawing",
    "",
  ].join("\n");
}

export function createRelationConfigTemplate(
  definition: CircuitDefinitionDetail | undefined,
) {
  return JSON.stringify(
    {
      title: definition?.name ?? "linked_schema",
      primary_element: definition?.normalized_output ? "Lj1" : "R1",
      secondary_element: "C1",
      labels: {},
    },
    null,
    2,
  );
}

export function ensureSchemdrawDraft(
  currentDraft: SchemdrawEditorDraft | undefined,
  definition: CircuitDefinitionDetail | undefined,
): SchemdrawEditorDraft {
  if (currentDraft) {
    return currentDraft;
  }

  return {
    sourceText: createSchemdrawSourceTemplate(definition?.name ?? null),
    relationText: createRelationConfigTemplate(definition),
    documentVersion: 1,
  };
}

export function updateSchemdrawDraft(
  draft: SchemdrawEditorDraft,
  patch: Readonly<Partial<Pick<SchemdrawEditorDraft, "sourceText" | "relationText">>>,
): SchemdrawEditorDraft {
  return {
    sourceText: patch.sourceText ?? draft.sourceText,
    relationText: patch.relationText ?? draft.relationText,
    documentVersion: draft.documentVersion + 1,
  };
}

export function parseRelationConfigText(relationText: string) {
  try {
    const parsed = JSON.parse(relationText) as unknown;
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      return {
        value: null,
        diagnostics: [
          buildClientDiagnostic(
            "schemdraw_relation_invalid",
            "Relation config must be a JSON object.",
          ),
        ],
      };
    }

    return {
      value: parsed as Record<string, unknown>,
      diagnostics: [] as readonly SchemdrawDiagnostic[],
    };
  } catch {
    return {
      value: null,
      diagnostics: [
        buildClientDiagnostic(
          "schemdraw_relation_invalid",
          "Relation config must be valid JSON before render can proceed.",
        ),
      ],
    };
  }
}

export function buildSchemdrawRenderRequest({
  activeDefinition,
  draft,
  renderMode,
  requestId,
}: BuildRequestInput) {
  const parsedRelation = parseRelationConfigText(draft.relationText);
  if (!parsedRelation.value) {
    return {
      request: null,
      diagnostics: parsedRelation.diagnostics,
    };
  }

  const linkedSchema: SchemdrawLinkedSchemaSnapshot | null = activeDefinition
    ? {
        definition_id: activeDefinition.definition_id,
        name: activeDefinition.name,
      }
    : null;

  const request: SchemdrawRenderRequest = {
    source_text: draft.sourceText,
    relation_config: parsedRelation.value,
    linked_schema: linkedSchema,
    document_version: draft.documentVersion,
    request_id: requestId,
    render_mode: renderMode,
  };

  return {
    request,
    diagnostics: [] as readonly SchemdrawDiagnostic[],
  };
}

export function buildRenderSurfaceFromResponse(
  response: SchemdrawRenderResponse,
  previousSurface: SchemdrawRenderSurface,
): SchemdrawRenderSurface {
  if (response.status === "rendered") {
    return {
      phase: "rendered",
      statusLabel: "Rendered",
      diagnostics: response.diagnostics,
      svg: response.svg ?? previousSurface.svg,
      previewMetadata: response.preview_metadata ?? null,
      requestId: response.request_id,
      appliedDocumentVersion: response.document_version,
      isStale: false,
    };
  }

  return {
    phase: response.status === "runtime_error" ? "runtime_error" : "syntax_error",
    statusLabel: response.status === "runtime_error" ? "Runtime Error" : "Syntax Error",
    diagnostics: response.diagnostics,
    svg: previousSurface.svg,
    previewMetadata: previousSurface.previewMetadata,
    requestId: response.request_id,
    appliedDocumentVersion: previousSurface.appliedDocumentVersion,
    isStale: true,
  };
}

export function buildRenderSurfaceFromError(
  error: Error,
  previousSurface: SchemdrawRenderSurface,
): SchemdrawRenderSurface {
  return {
    phase: "request_error",
    statusLabel: "Render Request Failed",
    diagnostics: [buildDiagnosticFromError(error)],
    svg: previousSurface.svg,
    previewMetadata: previousSurface.previewMetadata,
    requestId: previousSurface.requestId,
    appliedDocumentVersion: previousSurface.appliedDocumentVersion,
    isStale: true,
  };
}

export function markSchemdrawPreviewStale(surface: SchemdrawRenderSurface): SchemdrawRenderSurface {
  return {
    ...surface,
    phase: surface.svg ? "stale" : "idle",
    statusLabel: surface.svg ? "Preview Stale" : "Editing",
    isStale: surface.svg !== null,
  };
}

export function createInitialRenderSurface(): SchemdrawRenderSurface {
  return {
    phase: "idle",
    statusLabel: "Idle",
    diagnostics: [],
    svg: null,
    previewMetadata: null,
    requestId: null,
    appliedDocumentVersion: null,
    isStale: false,
  };
}

export function shouldApplySchemdrawResponse(
  response: SchemdrawRenderResponse,
  latestRequestId: string,
  latestDocumentVersion: number,
) {
  return (
    response.request_id === latestRequestId &&
    response.document_version === latestDocumentVersion
  );
}

function buildClientDiagnostic(code: string, message: string): SchemdrawDiagnostic {
  return {
    severity: "error",
    code,
    message,
    source: "relation_config",
    blocking: true,
  };
}

function buildDiagnosticFromError(error: Error): SchemdrawDiagnostic {
  if (error instanceof ApiError) {
    return {
      severity: "error",
      code: error.errorCode ?? "schemdraw_request_failed",
      message: error.message,
      source: "request",
      blocking: true,
    };
  }

  return {
    severity: "error",
    code: "schemdraw_request_failed",
    message: error.message,
    source: "request",
    blocking: true,
  };
}
