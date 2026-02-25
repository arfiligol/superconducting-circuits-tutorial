(() => {
  function getSiteBase() {
    try {
      const configRaw = document.getElementById('__config');
      const baseRel = configRaw ? JSON.parse(configRaw.textContent).base : ".";
      const basePath = new URL(baseRel + "/", window.location.href).pathname;
      return basePath.endsWith("/") ? basePath : `${basePath}/`;
    } catch (e) {
      return "/";
    }
  }

  const siteBase = getSiteBase();
  const DEFAULT_ZH = siteBase;
  const DEFAULT_EN = siteBase + "en/";

  function normalize(pathname) {
    if (!pathname) return siteBase;
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
    const relPath = path.startsWith(siteBase) ? path.slice(siteBase.length) : "";
    const candidates = [
      `${siteBase}en/${relPath}`,
      DEFAULT_EN,
    ];
    return unique(candidates).filter(c => c !== path);
  }

  function enToZhCandidates(currentPath) {
    const path = normalize(currentPath);
    if (path === DEFAULT_EN) return [DEFAULT_ZH];
    const prefix = `${siteBase}en/`;
    let candidates = [DEFAULT_ZH];
    if (path.startsWith(prefix)) {
      const relPath = path.slice(prefix.length);
      candidates.unshift(`${siteBase}${relPath}`);
    }
    return unique(candidates).filter(c => c !== path);
  }

  async function patchLanguageLinks() {
    const langLinks = document.querySelectorAll("a.md-select__link[hreflang]");
    const current = normalize(window.location.pathname);
    const isEnPage = current.includes('.en/') || current.endsWith('.en') || current.endsWith('about.en/');

    if (langLinks.length) {
      const zhTarget = await resolveFirst(enToZhCandidates(current));
      const enTarget = await resolveFirst(zhToEnCandidates(current));
      langLinks.forEach((link) => {
        const lang = (link.getAttribute("hreflang") || "").toLowerCase();
        if (lang.startsWith("zh")) link.setAttribute("href", zhTarget);
        if (lang === "en") link.setAttribute("href", enTarget);
      });
    }

    if (isEnPage) {
      const expectedZhPath = normalize(enToZhCandidates(current)[0]);
      const navLinks = document.querySelectorAll('.md-nav__link, .md-tabs__link');

      navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (!href || href.startsWith('http') || href.startsWith('#')) return;

        const urlObj = new URL(href, window.location.href);
        const urlPath = normalize(urlObj.pathname);

        // Fix Active State
        if (urlPath === expectedZhPath) {
          let parentLi = link.closest('.md-nav__item, .md-tabs__item');
          if (parentLi) {
            parentLi.classList.add(parentLi.classList.contains('md-tabs__item') ? 'md-tabs__item--active' : 'md-nav__item--active');
            let toggle = parentLi.querySelector('input.md-toggle');
            if (toggle) toggle.checked = true;

            let curr = parentLi.parentElement;
            while (curr && curr !== document.body) {
              if (curr.classList.contains('md-nav__item') || curr.classList.contains('md-tabs__item')) {
                curr.classList.add(curr.classList.contains('md-tabs__item') ? 'md-tabs__item--active' : 'md-nav__item--active');
                let t = curr.querySelector('input.md-toggle');
                if (t) t.checked = true;
              }
              curr = curr.parentElement;
            }
          }
        }

        // Rewrite Link to English
        let enHref;
        if (urlPath === siteBase) {
          enHref = siteBase + "index.en/";
        } else if (urlPath.endsWith("/")) {
          // E.g., /tutorials/ -> /tutorials/index.en/
          // But if it's already an English link (e.g., hardcoded from marketing.html), do nothing
          if (urlPath.includes('.en/')) {
            enHref = urlPath;
          } else {
            // Remove trailing slash and add .en/
            enHref = urlPath.replace(/\/$/, ".en/");
          }
        } else {
          enHref = urlPath.replace(/(\.html)?$/, ".en$1");
        }

        link.setAttribute('href', enHref + urlObj.search + urlObj.hash);
      });
    }
  }

  if (typeof document$ !== "undefined" && document$.subscribe) {
    document$.subscribe(patchLanguageLinks);
  } else {
    document.addEventListener("DOMContentLoaded", patchLanguageLinks);
  }
})();
