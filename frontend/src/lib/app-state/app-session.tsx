"use client";

import { createContext, useContext, useState } from "react";

export type AppSessionStatus = "loading" | "anonymous" | "authenticated";

export type AppSessionSnapshot = Readonly<{
  status: AppSessionStatus;
  displayName: string;
  roleLabel: string;
  authSource: "placeholder" | "backend";
  capabilities: readonly string[];
}>;

type AppSessionContextValue = Readonly<{
  session: AppSessionSnapshot;
  isAuthenticated: boolean;
  setSession: (nextSession: AppSessionSnapshot) => void;
  clearSession: () => void;
}>;

const anonymousSessionSnapshot: AppSessionSnapshot = {
  status: "anonymous",
  displayName: "Guest Session",
  roleLabel: "Rewrite Placeholder",
  authSource: "placeholder",
  capabilities: [],
};

const AppSessionContext = createContext<AppSessionContextValue | null>(null);

type AppSessionProviderProps = Readonly<{
  children: React.ReactNode;
}>;

export function createAnonymousSessionSnapshot() {
  return anonymousSessionSnapshot;
}

export function AppSessionProvider({ children }: AppSessionProviderProps) {
  const [session, setSession] = useState<AppSessionSnapshot>(anonymousSessionSnapshot);

  return (
    <AppSessionContext.Provider
      value={{
        session,
        isAuthenticated: session.status === "authenticated",
        setSession,
        clearSession() {
          setSession(anonymousSessionSnapshot);
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
