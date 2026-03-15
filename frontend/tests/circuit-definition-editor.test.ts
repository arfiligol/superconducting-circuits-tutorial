import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import {
  circuitDefinitionDetailKey,
  circuitDefinitionsListKey,
  unwrapCircuitDefinitionMutation,
} from "../src/features/circuit-definition-editor/lib/api";
import {
  filterCircuitDefinitionCatalog,
} from "../src/features/circuit-definition-editor/lib/catalog";
import {
  parseDefinitionIdParam,
  resolveSelectedDefinitionId,
} from "../src/features/circuit-definition-editor/lib/definition-id";
import {
  buildCircuitDefinitionCatalogHref,
  buildCircuitDefinitionEditorHref,
} from "../src/features/circuit-definition-editor/lib/routes";
import {
  buildCircuitDefinitionDraft,
  formatCircuitNetlistSource,
  summarizeCircuitNetlistDocument,
} from "../src/features/circuit-definition-editor/lib/netlist";
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

  it("filters and sorts the catalog for the dedicated schemas page", () => {
    expect(
      filterCircuitDefinitionCatalog(definitions, "flux", "name").map(
        (definition) => definition.definition_id,
      ),
    ).toEqual([12]);
  });

  it("routes new and existing catalog selections into the editor page", () => {
    expect(buildCircuitDefinitionCatalogHref()).toBe("/schemas");
    expect(buildCircuitDefinitionEditorHref("new")).toBe(
      "/circuit-definition-editor?definitionId=new",
    );
    expect(buildCircuitDefinitionEditorHref(18)).toBe(
      "/circuit-definition-editor?definitionId=18",
    );
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
  it("formats canonical netlist source and builds a save payload from it", () => {
    const formatted = formatCircuitNetlistSource(`{
      "name": "Scratch",
      "components": [
        {"name": "R1", "default": 50, "unit": "Ohm"},
        {"name": "C1", "value_ref": "Cj", "unit": "fF"}
      ],
      "parameters": [
        {"name": "Cj", "default": 100, "unit": "fF"}
      ],
      "topology": [
        ["P1", "1", "0", 1],
        ["R1", "1", "0", "R1"],
        ["C1", "1", "2", "C1"]
      ]
    }`);

    expect(formatted.diagnostics).toEqual([]);
    expect(summarizeCircuitNetlistDocument(formatted.document)).toEqual({
      componentCount: 2,
      topologyCount: 3,
      parameterCount: 1,
    });
    expect(
      buildCircuitDefinitionDraft({
        name: "RenamedCircuit",
        sourceText: formatted.formattedSource,
      }),
    ).toMatchObject({
      formattedSource: expect.stringContaining('"name": "RenamedCircuit"'),
      draft: {
        name: "RenamedCircuit",
      },
    });
  });

  it("reports blocking diagnostics for invalid netlist contracts", () => {
    expect(
      buildCircuitDefinitionDraft({
        name: "Invalid",
        sourceText: `{
          "name": "Invalid",
          "components": [
            {"name": "C1", "unit": "fF", "value_ref": "Missing"}
          ],
          "topology": [
            ["C1", "node-a", "0", "missing_component"]
          ]
        }`,
      }).diagnostics.map((diagnostic) => diagnostic.message),
    ).toEqual([
      'Component "C1" references undefined parameter "Missing".',
      'Topology row "C1" must use numeric string node tokens and ground token "0".',
      'Topology row "C1" must reference an existing component name.',
    ]);
  });

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

  it("keeps explicit format separate from persisted preview authority", () => {
    const formatted = formatCircuitNetlistSource(`{
      "name": "FloatingQubitWithXYLine",
      "components": [
        {"name": "R1", "default": 50, "unit": "Ohm"}
      ],
      "topology": [
        ["P1", "1", "0", 1],
        ["R1", "1", "0", "R1"]
      ]
    }`);

    expect(formatted.diagnostics).toEqual([]);
    expect(
      resolvePersistedPreviewState({
        selectedDefinitionId: 18,
        isDirty: true,
        isSaving: false,
        activeDefinition: {
          definition_id: 18,
          name: "FloatingQubitWithXYLine",
          created_at: "2026-03-08 18:19:42",
          element_count: 2,
          validation_status: "ok",
          preview_artifact_count: 1,
          source_text: '{\n  "name": "FloatingQubitWithXYLine"\n}',
          normalized_output: "{\n  \"circuit\": \"floating_xy\"\n}",
          validation_notices: [],
          validation_summary: {
            status: "ok",
            notice_count: 0,
            warning_count: 0,
          },
          preview_artifacts: ["definition.normalized.json"],
        },
      }),
    ).toMatchObject({
      label: "Preview Out Of Date",
      detail: "Panels below still show the last persisted definition. Save to refresh them.",
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

describe("circuit definition workspace boundaries", () => {
  const catalogWorkspaceSource = readFileSync(
    new URL(
      "../src/features/circuit-definition-editor/components/circuit-definition-catalog-workspace.tsx",
      import.meta.url,
    ),
    "utf8",
  );
  const editorWorkspaceSource = readFileSync(
    new URL(
      "../src/features/circuit-definition-editor/components/circuit-definition-editor-workspace.tsx",
      import.meta.url,
    ),
    "utf8",
  );
  const schemasPageSource = readFileSync(
    new URL("../src/app/(workspace)/schemas/page.tsx", import.meta.url),
    "utf8",
  );
  const editorPageSource = readFileSync(
    new URL("../src/app/(workspace)/circuit-definition-editor/page.tsx", import.meta.url),
    "utf8",
  );

  it("keeps the schemas route mounted on the catalog workspace only", () => {
    expect(schemasPageSource).toContain("CircuitDefinitionCatalogWorkspace");
    expect(schemasPageSource).not.toContain("CircuitDefinitionEditorWorkspace");
    expect(catalogWorkspaceSource).toContain("New Circuit");
    expect(catalogWorkspaceSource).toContain("Open Editor");
    expect(catalogWorkspaceSource).not.toContain("CodeMirror");
    expect(catalogWorkspaceSource).not.toContain("Validation & Preview");
    expect(catalogWorkspaceSource).not.toContain("Open Schemdraw");
  });

  it("keeps the editor route responsible for source editing and persisted preview", () => {
    expect(editorPageSource).toContain("CircuitDefinitionEditorWorkspace");
    expect(editorPageSource).not.toContain("CircuitDefinitionCatalogWorkspace");
    expect(editorWorkspaceSource).toContain("Format");
    expect(editorWorkspaceSource).toContain("Save");
    expect(editorWorkspaceSource).toContain("Discard");
    expect(editorWorkspaceSource).toContain("Validation & Preview");
    expect(editorWorkspaceSource).toContain("does not save");
  });
});
