"use client";

import { useEffect, useTransition } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { Database, LoaderCircle, Save } from "lucide-react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { useDataBrowserData } from "@/features/data-browser/hooks/use-data-browser-data";
import { parseDatasetIdParam } from "@/features/data-browser/lib/dataset-id";
import type {
  DatasetDetail,
  DatasetStatus,
  DatasetSummary,
} from "@/features/data-browser/lib/contracts";
import {
  SurfacePanel,
  SurfaceStat,
  SurfaceTag,
  cx,
} from "@/features/shared/components/surface-kit";

const metadataFormSchema = z.object({
  device_type: z.string().trim().min(1, "Device type is required."),
  capabilities_text: z.string().trim(),
  source: z.string().trim().min(1, "Source is required."),
});

type MetadataFormValues = z.infer<typeof metadataFormSchema>;

const emptyMetadataForm: MetadataFormValues = {
  device_type: "",
  capabilities_text: "",
  source: "",
};

function datasetSearchHref(pathname: string, searchParamsValue: string, datasetId: string) {
  const params = new URLSearchParams(searchParamsValue);
  params.set("datasetId", datasetId);
  return `${pathname}?${params.toString()}`;
}

function detailToFormValues(detail: DatasetDetail): MetadataFormValues {
  return {
    device_type: detail.device_type,
    capabilities_text: detail.capabilities.join(", "),
    source: detail.source,
  };
}

function parseCapabilities(value: string) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter((item) => item.length > 0);
}

function formatList(values: readonly string[], fallback = "None") {
  return values.length > 0 ? values.join(", ") : fallback;
}

function statusTone(status: DatasetStatus) {
  if (status === "Ready") {
    return "success" as const;
  }

  if (status === "Review") {
    return "warning" as const;
  }

  return "default" as const;
}

type MetadataFieldProps = Readonly<{
  label: string;
  error?: string;
  children: React.ReactNode;
}>;

function MetadataField({ label, error, children }: MetadataFieldProps) {
  return (
    <label className="block rounded-md border border-border bg-surface px-4 py-3">
      <span className="text-xs uppercase tracking-[0.16em] text-muted-foreground">{label}</span>
      <div className="mt-2">{children}</div>
      {error ? <p className="mt-2 text-xs text-rose-300">{error}</p> : null}
    </label>
  );
}

