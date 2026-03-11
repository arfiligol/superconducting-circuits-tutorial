"use client";

import { useState } from "react";
import useSWR, { useSWRConfig } from "swr";

import {
  datasetDetailKey,
  datasetsListKey,
  getDataset,
  listDatasets,
  updateDatasetMetadata,
} from "@/features/data-browser/lib/api";
import { resolveSelectedDatasetId } from "@/features/data-browser/lib/dataset-id";
import type {
  DatasetDetail,
  DatasetMetadataUpdate,
} from "@/features/data-browser/lib/contracts";

type MutationStatus = Readonly<{
  state: "idle" | "saving" | "success" | "error";
  message: string | null;
}>;

export function useDataBrowserData(selectedDatasetId: string | null) {
  const { mutate } = useSWRConfig();
  const [mutationStatus, setMutationStatus] = useState<MutationStatus>({
    state: "idle",
    message: null,
  });

  const datasetsQuery = useSWR(datasetsListKey, listDatasets);
  const resolvedDatasetId = resolveSelectedDatasetId(selectedDatasetId, datasetsQuery.data);
  const detailKey = resolvedDatasetId ? datasetDetailKey(resolvedDatasetId) : null;
  const detailQuery = useSWR(detailKey, () =>
    resolvedDatasetId ? getDataset(resolvedDatasetId) : Promise.resolve(undefined),
  );

  async function saveMetadata(payload: DatasetMetadataUpdate): Promise<DatasetDetail> {
    if (!resolvedDatasetId) {
      const error = new Error("Choose a dataset before updating metadata.");
      setMutationStatus({ state: "error", message: error.message });
      throw error;
    }

    setMutationStatus({ state: "saving", message: null });

    try {
      const detail = await updateDatasetMetadata(resolvedDatasetId, payload);

      await Promise.all([
        mutate(datasetsListKey),
        mutate(datasetDetailKey(resolvedDatasetId), detail, { revalidate: false }),
      ]);

      setMutationStatus({ state: "success", message: "Dataset metadata updated." });
      return detail;
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unable to update dataset metadata.";
      setMutationStatus({ state: "error", message });
      throw error;
    }
  }

  function clearMutationStatus() {
    setMutationStatus({ state: "idle", message: null });
  }

  return {
    datasets: datasetsQuery.data,
    datasetsError: datasetsQuery.error as Error | undefined,
    isDatasetsLoading: datasetsQuery.isLoading,
    resolvedDatasetId,
    activeDataset: detailQuery.data,
    activeDatasetError: detailQuery.error as Error | undefined,
    isActiveDatasetLoading: detailQuery.isLoading,
    mutationStatus,
    saveMetadata,
    clearMutationStatus,
  };
}
