import type {
  CircuitDefinitionDetail,
  DefinitionValidationNotice,
} from "@/features/circuit-definition-editor/lib/contracts";

export type PersistedPreviewState = Readonly<{
  label: string;
  detail: string;
  tone: "default" | "warning" | "accent";
}>;

export type ValidationNoticeGroups = Readonly<{
  warnings: readonly DefinitionValidationNotice[];
  checks: readonly DefinitionValidationNotice[];
}>;

export type NormalizedOutputField = Readonly<{
  key: string;
  label: string;
  value: string;
}>;

export type NormalizedOutputPreview = Readonly<{
  formattedOutput: string;
  lineCount: number;
  fieldCount: number;
  fields: readonly NormalizedOutputField[];
  isStructured: boolean;
}>;

type PreviewStateInput = Readonly<{
  selectedDefinitionId: number | "new" | null;
  isDirty: boolean;
  isSaving: boolean;
  activeDefinition: CircuitDefinitionDetail | undefined;
}>;

export function resolvePersistedPreviewState({
  selectedDefinitionId,
  isDirty,
  isSaving,
  activeDefinition,
}: PreviewStateInput): PersistedPreviewState {
  if (isSaving) {
    return {
      label: "Refreshing Preview",
      detail: "Saving the current draft and waiting for backend validation output.",
      tone: "accent",
    };
  }

  if (selectedDefinitionId === "new") {
    return {
      label: "Draft Preview",
      detail: "Save this draft to create a persisted normalized preview and validation report.",
      tone: "default",
    };
  }

  if (isDirty) {
    return {
      label: "Preview Out Of Date",
      detail: "Panels below still show the last persisted definition. Save to refresh them.",
      tone: "warning",
    };
  }

  if (activeDefinition) {
    return {
      label: "Persisted Preview",
      detail: `Backend validation is attached to definition #${activeDefinition.definition_id}.`,
      tone: "accent",
    };
  }

  return {
    label: "Preview Pending",
    detail: "Select or save a definition to inspect its persisted preview state.",
    tone: "default",
  };
}

export function partitionValidationNotices(
  notices: readonly DefinitionValidationNotice[],
): ValidationNoticeGroups {
  return {
    warnings: notices.filter((notice) => notice.level === "warning"),
    checks: notices.filter((notice) => notice.level === "ok"),
  };
}

export function buildNormalizedOutputPreview(
  normalizedOutput: string,
): NormalizedOutputPreview {
  const formattedOutput = normalizedOutput.trim().length > 0 ? normalizedOutput : "{}";
  const lineCount = formattedOutput.split(/\r?\n/).length;

  try {
    const parsed = JSON.parse(formattedOutput) as Record<string, unknown>;
    if (!parsed || Array.isArray(parsed) || typeof parsed !== "object") {
      throw new Error("normalized output is not a JSON object");
    }

    const fields = Object.entries(parsed).map(([key, value]) => ({
      key,
      label: humanizePreviewKey(key),
      value: formatPreviewValue(value),
    }));

    return {
      formattedOutput: JSON.stringify(parsed, null, 2),
      lineCount,
      fieldCount: fields.length,
      fields,
      isStructured: true,
    };
  } catch {
    return {
      formattedOutput,
      lineCount,
      fieldCount: 0,
      fields: [],
      isStructured: false,
    };
  }
}

function formatPreviewValue(value: unknown): string {
  if (Array.isArray(value)) {
    return `${value.length} item${value.length === 1 ? "" : "s"}`;
  }

  if (typeof value === "boolean") {
    return value ? "true" : "false";
  }

  if (value && typeof value === "object") {
    return JSON.stringify(value);
  }

  return String(value);
}

function humanizePreviewKey(key: string): string {
  return key
    .split("_")
    .filter(Boolean)
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(" ");
}
