document.addEventListener("DOMContentLoaded", () => {
  const root = document.querySelector("#paper-atlas");
  if (!root) return;

  const cards = Array.from(root.querySelectorAll(".atlas-card"));
  const query = root.querySelector("#atlas-query");
  const category = root.querySelector("#atlas-category");
  const year = root.querySelector("#atlas-year");
  const code = root.querySelector("#atlas-code");
  const controls = root.querySelector("#atlas-controls");
  const count = root.querySelector("#atlas-count");
  const empty = root.querySelector("#atlas-empty");
  const grid = root.querySelector("#atlas-grid");
  const more = root.querySelector("#atlas-more");
  const sort = root.querySelector("#atlas-sort");
  const view = root.querySelector("#atlas-view");
  const topicButtons = Array.from(root.querySelectorAll("[data-atlas-topic]"));
  const searchText = new Map(
    cards.map((card) => [card, card.textContent.trim().toLocaleLowerCase()]),
  );
  const pageSize = Number.parseInt(root.dataset.pageSize, 10) || 36;
  let orderedCards = [...cards];
  let visibleLimit = pageSize;

  root.classList.add("is-enhanced");

  const normalized = (value) => value.trim().toLocaleLowerCase();

  const matchingCards = () => {
    const terms = normalized(query.value).split(/\s+/).filter(Boolean);
    return orderedCards.filter((card) => {
      const matchesQuery = terms.every((term) =>
        searchText.get(card).includes(term),
      );
      const cardCategory = card.dataset.category;
      const matchesCategory =
        !category.value ||
        cardCategory === category.value ||
        cardCategory.startsWith(`${category.value}/`);
      const matchesYear = !year.value || card.dataset.year === year.value;
      const matchesCode = !code.value || card.dataset.code === code.value;
      return matchesQuery && matchesCategory && matchesYear && matchesCode;
    });
  };

  const syncTopicButtons = () => {
    topicButtons.forEach((button) => {
      const active = button.dataset.atlasTopic === category.value;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", active.toString());
    });
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
    grid.append(fragment);
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
    count.textContent = `Showing ${Math.min(visibleLimit, matches.length)} of ${matches.length} papers`;
    empty.hidden = matches.length !== 0;
    more.hidden = matches.length <= visibleLimit;
  };

  query.addEventListener("input", () => render({ resetLimit: true }));
  [category, year, code].forEach((select) => {
    select.addEventListener("change", () => {
      syncTopicButtons();
      render({ resetLimit: true });
    });
  });
  topicButtons.forEach((button) => {
    button.addEventListener("click", () => {
      category.value = button.dataset.atlasTopic;
      syncTopicButtons();
      render({ resetLimit: true });
    });
  });
  sort.addEventListener("change", () => {
    applySort();
    render({ resetLimit: true });
  });
  view.addEventListener("change", applySummaryView);
  controls.addEventListener("reset", () => {
    window.requestAnimationFrame(() => {
      sort.value = "newest";
      view.value = "zh";
      applySort();
      applySummaryView();
      syncTopicButtons();
      render({ resetLimit: true });
    });
  });
  more.addEventListener("click", () => {
    visibleLimit += pageSize;
    render();
  });

  applySort();
  applySummaryView();
  syncTopicButtons();
  render({ resetLimit: true });
});
