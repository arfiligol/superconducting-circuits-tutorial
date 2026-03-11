import { describe, expect, it } from "vitest";

import {
  circuitDefinitionDetailKey,
  circuitDefinitionsListKey,
} from "../src/features/circuit-definition-editor/lib/api";
import {
  parseDefinitionIdParam,
  resolveSelectedDefinitionId,
} from "../src/features/circuit-definition-editor/lib/definition-id";

describe("circuit definition editor routing helpers", () => {
  const definitions = [
    {
      definition_id: 18,
      name: "FloatingQubitWithXYLine",
      created_at: "2026-03-08 18:19:42",
      element_count: 12,
    },
    {
      definition_id: 12,
      name: "FluxoniumReadoutChain",
      created_at: "2026-03-05 11:14:03",
      element_count: 9,
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
});
