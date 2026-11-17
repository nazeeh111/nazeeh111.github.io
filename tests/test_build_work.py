"""Contract checks for the complete, escaped static work index."""
import copy
import importlib.util
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_work", ROOT / "scripts/build-work.py")
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)
TEMPLATE = (ROOT / "scripts/work.html").read_text()


class Index(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.projects = []
        self.links = []
        self.inputs = []
        self.ids = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "li" and attrs.get("class") == "project-item":
            self.projects.append(attrs)
        if tag == "a":
            self.links.append(attrs)
        if tag == "input":
            self.inputs.append(attrs)


def project(name, repository, **changes):
    value = {"name": name, "summary": "Inspect a bounded numerical example.",
             "url": "https://github.com/nazeeh111/" + repository,
             "subject": "Physics & quantum", "kind": "Python",
             "topics": ["numerical-computing"], "aliases": [], "upstream": None}
    value.update(changes)
    return value


class WorkBuilderTests(unittest.TestCase):
    def test_all_projects_are_static_sorted_and_counted_without_selected_prefix(self):
        catalog = {"projects": [project("Zulu", "Zulu"), project("alpha", "alpha")]}
        original = copy.deepcopy(catalog)
        data = builder.render(catalog, TEMPLATE)
        parsed = Index(data.decode())
        self.assertEqual([entry["id"] for entry in parsed.projects],
                         ["repository-nazeeh111-alpha", "repository-nazeeh111-zulu"])
        self.assertTrue(all("hidden" not in entry for entry in parsed.projects))
        self.assertIn(b"2 public repositories", data)
        self.assertNotIn(b"Browse all", data)
        self.assertIn(b'id="work-filters" hidden', data)
        self.assertIn(b'<noscript><p>All repositories are listed below.</p></noscript>', data)
        self.assertEqual(len(parsed.ids), len(set(parsed.ids)))
        self.assertEqual(catalog, original)
        self.assertEqual(data, builder.render(catalog, TEMPLATE))

    def test_untrusted_names_summaries_aliases_and_subjects_are_escaped(self):
        name = 'A "quoted" <script>alert(1)</script>'
        summary = 'Read <img src=x onerror=alert(1)> & keep the source.'
        alias = 'old" data-extra="injected'
        subject = 'Geometry & "CAD"'
        catalog = {"projects": [project(name, "safe", summary=summary, aliases=[alias], subject=subject)]}
        data = builder.render(catalog, TEMPLATE)
        parsed = Index(data.decode())
        self.assertIn(b"&lt;script&gt;", data)
        self.assertNotIn(b"<script>alert(1)", data)
        self.assertNotIn(b"<img src=x", data)
        self.assertEqual(parsed.projects[0]["data-subject"], subject)
        self.assertIn(alias, parsed.projects[0]["data-search"])
        self.assertNotIn("data-extra", parsed.projects[0])
        self.assertEqual(len(parsed.inputs), 1)

    def test_template_like_project_text_remains_literal_data(self):
        catalog = {"projects": [project("{{COUNT}}", "literal", aliases=["{{SUBJECTS}}"])]}
        data = builder.render(catalog, TEMPLATE).decode()
        parsed = Index(data)
        self.assertIn('>{{COUNT}}</a>', data)
        self.assertIn("{{SUBJECTS}}", parsed.projects[0]["data-search"])
        self.assertIn("1 public repositories", data)

    def test_upstream_technology_and_reviewed_case_are_distinct(self):
        catalog = {"projects": [project("Adapted tool", "adapted", upstream="upstream/tool"),
                                 project("Unclassified", "plain", kind="Local app")]}
        cases = [{"repository_url": "https://github.com/nazeeh111/adapted",
                  "case_url": "/work/adapted-tool/"}]
        data = builder.render(catalog, TEMPLATE, cases).decode()
        parsed = Index(data)
        self.assertIn('href="https://github.com/upstream/tool"', data)
        self.assertIn('class="upstream">Based on', data)
        self.assertEqual(data.count('class="technology">Python</p>'), 1)
        self.assertNotIn('class="technology">Local app', data)
        self.assertNotIn("Original project", data)
        self.assertEqual([link["href"] for link in parsed.links if link.get("class") == "case-link"],
                         ["/work/adapted-tool/"])
        for url in [item["url"] for item in catalog["projects"]]:
            self.assertEqual(sum(link.get("href") == url for link in parsed.links), 1)
        self.assertNotIn('class="case-link"', builder.render(catalog, TEMPLATE).decode())

    def test_aliases_and_technology_enter_search_without_becoming_authorship(self):
        catalog = {"projects": [project("Faultsplice", "Aetiory", aliases=["Aetiory"], kind="Rust")]}
        parsed = Index(builder.render(catalog, TEMPLATE).decode())
        text = parsed.projects[0]["data-search"]
        for value in ["Faultsplice", "Aetiory", "Rust", "numerical-computing"]:
            self.assertIn(value, text)
        self.assertNotIn("original", text.lower())

    def test_invalid_public_inputs_and_case_paths_fail_without_mutating_model(self):
        base = {"projects": [project("One", "one")]}
        bad = []
        for value in ["javascript:alert(1)", "https://github.com/a/b?next=x", "https://evil.test/a/b"]:
            model = copy.deepcopy(base);model["projects"][0]["url"] = value;bad.append((model, None))
        model = copy.deepcopy(base);model["projects"].append(copy.deepcopy(model["projects"][0]));bad.append((model, None))
        model = copy.deepcopy(base);model["projects"][0]["visibility"] = "private";bad.append((model, None))
        for path in ["//evil.test/work/a/", "/work/../other/", "/work/%2e%2e/", "/work/one/?q=x"]:
            bad.append((copy.deepcopy(base), [{"repository_url": base["projects"][0]["url"], "case_url": path}]))
        bad.append((copy.deepcopy(base), [{"repository_url": "https://github.com/nazeeh111/missing", "case_url": "/work/missing/"}]))
        case = {"repository_url": base["projects"][0]["url"], "case_url": "/work/one/"}
        bad.append((copy.deepcopy(base), [case, case]))
        for model, cases in bad:
            with self.subTest(model=model, cases=cases):
                snapshot = copy.deepcopy(model)
                with self.assertRaises(ValueError):
                    builder.render(model, TEMPLATE, cases)
                self.assertEqual(model, snapshot)


if __name__ == "__main__":
    unittest.main()
