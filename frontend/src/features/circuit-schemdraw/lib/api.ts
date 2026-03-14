import { apiRequest } from "@/lib/api/client";

export type SchemdrawDiagnostic = Readonly<{
  severity: "error" | "warning" | "info";
  code: string;
  message: string;
  source: "request" | "relation_config" | "python_syntax" | "render_runtime";
  blocking: boolean;
  line?: number | null;
  column?: number | null;
}>;

export type SchemdrawPreviewMetadata = Readonly<{
  width?: number | null;
  height?: number | null;
  view_box?: string | null;
}>;

export type SchemdrawLinkedSchemaSnapshot = Readonly<{
  definition_id: number;
  workspace_id?: string | null;
  name: string;
  source_hash?: string | null;
}>;

export type SchemdrawRenderRequest = Readonly<{
  source_text: string;
  relation_config: Record<string, unknown>;
  linked_schema?: SchemdrawLinkedSchemaSnapshot | null;
  document_version: number;
  request_id: string;
  render_mode?: "debounced" | "manual";
}>;

export type SchemdrawRenderResponse = Readonly<{
  request_id: string;
  document_version: number;
  status: "rendered" | "blocked" | "syntax_error" | "runtime_error";
  svg: string | null;
  diagnostics: readonly SchemdrawDiagnostic[];
  cursor_position?: Record<string, unknown> | null;
  probe_points?: readonly Record<string, unknown>[];
  render_time_ms?: number | null;
  preview_metadata?: SchemdrawPreviewMetadata | null;
}>;

type SchemdrawRenderEnvelope = Readonly<{
  ok: boolean;
  data?: SchemdrawRenderResponse;
}>;

export const schemdrawRenderEndpoint = "/api/backend/schemdraw/render";

export async function renderSchemdrawPreview(request: SchemdrawRenderRequest) {
  const response = await apiRequest<SchemdrawRenderEnvelope>(schemdrawRenderEndpoint, {
    method: "POST",
    body: request,
  });

  if (!response.ok || !response.data) {
    throw new Error("Schemdraw render response did not include a data payload.");
  }

  return response.data;
}
