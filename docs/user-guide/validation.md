# Validation

The plugin includes comprehensive validation to ensure your inputs are compatible and will produce meaningful results. Always validate before running an analysis.

## Running Validation

1. Configure your inputs in the **Inputs** tab
2. Click the **Validate Inputs** button
3. Switch to the **Validation** tab to see results

## Validation Results

Each check displays one of three status indicators:

| Status | Meaning |
|--------|---------|
| :material-check-circle:{ style="color: green" } **PASS** | Check passed - no issues |
| :material-alert:{ style="color: orange" } **WARN** | Warning - analysis can proceed but review recommended |
| :material-close-circle:{ style="color: red" } **FAIL** | Failed - must be fixed before analysis |

!!! danger "FAIL Items"
    You cannot run the analysis if any check shows FAIL. Fix the underlying issue and re-validate.

## Validation Checks

### CRS Consistency

**Check**: All rasters use the same Coordinate Reference System.

**PASS**: All rasters have identical CRS.

**FAIL**: Rasters have different CRS values.

**How to fix**:

- Reproject rasters to a common CRS using QGIS raster tools
- Use **Raster** > **Projections** > **Warp (Reproject)**

!!! warning "Reprojection Warning"
    When reprojecting categorical rasters, always use **Nearest Neighbor** resampling to preserve class values.

---

### Pixel Size Consistency

**Check**: All rasters have identical pixel dimensions.

**PASS**: All rasters have the same X and Y pixel size.

**FAIL**: Pixel sizes differ between rasters.

**How to fix**:

- Resample rasters to a common resolution
- Use **Raster** > **Projections** > **Warp (Reproject)** with target resolution

---

### Extent Consistency

**Check**: All rasters cover the same geographic extent.

**PASS**: All rasters have identical bounding boxes.

**FAIL**: Extents differ between rasters.

**How to fix**:

- Clip rasters to a common extent
- Use **Raster** > **Extraction** > **Clip Raster by Extent**

---

### Dimensions Consistency

**Check**: All rasters have the same width and height in pixels.

**PASS**: All rasters have identical dimensions.

**FAIL**: Raster dimensions differ.

**How to fix**:

- Usually resolved by fixing extent and pixel size issues
- Ensure all rasters were produced with the same grid specification

---

### Grid Alignment

**Check**: Pixel grids are aligned (same origin coordinates).

**PASS**: All rasters have aligned pixel grids.

**FAIL**: Pixel origins are offset between rasters.

**How to fix**:

- Align rasters using **Processing Toolbox** > **GDAL** > **Raster projections** > **Warp**
- Set a specific target extent that aligns with your grid

!!! info "Why Grid Alignment Matters"
    Even with matching extents and pixel sizes, rasters can be offset by fractions of a pixel. This causes each pixel to represent slightly different areas, making per-pixel comparisons invalid.

---

### Data Type Check

**Check**: Rasters contain integer data types.

**PASS**: All rasters use integer types (Byte, Int16, Int32, etc.).

**WARN**: One or more rasters use floating-point types.

**How to fix** (if needed):

- Convert float rasters to integer
- Use **Raster** > **Conversion** > **Translate** and set output type

!!! note "Float Warning"
    Float rasters can still be processed, but they're unusual for categorical LULC data. The warning ensures you're aware of the data type.

---

### NoData Presence

**Check**: NoData values are defined in raster metadata.

**PASS**: All rasters have NoData values defined.

**WARN**: Some rasters lack NoData definitions.

**How to fix**:

- Use the **Override** option in the Inputs tab to specify a NoData value
- Or set NoData in the source raster using GDAL tools

---

### NoData Consistency

**Check**: All rasters use the same NoData value.

**PASS**: NoData values are consistent.

**WARN**: Different NoData values are used.

**How to fix**:

- Use the **Override** option to specify a single NoData value for all rasters

---

### Value Range Detection

**Status**: Always INFO (informational only)

**Purpose**: Reports the range of class values found in each raster.

**Example output**: `Raster values: 0-15`

!!! tip "Use This Information"
    - Verify the range matches your expected class scheme
    - Identify unexpected values that might indicate data issues
    - Ensure all rasters use the same classification scheme

---

### Unique Class Count

**Status**: Always INFO (informational only)

**Purpose**: Reports the number of unique class values in each raster.

**Example output**: `12 unique classes detected`

!!! note "Class Count Limit"
    Detection is capped at 1024 classes for performance. If you have more than 1024 classes, only the first 1024 are counted.

---

### AOI Coverage

**Status**: Always INFO (informational only, only shown when AOI is selected)

**Purpose**: Reports what percentage of each raster is covered by the AOI.

**Example output**: `AOI covers 45.2% of raster extent`

!!! tip "Coverage Considerations"
    - Very low coverage might indicate AOI/raster misalignment
    - 100% coverage means AOI fully contains the raster
    - Coverage > 100% can occur if AOI extends beyond raster bounds

## Validation Best Practices

### Before Analysis

1. **Always validate** - Never skip validation
2. **Fix all FAIL items** - Analysis cannot proceed with failures
3. **Review all WARN items** - Understand why warnings occurred
4. **Check INFO items** - Verify values match expectations

### Common Validation Scenarios

=== "All PASS"

    Ready to run analysis. Proceed to the Options tab to configure outputs.

=== "Some WARN"

    Analysis can proceed, but review warnings:

    - Float data type: Verify this is expected
    - NoData inconsistency: Consider using Override
    - Missing NoData: Specify a value if needed

=== "Any FAIL"

    Must fix before proceeding:

    1. Note which checks failed
    2. Use QGIS tools to fix source data
    3. Reload rasters if modified externally
    4. Re-run validation

## Troubleshooting Validation

### "CRS mismatch" but CRS looks the same

Different CRS definitions can represent the same system:

- `EPSG:4326` vs `WGS 84` (same but different string)
- Check the actual EPSG codes
- Reproject all to a single well-defined CRS

### "Extent mismatch" by tiny amounts

Floating-point precision can cause tiny differences:

- Clip all rasters to a common extent
- Use the same bounding box coordinates for all

### Validation takes too long

For very large rasters:

- Validation scans class values, which takes time
- Consider working with a subset for testing
- The actual analysis uses efficient block processing

## Next Steps

Once all checks pass:

1. Review [Configuration options](configuration.md)
2. Proceed to [Running Analysis](running-analysis.md)
