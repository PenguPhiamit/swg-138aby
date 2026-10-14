# Stock ticket-map calibration: affine fit rejected

14 October 2026 · ChatGPT. Offline read of the stock ui_ticketpurchase.inc; no client/TRE edits or live actions. Tool: outputs/tools/hoth/fit_galaxy_map.py. Evidence: galaxy-map-calibration.json and galaxy-map-calibration.svg in this folder.

Ten stock button rectangles were parsed; their centres are GalaxyMap-local pixels, not screen pixels. Corellia/Talus and Naboo/Rori were averaged by shared atlas square, leaving eight independent system anchors. The model fits x and y as separate affine functions of atlas column,row,1.

- Training RMSE: 67.85 px.
- Largest stock residual: 132.63 px.
- Largest leave-one-out error: 236.66 px.
- Computed Hoth centre: 120.86, 397.37; Endor-size cloned button top-left would be 90, 368.
- **Do not adopt that candidate automatically.** The proposed diagnostic gate (30px maximum residual/60px leave-one-out) fails badly. Stock UI is stylized and atlas squares are coarse; a single affine fit does not faithfully preserve all stock positions. A numerical answer is not evidence of a correct layout.

The rejected candidate remains in JSON to make the failure reproducible, with fit_accepted=false and adopt_candidate=false. C14 lore grid K-18 remains valid; it is the conversion to client pixels that failed. Suggested next decision: keep provisional UI placement until human review, or design a consistent revised galaxy layout from all atlas anchors. Either is a design choice; do not silently move existing buttons or rebuild client archives.

Synthetic checks passed for recovering a known affine transform and rejecting singular/collinear input. SVG parsed as XML. Actual client rendering, label collisions, decorative route lines and button clicks remain untested.
