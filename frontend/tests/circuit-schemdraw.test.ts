import { describe, expect, it } from "vitest";

import {
  parseSchemdrawDefinitionIdParam,
  resolveSchemdrawDefinitionId,
} from "../src/features/circuit-schemdraw/lib/definition-id";
import { inferSchemdrawReadiness } from "../src/features/circuit-schemdraw/lib/readiness";
import {
  buildSchemdrawStructuredPreview,
  filterAndSortSchemdrawCatalog,
  partitionSchemdrawNotices,
  pinActiveSchemdrawDefinition,
  resolveSchemdrawAttachmentState,
  resolveSchemdrawSelectionRecovery,
  summarizeSchemdrawCatalog,
} from "../src/features/circuit-schemdraw/lib/workflow";

describe("circuit schemdraw routing helpers", () => {
  const definitions = [
    {
      definition_id: 18,
      name: "FloatingQubitWithXYLine",
      created_at: "2026-03-08 18:19:42",
      element_count: 12,
      validation_status: "warning",
      preview_artifact_count: 2,
    },
    {
      definition_id: 12,
      name: "FluxoniumReadoutChain",
      created_at: "2026-03-05 11:14:03",
      element_count: 9,
      validation_status: "warning",
      preview_artifact_count: 1,
    },
  ] as const;

  it("parses numeric ids and rejects draft-only values for schemdraw", () => {
    expect(parseSchemdrawDefinitionIdParam("18")).toBe(18);
    expect(parseSchemdrawDefinitionIdParam("new")).toBeNull();
    expect(parseSchemdrawDefinitionIdParam("bad")).toBeNull();
    expect(parseSchemdrawDefinitionIdParam(null)).toBeNull();
  });

  it("falls back to the first definition when the selection is missing or invalid", () => {
    expect(resolveSchemdrawDefinitionId(null, definitions)).toBe(18);
    expect(resolveSchemdrawDefinitionId("999", definitions)).toBe(18);
    expect(resolveSchemdrawDefinitionId("new", definitions)).toBe(18);
  });

  it("preserves a valid selected definition", () => {
    expect(resolveSchemdrawDefinitionId("12", definitions)).toBe(12);
  });
});

describe("circuit schemdraw readiness inference", () => {
  it("marks definitions ready when normalized output advertises schemdraw readiness and warnings are absent", () => {
    const readiness = inferSchemdrawReadiness({
      definition_id: 18,
      name: "FloatingQubitWithXYLine",
      created_at: "2026-03-08 18:19:42",
      element_count: 12,
      validation_status: "ok",
      preview_artifact_count: 2,
      source_text: "circuit:\n  name: fluxonium_reference_a\n",
      normalized_output:
        '{ "circuit": "fluxonium_reference_a", "elements": 3, "ports": "pending", "schemdraw_ready": true }',
      validation_notices: [{ level: "ok", message: "Canonical schema matches rewrite draft v1." }],
      validation_summary: {
        status: "ok",
        notice_count: 1,
        warning_count: 0,
      },
      preview_artifacts: ["definition.normalized.json", "schematic-input.yaml"],
    });

    expect(readiness.status).toBe("ready");
    expect(readiness.warningCount).toBe(0);
    expect(readiness.artifactCount).toBe(2);
    expect(readiness.normalizedOutput?.schemdraw_ready).toBe(true);
  });

  it("marks definitions warning when validation notices contain warnings", () => {
    const readiness = inferSchemdrawReadiness({
      definition_id: 12,
      name: "FluxoniumReadoutChain",
      created_at: "2026-03-05 11:14:03",
      element_count: 9,
      validation_status: "warning",
      preview_artifact_count: 1,
      source_text: "circuit:\n  name: fluxonium_readout_chain\n",
      normalized_output: '{ "schemdraw_ready": true }',
      validation_notices: [{ level: "warning", message: "Port mapping metadata still needs migration." }],
      validation_summary: {
        status: "warning",
        notice_count: 1,
        warning_count: 1,
      },
      preview_artifacts: ["definition.normalized.json"],
    });

    expect(readiness.status).toBe("warning");
    expect(readiness.warningCount).toBe(1);
  });

  it("returns a pending state when no definition is selected", () => {
    const readiness = inferSchemdrawReadiness(undefined);

    expect(readiness.status).toBe("pending");
    expect(readiness.label).toBe("Waiting for Definition");
  });
});

