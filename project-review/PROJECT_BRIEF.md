# Commuter Service Area Explorer: project ingestion and planning baseline

Reviewed October 12, 2026. This is an interpretation of the existing project and a proposed planning baseline, not an approved implementation specification.

## Scope and limits

All 40 non-Git project files were inventoried and read or parsed: the seven-page pitch deck, both Tableau XML workbooks, the notebook's source cells, all spreadsheet sheets and cells, CSV records, spatial JSON features, README, Git attributes, and DBeaver project/configuration files. Connection details are omitted from this report. No original project files were modified, notebook cells executed, database connection opened, or external data refreshed. Git internals were excluded. `SOURCE` contains no files; `DB` contains configuration rather than a database or schema.

The deck was also rendered and all seven pages visually inspected. Spreadsheet formulas were read but not recalculated. Tableau's saved structure was inspected without running Tableau; performance and runtime behavior have not been measured. Geometry features were parsed, but topology, spatial intersections, and projection transformations have not been validated.

The user mentioned the Mobility Metrics chat / Transit Service Area Demand Report. It was not present in the available recent-chat listing. Its contents have not been ingested, and this brief does not assume knowledge of that framework. Reconcile it before finalizing methodology.

Document instructions and historical design proposals are reference material. They do not authorize implementation or prescribe the replacement platform.

## What the original concept is trying to do

The March 21, 2025 deck proposes connecting commuter information to regional mobility context, with queries at different geographic scales:

1. Select an H-GAC sector to see Park & Ride use and demographic context.
2. Explore METRO's draft O-D areas and individual TAZs, showing relevant Park & Ride facilities.
3. Identify a selected TAZ's three leading destination TAZs, with nearby facilities, stops, and attractions.
4. Compare driving with Park & Ride travel, including drivesheds, connecting routes, and on-time performance.
5. Examine potential markets within catchments and compare facilities along corridors and across the system.

Page 3 also mentions H3M hexagonal aggregation. No corresponding hex grid or trip-flow dataset was found. Pages 5-7 show conceptual report illustrations; their example numbers are not treated as validated project observations.

Interpretation: this is a geographic planning and demand exploration tool. Its data model must distinguish resident/worker characteristics, general travel demand, observed transit use, and parking occupancy.

## Assets and current readiness

| Asset | Contents | How it can contribute |
| --- | --- | --- |
| `TAZTransitExplorer.pdf` | Seven-page concept pitch | Product intent and proposed workflows |
| `BI/PnR_Explorer_v01.twb` | Four worksheets, one dashboard; 19 saved relationships | Broad initial model integrating facilities, geography and selected demographics |
| `BI/PnR_Explorer_v02.twb` | Four worksheets: OD, SECTOR, Sheet 4, TAZ; three dashboards: FILTER MAP, MAIN, TAZ MAP; two selection filter actions | Later map/navigation experiment; inspect separately from v01 rather than assuming all v01 functionality survived |
| `CODE/esri_arcgis_export.ipynb` | Community Analyst report translator producing 12 tables | Existing extraction logic; despite its name, it is not an ArcGIS feature download pipeline |
| `RAW/pnr_esrigc/TAZ DATA.xlsx` | OD: 113 rows; SECT, TAZ, relate1: 1,239 rows each, excluding headers | TAZ identity, O-D membership, sector assignment, and a tract relationship |
| `RAW/pnr_esrigj/METRO_Pln_TAZ48d00.json` | 1,239 polygon features | TAZ map and draft O-D assignment |
| `RAW/pnr_esrigj/METRO_Pln_DissolvedOD.json` | 113 polygon features | O-D area map and DissolvedID |
| `RAW/pnr_esrigj/METRO_PnR_pt.geojson` | 27 point features | Facilities, capacity attributes, amenities, listed routes and stop IDs |
| `RAW/pnr_esrigj/METRO_PnR_Routes.json` | 25 route features | Commuter route map and route identity |
| `RAW/pnr_esrigj/EXTERNAL_HGAC_Forecast_CT.json` | 979 tract features; households, population and jobs, 2020-2050 at five-year intervals | Regional growth context |
| `RAW/pnr_esrigj/EXTERNAL_HGAC_OA_CT.json` | 679 tract features; occupations and location quotients | Employment/occupation context; definitions of abbreviated measures need source documentation |
| `RAW/pnr_esrigj/EXTERNAL_EJ_DC_CT.json` | 679 tract features; disadvantage and environmental/social indicators | Equity context; preserve source vintage, definitions and missing values |
| `RAW/ltsv_esrica/*.xlsx` | 15 original Community Analyst reports, 150 rows each | Original report evidence and a way to repair extraction |
| `RAW/pnr_esrigc/community_analyst_export.xlsx` | 12 normalized sheets covering those 15 O-D IDs | Demographics, journey to work, vehicle access, incomes, housing, spending, Tapestry and generations |
| `RAW/pnr_plnfmm/ALL PNR.xlsx` | Four sheets containing seven structured tables | Facility inventory, route-to-facility mapping, observed parking counts, date metadata, alternate capacities and approximate O-D associations |
| `RAW/hgac_fc/{Hh,Hp,J}_table.csv` | Each has 25 sector rows plus Grand Total; 2020-2050 forecasts | Regional sector benchmarks; keep totals separate from detail rows |
| `RAW/pnr_plnfmm/ddapi_project.csv` | 221 project records | Facility/project metadata; scope includes more than P&R |
| `RAW/pnr_plnfmm/ddapi_plan.csv` | 3,709 plan records keyed to project_id | Plan metadata; does not include the actual imagery or plan documents |
| `DB/*` | DBeaver CSV JDBC connection metadata and project settings | Evidence of a tabular exploration setup; no committed SQL schema or populated database |
| `README.md`, `.gitattributes` | Minimal project description and repository attributes | Repository context |

