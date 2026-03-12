"use client";

import { useEffect, useTransition } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  AlertTriangle,
  BadgeCheck,
  FileCode2,
  LoaderCircle,
  PackageOpen,
  Plus,
  Save,
  Trash2,
} from "lucide-react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { Controller, useForm } from "react-hook-form";
import CodeMirror from "@uiw/react-codemirror";
import { yaml } from "@codemirror/lang-yaml";
import { z } from "zod";

import { useCircuitDefinitionEditorData } from "@/features/circuit-definition-editor/hooks/use-circuit-definition-editor-data";
import {
  parseDefinitionIdParam,
  resolveSelectedDefinitionId,
} from "@/features/circuit-definition-editor/lib/definition-id";
import {
  buildNormalizedOutputPreview,
  partitionValidationNotices,
  resolvePersistedPreviewState,
} from "@/features/circuit-definition-editor/lib/preview";
import { cx } from "@/features/shared/components/surface-kit";

const definitionFormSchema = z.object({
  name: z.string().trim().min(1, "Name is required."),
  source_text: z.string().trim().min(1, "Definition source is required."),
});

type DefinitionFormValues = z.infer<typeof definitionFormSchema>;

const emptyDefinitionForm: DefinitionFormValues = {
  name: "",
  source_text: "circuit:\n  name: new_definition\n  family: fluxonium\n  elements:\n",
};

function definitionSearchHref(pathname: string, searchParamsValue: string, definitionId: string) {
  const params = new URLSearchParams(searchParamsValue);
  params.set("definitionId", definitionId);
  return `${pathname}?${params.toString()}`;
}

