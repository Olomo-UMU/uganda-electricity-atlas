Uganda Electricity Atlas: open data
BME 3102 Mechanics of Machines, Uganda Martyrs University. Data to May 2026.
When you use these files, cite the atlas and the original sources (ERA, UETCL, UEDCL, CCG Starter Data Kit) listed on the atlas page.

Inputs
  plants.csv              Power stations: type, capacity (MW), year, grid connection, town-level location.
  substations.csv         Grid substations, switchyards, planned substations and border points. load_weight is the model's relative
                          weight for placing domestic demand: a substation's share = its weight / sum of all weights (98).
                          The weights are estimates, not measurements.
  lines.csv               Transmission lines: ends, kV, circuits used in the model, length, status, model rating.
  load_centres.csv        Main load centres.

Model results (default settings: domestic peak 1,166 MW; exports Kenya 100, Rwanda 40, Tanzania 20, DR Congo 20 MW;
thermal allowed; no lines out; lines under construction excluded)
  model_line_flows.csv    DC load-flow result for every line, dry and rainy season, at 03:00, 08:00, 13:00 and 20:00.
                          Blank flow = line not in service.
  model_substation_loads.csv  Load placed at each substation (MW).
  model_generation.csv    Dispatch of each plant (MW). Owen Falls is the slack plant.
  n1_screening.csv        Each in-service line switched out in turn at the dry-season 20:00 peak: load lost and the worst loading
                          on any remaining line.

Flows, loads and dispatch are modelled, not measured. See "Sources, method and limitations" on the atlas page.
For other settings, use "Download this table (CSV)" on the atlas page, which exports what is on screen.

OpenStreetMap
  osm-grid.json           Made monthly by tools/osm_grid.py (GitHub Actions). OSM power lines (66 kV and above) and substations,
                          the route of each matched model line, and a report of what was not matched.
                          © OpenStreetMap contributors, Open Database Licence (ODbL).
