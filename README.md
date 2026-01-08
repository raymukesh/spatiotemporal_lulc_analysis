# Spatiotemporal LULC Analysis

Spatiotemporal LULC Analysis is a QGIS plugin for multi-year land use/land cover (LULC) change accounting on categorical rasters. It produces tabular change metrics and raster outputs to support change assessment across time.

## Features
- Area by class per year (CSV)
- Net and gross change per interval (CSV)
- Transition matrix per interval (CSV)
- Transition matrix for first/last year (CSV)
- Top transitions ranking (CSV)
- Change intensity per interval (CSV)
- Interactive charts for CSV outputs (HTML)
- Plotly is vendored under `vendor/` so charts work without external installs
- Sankey diagram across all intervals (HTML)
- Change frequency raster across all years (GeoTIFF)
- Change hotspots (heatmap) per interval (GeoTIFF)

## QGIS compatibility
- Minimum QGIS version: 3.28

## Inputs
- A set of categorical rasters representing LULC classes for multiple years
- Optional AOI polygon for clipping and coverage checks
- Optional class legend table to map class ID to label

## Outputs
- CSV files for areas and change metrics
- GeoTIFF rasters for change frequency and hotspots
- CSV values are rounded to 3 decimal places
- Transition matrices exclude NoData by default (optionally include NoData)
- Output units can be pixels, square meters, or square kilometers

## UI behavior highlights
- Floating dock opens centered at 900x700 by default
- Output CRS selector defaults to the project CRS if none is selected
- Raster/Year columns are resizable by dragging
- Splitter between Inputs and Input Validation is draggable
- Progress bar updates per raster block with a counter

## Validation checks
- CRS match
- Pixel size match
- Extent match
- Dimensions match
- Grid alignment (origin)
- Data type (warn on float)
- NoData presence/consistency or override
- Value range per raster
- Unique classes per raster (capped for performance)
- AOI coverage percent (if AOI selected and output dir set)

## Basic workflow
1. Add yearly LULC rasters and their corresponding years.
2. Optionally add a class legend table to map class IDs to labels.
3. (Optional) Add an AOI layer and output directory.
4. Click Validate Inputs and address any warnings.
5. Run the analysis to generate CSV and GeoTIFF outputs.

## Notes
- Heatmap extent handling is under investigation; the extent string includes a CRS tag.
- Icon path in metadata is `icons/icon.png`.

## Project structure
- `main_plugin.py` - main plugin logic and UI wiring
- `core/` - analysis logic
- `ui/` - UI layout and widgets
- `icons/` - plugin icons

## Author
Mukesh Ray
