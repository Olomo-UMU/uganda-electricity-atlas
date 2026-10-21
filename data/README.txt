Uganda Electricity Atlas: open data
A teaching atlas for electrical and mechanical engineering students in renewable energy and power systems units,
Uganda Martyrs University. Data to May 2026, with reliability, loss and access figures to October 2026.
Licence: CC BY 4.0 for the compiled data and text (see LICENSE). Cite the atlas (see CITATION.cff) and the original
sources (ERA, UETCL, UEDCL, UBOS, World Bank, CCG Starter Data Kit, Energy Sector GIS Working Group) listed on the atlas page.

Inputs
  plants.csv              Power stations: type, capacity (MW), year, grid connection, town-level location.
  substations.csv         Grid substations, switchyards, planned substations and border points. load_weight is the model's relative
                          weight for placing domestic demand: a substation's share = its weight / sum of all weights (100).
                          One third comes from homes with electricity in the districts it supplies (2014 census),
                          two thirds from an estimated industrial weighting. See demand_allocation.csv.
  lines.csv               Transmission lines: ends, kV, circuits used in the model, length, status, model rating.
  load_centres.csv        Main load centres.
  projects.csv            Register of transmission lines under construction or planned, and candidate power station sites (2016 GIS).

Model results (default settings: domestic peak 1,166 MW; exports Kenya 100, Rwanda 40, Tanzania 20, DR Congo 20 MW;
thermal allowed; no lines out; lines under construction excluded)
  model_line_flows.csv    DC load-flow result for every line, dry and rainy season, at 03:00, 08:00, 13:00 and 20:00.
                          Blank flow = line not in service.
  model_substation_loads.csv  Load placed at each substation (MW).
  model_generation.csv    Dispatch of each plant (MW). Owen Falls is the slack plant.
  n1_screening.csv        Each in-service line switched out in turn at the dry-season 20:00 peak: load lost and the worst loading
                          on any remaining line.

Reliability, losses and access
  reliability_losses_access.csv  Distribution losses and ERA targets, access to electricity (people; households on the grid)
                          and clean cooking, each value with its source.
  blackouts.csv           Nationwide blackouts reported since 2022 (press reports and operator notices; not an official count).

GIS (Uganda Energy Sector GIS Working Group data, supplied October 2026)
  demand_allocation.csv   How each substation's demand weight was set: previous estimate, households with electricity, result.
  district_households_2014.csv  Households, share with electricity and supplying substation for each of the 112 districts (2014 census).
  gis_crosscheck.csv      Model compared with the GIS layers and the 2024 MEMD transmission map: positions, plants and lines.
  distribution.json       33 kV and 11 kV lines (in service, under construction, proposed), simplified, for the map layer.
                          Source: Uganda Energy Sector GIS Working Group, distribution lines (2023).
  geo/*.geojson           Power stations, substations, transmission lines (mapped routes where known) and districts with
                          population, households, access, land area and woody biomass (2002 National Biomass Study layer;
                          totals recomputed from land-cover classes where the file's subtotal was inconsistent).
                          Coordinates in WGS84 (EPSG:4326). Open in QGIS or ArcGIS.

Flows, loads and dispatch are modelled, not measured. See "Sources and method" on the atlas page.
For other settings, use "Download this table (CSV)" on the atlas page, which exports what is on screen.
