# Uganda Electricity Atlas

An interactive map of Uganda's electricity system for teaching (BME 3102, Uganda Martyrs University): power stations, the 400/220/132 kV grid, substations, distribution areas, load centres, a DC load flow, N−1 checks, carbon intensity and scenario cases.

The site is static: `index.html` holds the whole page, including Leaflet. GitHub Pages serves it with no build step.

## Files

| Path | What it is |
|---|---|
| `index.html` | The atlas |
| `data/` | Open data as CSV files (see `data/README.txt`), and `osm-grid.json` once the workflow has run |
| `tools/osm_grid.py` | Downloads Uganda's 66–400 kV grid from OpenStreetMap and matches it to the model's lines |
| `.github/workflows/osm-grid.yml` | Runs `osm_grid.py` on the 3rd of each month and commits the result |
| `.nojekyll` | Tells GitHub Pages to serve the files as they are |

## Publish

1. Settings → Pages → Build and deployment: **Deploy from a branch**, branch `main`, folder `/ (root)`.
2. Actions → **Refresh OpenStreetMap grid** → **Run workflow** (first time only; afterwards it runs monthly).

## Licences

OpenStreetMap data © OpenStreetMap contributors, Open Database Licence (ODbL); `data/osm-grid.json` is shared under the same licence. Leaflet is under the BSD 2-Clause licence (`tools/LEAFLET-LICENSE.txt`). Sources for all other data are listed in the atlas under "Sources, method and limitations".
