"use client";

import { createContext, useContext } from "react";
import useSWR from "swr";

import {
  summarizeTaskQueue,
  type TaskQueueItem,
} from "@/lib/app-state/task-queue-store";
import { listTasks, tasksListKey } from "@/lib/api/tasks";

type TaskQueueContextValue = Readonly<{
  tasks: readonly TaskQueueItem[];
  summary: ReturnType<typeof summarizeTaskQueue>;
  latestTask: TaskQueueItem | undefined;
  isTaskQueueLoading: boolean;
  taskQueueError: Error | undefined;
  refreshTaskQueue: () => Promise<readonly TaskQueueItem[] | undefined>;
}>;

const TaskQueueContext = createContext<TaskQueueContextValue | null>(null);

type TaskQueueProviderProps = Readonly<{
  children: React.ReactNode;
}>;

export function TaskQueueProvider({ children }: TaskQueueProviderProps) {
  const tasksQuery = useSWR(tasksListKey, listTasks);
  const tasks = tasksQuery.data ?? [];

  return (
    <TaskQueueContext.Provider
      value={{
        tasks,
        summary: summarizeTaskQueue(tasks),
        latestTask: tasks[0],
        isTaskQueueLoading: tasksQuery.isLoading,
        taskQueueError: tasksQuery.error as Error | undefined,
        async refreshTaskQueue() {
          return tasksQuery.mutate();
        },
      }}
    >
      {children}
    </TaskQueueContext.Provider>
  );
}

export function useTaskQueue() {
  const context = useContext(TaskQueueContext);

  if (!context) {
    throw new Error("useTaskQueue must be used within a TaskQueueProvider.");
  }

  return context;
}
