"use client";

import { useEffect, useState } from "react";
import useSWR, { useSWRConfig } from "swr";

import {
  applyCharacterizationTagging,
  characterizationResultDetailKey,
  getCharacterizationResult,
  listCharacterizationResults,
} from "@/features/characterization/lib/api";
import type { CharacterizationTaggingInput } from "@/features/characterization/lib/contracts";
import {
  resolveSelectedCharacterizationDesignId,
  resolveSelectedCharacterizationResultId,
  type CharacterizationResultStatusFilter,
} from "@/features/characterization/lib/workflow";
import { datasetMetricsKey, listDesignBrowseRows } from "@/lib/api/datasets";
import { useActiveDataset } from "@/lib/app-state/active-dataset";

type TaggingMutationState = Readonly<{
  state: "idle" | "submitting" | "success" | "error";
  message: string | null;
}>;

export function useCharacterizationWorkflowData() {
  const { mutate } = useSWRConfig();
  const activeDatasetState = useActiveDataset();
  const activeDatasetId = activeDatasetState.activeDataset?.datasetId ?? null;
  const [designSearch, setDesignSearch] = useState("");
  const [resultSearch, setResultSearch] = useState("");
  const [statusFilter, setStatusFilter] =
    useState<CharacterizationResultStatusFilter>("all");
  const [selectedDesignId, setSelectedDesignId] = useState<string | null>(null);
  const [selectedResultId, setSelectedResultId] = useState<string | null>(null);
  const [taggingMutationState, setTaggingMutationState] = useState<TaggingMutationState>({
    state: "idle",
    message: null,
  });

  const designsQuery = useSWR(
    activeDatasetId ? ["characterization-designs", activeDatasetId, designSearch] : null,
    () =>
      activeDatasetId
        ? listDesignBrowseRows(activeDatasetId, {
            search: designSearch || null,
          })
        : Promise.resolve(undefined),
  );

  const resolvedDesignId = resolveSelectedCharacterizationDesignId(
    selectedDesignId,
    designsQuery.data?.rows,
  );

  const resultsQuery = useSWR(
    activeDatasetId && resolvedDesignId
      ? [
          "characterization-results",
          activeDatasetId,
          resolvedDesignId,
          resultSearch,
          statusFilter,
        ]
      : null,
    () =>
      activeDatasetId && resolvedDesignId
        ? listCharacterizationResults(activeDatasetId, resolvedDesignId, {
            search: resultSearch || null,
            status: statusFilter === "all" ? null : statusFilter,
          })
        : Promise.resolve(undefined),
  );

  const resolvedResultId = resolveSelectedCharacterizationResultId(
    selectedResultId,
    resultsQuery.data?.rows,
  );
  const detailKey =
    activeDatasetId && resolvedDesignId && resolvedResultId
      ? characterizationResultDetailKey(activeDatasetId, resolvedDesignId, resolvedResultId)
      : null;

  const detailQuery = useSWR(
    detailKey,
    () =>
      activeDatasetId && resolvedDesignId && resolvedResultId
        ? getCharacterizationResult(activeDatasetId, resolvedDesignId, resolvedResultId)
        : Promise.resolve(undefined),
  );

  useEffect(() => {
    setSelectedDesignId((current) =>
      resolveSelectedCharacterizationDesignId(current, designsQuery.data?.rows),
    );
  }, [designsQuery.data?.rows]);

  useEffect(() => {
    setSelectedResultId((current) =>
      resolveSelectedCharacterizationResultId(current, resultsQuery.data?.rows),
    );
  }, [resultsQuery.data?.rows]);

  useEffect(() => {
    setDesignSearch("");
    setResultSearch("");
    setStatusFilter("all");
    setSelectedDesignId(null);
    setSelectedResultId(null);
  }, [activeDatasetId]);

  useEffect(() => {
    setSelectedResultId(null);
  }, [resolvedDesignId]);

  useEffect(() => {
    setTaggingMutationState({
      state: "idle",
      message: null,
    });
  }, [resolvedResultId]);

  async function submitTagging(input: CharacterizationTaggingInput) {
    if (!activeDatasetId || !resolvedDesignId || !resolvedResultId) {
      throw new Error("Select a persisted characterization result before applying identify tags.");
    }

    setTaggingMutationState({
      state: "submitting",
      message: null,
    });

    try {
      const result = await applyCharacterizationTagging(
        activeDatasetId,
        resolvedDesignId,
        resolvedResultId,
        input,
      );
      await Promise.all([
        mutate(detailKey),
        mutate(datasetMetricsKey(activeDatasetId)),
      ]);
      setTaggingMutationState({
        state: "success",
        message:
          result.taggingStatus === "already_applied"
            ? "This identify tag was already applied and the dashboard summary remains consistent."
            : "Identify tag applied. Dashboard tagged core metrics were scheduled for revalidation.",
      });
      return result;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Unable to apply the identify tag.";
      setTaggingMutationState({
        state: "error",
        message,
      });
      throw error;
    }
  }

  return {
    activeDatasetState,
    designSearch,
    setDesignSearch,
    resultSearch,
    setResultSearch,
    statusFilter,
    setStatusFilter,
    designs: designsQuery.data?.rows ?? [],
    designsMeta: designsQuery.data?.meta,
    designsError: designsQuery.error as Error | undefined,
    isDesignsLoading: designsQuery.isLoading,
    requestedDesignId: selectedDesignId,
    selectedDesignId: resolvedDesignId,
    setSelectedDesignId,
    results: resultsQuery.data?.rows ?? [],
    resultsMeta: resultsQuery.data?.meta,
    resultsError: resultsQuery.error as Error | undefined,
    isResultsLoading: resultsQuery.isLoading,
    requestedResultId: selectedResultId,
    selectedResultId: resolvedResultId,
    setSelectedResultId,
    resultDetail: detailQuery.data,
    resultDetailError: detailQuery.error as Error | undefined,
    isResultDetailLoading: detailQuery.isLoading,
    taggingMutationState,
    submitTagging,
  };
}
