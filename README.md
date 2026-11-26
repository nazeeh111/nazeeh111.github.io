# Nazeeh Abdul-Hadi's engineering portfolio

[Open the portfolio](https://nazeeh111.github.io/) to follow a four-input neural classifier into two fixed-point Verilog circuits. Scroll through its compiled weights, hardware schedule and reference scores, or use the three section links. Each step remains readable on a phone and without JavaScript. The [work index](https://nazeeh111.github.io/work/) includes 59 public repositories and 13 case studies. The [research library](https://nazeeh111.github.io/research/) contains twelve studies with downloadable sources.

The site uses static HTML, CSS, self-hosted WOFF2 versions of Archivo and IBM Plex Sans, with the original TrueType files available as fallbacks. Figures use recorded data. The homepage also includes a wavelength probe built from PhotonSmith’s 21 stored solutions. [SiliconPilot figure sources and terms](assets/logic/PROVENANCE.md).

## Update the portfolio

Edit `projects.json` for public catalog content, `cases.json` for reviewed case records, `scripts/portfolio.html` for the homepage and `scripts/work.html` for the work index. Build the complete site into a **new directory outside the checkout**, then preview that generation:

```sh
python3 scripts/build-site.py --out /tmp/nazeeh-portfolio-preview
python3 -m http.server 8000 --bind 127.0.0.1 --directory /tmp/nazeeh-portfolio-preview
```

Open `http://127.0.0.1:8000/`. If the output path already exists, choose another new path; the builder refuses to overwrite an earlier generation. It validates the explicit public file list in `scripts/site-inputs.json`, renders the homepage, complete work index, thirteen case pages and research library, and writes a `.build-manifest.json` with output hashes. Unlisted local files are excluded. The builder gives the shared CSS, scripts and social preview content-based URL versions, so new pages request their matching assets even when a visitor has cached the previous design. Add intended new public assets to that file list before building. `build-portfolio.py`, `build-work.py`, `build-cases.py` and `build-research.py` are renderer modules used by this command.

`index.html`, `work/index.html` and `work/*/index.html` are generated deployable documents. The catalog records the source revision behind each entry; a description is not a runtime-validation claim. Keep private repositories and data out of this file. Search includes names, summaries, every declared discipline membership, topics, languages and recorded aliases; its URL preserves the current query, discipline, case-study filter and explicit legacy all parameter for sharing. Case studies only limits results to entries with a reviewed case in `cases.json`. Empty results can recover across disciplines without discarding the query. The work index starts with the five explicitly selected repositories, then lists every remaining repository in stable alphabetical order. `featured_repositories` contains canonical URLs and never creates a duplicate or changes upstream credit; without that optional field the renderer remains alphabetical. Root query, category and case bookmarks migrate to their corresponding routes when JavaScript is available; the static homepage retains direct navigation without it. New figures need accurate captions and provenance in [the original exhibits](assets/PROVENANCE.md) or [selected project cases](assets/featured/evidence.html). Font source and original OFL notices are in `assets/fonts/TECHNICAL-SOURCES.json` and the adjacent family notice files. PhotonSmith’s portable numerical-figure source, values, source ZIP and notices are in `assets/featured/photonsmith-hero/`; the original poster figures remain intact.

The homepage and index use separate `logic.css` and `interior.css` styles over the shared `assets/design/portfolio.css`; the research library keeps its reader layout while sharing the same fonts, palette and navigation. The comparison range reveals retained images rather than rerunning the estimator. Both complete images remain visible without JavaScript. Motion respects reduced-motion preferences. Check the final page on phone and desktop, operate controls from a keyboard, and verify linked applications before publication.

## Preserved project routes

- [`/Caustryn/demo/`](https://nazeeh111.github.io/Caustryn/demo/) is the recorded synthetic radio-inference lab.
- [`/Phaseglass/demo/`](https://nazeeh111.github.io/Phaseglass/demo/) retains the original Phaseglass replay.

Those directories and their supporting evidence remain in this repository so existing links continue to work. The work index links to the current Caustryn recorded lab without replacing either project-specific page. Each project page describes the scope of its claims.

The retained Caustryn screenshot captures its recorded synthetic counterexample; it is no longer the homepage's social preview. The displayed 3.488 m separation is a result of that example, not measured radio-localization accuracy.

## Research library

`/research/` contains one browser-readable article for each of the 12 studies. Each article explains the method, records the results, shows an original study figure, and states the limitations. Equations use native MathML; there is no client-side mathematics library. The 14 PDFs, Markdown report, manuscript-source bundles, and collection ZIP are downloadable. PDFs are compiled from the included sources with synchronized title dates and checked typography. `research/manifest.json` identifies the downloadable manuscript bytes by SHA-256.

The COUNTERPATCH report URL redirects to its canonical study article. Search and topic filters are progressive enhancements: articles, figures, contents links, and downloads work without JavaScript. The complete repository index provides discipline and text filters; project cases and research remain directly navigable.

### Editing

Edit `research/catalog.json`, then run the complete build command above. Both renderers use Python's standard library:

```sh
python3 scripts/build-site.py --out /tmp/nazeeh-portfolio-research-preview
```

This validates and rebuilds the library, study articles, homepage, work index and case pages together. No build is required to serve the checked-in static files.

`date` and `displayDate` contain the owner's selected document dates. The same dates appear in the PDFs and citation years. `dateStatus: "user-specified"` distinguishes these selected dates from independently verified research-history dates; `originalDate` retains the prior manuscript date for provenance.

Each study states its model, evaluation setting, results and limitations. Manuscript sources and numerical evidence are linked where available.