describe("circuit schemdraw workflow helpers", () => {
  const definitions = [
    {
      definition_id: 18,
      name: "FloatingQubitWithXYLine",
      created_at: "2026-03-08 18:19:42",
      element_count: 12,
      validation_status: "warning",
      preview_artifact_count: 2,
    },
    {
      definition_id: 12,
      name: "FluxoniumReadoutChain",
      created_at: "2026-03-05 11:14:03",
      element_count: 9,
      validation_status: "warning",
      preview_artifact_count: 0,
    },
    {
      definition_id: 24,
      name: "TransmonControlReference",
      created_at: "2026-03-10 09:22:11",
      element_count: 7,
      validation_status: "ok",
      preview_artifact_count: 3,
    },
  ] as const;

  it("summarizes catalog readiness and artifact coverage", () => {
    expect(summarizeSchemdrawCatalog(definitions)).toEqual({
      total: 3,
      readyCount: 1,
      warningCount: 2,
      artifactBackedCount: 2,
    });
  });

  it("filters and sorts the schemdraw catalog", () => {
    const results = filterAndSortSchemdrawCatalog(definitions, {
      searchQuery: "flux",
      filter: "warning",
      sort: "name",
    });

    expect(results.map((definition) => definition.definition_id)).toEqual([12]);
  });

  it("pins the active definition when it falls out of the filtered catalog", () => {
    const filtered = filterAndSortSchemdrawCatalog(definitions, {
      searchQuery: "",
      filter: "ready",
      sort: "recent",
    });

    expect(filtered.map((definition) => definition.definition_id)).toEqual([24]);
    expect(pinActiveSchemdrawDefinition(filtered, 18)).toBe(18);
    expect(pinActiveSchemdrawDefinition(filtered, 24)).toBeNull();
  });

  it("reports invalid or missing routed selections", () => {
    expect(resolveSchemdrawSelectionRecovery("abc", 18, definitions)?.title).toBe(
      "Invalid URL selection",
    );
    expect(resolveSchemdrawSelectionRecovery("999", 18, definitions)?.title).toBe(
      "Definition not found",
    );
    expect(resolveSchemdrawSelectionRecovery(null, 18, definitions)).toBeNull();
  });

  it("builds a structured normalized output preview", () => {
    const preview = buildSchemdrawStructuredPreview(
      JSON.stringify({
        circuit: "transmon_control_reference",
        schemdraw_ready: true,
        ports: ["drive", "readout"],
        metadata: { family: "transmon" },
      }),
    );

    expect(preview.parseError).toBeNull();
    expect(preview.topLevelCount).toBe(4);
    expect(preview.rows).toEqual([
      { key: "schemdraw_ready", value: "true", tone: "success" },
      { key: "circuit", value: "transmon_control_reference", tone: "default" },
      { key: "ports", value: "2 items", tone: "default" },
      { key: "metadata", value: "1 keys", tone: "default" },
    ]);
  });

  it("partitions notices and resolves attachment state", () => {
    const notices = partitionSchemdrawNotices([
      { level: "warning", message: "Port mapping still needs migration." },
      { level: "ok", message: "Canonical schema parsed successfully." },
    ]);

    expect(notices.warnings).toHaveLength(1);
    expect(notices.checks).toHaveLength(1);
    expect(
      resolveSchemdrawAttachmentState(
        {
          definition_id: 12,
          name: "FluxoniumReadoutChain",
          created_at: "2026-03-05 11:14:03",
          element_count: 9,
          validation_status: "warning",
          preview_artifact_count: 1,
          source_text: "circuit:\n  name: fluxonium_readout_chain\n",
          normalized_output: '{ "schemdraw_ready": true }',
          validation_notices: [{ level: "warning", message: "Port mapping still needs migration." }],
          validation_summary: {
            status: "warning",
            notice_count: 1,
            warning_count: 1,
          },
          preview_artifacts: ["definition.normalized.json"],
        },
        18,
      ),
    ).toEqual({
      isAttached: false,
      isStaleSnapshot: true,
    });
  });
});
