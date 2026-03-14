"use client";

import useSWR, { useSWRConfig } from "swr";

import {
  datasetCatalogKey,
  datasetMetricsKey,
  datasetProfileKey,
  getDatasetProfile,
  listDatasetCatalog,
  listTaggedCoreMetrics,
  updateDatasetProfile,
  type DatasetProfileUpdate,
} from "@/lib/api/datasets";
import { useActiveDataset } from "@/lib/app-state/active-dataset";

export function useDashboardData() {
  const { mutate } = useSWRConfig();
  const activeDatasetState = useActiveDataset();
  const activeDatasetId = activeDatasetState.activeDataset?.datasetId ?? null;

  const catalogQuery = useSWR(datasetCatalogKey, listDatasetCatalog);
  const profileQuery = useSWR(
    activeDatasetId ? datasetProfileKey(activeDatasetId) : null,
    () => (activeDatasetId ? getDatasetProfile(activeDatasetId) : Promise.resolve(undefined)),
  );
  const metricsQuery = useSWR(
    activeDatasetId ? datasetMetricsKey(activeDatasetId) : null,
    () => (activeDatasetId ? listTaggedCoreMetrics(activeDatasetId) : Promise.resolve([])),
  );

  async function saveProfile(payload: DatasetProfileUpdate) {
    if (!activeDatasetId) {
      throw new Error("Attach a dataset before editing dashboard metadata.");
    }
    const result = await updateDatasetProfile(activeDatasetId, payload);
    await Promise.all([
      mutate(datasetCatalogKey),
      mutate(datasetProfileKey(activeDatasetId), result.dataset, { revalidate: false }),
      activeDatasetState.refreshActiveDataset(),
    ]);
    return result;
  }

  return {
    activeDatasetState,
    catalog: catalogQuery.data,
    catalogError: catalogQuery.error as Error | undefined,
    isCatalogLoading: catalogQuery.isLoading,
    profile: profileQuery.data,
    profileError: profileQuery.error as Error | undefined,
    isProfileLoading: profileQuery.isLoading,
    metrics: metricsQuery.data ?? [],
    metricsError: metricsQuery.error as Error | undefined,
    isMetricsLoading: metricsQuery.isLoading,
    saveProfile,
  };
}