export function CircuitDefinitionEditorWorkspace() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [isNavigating, startTransition] = useTransition();

  const selectedDefinitionId = parseDefinitionIdParam(searchParams.get("definitionId"));
  const {
    definitions,
    definitionsError,
    isDefinitionsLoading,
    activeDefinition,
    activeDefinitionError,
    isActiveDefinitionLoading,
    mutationStatus,
    saveDefinition,
    removeDefinition,
    clearMutationStatus,
  } = useCircuitDefinitionEditorData(selectedDefinitionId);

  const form = useForm<DefinitionFormValues>({
    resolver: zodResolver(definitionFormSchema),
    defaultValues: emptyDefinitionForm,
  });

  useEffect(() => {
    const nextSelection = resolveSelectedDefinitionId(searchParams.get("definitionId"), definitions);
    if (!nextSelection || nextSelection === searchParams.get("definitionId")) {
      return;
    }

    startTransition(() => {
      router.replace(definitionSearchHref(pathname, searchParams.toString(), nextSelection), {
        scroll: false,
      });
    });
  }, [definitions, pathname, router, searchParams]);

  useEffect(() => {
    if (selectedDefinitionId === "new") {
      form.reset(emptyDefinitionForm);
      return;
    }

    if (activeDefinition) {
      form.reset({
        name: activeDefinition.name,
        source_text: activeDefinition.source_text,
      });
    }
  }, [activeDefinition, selectedDefinitionId, form]);

  const normalizedOutput = activeDefinition?.normalized_output ?? "{\n  \"circuit\": \"pending\"\n}";
  const validationNotices = activeDefinition?.validation_notices ?? [];
  const validationSummary = activeDefinition?.validation_summary ?? null;
  const previewArtifacts = activeDefinition?.preview_artifacts ?? [];
  const persistedPreviewState = resolvePersistedPreviewState({
    selectedDefinitionId,
    isDirty: form.formState.isDirty,
    isSaving: form.formState.isSubmitting,
    activeDefinition,
  });
  const normalizedPreview = buildNormalizedOutputPreview(normalizedOutput);
  const validationGroups = partitionValidationNotices(validationNotices);

  async function onSubmit(values: DefinitionFormValues) {
    const detail = await saveDefinition(values, selectedDefinitionId);
    replaceDefinitionId(String(detail.definition_id));
    form.reset({
      name: detail.name,
      source_text: detail.source_text,
    });
  }

  async function handleDelete(definitionId: number) {
    const confirmed = window.confirm("Delete this circuit definition?");
    if (!confirmed) {
      return;
    }

    await removeDefinition(definitionId);
    const remainingDefinitions = (definitions ?? []).filter(
      (definition) => definition.definition_id !== definitionId,
    );
    const fallbackSelection = remainingDefinitions[0]
      ? String(remainingDefinitions[0].definition_id)
      : "new";
    replaceDefinitionId(fallbackSelection);
  }

  function handleReplaceDefinitionIdRequest(nextId: string) {
    if (nextId === String(selectedDefinitionId)) {
      return;
    }

    if (form.formState.isDirty) {
      const confirmed = window.confirm("You have unsaved changes. Discard them?");
      if (!confirmed) {
        return;
      }
    }

    clearMutationStatus();
    replaceDefinitionId(nextId);
  }

  function startNewDefinition() {
    handleReplaceDefinitionIdRequest("new");
  }

  function discardChanges() {
    if (selectedDefinitionId === "new") {
      form.reset(emptyDefinitionForm);
    } else if (activeDefinition) {
      form.reset({
        name: activeDefinition.name,
        source_text: activeDefinition.source_text,
      });
    }
  }

  const activeDefinitionLabel =
    selectedDefinitionId === "new" ? "New Circuit Definition" : activeDefinition?.name ?? "Loading";

  function replaceDefinitionId(definitionId: string) {
    startTransition(() => {
      router.replace(definitionSearchHref(pathname, searchParams.toString(), definitionId), {
        scroll: false,
      });
    });
  }

  return (
    <div className="space-y-8">
      <section className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-[2.05rem] font-semibold tracking-tight text-foreground">
            Circuit Schemas
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Manage the canonical circuit definitions that feed schemdraw, simulation, and analysis.
          </p>
        </div>
        <button
          type="button"
          onClick={startNewDefinition}
          className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground transition hover:opacity-90"
        >
          <Plus size={16} />
          New Circuit
        </button>
      </section>

      {definitionsError ? (
        <div className="rounded-[1rem] border border-rose-500/30 bg-rose-500/8 px-4 py-3 text-sm text-rose-100">
          Unable to load circuit definitions. {definitionsError.message}
        </div>
      ) : null}

      {mutationStatus.message ? (
        <div
          className={cx(
            "rounded-[1rem] border px-4 py-3 text-sm",
            mutationStatus.state === "error"
              ? "border-rose-500/30 bg-rose-500/8 text-rose-100"
              : "border-primary/30 bg-primary/8 text-foreground",
          )}
        >
          {mutationStatus.message}
        </div>
      ) : null}

      <section className="grid gap-5 xl:grid-cols-[minmax(320px,0.72fr)_minmax(0,1.28fr)]">
        <div className="space-y-4">
          <section className="grid gap-3 xl:grid-cols-[minmax(0,1fr)_160px]">
            <div className="rounded-md border border-border bg-surface px-4 py-3 text-sm text-muted-foreground">
              Canonical Circuit Definitions
            </div>
            <div className="rounded-md border border-border bg-surface px-4 py-3 text-sm text-foreground">
              Created At ▾
            </div>
          </section>

          {isDefinitionsLoading && !definitions ? (
            <div className="rounded-[1rem] border border-border bg-card px-5 py-6 text-sm text-muted-foreground">
              Loading circuit definitions...
            </div>
          ) : null}

          {(definitions ?? []).map((definition) => {
            const isActive = definition.definition_id === selectedDefinitionId;

            return (
              <article
                key={definition.definition_id}
                className={cx(
                  "rounded-[1rem] border px-4 py-4 shadow-[0_10px_30px_rgba(0,0,0,0.08)] transition",
                  isActive
                    ? "border-primary/40 bg-card"
                    : "border-border bg-card hover:border-primary/20",
                )}
              >
                <div className="grid grid-cols-[minmax(0,1fr)_96px] gap-4">
                  <button
                    type="button"
                    onClick={() => {
                      handleReplaceDefinitionIdRequest(String(definition.definition_id));
                    }}
                    className="min-w-0 cursor-pointer text-left transition hover:text-primary"
                  >
                    <h2 className="truncate text-lg font-semibold text-foreground">
                      {definition.name}
                    </h2>
                    <p className="mt-2 text-xs text-muted-foreground">
                      Created: {definition.created_at}
                    </p>
                    <p className="mt-2 text-xs text-muted-foreground">
                      Elements: {definition.element_count}
                    </p>
                    <div className="mt-3 flex flex-wrap gap-2 text-[11px]">
                      <span
                        className={cx(
                          "rounded-full px-3 py-1 font-medium",
                          definition.validation_status === "warning"
                            ? "bg-amber-500/12 text-amber-300"
                            : "bg-emerald-500/12 text-emerald-300",
                        )}
                      >
                        {definition.validation_status === "warning"
                          ? "Warnings present"
                          : "Validation clean"}
                      </span>
                      <span className="rounded-full bg-surface px-3 py-1 text-muted-foreground">
                        {definition.preview_artifact_count} preview artifacts
                      </span>
                    </div>
                  </button>
                  <div className="flex items-start justify-end gap-2">
                    <button
                      type="button"
                      aria-label={`Delete ${definition.name}`}
                      onClick={() => {
                        void handleDelete(definition.definition_id);
                      }}
                      className="inline-flex h-9 w-9 cursor-pointer items-center justify-center rounded-full border border-rose-500/30 text-rose-300 transition hover:bg-rose-500/10"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              </article>
            );
          })}

          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>{definitions?.length ?? 0} schemas · Page 1 / 1</span>
            <div className="rounded-md border border-border bg-surface px-3 py-2">
              rewrite catalog
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <section className="rounded-[1rem] border border-border bg-card px-5 py-5 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
            <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
              <div>
                <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                  Active Schema
                </h2>
                <p className="mt-2 text-lg font-semibold text-foreground">{activeDefinitionLabel}</p>
                <div className="mt-3 flex flex-wrap gap-2 text-xs text-muted-foreground">
                  <span className="rounded-full bg-primary/10 px-3 py-1 text-primary">
                    {selectedDefinitionId === "new"
                      ? "Draft"
                      : `Definition #${activeDefinition?.definition_id ?? "--"}`}
                  </span>
                  {activeDefinition ? (
                    <>
                      <span className="rounded-full bg-surface px-3 py-1">
                        {activeDefinition.element_count} elements
                      </span>
                      <span
                        className={cx(
                          "rounded-full px-3 py-1 font-medium",
                          activeDefinition.validation_status === "warning"
                            ? "bg-amber-500/12 text-amber-300"
                            : "bg-emerald-500/12 text-emerald-300",
                        )}
                      >
                        {activeDefinition.validation_status === "warning"
                          ? `${activeDefinition.validation_summary.warning_count} warning${activeDefinition.validation_summary.warning_count === 1 ? "" : "s"}`
                          : "Validation clean"}
                      </span>
                      <span className="rounded-full bg-surface px-3 py-1">
                        {activeDefinition.preview_artifact_count} artifacts
                      </span>
                    </>
                  ) : null}
                </div>
              </div>
              <div className="grid gap-2 text-right text-xs text-muted-foreground">
                <span>Created At</span>
                <span className="font-medium text-foreground">
                  {activeDefinition?.created_at ?? "Pending save"}
                </span>
              </div>
            </div>
          </section>

          <form
            className="space-y-4"
            onSubmit={(event) => {
              void form.handleSubmit(onSubmit)(event);
            }}
          >
            <section className="rounded-[1rem] border border-border bg-card px-5 py-5 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
              <div className="flex flex-col gap-3 border-b border-border/80 pb-4 md:flex-row md:items-start md:justify-between">
                <div>
                  <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                    Definition Source
                    {form.formState.isDirty ? (
                      <span className="rounded-full bg-amber-500/20 px-2 py-0.5 text-[10px] font-bold normal-case tracking-normal text-amber-500">
                        Unsaved Changes
                      </span>
                    ) : null}
                  </h2>
                  <p className="mt-2 text-sm leading-6 text-muted-foreground">
                    Edit the canonical source text that downstream schematic and simulation tools
                    will consume.
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  {selectedDefinitionId !== "new" ? (
                    <button
                      type="button"
                      onClick={() => {
                        if (selectedDefinitionId && typeof selectedDefinitionId === "number") {
                          void handleDelete(selectedDefinitionId);
                        }
                      }}
                      className="inline-flex items-center gap-2 rounded-md border border-rose-500/30 px-3 py-2 text-sm text-rose-200 transition hover:bg-rose-500/10"
                    >
                      <Trash2 size={14} />
                      Delete
                    </button>
                  ) : null}
                  {form.formState.isDirty ? (
                    <button
                      type="button"
                      onClick={discardChanges}
                      disabled={form.formState.isSubmitting || isNavigating}
                      className="inline-flex items-center gap-2 rounded-md border border-border px-3 py-2 text-sm text-muted-foreground transition hover:bg-surface-elevated disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      Discard
                    </button>
                  ) : null}
                  <button
                    type="submit"
                    disabled={!form.formState.isDirty || form.formState.isSubmitting || isNavigating}
                    className="inline-flex items-center gap-2 rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {form.formState.isSubmitting ? (
                      <LoaderCircle size={14} className="animate-spin" />
                    ) : (
                      <Save size={14} />
                    )}
                    Save
                  </button>
                </div>
              </div>

              <div className="mt-4 grid gap-4">
                <label className="grid gap-2 text-sm">
                  <span className="font-medium text-foreground">Name</span>
                  <input
                    type="text"
                    className="rounded-[0.8rem] border border-border bg-background px-4 py-3 text-sm text-foreground outline-none"
                    {...form.register("name")}
                  />
                  {form.formState.errors.name ? (
                    <span className="text-xs text-rose-300">
                      {form.formState.errors.name.message}
                    </span>
                  ) : null}
                </label>

                <div className="grid gap-2 text-sm">
                  <span className="font-medium text-foreground">Canonical Source</span>
                  <div className="overflow-hidden rounded-[0.8rem] border border-border bg-background">
                    <Controller
                      name="source_text"
                      control={form.control}
                      render={({ field }) => (
                        <CodeMirror
                          value={field.value}
                          height="400px"
                          theme="dark"
                          extensions={[yaml()]}
                          onChange={(value) => field.onChange(value)}
                          className="text-sm leading-6"
                        />
                      )}
                    />
                  </div>
                  {form.formState.errors.source_text ? (
                    <span className="text-xs text-rose-300">
                      {form.formState.errors.source_text.message}
                    </span>
                  ) : null}
                </div>
              </div>
            </section>
          </form>

          <section className="rounded-[1rem] border border-border bg-card px-5 py-5 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
            <div className="flex items-start justify-between gap-3 border-b border-border/80 pb-4">
              <div>
                <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                  Validation & Preview
                </h2>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">
                  Persisted backend validation, normalized output, and preview artifacts for the
                  selected definition.
                </p>
              </div>
              <div
                className={cx(
                  "rounded-full px-3 py-1 text-xs font-medium",
                  persistedPreviewState.tone === "warning"
                    ? "bg-amber-500/12 text-amber-300"
                    : persistedPreviewState.tone === "accent"
                      ? "bg-primary/10 text-primary"
                      : "bg-surface text-muted-foreground",
                )}
              >
                <FileCode2 size={14} className="mr-1 inline-block" />
                {persistedPreviewState.label}
              </div>
            </div>

            <div
              className={cx(
                "mt-4 rounded-[0.8rem] border px-4 py-3 text-sm",
                persistedPreviewState.tone === "warning"
                  ? "border-amber-500/20 bg-amber-500/8 text-amber-100"
                  : persistedPreviewState.tone === "accent"
                    ? "border-primary/20 bg-primary/8 text-foreground"
                    : "border-border bg-surface text-muted-foreground",
              )}
            >
              {persistedPreviewState.detail}
            </div>

            <div className="mt-4 grid gap-3 md:grid-cols-4">
              <div className="rounded-[0.8rem] border border-border bg-surface px-4 py-3">
                <p className="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">
                  Validation Status
                </p>
                <p className="mt-2 text-lg font-semibold text-foreground">
                  {validationSummary
                    ? validationSummary.status === "warning"
                      ? "Warnings Present"
                      : "Ready"
                    : "Pending Save"}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  Persisted result from the backend inspection pipeline
                </p>
              </div>
              <div className="rounded-[0.8rem] border border-border bg-surface px-4 py-3">
                <p className="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">
                  Notice Count
                </p>
                <p className="mt-2 text-lg font-semibold text-foreground">
                  {validationSummary?.notice_count ?? 0}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">Checks and warnings combined</p>
              </div>
              <div className="rounded-[0.8rem] border border-border bg-surface px-4 py-3">
                <p className="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">
                  Warning Count
                </p>
                <p className="mt-2 text-lg font-semibold text-foreground">
                  {validationSummary?.warning_count ?? 0}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">Issues that still need review</p>
              </div>
              <div className="rounded-[0.8rem] border border-border bg-surface px-4 py-3">
                <p className="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">
                  Preview Artifacts
                </p>
                <p className="mt-2 text-lg font-semibold text-foreground">
                  {activeDefinition?.preview_artifact_count ?? previewArtifacts.length}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">Generated from the last save</p>
              </div>
            </div>

            <div className="mt-4 grid gap-4 xl:grid-cols-[minmax(0,0.92fr)_minmax(0,1.08fr)]">
              <section className="rounded-[0.8rem] border border-border bg-surface px-4 py-4">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <h3 className="text-sm font-semibold text-foreground">Validation Notices</h3>
                    <p className="mt-1 text-xs text-muted-foreground">
                      Parse, validation, and preview-readiness feedback from the persisted
                      definition.
                    </p>
                  </div>
                  <div className="rounded-full bg-background px-3 py-1 text-xs text-muted-foreground">
                    {validationSummary?.status === "warning" ? "Needs review" : "Ready"}
                  </div>
                </div>

                {validationNotices.length === 0 ? (
                  <div className="mt-4 rounded-[0.8rem] border border-border bg-background px-4 py-3 text-sm text-muted-foreground">
                    {selectedDefinitionId === "new"
                      ? "Save the draft to generate backend validation notices."
                      : form.formState.isDirty
                        ? "Save the current draft to refresh the persisted validation report."
                        : "No validation notices were returned for this definition."}
                  </div>
                ) : (
                  <div className="mt-4 space-y-4">
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-[0.18em] text-amber-300">
                        <AlertTriangle size={14} />
                        Warnings
                      </div>
                      {validationGroups.warnings.length === 0 ? (
                        <div className="rounded-[0.8rem] border border-emerald-500/20 bg-emerald-500/8 px-4 py-3 text-sm text-emerald-100">
                          No persisted warnings. The current preview slice looks ready for the next
                          workflow step.
                        </div>
                      ) : (
                        validationGroups.warnings.map((notice) => (
                          <div
                            key={`warning-${notice.message}`}
                            className="rounded-[0.8rem] border border-amber-500/20 bg-amber-500/8 px-4 py-3 text-sm text-amber-100"
                          >
                            {notice.message}
                          </div>
                        ))
                      )}
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-[0.18em] text-emerald-300">
                        <BadgeCheck size={14} />
                        Checks
                      </div>
                      {validationGroups.checks.length === 0 ? (
                        <div className="rounded-[0.8rem] border border-border bg-background px-4 py-3 text-sm text-muted-foreground">
                          No passing notices have been recorded yet.
                        </div>
                      ) : (
                        validationGroups.checks.map((notice) => (
                          <div
                            key={`check-${notice.message}`}
                            className="rounded-[0.8rem] border border-emerald-500/20 bg-emerald-500/8 px-4 py-3 text-sm text-emerald-100"
                          >
                            {notice.message}
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                )}
              </section>

              <section className="rounded-[0.8rem] border border-border bg-surface px-4 py-4">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <h3 className="text-sm font-semibold text-foreground">Preview Artifacts</h3>
                    <p className="mt-1 text-xs text-muted-foreground">
                      Generated artifact handles from the persisted preview slice.
                    </p>
                  </div>
                  <div className="rounded-full bg-background px-3 py-1 text-xs text-muted-foreground">
                    {previewArtifacts.length} listed
                  </div>
                </div>

                {previewArtifacts.length === 0 ? (
                  <div className="mt-4 rounded-[0.8rem] border border-border bg-background px-4 py-3 text-sm text-muted-foreground">
                    {selectedDefinitionId === "new"
                      ? "Save this draft to create preview artifacts."
                      : form.formState.isDirty
                        ? "Artifacts still reflect the last saved definition until you save again."
                        : "No preview artifacts were returned for this definition."}
                  </div>
                ) : (
                  <div className="mt-4 grid gap-3">
                    {previewArtifacts.map((artifact, index) => (
                      <div
                        key={artifact}
                        className="flex items-center justify-between rounded-[0.8rem] border border-border bg-background px-4 py-3 text-sm"
                      >
                        <div className="min-w-0">
                          <p className="truncate font-medium text-foreground">{artifact}</p>
                          <p className="mt-1 text-xs text-muted-foreground">
                            Artifact {index + 1} of {previewArtifacts.length}
                          </p>
                        </div>
                        <span className="rounded-full bg-primary/10 px-2.5 py-1 text-xs font-medium text-primary">
                          persisted
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </section>
            </div>

            <section className="mt-4 rounded-[0.8rem] border border-border bg-surface px-4 py-4">
              <div className="flex flex-col gap-3 border-b border-border/80 pb-4 md:flex-row md:items-start md:justify-between">
                <div>
                  <h3 className="text-sm font-semibold text-foreground">Normalized Output</h3>
                  <p className="mt-1 text-xs leading-6 text-muted-foreground">
                    Read-only backend output derived from the last persisted definition. This does
                    not track unsaved editor edits until you save.
                  </p>
                </div>
                <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
                  <span className="rounded-full bg-background px-3 py-1">
                    {normalizedPreview.lineCount} lines
                  </span>
                  <span className="rounded-full bg-background px-3 py-1">
                    {normalizedPreview.fieldCount} top-level fields
                  </span>
                </div>
              </div>

              {activeDefinitionError ? (
                <div className="mt-4 rounded-[0.8rem] border border-rose-500/20 bg-rose-500/8 px-4 py-3 text-sm text-rose-100">
                  Unable to load normalized output. {activeDefinitionError.message}
                </div>
              ) : null}

              {isActiveDefinitionLoading && selectedDefinitionId !== "new" ? (
                <div className="mt-4 rounded-[0.8rem] border border-border bg-background px-4 py-3 text-sm text-muted-foreground">
                  Loading normalized output...
                </div>
              ) : null}

              {!isActiveDefinitionLoading && !activeDefinitionError ? (
                <>
                  {normalizedPreview.isStructured ? (
                    <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                      {normalizedPreview.fields.map((field) => (
                        <div
                          key={field.key}
                          className="rounded-[0.8rem] border border-border bg-background px-4 py-3"
                        >
                          <p className="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">
                            {field.label}
                          </p>
                          <p className="mt-2 text-sm font-medium text-foreground">{field.value}</p>
                        </div>
                      ))}
                    </div>
                  ) : null}

                  <div className="mt-4 rounded-[0.8rem] border border-border bg-background p-4">
                    <pre className="m-0 overflow-x-auto text-sm leading-6 text-muted-foreground">
                      {normalizedPreview.formattedOutput}
                    </pre>
                  </div>
                </>
              ) : null}

              {!normalizedPreview.isStructured && !isActiveDefinitionLoading && !activeDefinitionError ? (
                <div className="mt-3 flex items-center gap-2 rounded-[0.8rem] border border-border bg-background px-4 py-3 text-xs text-muted-foreground">
                  <PackageOpen size={14} />
                  The normalized preview is shown as raw output because it could not be parsed into
                  top-level fields.
                </div>
              ) : null}
            </section>
          </section>
        </div>
      </section>
    </div>
  );
}
