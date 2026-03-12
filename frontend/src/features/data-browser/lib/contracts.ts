import { components } from "@/lib/api/generated/schema";

export type DatasetStatus = "Ready" | "Queued" | "Review";

export type DatasetSummary = components["schemas"]["DatasetSummaryResponse"];

export type DatasetDetail = components["schemas"]["DatasetDetailResponse"];

export type DatasetMetadataUpdate = components["schemas"]["DatasetMetadataUpdateRequest"];

