"""Build the static public project catalog and the portfolio homepage."""

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def escape(value):
    return html.escape(str(value), quote=True)


def render(catalog, template):
    entries = []
    groups = sorted({project["subject"] for project in catalog["projects"]})
    for project in catalog["projects"]:
        name = escape(project["name"])
        summary = escape(project["summary"])
        searchable = escape(" ".join([project["name"], project["summary"], project["subject"], *project["topics"], *project.get("aliases", [])]).lower())
        upstream = ""
        if project.get("upstream"):
            parent = escape(project["upstream"])
            upstream = f'<p class="upstream">Based on <a href="https://github.com/{parent}">{parent}</a></p>'
        entries.append(f'''<li class="project-item" data-subject="{escape(project['subject'])}" data-search="{searchable}">
<div><h3><a href="{escape(project['url'])}">{name}</a></h3><p>{summary}</p>{upstream}</div>
<span class="project-kind">{escape('Fork' if project.get('upstream') else project['kind'])}</span></li>''')
    options = "".join(f'<option value="{escape(group)}">{escape(group)}</option>' for group in groups)
    result = template.replace("{{PROJECTS}}", "\n".join(entries)).replace("{{SUBJECTS}}", options).replace("{{COUNT}}", str(len(entries)))
    return result.encode("utf-8")


if __name__ == '__main__':
    raise SystemExit('Use python3 scripts/build-site.py --out <new-directory>')
