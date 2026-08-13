document.addEventListener("DOMContentLoaded", () => {
  const root = document.querySelector("#paper-atlas");
  if (!root) return;

  const STORAGE = "paper-atlas-state";
  const cards = Array.from(root.querySelectorAll(".atlas-card"));
  const query = root.querySelector("#atlas-query");
  const year = root.querySelector("#atlas-year");
  const journal = root.querySelector("#atlas-journal");
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
  const layoutButtons = Array.from(root.querySelectorAll("[data-atlas-layout]"));
  const searchFields = new Map(
    cards.map((card) => [
      card,
      {
        method: (
          card.dataset.method ||
          card.querySelector("h2").getAttribute("aria-label") ||
          ""
        ).toLocaleLowerCase(),
        title: (card.querySelector(".atlas-card__title").textContent || "").toLocaleLowerCase(),
        journal: (card.dataset.journalLabel || "").toLocaleLowerCase(),
        notes: Array.from(card.querySelectorAll(".atlas-card__summary"))
          .map((node) => node.textContent)
          .join("\n")
          .toLocaleLowerCase(),
      },
    ]),
  );
  const topicLabels = new Map(
    topicButtons.map((button) => [
      button.dataset.atlasTopic,
      button.querySelector("span").textContent,
    ]),
  );
  const journalLabels = new Map(
    Array.from(journal ? journal.options : []).map((option) => [option.value, option.textContent]),
  );
  const pageSize = Number.parseInt(root.dataset.pageSize, 10) || 36;
  const defaults = {
    q: "",
    topic: "",
    year: "",
    journal: "",
    code: "",
    lang: "zh",
    sort: "newest",
    layout: "cards",
    n: String(pageSize),
  };
  let orderedCards = [...cards];
  let visibleLimit = pageSize;
  let topic = "";
  let layout = "cards";
  let syncing = false;

  root.classList.add("is-enhanced");

  const normalized = (value) => value.trim().toLocaleLowerCase();

  const scoreCard = (card, terms) => {
    if (!terms.length) return 0;
    const fields = searchFields.get(card);
    let score = 0;
    for (const term of terms) {
      if (fields.method.includes(term)) score += 8;
      else if (fields.title.includes(term)) score += 4;
      else if (fields.journal.includes(term)) score += 2;
      else if (fields.notes.includes(term)) score += 1;
      else return -1;
    }
    return score;
  };

  const matchingCards = () => {
    const terms = normalized(query.value).split(/\s+/).filter(Boolean);
    const rank = new Map(orderedCards.map((card, index) => [card, index]));
    const filtered = orderedCards.filter((card) => {
      const cardCategory = card.dataset.category;
      const matchesTopic =
        !topic ||
        cardCategory === topic ||
        cardCategory.startsWith(`${topic}/`);
      const matchesYear = !year.value || card.dataset.year === year.value;
      const matchesJournal = !journal || !journal.value || card.dataset.journal === journal.value;
      const matchesCode = !code.value || card.dataset.code === code.value;
      return matchesTopic && matchesYear && matchesJournal && matchesCode && scoreCard(card, terms) >= 0;
    });
    if (!terms.length) return filtered;
    return [...filtered].sort((left, right) => {
      const diff = scoreCard(right, terms) - scoreCard(left, terms);
      return diff || rank.get(left) - rank.get(right);
    });
  };

  const syncTopicButtons = () => {
    const activeParent = topic.split("/")[0];
    topicButtons.forEach((button) => {
      const value = button.dataset.atlasTopic;
      const active = value === topic;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", active.toString());
      const parent = button.dataset.atlasParent;
      if (parent) button.hidden = parent !== activeParent;
    });
  };

  const syncLayoutButtons = () => {
    root.classList.toggle("is-list", layout === "list");
    layoutButtons.forEach((button) => {
      const active = button.dataset.atlasLayout === layout;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", active.toString());
    });
  };

  const syncCodeShortcut = () => {
    if (!codeShortcut) return;
    const active = code.value === "yes";
    codeShortcut.classList.toggle("is-active", active);
    codeShortcut.setAttribute("aria-pressed", active.toString());
  };

  const describeFilters = () => {
    const parts = [];
    if (topic) parts.push(topicLabels.get(topic) || topic);
    if (year.value) parts.push(year.value);
    if (journal && journal.value) {
      const label = journalLabels.get(journal.value) || journal.value;
      parts.push(label.replace(/\s*\(\d+\)\s*$/, ""));
    }
    if (code.value === "yes") parts.push("code available");
    if (code.value === "no") parts.push("no public code");
    if (query.value.trim()) parts.push(`“${query.value.trim()}”`);
    activeFilters.textContent = parts.length ? `Filtered by ${parts.join(" · ")}` : "";
  };

  const applySort = () => {
    orderedCards = [...cards].sort((left, right) => {
      const leftYear = Number.parseInt(left.dataset.year, 10) || 0;
      const rightYear = Number.parseInt(right.dataset.year, 10) || 0;
      const leftName = left.dataset.method || left.querySelector("h2").textContent;
      const rightName = right.dataset.method || right.querySelector("h2").textContent;
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

  const syncDetailLinks = () => {
    const lang = view.value;
    cards.forEach((card) => {
      const link = card.querySelector(".atlas-details-link");
      if (!link) return;
      const url = new URL(link.getAttribute("href"), window.location.href);
      if (lang && lang !== "zh") url.searchParams.set("lang", lang);
      else url.searchParams.delete("lang");
      link.href = `${url.pathname}${url.search}`;
    });
  };

  const currentParams = () => {
    const params = new URLSearchParams();
    const values = {
      q: query.value.trim(),
      topic,
      year: year.value,
      journal: journal ? journal.value : "",
      code: code.value,
      lang: view.value,
      sort: sort.value,
      layout,
      n: String(visibleLimit),
    };
    Object.entries(values).forEach(([key, value]) => {
      if (value && value !== defaults[key]) params.set(key, value);
    });
    return params;
  };

  const writeState = () => {
    if (syncing) return;
    const params = currentParams();
    const search = params.toString();
    const next = search ? `${window.location.pathname}?${search}` : window.location.pathname;
    const current = `${window.location.pathname}${window.location.search}`;
    if (next !== current) history.replaceState(null, "", next);
    try {
      sessionStorage.setItem(STORAGE, search ? `?${search}` : "");
    } catch {
      /* ignore private-mode quota */
    }
  };

  const readState = () => {
    const params = new URLSearchParams(window.location.search);
    query.value = params.get("q") || "";
    topic = params.get("topic") || "";
    year.value = params.get("year") || "";
    if (journal) journal.value = params.get("journal") || "";
    code.value = params.get("code") || "";
    view.value = params.get("lang") || "zh";
    sort.value = params.get("sort") || "newest";
    layout = params.get("layout") === "list" ? "list" : "cards";
    const requested = Number.parseInt(params.get("n") || "", 10);
    visibleLimit = Number.isFinite(requested) && requested > 0 ? requested : pageSize;
  };

  const render = ({ resetLimit = false, persist = true } = {}) => {
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
    syncCodeShortcut();
    syncDetailLinks();
    markClipped();
    if (persist) writeState();
  };

  const applyAll = ({ resetLimit = false, persist = true } = {}) => {
    applySort();
    applySummaryView();
    syncTopicButtons();
    syncLayoutButtons();
    render({ resetLimit, persist });
  };

  controls.addEventListener("submit", (event) => event.preventDefault());
  query.addEventListener("input", () => render({ resetLimit: true }));
  [year, journal, code].filter(Boolean).forEach((select) => {
    select.addEventListener("change", () => render({ resetLimit: true }));
  });
  topicButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const value = button.dataset.atlasTopic;
      topic = topic === value ? "" : value;
      syncTopicButtons();
      render({ resetLimit: true });
    });
  });
  sort.addEventListener("change", () => applyAll({ resetLimit: true }));
  view.addEventListener("change", () => {
    applySummaryView();
    render({ resetLimit: false });
    markClipped();
  });
  layoutButtons.forEach((button) => {
    button.addEventListener("click", () => {
      layout = button.dataset.atlasLayout === "list" ? "list" : "cards";
      syncLayoutButtons();
      render({ resetLimit: false });
    });
  });
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
      layout = "cards";
      if (journal) journal.value = "";
      applyAll({ resetLimit: true });
    });
  });
  more.addEventListener("click", () => {
    const firstNewIndex = visibleLimit;
    visibleLimit += pageSize;
    render();
    const nextCard = matchingCards()[firstNewIndex];
    if (nextCard) nextCard.querySelector("h2").scrollIntoView({ block: "center" });
  });

  grid.addEventListener("click", (event) => {
    const trigger = event.target.closest(".atlas-expand");
    if (!trigger) return;
    const card = trigger.closest(".atlas-card");
    const expanded = card.classList.toggle("is-expanded");
    const method = trigger.dataset.atlasMethod || "";
    trigger.textContent = expanded ? "Show less" : "Expand note";
    trigger.setAttribute(
      "aria-label",
      `${expanded ? "Show less" : "Expand note"} of the note on ${method}`,
    );
    trigger.setAttribute("aria-expanded", expanded.toString());
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "/" || event.metaKey || event.ctrlKey || event.altKey) return;
    const tag = document.activeElement && document.activeElement.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
    event.preventDefault();
    query.focus();
    query.select();
  });

  window.addEventListener("popstate", () => {
    syncing = true;
    readState();
    applyAll({ persist: false });
    syncing = false;
  });

  function markClipped() {
    if (layout === "list") return;
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
        trigger.textContent = "Expand note";
        trigger.setAttribute("aria-expanded", "false");
        const method = card.querySelector("h2");
        const name = card.dataset.method || method.getAttribute("aria-label") || method.textContent;
        trigger.dataset.atlasMethod = name;
        trigger.setAttribute("aria-label", `Expand note on ${name}`);
        card.querySelector("footer").before(trigger);
      }
      if (trigger) trigger.hidden = !clipped;
    });
  }

  readState();
  applyAll({ persist: true });
});
