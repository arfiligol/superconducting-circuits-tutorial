import { describe, expect, it } from "vitest";

import {
  parseSchemdrawDefinitionIdParam,
  resolveSchemdrawDefinitionId,
} from "../src/features/circuit-schemdraw/lib/definition-id";
import { inferSchemdrawReadiness } from "../src/features/circuit-schemdraw/lib/readiness";

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
