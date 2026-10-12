# Commuter Service Area Explorer

Copy this folder anywhere. Open `index.html` in a current browser. The complete explorer is in that one HTML file: no installation, server, build step, account, API key, external font, map tile service, or internet connection is required for browsing.

The flow is **region sector → freeway corridor → origin neighborhood → nearest commuter facility → transit destinations**. The fifth step links to official schedules and METRO's system map; those external links require internet access.

## Using it in a rider conversation

1. Pick a sector from the neighborhood examples, search by a neighborhood, or use the map.
2. Pick a familiar freeway corridor.
3. Pick the origin neighborhood. Neighborhoods that span sectors/corridors appear in each relevant portion.
4. Review facilities ranked by straight-line proximity. The first is closest to the selected origin reference point; the next four are alternatives across all corridors. Optionally narrow the origin to one TAZ.
5. Select a facility to see its direct destination areas, route numbers, listed stops, and links to current schedules. Confirm the actual trip, direction, boarding bay, and return service using METRO.

Use the step buttons to go back; changing an earlier choice clears downstream choices. Start over resets the conversation. Text choices work with a keyboard; the map is supplemental. The page adapts to tablets and phones.

## What “nearest” means for now

Great-circle straight-line miles from the area-weighted polygon center of the neighborhood's TAZs in the selected sector and corridor, or from the selected TAZ center. This is not a drive-time estimate and not distance from a rider's home address. Corridor grouping assigns each TAZ to its nearest active commuter facility's corridor. There is no arbitrary maximum distance cutoff and all project origins remain available.

All 1,239 project TAZs and 113 draft O-D neighborhoods are included. The original project contains 18 parent H-GAC sector IDs after sector 11 subdivisions are combined, not the entire 25-sector region. Seven corridor groups and 22 facilities with checked commuter stops are included. Other inventory facilities without stops in the current commuter schedule list are excluded from commuter ranking, rather than presented as boarding options.

## Service snapshot and maintenance

The 26 official METRO commuter timetable stop lists were downloaded on October 12, 2026. Route-to-facility relationships are matched against the named stops in those lists, not the older route mapping in the workbook. Direct destination areas are Downtown Houston or Texas Medical Center according to METRO's corridor service table. Stop lists include multiple directions and trip patterns; appearing in the list does not mean every departure serves that stop. The page deliberately does not publish static fares, departure times, driving times or transfer itineraries.

Facility coordinates and addresses come from the project's existing point layer and retain that source's vintage. Confirm them during operational data review, particularly any relocated facilities. TAZ polygons and O-D membership also retain project vintage. This app does not collect rider addresses, names or travel details, and does not store conversation choices after reload.

Official sources:

- [METRO corridor and destination information](https://www.ridemetro.org/riding-metro/transit-services/park-and-ride-bus/)
- [Current commuter schedules](https://webapps.ridemetro.org/schedules/?q=pr)
- Individual route schedule URLs are retained in `source/official-routes.json` and embedded in the page.

For a data refresh, run `CODE/refresh_routes.py --checked YYYY-MM-DD` from the repository with Python and network access, supplying the actual review date. Review the official service page for route additions/removals, edit the route registry and corridor definitions if needed, run `CODE/build_explorer.py`, and run `CODE/check_explorer.mjs` with Node. Python's build-time dependency is openpyxl. End users need none of these tools. Do not manually edit generated `index.html` for lasting changes; update `source/template.html` and rebuild.

Future drive-time/catchment inputs can replace the proximity method in the builder and ranking functions. Include stable facility IDs, the network/date/time assumptions, and either catchment geometry or an origin-to-facility travel-time table. No placeholder driving times are shown today.

## SharePoint

The folder is storage-platform agnostic. Locally, double-click the HTML. In SharePoint, copying a file into an ordinary library is not by itself a guarantee that SharePoint will execute it as a page.

Microsoft's current HTML page workflow supports uploading an existing HTML file to **Site Pages**:

1. Open Site Pages; if necessary a site owner enables **File types → Allow HTML files**.
2. Use **Create or upload → Upload HTML page** and select `index.html`.
3. Open and verify the draft, then publish using your normal page workflow.
4. If external schedule links are blocked, a site administrator can add `webapps.ridemetro.org`, `www.ridemetro.org`, and `map.ridemetro.org` to the site's HTML Field Security allowlist.

Availability is being introduced gradually and may differ by tenant. If the library downloads/previews the HTML instead of running it, download the file and open it locally, or use the supported Site Pages workflow when available. This is a SharePoint hosting setting rather than an app installation requirement. Do not assume that renaming HTML to ASPX resolves it.

The HTML is under 1 MB, with all JavaScript, CSS and map/data assets inline. It uses no runtime fetch calls, external scripts, browser storage, forms, workers or popups, fitting Microsoft's documented sandbox constraints. The actual tenant must still be checked; this project was not uploaded to your work SharePoint.

[Microsoft: Create, upload, edit, and publish HTML pages in SharePoint](https://support.microsoft.com/en-us/sharepoint/create-edit-publish-html-pages)

## Verification

The check script verifies every TAZ is reachable through the guided flow, all 203 sector/corridor/neighborhood combinations have ranked facilities, distance calculation and ordering, route/facility consistency, current-service regression cases, downstream reset behavior, package size, and absence of runtime external-asset dependencies. Results are saved in `source/verification.json`.

Browser QA covers the end-to-end Katy workflow, TAZ refinement, a facility with both Downtown and TMC routes, an additional corridor, search/no-result recovery, navigation resets, zoom controls, desktop and 390-pixel layouts, and a restrictive sandbox preview. The browser automation tool permits HTTP/HTTPS only, so direct `file://` opening and actual SharePoint rendering cannot be exercised by that tool. A copied standalone file is also tested over local HTTP without access to source or repository assets. Verify direct opening on your device and tenant before using the page operationally.
