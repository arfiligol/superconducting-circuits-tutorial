export function parseDatasetIdFromSearch(search: string): string | null {
  const params = new URLSearchParams(search.startsWith("?") ? search.slice(1) : search);
  const datasetId = params.get("datasetId")?.trim();
  return datasetId ? datasetId : null;
}

export function resolveActiveDatasetId(
  routeDatasetId: string | null,
  preferredDatasetId: string | null,
): string | null {
  return routeDatasetId ?? preferredDatasetId;
}

export function resolveActiveDatasetSource(
  routeDatasetId: string | null,
  preferredDatasetId: string | null,
): "url" | "memory" | "none" {
  if (routeDatasetId) {
    return "url";
  }

  if (preferredDatasetId) {
    return "memory";
  }

  return "none";
}
