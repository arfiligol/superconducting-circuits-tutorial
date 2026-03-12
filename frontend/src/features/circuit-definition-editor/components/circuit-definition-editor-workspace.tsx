"use client";

import { useEffect, useTransition } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { FileCode2, LoaderCircle, Plus, Save, Trash2 } from "lucide-react";
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
      router.replace(
        definitionSearchHref(pathname, searchParams.toString(), nextSelection),
        { scroll: false },
      );
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
  const previewArtifacts = activeDefinition?.preview_artifacts ?? [];

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
          className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground"
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
                  "rounded-[1rem] border px-4 py-4 shadow-[0_10px_30px_rgba(0,0,0,0.08)]",
                  isActive ? "border-primary/40 bg-card" : "border-border bg-card",
                )}
              >
                <div className="grid grid-cols-[minmax(0,1fr)_96px] gap-4">
                  <button
                    type="button"
                    onClick={() => {
                      handleReplaceDefinitionIdRequest(String(definition.definition_id));
                    }}
                    className="min-w-0 text-left"
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
                  </button>
                  <div className="flex items-start justify-end gap-2">
                    <button
                      type="button"
                      aria-label={`Delete ${definition.name}`}
                      onClick={() => {
                        void handleDelete(definition.definition_id);
                      }}
                      className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-rose-500/30 text-rose-300 transition hover:bg-rose-500/10"
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
                    <span className="rounded-full bg-surface px-3 py-1">
                      {activeDefinition.element_count} elements
                    </span>
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
                    className="inline-flex items-center gap-2 rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground transition disabled:cursor-not-allowed disabled:opacity-60"
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
                  Normalized Output
                </h2>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">
                  Backend-generated canonical output and validation notices for the selected
                  definition.
                </p>
              </div>
              <div className="rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
                <FileCode2 size={14} className="mr-1 inline-block" />
                Preview
              </div>
            </div>

            <div className="mt-4 rounded-[0.8rem] border border-border bg-background p-4">
              {isActiveDefinitionLoading && selectedDefinitionId !== "new" ? (
                <div className="text-sm text-muted-foreground">Loading normalized output...</div>
              ) : activeDefinitionError ? (
                <div className="text-sm text-rose-200">
                  Unable to load normalized output. {activeDefinitionError.message}
                </div>
              ) : (
                <pre className="m-0 overflow-x-auto text-sm leading-6 text-muted-foreground">
                  {normalizedOutput}
                </pre>
              )}
            </div>

            <div className="mt-4 space-y-3">
              {validationNotices.length === 0 ? (
                <div className="rounded-[0.8rem] border border-border bg-surface px-4 py-3 text-sm text-muted-foreground">
                  Save the definition to generate validation notices.
                </div>
              ) : (
                validationNotices.map((notice) => (
                  <div
                    key={notice.message}
                    className="rounded-[0.8rem] border border-border bg-surface px-4 py-3 text-sm text-foreground"
                  >
                    <span
                      className={cx(
                        "mr-2 inline-flex rounded-full px-2 py-0.5 text-xs font-medium",
                        notice.level === "ok"
                          ? "bg-emerald-500/10 text-emerald-300"
                          : "bg-amber-500/10 text-amber-300",
                      )}
                    >
                      {notice.level === "ok" ? "Pass" : "Pending"}
                    </span>
                    {notice.message}
                  </div>
                ))
              )}
            </div>

            <div className="mt-4 grid gap-3">
              {previewArtifacts.length === 0 ? (
                <div className="rounded-[0.8rem] border border-border bg-surface px-4 py-3 text-sm text-muted-foreground">
                  Preview artifacts will appear after the definition is persisted.
                </div>
              ) : (
                previewArtifacts.map((artifact) => (
                  <div
                    key={artifact}
                    className="flex items-center justify-between rounded-[0.8rem] border border-border bg-surface px-4 py-3 text-sm"
                  >
                    <span>{artifact}</span>
                    <span className="rounded-full bg-primary/10 px-2.5 py-1 text-xs font-medium text-primary">
                      preview
                    </span>
                  </div>
                ))
              )}
            </div>
          </section>
        </div>
      </section>
    </div>
  );
}
