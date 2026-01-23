# FAQ & Troubleshooting

Frequently asked questions and solutions to common issues.

## General Questions

### What types of rasters can I use?

The plugin works with **categorical (classified) rasters** where each pixel value represents a land use/land cover class. Supported formats:

- GeoTIFF (.tif, .tiff)
- ERDAS Imagine (.img)

Data should be integer type. Float rasters will work but trigger a warning.

### How many rasters can I analyze?

There's no hard limit, but practical considerations apply:

- **Minimum**: 1 raster (area statistics only)
- **For change analysis**: 2 or more rasters
- **Recommended**: 2-10 rasters for most analyses
- **Large series**: Processing time increases linearly

### What's the maximum raster size?

The plugin uses block-based processing (256×256 chunks) so memory usage stays bounded regardless of raster size. Very large rasters simply take longer to process.

### Do rasters need to be in the same location?

Yes. All input rasters must:

- Have the same CRS
- Have the same pixel size
- Cover the same extent
- Have aligned pixel grids

The validation step checks all of these requirements.

---

## Input Issues

### "CRS mismatch" error

**Problem**: Rasters have different coordinate reference systems.

**Solution**:

1. Reproject all rasters to a common CRS
2. Use **Raster** → **Projections** → **Warp (Reproject)**
3. Use **Nearest Neighbor** resampling for categorical data

### "Pixel size mismatch" error

**Problem**: Rasters have different resolutions.

**Solution**:

1. Resample to a common resolution
2. Choose the coarsest resolution to avoid artificial precision
3. Use **Nearest Neighbor** resampling

### "Extent mismatch" error

**Problem**: Rasters don't cover the same area.

**Solution**:

1. Clip all rasters to a common extent
2. Use **Raster** → **Extraction** → **Clip Raster by Extent**
3. Use the smallest common extent

### "Grid alignment" error

**Problem**: Pixel grids are offset between rasters.

**Solution**:

1. Align rasters using Warp with a target extent
2. Ensure the target extent coordinates align with pixel boundaries
3. Consider recreating rasters from source data with consistent parameters

### Years not detected correctly

**Problem**: The plugin didn't find the year in the filename.

**Solution**:

- Manually edit the year in the table
- Ensure filenames contain 4-digit years (1990-2099)
- Examples that work: `lulc_2010.tif`, `2015_classified.tif`

---

## Validation Issues

### Float data type warning

**Problem**: Raster uses float instead of integer data type.

**Is this a problem?**

- If your data is truly categorical integers stored as float: No, it will work
- If your data has decimal values: Yes, results may be unexpected

**Solution** (if needed):

1. Convert to integer using **Raster** → **Conversion** → **Translate**
2. Set output data type to Int16 or Int32

### NoData not defined

**Problem**: Raster doesn't have a NoData value in its metadata.

**Solution**:

1. Use the **Override** option in the Inputs tab
2. Enter the value that represents NoData in your data (e.g., 0, 255, -9999)

### Different NoData values

**Problem**: Rasters use different NoData values.

**Solution**:

1. Use the **Override** option to specify a single NoData value
2. This value will be applied to all input rasters

---

## Analysis Issues

### Analysis won't start

**Possible causes**:

- Validation has FAIL items → Fix and re-validate
- No output directory specified → Set in Inputs tab
- No rasters added → Add at least one raster

### Analysis is very slow

**For large rasters**:

1. Disable hotspot generation (most resource-intensive)
2. Disable chart generation
3. Use an AOI to limit the analysis area
4. Consider using lower-resolution data for initial exploration

**For many rasters**:

- Processing time scales linearly with number of rasters
- Consider analyzing in subsets

### Analysis stopped unexpectedly

**Check**:

1. QGIS message bar for errors
2. Log panel in the plugin for messages
3. Available disk space in output directory
4. QGIS stability (try restarting QGIS)

### Memory errors

**Although rare due to block processing**:

1. Close other applications
2. Restart QGIS
3. Disable hotspot generation
4. Process fewer rasters at once

---

## Output Issues

### Missing CSV files

**Check**:

- Is that output type enabled in Options tab?
- Is there an error in the log panel?
- Is there disk space available?

### Missing rasters in QGIS

**Rasters not appearing in Layers panel**:

1. Check if files exist in output directory
2. Manually add via **Layer** → **Add Raster Layer**
3. Check log for errors during raster creation

### Charts not generated

**Check**:

1. Is "Generate charts" enabled in Options tab?
2. Does `vendor/js/plotly.min.js` exist in the plugin folder?
3. Check log for chart-related errors

**If Plotly.js is missing**:

- Charts are disabled but other outputs proceed
- Reinstall the plugin to restore Plotly.js

### Charts won't open

**Try**:

1. Open in a different web browser
2. Check file size (should be several MB due to embedded Plotly.js)
3. Try a simple HTML test file to verify browser works

### Incorrect values in outputs

**Check**:

1. Correct NoData value specified?
2. AOI covering expected area?
3. Class values match your expectations?
4. Output units configured correctly?

---

## Performance Questions

### How can I speed up analysis?

1. **Reduce outputs**: Disable charts, hotspots if not needed
2. **Use AOI**: Analyze only your study area
3. **Fewer rasters**: Process subset first
4. **Lower resolution**: Resample for exploratory analysis

### How much disk space do I need?

Approximate output sizes:

| Output | Size |
|--------|------|
| CSV files | KB to MB (text) |
| Change frequency | Same as input raster |
| Hotspot rasters | Same as input raster per interval |
| Chart HTML files | ~5MB each (includes Plotly.js) |

### Can I run multiple analyses simultaneously?

Not recommended. The plugin is designed for single-threaded operation. Run one analysis at a time for reliable results.

---

## Interpretation Questions

### What does negative net change mean?

The class is losing more area than it's gaining. This indicates:

- Class contraction
- Conversion to other classes
- May indicate land cover conversion trends

### What does high gross with low net mean?

The class has high turnover but stable total area. This indicates:

- Active dynamics
- Balanced gains and losses
- The class is both expanding in some areas and contracting in others

### How do I interpret change frequency?

| Value | Interpretation |
|-------|----------------|
| 0 | Stable/persistent area |
| 1 | Changed once during study period |
| High | Dynamic area, frequent change |
| Max possible | Changed every interval |

### What do hotspot values mean?

- **Low values**: Sparse change
- **High values**: Concentrated change
- Values are relative within each raster
- Not directly comparable across intervals without normalization

---

## Getting Help

### Where can I report bugs?

Report issues on the [GitHub Issues page](https://github.com/raymukesh/spatiotemporal_lulc_analysis/issues).

Include:

- QGIS version
- Plugin version
- Steps to reproduce
- Error messages from log panel
- Sample data if possible (or description)

### Where can I request features?

Use [GitHub Issues](https://github.com/raymukesh/spatiotemporal_lulc_analysis/issues) with the "enhancement" label.

### Is there a user community?

Currently, support is provided through GitHub Issues. Watch the repository for updates and discussions.
