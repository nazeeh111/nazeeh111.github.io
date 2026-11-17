# PhotonSmith retained-data figures

Reproduce the field and spectrum figures from saved numerical data. This bundle performs no simulation, model inference, fitting or new experiment.

From this directory, with Python 3.11+ and existing NumPy/Matplotlib:

```sh
python -B renderer/render.py
```

The generator writes desktop/mobile SVGs, PNG fallbacks, exact-value CSVs and a public export manifest under `assets/`. All paths default relative to this bundle. `--source`, `--font` and `--out` accept explicit paths. The bundled plot-data and font hashes are checked before outputs are opened. The renderer uses a temporary Agg/font cache and never installs a system font.

The tested package versions were Matplotlib 3.11.2 and NumPy 2.5.5. Outputs may differ with other library versions. No package is installed automatically and the generator makes no network calls.

`data/plot-data.json` is a minimal, numerically unchanged extraction from the pinned [retained 1550 nm design](https://github.com/nazeeh111/PhotonSmith/blob/13912d9d640938acf8ce299a152298666ae61d44/experiments/designs/interactive-refined-1550nm.json). It includes only the plotted field, coordinates, geometry, permittivity and spectrum. Original and extracted hashes are in `sources.json`.

To verify the extraction against a separately downloaded copy of that exact original JSON:

```sh
python -B renderer/extract_data.py retained-original.json --out data/plot-data.json
```

A changed original is refused. No download happens inside either script.

Use `captions.json` for alt text and concise caption copy. See [PROVENANCE.md](PROVENANCE.md) for units, sample support, source/formulation distinctions and limits. Retain `LICENSE.txt` and `fonts/OFL.txt` with the bundle. IBM Plex Sans glyphs are outlined in the SVGs, so exported images have no font or script dependency.
