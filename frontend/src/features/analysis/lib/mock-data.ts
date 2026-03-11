export type AnalysisCategory = Readonly<{
  title: string;
  count: string;
  focus: string;
}>;

export const analysisCategories: readonly AnalysisCategory[] = [
  { title: "Fitting", count: "4 queues", focus: "nonlinear parameter recovery" },
  { title: "Comparison", count: "3 baselines", focus: "experiment vs reference" },
  { title: "Reporting", count: "2 bundles", focus: "review-ready summaries" },
];

export const fitQueue = [
  { name: "fluxonium_baseline_fit", model: "loss-tangent", status: "ready" },
  { name: "coupler_detuning_fit", model: "cross-resonance", status: "review" },
  { name: "readout_chain_fit", model: "resonator", status: "queued" },
] as const;

export const comparisonRows = [
  ["baseline_a", "0.98", "0.93", "stable"],
  ["baseline_b", "1.04", "0.88", "watch"],
  ["baseline_c", "0.95", "0.90", "stable"],
] as const;
