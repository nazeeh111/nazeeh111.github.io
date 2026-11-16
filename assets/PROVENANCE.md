# Portfolio figures and identity

## Solidrift

`solidrift-comparison.svg`, its phone variant, and the separate `solidrift-input.svg` / `solidrift-union.svg` panels recompose the two mesh projection panels from the preserved original `sources/solidrift-profile.svg`. Geometry, source polygon coordinates and recorded FLOAT output are unchanged. The source illustration comes from the public profile repository at its pre-redesign revision; the original projections derive from Solidrift's [native report](https://github.com/nazeeh111/Solidrift/blob/8fc9e23471a18165d73646e290700cc10d351eea/tests/fixtures/native-report.json) and [projection generator](https://github.com/nazeeh111/Solidrift/blob/8fc9e23471a18165d73646e290700cc10d351eea/tools/tour/generate-geometry.py).

Both pictured panels show the original 132-triangle stage. They do not depict the later 12-triangle witness or a fresh Blender execution. Layout and labels are changed by `scripts/build-geometry-figure.py`; run it to reproduce the figure from the preserved source SVG. The original operands descend from Manifold regression fixtures under Apache-2.0. Their [license](sources/solidrift-fixture-LICENSE.txt) is retained.

## Capsulith

`capsulith-restored.jpg` is an actual browser screenshot of the public [image workbench](https://nazeeh111.github.io/Capsulith/studio/image.html), observed November 16, 2026. “Load & run example” executed the prepared QOI decoder. “Reopen in a fresh worker” then reported that 49,152 RGBA bytes matched the prior native output, and that the native allocation was freed. The selected pixel at (64, 48) read RGBA (126, 135, 250, 255). The screenshot records that execution; it is not an independent native-code oracle or proof of arbitrary-binary equivalence or isolation.

Orbit is prepared example artwork. QOI is by Dominic Szablewski and contributors, under MIT. Runtime emulation uses Unicorn.js and Unicorn; Capsulith's runtime is GPL-2.0-only. See the project's [complete notices and provenance](https://nazeeh111.github.io/Capsulith/THIRD_PARTY_NOTICES.md). No third-party implementation is copied into this website.

## Research

The existing `research/figures/phaseglass-quantum.webp` is the study's finite-shot simulation across source-copy budgets. It is distinct from the exact two-copy theorem. The new HTML comparison displays the exact study values, 75% success for the joint sector measurement and a certified separate-copy upper bound below 66.91%, with the same two total copies and specified state/symmetry assumptions. See the [article and manuscript](../research/phaseglass-quantum/) for the exact problem, scope and empirical limits. Source papers, dates, figures, citations and downloadable bytes are retained from the existing research library.

## Identity

`identity.png` retains Nazeeh's existing waveform N avatar from the public profile repository. No new authorship or credential is implied by the redesign.
