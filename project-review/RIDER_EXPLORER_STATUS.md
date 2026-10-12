# Rider-facing explorer: goal and completion audit

The latest user direction supersedes the earlier analytical-dashboard scope for this release. This is a lightweight, easy-to-use HTML website for conversations with prospective commuters who may be new to transit. The required flow is region sector → coverage corridor/freeway → TAZ O-D origin neighborhood → nearest facility → destinations reachable from that facility.

The user clarified that delivery should be storage-platform agnostic: copy a folder and open the HTML. Straight-line proximity is accepted initially; driving catchments will be supplied later. Uploading to the actual work SharePoint is not part of this local delivery.

Previous goal-turn classification: progress. The project ingestion established source coverage, relationships and gaps. This turn built and packaged the rider-facing application and gathered functional evidence.

## Current deliverables

- `output/commuter-explorer/index.html`: the standalone application, 480,966 bytes.
- `output/commuter-explorer/README.md`: usage and environment guidance.
- `output/commuter-explorer.zip`: same two files in a copy-ready folder.
- `explorer/source/template.html`: maintainable UI source.
- `CODE/build_explorer.py`, `CODE/refresh_routes.py`, `CODE/check_explorer.mjs`: build, evidence refresh, and verification.
- `explorer/source/verification.json`: automated check results.
- `explorer/source/desktop-preview.png`, `mobile-preview.png`: inspected browser output.

## Requirement audit

| Requirement | Evidence | Status |
| --- | --- | --- |
| HTML-based, lightweight | Generated standalone HTML below 0.5 MB, no external runtime assets or libraries | Implemented; automated check passed |
| Copy folder without installation | Package contains HTML and README only; source data, CSS, JS and vector map embedded | Implemented; isolated copied-page HTTP test passed |
| Easy flow for first-time riders | Five sequential choices, neighborhood search, plain-language facility/destination cards, first-ride notes | Desktop and mobile browser review passed; real staff/rider usability feedback remains desirable |
| Region sector | All 18 parent sector IDs present in the supplied TAZ subset; sector 11 subdivisions rolled up | Implemented; full data check passed |
| Freeway corridor | Seven explicit freeway corridor groups; origin grouping based on nearest active facility | Implemented; provisional proximity method disclosed |
| TAZ O-D origin neighborhood | All 113 neighborhoods and 1,239 TAZs reachable; optional TAZ refinement | All 203 origin combinations checked; refinement exercised in browser |
| Nearest facility | Great-circle ranking from documented origin reference across all 22 facilities with checked commuter stops | Full ranking checks passed; examples exercised in browser |
| Transit destinations | 26 checked timetable route lists; direct destination areas, route numbers, official schedule links | Katy, Addicks and Kingwood flows exercised; Addicks Downtown/TMC split verified |
| Mobile/tablet layout | Responsive layout, no document-level horizontal overflow at 390 px | Browser render inspected; viewport reset after QA |
| No live network dependency for browsing | Copied HTML under restrictive CSP and an opaque-origin `allow-scripts` sandbox; complete Katy flow to destinations | Passed with no console errors |
| Open HTML directly on user's device | User confirmed on October 12, 2026: “It opens and the flow works” | Passed on user's device |
| Run in actual SharePoint | User requested agnostic package; Microsoft Site Pages workflow documented | Not deployed or verified in tenant; depends on tenant HTML availability and external-link settings |

The user confirmed on October 12, 2026 that the packaged HTML opens directly and the five-step flow works. Together with the recorded functional, coverage, sandbox and package-integrity checks, this closes the remaining verification item for the storage-platform-agnostic delivery the user requested. The goal is complete for that authorized scope. Actual SharePoint deployment remains unperformed, as disclosed; the user requested a copy-ready package rather than tenant deployment. No ongoing process or external job is being awaited.

No failure of the application has been observed. The remaining local-opening verification is a tool protocol limitation, not an application error. The request for a user check explicitly explained that the browser tool permits HTTP/HTTPS only.

## Next evidence or inputs

1. Direct opening and flow confirmed by the user; no defect reported.
2. Replace provisional corridor/proximity associations once driving-time or catchment inputs are supplied; those future inputs are not required for this initial release.
3. Confirm facility location/address vintage during operational rollout and refresh route evidence when service changes.
