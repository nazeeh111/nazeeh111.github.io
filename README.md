# Nazeeh Abdul-Hadi's engineering portfolio

[`nazeeh111.github.io`](https://nazeeh111.github.io/) brings together working engineering tools, source code and research. The opening cases show a recorded geometry failure, an exact quantum-measurement result, and an executed native image decoder. A searchable catalog spans the 66 public repositories observed on November 16, 2026, distinguishing upstream forks and foundations.

The checked-in site uses static HTML, CSS and a small local JavaScript enhancement. It has no framework, external fonts, tracking or account requirement. Without JavaScript, all selected cases and repository links remain available. Preview with `python3 -m http.server 8000 --bind 127.0.0.1`, then open `http://127.0.0.1:8000/`.

## Update the portfolio

Edit `projects.json` for public catalog content and `scripts/portfolio.html` for page structure, then run:

```sh
python3 scripts/build-site.py --out /tmp/portfolio-generation
```

`index.html` in the new generation is the rendered homepage. The checked-in site remains unchanged. The catalog records the source revision behind each entry; a description is not a runtime-validation claim. Keep private repositories and data out of this file. Search includes names, summaries, disciplines, topics, languages and recorded aliases. A curated selection opens first; filtering searches the complete catalog. New figures need accurate captions and an entry in [asset provenance](assets/PROVENANCE.md).

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

Edit `research/catalog.json`, then run:

```sh
python3 scripts/build-site.py --out /tmp/portfolio-generation
```

The reviewed `scripts/site-inputs.json` lists every public input to include; add a new public file there deliberately. Unlisted local files are never read or copied. The inventory also works from an extracted source archive without Git. The standard-library build validates the catalog and paper hashes, renders the homepage, library and study articles, then writes a complete copy to a fresh directory outside the checkout. Use a new output path on each run. Existing site files and earlier generations are never overwritten. A `.build-manifest.json` appears last; if a write is interrupted, an incomplete output directory may remain without that marker and a retry needs a new path. The manifest records file hashes, not authorship or deployment. Input files should remain stable while captured. Paper hashes come from the research manifest; source ZIP integrity is checked and their exact bytes recorded in the output manifest, but no independent expected source-ZIP hashes are supplied. No build is required to serve the checked-in static files.

`date` and `displayDate` contain the owner's selected document dates. The same dates appear in the PDFs and citation years. `dateStatus: "user-specified"` distinguishes these selected dates from independently verified research-history dates; `originalDate` retains the prior manuscript date for provenance.

Each study states its model, evaluation setting, results and limitations. Manuscript sources and numerical evidence are linked where available.
