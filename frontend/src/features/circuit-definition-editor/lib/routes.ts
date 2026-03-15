export function buildCircuitDefinitionEditorHref(definitionId: number | "new") {
  return definitionId === "new"
    ? "/circuit-definition-editor?definitionId=new"
    : `/circuit-definition-editor?definitionId=${definitionId}`;
}

export function buildCircuitDefinitionCatalogHref() {
  return "/schemas";
}

export function buildCircuitSchemdrawHref(definitionId: number) {
  return `/circuit-schemdraw?definitionId=${definitionId}`;
}
