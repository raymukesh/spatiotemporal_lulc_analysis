# Adding Inputs

The **Inputs** tab is where you configure the raster data and basic settings for your analysis.

## Raster Input Table

The input table displays all rasters that will be analyzed:

| Column | Description |
|--------|-------------|
| **Raster** | Path to the raster file |
| **Year** | The year this raster represents (editable) |

### Adding Rasters

You have two options for adding rasters:

=== "Add Files"

    Click **Add Files** to open a file browser:

    1. Navigate to your raster files
    2. Select files (.tif, .tiff, or .img formats supported)
    3. Use ++ctrl+click++ to select multiple files
    4. Click **Open**

    !!! info "Supported Formats"
        The plugin supports GeoTIFF (.tif, .tiff) and ERDAS Imagine (.img) formats. All rasters must contain integer categorical data.

=== "Add From Project"

    Click **Add From Project** to select from loaded layers:

    1. A dialog lists all raster layers in your current QGIS project
    2. Check the layers you want to include
    3. Click **OK**

    !!! tip "Load First"
        Make sure your rasters are loaded in QGIS before using this option.

### Automatic Year Detection

The plugin automatically extracts years from filenames:

- Looks for 4-digit patterns: `19XX` or `20XX`
- Examples:
    - `landcover_2010.tif` → Year: 2010
    - `LULC_2015_classified.tif` → Year: 2015
    - `study_area_2020.img` → Year: 2020

!!! warning "Manual Verification"
    Always verify the automatically detected years. Click on the Year cell to edit if needed.

### Managing Rasters

**Reorder rasters**: Drag and drop rows to change the order. Rasters are processed in chronological order by year.

**Remove rasters**: Select a row and press ++delete++ or click the **Remove** button.

!!! note "Minimum Requirement"
    At least one raster is required, but meaningful change analysis needs two or more rasters from different years.

## Area of Interest (AOI)

Optionally limit your analysis to a specific geographic area:

1. Load a polygon layer into QGIS
2. Select it from the **AOI Layer** dropdown
3. Only pixels within the AOI polygon(s) will be analyzed

!!! tip "AOI Benefits"
    - Focus analysis on your study area
    - Exclude irrelevant regions
    - Reduce processing time for large rasters

**AOI Requirements:**

- Must be a polygon or multipolygon layer
- Should overlap with your raster extent
- Can contain multiple features (all will be used)

## NoData Handling

Configure how the plugin handles NoData (null/missing) values:

### Use Raster NoData

Select **Use raster NoData** to use the NoData value defined in each raster's metadata:

- Most GeoTIFFs have NoData values defined
- Common values: -9999, 0, 255, etc.
- The plugin reads this from GDAL metadata

### Override NoData

Select **Override** to specify a custom NoData value:

1. Enter the value in the text field
2. This value will be treated as NoData in ALL input rasters

!!! warning "Override Carefully"
    When overriding, ensure the value you specify is not a valid class ID in any of your rasters.

### Include NoData in Transitions

Check **Include NoData class in transitions** to treat NoData as a valid class:

- **Unchecked (default)**: NoData pixels are excluded from all calculations
- **Checked**: Transitions to/from NoData are tracked in the transition matrix

This is useful when:

- NoData represents a meaningful category (e.g., "No Data" or "Unclassified")
- You want to track data coverage changes over time

## Output Directory

Specify where analysis results will be saved:

1. Click **Browse**
2. Select or create a folder
3. The path appears in the text field

!!! important "Required"
    You must specify an output directory before running the analysis.

**Output structure:**

```
output_directory/
├── area_by_class.csv
├── net_gross_change_2010_2015.csv
├── net_gross_change_2015_2020.csv
├── transition_matrix_2010_2015.csv
├── transition_matrix_2015_2020.csv
├── transition_matrix_first_last_2010_2020.csv
├── top_transitions_2010_2015.csv
├── change_intensity.csv
├── change_frequency.tif
├── change_hotspot_2010_2015.tif
├── change_hotspot_2015_2020.tif
└── charts/
    ├── area_by_class.html
    ├── net_gross_change.html
    ├── transition_matrix_2010_2015.html
    └── ...
```

## Input Requirements Summary

| Requirement | Details |
|-------------|---------|
| **Format** | GeoTIFF (.tif, .tiff) or ERDAS Imagine (.img) |
| **Data type** | Integer (categorical). Float triggers a warning. |
| **CRS** | All rasters must have the same CRS |
| **Pixel size** | All rasters must have identical resolution |
| **Extent** | All rasters should cover the same area |
| **Grid alignment** | Pixel grids must align (same origin) |
| **Minimum count** | At least 1 raster (2+ for change analysis) |

!!! tip "Validation"
    Run validation to verify all requirements are met before analysis. See [Validation](validation.md) for details.

## Next Steps

After adding inputs:

1. [Configure the legend](configuration.md) (optional but recommended)
2. [Set output options](configuration.md#output-options)
3. [Validate your inputs](validation.md)
