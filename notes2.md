You are Codex CLI. Modify this QGIS plugin repo to remove the Python Plotly dependency and replace chart generation with Plotly.js (a vendored JS file) so packaging works with qgis-plugin-ci and plugin size stays under the 25 MB QGIS plugin repo limit.

Repo: spatiotemporal_lulc_analysis (QGIS plugin)
Goal release: v0.1.1 (patch fix). Only charts feature is currently broken due to missing python plotly packaging; everything else works. Fix charts without requiring users to pip install anything.

HIGH-LEVEL PLAN

1. Vendor Plotly.js (plotly.min.js) in the plugin, ensure it is packaged.
2. Replace all Python plotly usage (import plotly, graph_objects, express, fig.write_html, etc.) with pure HTML generation that uses Plotly.js + JSON data and renders charts via Plotly.newPlot().
3. Ensure HTML output works when opened outside QGIS (portable). Prefer inlining Plotly.js into the generated HTML so it has no external dependencies.
4. Ensure qgis-plugin-ci packaging includes the new vendor assets.
5. Bump plugin version to 0.1.1 and update CHANGELOG.

DETAILED INSTRUCTIONS

A. Locate current chart implementation

- Search for any usage of Python Plotly:
  - `import plotly`
  - `plotly.express`
  - `plotly.graph_objects`
  - `fig.write_html`
  - `to_html()`
- Identify the module(s) that build charts and output HTML files.

B. Add Plotly.js to the repo (vendoring)

1. Create folder: `vendor/js/`
2. Add `plotly.min.js` there.
   - Use the official Plotly.js distribution (minified). The file should be committed into the repo.
3. Verify it is not excluded by packaging rules:
   - Check `.qgis-plugin.donotpackage` and remove any patterns that exclude `vendor/` or `*.js` or the new folder.
   - Check `.qgis-plugin-ci` config if present; ensure it does not exclude `vendor/`.

C. Implement Plotly.js-based HTML generator (no python plotly)
Create a reusable helper function in an appropriate module (e.g., `utils/charts.py` or inside the existing charts module) with this behavior:

Function: `write_plotlyjs_html(output_html_path, title, traces, layout, config=None, inline_plotly=True)`

Inputs:

- `output_html_path`: file path to write HTML
- `title`: title string for the page/chart
- `traces`: Python list of dicts representing plotly traces (same structure Plotly.js expects)
- `layout`: Python dict for plotly layout
- `config`: optional dict for plotly config
- `inline_plotly`: if True, read vendored `vendor/js/plotly.min.js` and inline it into the HTML in a <script> tag

Requirements:

- Use `json.dumps(..., ensure_ascii=False)` to embed `traces/layout/config` into the HTML.
- The generated HTML must:
  - include a `<div id="chart">`
  - load Plotly (inline if inline_plotly True; else reference local `vendor/js/plotly.min.js` with a relative path that works)
  - call: `Plotly.newPlot('chart', traces, layout, config);`
- Add minimal CSS to make the chart responsive:
  - `width: 100%; height: 100vh;` or similar
- Add a window resize handler:
  - `window.onresize = () => Plotly.Plots.resize('chart');`

D. Replace existing plotly python chart creation
For each chart the plugin produces:

1. Replace Python plotly object creation with dict-based traces/layout:
   - Example trace dict patterns:
     - Bar: `{ "type": "bar", "x": [...], "y": [...], "name": "..." }`
     - Line: `{ "type": "scatter", "mode": "lines+markers", "x": [...], "y": [...], "name": "..." }`
     - Heatmap: `{ "type": "heatmap", "z": [[...]], "x": [...], "y": [...], "colorscale": "Viridis" }` (use built-in colorscales)
2. Call `write_plotlyjs_html(...)` to write the HTML.
3. Preserve the plugin’s existing output paths/naming so other code doesn’t break.

E. Viewing charts in QGIS (do not break UX)

- Keep existing behavior if the plugin currently opens HTML. If it used plotly’s `write_html`, it probably opens the saved HTML.
- Provide a robust opening method:
  - Use `QDesktopServices.openUrl(QUrl.fromLocalFile(output_html_path))` to open in default browser.
- If plugin embeds HTML in a widget, keep it, but ensure a fallback “Open in Browser” works.

F. Fail gracefully if vendor file missing

- If `vendor/js/plotly.min.js` is not found at runtime:
  - Show a non-crashing message (QMessageBox / log) explaining charts are unavailable and suggest reinstalling v0.1.1.
  - Continue plugin operations for non-chart features.

G. Version bump and changelog

1. In `metadata.txt`, set:
   - `version=0.1.1`
2. In `CHANGELOG.md`, add:
   - `## 0.1.1`
   - `- Fixed: charts now use Plotly.js (vendored) instead of Python plotly; packaging works with qgis-plugin-ci.`

H. Packaging verification (must do)

- Run qgis-plugin-ci packaging workflow locally if possible or simulate build.
- Confirm the produced ZIP includes:
  - plugin folder
  - `metadata.txt`
  - `vendor/js/plotly.min.js` (even if you inline, keep it in repo and package)
- Install the ZIP in QGIS (“Install from ZIP”) and test:
  - Charts generate and open correctly.
  - Rest of plugin works.

DELIVERABLES

- Code changes implementing Plotly.js HTML generation (no Python plotly dependency).
- Vendored `vendor/js/plotly.min.js` added and included in package.
- Updated packaging config to include vendor assets.
- Version bumped to 0.1.1 + changelog updated.

CONSTRAINTS

- Do NOT add Python runtime dependencies requiring pip.
- Keep changes minimal and patch-safe.
- Keep output HTML files portable (prefer inlined Plotly.js).
