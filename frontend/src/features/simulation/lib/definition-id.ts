import { parseDefinitionIdParam } from "@/features/circuit-definition-editor/lib/definition-id";
import type { CircuitDefinitionSummary } from "@/features/circuit-definition-editor/lib/contracts";

export function parseSimulationDefinitionIdParam(value: string | null): number | null {
  const parsedValue = parseDefinitionIdParam(value);
  return typeof parsedValue === "number" ? parsedValue : null;
}

export function resolveSimulationDefinitionId(
  currentValue: string | null,
  definitions: readonly CircuitDefinitionSummary[] | undefined,
): number | null {
  if (!definitions || definitions.length === 0) {
    return parseSimulationDefinitionIdParam(currentValue);
  }

  const parsedValue = parseSimulationDefinitionIdParam(currentValue);
  if (typeof parsedValue === "number") {
    return definitions.some((definition) => definition.definition_id === parsedValue)
      ? parsedValue
      : definitions[0].definition_id;
  }

  return definitions[0].definition_id;
}
