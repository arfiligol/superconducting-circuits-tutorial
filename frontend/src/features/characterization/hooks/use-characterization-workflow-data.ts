"use client";

import { useState } from "react";
import useSWR, { useSWRConfig } from "swr";

import {
  buildCharacterizationRequestSummary,
  resolveLatestCharacterizationTask,
} from "@/features/characterization/lib/workflow";
import { resolveCharacterizationTaskId } from "@/features/characterization/lib/task-id";
import { useActiveDataset } from "@/lib/app-state/active-dataset";
import { useAppSession } from "@/lib/app-state/app-session";
import { useTaskQueue } from "@/lib/app-state/task-queue";
import {
  getTask,
  submitTask,
  taskDetailKey,
  tasksListKey,
  type TaskDetail,
} from "@/lib/api/tasks";

type TaskMutationStatus = Readonly<{
  state: "idle" | "submitting" | "success" | "error";
  message: string | null;
}>;

type SubmitCharacterizationTaskInput = Readonly<{
  note: string;
}>;

export function useCharacterizationWorkflowData(selectedTaskId: number | null) {
  const { mutate } = useSWRConfig();
  const { session } = useAppSession();
  const activeDatasetState = useActiveDataset();
  const taskQueueState = useTaskQueue();
  const [taskMutationStatus, setTaskMutationStatus] = useState<TaskMutationStatus>({
    state: "idle",
    message: null,
  });

  const characterizationTasks = taskQueueState.tasks.filter(
    (task) => task.kind === "characterization" || task.lane === "characterization",
  );
  const latestCharacterizationTask = resolveLatestCharacterizationTask(characterizationTasks);
  const resolvedTaskId = resolveCharacterizationTaskId(
    selectedTaskId,
    latestCharacterizationTask?.taskId ?? null,
  );
  const detailKey = resolvedTaskId ? taskDetailKey(resolvedTaskId) : null;
  const taskDetailQuery = useSWR(
    detailKey,
    () => (resolvedTaskId ? getTask(resolvedTaskId) : Promise.resolve(undefined)),
    {
      keepPreviousData: true,
      refreshInterval(currentData) {
        if (!currentData) {
          return 5_000;
        }

        return currentData.status === "queued" || currentData.status === "running" ? 2_000 : 0;
      },
    },
  );
  const activeTask = taskDetailQuery.data;
  const hasAttachedTask =
    typeof resolvedTaskId === "number" && activeTask?.taskId === resolvedTaskId;

  async function submitCharacterizationTask({
    note,
  }: SubmitCharacterizationTaskInput): Promise<TaskDetail> {
    if (!session?.canSubmitTasks) {
      const error = new Error("This session cannot submit tasks.");
      setTaskMutationStatus({ state: "error", message: error.message });
      throw error;
    }

    const datasetId = activeDatasetState.activeDataset?.datasetId ?? null;
    if (!datasetId) {
      const error = new Error("Attach an active dataset before submitting characterization.");
      setTaskMutationStatus({ state: "error", message: error.message });
      throw error;
    }

    setTaskMutationStatus({ state: "submitting", message: null });

    try {
      const task = await submitTask({
        kind: "characterization",
        dataset_id: datasetId,
        summary: buildCharacterizationRequestSummary({
          datasetId,
          datasetName: activeDatasetState.activeDataset?.name ?? null,
          note,
        }),
      });

      await Promise.all([
        mutate(tasksListKey),
        mutate(taskDetailKey(task.taskId), task, { revalidate: false }),
        taskQueueState.refreshTaskQueue(),
      ]);

      setTaskMutationStatus({
        state: "success",
        message: `Characterization task #${task.taskId} submitted.`,
      });

      return task;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Unable to submit the characterization task.";
      setTaskMutationStatus({ state: "error", message });
      throw error;
    }
  }

  function clearTaskMutationStatus() {
    setTaskMutationStatus({ state: "idle", message: null });
  }

  async function refreshCharacterizationWorkflow() {
    await Promise.all([
      taskQueueState.refreshTaskQueue().then(() => undefined),
      taskDetailQuery.mutate(),
      activeDatasetState.refreshActiveDataset(),
    ]);
  }

  return {
    session,
    activeDatasetState,
    taskQueueState,
    characterizationTasks,
    latestCharacterizationTask,
    resolvedTaskId,
    activeTask,
    activeTaskError: taskDetailQuery.error as Error | undefined,
    isTaskTransitioning:
      typeof resolvedTaskId === "number" && (!hasAttachedTask || taskDetailQuery.isLoading),
    taskMutationStatus,
    submitCharacterizationTask,
    clearTaskMutationStatus,
    refreshCharacterizationWorkflow,
    refreshTaskQueue: taskQueueState.refreshTaskQueue,
    refreshActiveTask: taskDetailQuery.mutate,
  };
}
