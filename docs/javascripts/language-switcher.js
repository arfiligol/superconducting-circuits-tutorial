/*
 * Native Single-Build Bilingual Pages switcher.
 *
 * Zensical only supports site-level `extra.alternate` links natively.
 * This script upgrades the language selector to point at the paired
 * `.md` / `.en.md` page when a real counterpart exists.
 * Refresh the route map whenever bilingual source paths are added, removed,
 * or renamed.
 */

const LANGUAGE_ROUTE_MAP = Object.freeze({
  "": "index.en/",
  "about.en/": "about/",
  "about/": "about.en/",
  "explanation/": "explanation/index.en/",
  "explanation/architecture/": "explanation/architecture/index.en/",
  "explanation/architecture/circuit-simulation/": "explanation/architecture/circuit-simulation/index.en/",
  "explanation/architecture/circuit-simulation/index.en/": "explanation/architecture/circuit-simulation/",
  "explanation/architecture/design-decisions/": "explanation/architecture/design-decisions/index.en/",
  "explanation/architecture/design-decisions/clean-architecture.en/": "explanation/architecture/design-decisions/clean-architecture/",
  "explanation/architecture/design-decisions/clean-architecture/": "explanation/architecture/design-decisions/clean-architecture.en/",
  "explanation/architecture/design-decisions/index.en/": "explanation/architecture/design-decisions/",
  "explanation/architecture/design-decisions/schema-design.en/": "explanation/architecture/design-decisions/schema-design/",
  "explanation/architecture/design-decisions/schema-design/": "explanation/architecture/design-decisions/schema-design.en/",
  "explanation/architecture/design-decisions/visualization-backend.en/": "explanation/architecture/design-decisions/visualization-backend/",
  "explanation/architecture/design-decisions/visualization-backend/": "explanation/architecture/design-decisions/visualization-backend.en/",
  "explanation/architecture/index.en/": "explanation/architecture/",
  "explanation/architecture/pipeline/": "explanation/architecture/pipeline/index.en/",
  "explanation/architecture/pipeline/data-flow.en/": "explanation/architecture/pipeline/data-flow/",
  "explanation/architecture/pipeline/data-flow/": "explanation/architecture/pipeline/data-flow.en/",
  "explanation/architecture/pipeline/index.en/": "explanation/architecture/pipeline/",
  "explanation/architecture/pipeline/preprocessing-rationale.en/": "explanation/architecture/pipeline/preprocessing-rationale/",
  "explanation/architecture/pipeline/preprocessing-rationale/": "explanation/architecture/pipeline/preprocessing-rationale.en/",
  "explanation/index.en/": "explanation/",
  "explanation/physics/": "explanation/physics/index.en/",
  "explanation/physics/index.en/": "explanation/physics/",
  "explanation/physics/symbol-glossary.en/": "explanation/physics/symbol-glossary/",
  "explanation/physics/symbol-glossary/": "explanation/physics/symbol-glossary.en/",
  "how-to/": "how-to/index.en/",
  "how-to/cli/": "how-to/cli/index.en/",
  "how-to/cli/index.en/": "how-to/cli/",
  "how-to/contributing.en/": "how-to/contributing/",
  "how-to/contributing/": "how-to/contributing.en/",
  "how-to/contributing/circuit-diagrams.en/": "how-to/contributing/circuit-diagrams/",
  "how-to/contributing/circuit-diagrams/": "how-to/contributing/circuit-diagrams.en/",
  "how-to/contributing/cli-docs-automation.en/": "how-to/contributing/cli-docs-automation/",
  "how-to/contributing/cli-docs-automation/": "how-to/contributing/cli-docs-automation.en/",
  "how-to/extend/": "how-to/extend/index.en/",
  "how-to/extend/add-data-source.en/": "how-to/extend/add-data-source/",
  "how-to/extend/add-data-source/": "how-to/extend/add-data-source.en/",
  "how-to/extend/extend-julia-functions.en/": "how-to/extend/extend-julia-functions/",
  "how-to/extend/extend-julia-functions/": "how-to/extend/extend-julia-functions.en/",
  "how-to/extend/index.en/": "how-to/extend/",
  "how-to/fit-model/squid.en/": "how-to/fit-model/squid/",
  "how-to/fit-model/squid/": "how-to/fit-model/squid.en/",
  "how-to/getting-started/first-simulation.en/": "how-to/getting-started/first-simulation/",
  "how-to/getting-started/first-simulation/": "how-to/getting-started/first-simulation.en/",
  "how-to/getting-started/installation.en/": "how-to/getting-started/installation/",
  "how-to/getting-started/installation/": "how-to/getting-started/installation.en/",
  "how-to/index.en/": "how-to/",
  "how-to/ingest-data/": "how-to/ingest-data/index.en/",
  "how-to/ingest-data/hfss-admittance.en/": "how-to/ingest-data/hfss-admittance/",
  "how-to/ingest-data/hfss-admittance/": "how-to/ingest-data/hfss-admittance.en/",
  "how-to/ingest-data/hfss-scattering.en/": "how-to/ingest-data/hfss-scattering/",
  "how-to/ingest-data/hfss-scattering/": "how-to/ingest-data/hfss-scattering.en/",
  "how-to/ingest-data/index.en/": "how-to/ingest-data/",
  "how-to/manage-db/": "how-to/manage-db/index.en/",
  "how-to/manage-db/datasets.en/": "how-to/manage-db/datasets/",
  "how-to/manage-db/datasets/": "how-to/manage-db/datasets.en/",
  "how-to/manage-db/index.en/": "how-to/manage-db/",
  "how-to/manage-db/reorder-record-ids.en/": "how-to/manage-db/reorder-record-ids/",
  "how-to/manage-db/reorder-record-ids/": "how-to/manage-db/reorder-record-ids.en/",
  "how-to/manage-db/tags.en/": "how-to/manage-db/tags/",
  "how-to/manage-db/tags/": "how-to/manage-db/tags.en/",
  "how-to/simulation/": "how-to/simulation/index.en/",
  "how-to/simulation/index.en/": "how-to/simulation/",
  "how-to/simulation/native-julia.en/": "how-to/simulation/native-julia/",
  "how-to/simulation/native-julia/": "how-to/simulation/native-julia.en/",
  "how-to/simulation/python-api.en/": "how-to/simulation/python-api/",
  "how-to/simulation/python-api/": "how-to/simulation/python-api.en/",
  "index.en/": "",
  "notebooks/floating-qubit-study.en/": "notebooks/floating-qubit-study/",
  "notebooks/floating-qubit-study/": "notebooks/floating-qubit-study.en/",
  "notebooks/lagrangian-mechanics-and-circuit-physics.en/": "notebooks/lagrangian-mechanics-and-circuit-physics/",
  "notebooks/lagrangian-mechanics-and-circuit-physics/": "notebooks/lagrangian-mechanics-and-circuit-physics.en/",
  "notebooks/macroscopic-wavefunction.en/": "notebooks/macroscopic-wavefunction/",
  "notebooks/macroscopic-wavefunction/": "notebooks/macroscopic-wavefunction.en/",
  "notebooks/s-parameter-resonance-fit-theory.en/": "notebooks/s-parameter-resonance-fit-theory/",
  "notebooks/s-parameter-resonance-fit-theory/": "notebooks/s-parameter-resonance-fit-theory.en/",
  "notebooks/squid-controls-nonlinear-inductance.en/": "notebooks/squid-controls-nonlinear-inductance/",
  "notebooks/squid-controls-nonlinear-inductance/": "notebooks/squid-controls-nonlinear-inductance.en/",
  "notebooks/why-flux-is-quantized.en/": "notebooks/why-flux-is-quantized/",
  "notebooks/why-flux-is-quantized/": "notebooks/why-flux-is-quantized.en/",
  "notebooks/why-nonlinearity-makes-unequal-level-spacing.en/": "notebooks/why-nonlinearity-makes-unequal-level-spacing/",
  "notebooks/why-nonlinearity-makes-unequal-level-spacing/": "notebooks/why-nonlinearity-makes-unequal-level-spacing.en/",
  "reference/": "reference/index.en/",
  "reference/cli/": "reference/cli/index.en/",
  "reference/cli/flux-dependence-plot.en/": "reference/cli/flux-dependence-plot/",
  "reference/cli/flux-dependence-plot/": "reference/cli/flux-dependence-plot.en/",
  "reference/cli/generated/sc-db.en/": "reference/cli/generated/sc-db/",
  "reference/cli/generated/sc-db/": "reference/cli/generated/sc-db.en/",
  "reference/cli/generated/sc-fit-squid.en/": "reference/cli/generated/sc-fit-squid/",
  "reference/cli/generated/sc-fit-squid/": "reference/cli/generated/sc-fit-squid.en/",
  "reference/cli/generated/sc-preprocess-hfss-admittance.en/": "reference/cli/generated/sc-preprocess-hfss-admittance/",
  "reference/cli/generated/sc-preprocess-hfss-admittance/": "reference/cli/generated/sc-preprocess-hfss-admittance.en/",
  "reference/cli/generated/sc-preprocess-hfss-scattering.en/": "reference/cli/generated/sc-preprocess-hfss-scattering/",
  "reference/cli/generated/sc-preprocess-hfss-scattering/": "reference/cli/generated/sc-preprocess-hfss-scattering.en/",
  "reference/cli/generated/sc-preprocess-vna-flux-dependence.en/": "reference/cli/generated/sc-preprocess-vna-flux-dependence/",
  "reference/cli/generated/sc-preprocess-vna-flux-dependence/": "reference/cli/generated/sc-preprocess-vna-flux-dependence.en/",
  "reference/cli/generated/sc-simulate-lc.en/": "reference/cli/generated/sc-simulate-lc/",
  "reference/cli/generated/sc-simulate-lc/": "reference/cli/generated/sc-simulate-lc.en/",
  "reference/cli/generated/sc.en/": "reference/cli/generated/sc/",
  "reference/cli/generated/sc/": "reference/cli/generated/sc.en/",
  "reference/cli/index.en/": "reference/cli/",
  "reference/cli/plot-admittance.en/": "reference/cli/plot-admittance/",
  "reference/cli/plot-admittance/": "reference/cli/plot-admittance.en/",
  "reference/cli/sc-db-data-record.en/": "reference/cli/sc-db-data-record/",
  "reference/cli/sc-db-data-record/": "reference/cli/sc-db-data-record.en/",
  "reference/cli/sc-db-dataset-record.en/": "reference/cli/sc-db-dataset-record/",
  "reference/cli/sc-db-dataset-record/": "reference/cli/sc-db-dataset-record.en/",
  "reference/cli/sc-db-derived-parameter.en/": "reference/cli/sc-db-derived-parameter/",
  "reference/cli/sc-db-derived-parameter/": "reference/cli/sc-db-derived-parameter.en/",
  "reference/cli/sc-db-tag.en/": "reference/cli/sc-db-tag/",
  "reference/cli/sc-db-tag/": "reference/cli/sc-db-tag.en/",
  "reference/cli/sc-db.en/": "reference/cli/sc-db/",
  "reference/cli/sc-db/": "reference/cli/sc-db.en/",
  "reference/cli/sc-fit-squid.en/": "reference/cli/sc-fit-squid/",
  "reference/cli/sc-fit-squid/": "reference/cli/sc-fit-squid.en/",
  "reference/cli/sc-plot-resonance-map.en/": "reference/cli/sc-plot-resonance-map/",
  "reference/cli/sc-plot-resonance-map/": "reference/cli/sc-plot-resonance-map.en/",
  "reference/cli/sc-preprocess-hfss-admittance.en/": "reference/cli/sc-preprocess-hfss-admittance/",
  "reference/cli/sc-preprocess-hfss-admittance/": "reference/cli/sc-preprocess-hfss-admittance.en/",
  "reference/cli/sc-preprocess-hfss-scattering.en/": "reference/cli/sc-preprocess-hfss-scattering/",
  "reference/cli/sc-preprocess-hfss-scattering/": "reference/cli/sc-preprocess-hfss-scattering.en/",
  "reference/cli/sc-preprocess-vna-flux-dependence.en/": "reference/cli/sc-preprocess-vna-flux-dependence/",
  "reference/cli/sc-preprocess-vna-flux-dependence/": "reference/cli/sc-preprocess-vna-flux-dependence.en/",
  "reference/cli/sc-simulate-lc.en/": "reference/cli/sc-simulate-lc/",
  "reference/cli/sc-simulate-lc/": "reference/cli/sc-simulate-lc.en/",
  "reference/contributors.en/": "reference/contributors/",
  "reference/contributors/": "reference/contributors.en/",
  "reference/data-formats/": "reference/data-formats/index.en/",
  "reference/data-formats/analysis-result.en/": "reference/data-formats/analysis-result/",
  "reference/data-formats/analysis-result/": "reference/data-formats/analysis-result.en/",
  "reference/data-formats/circuit-netlist.en/": "reference/data-formats/circuit-netlist/",
  "reference/data-formats/circuit-netlist/": "reference/data-formats/circuit-netlist.en/",
  "reference/data-formats/dataset-record.en/": "reference/data-formats/dataset-record/",
  "reference/data-formats/dataset-record/": "reference/data-formats/dataset-record.en/",
  "reference/data-formats/index.en/": "reference/data-formats/",
  "reference/data-formats/raw-data-layout.en/": "reference/data-formats/raw-data-layout/",
  "reference/data-formats/raw-data-layout/": "reference/data-formats/raw-data-layout.en/",
  "reference/guardrails/": "reference/guardrails/index.en/",
  "reference/guardrails/code-quality/code-style.en/": "reference/guardrails/code-quality/code-style/",
  "reference/guardrails/code-quality/code-style/": "reference/guardrails/code-quality/code-style.en/",
  "reference/guardrails/code-quality/data-handling.en/": "reference/guardrails/code-quality/data-handling/",
  "reference/guardrails/code-quality/data-handling/": "reference/guardrails/code-quality/data-handling.en/",
  "reference/guardrails/code-quality/logging.en/": "reference/guardrails/code-quality/logging/",
  "reference/guardrails/code-quality/logging/": "reference/guardrails/code-quality/logging.en/",
  "reference/guardrails/code-quality/script-authoring.en/": "reference/guardrails/code-quality/script-authoring/",
  "reference/guardrails/code-quality/script-authoring/": "reference/guardrails/code-quality/script-authoring.en/",
  "reference/guardrails/code-quality/type-checking.en/": "reference/guardrails/code-quality/type-checking/",
  "reference/guardrails/code-quality/type-checking/": "reference/guardrails/code-quality/type-checking.en/",
  "reference/guardrails/documentation-design/documentation.en/": "reference/guardrails/documentation-design/documentation/",
  "reference/guardrails/documentation-design/documentation/": "reference/guardrails/documentation-design/documentation.en/",
  "reference/guardrails/documentation-design/explanation-physics.en/": "reference/guardrails/documentation-design/explanation-physics/",
  "reference/guardrails/documentation-design/explanation-physics/": "reference/guardrails/documentation-design/explanation-physics.en/",
  "reference/guardrails/documentation-design/maintenance.en/": "reference/guardrails/documentation-design/maintenance/",
  "reference/guardrails/documentation-design/maintenance/": "reference/guardrails/documentation-design/maintenance.en/",
  "reference/guardrails/documentation-design/standards.en/": "reference/guardrails/documentation-design/standards/",
  "reference/guardrails/documentation-design/standards/": "reference/guardrails/documentation-design/standards.en/",
  "reference/guardrails/documentation-design/style.en/": "reference/guardrails/documentation-design/style/",
  "reference/guardrails/documentation-design/style/": "reference/guardrails/documentation-design/style.en/",
  "reference/guardrails/execution-verification/build-commands.en/": "reference/guardrails/execution-verification/build-commands/",
  "reference/guardrails/execution-verification/build-commands/": "reference/guardrails/execution-verification/build-commands.en/",
  "reference/guardrails/execution-verification/ci-gates.en/": "reference/guardrails/execution-verification/ci-gates/",
  "reference/guardrails/execution-verification/ci-gates/": "reference/guardrails/execution-verification/ci-gates.en/",
  "reference/guardrails/execution-verification/commit-standards.en/": "reference/guardrails/execution-verification/commit-standards/",
  "reference/guardrails/execution-verification/commit-standards/": "reference/guardrails/execution-verification/commit-standards.en/",
  "reference/guardrails/execution-verification/linting.en/": "reference/guardrails/execution-verification/linting/",
  "reference/guardrails/execution-verification/linting/": "reference/guardrails/execution-verification/linting.en/",
  "reference/guardrails/execution-verification/testing.en/": "reference/guardrails/execution-verification/testing/",
  "reference/guardrails/execution-verification/testing/": "reference/guardrails/execution-verification/testing.en/",
  "reference/guardrails/index.en/": "reference/guardrails/",
  "reference/guardrails/project-basics/folder-structure.en/": "reference/guardrails/project-basics/folder-structure/",
  "reference/guardrails/project-basics/folder-structure/": "reference/guardrails/project-basics/folder-structure.en/",
  "reference/guardrails/project-basics/project-overview.en/": "reference/guardrails/project-basics/project-overview/",
  "reference/guardrails/project-basics/project-overview/": "reference/guardrails/project-basics/project-overview.en/",
  "reference/guardrails/project-basics/tech-stack.en/": "reference/guardrails/project-basics/tech-stack/",
  "reference/guardrails/project-basics/tech-stack/": "reference/guardrails/project-basics/tech-stack.en/",
  "reference/guardrails/ui-ux-quality/": "reference/guardrails/ui-ux-quality/index.en/",
  "reference/guardrails/ui-ux-quality/component-guidelines.en/": "reference/guardrails/ui-ux-quality/component-guidelines/",
  "reference/guardrails/ui-ux-quality/component-guidelines/": "reference/guardrails/ui-ux-quality/component-guidelines.en/",
  "reference/guardrails/ui-ux-quality/index.en/": "reference/guardrails/ui-ux-quality/",
  "reference/guardrails/ui-ux-quality/layout-patterns.en/": "reference/guardrails/ui-ux-quality/layout-patterns/",
  "reference/guardrails/ui-ux-quality/layout-patterns/": "reference/guardrails/ui-ux-quality/layout-patterns.en/",
  "reference/guardrails/ui-ux-quality/theming.en/": "reference/guardrails/ui-ux-quality/theming/",
  "reference/guardrails/ui-ux-quality/theming/": "reference/guardrails/ui-ux-quality/theming.en/",
  "reference/index.en/": "reference/",
  "reference/utilities.en/": "reference/utilities/",
  "reference/utilities/": "reference/utilities.en/",
  "tutorials/": "tutorials/index.en/",
  "tutorials/flux-analysis.en/": "tutorials/flux-analysis/",
  "tutorials/flux-analysis/": "tutorials/flux-analysis.en/",
  "tutorials/index.en/": "tutorials/",
  "tutorials/lc-resonator.en/": "tutorials/lc-resonator/",
  "tutorials/lc-resonator/": "tutorials/lc-resonator.en/",
  "tutorials/parameter-sweep.en/": "tutorials/parameter-sweep/",
  "tutorials/parameter-sweep/": "tutorials/parameter-sweep.en/",
  "tutorials/resonance-fitting.en/": "tutorials/resonance-fitting/",
  "tutorials/resonance-fitting/": "tutorials/resonance-fitting.en/",
  "tutorials/simulation-workflow.en/": "tutorials/simulation-workflow/",
  "tutorials/simulation-workflow/": "tutorials/simulation-workflow.en/"
});

