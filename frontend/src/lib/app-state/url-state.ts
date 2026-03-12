"use client";

import { useSyncExternalStore } from "react";

export type UrlSnapshot = Readonly<{
  pathname: string;
  search: string;
}>;

const URL_STATE_EVENT = "app:url-state-change";
const EMPTY_URL_SNAPSHOT: UrlSnapshot = {
  pathname: "",
  search: "",
};
let historyPatched = false;
let cachedUrlSnapshot: UrlSnapshot = EMPTY_URL_SNAPSHOT;

function emitUrlStateChange() {
  window.dispatchEvent(new Event(URL_STATE_EVENT));
}

function patchHistoryMethods() {
  if (historyPatched || typeof window === "undefined") {
    return;
  }

  historyPatched = true;

  const originalPushState = window.history.pushState.bind(window.history);
  const originalReplaceState = window.history.replaceState.bind(window.history);

  window.history.pushState = function pushState(...args) {
    originalPushState(...args);
    emitUrlStateChange();
  };

  window.history.replaceState = function replaceState(...args) {
    originalReplaceState(...args);
    emitUrlStateChange();
  };
}

export function resolveUrlSnapshot(
  previousSnapshot: UrlSnapshot,
  pathname: string,
  search: string,
): UrlSnapshot {
  if (previousSnapshot.pathname === pathname && previousSnapshot.search === search) {
    return previousSnapshot;
  }

  return {
    pathname,
    search,
  };
}

function getClientUrlSnapshot(): UrlSnapshot {
  cachedUrlSnapshot = resolveUrlSnapshot(
    cachedUrlSnapshot,
    window.location.pathname,
    window.location.search,
  );

  return cachedUrlSnapshot;
}

function getServerUrlSnapshot(): UrlSnapshot {
  return EMPTY_URL_SNAPSHOT;
}

function getUrlSnapshot(): UrlSnapshot {
  if (typeof window === "undefined") {
    return getServerUrlSnapshot();
  }

  return getClientUrlSnapshot();
}

function subscribeToUrlState(onStoreChange: () => void) {
  if (typeof window === "undefined") {
    return () => undefined;
  }

  patchHistoryMethods();

  window.addEventListener(URL_STATE_EVENT, onStoreChange);
  window.addEventListener("popstate", onStoreChange);

  return () => {
    window.removeEventListener(URL_STATE_EVENT, onStoreChange);
    window.removeEventListener("popstate", onStoreChange);
  };
}

export function useUrlState() {
  return useSyncExternalStore(
    subscribeToUrlState,
    getUrlSnapshot,
    getServerUrlSnapshot,
  );
}
