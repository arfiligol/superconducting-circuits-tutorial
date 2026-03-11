"use client";

import useSWR from "swr";

import {
  circuitDefinitionDetailKey,
  circuitDefinitionsListKey,
  getCircuitDefinition,
  listCircuitDefinitions,
} from "@/features/circuit-definition-editor/lib/api";
import { resolveSchemdrawDefinitionId } from "@/features/circuit-schemdraw/lib/definition-id";

export function useCircuitSchemdrawData(selectedDefinitionId: number | null) {
  const definitionsQuery = useSWR(circuitDefinitionsListKey, listCircuitDefinitions);
  const resolvedDefinitionId = resolveSchemdrawDefinitionId(
    selectedDefinitionId === null ? null : String(selectedDefinitionId),
    definitionsQuery.data,
  );
  const detailKey =
    typeof resolvedDefinitionId === "number"
      ? circuitDefinitionDetailKey(resolvedDefinitionId)
      : null;

  const detailQuery = useSWR(detailKey, () =>
    typeof resolvedDefinitionId === "number"
      ? getCircuitDefinition(resolvedDefinitionId)
      : Promise.resolve(undefined),
  );

  return {
    definitions: definitionsQuery.data,
    definitionsError: definitionsQuery.error as Error | undefined,
    isDefinitionsLoading: definitionsQuery.isLoading,
    resolvedDefinitionId,
    activeDefinition: detailQuery.data,
    activeDefinitionError: detailQuery.error as Error | undefined,
    isActiveDefinitionLoading: detailQuery.isLoading,
  };
}
