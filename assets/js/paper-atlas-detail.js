document.addEventListener("DOMContentLoaded", () => {
  const root = document.querySelector("#paper-detail");
  if (!root) return;

  const STORAGE = "paper-atlas-state";
  const HEADING_SELECTOR = "h2, h3";
  const tabs = Array.from(root.querySelectorAll("[data-detail-tab]"));
  const panels = Array.from(root.querySelectorAll("[data-detail-panel]"));
  const back = root.querySelector("[data-atlas-back]");
  if (back) {
    try {
      const stored = sessionStorage.getItem(STORAGE);
      if (stored) {
        const url = new URL(back.getAttribute("href"), window.location.href);
        back.href = `${url.pathname}${stored.startsWith("?") ? stored : `?${stored}`}`;
      }
    } catch {
      /* ignore */
    }
  }

  const tocNav = document.createElement("nav");
  tocNav.className = "paper-detail__toc";
  tocNav.hidden = true;

  const tocToggle = document.createElement("button");
  tocToggle.type = "button";
  tocToggle.className = "paper-detail__toc-toggle";
  tocToggle.setAttribute("aria-expanded", "false");

  const tocLabel = document.createElement("p");
  tocLabel.className = "paper-detail__toc-label";

  const tocList = document.createElement("ol");
  tocList.className = "paper-detail__toc-list";

  tocNav.append(tocToggle, tocLabel, tocList);

  const layout = document.createElement("div");
  layout.className = "paper-detail__layout";
  if (panels[0]) {
    panels[0].before(layout);
    layout.append(tocNav);
    panels.forEach((panel) => layout.append(panel));
  }

  let trackedHeadings = [];
  let ticking = false;

  const prefersReducedMotion = () =>
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const setActive = (id) => {
    tocList.querySelectorAll("a").forEach((link) => {
      const href = link.getAttribute("href") || "";
      const on = decodeURIComponent(href.replace(/^#/, "")) === id;
      link.classList.toggle("is-active", on);
      if (on) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    });
  };

  const updateFromScroll = () => {
    if (!trackedHeadings.length) return;
    const offset = 96;
    let current = trackedHeadings[0];
    for (const heading of trackedHeadings) {
      if (heading.getBoundingClientRect().top - offset <= 0) current = heading;
      else break;
    }
    if (current) setActive(current.id);
  };

  const onScroll = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      ticking = false;
      updateFromScroll();
    });
  };

  window.addEventListener("scroll", onScroll, { passive: true });

  const slugify = (text, index) => {
    const ascii = text
      .toLowerCase()
      .normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .slice(0, 48);
    return ascii || `section-${index}`;
  };

  const ensureHeadingId = (heading, panel, index) => {
    if (heading.id) return heading.id;
    heading.id = `${panel.dataset.detailPanel}-${slugify(heading.textContent, index)}`;
    return heading.id;
  };

  const closeMobileToc = () => {
    tocNav.classList.remove("is-open");
    tocToggle.setAttribute("aria-expanded", "false");
  };

  const buildToc = (panel) => {
    if (!panel) return;
    const lang = panel.dataset.detailPanel;
    const label = lang === "zh" ? "本页目录" : "On this page";
    tocLabel.textContent = label;
    tocToggle.textContent = label;
    tocNav.setAttribute("aria-label", label);
    tocList.replaceChildren();

    const headings = Array.from(panel.querySelectorAll(HEADING_SELECTOR));
    if (headings.length < 2) {
      tocNav.hidden = true;
      root.classList.remove("has-toc");
      trackedHeadings = [];
      return;
    }

    const h2s = headings.filter((heading) => heading.tagName === "H2");
    const skipLoneTitle =
      h2s.length === 1 && headings.some((heading) => heading.tagName === "H3");

    let lastH2Item = null;
    headings.forEach((heading, index) => {
      const id = ensureHeadingId(heading, panel, index);
      if (skipLoneTitle && heading === h2s[0]) return;
      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = `#${id}`;
      link.textContent = heading.textContent.replace(/\s+/g, " ").trim();
      item.append(link);
      if (heading.tagName === "H3" && lastH2Item) {
        let nested = lastH2Item.querySelector(":scope > ol");
        if (!nested) {
          nested = document.createElement("ol");
          lastH2Item.append(nested);
        }
        nested.append(item);
      } else {
        tocList.append(item);
        lastH2Item = heading.tagName === "H2" ? item : null;
      }
    });

    tocNav.hidden = false;
    root.classList.add("has-toc");
    closeMobileToc();
    trackedHeadings = skipLoneTitle ? headings.filter((heading) => heading !== h2s[0]) : headings;
    updateFromScroll();
  };

  tocToggle.addEventListener("click", () => {
    const open = tocNav.classList.toggle("is-open");
    tocToggle.setAttribute("aria-expanded", open.toString());
  });

  tocNav.addEventListener("click", (event) => {
    const link = event.target.closest("a[href^='#']");
    if (!link) return;
    const id = decodeURIComponent(link.getAttribute("href").slice(1));
    const target = document.getElementById(id);
    if (!target) return;
    event.preventDefault();
    target.scrollIntoView({
      behavior: prefersReducedMotion() ? "auto" : "smooth",
      block: "start",
    });
    const url = new URL(window.location.href);
    url.hash = id;
    history.replaceState(null, "", `${url.pathname}${url.search}${url.hash}`);
    setActive(id);
    closeMobileToc();
  });

  if (!tabs.length) {
    buildToc(panels[0]);
    return;
  }

  // Roving tabindex: the tablist is one tab stop, arrows move between tabs.
  const select = (tab, { focus = false, persist = true } = {}) => {
    tabs.forEach((candidate) => {
      const active = candidate === tab;
      candidate.classList.toggle("is-active", active);
      candidate.setAttribute("aria-selected", active.toString());
      candidate.tabIndex = active ? 0 : -1;
    });
    panels.forEach((panel) => {
      panel.hidden = panel.dataset.detailPanel !== tab.dataset.detailTab;
    });
    if (persist) {
      const url = new URL(window.location.href);
      if (tab.dataset.detailTab === "en") url.searchParams.set("lang", "en");
      else url.searchParams.delete("lang");
      const hashId = decodeURIComponent(url.hash.replace(/^#/, ""));
      const hashEl = hashId ? document.getElementById(hashId) : null;
      if (!hashEl || hashEl.closest("[data-detail-panel]")?.hidden) url.hash = "";
      const next = `${url.pathname}${url.search}${url.hash}`;
      const current = `${window.location.pathname}${window.location.search}${window.location.hash}`;
      if (next !== current) history.replaceState(null, "", next);
    }
    if (focus) tab.focus();
    buildToc(panels.find((panel) => !panel.hidden) || panels[0]);
  };

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => select(tab));
  });

  const hashId = decodeURIComponent(window.location.hash.replace(/^#/, ""));
  const hashTarget = hashId ? document.getElementById(hashId) : null;
  const hashPanel = hashTarget && hashTarget.closest("[data-detail-panel]");
  const requested =
    new URLSearchParams(window.location.search).get("lang") ||
    (hashPanel && hashPanel.dataset.detailPanel);
  const initial = tabs.find((tab) => tab.dataset.detailTab === requested);
  if (initial) select(initial, { persist: false });
  else buildToc(panels.find((panel) => !panel.hidden) || panels[0]);

  if (hashTarget) {
    requestAnimationFrame(() => {
      hashTarget.scrollIntoView({ behavior: "auto", block: "start" });
      setActive(hashTarget.id);
    });
  }

  root.querySelector('[role="tablist"]').addEventListener("keydown", (event) => {
    const current = tabs.indexOf(document.activeElement);
    if (current === -1) return;
    const last = tabs.length - 1;
    let next = null;
    if (event.key === "ArrowRight") next = current === last ? 0 : current + 1;
    if (event.key === "ArrowLeft") next = current === 0 ? last : current - 1;
    if (event.key === "Home") next = 0;
    if (event.key === "End") next = last;
    if (next === null) return;
    event.preventDefault();
    select(tabs[next], { focus: true });
  });
});