function ensureTrailingSlash(pathname) {
  return pathname.endsWith("/") ? pathname : `${pathname}/`;
}

function isEnglishRoute(route) {
  return route === "index.en/" || route.endsWith(".en/");
}

function getRouteFromPath(pathname, prefix) {
  const normalizedPath = ensureTrailingSlash(pathname);
  if (!normalizedPath.startsWith(prefix)) {
    return null;
  }

  return normalizedPath === prefix ? "" : normalizedPath.slice(prefix.length);
}

function getRouteFromHref(href, prefix) {
  const url = new URL(href, window.location.href);
  if (url.origin !== window.location.origin) {
    return null;
  }

  return getRouteFromPath(url.pathname, prefix);
}

function toLanguageRoute(route, targetIsEnglish) {
  if (route === null) {
    return null;
  }

  const routeIsEnglish = isEnglishRoute(route);
  if (routeIsEnglish === targetIsEnglish) {
    return route;
  }

  return LANGUAGE_ROUTE_MAP[route] || route;
}

function setLocalizedHref(node, nextRoute, prefix) {
  if (nextRoute === null) {
    return;
  }

  const currentUrl = new URL(node.getAttribute("href"), window.location.href);
  const nextUrl = new URL(`${prefix}${nextRoute}`, window.location.origin);
  nextUrl.hash = currentUrl.hash;
  node.setAttribute("href", nextUrl.toString());
}

