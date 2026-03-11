export type DatasetRecord = Readonly<{
  id: string;
  name: string;
  family: string;
  owner: string;
  updatedAt: string;
  samples: number;
  status: "Ready" | "Queued" | "Review";
  tags: readonly string[];
  previewColumns: readonly string[];
  previewRows: readonly string[][];
  artifacts: readonly string[];
  lineage: readonly string[];
}>;

export const datasetRecords: readonly DatasetRecord[] = [
  {
    id: "fluxonium-2025-031",
    name: "Fluxonium sweep 031",
    family: "Fluxonium",
    owner: "Device Lab",
    updatedAt: "2026-02-26 13:40",
    samples: 184,
    status: "Ready",
    tags: ["sweet-spot", "multi-tone", "validated"],
    previewColumns: ["frequency", "bias", "T1", "fit"],
    previewRows: [
      ["5.812 GHz", "0.120", "18.4 us", "pass"],
      ["5.824 GHz", "0.126", "17.8 us", "pass"],
      ["5.839 GHz", "0.132", "16.2 us", "review"],
    ],
    artifacts: ["raw.h5", "metadata.yaml", "fit-summary.json", "plot-bundle.zip"],
    lineage: ["capture/2026-02-25", "normalize/v2", "fit/transmon-loss", "review/device-lab"],
  },
  {
    id: "transmon-coupler-014",
    name: "Coupler detuning 014",
    family: "Transmon",
    owner: "Modeling",
    updatedAt: "2026-02-24 09:15",
    samples: 76,
    status: "Review",
    tags: ["coupler", "cross-resonance"],
    previewColumns: ["bias", "coupling", "chi", "note"],
    previewRows: [
      ["-0.280", "11.2 MHz", "0.41", "re-fit"],
      ["-0.265", "10.8 MHz", "0.39", "queued"],
    ],
    artifacts: ["detuning.csv", "fit-report.md"],
    lineage: ["import/legacy", "regrid/v1", "fit/manual"],
  },
  {
    id: "resonator-qa-008",
    name: "Resonator QA 008",
    family: "Readout",
    owner: "QA",
    updatedAt: "2026-02-20 18:02",
    samples: 42,
    status: "Queued",
    tags: ["qa", "resonator"],
    previewColumns: ["device", "Q_i", "Q_c", "status"],
    previewRows: [
      ["R04", "2.1e5", "6.3e4", "queued"],
      ["R05", "2.4e5", "5.9e4", "queued"],
    ],
    artifacts: ["staging.json"],
    lineage: ["upload/manual"],
  },
];
