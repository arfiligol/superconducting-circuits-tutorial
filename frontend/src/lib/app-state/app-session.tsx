"use client";

import { createContext, useContext } from "react";
import useSWR from "swr";

import {
  appSessionKey,
  getSession,
  type SessionSnapshot,
} from "@/lib/api/session";

type AppSessionContextValue = Readonly<{
  session: SessionSnapshot | undefined;
  sessionError: Error | undefined;
  isSessionLoading: boolean;
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

  return (
    <AppSessionContext.Provider
      value={{
        session: sessionQuery.data,
        sessionError: sessionQuery.error as Error | undefined,
        isSessionLoading: sessionQuery.isLoading,
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