The 15 Community Analyst O-D IDs are 3, 9, 15, 16, 21, 23, 32, 56, 57, 58, 59, 67, 100, 105 and 111. This is partial coverage of 113 O-D areas. It should not appear as systemwide coverage in an explorer.

## Geography and relationships

TAZ is the useful common geographic unit in the existing model. Each of the 1,239 workbook TAZs has a sector assignment and O-D area name. O-D names match the 113 OD reference names. However, O-D areas do not form a strict hierarchy beneath sectors: 42 O-D areas contain TAZs from multiple stored sector values. Examples include Katy, Cypress, IAH and Greater Greenspoint.

The stored SECT values include 11.1 through 11.8, alongside integer sector values. Treat them as identifiers, not quantities; define how these subdivisions roll up to H-GAC sector 11 and how the local subset relates to the 25-sector regional forecast tables.

The intended sector -> O-D -> TAZ navigation therefore needs explicit selection semantics. Selecting a sector could show intersecting O-D areas while limiting measures to the selected TAZs, or display full O-D totals clearly labeled as extending beyond the sector. Whole O-D demographics cannot simply be summed into sectors without an allocation method.

Important keys and bridges:

- TAZ IDs join geography, SECT and relate1. JSON TAZ IDs have leading spaces; spreadsheet TAZ IDs are numeric.
- O-D geography uses ODAREA and DissolvedID; the workbook provides OD_ID. Establish one stable O-D dimension rather than relying on names alone.
- Facility keys are PRKNRD_ID; route keys are RouteNum / Bus Routes.
- `ApproxRelate` contains 267 facility-to-DissolvedID rows. It represents an approximate association, not demonstrated rider origins or a computed driveshed.
- Census joins involve GEOID20, Tract, tract and Census_tract_ID. Normalize to fixed-length strings and preserve geography vintage.
- Project and plan metadata join on project_id; facility-name matches need their own verification.

## Findings that matter before rebuilding

### Aggregation and evidence

1. `relate1` has one row per TAZ but Join_Count exceeds one for 1,179 of 1,239 rows (up to 19), while retaining only one GEOID20 per row. This indicates multiple spatial matches without a complete allocation bridge in the stored output. The underlying spatial join method is unknown. A selected tract cannot safely stand in for a TAZ's population or jobs; rebuild and validate the tract/TAZ relationship.
2. The parking workbook's `COUNTS` measures are occupied and empty parking spaces. They are not transit boardings or unique riders. The deck's proposed P&R ridership metrics require a separate source or an explicitly documented estimate.
3. No origin-TAZ/destination-TAZ flow table, mode-tagged trip observations, GTFS stop/schedule dataset, network travel-time matrix, driveshed polygons, or route OTP time series was found. O-D area polygons are not trip-flow data. The top-destination and travel-comparison reports need these inputs.
4. Regional tract layers have differing coverage: 979 forecast tracts versus 679 occupation and equity tracts. Missing coverage must remain visible.
5. Inputs mix Census 2010/2020, ACS 2018-2022, Esri 2024/2029, and H-GAC forecast years. Source year, estimation method and reporting period must travel with every metric.
6. Capacity values differ by source. For example, Addicks has PSPACES 1,999 in the point layer, SPACES_FMM 2,386 in DATA_PNR and SPACES_SVP 2,438 in the first count record. These may represent different vintages or definitions; do not choose one silently.
7. Counts, medians, rates, percentages, location quotients and overlapping vehicle categories need different aggregation rules. Summing median incomes or averaging percentages without denominators will mislead.

### Existing extraction issues

The notebook selects columns and rows by fixed positions. Several source reports contain multiple area comparison columns; Harris County is not always the third column. For example, report 100 has Harris County in its last column, whereas the normalized generation table labels its third source column Harris County and stores 10,817 rather than the original Harris County male-worker value 1,268,361. This is a verified labeling/extraction error.

