import { datasetRecords } from "@/features/data-browser/lib/mock-data";

const selectedRecord = datasetRecords[0];

export function DataBrowserWorkspace() {
  return (
    <div className="space-y-8">
      <section className="space-y-6">
        <h1 className="text-[2.05rem] font-semibold tracking-tight text-foreground">Dashboard</h1>

        <div className="flex flex-col gap-3 lg:max-w-xl">
          <div className="flex items-center gap-4">
            <span className="text-base font-semibold text-foreground">Dataset:</span>
            <div className="flex min-h-11 min-w-0 flex-1 items-center justify-between rounded-md border border-border bg-surface px-4 text-sm text-foreground shadow-[inset_0_1px_0_rgba(255,255,255,0.03)]">
              <span className="truncate">{selectedRecord.name}</span>
              <span className="text-muted-foreground">▾</span>
            </div>
          </div>
        </div>
      </section>

      <section className="rounded-[1rem] border border-border bg-card px-4 py-5 shadow-[0_10px_30px_rgba(0,0,0,0.08)] md:px-5">
        <div className="space-y-2">
          <h2 className="text-[1.05rem] font-semibold uppercase tracking-[0.08em] text-foreground">
            Dataset Metadata
          </h2>
          <p className="text-sm text-muted-foreground">
            Device Type: {selectedRecord.deviceType.toLowerCase()} | Capabilities:{" "}
            {selectedRecord.capabilities.length > 0 ? selectedRecord.capabilities.join(", ") : "None"} |
            {" "}Source: {selectedRecord.source}
          </p>
        </div>

        <div className="mt-5 grid gap-3 xl:grid-cols-[minmax(0,1fr)_minmax(0,1.2fr)_auto_auto]">
          <div className="rounded-md border border-border bg-surface px-4 py-2.5">
            <p className="text-xs text-muted-foreground">Device Type</p>
            <div className="mt-1 flex items-center justify-between">
              <span>{selectedRecord.deviceType}</span>
              <span className="text-muted-foreground">▾</span>
            </div>
          </div>
          <div className="rounded-md border border-border bg-surface px-4 py-2.5">
            <p className="text-xs text-muted-foreground">Capabilities</p>
            <div className="mt-1 flex items-center justify-between">
              <span className="truncate">
                {selectedRecord.capabilities.length > 0
                  ? selectedRecord.capabilities.join(", ")
                  : "Capabilities"}
              </span>
              <span className="text-muted-foreground">▾</span>
            </div>
          </div>
          <button
            type="button"
            disabled
            className="rounded-md border border-primary/60 px-4 py-3 text-sm font-medium text-primary"
          >
            Auto Suggest
          </button>
          <button
            type="button"
            disabled
            className="rounded-md bg-primary px-4 py-3 text-sm font-medium text-primary-foreground"
          >
            Save Metadata
          </button>
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-muted-foreground">
          Tagged Core Metrics
        </h2>
        <div className="grid gap-4 xl:grid-cols-[minmax(0,1.2fr)_minmax(360px,0.8fr)]">
          <div className="rounded-[1rem] border border-border bg-card px-5 py-5 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
            <div className="flex min-h-[250px] flex-col items-center justify-center rounded-[0.8rem] border border-border/80 bg-background px-6 py-8 text-center">
              <div className="text-5xl leading-none text-muted-foreground/55">🏷️</div>
              <h3 className="mt-6 text-[2rem] font-semibold text-muted-foreground">No Metrics Tagged</h3>
              <p className="mt-4 max-w-xl text-lg text-muted-foreground">
                Use the Identify Mode tool in the Characterization page to tag key parameters.
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="rounded-[1rem] border border-border bg-card px-5 py-5 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
              <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                Active Dataset Summary
              </h3>
              <dl className="mt-4 space-y-4 text-sm">
                <div>
                  <dt className="text-xs uppercase tracking-[0.16em] text-muted-foreground">Dataset ID</dt>
                  <dd className="mt-1 font-medium text-foreground">{selectedRecord.id}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-[0.16em] text-muted-foreground">Owner</dt>
                  <dd className="mt-1 font-medium text-foreground">{selectedRecord.owner}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-[0.16em] text-muted-foreground">Updated At</dt>
                  <dd className="mt-1 font-medium text-foreground">{selectedRecord.updatedAt}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-[0.16em] text-muted-foreground">Artifacts</dt>
                  <dd className="mt-1 font-medium text-foreground">{selectedRecord.artifacts.length}</dd>
                </div>
              </dl>
            </div>

            <div className="rounded-[1rem] border border-border bg-card px-5 py-5 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
              <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                Preview Rows
              </h3>
              <div className="mt-4 overflow-hidden rounded-[0.8rem] border border-border">
                <table className="min-w-full border-collapse text-left text-sm">
                  <thead className="bg-surface text-xs uppercase tracking-[0.14em] text-muted-foreground">
                    <tr>
                      {selectedRecord.previewColumns.map((column) => (
                        <th key={column} className="px-3 py-3">
                          {column}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {selectedRecord.previewRows.map((row, index) => (
                      <tr key={`${selectedRecord.id}-${index}`} className="bg-card">
                        {row.map((value) => (
                          <td key={value} className="border-t border-border px-3 py-3">
                            {value}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
