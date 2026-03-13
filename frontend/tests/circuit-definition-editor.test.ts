import { describe, expect, it } from "vitest";

import {
  circuitDefinitionDetailKey,
  circuitDefinitionsListKey,
  unwrapCircuitDefinitionMutation,
} from "../src/features/circuit-definition-editor/lib/api";
import {
  parseDefinitionIdParam,
  resolveSelectedDefinitionId,
} from "../src/features/circuit-definition-editor/lib/definition-id";
import {
  buildNormalizedOutputPreview,
  partitionValidationNotices,
  resolvePersistedPreviewState,
} from "../src/features/circuit-definition-editor/lib/preview";

describe("circuit definition editor routing helpers", () => {
  const definitions = [
    {
      definition_id: 18,
      name: "FloatingQubitWithXYLine",
      created_at: "2026-03-08 18:19:42",
      element_count: 12,
      validation_status: "warning",
      preview_artifact_count: 3,
    },
    {
      definition_id: 12,
      name: "FluxoniumReadoutChain",
      created_at: "2026-03-05 11:14:03",
      element_count: 9,
      validation_status: "ok",
      preview_artifact_count: 2,
    },
  ] as const;

  it("parses numeric and new definition query params", () => {
    expect(parseDefinitionIdParam("18")).toBe(18);
    expect(parseDefinitionIdParam("new")).toBe("new");
    expect(parseDefinitionIdParam("bad")).toBeNull();
    expect(parseDefinitionIdParam(null)).toBeNull();
  });

  it("falls back to the first definition when the selection is missing or invalid", () => {
    expect(resolveSelectedDefinitionId(null, definitions)).toBe("18");
    expect(resolveSelectedDefinitionId("999", definitions)).toBe("18");
  });

  it("preserves explicit new-draft selection", () => {
    expect(resolveSelectedDefinitionId("new", definitions)).toBe("new");
  });
});

describe("circuit definition editor api keys", () => {
  it("keeps stable list and detail paths", () => {
    expect(circuitDefinitionsListKey).toBe("/api/backend/circuit-definitions");
    expect(circuitDefinitionDetailKey(18)).toBe("/api/backend/circuit-definitions/18");
  });

  it("unwraps mutation responses into detail payloads", () => {
    expect(
      unwrapCircuitDefinitionMutation({
        operation: "updated",
        definition: {
          definition_id: 18,
          name: "FloatingQubitWithXYLine",
          created_at: "2026-03-08 18:19:42",
          element_count: 12,
          validation_status: "warning",
          preview_artifact_count: 3,
          source_text: "circuit:\n  name: floating_xy\n",
          normalized_output: "{\n  \"circuit\": \"floating_xy\"\n}",
          validation_notices: [
            {
              level: "warning",
              message: "Port mapping metadata still needs migration from legacy forms.",
            },
          ],
          validation_summary: {
            status: "warning",
            notice_count: 1,
            warning_count: 1,
          },
          preview_artifacts: ["definition.normalized.json"],
        },
      }),
    ).toMatchObject({
      definition_id: 18,
      validation_status: "warning",
      preview_artifact_count: 3,
    });
  });
});

describe("circuit definition preview helpers", () => {
  it("describes stale and persisted preview states distinctly", () => {
    expect(
      resolvePersistedPreviewState({
        selectedDefinitionId: "new",
        isDirty: true,
        isSaving: false,
        activeDefinition: undefined,
      }),
    ).toEqual({
      label: "Draft Preview",
      detail: "Save this draft to create a persisted normalized preview and validation report.",
      tone: "default",
    });

    expect(
      resolvePersistedPreviewState({
        selectedDefinitionId: 18,
        isDirty: true,
        isSaving: false,
        activeDefinition: {
          definition_id: 18,
          name: "FloatingQubitWithXYLine",
          created_at: "2026-03-08 18:19:42",
          element_count: 12,
          validation_status: "warning",
          preview_artifact_count: 3,
          source_text: "circuit:\n  name: floating_xy\n",
          normalized_output: "{\n  \"circuit\": \"floating_xy\"\n}",
          validation_notices: [],
          validation_summary: {
            status: "warning",
            notice_count: 0,
            warning_count: 0,
          },
          preview_artifacts: [],
        },
      }),
    ).toMatchObject({
      label: "Preview Out Of Date",
      tone: "warning",
    });
  });

  it("partitions validation notices and extracts structured normalized output fields", () => {
    expect(
      partitionValidationNotices([
        { level: "ok", message: "All required element blocks are present." },
        { level: "warning", message: "Ports still need migration." },
      ]),
    ).toEqual({
      warnings: [{ level: "warning", message: "Ports still need migration." }],
      checks: [{ level: "ok", message: "All required element blocks are present." }],
    });

    expect(
      buildNormalizedOutputPreview(
        '{\n  "circuit": "fluxonium_reference_a",\n  "family": "fluxonium",\n  "elements": 12,\n  "schemdraw_ready": true\n}',
      ),
    ).toEqual({
      formattedOutput:
        '{\n  "circuit": "fluxonium_reference_a",\n  "family": "fluxonium",\n  "elements": 12,\n  "schemdraw_ready": true\n}',
      lineCount: 6,
      fieldCount: 4,
      isStructured: true,
      fields: [
        { key: "circuit", label: "Circuit", value: "fluxonium_reference_a" },
        { key: "family", label: "Family", value: "fluxonium" },
        { key: "elements", label: "Elements", value: "12" },
        { key: "schemdraw_ready", label: "Schemdraw Ready", value: "true" },
      ],
    });
  });
});
