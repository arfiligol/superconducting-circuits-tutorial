import type { CircuitDefinitionSummary } from "@/features/circuit-definition-editor/lib/contracts";

export function parseDefinitionIdParam(value: string | null): number | "new" | null {
  if (!value) {
    return null;
  }

  if (value === "new") {
    return "new";
  }

  const numericValue = Number.parseInt(value, 10);
  return Number.isFinite(numericValue) ? numericValue : null;
}

export function resolveSelectedDefinitionId(
  currentValue: string | null,
  definitions: readonly CircuitDefinitionSummary[] | undefined,
): string | null {
  if (!definitions || definitions.length === 0) {
    return currentValue;
  }

  const parsedValue = parseDefinitionIdParam(currentValue);
  if (parsedValue === "new") {
    return "new";
  }

  if (typeof parsedValue === "number") {
    return definitions.some((definition) => definition.definition_id === parsedValue)
      ? String(parsedValue)
      : String(definitions[0].definition_id);
  }

  return String(definitions[0].definition_id);
}
