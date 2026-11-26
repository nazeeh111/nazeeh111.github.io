"""Render the complete public repository index without client-side dependencies."""

import html
import re
from urllib.parse import urlsplit


LANGUAGES = frozenset({
    "C", "C++", "C#", "Go", "HTML", "Java", "JavaScript", "Julia", "Lean",
    "MATLAB", "Python", "R", "Rust", "Swift", "TypeScript", "Verilog",
})
SLUG = re.compile(r"[A-Za-z0-9_.-]+\Z")
DISCIPLINES = frozenset({"Creative & everyday tools", "EE & sensing", "Geometry & CAD", "ML & data", "Physics & quantum", "Systems & developer tools"})


def memberships(project, subject):
    values = project.get("subjects", [subject])
    if (not isinstance(values, list) or not values or
            any(not isinstance(v, str) or not v.strip() or "|" in v for v in values) or
            len(set(values)) != len(values) or subject not in values or
            ("subjects" in project and any(v not in DISCIPLINES for v in values))):
        raise ValueError("Invalid project discipline memberships")
    return values


CASE_PATH = re.compile(r"/work/[a-z0-9]+(?:-[a-z0-9]+)*/\Z")


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a nonempty string")
    return value


def _strings(value, field):
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"{field} must be a list of strings")
    return value


def _repository(value):
    value = _text(value, "repository URL")
    parsed = urlsplit(value)
    parts = parsed.path.strip("/").split("/")
    if (parsed.scheme != "https" or parsed.netloc != "github.com"
            or parsed.query or parsed.fragment or parsed.path.endswith("/")
            or len(parts) != 2
            or any(not SLUG.fullmatch(part) or part in (".", "..") for part in parts)):
        raise ValueError("Expected a canonical https://github.com/owner/repository URL")
    return value


def _upstream(value):
    if value is None:
        return None
    value = _text(value, "upstream")
    parts = value.split("/")
    if len(parts) != 2 or any(not SLUG.fullmatch(part) or part in (".", "..") for part in parts):
        raise ValueError("upstream must name owner/repository")
    return value


def _case_links(cases, known_urls):
    if cases is None:
        return {}
    if not isinstance(cases, list):
        raise ValueError("cases must be a list of reviewed case records")
    links = {}
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("Each case must be an object")
        repository = _repository(case.get("repository_url"))
        path = case.get("case_url")
        if not isinstance(path, str) or not CASE_PATH.fullmatch(path):
            raise ValueError("case_url must be a local /work/case-name/ path")
        key = repository.casefold()
        if key not in known_urls:
            raise ValueError("A reviewed case names a repository absent from the catalog")
        if key in links:
            raise ValueError("Duplicate case record for one repository")
        links[key] = path
    return links


def browser_link(action):
    if action is None:
        return ""
    if not isinstance(action, dict):
        raise ValueError("Invalid browser action")
    label = _text(action.get("label"), "browser action label")
    url = _text(action.get("url"), "browser action URL")
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc not in {
        "nazeeh111.github.io", "cascade-flight-intelligence.nazeeh1.chatgpt.site",
        "civicledger.nazeeh1.chatgpt.site",
    }:
        raise ValueError("Expected a reviewed public browser destination")
    return f'<a class="browser-action" href="{html.escape(url, quote=True)}">{html.escape(label)}</a>'


def bracket_plate():
    return '''<figure class="bracket-plate"><picture>
<source media="(max-width: 650px)" srcset="/assets/featured/solidframe-bracket/isometric-mobile.webp">
<img src="/assets/featured/solidframe-bracket/bracket.png" width="1920" height="1132"
 alt="Isometric view of the editable right-angle bracket with a two-by-two hole grid on each flange.">
</picture><figcaption><span>100 × 80 × 60 mm · 6 mm stock · Ø8 mm through-holes</span>
<span><a href="/assets/featured/solidframe-bracket/bracket-mobile.png">Dimensioned drawing</a> ·
<a href="https://github.com/nazeeh111/SolidFrame/tree/0ffd50b029138097ea204cc7757f4280a44ff2e3/docs/presentation">Drawing source</a></span></figcaption></figure>'''


