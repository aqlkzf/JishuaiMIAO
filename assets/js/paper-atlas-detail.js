document.addEventListener("DOMContentLoaded", () => {
  const root = document.querySelector("#paper-detail");
  if (!root) return;

  const tabs = Array.from(root.querySelectorAll("[data-detail-tab]"));
  const panels = Array.from(root.querySelectorAll("[data-detail-panel]"));

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const selected = tab.dataset.detailTab;
      tabs.forEach((candidate) => {
        const active = candidate === tab;
        candidate.classList.toggle("is-active", active);
        candidate.setAttribute("aria-selected", active.toString());
      });
      panels.forEach((panel) => {
        panel.hidden = panel.dataset.detailPanel !== selected;
      });
    });
  });
});
