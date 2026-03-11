import { apiRequest } from "@/lib/api/client";

import type {
  DatasetDetail,
  DatasetMetadataUpdate,
  DatasetSummary,
} from "@/features/data-browser/lib/contracts";

export const datasetsListKey = "/api/backend/datasets";

export function datasetDetailKey(datasetId: string) {
  return `/api/backend/datasets/${encodeURIComponent(datasetId)}`;
}

export function datasetMetadataKey(datasetId: string) {
  return `${datasetDetailKey(datasetId)}/metadata`;
}

export async function listDatasets() {
  return apiRequest<DatasetSummary[]>(datasetsListKey);
}

export async function getDataset(datasetId: string) {
  return apiRequest<DatasetDetail>(datasetDetailKey(datasetId));
}

export async function updateDatasetMetadata(
  datasetId: string,
  payload: DatasetMetadataUpdate,
) {
  return apiRequest<DatasetDetail>(datasetMetadataKey(datasetId), {
    method: "PATCH",
    body: payload,
  });
}
