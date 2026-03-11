export type DatasetStatus = "Ready" | "Queued" | "Review";

export type DatasetSummary = Readonly<{
  dataset_id: string;
  name: string;
  family: string;
  owner: string;
  updated_at: string;
  samples: number;
  status: DatasetStatus;
}>;

export type DatasetDetail = DatasetSummary &
  Readonly<{
    device_type: string;
    capabilities: readonly string[];
    source: string;
    tags: readonly string[];
    preview_columns: readonly string[];
    preview_rows: readonly (readonly string[])[];
    artifacts: readonly string[];
    lineage: readonly string[];
  }>;

export type DatasetMetadataUpdate = Readonly<{
  device_type: string;
  capabilities: readonly string[];
  source: string;
}>;