The generation slice also omits the total civilian employed population row at Excel row 139 while retaining male/female rows. The `Income Table` calls its numeric column `Number of Households`, although it contains median income, disposable income and net worth amounts. Preserve indicator-specific units. The raw report supplies these distinctions.

Notebook paths reference older folder locations (`./ltsv_esrica`, `./pnr_esrigc`, and a separate test path) rather than the current RAW layout. Running the test then the batch against the same in-memory tables can append the test area twice. The saved normalized workbook currently has no duplicate (indicator, OD_ID) keys, so this is a pipeline risk rather than a demonstrated duplicate in the current output.

### Tableau portability and completeness

v01 contains absolute paths to a previous user's OneDrive project. v02 points its source files into the current E: repository, but also references a temporary `.hyper` extract under a TableauTemp directory; no `.hyper` file is included. This is a portability/reproducibility issue, not a proven explanation of the user's experience.

v01 contains 19 relationships and broadly integrates the geography and demographic tables. v02's saved relationship graph contains only one explicit relationship, routes to BUSROUTES, despite numerous retained table/extract objects. It should not be assumed to preserve the full earlier analytical model. A runtime review would be needed to assess what each dashboard actually returns and why it feels unsatisfactory.

## Proposed goals to discuss

These goals are inferred from the deck and the user's desire to move beyond the current Tableau experience; they are not yet agreed requirements.

1. Establish a reliable geographic model connecting TAZs, O-D areas, sectors, census geography, P&R facilities and routes.
2. Make commuter service areas easy to explore, with clear geographic selection and a concise profile of available demand, demographic, growth and facility measures.
3. Separate measured service use from market potential and general travel patterns; expose provenance and coverage.
4. Support comparable facility/corridor assessments with consistent time periods, capacity definitions and catchment methods.
5. Add destination and transit-versus-driving analysis once the required evidence and methods are available.
6. Make data ingestion repeatable and the explorer portable, with explicit validation and refresh procedures.

## Proposed task sequence and completion criteria

| Order | Task | Completion criterion |
| --- | --- | --- |
| 1 | Reconcile this baseline with Mobility Metrics / Transit Service Area Demand Report | Record agreed TAZ vintage, demand definitions, geographic scope, catchment method and analytical assumptions |
| 2 | Define primary users, planning decisions and what feels wrong in Tableau | List three priority workflows and measurable usability/performance expectations |
| 3 | Build a source and metric dictionary | Every priority metric has a source, grain, unit, vintage, denominator, aggregation rule and coverage status |
| 4 | Validate geographic identity and crosswalks | TAZ/OD/sector IDs reconcile; cross-sector O-D behavior is specified; tract allocation has documented weights and conservation checks |
| 5 | Repair Community Analyst extraction | Labels drive extraction; comparison geographies are identified correctly; original values reconcile; reruns do not append duplicates |
| 6 | Normalize facility inventory and parking counts | Resolve IDs, alternate capacities, dates and exclusions; label parking utilization distinctly from ridership |
| 7 | Establish a reusable analytical data layer | Clean dimensions, fact tables and bridges load reproducibly with source lineage and coverage checks |
| 8 | Prototype the core explorer workflow | Sector/O-D/TAZ/facility selection produces reconciled profiles and makes missing data explicit |
| 9 | Obtain trip-flow and service-performance inputs | Document trip purpose/mode/time period and obtain needed stops, schedules, travel-time and OTP evidence |
| 10 | Implement destination, catchment and comparison reports | Top destinations and travel comparisons follow documented methods with defensible source data |
| 11 | Evaluate delivery platform and operational handoff | Chosen approach satisfies priority workflows, expected data volume, hosting/access needs and refresh ownership |

Suggested first release: geographic browsing, facility context, validated demographics for covered O-D areas, regional growth context, and parking utilization. This is a scope proposal, not a decision to build. Avoid presenting unvalidated tract allocation or absent trip flows as calculated demand.

## Questions for the next planning conversation

- Which parts of the Mobility Metrics framework are authoritative for this project, and can that chat/report be supplied or referenced directly?
- Who will use the explorer and what planning decision should it help them make first?
- Is the intended scope P&R commuter service only, or all transit services?
- What is unsatisfactory in Tableau: responsiveness, map navigation, filters, analytical results, maintainability, or sharing?
- Should a service area mean an administrative geography, approximate facility assignment, driving catchment, transit accessibility catchment, or observed rider-origin catchment?
- Which trip-flow, ridership, schedule, travel-time and OTP datasets are available beyond this repository?

## Supporting review artifacts

`inventory.json` records each file's size, spreadsheet sheet dimensions and preview rows, CSV headers and record counts, spatial schemas and property missingness, Tableau connections/relations/actions, notebook source cells, and deck text. It is a structural inventory rather than a duplicate of all source data. `FILE_INVENTORY.md` gives a compact per-file index. Rendered deck images are review intermediates. The ingestion scripts under `tmp` read sources and write review outputs only.
