# Nazeeh Abdul-Hadi's engineering portfolio

[`nazeeh111.github.io`](https://nazeeh111.github.io/) brings together working engineering tools, source code and research. The opening cases show a recorded geometry failure, an exact quantum-measurement result, and an executed native image decoder. Six further cases connect CAD, video measurement, quantum compilation, photonics, signal analysis and developer tooling to their actual artifacts. A searchable catalog spans the 66 public repositories observed on November 16, 2026, distinguishing upstream forks and foundations.

The checked-in site uses static HTML, CSS, self-hosted Rethink Sans and a small local JavaScript enhancement. It has no framework, tracking or account requirement. Without JavaScript, all selected cases and repository links remain available. Preview the checked-in files with `python3 -m http.server 8000 --bind 127.0.0.1`, then open `http://127.0.0.1:8000/`.

## Update the portfolio

Edit `projects.json` for public catalog content and `scripts/portfolio.html` for page structure. Build the complete site into a **new directory outside the checkout**, then preview that generation:

```sh
python3 scripts/build-site.py --out /tmp/nazeeh-portfolio-preview
python3 -m http.server 8000 --bind 127.0.0.1 --directory /tmp/nazeeh-portfolio-preview
```

Open `http://127.0.0.1:8000/`. If the output path already exists, choose another new path; the builder refuses to overwrite an earlier generation. It validates the explicit public file list in `scripts/site-inputs.json`, renders both the homepage and research library, and writes a `.build-manifest.json` with output hashes. Unlisted local files are excluded. Add intended new public assets to that file list before building. `build-portfolio.py` and `build-research.py` are renderer modules used by this command.

`index.html` is the generated deployable document. The catalog records the source revision behind each entry; a description is not a runtime-validation claim. Keep private repositories and data out of this file. Search includes names, summaries, disciplines, topics, languages and recorded aliases; its URL preserves the current query and discipline for sharing. A curated selection opens first; filtering searches the complete catalog. New figures need accurate captions and provenance in [the original exhibits](assets/PROVENANCE.md) or [selected project cases](assets/featured/evidence.html). Font source and license are in `assets/fonts/`.

Homepage styling and scripts are independent of the research library. Check the final page on phone and desktop, operate controls from a keyboard, and verify linked applications before publication.

## Preserved project routes

- [`/Caustryn/demo/`](https://nazeeh111.github.io/Caustryn/demo/) is the recorded synthetic radio-inference lab.
- [`/Phaseglass/demo/`](https://nazeeh111.github.io/Phaseglass/demo/) retains the original Phaseglass replay.

Those directories and their supporting evidence remain in this repository so existing links continue to work. The root index links to the current Caustryn recorded lab without replacing either project-specific page. Each project page describes the scope of its claims.

The retained Caustryn screenshot captures its recorded synthetic counterexample; it is no longer the homepage's social preview. The displayed 3.488 m separation is a result of that example, not measured radio-localization accuracy.

## Research library

`/research/` contains one browser-readable article for each of the 12 studies. Each article explains the method, records the results, shows an original study figure, and states the limitations. Equations use native MathML; there is no client-side mathematics library. The 14 PDFs, Markdown report, manuscript-source bundles, and collection ZIP are downloadable. PDFs are compiled from the included sources with synchronized title dates and checked typography. `research/manifest.json` identifies the downloadable manuscript bytes by SHA-256.

The COUNTERPATCH report URL redirects to its canonical study article. Search and topic filters are progressive enhancements: articles, figures, contents links, and downloads work without JavaScript. The homepage retains the existing project links and adds category navigation.

### Editing

Edit `research/catalog.json`, then run the complete build command above. Both renderers use Python's standard library:

```sh
python3 scripts/build-site.py --out /tmp/nazeeh-portfolio-research-preview
```

This validates and rebuilds the library, study articles and homepage together. No build is required to serve the checked-in static files.

`date` and `displayDate` contain the owner's selected document dates. The same dates appear in the PDFs and citation years. `dateStatus: "user-specified"` distinguishes these selected dates from independently verified research-history dates; `originalDate` retains the prior manuscript date for provenance.

Each study states its model, evaluation setting, results and limitations. Manuscript sources and numerical evidence are linked where available.
