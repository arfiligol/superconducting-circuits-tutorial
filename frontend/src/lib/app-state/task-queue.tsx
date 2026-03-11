"use client";

import { createContext, useContext, useReducer } from "react";

import {
  createTaskQueueItem,
  summarizeTaskQueue,
  taskQueueReducer,
  type TaskQueueItem,
  type TaskQueueScope,
} from "@/lib/app-state/task-queue-store";

type TaskQueueContextValue = Readonly<{
  tasks: readonly TaskQueueItem[];
  summary: ReturnType<typeof summarizeTaskQueue>;
  enqueueTask: (input: {
    taskId: string;
    label: string;
    detail: string;
    scope: TaskQueueScope;
  }) => void;
  updateTask: (
    taskId: string,
    patch: Partial<Pick<TaskQueueItem, "label" | "detail" | "status" | "updatedAt">>,
  ) => void;
  removeTask: (taskId: string) => void;
  clearTasks: () => void;
  replaceTasks: (tasks: readonly TaskQueueItem[]) => void;
}>;

const TaskQueueContext = createContext<TaskQueueContextValue | null>(null);

type TaskQueueProviderProps = Readonly<{
  children: React.ReactNode;
}>;

export function TaskQueueProvider({ children }: TaskQueueProviderProps) {
  const [tasks, dispatch] = useReducer(taskQueueReducer, [] as readonly TaskQueueItem[]);

  return (
    <TaskQueueContext.Provider
      value={{
        tasks,
        summary: summarizeTaskQueue(tasks),
        enqueueTask(input) {
          dispatch({
            type: "enqueue",
            task: createTaskQueueItem(input),
          });
        },
        updateTask(taskId, patch) {
          dispatch({ type: "update", taskId, patch });
        },
        removeTask(taskId) {
          dispatch({ type: "remove", taskId });
        },
        clearTasks() {
          dispatch({ type: "clear" });
        },
        replaceTasks(nextTasks) {
          dispatch({ type: "replace", tasks: nextTasks });
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
