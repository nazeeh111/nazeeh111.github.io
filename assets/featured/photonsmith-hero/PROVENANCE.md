# Source and figure meaning

Source: [PhotonSmith retained design](https://github.com/nazeeh111/PhotonSmith/blob/13912d9d640938acf8ce299a152298666ae61d44/experiments/designs/interactive-refined-1550nm.json), revision `13912d9d640938acf8ce299a152298666ae61d44`, SHA-256 `bf63ba3ebec2013dde9f10cbd65fa438634d71abd1bbf504577701dbd8a23b1e`.

The original source has 733,968 bytes. The bundled 203,779-byte plotted-data extraction preserves every value used by the figures and omits unused imaginary field, auxiliary powers, validation and training metadata. Its SHA-256 is `21c935558d8fe79e937e47c959f7d6288dc563c3671fc4440a196269b80055f7`. The extractor verifies the original source hash and the exact extraction hash. The renderer refuses a changed extraction or font and verifies the recorded original revision/hash/URL.

The field shows all 97 × 96 stored real values, `Re(Ey)` relative to unit incident amplitude, not intensity. This is the legacy M9 two-dimensional formulation; search used M5. The experimental stable backend refuses interior fields and is not the source of this field.

Color maps linearly from −2 to +2 around zero. Source values are approximately −1.930799…+1.634272, so none is clipped or normalized to its own maximum. Each stored sample occupies a flat cell bounded by coordinate midpoints, with half-interval support at the outer edges. That display support adds no calculated samples. Stored x is 0…2.375 µm; cell support is −0.0125…2.3875 µm, one 2.4 µm period. Stored z is −0.45…1.35 µm; support is −0.459375…1.359375 µm. z increases downward. Both axes have equal physical scale.

The continuous geometry outlines come from the exact saved bar widths, centres, 2.4 µm period and 0.3 µm layer height. Their membership reproduces every stored binary permittivity sample. This is a geometry check, not a new Maxwell solve. A light halo around the dark outlines preserves visibility across signed colors.

The spectrum preserves all 21 wavelength/efficiency pairs. Wavelength is multiplied by 1000 (µm to nm); efficiency by 100 (fraction to percent of incident power). The percentage axis spans 0…100. Open circles mark actual solves; straight segments only connect those points. No new estimator, fit, smoothing, interpolated series or solve is added.

Those spectrum samples run 1300…1700 nm in 20 nm steps. **1550 nm is not a spectrum sample.** The separate retained 1550 nm design solve gives 93.58787717897128%; the sampled spectrum maximum is 93.18919426520034% at 1540 nm. Do not insert a 1550 nm point or relabel the sampled peak 93.59%.

Field/spectrum SVGs are standalone vectors with outlined IBM Plex Sans glyphs and no external image, font or script references. Desktop exports are 640 px wide; mobile layouts are designed at 320 px, with direct 390 px PNG review renders. Preserve their aspect ratios. The PNG fallbacks are smaller web assets; use accompanying HTML captions/alt text and CSV/JSON alternatives. SVG outlines preserve appearance, not searchable body text.

The renderer checks all 9,312 field cells, exact saved-geometry membership, equal scale, 21 SVG spectrum vertices/markers, source-to-SVG coordinate agreement, complete label bounds, source/font hashes and export identity. These are figure-integrity checks, not physical validation or an accessibility certification. Existing resolution/formulation comparisons do not establish convergence, omitted physics, fabrication readiness or measured-device performance.

The bundled original Plex font is covered by OFL 1.1 in `fonts/OFL.txt`; its public source and exact object/hash appear in `sources.json`. PhotonSmith's MIT notice is retained in `LICENSE.txt`. No global font installation or new scientific data is required.
