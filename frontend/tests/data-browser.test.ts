import { describe, expect, it } from "vitest";

import {
  datasetDetailKey,
  datasetMetadataKey,
  datasetsListKey,
} from "../src/features/data-browser/lib/api";
import {
  parseDatasetIdParam,
  resolveSelectedDatasetId,
} from "../src/features/data-browser/lib/dataset-id";

describe("data browser routing helpers", () => {
  const datasets = [
    {
      dataset_id: "fluxonium-2025-031",
      name: "Fluxonium sweep 031",
      family: "Fluxonium",
      owner: "Device Lab",
      updated_at: "2026-02-26 13:40",
      samples: 184,
      status: "Ready",
    },
    {
      dataset_id: "transmon-coupler-014",
      name: "Coupler detuning 014",
      family: "Transmon",
      owner: "Modeling",
      updated_at: "2026-02-24 09:15",
      samples: 76,
      status: "Review",
    },
  ] as const;

  it("parses present dataset ids and drops empty values", () => {
    expect(parseDatasetIdParam("fluxonium-2025-031")).toBe("fluxonium-2025-031");
    expect(parseDatasetIdParam("   ")).toBeNull();
    expect(parseDatasetIdParam(null)).toBeNull();
  });

  it("falls back to the first dataset when the selection is missing or invalid", () => {
    expect(resolveSelectedDatasetId(null, datasets)).toBe("fluxonium-2025-031");
    expect(resolveSelectedDatasetId("missing-id", datasets)).toBe("fluxonium-2025-031");
  });

  it("preserves a valid dataset selection", () => {
    expect(resolveSelectedDatasetId("transmon-coupler-014", datasets)).toBe(
      "transmon-coupler-014",
    );
  });
});

describe("data browser api keys", () => {
  it("keeps stable list, detail, and metadata paths", () => {
    expect(datasetsListKey).toBe("/api/backend/datasets");
    expect(datasetDetailKey("fluxonium-2025-031")).toBe(
      "/api/backend/datasets/fluxonium-2025-031",
    );
    expect(datasetMetadataKey("fluxonium-2025-031")).toBe(
      "/api/backend/datasets/fluxonium-2025-031/metadata",
    );
  });

  it("encodes dataset ids when building detail paths", () => {
    expect(datasetDetailKey("folder/a b")).toBe("/api/backend/datasets/folder%2Fa%20b");
  });
});