function localizeNavigationLinks(prefix, currentIsEnglish) {
  document
    .querySelectorAll(
      "[data-md-component=\"sidebar\"][data-md-type=\"navigation\"] a.md-nav__link[href], nav.md-tabs a.md-tabs__link[href]"
    )
    .forEach((node) => {
      const route = getRouteFromHref(node.href, prefix);
      if (route === null) {
        return;
      }

      setLocalizedHref(node, toLanguageRoute(route, currentIsEnglish), prefix);
    });
}

function setPrimaryNavOpenState(item, expanded) {
  const toggle = item.querySelector(":scope > input.md-nav__toggle");
  if (toggle) {
    toggle.checked = expanded;
  }

  const nestedNav = item.querySelector(":scope > nav.md-nav");
  if (nestedNav) {
    nestedNav.setAttribute("aria-expanded", expanded ? "true" : "false");
  }
}

function syncPrimarySidebar(prefix, currentRoute) {
  const sidebar = document.querySelector(
    "[data-md-component=\"sidebar\"][data-md-type=\"navigation\"]"
  );
  if (!sidebar) {
    return;
  }

  sidebar
    .querySelectorAll("a.md-nav__link--active, label.md-nav__link--active")
    .forEach((node) => node.classList.remove("md-nav__link--active"));
  sidebar
    .querySelectorAll("li.md-nav__item--active")
    .forEach((node) => node.classList.remove("md-nav__item--active"));
  sidebar
    .querySelectorAll("li.md-nav__item--nested")
    .forEach((item) => setPrimaryNavOpenState(item, false));

  const activeLink = Array.from(sidebar.querySelectorAll("a.md-nav__link[href]")).find(
    (node) => getRouteFromHref(node.href, prefix) === currentRoute
  );

  if (!activeLink) {
    return;
  }

  activeLink.classList.add("md-nav__link--active");

  let item = activeLink.closest("li.md-nav__item");
  while (item) {
    item.classList.add("md-nav__item--active");
    setPrimaryNavOpenState(item, true);

    const label = item.querySelector(":scope > label.md-nav__link");
    if (label) {
      label.classList.add("md-nav__link--active");
    }

    const parentNav = item.parentElement?.closest("nav.md-nav");
    item = parentNav ? parentNav.closest("li.md-nav__item") : null;
  }
}

