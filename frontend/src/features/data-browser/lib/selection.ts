import type { DesignBrowseRow, TraceMetadataRow } from "@/features/data-browser/lib/contracts";

export function resolveSelectedDesignId(
  selectedDesignId: string | null,
  rows: readonly DesignBrowseRow[] | undefined,
) {
  if (!rows || rows.length === 0) {
    return null;
  }
  if (selectedDesignId && rows.some((row) => row.design_id === selectedDesignId)) {
    return selectedDesignId;
  }
  return rows[0]?.design_id ?? null;
}

export function resolveSelectedTraceId(
  selectedTraceId: string | null,
  rows: readonly TraceMetadataRow[] | undefined,
) {
  if (!rows || rows.length === 0) {
    return null;
  }
  if (selectedTraceId && rows.some((row) => row.trace_id === selectedTraceId)) {
    return selectedTraceId;
  }
  return rows[0]?.trace_id ?? null;
}
