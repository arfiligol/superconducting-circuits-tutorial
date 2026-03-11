import {
  SurfaceHeader,
  SurfacePanel,
  SurfaceTag,
} from "@/features/shared/components/surface-kit";
import {
  schemdrawArtifacts,
  schemdrawNodes,
  schemdrawParameterGroups,
} from "@/features/circuit-schemdraw/lib/mock-data";

export function CircuitSchemdrawWorkspace() {
  return (
    <div className="space-y-4">
      <SurfaceHeader
        eyebrow="Circuit Schemdraw"
        title="Parameter staging and schematic canvas"
        description="Structured shell for translating canonical circuit definitions into annotated schematics and exportable render artifacts."
        actions={
          <>
            <SurfaceTag tone="primary">Render pipeline staging</SurfaceTag>
            <SurfaceTag>Canvas placeholder</SurfaceTag>
          </>
        }
      />

      <section className="grid gap-4 xl:grid-cols-[minmax(0,0.72fr)_minmax(0,1.28fr)]">
        <SurfacePanel
          title="Parameter Rail"
          description="Input groups that later map to schema-derived rendering controls."
        >
          <div className="space-y-4">
            {schemdrawParameterGroups.map((group) => (
              <div key={group.title} className="rounded-2xl border border-border bg-muted/25 p-4">
                <h4 className="text-sm font-semibold">{group.title}</h4>
                <dl className="mt-3 space-y-3 text-sm">
                  {group.fields.map((field) => (
                    <div
                      key={field.label}
                      className="flex items-center justify-between gap-4 rounded-xl border border-border bg-card px-3 py-2"
                    >
                      <dt className="text-muted-foreground">{field.label}</dt>
                      <dd className="font-medium">{field.value}</dd>
                    </div>
                  ))}
                </dl>
              </div>
            ))}

            <div className="rounded-2xl border border-dashed border-border bg-muted/20 p-4 text-sm text-muted-foreground">
              Parameter persistence, drag interactions, and schemdraw execution remain intentionally out of scope for this contributor task.
            </div>
          </div>
        </SurfacePanel>

        <div className="grid gap-4">
          <SurfacePanel
            title="Schematic Canvas"
            description="Expanded result area reserved for the generated diagram and later interaction tooling."
          >
            <div className="relative min-h-[24rem] overflow-hidden rounded-[1.5rem] border border-border bg-[linear-gradient(to_right,color-mix(in_srgb,var(--border)_45%,transparent)_1px,transparent_1px),linear-gradient(to_bottom,color-mix(in_srgb,var(--border)_45%,transparent)_1px,transparent_1px)] bg-[size:2.5rem_2.5rem]">
              {schemdrawNodes.map((node) => (
                <div
                  key={node.label}
                  className="absolute rounded-full border border-primary/30 bg-card px-4 py-2 text-sm font-medium shadow-sm"
                  style={{ left: node.x, top: node.y }}
                >
                  {node.label}
                </div>
              ))}
              <div className="absolute inset-x-[17%] top-[48%] h-px bg-border" />
              <div className="absolute left-[50%] top-[31%] h-[17%] w-px bg-border" />
              <div className="absolute left-[50%] top-[49%] h-[15%] w-px bg-border" />
            </div>
          </SurfacePanel>

          <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,0.8fr)]">
            <SurfacePanel
              title="Generated Notes"
              description="Schema and rendering notes that help validate migration assumptions."
            >
              <ul className="space-y-3 text-sm">
                <li className="rounded-2xl border border-border bg-muted/25 px-4 py-3">
                  Junction and shunt branches map cleanly from canonical element names.
                </li>
                <li className="rounded-2xl border border-border bg-muted/25 px-4 py-3">
                  Port annotations are reserved for the follow-up migration task.
                </li>
                <li className="rounded-2xl border border-border bg-muted/25 px-4 py-3">
                  Export sizes and theme variants can be attached without changing the surface layout.
                </li>
              </ul>
            </SurfacePanel>

            <SurfacePanel
              title="Artifacts"
              description="Expected outputs from the later rendering service."
            >
              <div className="space-y-3 text-sm">
                {schemdrawArtifacts.map((artifact) => (
                  <div
                    key={artifact}
                    className="flex items-center justify-between rounded-2xl border border-border bg-muted/25 px-4 py-3"
                  >
                    <span>{artifact}</span>
                    <SurfaceTag tone="primary">planned</SurfaceTag>
                  </div>
                ))}
              </div>
            </SurfacePanel>
          </div>
        </div>
      </section>
    </div>
  );
}
