# Nazeeh Abdul-Hadi's project index

This repository serves [`nazeeh111.github.io`](https://nazeeh111.github.io/) as a short entry point to selected public projects. Its root page distinguishes browser experiments from tools that run locally; the [GitHub profile](https://github.com/nazeeh111) and [repository list](https://github.com/nazeeh111?tab=repositories) provide the wider portfolio.

The root page is a static HTML document with no build step, external scripts, fonts, tracking, or account requirement. Preview locally with `python3 -m http.server 8000 --bind 127.0.0.1`, then open `http://127.0.0.1:8000/`. Project links point to their own repositories or hosted pages for source, setup, evidence and limits.

## Preserved project routes

- [`/Caustryn/demo/`](https://nazeeh111.github.io/Caustryn/demo/) is the recorded synthetic radio-inference lab.
- [`/Phaseglass/demo/`](https://nazeeh111.github.io/Phaseglass/demo/) retains the original Phaseglass replay.

Those directories and their supporting evidence remain in this repository so existing links continue to work. The root index links to the current Caustryn recorded lab without replacing either project-specific page. Each project page describes the scope of its claims.

The index's featured Caustryn screenshot is a capture of its recorded synthetic counterexample. The displayed 3.488 m separation is a result of that example, not measured radio-localization accuracy.

## Research library

`/research/` contains one browser-readable article for each of the 12 studies. Each article explains the method, records the results, shows an original study figure, and states the limitations. Equations use native MathML; there is no client-side mathematics library. The 14 PDFs, Markdown report, manuscript-source bundles, and collection ZIP are downloadable. PDFs are compiled from the included sources with synchronized title dates and checked typography. `research/manifest.json` identifies the downloadable manuscript bytes by SHA-256.

The COUNTERPATCH report URL redirects to its canonical study article. Search and topic filters are progressive enhancements: articles, figures, contents links, and downloads work without JavaScript. The homepage retains the existing project links and adds category navigation.

### Editing

Edit `research/catalog.json`, then run:

```sh
python3 scripts/build-research.py
```

The generator uses Python's standard library. It rebuilds the library and study articles; the homepage and shared CSS are edited directly. No build is required to serve the checked-in static files.

`date` and `displayDate` contain the owner's selected document dates. The same dates appear in the PDFs and citation years. `dateStatus: "user-specified"` distinguishes these selected dates from independently verified research-history dates; `originalDate` retains the prior manuscript date for provenance.

The public collection distinguishes exact results in restricted models, simulated findings, preliminary work, and missed performance targets. It makes no journal-acceptance or external-peer-review claim.
