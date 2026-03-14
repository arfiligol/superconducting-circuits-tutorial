"use client";

import { useMemo, useState, useTransition } from "react";
import {
  ArrowRight,
  Plus,
  Search,
  Shapes,
  Trash2,
} from "lucide-react";
import { useRouter } from "next/navigation";

import { useCircuitDefinitionEditorData } from "@/features/circuit-definition-editor/hooks/use-circuit-definition-editor-data";
import {
  filterCircuitDefinitionCatalog,
  type CircuitDefinitionCatalogSort,
} from "@/features/circuit-definition-editor/lib/catalog";
import { cx } from "@/features/shared/components/surface-kit";

export function CircuitDefinitionCatalogWorkspace() {
  const router = useRouter();
  const [, startTransition] = useTransition();
  const [searchQuery, setSearchQuery] = useState("");
  const [sortMode, setSortMode] = useState<CircuitDefinitionCatalogSort>("recent");
  const {
    definitions,
    definitionsError,
    isDefinitionsLoading,
    removeDefinition,
    mutationStatus,
  } = useCircuitDefinitionEditorData(null);

  const visibleDefinitions = useMemo(
    () => filterCircuitDefinitionCatalog(definitions, searchQuery, sortMode),
    [definitions, searchQuery, sortMode],
  );

  function openEditor(definitionId: number | "new") {
    const target =
      definitionId === "new"
        ? "/circuit-definition-editor?definitionId=new"
        : `/circuit-definition-editor?definitionId=${definitionId}`;
    startTransition(() => {
      router.push(target);
    });
  }

  function openSchemdraw(definitionId: number) {
    startTransition(() => {
      router.push(`/circuit-schemdraw?definitionId=${definitionId}`);
    });
  }

  async function handleDelete(definitionId: number, definitionName: string) {
    const confirmed = window.confirm(`Delete "${definitionName}"?`);
    if (!confirmed) {
      return;
    }

    await removeDefinition(definitionId);
  }

  return (
    <div className="space-y-6">
      <section className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 className="text-[2.05rem] font-semibold tracking-tight text-foreground">Schemas</h1>
          <p className="mt-2 max-w-4xl text-sm leading-6 text-muted-foreground">
            Browse canonical circuit schemas, start a new authoring flow, or jump into the editor
            and Schemdraw assist surfaces.
          </p>
        </div>
        <button
          type="button"
          onClick={() => {
            openEditor("new");
          }}
          className="inline-flex cursor-pointer items-center gap-2 rounded-md bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground transition hover:opacity-90"
        >
          <Plus className="h-4 w-4" />
          New Circuit
        </button>
      </section>

      {definitionsError ? (
        <div className="rounded-[1rem] border border-rose-500/30 bg-rose-500/8 px-4 py-3 text-sm text-rose-100">
          Unable to load circuit schema catalog. {definitionsError.message}
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

      <section className="rounded-[1rem] border border-border bg-card px-5 py-5 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
        <div className="grid gap-3 border-b border-border/80 pb-4 md:grid-cols-[minmax(0,1fr)_200px]">
          <label className="rounded-[0.9rem] border border-border bg-surface px-4 py-3">
            <span className="mb-2 flex items-center gap-2 text-xs uppercase tracking-[0.16em] text-muted-foreground">
              <Search className="h-3.5 w-3.5" />
              Search
            </span>
            <input
              value={searchQuery}
              onChange={(event) => {
                setSearchQuery(event.target.value);
              }}
              placeholder="Find by name or id"
              className="w-full bg-transparent text-sm text-foreground outline-none placeholder:text-muted-foreground"
            />
          </label>

          <label className="rounded-[0.9rem] border border-border bg-surface px-4 py-3">
            <span className="mb-2 block text-xs uppercase tracking-[0.16em] text-muted-foreground">
              Sort
            </span>
            <select
              value={sortMode}
              onChange={(event) => {
                setSortMode(event.target.value as CircuitDefinitionCatalogSort);
              }}
              className="w-full bg-transparent text-sm text-foreground outline-none"
            >
              <option value="recent">Newest first</option>
              <option value="name">Name A-Z</option>
            </select>
          </label>
        </div>

        <div className="mt-4 flex items-center justify-between gap-3 rounded-[0.9rem] border border-border bg-surface px-4 py-3 text-xs text-muted-foreground">
          <span>
            Showing {visibleDefinitions.length} of {definitions?.length ?? 0} schemas
          </span>
          <span className="rounded-full border border-border px-3 py-1">
            Catalog authority only
          </span>
        </div>

        {isDefinitionsLoading && !definitions ? (
          <div className="mt-4 rounded-[0.9rem] border border-border bg-surface px-4 py-5 text-sm text-muted-foreground">
            Loading circuit schema catalog...
          </div>
        ) : null}

        {visibleDefinitions.length > 0 ? (
          <div className="mt-4 space-y-3">
            {visibleDefinitions.map((definition) => (
              <article
                key={definition.definition_id}
                className="rounded-[1rem] border border-border bg-background px-4 py-4"
              >
                <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="truncate text-base font-semibold text-foreground">
                        {definition.name}
                      </h2>
                      <span
                        className={cx(
                          "rounded-full px-3 py-1 text-[11px] font-medium",
                          definition.validation_status === "warning"
                            ? "bg-amber-500/12 text-amber-300"
                            : "bg-emerald-500/12 text-emerald-300",
                        )}
                      >
                        {definition.validation_status === "warning" ? "Warnings" : "Ready"}
                      </span>
                    </div>
                    <div className="mt-3 flex flex-wrap gap-2 text-[11px] text-muted-foreground">
                      <span className="rounded-full border border-border px-3 py-1">
                        Definition #{definition.definition_id}
                      </span>
                      <span className="rounded-full border border-border px-3 py-1">
                        {definition.element_count} elements
                      </span>
                      <span className="rounded-full border border-border px-3 py-1">
                        {definition.preview_artifact_count} preview artifacts
                      </span>
                    </div>
                    <p className="mt-3 text-xs text-muted-foreground">
                      Created: {definition.created_at}
                    </p>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        openEditor(definition.definition_id);
                      }}
                      className="inline-flex cursor-pointer items-center gap-2 rounded-md border border-border px-3 py-2 text-sm text-foreground transition hover:border-primary/40 hover:bg-primary/10"
                    >
                      <ArrowRight className="h-4 w-4" />
                      Open Editor
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        openSchemdraw(definition.definition_id);
                      }}
                      className="inline-flex cursor-pointer items-center gap-2 rounded-md border border-border px-3 py-2 text-sm text-foreground transition hover:border-primary/40 hover:bg-primary/10"
                    >
                      <Shapes className="h-4 w-4" />
                      Schemdraw
                    </button>
                    <button
                      type="button"
                      aria-label={`Delete ${definition.name}`}
                      onClick={() => {
                        void handleDelete(definition.definition_id, definition.name);
                      }}
                      className="inline-flex h-10 w-10 cursor-pointer items-center justify-center rounded-full border border-rose-500/30 text-rose-300 transition hover:bg-rose-500/10"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        ) : null}

        {!isDefinitionsLoading && visibleDefinitions.length === 0 ? (
          <div className="mt-4 rounded-[0.9rem] border border-dashed border-border bg-surface px-4 py-5 text-sm text-muted-foreground">
            No schemas match the current catalog controls.
          </div>
        ) : null}
      </section>
    </div>
  );
}
