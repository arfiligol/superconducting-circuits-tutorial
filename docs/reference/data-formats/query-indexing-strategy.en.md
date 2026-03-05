---
aliases:
  - Query Indexing Strategy
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/data-format
status: stable
owner: docs-team
audience: team
scope: "High-frequency DataRecord/ResultBundle query paths and index strategy (without changing DB architecture direction)"
version: v1.0.0
last_updated: 2026-03-05
updated_by: codex
---

# Query Indexing Strategy

This page defines high-frequency query paths and index strategy to:

1. Keep the current `SQLModel + UnitOfWork + Repository` architecture unchanged.
2. Maintain predictable latency for large-data pages (Raw Data / Characterization).
3. Document priority index candidates before any schema migration.

!!! important "Scope boundary"
    This page is a **query strategy contract**, not a migration script.
    Any new index must still go through the normal DB migration workflow.

## High-Frequency Query Paths

### DataRecord paths (trace-first)

| Repo API | Usage | Primary filter/sort |
|---|---|---|
| `count_by_dataset(dataset_id)` | Characterization/Raw Data scope summary | `dataset_id` |
| `list_distinct_index_for_profile(dataset_id)` | dataset-profile hint inference | `dataset_id` + distinct over `data_type/parameter/representation` |
| `list_index_page_by_dataset(dataset_id, query=...)` | Trace table paging/filtering/sorting | `dataset_id`, `data_type`, `parameter`, `representation`, `mode_filter`, `search`, `sort_by` |

### ResultBundle paths (cache/provenance split)

| Repo API | Usage | Primary filter/sort |
|---|---|---|
| `list_by_dataset(dataset_id)` | all bundles under dataset (debug/provenance) | `dataset_id`, `id` |
| `list_cache_by_dataset(dataset_id)` | simulation cache management | `dataset_id`, `role=cache` |
| `list_provenance_by_dataset(dataset_id)` | UI-visible provenance bundles | `dataset_id`, `role!=cache` |
| `count_by_dataset(..., include_cache=...)` | Source Scope / summary counters | `dataset_id`, `bundle_type`, `role` |
| `list_data_record_index_page(bundle_id, query=...)` | bundle-scoped trace paging | `result_bundle_id` + trace query filters |

## Current Indexed Fields (Model Layer)

Current explicit indexes in `SQLModel`:

- `dataset_records.name`
- `data_records.dataset_id`
- `result_bundle_records.dataset_id`
- `result_bundle_records.bundle_type`
- `result_bundle_records.role`
- `result_bundle_records.status`
- `result_bundle_records.schema_source_hash`
- `result_bundle_records.simulation_setup_hash`

References:
- [`models.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/core/shared/persistence/models.py)
- [`data_record_repository.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/core/shared/persistence/repositories/data_record_repository.py)
- [`result_bundle_repository.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/core/shared/persistence/repositories/result_bundle_repository.py)

## Priority Index Candidates (next phase)

!!! note "Candidates, not mandatory yet"
    Validate these in dedicated migration tasks before applying.

1. `data_records(dataset_id, data_type, parameter, representation)`  
   For multi-filter `list_index_page_by_dataset`.
2. `result_bundle_data_links(result_bundle_id, data_record_id)`  
   For bundle-scoped trace paging joins.
3. `result_bundle_records(dataset_id, role, bundle_type, status)`  
   For provenance/cache summary and listing.

## Monitoring Guidance

1. Track P95 query latency on JTWPA-scale datasets.
2. Log execution time for `count_*` and `list_*_page` APIs.
3. Prioritize compound indexes when `search + mode_filter` combinations regress.

## Related

- [Dataset Record](dataset-record.en.md)
- [Analysis Result](analysis-result.en.md)
- [Characterization UI](../ui/characterization.en.md)
- [Data Handling Guardrail](../guardrails/code-quality/data-handling.en.md)
