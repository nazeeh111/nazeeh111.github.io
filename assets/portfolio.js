// Keep legacy bookmarks useful while giving the homepage and work index separate jobs.
const caseRoutes = {
  "case-solidframe": "/work/solidframe/",
  "case-vibescope": "/work/vibescope/",
  "case-qloom": "/work/qloom/",
  "case-photonsmith": "/work/photonsmith/",
  "case-instrumentzero": "/work/instrumentzero/",
  "case-nstack": "/work/nstack/",
  geometry: "/work/solidrift/",
  science: "/research/phaseglass-quantum/",
  systems: "/work/capsulith/",
};
const categories = {
  "project-geometry": "Geometry & CAD",
  "project-sensing": "EE & sensing",
  "project-data-and-motion": "ML & data",
  "project-systems": "Systems & developer tools",
  "project-scientific-tools": "Physics & quantum",
};
function legacyDestination() {
  const source = new URL(location.href),
    hash = source.hash.slice(1);
  if (Object.hasOwn(caseRoutes, hash))
    return new URL(caseRoutes[hash], location.origin);
  if (Object.hasOwn(categories, hash)) {
    const target = new URL("/work/", location.origin);
    target.searchParams.set("discipline", categories[hash]);
    target.hash = "projects";
    return target;
  }
  if (
    hash === "projects" ||
    ["q", "discipline", "all"].some((key) => source.searchParams.has(key))
  ) {
    const target = new URL("/work/", location.origin);
    for (const key of ["q", "discipline", "all"])
      if (source.searchParams.has(key))
        target.searchParams.set(key, source.searchParams.get(key));
    target.hash = "projects";
    return target;
  }
  return null;
}
const destination = legacyDestination();
if (destination) location.replace(destination.href);
const reveal = document.querySelector("#frame-reveal"),
  comparison = document.querySelector(".frame-comparison"),
  comparisonControl = document.querySelector(".comparison-control");
if (reveal && comparison && comparisonControl) {
  function updateComparison() {
    const value = Number(reveal.value);
    comparison.style.setProperty("--reveal", value + "%");
    reveal.setAttribute("aria-valuetext", value + "% enhanced view");
  }
  reveal.addEventListener("input", updateComparison);
  updateComparison();
  comparison.classList.add("is-ready");
  comparisonControl.hidden = false;
}
addEventListener("hashchange", () => {
  const target = legacyDestination();
  if (target) location.replace(target.href);
});
document.documentElement.classList.replace("no-js", "js");
