import {
  SurfaceHeader,
  SurfacePanel,
  SurfaceStat,
  SurfaceTag,
} from "@/features/shared/components/surface-kit";
import {
  definitionSections,
  definitionSource,
  previewArtifacts,
  validationNotices,
} from "@/features/circuit-definition-editor/lib/mock-data";

export function CircuitDefinitionEditorWorkspace() {
  return (
    <div className="space-y-4">
      <SurfaceHeader
        eyebrow="Circuit Definition Editor"
        title="Canonical circuit source and preview"
        description="Editor-first skeleton for shaping circuit definitions before they flow into schemdraw and simulation pipelines."
        actions={
          <>
            <SurfaceTag tone="primary">Schema-aware layout</SurfaceTag>
            <SurfaceTag>Read-only mock inputs</SurfaceTag>
          </>
        }
      />

      <section className="grid gap-4 xl:grid-cols-[minmax(0,1.15fr)_minmax(0,0.95fr)]">
        <div className="grid gap-4">
          <SurfacePanel
            title="Source Form"
            description="Migration-ready form sections for the canonical definition model."
          >
            <div className="grid gap-4 lg:grid-cols-3">
              {definitionSections.map((section) => (
                <div key={section.title} className="rounded-2xl border border-border bg-muted/25 p-4">
                  <h4 className="text-sm font-semibold">{section.title}</h4>
                  <dl className="mt-3 space-y-3 text-sm">
                    {section.fields.map((field) => (
                      <div key={field.label}>
                        <dt className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                          {field.label}
                        </dt>
                        <dd className="mt-1 rounded-xl border border-border bg-card px-3 py-2 font-medium">
                          {field.value}
                        </dd>
                      </div>
                    ))}
                  </dl>
                </div>
              ))}
            </div>

            <div className="mt-4 rounded-2xl border border-border bg-muted/20 p-4">
              <label className="text-xs uppercase tracking-[0.16em] text-muted-foreground" htmlFor="definition-source">
                Definition Source
              </label>
              <textarea
                id="definition-source"
                className="mt-3 min-h-72 w-full rounded-2xl border border-border bg-card px-4 py-3 text-sm leading-6 outline-none"
                defaultValue={definitionSource}
                readOnly
              />
            </div>
          </SurfacePanel>
        </div>

        <div className="grid gap-4">
          <SurfacePanel
            title="Validation and Preview"
            description="Expanded preview region for schema checks, normalization outputs, and generated downstream inputs."
          >
            <div className="grid gap-3 md:grid-cols-3">
              <SurfaceStat label="Revision" value="draft-04" tone="primary" />
              <SurfaceStat label="Checks" value="2 pass / 1 pending" />
              <SurfaceStat label="Artifacts" value={String(previewArtifacts.length)} />
            </div>

            <div className="mt-4 space-y-3">
              {validationNotices.map((notice) => (
                <div
                  key={notice.message}
                  className="rounded-2xl border border-border bg-muted/25 px-4 py-3 text-sm"
                >
                  <div className="flex items-center gap-2">
                    <SurfaceTag tone={notice.level === "ok" ? "success" : "warning"}>
                      {notice.level === "ok" ? "Pass" : "Pending"}
                    </SurfaceTag>
                    <span>{notice.message}</span>
                  </div>
                </div>
              ))}
            </div>
          </SurfacePanel>

          <SurfacePanel
            title="Normalized Output"
            description="Future backend wiring can replace these previews with parser output and diff-aware validation."
          >
            <div className="rounded-2xl border border-border bg-muted/20 p-4">
              <pre className="m-0 overflow-x-auto text-sm leading-6 text-muted-foreground">
{`{
  "circuit": "fluxonium_reference_a",
  "elements": 3,
  "ports": "pending migration",
  "schemdraw_ready": true
}`}
              </pre>
            </div>

            <div className="mt-4 grid gap-3">
              {previewArtifacts.map((artifact) => (
                <div
                  key={artifact}
                  className="flex items-center justify-between rounded-2xl border border-border bg-muted/25 px-4 py-3 text-sm"
                >
                  <span>{artifact}</span>
                  <SurfaceTag tone="primary">preview</SurfaceTag>
                </div>
              ))}
            </div>
          </SurfacePanel>
        </div>
      </section>
    </div>
  );
}
