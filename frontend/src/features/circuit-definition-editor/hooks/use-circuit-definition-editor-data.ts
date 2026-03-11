"use client";

import { useState } from "react";
import useSWR, { useSWRConfig } from "swr";

import {
  circuitDefinitionDetailKey,
  circuitDefinitionsListKey,
  createCircuitDefinition,
  deleteCircuitDefinition,
  getCircuitDefinition,
  listCircuitDefinitions,
  updateCircuitDefinition,
} from "@/features/circuit-definition-editor/lib/api";
import type {
  CircuitDefinitionDraft,
  CircuitDefinitionDetail,
} from "@/features/circuit-definition-editor/lib/contracts";

type MutationStatus = Readonly<{
  state: "idle" | "saving" | "deleting" | "success" | "error";
  message: string | null;
}>;

export function useCircuitDefinitionEditorData(selectedDefinitionId: number | "new" | null) {
  const { mutate } = useSWRConfig();
  const [mutationStatus, setMutationStatus] = useState<MutationStatus>({
    state: "idle",
    message: null,
  });

  const definitionsQuery = useSWR(circuitDefinitionsListKey, listCircuitDefinitions);
  const detailKey =
    typeof selectedDefinitionId === "number"
      ? circuitDefinitionDetailKey(selectedDefinitionId)
      : null;

  const detailQuery = useSWR(detailKey, () =>
    typeof selectedDefinitionId === "number"
      ? getCircuitDefinition(selectedDefinitionId)
      : Promise.resolve(undefined),
  );

  async function refreshDefinitionQueries(definitionId: number) {
    await Promise.all([
      mutate(circuitDefinitionsListKey),
      mutate(circuitDefinitionDetailKey(definitionId)),
    ]);
  }

  async function saveDefinition(
    draft: CircuitDefinitionDraft,
    definitionId: number | "new" | null,
  ): Promise<CircuitDefinitionDetail> {
    setMutationStatus({ state: "saving", message: null });

    try {
      const detail =
        typeof definitionId === "number"
          ? await updateCircuitDefinition(definitionId, draft)
          : await createCircuitDefinition(draft);

      await refreshDefinitionQueries(detail.definition_id);
      setMutationStatus({
        state: "success",
        message:
          typeof definitionId === "number"
            ? "Circuit definition updated."
            : "Circuit definition created.",
      });
      return detail;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Unable to save the circuit definition.";
      setMutationStatus({ state: "error", message });
      throw error;
    }
  }

  async function removeDefinition(definitionId: number) {
    setMutationStatus({ state: "deleting", message: null });

    try {
      await deleteCircuitDefinition(definitionId);
      await Promise.all([
        mutate(circuitDefinitionsListKey),
        mutate(circuitDefinitionDetailKey(definitionId), undefined, { revalidate: false }),
      ]);
      setMutationStatus({ state: "success", message: "Circuit definition removed." });
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Unable to delete the circuit definition.";
      setMutationStatus({ state: "error", message });
      throw error;
    }
  }

  function clearMutationStatus() {
    setMutationStatus({ state: "idle", message: null });
  }

  return {
    definitions: definitionsQuery.data,
    definitionsError: definitionsQuery.error as Error | undefined,
    isDefinitionsLoading: definitionsQuery.isLoading,
    activeDefinition: detailQuery.data,
    activeDefinitionError: detailQuery.error as Error | undefined,
    isActiveDefinitionLoading: detailQuery.isLoading,
    mutationStatus,
    saveDefinition,
    removeDefinition,
    clearMutationStatus,
  };
}
