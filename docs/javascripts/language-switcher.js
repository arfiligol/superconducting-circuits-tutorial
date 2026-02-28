/*
 * Native Separate Builds switcher.
 *
 * The zh-TW build is served at the site root and the English build is
 * served under /en/. Both builds generate the same route structure, so the
 * language selector can switch by preserving the current relative path.
 */

function ensureTrailingSlash(pathname) {
  return pathname.endsWith("/") ? pathname : `${pathname}/`;
}

function getLocaleBases() {
  const zhAlternate = document.querySelector(
    'link[rel="alternate"][hreflang="zh-TW"]'
  );
  const enAlternate = document.querySelector(
    'link[rel="alternate"][hreflang="en"]'
  );
  const currentPath = ensureTrailingSlash(window.location.pathname);

  const deployedZhBase = zhAlternate
    ? ensureTrailingSlash(new URL(zhAlternate.href, window.location.href).pathname)
    : "/";
  const deployedEnBase = enAlternate
    ? ensureTrailingSlash(new URL(enAlternate.href, window.location.href).pathname)
    : `${deployedZhBase}en/`;

  if (
    currentPath.startsWith(deployedZhBase) ||
    currentPath.startsWith(deployedEnBase)
  ) {
    return {
      zhBase: deployedZhBase,
      enBase: deployedEnBase,
    };
  }

  return {
    zhBase: "/",
    enBase: "/en/",
  };
}

function getCurrentRelativePath(currentPath, zhBase, enBase) {
  if (currentPath.startsWith(enBase)) {
    return currentPath.slice(enBase.length);
  }

  if (currentPath.startsWith(zhBase)) {
    return currentPath.slice(zhBase.length);
  }

  return "";
}

function applyLanguageSwitcher() {
  const currentPath = ensureTrailingSlash(window.location.pathname);
  const { zhBase, enBase } = getLocaleBases();
  const relativePath = getCurrentRelativePath(currentPath, zhBase, enBase);

  document.querySelectorAll('a.md-select__link[hreflang]').forEach((node) => {
    const currentUrl = new URL(node.getAttribute('href'), window.location.href);
    const hreflang = (node.getAttribute('hreflang') || '').toLowerCase();
    const basePath = hreflang.startsWith('en') ? enBase : zhBase;
    const nextUrl = new URL(`${basePath}${relativePath}`, window.location.origin);
    nextUrl.hash = currentUrl.hash;
    node.setAttribute('href', nextUrl.toString());
  });
}

document.addEventListener('DOMContentLoaded', applyLanguageSwitcher);

if (window.document$ && typeof window.document$.subscribe === 'function') {
  window.document$.subscribe(applyLanguageSwitcher);
}
