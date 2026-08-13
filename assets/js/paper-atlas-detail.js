document.addEventListener("DOMContentLoaded", () => {
  const root = document.querySelector("#paper-detail");
  if (!root) return;

  const STORAGE = "paper-atlas-state";
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
  if (!tabs.length) return;

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
      const next = `${url.pathname}${url.search}`;
      const current = `${window.location.pathname}${window.location.search}`;
      if (next !== current) history.replaceState(null, "", next);
    }
    if (focus) tab.focus();
  };

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => select(tab));
  });

  const requested = new URLSearchParams(window.location.search).get("lang");
  const initial = tabs.find((tab) => tab.dataset.detailTab === requested);
  if (initial) select(initial, { persist: false });

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