def render(catalog, template, cases=None):
    """Return complete work/index.html bytes from the existing public catalog.

    cases, when provided, is a list of {repository_url, case_url} records.
    Source/foundation credit is explicit; absence of upstream is never an
    assertion of original authorship. The renderer writes no files.
    """
    if not isinstance(catalog, dict) or not isinstance(catalog.get("projects"), list):
        raise ValueError("catalog must contain a projects list")
    if not catalog["projects"]:
        raise ValueError("The public work catalog cannot be empty")
    if not isinstance(template, str):
        raise ValueError("template must be text")
    for token in ("{{PROJECTS}}", "{{SUBJECTS}}", "{{COUNT}}"):
        if token not in template:
            raise ValueError(f"Missing work template token: {token}")

    projects = []
    known = set()
    for project in catalog["projects"]:
        if not isinstance(project, dict):
            raise ValueError("Each project must be an object")
        if project.get("visibility") == "private":
            raise ValueError("A private repository cannot enter the public work catalog")
        name = _text(project.get("name"), "project name")
        summary = _text(project.get("summary"), "project summary")
        subject = _text(project.get("subject"), "project subject")
        url = _repository(project.get("url"))
        key = url.casefold()
        if key in known:
            raise ValueError("Duplicate repository URL in work catalog")
        known.add(key)
        topics = _strings(project.get("topics", []), "project topics")
        aliases = _strings(project.get("aliases", []), "project aliases")
        kind = project.get("kind", "")
        if not isinstance(kind, str):
            raise ValueError("project kind must be text")
        upstream = _upstream(project.get("upstream"))
        projects.append({"name": name, "summary": summary, "subject": subject,
                         "url": url, "kind": kind, "topics": topics,
                         "aliases": aliases, "browser_action": project.get("browser_action"), "upstream": upstream, "subjects": memberships(project, subject)})

    case_links = _case_links(cases, known)
    # Optional editorial order uses canonical identities. Unselected work keeps
    # the stable alphabetical order; every repository remains present once.
    featured = _strings(catalog.get("featured_repositories", []), "featured_repositories")
    priority = {}
    for position, repository in enumerate(featured):
        key = _repository(repository).casefold()
        if key not in known or key in priority:
            raise ValueError("Featured repository must be known and unique")
        priority[key] = position
    escape = lambda value: html.escape(str(value), quote=True)
    entries = []
    for project in sorted(projects, key=lambda item: (
            priority.get(item["url"].casefold(), len(priority)),
            item["name"].casefold(), item["url"].casefold())):
        url = project["url"]
        upstream = project["upstream"]
        words = [project["name"], project["summary"], *project["subjects"],
                 project["kind"], *project["topics"], *project["aliases"]]
        if upstream:
            words.extend([upstream, "fork"])
        identity = re.sub(r"[^a-z0-9]+", "-", url.split("github.com/", 1)[1].casefold()).strip("-")
        credit = (f'<p class="upstream">Based on <a href="https://github.com/{escape(upstream)}">'
                  f'{escape(upstream)}</a></p>') if upstream else ""
        technology = (f'<p class="technology">{escape(project["kind"])}</p>'
                      if project["kind"] in LANGUAGES else "")
        case_url = case_links.get(url.casefold())
        case_link = (f'<a class="case-link" href="{escape(case_url)}" '
                     f'aria-label="Read case: {escape(project["name"])}">Read case</a>') if case_url else ""
        action = browser_link(project["browser_action"])
        is_bracket = url == "https://github.com/nazeeh111/SolidFrame" and bool(action)
        feature = ' data-bracket="true"' if is_bracket else ''
        browser = ' data-browser="true"' if action else ''
        if action:
            words.append(project["browser_action"]["label"])
        if is_bracket:
            words.extend(["bracket", "flanges", "hole grids"])
        meta = (f'<div class="project-meta">{action}{case_link}{technology}</div>'
                if action or case_link or technology else "")
        discipline = f'<p class="project-discipline">{escape(project["subject"])}</p>'
        summary = ('Edit the stock or either flange’s hole grid, then rebuild the solid. '
                   'Powered by Chili3D and OpenCascade.' if is_bracket else escape(project["summary"]))
        entries.append(
            f'<li class="project-item" id="repository-{identity}"{feature}{browser} '
            f'data-subject="{escape(project["subject"])}" data-subjects="{escape("|".join(project["subjects"]))}" '
            f'data-search="{escape(" ".join(words))}">\n'
            f'<div class="project-title"><h2><a class="project-wordmark" href="{escape(url)}">'
            f'{escape(project["name"])}</a></h2>{discipline}</div>'
            f'<div class="project-copy"><p class="project-summary">{summary}</p>{credit}</div>'
            f'{meta}{bracket_plate() if is_bracket else ""}</li>'
        )
    subjects = sorted({subject for project in projects for subject in project["subjects"]}, key=str.casefold)
    options = "".join(f'<option value="{escape(subject)}">{escape(subject)}</option>' for subject in subjects)
    values = {"{{PROJECTS}}": "\n".join(entries), "{{SUBJECTS}}": options,
              "{{COUNT}}": str(len(projects))}
    tokens = set(re.findall(r"\{\{[A-Z_]+\}\}", template))
    if tokens - values.keys():
        raise ValueError("Unresolved work template token")
    # Replace template tokens once; project text that resembles a token is data.
    result = re.sub(r"\{\{[A-Z_]+\}\}", lambda match: values[match[0]], template)
    return result.encode("utf-8")


if __name__ == "__main__":
    raise SystemExit("Use python3 scripts/build-site.py --out <new-directory>")
