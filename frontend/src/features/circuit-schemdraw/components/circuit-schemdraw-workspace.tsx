import {
  schemdrawArtifacts,
  schemdrawNodes,
  schemdrawParameterGroups,
} from "@/features/circuit-schemdraw/lib/mock-data";

export function CircuitSchemdrawWorkspace() {
  return (
    <div className="space-y-8">
      <section className="space-y-2">
        <h1 className="text-[2.05rem] font-semibold tracking-tight text-foreground">
          Schemdraw Live Preview
        </h1>
        <p className="max-w-4xl text-sm leading-6 text-muted-foreground">
          Write standalone Schemdraw code in WebUI and see SVG updates live. This workspace is
          isolated and does not modify existing schema or simulation pages.
        </p>
      </section>

      <section className="grid gap-5 xl:grid-cols-[minmax(0,0.86fr)_minmax(0,1.14fr)]">
        <div className="rounded-[1rem] border border-border bg-card px-5 py-5 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
          <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-muted-foreground">
            Editor
          </h2>

          <div className="mt-4 space-y-4">
            <div className="rounded-md border border-border bg-surface px-4 py-3">
              <p className="text-xs text-muted-foreground">Linked Schema (optional)</p>
              <div className="mt-1 flex items-center justify-between text-sm text-foreground">
                <span>No linked schema</span>
                <span className="text-muted-foreground">▾</span>
              </div>
            </div>

            <div className="rounded-md border border-border bg-surface px-4 py-3">
              <p className="text-xs text-muted-foreground">Relation Config (JSON)</p>
              <pre className="mt-3 overflow-x-auto text-sm leading-6 text-foreground">
{`{
  "tag": "draft",
  "labels": {
    "P1": "input",
    "R1": "series",
    "C1": "shunt"
  }
}`}
              </pre>
            </div>

            <div className="rounded-[0.8rem] border border-border bg-background">
              <div className="flex border-b border-border">
                <div className="w-14 shrink-0 border-r border-border bg-surface px-3 py-3 text-right text-xs leading-6 text-muted-foreground">
                  {Array.from({ length: 14 }, (_, index) => (
                    <div key={index}>{index + 1}</div>
                  ))}
                </div>
                <div className="min-w-0 flex-1 overflow-x-auto px-4 py-3 text-sm leading-6 text-foreground">
                  <pre className="m-0">
{`import schemdraw
import schemdraw.elements as elm

def build_drawing(relation):
    schema_name = relation.get("schema", {}).get("name") or "No linked schema"
    relation_tag = relation.get("config", {}).get("tag", "draft")

    d = schemdraw.Drawing(canvas="svg", show=False)
    d += elm.SourceSin().label("P1")
    d += elm.Line().right().length(1.2)
    d += elm.Resistor().label("R1")
    d += elm.Line().right().length(1.2)
    d += elm.Capacitor().label("C1")
    d += elm.Line().right().length(0.8)
    d += elm.Ground()
    return d`}
                  </pre>
                </div>
              </div>
            </div>

            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                disabled
                className="rounded-md border border-border bg-surface px-4 py-2.5 text-sm font-medium text-foreground"
              >
                Format
              </button>
              <button
                type="button"
                disabled
                className="rounded-md bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground"
              >
                Render Now
              </button>
              <button
                type="button"
                disabled
                className="rounded-md border border-border bg-surface px-4 py-2.5 text-sm font-medium text-foreground"
              >
                Reset Template
              </button>
            </div>

            <div className="space-y-2 text-sm text-muted-foreground">
              <p>Shortcut: Ctrl/Cmd + Shift + F</p>
              <p>
                Tip: insert <code>probe_here(d, &quot;name&quot;)</code> to record cursor coordinates at
                that line.
              </p>
            </div>

            <div className="space-y-3">
              {schemdrawParameterGroups.map((group) => (
                <div key={group.title} className="rounded-[0.8rem] border border-border bg-surface px-4 py-3">
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                    {group.title}
                  </p>
                  <dl className="mt-3 space-y-2 text-sm">
                    {group.fields.map((field) => (
                      <div key={field.label} className="flex items-center justify-between gap-3">
                        <dt className="text-muted-foreground">{field.label}</dt>
                        <dd className="font-medium text-foreground">{field.value}</dd>
                      </div>
                    ))}
                  </dl>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <section className="rounded-[1rem] border border-border bg-card px-5 py-5 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
            <div className="flex items-center justify-between gap-3">
              <div>
                <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                  Live Preview
                </h2>
                <p className="mt-2 text-sm text-muted-foreground">100%</p>
              </div>
              <div className="flex items-center gap-2">
                <button type="button" disabled className="rounded-md border border-border bg-surface px-3 py-2 text-sm">
                  +
                </button>
                <button type="button" disabled className="rounded-md border border-border bg-surface px-3 py-2 text-sm">
                  -
                </button>
                <button type="button" disabled className="rounded-md border border-border bg-surface px-3 py-2 text-sm">
                  Fit
                </button>
              </div>
            </div>

            <div className="mt-4 space-y-2 text-sm text-muted-foreground">
              <p>Live preview ready.</p>
              <p>Pen cursor: N/A</p>
              <p>Probe points: (none)</p>
            </div>

            <div className="relative mt-4 min-h-[32rem] overflow-hidden rounded-[0.8rem] border border-border bg-background">
              <div className="absolute inset-0 bg-[linear-gradient(to_right,color-mix(in_srgb,var(--border)_45%,transparent)_1px,transparent_1px),linear-gradient(to_bottom,color-mix(in_srgb,var(--border)_45%,transparent)_1px,transparent_1px)] bg-[size:2.5rem_2.5rem]" />
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
          </section>

          <section className="rounded-[1rem] border border-border bg-card px-5 py-5 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
            <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              Relation Context Contract
            </h2>
            <p className="mt-4 text-sm leading-6 text-muted-foreground">
              Use <code>relation[&quot;schema&quot;]</code> for linked schema metadata and{" "}
              <code>relation[&quot;config&quot;]</code> for manual labels and mappings.
            </p>

            <div className="mt-4 space-y-3 text-sm">
              {schemdrawArtifacts.map((artifact) => (
                <div
                  key={artifact}
                  className="flex items-center justify-between rounded-[0.8rem] border border-border bg-surface px-4 py-3"
                >
                  <span>{artifact}</span>
                  <span className="rounded-full bg-primary/10 px-2.5 py-1 text-xs font-medium text-primary">
                    planned
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
