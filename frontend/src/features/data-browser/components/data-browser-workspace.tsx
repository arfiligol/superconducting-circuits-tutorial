import { datasetRecords } from "@/features/data-browser/lib/mock-data";
import {
  SurfaceHeader,
  SurfacePanel,
  SurfaceStat,
  SurfaceTag,
} from "@/features/shared/components/surface-kit";

const selectedRecord = datasetRecords[0];

export function DataBrowserWorkspace() {
  return (
    <div className="space-y-4">
      <SurfaceHeader
        eyebrow="Data Browser"
        title="Trace catalogs and dataset inspection"
        description="Master-detail scaffolding for browsing imported datasets, checking lineage, and previewing normalized artifacts before backend wiring lands."
        actions={
          <>
            <SurfaceTag tone="primary">Catalog index ready</SurfaceTag>
            <SurfaceTag>Mock state only</SurfaceTag>
          </>
        }
      />

      <section className="grid gap-4 lg:grid-cols-[minmax(0,1.05fr)_minmax(0,1.4fr)]">
        <SurfacePanel
          title="Dataset Catalog"
          description="Summary list for the imported traces and prepared analysis bundles."
        >
          <div className="grid gap-3 md:grid-cols-3">
            <SurfaceStat label="Datasets" value={String(datasetRecords.length)} tone="primary" />
            <SurfaceStat label="Ready" value="1 active selection" />
            <SurfaceStat label="Owners" value="3 groups" />
          </div>

          <div className="mt-4 overflow-hidden rounded-2xl border border-border">
            <table className="min-w-full border-collapse text-left text-sm">
              <thead className="bg-muted/45 text-xs uppercase tracking-[0.18em] text-muted-foreground">
                <tr>
                  <th className="px-4 py-3">Dataset</th>
                  <th className="px-4 py-3">Family</th>
                  <th className="px-4 py-3">Samples</th>
                  <th className="px-4 py-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {datasetRecords.map((record) => (
                  <tr
                    key={record.id}
                    className={record.id === selectedRecord.id ? "bg-primary/8" : "bg-card"}
                  >
                    <td className="border-t border-border px-4 py-3">
                      <p className="font-medium">{record.name}</p>
                      <p className="mt-1 text-xs text-muted-foreground">{record.updatedAt}</p>
                    </td>
                    <td className="border-t border-border px-4 py-3">{record.family}</td>
                    <td className="border-t border-border px-4 py-3">{record.samples}</td>
                    <td className="border-t border-border px-4 py-3">
                      <SurfaceTag
                        tone={
                          record.status === "Ready"
                            ? "success"
                            : record.status === "Review"
                              ? "warning"
                              : "default"
                        }
                      >
                        {record.status}
                      </SurfaceTag>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </SurfacePanel>

        <div className="grid gap-4">
          <SurfacePanel
            title="Selection Preview"
            description="Detail region for the selected dataset, including metadata, preview rows, and tags."
          >
            <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(0,1.1fr)]">
              <div className="space-y-4">
                <div className="rounded-2xl border border-border bg-muted/30 p-4">
                  <div className="flex flex-wrap gap-2">
                    {selectedRecord.tags.map((tag) => (
                      <SurfaceTag key={tag}>{tag}</SurfaceTag>
                    ))}
                  </div>
                  <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
                    <div>
                      <dt className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                        Dataset ID
                      </dt>
                      <dd className="mt-1 font-medium">{selectedRecord.id}</dd>
                    </div>
                    <div>
                      <dt className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                        Owner
                      </dt>
                      <dd className="mt-1 font-medium">{selectedRecord.owner}</dd>
                    </div>
                    <div>
                      <dt className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                        Family
                      </dt>
                      <dd className="mt-1 font-medium">{selectedRecord.family}</dd>
                    </div>
                    <div>
                      <dt className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                        Sample Count
                      </dt>
                      <dd className="mt-1 font-medium">{selectedRecord.samples}</dd>
                    </div>
                  </dl>
                </div>

                <div className="rounded-2xl border border-border bg-muted/20 p-4">
                  <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                    Preview Columns
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {selectedRecord.previewColumns.map((column) => (
                      <SurfaceTag key={column} tone="primary">
                        {column}
                      </SurfaceTag>
                    ))}
                  </div>
                </div>
              </div>

              <div className="overflow-hidden rounded-2xl border border-border">
                <table className="min-w-full border-collapse text-left text-sm">
                  <thead className="bg-muted/45 text-xs uppercase tracking-[0.18em] text-muted-foreground">
                    <tr>
                      {selectedRecord.previewColumns.map((column) => (
                        <th key={column} className="px-4 py-3">
                          {column}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {selectedRecord.previewRows.map((row, index) => (
                      <tr key={`${selectedRecord.id}-${index}`}>
                        {row.map((value) => (
                          <td key={value} className="border-t border-border px-4 py-3">
                            {value}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </SurfacePanel>

          <div className="grid gap-4 xl:grid-cols-2">
            <SurfacePanel
              title="Artifacts"
              description="Prepared files that later backend endpoints can expose directly."
            >
              <ul className="space-y-3 text-sm">
                {selectedRecord.artifacts.map((artifact) => (
                  <li key={artifact} className="rounded-2xl border border-border bg-muted/25 px-4 py-3">
                    {artifact}
                  </li>
                ))}
              </ul>
            </SurfacePanel>

            <SurfacePanel
              title="Lineage"
              description="Processing chain skeleton for auditability and re-run traceability."
            >
              <ol className="space-y-3 text-sm">
                {selectedRecord.lineage.map((step, index) => (
                  <li
                    key={step}
                    className="flex items-center gap-3 rounded-2xl border border-border bg-muted/25 px-4 py-3"
                  >
                    <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-primary/12 text-xs font-semibold">
                      {index + 1}
                    </span>
                    <span>{step}</span>
                  </li>
                ))}
              </ol>
            </SurfacePanel>
          </div>
        </div>
      </section>
    </div>
  );
}
