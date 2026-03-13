"use client";

import { createContext, useContext } from "react";
import useSWR from "swr";

import { getTask, taskDetailKey, type TaskDetail } from "@/lib/api/tasks";
import { parseTaskIdFromSearch, resolveActiveTaskId } from "@/lib/app-state/active-task-state";
import { useTaskQueue } from "@/lib/app-state/task-queue";
import { useUrlState } from "@/lib/app-state/url-state";

export type ActiveTaskStatus = "loading" | "ready" | "empty" | "error";

type ActiveTaskContextValue = Readonly<{
  activeTaskDetail: TaskDetail | null;
  routeTaskId: number | null;
  queueTaskId: number | null;
  resolvedTaskId: number | null;
  status: ActiveTaskStatus;
  isActiveTaskLoading: boolean;
  activeTaskError: Error | undefined;
  refreshActiveTask: () => Promise<void>;
}>;

const ActiveTaskContext = createContext<ActiveTaskContextValue | null>(null);

type ActiveTaskProviderProps = Readonly<{
  children: React.ReactNode;
}>;

export function ActiveTaskProvider({ children }: ActiveTaskProviderProps) {
  const urlState = useUrlState();
  const { latestTask, hasResolvedTaskQueue } = useTaskQueue();

  const routeTaskId = parseTaskIdFromSearch(urlState.search);
  const queueTaskId = latestTask?.taskId ?? null;
  const resolvedTaskId = resolveActiveTaskId(routeTaskId, queueTaskId);

  const detailKey = resolvedTaskId ? taskDetailKey(resolvedTaskId) : null;
  const detailQuery = useSWR(detailKey, () =>
    resolvedTaskId ? getTask(resolvedTaskId) : Promise.resolve(undefined),
    {
      refreshInterval(currentData) {
        if (!currentData) return 5_000;
        return currentData.status === "queued" || currentData.status === "running" ? 2_000 : 0;
      }
    }
  );

  const activeTaskDetail = detailQuery.data ?? null;
  const activeTaskError = detailQuery.error as Error | undefined;

  const status: ActiveTaskStatus =
    (!hasResolvedTaskQueue && !activeTaskDetail) || detailQuery.isLoading
      ? "loading"
      : activeTaskError && !activeTaskDetail
        ? "error"
        : activeTaskDetail
          ? "ready"
          : "empty";

  return (
    <ActiveTaskContext.Provider
      value={{
        activeTaskDetail,
        routeTaskId,
        queueTaskId,
        resolvedTaskId,
        status,
        isActiveTaskLoading: detailQuery.isLoading,
        activeTaskError,
        async refreshActiveTask() {
          await detailQuery.mutate().then(() => undefined);
        },
      }}
    >
      {children}
    </ActiveTaskContext.Provider>
  );
}

export function useActiveTask() {
  const context = useContext(ActiveTaskContext);

  if (!context) {
    throw new Error("useActiveTask must be used within an ActiveTaskProvider.");
  }

  return context;
}
