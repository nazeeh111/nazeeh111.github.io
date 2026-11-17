(() => {
  "use strict";

  const search = document.querySelector("#project-search");
  const subject = document.querySelector("#project-subject");
  const caseFilter = document.querySelector("#case-filter");
  const filters = document.querySelector("#work-filters");
  const status = document.querySelector("#catalog-status");
  const empty = document.querySelector("#catalog-empty");
  const reset = document.querySelector("#reset-search");
  const recovery = document.querySelector("#search-all-disciplines");
  const emptyMessage = document.querySelector("#catalog-empty-message");
  const entries = [...document.querySelectorAll(".project-item")];
  if (!search || !subject || !filters || !status || !empty || !reset) return;

  const categories = {
    "project-geometry": "Geometry & CAD",
    "project-sensing": "EE & sensing",
    "project-data-and-motion": "ML & data",
    "project-systems": "Systems & developer tools",
    "project-scientific-tools": "Physics & quantum",
  };
  const validSubjects = new Set(
    [...subject.options].map((option) => option.value),
  );

  function words(value) {
    return value
      .normalize("NFKD")
      .replace(/\p{M}/gu, "")
      .toLocaleLowerCase()
      .replace(/[^\p{L}\p{N}]+/gu, " ")
      .trim()
      .split(/\s+/u)
      .filter(Boolean);
  }
  const searchable = new Map(
    entries.map((entry) => [entry, words(entry.dataset.search || "")]),
  );

  const caseEntries = new Set(entries.filter((entry) => entry.querySelector(".case-link")));

  function writeLocation({ categoryFragment = false, clearAll = false } = {}) {
    const url = new URL(location.href);
    for (const [key, value] of [
      ["q", search.value.trim()],
      ["discipline", subject.value],
    ]) {
      if (value) url.searchParams.set(key, value);
      else url.searchParams.delete(key);
    }
    if (caseFilter?.checked) url.searchParams.set("cases", "1");
    else url.searchParams.delete("cases");
    // Full index is the default; retain an explicit legacy all URL until reset.
    if (clearAll) url.searchParams.delete("all");
    if (categoryFragment) url.hash = "projects";
    if (url.href !== location.href) history.replaceState(null, "", url);
  }

  function filterProjects(options = {}) {
    const query = words(search.value);
    const category = subject.value;
    const casesOnly = Boolean(caseFilter?.checked);
    let visible = 0;
    let acrossDisciplines = 0;
    for (const entry of entries) {
      const inScope = !casesOnly || caseEntries.has(entry);
      const queryMatches = inScope && query.every((term) => searchable.get(entry).some((word) => word.startsWith(term)));
      if (queryMatches) acrossDisciplines += 1;
      const subjects = (entry.dataset.subjects || entry.dataset.subject).split("|");
      const matches = (!category || subjects.includes(category)) && queryMatches;
      entry.hidden = !matches;
      if (matches) visible += 1;
    }
    const filtering = Boolean(search.value.trim() || category);
    const total = casesOnly ? caseEntries.size : entries.length;
    const count = filtering ? `${visible} of ${total}` : total;
    const label = casesOnly ? (total === 1 ? "case study" : "case studies") : "public repositories";
    status.textContent = `${count} ${label}`;
    empty.hidden = visible !== 0;
    const resultType = casesOnly ? "case studies" : "projects";
    if (emptyMessage) emptyMessage.textContent = category
      ? `No ${resultType} match${search.value.trim() ? ` “${search.value.trim()}”` : ""} in ${category}.`
      : `No ${resultType} match this search.`;
    if (recovery) recovery.hidden = !(visible === 0 && category && query.length && acrossDisciplines > 0);
    reset.hidden = !(filtering || casesOnly);
    writeLocation(options);
  }

  function restoreLocation() {
    const params = new URL(location.href).searchParams;
    search.value = params.get("q") || "";
    if (caseFilter) caseFilter.checked = caseEntries.size > 0 && params.get("cases") === "1";
    const requested = params.get("discipline") || "";
    subject.value = validSubjects.has(requested) ? requested : "";
    const fragment = location.hash.slice(1);
    const category = Object.hasOwn(categories, fragment)
      ? categories[fragment]
      : null;
    if (category && validSubjects.has(category) && !["q", "discipline", "all", "cases"].some((key) => params.has(key))) {
      // A legacy fragment supplies a default scope only without explicit catalog parameters.
      search.value = "";
      subject.value = category;
    }
    filterProjects({ categoryFragment: Boolean(category) });
  }

  search.addEventListener("input", () => filterProjects());
  subject.addEventListener("change", () => filterProjects());
  caseFilter?.addEventListener("change", () => filterProjects());
  reset.addEventListener("click", () => {
    search.value = "";
    subject.value = "";
    if (caseFilter) caseFilter.checked = false;
    filterProjects({ clearAll: true });
    search.focus();
  });
  if (recovery) recovery.addEventListener("click", () => {
    subject.value = "";
    filterProjects();
    search.focus();
  });
  addEventListener("popstate", restoreLocation);
  addEventListener("hashchange", restoreLocation);

  restoreLocation();
  filters.hidden = false;
  if (caseFilter && caseEntries.size) caseFilter.closest("label").hidden = false;
  document.documentElement.classList.replace("no-js", "js");
})();
