"use client";

import { ActiveDatasetProvider } from "@/lib/app-state/active-dataset";
import { AppSessionProvider } from "@/lib/app-state/app-session";
import { TaskQueueProvider } from "@/lib/app-state/task-queue";

type AppStateProvidersProps = Readonly<{
  children: React.ReactNode;
}>;

export function AppStateProviders({ children }: AppStateProvidersProps) {
  return (
    <AppSessionProvider>
      <ActiveDatasetProvider>
        <TaskQueueProvider>{children}</TaskQueueProvider>
      </ActiveDatasetProvider>
    </AppSessionProvider>
  );
}

export { useActiveDataset } from "@/lib/app-state/active-dataset";
export { createAnonymousSessionSnapshot, useAppSession } from "@/lib/app-state/app-session";
export { useTaskQueue } from "@/lib/app-state/task-queue";
