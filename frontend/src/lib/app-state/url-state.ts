"use client";

import { useSyncExternalStore } from "react";

export type UrlSnapshot = Readonly<{
  pathname: string;
  search: string;
}>;

const URL_STATE_EVENT = "app:url-state-change";
let historyPatched = false;

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

function getUrlSnapshot(): UrlSnapshot {
  if (typeof window === "undefined") {
    return { pathname: "", search: "" };
  }

  return {
    pathname: window.location.pathname,
    search: window.location.search,
  };
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
  return useSyncExternalStore(subscribeToUrlState, getUrlSnapshot, getUrlSnapshot);
}
