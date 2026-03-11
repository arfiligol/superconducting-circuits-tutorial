"use client";

import { createContext, useContext, useEffect, useEffectEvent, useState } from "react";
import useSWR from "swr";

import {
  datasetDetailKey,
  getDataset,
} from "@/lib/api/datasets";
import { patchActiveDataset } from "@/lib/api/session";
import {
  parseDatasetIdFromSearch,
  resolveActiveDatasetId,
  resolveActiveDatasetSource,
} from "@/lib/app-state/active-dataset-state";
import { useAppSession } from "@/lib/app-state/app-session";
import { useUrlState } from "@/lib/app-state/url-state";

export type ActiveDatasetSource = "url" | "session" | "none";

export type ActiveDatasetSnapshot = Readonly<{
  datasetId: string;
  name: string | null;
  owner: string | null;
  family: string | null;
  status: "Ready" | "Queued" | "Review" | null;
  source: Exclude<ActiveDatasetSource, "none">;
}>;

type ActiveDatasetContextValue = Readonly<{
  activeDataset: ActiveDatasetSnapshot | null;
  routeDatasetId: string | null;
  sessionDatasetId: string | null;
  source: ActiveDatasetSource;
  isDatasetDetailLoading: boolean;
  datasetDetailError: Error | undefined;
  isUpdatingActiveDataset: boolean;
  activeDatasetError: Error | undefined;
  setActiveDataset: (datasetId: string | null) => Promise<void>;
  clearActiveDataset: () => Promise<void>;
}>;

const ActiveDatasetContext = createContext<ActiveDatasetContextValue | null>(null);

type ActiveDatasetProviderProps = Readonly<{
  children: React.ReactNode;
}>;

export function ActiveDatasetProvider({ children }: ActiveDatasetProviderProps) {
  const {
    session,
    sessionError,
    replaceSession,
  } = useAppSession();
  const urlState = useUrlState();
  const [mutationError, setMutationError] = useState<Error | undefined>(undefined);
  const [isUpdatingActiveDataset, setIsUpdatingActiveDataset] = useState(false);
  const [lastRouteSyncTargetId, setLastRouteSyncTargetId] = useState<string | null>(null);
  const routeDatasetId = parseDatasetIdFromSearch(urlState.search);
  const sessionDatasetId = session?.activeDataset?.datasetId ?? null;
  const resolvedDatasetId = resolveActiveDatasetId(routeDatasetId, sessionDatasetId);
  const source = resolveActiveDatasetSource(routeDatasetId, sessionDatasetId);
  const detailKey = resolvedDatasetId ? datasetDetailKey(resolvedDatasetId) : null;
  const detailQuery = useSWR(detailKey, () =>
    resolvedDatasetId ? getDataset(resolvedDatasetId) : Promise.resolve(undefined),
  );

  async function syncActiveDataset(datasetId: string | null) {
    setMutationError(undefined);
    setIsUpdatingActiveDataset(true);
    setLastRouteSyncTargetId(datasetId);

    try {
      const nextSession = await patchActiveDataset(datasetId);
      await replaceSession(nextSession);
    } catch (error) {
      setMutationError(error instanceof Error ? error : new Error("Unable to update active dataset."));
      throw error;
    } finally {
      setIsUpdatingActiveDataset(false);
    }
  }

  const syncRouteDatasetToSession = useEffectEvent((datasetId: string) => {
    void syncActiveDataset(datasetId).catch(() => undefined);
  });

  useEffect(() => {
    if (
      !routeDatasetId ||
      routeDatasetId === sessionDatasetId ||
      isUpdatingActiveDataset ||
      routeDatasetId === lastRouteSyncTargetId
    ) {
      return;
    }

    syncRouteDatasetToSession(routeDatasetId);
  }, [routeDatasetId, sessionDatasetId, isUpdatingActiveDataset, lastRouteSyncTargetId]);

  useEffect(() => {
    if (routeDatasetId && routeDatasetId === sessionDatasetId && lastRouteSyncTargetId === routeDatasetId) {
      setLastRouteSyncTargetId(null);
    }
  }, [routeDatasetId, sessionDatasetId, lastRouteSyncTargetId]);

  const activeDataset =
    resolvedDatasetId && source !== "none"
      ? {
          datasetId: resolvedDatasetId,
          name:
            session?.activeDataset?.datasetId === resolvedDatasetId
              ? session.activeDataset.name
              : (detailQuery.data?.name ?? null),
          owner: detailQuery.data?.owner ?? null,
          family:
            session?.activeDataset?.datasetId === resolvedDatasetId
              ? session.activeDataset.family
              : (detailQuery.data?.family ?? null),
          status:
            session?.activeDataset?.datasetId === resolvedDatasetId
              ? session.activeDataset.status
              : (detailQuery.data?.status ?? null),
          source,
        }
      : null;

  return (
    <ActiveDatasetContext.Provider
      value={{
        activeDataset,
        routeDatasetId,
        sessionDatasetId,
        source,
        isDatasetDetailLoading: detailQuery.isLoading,
        datasetDetailError: detailQuery.error as Error | undefined,
        isUpdatingActiveDataset,
        activeDatasetError: mutationError ?? (detailQuery.error as Error | undefined) ?? sessionError,
        async setActiveDataset(datasetId) {
          await syncActiveDataset(datasetId);
        },
        async clearActiveDataset() {
          await syncActiveDataset(null);
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
