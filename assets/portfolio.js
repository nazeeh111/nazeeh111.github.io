// Keep legacy bookmarks useful while giving the homepage and work index separate jobs.
const caseRoutes = {
  "case-solidframe": "/work/solidframe/",
  "case-vibescope": "/work/vibescope/",
  "case-qloom": "/work/qloom/",
  "case-photonsmith": "/work/photonsmith/",
  "case-instrumentzero": "/work/instrumentzero/",
  "case-nstack": "/work/nstack/",
  "case-materialmind": "/work/materialmind/",
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
  const explicitCatalog = ["q", "discipline", "all"].some((key) => source.searchParams.has(key));
  if (explicitCatalog || hash === "projects") {
    const target = new URL("/work/", location.origin);
    for (const key of ["q", "discipline", "all"])
      if (source.searchParams.has(key)) target.searchParams.set(key, source.searchParams.get(key));
    target.hash = "projects";
    return target;
  }
  if (Object.hasOwn(caseRoutes, hash)) return new URL(caseRoutes[hash], location.origin);
  if (Object.hasOwn(categories, hash)) {
    const target = new URL("/work/", location.origin);
    target.searchParams.set("discipline", categories[hash]);
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

const spectrum = document.querySelector('.spectrum-probe');
if (spectrum) {
  const samples = [...spectrum.querySelectorAll('circle[data-nm]')];
  const slider = spectrum.querySelector('input');
  const value = spectrum.querySelector('output');
  function inspectWavelength() {
    const selected = samples[slider.valueAsNumber];
    for (const sample of samples) sample.classList.toggle('peak', sample === selected);
    const reading = selected.dataset.nm + ' nm · ' + selected.dataset.percent + '% into order +1';
    value.textContent = reading;
    slider.setAttribute('aria-valuetext', reading);
  }
  slider.addEventListener('input', inspectWavelength);
  inspectWavelength();
  slider.closest('label').hidden = false;
}

// Scrolling changes the evidence on the reading desk. Small screens and the
// script-free document keep each plate beside its own explanation.
const desk = document.querySelector('.logic-story');
if (desk) {
  const chapters = [...desk.querySelectorAll('.chapter[data-image]')];
  const navigation = [...desk.querySelectorAll('.story-rail a')];
  const viewer = desk.querySelector('.viewer');
  const image = viewer.querySelector('img');
  const narrowSource = viewer.querySelector('source');
  const caption = viewer.querySelector('#logic-caption');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let active;
  function reflectPosition() {
    const line = Math.min(innerHeight * .48, 420);
    const selected = chapters.filter(chapter => chapter.getBoundingClientRect().top <= line).at(-1) || chapters[0];
    if (active === selected) return;
    const initial = !active;
    active = selected;
    const plate = selected.querySelector('img');
    const source = selected.querySelector('picture source');
    for (const name of ['srcset', 'width', 'height']) {
      narrowSource.setAttribute(name, source.getAttribute(name));
    }
    image.src = plate.getAttribute('src');
    image.width = Number(plate.getAttribute('width'));
    image.height = Number(plate.getAttribute('height'));
    image.alt = plate.alt;
    caption.textContent = {model: 'Compiled logical network', schedule: 'Core clock allocation', verification: 'Reference score words'}[selected.dataset.image];
    navigation.forEach(link => {
      if (link.hash === '#' + selected.id) link.setAttribute('aria-current', 'step');
      else link.removeAttribute('aria-current');
    });
    if (!initial && !reduced.matches && image.animate) {
      image.animate([{opacity:.55, transform:'translateY(5px)'},{opacity:1, transform:'translateY(0)'}],{duration:180,easing:'ease-out'});
    }
  }
  reflectPosition();
  viewer.hidden = false;
  desk.classList.add('enhanced');
  let pending = false;
  addEventListener('scroll', () => {
    if (pending) return;
    pending = true;
    requestAnimationFrame(() => {
      pending = false;
      reflectPosition();
    });
  }, {passive:true});
  addEventListener('resize', reflectPosition, {passive:true});
}
