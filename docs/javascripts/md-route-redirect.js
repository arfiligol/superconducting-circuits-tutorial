(function () {
  function normalizeMdPath(pathname) {
    if (!pathname.endsWith(".md")) {
      return pathname;
    }

    var normalized = pathname.slice(0, -3);

    if (normalized === "index" || normalized === "/index") {
      return "/";
    }

    if (normalized.endsWith("/index")) {
      return normalized.slice(0, -6).replace(/\/?$/, "/");
    }

    return normalized.replace(/\/?$/, "/");
  }

  // Redirect direct .md visits to canonical directory routes.
  if (window.location.pathname.endsWith(".md")) {
    var targetPath = normalizeMdPath(window.location.pathname);
    if (targetPath !== window.location.pathname) {
      window.location.replace(
        targetPath + window.location.search + window.location.hash,
      );
      return;
    }
  }

  // Rewrite in-page internal links ending with .md to canonical routes.
  var links = document.querySelectorAll("a[href]");
  links.forEach(function (anchor) {
    var rawHref = anchor.getAttribute("href");
    if (
      !rawHref ||
      rawHref.startsWith("mailto:") ||
      rawHref.startsWith("tel:")
    ) {
      return;
    }
    try {
      var url = new URL(rawHref, window.location.href);
      if (url.origin !== window.location.origin) {
        return;
      }
      if (!url.pathname.endsWith(".md")) {
        return;
      }
      url.pathname = normalizeMdPath(url.pathname);
      anchor.setAttribute("href", url.pathname + url.search + url.hash);
    } catch (_err) {
      // Ignore malformed href.
    }
  });
})();
