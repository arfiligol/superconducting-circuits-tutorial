import { apiRequest } from "@/lib/api/client";

import type {
  CircuitDefinitionDetail,
  CircuitDefinitionDraft,
  CircuitDefinitionMutationResponse,
  CircuitDefinitionSummary,
} from "@/features/circuit-definition-editor/lib/contracts";

export const circuitDefinitionsListKey = "/api/backend/circuit-definitions";

export function circuitDefinitionDetailKey(definitionId: number) {
  return `/api/backend/circuit-definitions/${definitionId}`;
}

export function unwrapCircuitDefinitionMutation(
  response: CircuitDefinitionMutationResponse,
): CircuitDefinitionDetail {
  return response.definition;
}

export async function listCircuitDefinitions() {
  return apiRequest<CircuitDefinitionSummary[]>(circuitDefinitionsListKey);
}

export async function getCircuitDefinition(definitionId: number) {
  return apiRequest<CircuitDefinitionDetail>(circuitDefinitionDetailKey(definitionId));
}

export async function createCircuitDefinition(payload: CircuitDefinitionDraft) {
  const response = await apiRequest<CircuitDefinitionMutationResponse>(circuitDefinitionsListKey, {
    method: "POST",
    body: payload,
  });

  return unwrapCircuitDefinitionMutation(response);
}

export async function updateCircuitDefinition(
  definitionId: number,
  payload: CircuitDefinitionDraft,
) {
  const response = await apiRequest<CircuitDefinitionMutationResponse>(
    circuitDefinitionDetailKey(definitionId),
    {
      method: "PUT",
      body: payload,
    },
  );

  return unwrapCircuitDefinitionMutation(response);
}

export async function deleteCircuitDefinition(definitionId: number) {
  return apiRequest<void>(circuitDefinitionDetailKey(definitionId), {
    method: "DELETE",
  });
}
