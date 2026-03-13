"use client";

import { createContext, useContext } from "react";
import useSWR from "swr";

import {
  appSessionKey,
  getSession,
  type SessionSnapshot,
} from "@/lib/api/session";

export type AppSessionStatus = "loading" | "ready" | "error" | "refreshing";

type AppSessionContextValue = Readonly<{
  session: SessionSnapshot | undefined;
  workspace: SessionSnapshot["workspace"] | undefined;
  sessionError: Error | undefined;
  status: AppSessionStatus;
  isSessionLoading: boolean;
  isSessionRefreshing: boolean;
  hasResolvedSession: boolean;
  isAuthenticated: boolean;
  refreshSession: () => Promise<SessionSnapshot | undefined>;
  replaceSession: (nextSession: SessionSnapshot) => Promise<SessionSnapshot | undefined>;
}>;

const AppSessionContext = createContext<AppSessionContextValue | null>(null);

type AppSessionProviderProps = Readonly<{
  children: React.ReactNode;
}>;

export function AppSessionProvider({ children }: AppSessionProviderProps) {
  const sessionQuery = useSWR(appSessionKey, getSession);
  const status: AppSessionStatus =
    sessionQuery.isLoading && !sessionQuery.data
      ? "loading"
      : sessionQuery.error && !sessionQuery.data
        ? "error"
        : sessionQuery.isValidating && !!sessionQuery.data
          ? "refreshing"
          : "ready";

  return (
    <AppSessionContext.Provider
      value={{
        session: sessionQuery.data,
        workspace: sessionQuery.data?.workspace,
        sessionError: sessionQuery.error as Error | undefined,
        status,
        isSessionLoading: sessionQuery.isLoading,
        isSessionRefreshing: status === "refreshing",
        hasResolvedSession: !!sessionQuery.data || !!sessionQuery.error,
        isAuthenticated: sessionQuery.data?.authState === "authenticated",
        async refreshSession() {
          return sessionQuery.mutate();
        },
        async replaceSession(nextSession) {
          return sessionQuery.mutate(nextSession, { revalidate: false });
        },
      }}
    >
      {children}
    </AppSessionContext.Provider>
  );
}

export function useAppSession() {
  const context = useContext(AppSessionContext);

  if (!context) {
    throw new Error("useAppSession must be used within an AppSessionProvider.");
  }

  return context;
}
