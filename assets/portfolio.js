const panels = [...document.querySelectorAll(".exhibit")];
const choices = [...document.querySelectorAll("[data-exhibit]")];
const search = document.querySelector("#project-search");
const subject = document.querySelector("#project-subject");
const entries = [...document.querySelectorAll(".project-item")];
const status = document.querySelector("#catalog-status");
const empty = document.querySelector("#catalog-empty");
const catalogToggle = document.querySelector("#catalog-toggle");
const emptyMessage = document.querySelector("#catalog-empty-message");
const searchAll = document.querySelector("#search-all-disciplines");
let showAll = false;

// Keep a catalog view shareable without requiring a server or client router.
function readCatalogLocation() {
  const params = new URL(location.href).searchParams;
  search.value = params.get("q") || "";
  const requestedSubject = params.get("discipline") || "";
  subject.value = [...subject.options].some((option) => option.value === requestedSubject)
    ? requestedSubject
    : "";
  showAll = params.get("all") === "1";
}

function writeCatalogLocation() {
  const url = new URL(location.href);
  for (const [key, value] of [
    ["q", search.value.trim()],
    ["discipline", subject.value],
    ["all", showAll ? "1" : ""],
  ]) {
    if (value) url.searchParams.set(key, value);
    else url.searchParams.delete(key);
  }
  if (url.href !== location.href) history.replaceState(null, "", url);
}

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
const searchableWords = new Map(entries.map((entry) => [entry, words(entry.dataset.search)]));
const disciplines = new Map(entries.map((entry) => [entry, (entry.dataset.subjects || entry.dataset.subject).split("|")]));

function selectExhibit(id) {
  if (!panels.some((panel) => panel.id === id)) return;
  for (const panel of panels) panel.hidden = panel.id !== id;
  for (const choice of choices)
    choice.setAttribute("aria-pressed", String(choice.dataset.exhibit === id));
}

function filterProjects({ updateLocation = true } = {}) {
  const query = words(search.value);
  const category = subject.value;
  const filtering = Boolean(query.length || category);
  let visible = 0;
  let matchesAcrossDisciplines = 0;
  for (const [index, entry] of entries.entries()) {
    const queryMatches = query.every((term) => searchableWords.get(entry).some((word) => word.startsWith(term)));
    if (queryMatches) matchesAcrossDisciplines += 1;
    const match =
      (!category || disciplines.get(entry).includes(category)) &&
      queryMatches &&
      (filtering || showAll || index < 12);
    entry.hidden = !match;
    if (match) visible += 1;
  }
  status.textContent =
    !filtering && !showAll
      ? `${visible} selected projects from ${entries.length} public repositories`
      : `${visible} of ${entries.length} public repositories${category ? ` · ${category}` : ""}`;
  catalogToggle.hidden = filtering;
  catalogToggle.textContent = showAll
    ? "Show selected projects"
    : `Browse all ${entries.length} repositories`;
  catalogToggle.setAttribute("aria-expanded", String(showAll));
  empty.hidden = visible > 0;
  emptyMessage.textContent = category
    ? `No projects match${search.value.trim() ? ` “${search.value.trim()}”` : ""} in ${category}.`
    : "No projects match this search.";
  searchAll.hidden = !(visible === 0 && category && query.length && matchesAcrossDisciplines > 0);
  if (updateLocation) writeCatalogLocation();
}

for (const choice of choices)
  choice.addEventListener("click", () => {
    selectExhibit(choice.dataset.exhibit);
    history.replaceState(null, "", `#${choice.dataset.exhibit}`);
  });
catalogToggle.addEventListener("click", () => {
  showAll = !showAll;
  filterProjects();
});
search.addEventListener("input", () => filterProjects());
subject.addEventListener("change", () => filterProjects());
searchAll.addEventListener("click", () => {
  subject.value = "";
  filterProjects();
  search.focus();
});
document.querySelector("#reset-search").addEventListener("click", () => {
  search.value = "";
  subject.value = "";
  showAll = false;
  filterProjects();
  search.focus();
});
document.documentElement.classList.replace("no-js", "js");
const requested = location.hash.slice(1);
selectExhibit(panels.some((panel) => panel.id === requested) ? requested : "geometry");
const legacyCategories = {
  "project-geometry": "Geometry & CAD",
  "project-sensing": "EE & sensing",
  "project-data-and-motion": "ML & data",
  "project-systems": "Systems & developer tools",
  "project-scientific-tools": "Physics & quantum",
};
function restoreFragment() {
  const fragment = location.hash.slice(1);
  selectExhibit(fragment);
  if (Object.hasOwn(legacyCategories, fragment)) {
    const url = new URL(location.href);
    const explicitCatalog = ["q", "discipline", "all"].some((key) => url.searchParams.has(key));
    if (!explicitCatalog) {
      search.value = "";
      subject.value = legacyCategories[fragment];
    }
    // Legacy bookmarks supply an initial scope, then use the canonical catalog
    // anchor so a later recovery or reset survives reload and shared links.
    url.hash = "projects";
    history.replaceState(null, "", url);
    filterProjects();
    document.querySelector("#projects").scrollIntoView();
  }
}
addEventListener("hashchange", restoreFragment);
addEventListener("popstate", () => {
  readCatalogLocation();
  filterProjects({ updateLocation: false });
  restoreFragment();
});
readCatalogLocation();
restoreFragment();
filterProjects({ updateLocation: false });
