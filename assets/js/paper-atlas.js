document.addEventListener("DOMContentLoaded", () => {
  const root = document.querySelector("#paper-atlas");
  if (!root) return;

  const cards = Array.from(root.querySelectorAll(".atlas-card"));
  const query = root.querySelector("#atlas-query");
  const year = root.querySelector("#atlas-year");
  const code = root.querySelector("#atlas-code");
  const controls = root.querySelector("#atlas-controls");
  const count = root.querySelector("#atlas-count");
  const activeFilters = root.querySelector("#atlas-active-filters");
  const empty = root.querySelector("#atlas-empty");
  const grid = root.querySelector("#atlas-grid");
  const more = root.querySelector("#atlas-more");
  const sort = root.querySelector("#atlas-sort");
  const view = root.querySelector("#atlas-view");
  const codeShortcut = root.querySelector("#atlas-code-shortcut");
  const topicButtons = Array.from(root.querySelectorAll("[data-atlas-topic]"));
  const searchText = new Map(
    cards.map((card) => [card, card.textContent.trim().toLocaleLowerCase()]),
  );
  const topicLabels = new Map(
    topicButtons.map((button) => [
      button.dataset.atlasTopic,
      button.querySelector("span").textContent,
    ]),
  );
  const pageSize = Number.parseInt(root.dataset.pageSize, 10) || 36;
  let orderedCards = [...cards];
  let visibleLimit = pageSize;
  let topic = "";

  root.classList.add("is-enhanced");

  const normalized = (value) => value.trim().toLocaleLowerCase();

  const matchingCards = () => {
    const terms = normalized(query.value).split(/\s+/).filter(Boolean);
    return orderedCards.filter((card) => {
      const matchesQuery = terms.every((term) =>
        searchText.get(card).includes(term),
      );
      const cardCategory = card.dataset.category;
      const matchesTopic =
        !topic ||
        cardCategory === topic ||
        cardCategory.startsWith(`${topic}/`);
      const matchesYear = !year.value || card.dataset.year === year.value;
      const matchesCode = !code.value || card.dataset.code === code.value;
      return matchesQuery && matchesTopic && matchesYear && matchesCode;
    });
  };

  const syncTopicButtons = () => {
    const activeParent = topic.split("/")[0];
    topicButtons.forEach((button) => {
      const value = button.dataset.atlasTopic;
      const active = value === topic;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", active.toString());
      // Sub-topics only surface once their parent is the active filter.
      const parent = button.dataset.atlasParent;
      if (parent) button.hidden = parent !== activeParent;
    });
  };

  // Restate the filters in words, so a short result list never looks like a bug.
  const describeFilters = () => {
    const parts = [];
    if (topic) parts.push(topicLabels.get(topic) || topic);
    if (year.value) parts.push(year.value);
    if (code.value === "yes") parts.push("code available");
    if (code.value === "no") parts.push("no public code");
    if (query.value.trim()) parts.push(`“${query.value.trim()}”`);
    activeFilters.textContent = parts.length ? `Filtered by ${parts.join(" · ")}` : "";
  };

  const applySort = () => {
    orderedCards = [...cards].sort((left, right) => {
      const leftYear = Number.parseInt(left.dataset.year, 10) || 0;
      const rightYear = Number.parseInt(right.dataset.year, 10) || 0;
      const leftName = left.querySelector("h2").textContent;
      const rightName = right.querySelector("h2").textContent;
      if (sort.value === "oldest")
        return leftYear - rightYear || leftName.localeCompare(rightName);
      if (sort.value === "name") return leftName.localeCompare(rightName);
      return rightYear - leftYear || leftName.localeCompare(rightName);
    });
    const fragment = document.createDocumentFragment();
    orderedCards.forEach((card) => fragment.append(card));
    grid.prepend(fragment);
  };

  const applySummaryView = () => {
    root.querySelectorAll("[data-atlas-summary]").forEach((summary) => {
      summary.hidden = summary.dataset.atlasSummary !== view.value;
    });
  };

  const render = ({ resetLimit = false } = {}) => {
    if (resetLimit) visibleLimit = pageSize;
    const matches = matchingCards();
    const visible = new Set(matches.slice(0, visibleLimit));
    orderedCards.forEach((card) => {
      card.hidden = !visible.has(card);
    });
    const shown = Math.min(visibleLimit, matches.length);
    count.innerHTML = `Showing <strong>${shown}</strong> of <strong>${matches.length}</strong> paper${matches.length === 1 ? "" : "s"}`;
    empty.hidden = matches.length !== 0;
    more.hidden = matches.length <= visibleLimit;
    describeFilters();
    markClipped();
  };

  query.addEventListener("input", () => render({ resetLimit: true }));
  [year, code].forEach((select) => {
    select.addEventListener("change", () => render({ resetLimit: true }));
  });
  topicButtons.forEach((button) => {
    button.addEventListener("click", () => {
      topic = button.dataset.atlasTopic;
      syncTopicButtons();
      render({ resetLimit: true });
    });
  });
  sort.addEventListener("change", () => {
    applySort();
    render({ resetLimit: true });
  });
  view.addEventListener("change", applySummaryView);
  if (codeShortcut) {
    codeShortcut.addEventListener("click", () => {
      code.value = code.value === "yes" ? "" : "yes";
      render({ resetLimit: true });
    });
  }
  controls.addEventListener("reset", () => {
    window.requestAnimationFrame(() => {
      topic = "";
      sort.value = "newest";
      view.value = "zh";
      applySort();
      applySummaryView();
      syncTopicButtons();
      render({ resetLimit: true });
    });
  });
  more.addEventListener("click", () => {
    const firstNewIndex = visibleLimit;
    visibleLimit += pageSize;
    render();
    const nextCard = matchingCards()[firstNewIndex];
    if (nextCard) nextCard.querySelector("h2").scrollIntoView({ block: "center" });
  });

  // Reveal a clipped note in place, so scanning never costs a page load.
  grid.addEventListener("click", (event) => {
    const trigger = event.target.closest(".atlas-expand");
    if (!trigger) return;
    const card = trigger.closest(".atlas-card");
    const expanded = card.classList.toggle("is-expanded");
    const method = trigger.dataset.atlasMethod || "";
    trigger.textContent = expanded ? "Show less" : "Show more";
    trigger.setAttribute(
      "aria-label",
      `${expanded ? "Show less" : "Show more"} of the note on ${method}`,
    );
    trigger.setAttribute("aria-expanded", expanded.toString());
  });

  // "/" focuses search, the convention for a reference index.
  document.addEventListener("keydown", (event) => {
    if (event.key !== "/" || event.metaKey || event.ctrlKey || event.altKey) return;
    const tag = document.activeElement && document.activeElement.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
    event.preventDefault();
    query.focus();
    query.select();
  });

  // Only offer the expand control on notes that are actually clipped.
  // Declared as a function so render() can call it before this point.
  function markClipped() {
    cards.forEach((card) => {
      if (card.hidden || card.classList.contains("is-expanded")) return;
      if (card.dataset.atlasMeasured === view.value) return;
      const panel = card.querySelector(`[data-atlas-summary="${view.value}"]`);
      const summary = panel && panel.querySelector(".atlas-card__summary");
      if (!summary) return;
      card.dataset.atlasMeasured = view.value;
      const clipped = summary.scrollHeight > summary.clientHeight + 2;
      let trigger = card.querySelector(".atlas-expand");
      if (clipped && !trigger) {
        trigger = document.createElement("button");
        trigger.type = "button";
        trigger.className = "atlas-expand";
        trigger.textContent = "Show more";
        trigger.setAttribute("aria-expanded", "false");
        // Name the paper: every card's button reads "Show more" otherwise.
        const method = card.querySelector("h2");
        const name = method.getAttribute("aria-label") || method.textContent;
        trigger.dataset.atlasMethod = name;
        trigger.setAttribute("aria-label", `Show more of the note on ${name}`);
        card.querySelector("footer").before(trigger);
      }
      if (trigger) trigger.hidden = !clipped;
    });
  }

  applySort();
  applySummaryView();
  syncTopicButtons();
  render({ resetLimit: true });
  view.addEventListener("change", markClipped);
});
