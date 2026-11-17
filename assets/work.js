(() => {
  "use strict";

  const search = document.querySelector("#project-search");
  const subject = document.querySelector("#project-subject");
  const filters = document.querySelector("#work-filters");
  const status = document.querySelector("#catalog-status");
  const empty = document.querySelector("#catalog-empty");
  const reset = document.querySelector("#reset-search");
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

  function writeLocation({ categoryFragment = false } = {}) {
    const url = new URL(location.href);
    for (const [key, value] of [
      ["q", search.value.trim()],
      ["discipline", subject.value],
    ]) {
      if (value) url.searchParams.set(key, value);
      else url.searchParams.delete(key);
    }
    // The complete index is now the default. Old all=1 URLs remain equivalent.
    url.searchParams.delete("all");
    if (categoryFragment) url.hash = "projects";
    if (url.href !== location.href) history.replaceState(null, "", url);
  }

  function filterProjects(options = {}) {
    const query = words(search.value);
    const category = subject.value;
    let visible = 0;
    for (const entry of entries) {
      const matches =
        (!category || entry.dataset.subject === category) &&
        query.every((term) =>
          searchable.get(entry).some((word) => word.startsWith(term)),
        );
      entry.hidden = !matches;
      if (matches) visible += 1;
    }
    const filtering = Boolean(search.value.trim() || category);
    status.textContent = filtering
      ? `${visible} of ${entries.length} public repositories`
      : `${entries.length} public repositories`;
    empty.hidden = visible !== 0;
    reset.hidden = !filtering;
    writeLocation(options);
  }

  function restoreLocation() {
    const params = new URL(location.href).searchParams;
    search.value = params.get("q") || "";
    const requested = params.get("discipline") || "";
    subject.value = validSubjects.has(requested) ? requested : "";
    const fragment = location.hash.slice(1);
    const category = Object.hasOwn(categories, fragment)
      ? categories[fragment]
      : null;
    if (category && validSubjects.has(category)) {
      // Old category anchors took precedence over q. Normalize the fragment so
      // subsequent typing/reloading does not repeatedly discard a new query.
      search.value = "";
      subject.value = category;
    }
    filterProjects({ categoryFragment: Boolean(category) });
  }

  search.addEventListener("input", () => filterProjects());
  subject.addEventListener("change", () => filterProjects());
  reset.addEventListener("click", () => {
    search.value = "";
    subject.value = "";
    filterProjects();
    search.focus();
  });
  addEventListener("popstate", restoreLocation);
  addEventListener("hashchange", restoreLocation);

  restoreLocation();
  filters.hidden = false;
  document.documentElement.classList.replace("no-js", "js");
})();
