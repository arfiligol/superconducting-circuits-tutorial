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
  const selectedDefinitionSummary =
    typeof resolvedDefinitionId === "number"
      ? definitionsQuery.data?.find(
          (definition) => definition.definition_id === resolvedDefinitionId,
        )
      : undefined;
  const detailKey =
    typeof resolvedDefinitionId === "number"
      ? circuitDefinitionDetailKey(resolvedDefinitionId)
      : null;

  const detailQuery = useSWR(detailKey, () =>
    typeof resolvedDefinitionId === "number"
      ? getCircuitDefinition(resolvedDefinitionId)
      : Promise.resolve(undefined), {
        keepPreviousData: true,
      },
  );
  const activeDefinition = detailQuery.data;
  const hasAttachedDefinition =
    typeof resolvedDefinitionId === "number" &&
    activeDefinition?.definition_id === resolvedDefinitionId;

  return {
    definitions: definitionsQuery.data,
    definitionsError: definitionsQuery.error as Error | undefined,
    isDefinitionsLoading: definitionsQuery.isLoading,
    resolvedDefinitionId,
    selectedDefinitionSummary,
    activeDefinition,
    activeDefinitionError: detailQuery.error as Error | undefined,
    isActiveDefinitionLoading: detailQuery.isLoading,
    isDefinitionTransitioning:
      typeof resolvedDefinitionId === "number" &&
      (!hasAttachedDefinition || detailQuery.isLoading),
    refreshDefinitions: definitionsQuery.mutate,
    refreshActiveDefinition: detailQuery.mutate,
  };
}
