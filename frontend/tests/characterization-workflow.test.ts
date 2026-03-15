import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import {
  characterizationResultDetailKey,
  characterizationResultsListKey,
} from "../src/features/characterization/lib/api";
import {
  resolveCharacterizationSelectionRecovery,
  resolveSelectedCharacterizationDesignId,
  resolveSelectedCharacterizationResultId,
  summarizeCharacterizationResults,
} from "../src/features/characterization/lib/workflow";

const characterizationWorkspaceSource = readFileSync(
  fileURLToPath(
    new URL(
      "../src/features/characterization/components/characterization-workspace.tsx",
      import.meta.url,
    ),
  ),
  "utf8",
);
const characterizationHookSource = readFileSync(
  fileURLToPath(
    new URL(
      "../src/features/characterization/hooks/use-characterization-workflow-data.ts",
      import.meta.url,
    ),
  ),
  "utf8",
);

describe("characterization results api keys", () => {
  it("builds stable dataset and result detail paths", () => {
    expect(
      characterizationResultsListKey("fluxonium-2025-031", "design_flux_scan_a"),
    ).toBe(
      "/api/backend/datasets/fluxonium-2025-031/designs/design_flux_scan_a/characterization-results",
    );
    expect(
      characterizationResultDetailKey(
        "fluxonium-2025-031",
        "design_flux_scan_a",
        "char-fit-flux-a-01",
      ),
    ).toBe(
      "/api/backend/datasets/fluxonium-2025-031/designs/design_flux_scan_a/characterization-results/char-fit-flux-a-01",
    );
  });

  it("encodes dataset, design, and result ids for nested routes", () => {
    expect(
      characterizationResultDetailKey("dataset/a", "design b", "result/c"),
    ).toBe(
      "/api/backend/datasets/dataset%2Fa/designs/design%20b/characterization-results/result%2Fc",
    );
  });
});

describe("characterization browse helpers", () => {
  const designs = [
    {
      design_id: "design_flux_scan_a",
      dataset_id: "fluxonium-2025-031",
      name: "Flux Scan A",
      source_coverage: { measurement: 2 },
      compare_readiness: "ready",
      trace_count: 3,
      updated_at: "2026-03-15T08:20:00Z",
    },
    {
      design_id: "design_flux_scan_b",
      dataset_id: "fluxonium-2025-031",
      name: "Flux Scan B",
      source_coverage: { layout_simulation: 1 },
      compare_readiness: "inspect_only",
      trace_count: 1,
      updated_at: "2026-03-15T07:55:00Z",
    },
  ] as const;

  const results = [
    {
      resultId: "char-fit-flux-a-01",
      datasetId: "fluxonium-2025-031",
      designId: "design_flux_scan_a",
      analysisId: "admittance_extraction",
      title: "Admittance Fit",
      status: "completed",
      freshnessSummary: "Fresh",
      provenanceSummary: "Measurement · Postprocess batch #4",
      traceCount: 2,
      artifactCount: 3,
      updatedAt: "2026-03-15T08:22:00Z",
    },
    {
      resultId: "char-sideband-flux-a-02",
      datasetId: "fluxonium-2025-031",
      designId: "design_flux_scan_a",
      analysisId: "sideband_identification",
      title: "Sideband Identification",
      status: "failed",
      freshnessSummary: "Input scope needs review",
      provenanceSummary: "Measurement · Sideband batch #7",
      traceCount: 1,
      artifactCount: 1,
      updatedAt: "2026-03-15T08:25:00Z",
    },
  ] as const;

  it("resolves visible design and result selections", () => {
    expect(resolveSelectedCharacterizationDesignId(null, designs)).toBe("design_flux_scan_a");
    expect(
      resolveSelectedCharacterizationDesignId("design_flux_scan_b", designs),
    ).toBe("design_flux_scan_b");
    expect(resolveSelectedCharacterizationDesignId("missing", designs)).toBe(
      "design_flux_scan_a",
    );
    expect(resolveSelectedCharacterizationDesignId("missing", [])).toBeNull();

    expect(resolveSelectedCharacterizationResultId(null, results)).toBe("char-fit-flux-a-01");
    expect(
      resolveSelectedCharacterizationResultId("char-sideband-flux-a-02", results),
    ).toBe("char-sideband-flux-a-02");
    expect(resolveSelectedCharacterizationResultId("missing", results)).toBe(
      "char-fit-flux-a-01",
    );
    expect(resolveSelectedCharacterizationResultId("missing", [])).toBeNull();
  });

  it("summarizes persisted results and emits recovery notices for stale browse state", () => {
    expect(summarizeCharacterizationResults(results)).toEqual({
      total: 2,
      completedCount: 1,
      failedCount: 1,
      blockedCount: 0,
      artifactCount: 4,
    });

    expect(
      resolveCharacterizationSelectionRecovery({
        activeDatasetName: "Fluxonium sweep 031",
        requestedDesignId: "design_old",
        resolvedDesignId: "design_flux_scan_a",
        requestedResultId: null,
        resolvedResultId: null,
      }),
    ).toEqual({
      tone: "warning",
      title: "Design scope rebound",
      message:
        "The active dataset now exposes design_flux_scan_a instead of design_old. Browse state was rebound to stay within Fluxonium sweep 031.",
    });

    expect(
      resolveCharacterizationSelectionRecovery({
        activeDatasetName: "Fluxonium sweep 031",
        requestedDesignId: "design_flux_scan_a",
        resolvedDesignId: "design_flux_scan_a",
        requestedResultId: "missing-result",
        resolvedResultId: "char-fit-flux-a-01",
      }),
    ).toEqual({
      tone: "warning",
      title: "Result selection rebound",
      message:
        "Result missing-result is no longer available for this design. The detail surface switched to char-fit-flux-a-01.",
    });
  });
});

describe("characterization source contracts", () => {
  it("keeps the page on dataset/design/result browse and read responsibilities", () => {
    expect(characterizationWorkspaceSource).toContain("Result Summary List");
    expect(characterizationWorkspaceSource).toContain("Persisted Result Detail");
    expect(characterizationWorkspaceSource).toContain("Payload Preview");
    expect(characterizationWorkspaceSource).not.toContain("submitTask(");
    expect(characterizationWorkspaceSource).not.toContain("TaskLifecyclePanel");
    expect(characterizationWorkspaceSource).not.toContain("ResearchTaskQueuePanel");
    expect(characterizationWorkspaceSource).not.toContain("Tasks Queue");
  });

  it("binds characterization data to the shared active dataset and page-local selection state", () => {
    expect(characterizationHookSource).toContain(
      "const activeDatasetId = activeDatasetState.activeDataset?.datasetId ?? null",
    );
    expect(characterizationHookSource).toContain("listDesignBrowseRows(activeDatasetId");
    expect(characterizationHookSource).toContain("listCharacterizationResults(activeDatasetId, resolvedDesignId");
    expect(characterizationHookSource).toContain(
      "getCharacterizationResult(activeDatasetId, resolvedDesignId, resolvedResultId)",
    );
    expect(characterizationHookSource).toContain("setSelectedDesignId(null);");
    expect(characterizationHookSource).toContain("setSelectedResultId(null);");
    expect(characterizationHookSource).not.toContain("useTaskQueue");
    expect(characterizationHookSource).not.toContain("submitCharacterizationTask");
  });
});
