(() => {
  const DEFAULT_ZH = "/";
  const DEFAULT_EN = "/index.en/";

  function normalize(pathname) {
    if (!pathname) return "/";
    return pathname.endsWith("/") ? pathname : `${pathname}/`;
  }

  function unique(items) {
    return [...new Set(items)];
  }

  async function urlExists(path) {
    try {
      const head = await fetch(path, { method: "HEAD" });
      if (head.ok) return true;
      if (head.status !== 405) return false;
    } catch {
      return false;
    }

    try {
      const get = await fetch(path, { method: "GET" });
      return get.ok;
    } catch {
      return false;
    }
  }

  async function resolveFirst(candidates) {
    const normalized = unique(candidates.map(normalize));
    for (const candidate of normalized) {
      // Keep local previews responsive by accepting default routes without probing.
      if (candidate === DEFAULT_ZH || candidate === DEFAULT_EN) return candidate;
      if (await urlExists(candidate)) return candidate;
    }
    return normalized[normalized.length - 1] || DEFAULT_ZH;
  }

  function zhToEnCandidates(currentPath) {
    const path = normalize(currentPath);
    if (path === DEFAULT_ZH) return [DEFAULT_EN];
    const candidates = [
      path.replace(/\/$/, ".en/"),
      `${path}index.en/`,
      DEFAULT_EN,
    ];
    return unique(candidates).filter(c => c !== path);
  }

  function enToZhCandidates(currentPath) {
    const path = normalize(currentPath);
    if (path === DEFAULT_EN) return [DEFAULT_ZH];
    const candidates = [
      path.replace(/index\.en\/$/, ""),
      path.replace(/\.en\/$/, "/"),
      DEFAULT_ZH,
    ];
    return unique(candidates).filter(c => c !== path);
  }

  async function patchLanguageLinks() {
    const langLinks = document.querySelectorAll("a.md-select__link[hreflang]");
    if (!langLinks.length) return;

    const current = normalize(window.location.pathname);
    const zhTarget = await resolveFirst(enToZhCandidates(current));
    const enTarget = await resolveFirst(zhToEnCandidates(current));

    langLinks.forEach((link) => {
      const lang = (link.getAttribute("hreflang") || "").toLowerCase();
      if (lang.startsWith("zh")) link.setAttribute("href", zhTarget);
      if (lang === "en") link.setAttribute("href", enTarget);
    });
  }

  if (typeof document$ !== "undefined" && document$.subscribe) {
    document$.subscribe(patchLanguageLinks);
  } else {
    document.addEventListener("DOMContentLoaded", patchLanguageLinks);
  }
})();
