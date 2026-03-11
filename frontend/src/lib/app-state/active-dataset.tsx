"use client";

import { createContext, useContext, useState } from "react";
import useSWR from "swr";

import {
  datasetDetailKey,
  getDataset,
  type DatasetDetail,
} from "@/lib/api/datasets";
import {
  parseDatasetIdFromSearch,
  resolveActiveDatasetId,
  resolveActiveDatasetSource,
} from "@/lib/app-state/active-dataset-state";
import { useUrlState } from "@/lib/app-state/url-state";

export type ActiveDatasetSource = "url" | "memory" | "none";

export type ActiveDatasetSnapshot = Readonly<{
  datasetId: string;
  name: string | null;
  owner: string | null;
  source: Exclude<ActiveDatasetSource, "none">;
}>;

type ActiveDatasetContextValue = Readonly<{
  activeDataset: ActiveDatasetSnapshot | null;
  routeDatasetId: string | null;
  preferredDatasetId: string | null;
  source: ActiveDatasetSource;
  datasetDetail: DatasetDetail | undefined;
  datasetDetailError: Error | undefined;
  isDatasetDetailLoading: boolean;
  rememberDataset: (datasetId: string) => void;
  clearPreferredDataset: () => void;
}>;

const ActiveDatasetContext = createContext<ActiveDatasetContextValue | null>(null);

type ActiveDatasetProviderProps = Readonly<{
  children: React.ReactNode;
}>;

export function ActiveDatasetProvider({ children }: ActiveDatasetProviderProps) {
  const urlState = useUrlState();
  const [preferredDatasetId, setPreferredDatasetId] = useState<string | null>(null);
  const routeDatasetId = parseDatasetIdFromSearch(urlState.search);
  const resolvedDatasetId = resolveActiveDatasetId(routeDatasetId, preferredDatasetId);
  const source = resolveActiveDatasetSource(routeDatasetId, preferredDatasetId);
  const detailKey = resolvedDatasetId ? datasetDetailKey(resolvedDatasetId) : null;
  const detailQuery = useSWR(detailKey, () =>
    resolvedDatasetId ? getDataset(resolvedDatasetId) : Promise.resolve(undefined),
  );

  const activeDataset =
    resolvedDatasetId && source !== "none"
      ? {
          datasetId: resolvedDatasetId,
          name: detailQuery.data?.name ?? null,
          owner: detailQuery.data?.owner ?? null,
          source,
        }
      : null;

  return (
    <ActiveDatasetContext.Provider
      value={{
        activeDataset,
        routeDatasetId,
        preferredDatasetId,
        source,
        datasetDetail: detailQuery.data,
        datasetDetailError: detailQuery.error as Error | undefined,
        isDatasetDetailLoading: detailQuery.isLoading,
        rememberDataset(datasetId) {
          setPreferredDatasetId(datasetId);
        },
        clearPreferredDataset() {
          setPreferredDatasetId(null);
        },
      }}
    >
      {children}
    </ActiveDatasetContext.Provider>
  );
}

export function useActiveDataset() {
  const context = useContext(ActiveDatasetContext);

  if (!context) {
    throw new Error("useActiveDataset must be used within an ActiveDatasetProvider.");
  }

  return context;
}
