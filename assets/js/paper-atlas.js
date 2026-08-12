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
  const more = root.querySelector("#atlas-more");
  const pageSize = Number.parseInt(root.dataset.pageSize, 10) || 36;
  let visibleLimit = pageSize;

  root.classList.add("is-enhanced");

  const normalized = (value) => value.trim().toLocaleLowerCase();

  const matchingCards = () => {
    const terms = normalized(query.value).split(/\s+/).filter(Boolean);
    return cards.filter((card) => {
      const searchableText = normalized(card.textContent);
      const matchesQuery = terms.every((term) => searchableText.includes(term));
      const matchesCategory =
        !category.value || card.dataset.category === category.value;
      const matchesYear = !year.value || card.dataset.year === year.value;
      const matchesCode = !code.value || card.dataset.code === code.value;
      return matchesQuery && matchesCategory && matchesYear && matchesCode;
    });
  };

  const render = ({ resetLimit = false } = {}) => {
    if (resetLimit) visibleLimit = pageSize;
    const matches = matchingCards();
    const visible = new Set(matches.slice(0, visibleLimit));
    cards.forEach((card) => {
      card.hidden = !visible.has(card);
    });
    count.textContent = `Showing ${Math.min(visibleLimit, matches.length)} of ${matches.length} papers`;
    empty.hidden = matches.length !== 0;
    more.hidden = matches.length <= visibleLimit;
  };

  query.addEventListener("input", () => render({ resetLimit: true }));
  [category, year, code].forEach((select) => {
    select.addEventListener("change", () => render({ resetLimit: true }));
  });
  controls.addEventListener("reset", () => {
    window.requestAnimationFrame(() => render({ resetLimit: true }));
  });
  more.addEventListener("click", () => {
    visibleLimit += pageSize;
    render();
  });

  render({ resetLimit: true });
});
