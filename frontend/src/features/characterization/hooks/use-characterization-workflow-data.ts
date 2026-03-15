"use client";

import { useEffect, useState } from "react";
import useSWR from "swr";

import {
  getCharacterizationResult,
  listCharacterizationResults,
} from "@/features/characterization/lib/api";
import {
  resolveSelectedCharacterizationDesignId,
  resolveSelectedCharacterizationResultId,
  type CharacterizationResultStatusFilter,
} from "@/features/characterization/lib/workflow";
import { listDesignBrowseRows } from "@/lib/api/datasets";
import { useActiveDataset } from "@/lib/app-state/active-dataset";

export function useCharacterizationWorkflowData() {
  const activeDatasetState = useActiveDataset();
  const activeDatasetId = activeDatasetState.activeDataset?.datasetId ?? null;
  const [designSearch, setDesignSearch] = useState("");
  const [resultSearch, setResultSearch] = useState("");
  const [statusFilter, setStatusFilter] =
    useState<CharacterizationResultStatusFilter>("all");
  const [selectedDesignId, setSelectedDesignId] = useState<string | null>(null);
  const [selectedResultId, setSelectedResultId] = useState<string | null>(null);

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

  const detailQuery = useSWR(
    activeDatasetId && resolvedDesignId && resolvedResultId
      ? ["characterization-result-detail", activeDatasetId, resolvedDesignId, resolvedResultId]
      : null,
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
  };
}
