# Spatiotemporal LULC Analysis - Notes

## Current Context
This plugin started as "Land Change Accounting" and has been renamed to "Spatiotemporal LULC Analysis".
The installed QGIS plugin folder has been renamed to:
C:\Users\140790\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\spatiotemporal_lulc_analysis

## Core Features
- Area by class per year (CSV)
- Net/gross change per interval (CSV)
- Transition matrix per interval (CSV)
- Top transitions ranking (CSV)
- Change frequency raster across all years (GeoTIFF)
- Change intensity per interval (CSV)
- Change hotspots (heatmap) per interval (GeoTIFF)

## UI and Behavior
- Floating dock opens centered and larger by default (900x700).
- Output CRS selector defaults to project CRS if none selected.
- Class legend table allows mapping class ID -> label; labels are included in CSVs.
- Input Validation panel with a Validate Inputs button and detailed checks.
- About and Help buttons at the bottom with detailed text.
- Raster/Year columns are resizable by dragging.
- Progress bar updates per raster block with a counter.
- Splitter between Inputs and Input Validation is draggable.

## Validation Checks Included
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

## Outputs Formatting
- CSV float values are rounded to 3 decimal places.
- Transition matrix excludes NoData class by default but can include it via checkbox.

## Metadata
- Plugin name: Spatiotemporal LULC Analysis
- Author: Mukesh Ray
- Description updated to list analysis types
- Icon path set to icons\icon.png (ensure icon.png exists in icons/)

## Known Issues/Notes
- Heatmap extent still under investigation; extent string now includes CRS tag.
- Project folder rename required manual permission change.

## Paths
Source: C:\my apps\lulc-plugin\spatiotemporal_lulc_analysis
Installed: C:\Users\140790\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\spatiotemporal_lulc_analysis
