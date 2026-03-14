import type { CircuitDefinitionSummary } from "@/features/circuit-definition-editor/lib/contracts";

export type CircuitDefinitionCatalogSort = "recent" | "name";

export function filterCircuitDefinitionCatalog(
  definitions: readonly CircuitDefinitionSummary[] | undefined,
  searchQuery: string,
  sort: CircuitDefinitionCatalogSort,
) {
  const normalizedQuery = searchQuery.trim().toLowerCase();
  const filteredDefinitions = (definitions ?? []).filter((definition) => {
    if (!normalizedQuery) {
      return true;
    }

    return (
      definition.name.toLowerCase().includes(normalizedQuery) ||
      String(definition.definition_id).includes(normalizedQuery)
    );
  });

  const sortedDefinitions = [...filteredDefinitions];
  sortedDefinitions.sort((left, right) => {
    if (sort === "name") {
      return left.name.localeCompare(right.name) || right.created_at.localeCompare(left.created_at);
    }

    return right.created_at.localeCompare(left.created_at);
  });

  return sortedDefinitions;
}
