# Uganda Electricity Atlas

An interactive map of Uganda's electricity system for electrical and mechanical engineering students in renewable energy and power systems units (Uganda Martyrs University): power stations, the 400/220/132 kV grid, substations, 33 kV distribution, a DC load flow, N−1 checks, frequency after a trip, blackout replays and restoration, carbon intensity, new generation and demand scenarios, district shading (access, population, biomass), a projects register, distribution losses, blackout history, and access to electricity and clean cooking.

The site is static: `index.html` holds the whole page, including Leaflet. GitHub Pages serves it with no build step.

## Files

| Path | What it is |
|---|---|
| `index.html` | The atlas |
| `data/` | Open data: CSV, GeoJSON (`data/geo/`) and one ZIP of everything (see `data/README.txt`), plus `osm-grid.json` once the workflow has run |
| `LICENSE` | CC BY 4.0 for data and text; MIT for code |
| `CITATION.cff` | How to cite the atlas; GitHub shows a "Cite this repository" button from it |
| `tools/osm_grid.py` | Downloads Uganda's 66–400 kV grid from OpenStreetMap and matches it to the model's lines |
| `.github/workflows/osm-grid.yml` | Runs `osm_grid.py` on the 3rd of each month and commits the result |
| `.nojekyll` | Tells GitHub Pages to serve the files as they are |

## Publish

1. Settings → Pages → Build and deployment: **Deploy from a branch**, branch `main`, folder `/ (root)`.
2. Actions → **Refresh OpenStreetMap grid** → **Run workflow** (first time only; afterwards it runs monthly).

## Cite and archive

The page's **Data, licence and links** tab shows a suggested APA citation. To give the atlas a permanent DOI, connect the repository to [Zenodo](https://zenodo.org/) (log in with GitHub, switch the repository on under GitHub settings), then publish a release on GitHub. Zenodo archives each release and issues a DOI; add it to `CITATION.cff` as `doi:`.

## Licences

The atlas's own data and text are under CC BY 4.0 and its code under the MIT licence (`LICENSE`).

OpenStreetMap data © OpenStreetMap contributors, Open Database Licence (ODbL); `data/osm-grid.json` is shared under the same licence. Leaflet is under the BSD 2-Clause licence (`tools/LEAFLET-LICENSE.txt`). Sources for all other data are listed in the atlas under "Sources, method and limitations".
