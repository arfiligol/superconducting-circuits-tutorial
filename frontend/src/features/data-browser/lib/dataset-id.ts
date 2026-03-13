import type { DatasetSummary } from "@/features/data-browser/lib/contracts";

export function parseDatasetIdParam(value: string | null): string | null {
  if (!value) {
    return null;
  }

  const normalizedValue = value.trim();
  return normalizedValue.length > 0 ? normalizedValue : null;
}

export function resolveSelectedDatasetId(
  currentValue: string | null,
  datasets: readonly DatasetSummary[] | undefined,
): string | null {
  if (!datasets || datasets.length === 0) {
    return parseDatasetIdParam(currentValue);
  }

  const parsedValue = parseDatasetIdParam(currentValue);
  if (parsedValue && datasets.some((dataset) => dataset.dataset_id === parsedValue)) {
    return parsedValue;
  }

  return datasets[0].dataset_id;
}
