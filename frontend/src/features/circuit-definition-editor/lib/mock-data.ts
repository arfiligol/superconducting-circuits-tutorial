export type DefinitionSection = Readonly<{
  title: string;
  fields: readonly Readonly<{ label: string; value: string }>[];
}>;

export type ValidationNotice = Readonly<{
  level: "ok" | "warning";
  message: string;
}>;

export const definitionSections: readonly DefinitionSection[] = [
  {
    title: "Circuit Metadata",
    fields: [
      { label: "Name", value: "fluxonium_reference_a" },
      { label: "Family", value: "fluxonium" },
      { label: "Revision", value: "draft-04" },
    ],
  },
  {
    title: "Elements",
    fields: [
      { label: "Josephson Junction", value: "EJ = 8.45 GHz" },
      { label: "Shunt Inductor", value: "EL = 0.42 GHz" },
      { label: "Capacitance", value: "EC = 1.22 GHz" },
    ],
  },
  {
    title: "Sweep Context",
    fields: [
      { label: "Flux Bias", value: "0.0 -> 0.5 Phi0" },
      { label: "Temperature", value: "15 mK" },
      { label: "Notes", value: "Baseline migration candidate" },
    ],
  },
];

export const definitionSource = `circuit:\n  name: fluxonium_reference_a\n  family: fluxonium\n  elements:\n    junction:\n      ej_ghz: 8.45\n    shunt_inductor:\n      el_ghz: 0.42\n    capacitance:\n      ec_ghz: 1.22\n  sweep:\n    flux_bias: [0.0, 0.5]\n    temperature_mk: 15\n`;

export const validationNotices: readonly ValidationNotice[] = [
  { level: "ok", message: "Canonical schema matches rewrite draft v1." },
  { level: "ok", message: "All required element blocks are present." },
  { level: "warning", message: "Port mapping metadata still needs migration from legacy forms." },
];

export const previewArtifacts = [
  "definition.normalized.json",
  "schematic-input.yaml",
  "parameter-bundle.toml",
] as const;
