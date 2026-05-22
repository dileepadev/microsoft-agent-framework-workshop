(function () {
  const faviconHref = "/public/opsagent-mark.svg";

  function setFavicon(rel) {
    let link = document.head.querySelector(`link[rel="${rel}"]`);

    if (!link) {
      link = document.createElement("link");
      link.rel = rel;
      document.head.appendChild(link);
    }

    link.type = "image/svg+xml";
    link.href = faviconHref;
  }

  function applyBranding() {
    setFavicon("icon");
    setFavicon("shortcut icon");
    setFavicon("apple-touch-icon");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applyBranding, { once: true });
  } else {
    applyBranding();
  }
})();