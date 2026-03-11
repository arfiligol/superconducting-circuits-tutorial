export function parseDatasetIdFromSearch(search: string): string | null {
  const params = new URLSearchParams(search.startsWith("?") ? search.slice(1) : search);
  const datasetId = params.get("datasetId")?.trim();
  return datasetId ? datasetId : null;
}

export function resolveActiveDatasetId(
  routeDatasetId: string | null,
  sessionDatasetId: string | null,
): string | null {
  return routeDatasetId ?? sessionDatasetId;
}

export function resolveActiveDatasetSource(
  routeDatasetId: string | null,
  sessionDatasetId: string | null,
): "url" | "session" | "none" {
  if (routeDatasetId) {
    return "url";
  }

  if (sessionDatasetId) {
    return "session";
  }

  return "none";
}
