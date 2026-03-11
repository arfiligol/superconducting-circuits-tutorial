import {
  definitionSource,
  previewArtifacts,
  schemaSummaries,
  validationNotices,
} from "@/features/circuit-definition-editor/lib/mock-data";

export function CircuitDefinitionEditorWorkspace() {
  const activeSchema = schemaSummaries[0];

  return (
    <div className="space-y-8">
      <section className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-[2.05rem] font-semibold tracking-tight text-foreground">
            Circuit Schemas
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Manage your superconducting circuit designs.
          </p>
        </div>
        <button
          type="button"
          disabled
          className="inline-flex items-center rounded-md bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground"
        >
          New Circuit
        </button>
      </section>

      <section className="grid gap-3 xl:grid-cols-[minmax(260px,1fr)_180px_160px]">
        <div className="rounded-md border border-border bg-surface px-4 py-3 text-sm text-muted-foreground">
          Search Schema
        </div>
        <div className="rounded-md border border-border bg-surface px-4 py-3 text-sm text-foreground">
          Created At ▾
        </div>
        <div className="rounded-md border border-border bg-surface px-4 py-3 text-sm text-foreground">
          Descending ▾
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-[minmax(0,0.78fr)_minmax(0,1.22fr)]">
        <div className="space-y-4">
          {schemaSummaries.map((schema, index) => (
            <article
              key={schema.id}
              className={[
                "rounded-[1rem] border px-4 py-4 shadow-[0_10px_30px_rgba(0,0,0,0.08)]",
                index === 0 ? "border-primary/40 bg-card" : "border-border bg-card",
              ].join(" ")}
            >
              <div className="grid grid-cols-[minmax(0,1fr)_96px] gap-4">
                <div>
                  <h2 className="text-lg font-semibold text-foreground">{schema.name}</h2>
                  <p className="mt-2 text-xs text-muted-foreground">Created: {schema.createdAt}</p>
                  <p className="mt-2 text-xs text-muted-foreground">
                    Elements: {schema.elementCount}
                  </p>
                </div>
                <div className="flex items-start justify-end gap-2">
                  <button
                    type="button"
                    disabled
                    className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-primary/40 text-primary"
                  >
                    ✎
                  </button>
                  <button
                    type="button"
                    disabled
                    className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-rose-500/30 text-rose-300"
                  >
                    🗑
                  </button>
                </div>
              </div>
            </article>
          ))}

          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>{schemaSummaries.length} schemas · Page 1 / 1</span>
            <div className="flex items-center gap-2">
              <div className="rounded-md border border-border bg-surface px-3 py-2">12 / page</div>
              <button type="button" disabled className="rounded-md px-3 py-2">
                Prev
              </button>
              <button type="button" disabled className="rounded-md px-3 py-2">
                Next
              </button>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <section className="rounded-[1rem] border border-border bg-card px-5 py-5 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
            <div className="flex items-center justify-between gap-3">
              <div>
                <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                  Active Schema
                </h2>
                <p className="mt-2 text-lg font-semibold text-foreground">{activeSchema.name}</p>
              </div>
              <div className="rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
                Preview
              </div>
            </div>
          </section>

          <section className="rounded-[1rem] border border-border bg-card px-5 py-5 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
            <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              Definition Source
            </h2>
            <textarea
              id="definition-source"
              className="mt-4 min-h-80 w-full rounded-[0.8rem] border border-border bg-background px-4 py-3 text-sm leading-6 text-foreground outline-none"
              defaultValue={definitionSource}
              readOnly
            />
          </section>

          <section className="rounded-[1rem] border border-border bg-card px-5 py-5 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
            <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              Normalized Output
            </h2>
            <div className="mt-4 rounded-[0.8rem] border border-border bg-background p-4">
              <pre className="m-0 overflow-x-auto text-sm leading-6 text-muted-foreground">
{`{
  "circuit": "fluxonium_reference_a",
  "elements": 3,
  "ports": "pending migration",
  "schemdraw_ready": true
}`}
              </pre>
            </div>

            <div className="mt-4 space-y-3">
              {validationNotices.map((notice) => (
                <div
                  key={notice.message}
                  className="rounded-[0.8rem] border border-border bg-surface px-4 py-3 text-sm text-foreground"
                >
                  <span
                    className={[
                      "mr-2 inline-flex rounded-full px-2 py-0.5 text-xs font-medium",
                      notice.level === "ok"
                        ? "bg-emerald-500/10 text-emerald-300"
                        : "bg-amber-500/10 text-amber-300",
                    ].join(" ")}
                  >
                    {notice.level === "ok" ? "Pass" : "Pending"}
                  </span>
                  {notice.message}
                </div>
              ))}
            </div>

            <div className="mt-4 grid gap-3">
              {previewArtifacts.map((artifact) => (
                <div
                  key={artifact}
                  className="flex items-center justify-between rounded-[0.8rem] border border-border bg-surface px-4 py-3 text-sm"
                >
                  <span>{artifact}</span>
                  <span className="rounded-full bg-primary/10 px-2.5 py-1 text-xs font-medium text-primary">
                    preview
                  </span>
                </div>
              ))}
            </div>
          </section>
        </div>
      </section>
    </div>
  );
}
