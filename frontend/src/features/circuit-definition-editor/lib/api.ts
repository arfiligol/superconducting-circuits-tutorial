import { apiRequest } from "@/lib/api/client";

import type {
  CircuitDefinitionDetail,
  CircuitDefinitionDraft,
  CircuitDefinitionSummary,
} from "@/features/circuit-definition-editor/lib/contracts";

export const circuitDefinitionsListKey = "/api/backend/circuit-definitions";

export function circuitDefinitionDetailKey(definitionId: number) {
  return `/api/backend/circuit-definitions/${definitionId}`;
}

export async function listCircuitDefinitions() {
  return apiRequest<CircuitDefinitionSummary[]>(circuitDefinitionsListKey);
}

export async function getCircuitDefinition(definitionId: number) {
  return apiRequest<CircuitDefinitionDetail>(circuitDefinitionDetailKey(definitionId));
}

export async function createCircuitDefinition(payload: CircuitDefinitionDraft) {
  return apiRequest<CircuitDefinitionDetail>(circuitDefinitionsListKey, {
    method: "POST",
    body: payload,
  });
}

export async function updateCircuitDefinition(
  definitionId: number,
  payload: CircuitDefinitionDraft,
) {
  return apiRequest<CircuitDefinitionDetail>(circuitDefinitionDetailKey(definitionId), {
    method: "PUT",
    body: payload,
  });
}

export async function deleteCircuitDefinition(definitionId: number) {
  return apiRequest<void>(circuitDefinitionDetailKey(definitionId), {
    method: "DELETE",
  });
}