function getCurrentPrefix() {
  const preferred = document.querySelector(
    "link[rel=\"alternate\"][hreflang=\"zh-TW\"]"
  );
  const fallback = document.querySelector(
    "link[rel=\"alternate\"][hreflang]"
  );
  const href = (preferred && preferred.href) || (fallback && fallback.href) || window.location.href;
  const deployedPrefix = ensureTrailingSlash(
    new URL(href, window.location.href).pathname
  );
  const currentPath = ensureTrailingSlash(window.location.pathname);

  if (currentPath.startsWith(deployedPrefix)) {
    return deployedPrefix;
  }

  return "/";
}

function applyLanguageSwitcher() {
  const prefix = getCurrentPrefix();
  const currentPath = ensureTrailingSlash(window.location.pathname);
  const currentRoute = currentPath === prefix ? "" : currentPath.slice(prefix.length);
  const counterpartPath = LANGUAGE_ROUTE_MAP[currentRoute];
  if (!counterpartPath) {
    // Keep selector usable even when the current page has no counterpart.
  }

  const currentIsEnglish = isEnglishRoute(currentRoute);
  const zhPath = currentIsEnglish ? (counterpartPath || "") : currentRoute;
  const enPath = currentIsEnglish ? currentRoute : (counterpartPath || "index.en/");

  document
    .querySelectorAll("a.md-select__link[hreflang]")
    .forEach((node) => {
      const hreflang = (node.getAttribute("hreflang") || "").toLowerCase();
      const nextPath = hreflang.startsWith("en") ? enPath : zhPath;
      node.setAttribute("href", new URL(`${prefix}${nextPath}`, window.location.origin).toString());
    });

  if (currentIsEnglish) {
    localizeNavigationLinks(prefix, true);
    syncPrimarySidebar(prefix, currentRoute);
  }
}

document.addEventListener("DOMContentLoaded", applyLanguageSwitcher);

if (window.document$ && typeof window.document$.subscribe === "function") {
  window.document$.subscribe(applyLanguageSwitcher);
}

/* Missing English counterparts: ["explanation/architecture/design-decisions/circuit-schema-live-preview.md", "explanation/architecture/design-decisions/live-preview-domain-semantics.md", "explanation/architecture/design-decisions/schema-editor-formatting.md", "reference/cli/sc-analysis-resonance-extract.md", "reference/cli/sc-analysis-resonance-fit.md", "tutorials/end-to-end-fitting.md"] */
/* English-only pages (no zh-TW source): ["explanation/harmonic-balance.en.md", "explanation/s-parameters.en.md"] */
