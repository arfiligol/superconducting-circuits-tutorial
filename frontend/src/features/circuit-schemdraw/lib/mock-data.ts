export type SchemdrawParameterGroup = Readonly<{
  title: string;
  fields: readonly Readonly<{ label: string; value: string }>[];
}>;

export const schemdrawParameterGroups: readonly SchemdrawParameterGroup[] = [
  {
    title: "Definition Input",
    fields: [
      { label: "Source", value: "fluxonium_reference_a" },
      { label: "Variant", value: "draft-04" },
      { label: "View", value: "canonical" },
    ],
  },
  {
    title: "Rendering",
    fields: [
      { label: "Orientation", value: "left-to-right" },
      { label: "Labels", value: "expanded" },
      { label: "Ports", value: "annotated" },
    ],
  },
];

export const schemdrawNodes = [
  { label: "Drive", x: "8%", y: "45%" },
  { label: "JJ", x: "30%", y: "45%" },
  { label: "Lsh", x: "50%", y: "28%" },
  { label: "C", x: "50%", y: "62%" },
  { label: "Readout", x: "74%", y: "45%" },
] as const;

export const schemdrawArtifacts = [
  "schematic.svg",
  "schematic.json",
  "label-map.yaml",
] as const;
