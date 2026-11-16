const panels = [...document.querySelectorAll(".exhibit")];
const choices = [...document.querySelectorAll("[data-exhibit]")];
const search = document.querySelector("#project-search");
const subject = document.querySelector("#project-subject");
const entries = [...document.querySelectorAll(".project-item")];
const status = document.querySelector("#catalog-status");
const empty = document.querySelector("#catalog-empty");
const catalogToggle = document.querySelector("#catalog-toggle");
let showAll = false;

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

function selectExhibit(id) {
  if (!panels.some((panel) => panel.id === id)) return;
  for (const panel of panels) panel.hidden = panel.id !== id;
  for (const choice of choices)
    choice.setAttribute("aria-pressed", String(choice.dataset.exhibit === id));
}

function filterProjects() {
  const query = words(search.value);
  const category = subject.value;
  const filtering = Boolean(query.length || category);
  let visible = 0;
  for (const [index, entry] of entries.entries()) {
    const match =
      (!category || entry.dataset.subject === category) &&
      query.every((term) => searchableWords.get(entry).some((word) => word.startsWith(term))) &&
      (filtering || showAll || index < 12);
    entry.hidden = !match;
    if (match) visible += 1;
  }
  status.textContent =
    !filtering && !showAll
      ? `${visible} selected projects from ${entries.length} public repositories`
      : `${visible} of ${entries.length} public repositories`;
  catalogToggle.hidden = filtering;
  catalogToggle.textContent = showAll
    ? "Show selected projects"
    : `Browse all ${entries.length} repositories`;
  catalogToggle.setAttribute("aria-expanded", String(showAll));
  empty.hidden = visible > 0;
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
search.addEventListener("input", filterProjects);
subject.addEventListener("change", filterProjects);
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
  if (legacyCategories[fragment]) {
    search.value = "";
    subject.value = legacyCategories[fragment];
    filterProjects();
    document.querySelector("#projects").scrollIntoView();
  }
}
addEventListener("hashchange", restoreFragment);
restoreFragment();
filterProjects();