function DatasetCatalogCard({
  dataset,
  active,
  onSelect,
}: Readonly<{
  dataset: DatasetSummary;
  active: boolean;
  onSelect: (datasetId: string) => void;
}>) {
  return (
    <button
      type="button"
      onClick={() => {
        onSelect(dataset.dataset_id);
      }}
      className={cx(
        "w-full rounded-[1rem] border px-4 py-4 text-left shadow-[0_10px_30px_rgba(0,0,0,0.08)] transition",
        active ? "border-primary/40 bg-card" : "border-border bg-card hover:border-primary/25",
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="truncate text-base font-semibold text-foreground">{dataset.name}</h3>
          <p className="mt-1 text-xs uppercase tracking-[0.14em] text-muted-foreground">
            {dataset.family}
          </p>
        </div>
        <SurfaceTag tone={statusTone(dataset.status)}>{dataset.status}</SurfaceTag>
      </div>
      <div className="mt-4 grid gap-2 text-xs text-muted-foreground sm:grid-cols-2">
        <span>Owner: {dataset.owner}</span>
        <span>Samples: {dataset.samples}</span>
        <span className="sm:col-span-2">Updated: {dataset.updated_at}</span>
      </div>
    </button>
  );
}

export function DataBrowserWorkspace() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [isNavigating, startTransition] = useTransition();

  const rawDatasetId = parseDatasetIdParam(searchParams.get("datasetId"));
  const {
    datasets,
    datasetsError,
    isDatasetsLoading,
    resolvedDatasetId,
    activeDataset,
    activeDatasetError,
    isActiveDatasetLoading,
    mutationStatus,
    saveMetadata,
    clearMutationStatus,
  } = useDataBrowserData(rawDatasetId);
  const selectedDatasetSummary = datasets?.find((dataset) => dataset.dataset_id === resolvedDatasetId);

  const form = useForm<MetadataFormValues>({
    resolver: zodResolver(metadataFormSchema),
    defaultValues: emptyMetadataForm,
  });

  useEffect(() => {
    if (!resolvedDatasetId || resolvedDatasetId === rawDatasetId) {
      return;
    }

    startTransition(() => {
      router.replace(datasetSearchHref(pathname, searchParams.toString(), resolvedDatasetId), {
        scroll: false,
      });
    });
  }, [pathname, rawDatasetId, resolvedDatasetId, router, searchParams]);

  useEffect(() => {
    if (activeDataset) {
      form.reset(detailToFormValues(activeDataset));
      return;
    }

    if (!resolvedDatasetId) {
      form.reset(emptyMetadataForm);
    }
  }, [activeDataset, form, resolvedDatasetId]);

  async function onSubmit(values: MetadataFormValues) {
    const detail = await saveMetadata({
      device_type: values.device_type.trim(),
      capabilities: parseCapabilities(values.capabilities_text),
      source: values.source.trim(),
    });

    form.reset(detailToFormValues(detail));
  }

  function replaceDatasetId(datasetId: string) {
    clearMutationStatus();
    startTransition(() => {
      router.replace(datasetSearchHref(pathname, searchParams.toString(), datasetId), {
        scroll: false,
      });
    });
  }

  const readyCount = (datasets ?? []).filter((dataset) => dataset.status === "Ready").length;
  const hasActiveDataset = Boolean(activeDataset);
  const isSaveDisabled =
    !hasActiveDataset ||
    isActiveDatasetLoading ||
    mutationStatus.state === "saving" ||
    !form.formState.isDirty;

  return (
    <div className="space-y-8">
      <section className="space-y-6">
        <div>
          <h1 className="text-[2.05rem] font-semibold tracking-tight text-foreground">Dashboard</h1>
          <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
            Browse rewrite datasets, inspect preview payloads, and update catalog metadata without
            leaving the workspace shell.
          </p>
        </div>

        <div className="grid gap-4 xl:grid-cols-[minmax(0,1.2fr)_minmax(180px,0.4fr)_minmax(180px,0.4fr)]">
          <div className="flex items-center gap-4 rounded-[1rem] border border-border bg-card px-4 py-4 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
            <span className="text-base font-semibold text-foreground">Dataset</span>
            <div className="min-w-0 flex-1">
              <select
                value={resolvedDatasetId ?? ""}
                onChange={(event) => {
                  replaceDatasetId(event.target.value);
                }}
                disabled={isDatasetsLoading || !datasets || datasets.length === 0 || isNavigating}
                className="min-h-11 w-full rounded-md border border-border bg-surface px-4 text-sm text-foreground"
              >
                <option value="" disabled>
                  {isDatasetsLoading ? "Loading datasets..." : "Select a dataset"}
                </option>
                {(datasets ?? []).map((dataset) => (
                  <option key={dataset.dataset_id} value={dataset.dataset_id}>
                    {dataset.name}
                  </option>
                ))}
              </select>
            </div>
            {isNavigating ? (
              <LoaderCircle className="h-4 w-4 animate-spin text-muted-foreground" />
            ) : null}
          </div>
          <SurfaceStat label="Catalog Rows" value={String(datasets?.length ?? 0)} />
          <SurfaceStat label="Ready" value={String(readyCount)} tone="primary" />
        </div>
      </section>

      {datasetsError ? (
        <div className="rounded-[1rem] border border-rose-500/30 bg-rose-500/8 px-4 py-3 text-sm text-rose-100">
          Unable to load the dataset catalog. {datasetsError.message}
        </div>
      ) : null}

      <section className="grid gap-5 xl:grid-cols-[minmax(320px,0.74fr)_minmax(0,1.26fr)]">
        <SurfacePanel
          title="Dataset Catalog"
          description="Summary rows come from the rewrite catalog API and drive the detail panel selection."
        >
          {isDatasetsLoading && !datasets ? (
            <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-5 text-sm text-muted-foreground">
              Loading dataset summaries...
            </div>
          ) : null}

          {!isDatasetsLoading && (datasets?.length ?? 0) === 0 ? (
            <div className="rounded-[0.9rem] border border-dashed border-border bg-surface px-4 py-5 text-sm text-muted-foreground">
              No datasets are available from the rewrite catalog yet.
            </div>
          ) : null}

          <div className="space-y-3">
            {(datasets ?? []).map((dataset) => (
              <DatasetCatalogCard
                key={dataset.dataset_id}
                dataset={dataset}
                active={dataset.dataset_id === resolvedDatasetId}
                onSelect={replaceDatasetId}
              />
            ))}
          </div>
        </SurfacePanel>

        <SurfacePanel
          title="Dataset Metadata"
          description="Update device type, capabilities, and provenance source using the datasets metadata patch endpoint."
          actions={
            hasActiveDataset ? (
              <div className="flex flex-wrap items-center gap-2">
                <SurfaceTag tone="primary">{selectedDatasetSummary?.family ?? activeDataset?.family}</SurfaceTag>
                <SurfaceTag tone={statusTone(activeDataset?.status ?? selectedDatasetSummary?.status ?? "Queued")}>
                  {activeDataset?.status ?? selectedDatasetSummary?.status ?? "Queued"}
                </SurfaceTag>
              </div>
            ) : null
          }
        >
          {activeDatasetError ? (
            <div className="rounded-[0.9rem] border border-rose-500/30 bg-rose-500/8 px-4 py-3 text-sm text-rose-100">
              Unable to load dataset detail. {activeDatasetError.message}
            </div>
          ) : null}

          {mutationStatus.message ? (
            <div
              className={cx(
                "mb-4 rounded-[0.9rem] border px-4 py-3 text-sm",
                mutationStatus.state === "error"
                  ? "border-rose-500/30 bg-rose-500/8 text-rose-100"
                  : "border-primary/30 bg-primary/8 text-foreground",
              )}
            >
              {mutationStatus.message}
            </div>
          ) : null}

          {isActiveDatasetLoading && resolvedDatasetId ? (
            <div className="flex items-center gap-3 rounded-[0.9rem] border border-border bg-surface px-4 py-4 text-sm text-muted-foreground">
              <LoaderCircle className="h-4 w-4 animate-spin" />
              Loading dataset metadata...
            </div>
          ) : null}

          {!resolvedDatasetId && !isDatasetsLoading ? (
            <div className="rounded-[0.9rem] border border-dashed border-border bg-surface px-4 py-5 text-sm text-muted-foreground">
              Select a dataset to inspect its metadata and preview payload.
            </div>
          ) : null}

          <form className="space-y-4" onSubmit={form.handleSubmit(onSubmit)}>
            <div className="grid gap-3 xl:grid-cols-[minmax(0,1fr)_minmax(0,1.2fr)]">
              <MetadataField
                label="Device Type"
                error={form.formState.errors.device_type?.message}
              >
                <input
                  {...form.register("device_type")}
                  disabled={!hasActiveDataset || isActiveDatasetLoading}
                  className="w-full bg-transparent text-sm text-foreground outline-none placeholder:text-muted-foreground"
                  placeholder="Fluxonium"
                />
              </MetadataField>

              <MetadataField
                label="Capabilities"
                error={form.formState.errors.capabilities_text?.message}
              >
                <input
                  {...form.register("capabilities_text")}
                  disabled={!hasActiveDataset || isActiveDatasetLoading}
                  className="w-full bg-transparent text-sm text-foreground outline-none placeholder:text-muted-foreground"
                  placeholder="cross-resonance, sweet-spot"
                />
              </MetadataField>
            </div>

            <div className="grid gap-3 xl:grid-cols-[minmax(0,1fr)_auto_auto]">
              <MetadataField label="Source" error={form.formState.errors.source?.message}>
                <input
                  {...form.register("source")}
                  disabled={!hasActiveDataset || isActiveDatasetLoading}
                  list="dataset-source-options"
                  className="w-full bg-transparent text-sm text-foreground outline-none placeholder:text-muted-foreground"
                  placeholder="inferred"
                />
                <datalist id="dataset-source-options">
                  <option value="inferred" />
                  <option value="imported" />
                  <option value="uploaded" />
                  <option value="manual" />
                </datalist>
              </MetadataField>

              <button
                type="button"
                disabled
                className="rounded-md border border-primary/60 px-4 py-3 text-sm font-medium text-primary disabled:opacity-60"
              >
                Auto Suggest
              </button>

              <button
                type="submit"
                disabled={isSaveDisabled}
                className="inline-flex items-center justify-center gap-2 rounded-md bg-primary px-4 py-3 text-sm font-medium text-primary-foreground disabled:cursor-not-allowed disabled:opacity-60"
              >
                {mutationStatus.state === "saving" ? (
                  <LoaderCircle className="h-4 w-4 animate-spin" />
                ) : (
                  <Save className="h-4 w-4" />
                )}
                Save Metadata
              </button>
            </div>

            {activeDataset ? (
              <div className="rounded-[0.9rem] border border-border/80 bg-surface px-4 py-4 text-sm text-muted-foreground">
                Device Type: {activeDataset.device_type.toLowerCase()} | Capabilities:{" "}
                {formatList(activeDataset.capabilities)} | Source: {activeDataset.source}
              </div>
            ) : null}
          </form>
        </SurfacePanel>
      </section>

      <section className="space-y-4">
        <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-muted-foreground">
          Tagged Core Metrics
        </h2>
        <div className="grid gap-4 xl:grid-cols-[minmax(0,1.2fr)_minmax(360px,0.8fr)]">
          <SurfacePanel
            title="Tag Coverage"
            description="Review the tag payload that travels with the selected dataset detail."
          >
            {activeDataset?.tags.length ? (
              <div className="flex flex-wrap gap-2">
                {activeDataset.tags.map((tag) => (
                  <SurfaceTag key={tag}>{tag}</SurfaceTag>
                ))}
              </div>
            ) : (
              <div className="flex min-h-[250px] flex-col items-center justify-center rounded-[0.8rem] border border-border/80 bg-background px-6 py-8 text-center">
                <Database className="h-12 w-12 text-muted-foreground/55" />
                <h3 className="mt-6 text-[2rem] font-semibold text-muted-foreground">
                  No Metrics Tagged
                </h3>
                <p className="mt-4 max-w-xl text-lg text-muted-foreground">
                  Use the Identify Mode tool in the Characterization page to tag key parameters.
                </p>
              </div>
            )}
          </SurfacePanel>

          <div className="space-y-4">
            <SurfacePanel
              title="Active Dataset Summary"
              description="Detail payload stays separate from the summary catalog so the browser only loads heavy data on selection."
            >
              {activeDataset ? (
                <div className="space-y-5 text-sm">
                  <dl className="grid gap-4 md:grid-cols-2">
                    <div>
                      <dt className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                        Dataset ID
                      </dt>
                      <dd className="mt-1 font-medium text-foreground">{activeDataset.dataset_id}</dd>
                    </div>
                    <div>
                      <dt className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                        Owner
                      </dt>
                      <dd className="mt-1 font-medium text-foreground">{activeDataset.owner}</dd>
                    </div>
                    <div>
                      <dt className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                        Updated At
                      </dt>
                      <dd className="mt-1 font-medium text-foreground">{activeDataset.updated_at}</dd>
                    </div>
                    <div>
                      <dt className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                        Samples
                      </dt>
                      <dd className="mt-1 font-medium text-foreground">{activeDataset.samples}</dd>
                    </div>
                  </dl>

                  <div>
                    <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                      Artifacts
                    </p>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {activeDataset.artifacts.map((artifact) => (
                        <SurfaceTag key={artifact}>{artifact}</SurfaceTag>
                      ))}
                    </div>
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                      Lineage
                    </p>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {activeDataset.lineage.map((step) => (
                        <SurfaceTag key={step} tone="primary">
                          {step}
                        </SurfaceTag>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">
                  Dataset summary details appear here after a catalog selection.
                </p>
              )}
            </SurfacePanel>

            <SurfacePanel
              title="Preview Rows"
              description="Preview data is requested from the detail endpoint only for the active dataset."
            >
              {activeDataset?.preview_rows.length ? (
                <div className="overflow-hidden rounded-[0.8rem] border border-border">
                  <table className="min-w-full border-collapse text-left text-sm">
                    <thead className="bg-surface text-xs uppercase tracking-[0.14em] text-muted-foreground">
                      <tr>
                        {activeDataset.preview_columns.map((column) => (
                          <th key={column} className="px-3 py-3">
                            {column}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {activeDataset.preview_rows.map((row, index) => (
                        <tr
                          key={`${activeDataset.dataset_id}-${index}`}
                          className="bg-card align-top"
                        >
                          {row.map((value, valueIndex) => (
                            <td
                              key={`${activeDataset.preview_columns[valueIndex]}-${value}`}
                              className="border-t border-border px-3 py-3"
                            >
                              {value}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">
                  No preview rows are available for the current dataset.
                </p>
              )}
            </SurfacePanel>
          </div>
        </div>
      </section>
    </div>
  );
}
