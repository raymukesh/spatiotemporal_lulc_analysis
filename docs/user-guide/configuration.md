# Configuration

The **Legend** and **Options** tabs let you configure how the analysis is performed and what outputs are generated.

## Legend Tab

The legend maps numeric class IDs to human-readable labels. While optional, adding a legend significantly improves the readability of outputs.

### Adding Class Labels

1. Switch to the **Legend** tab
2. Click **Add Row** to add a new entry
3. Enter the **Class ID** (integer)
4. Enter the **Label** (text description)

| Class ID | Label |
|----------|-------|
| 1 | Forest |
| 2 | Agriculture |
| 3 | Urban |
| 4 | Water |
| 5 | Barren |

### Managing Legend Entries

- **Edit**: Click on any cell to modify
- **Remove**: Select a row and click **Remove Row**
- **Clear all**: Click **Clear** to remove all entries

### Where Labels Appear

When a legend is defined, labels appear in:

- All CSV output files
- Chart titles and legends
- Transition matrix headers
- Sankey diagram nodes

!!! tip "Consistent Labeling"
    Use the same legend across multiple analyses for consistent reporting.

### Class ID Limit

The legend supports up to 1024 class entries. This matches the maximum classes detected during validation.

---

## Options Tab

The Options tab controls what outputs are generated and how they're formatted.

### Output Selection

Check or uncheck outputs to include or exclude them:

#### CSV Outputs

| Option | Description | File(s) Generated |
|--------|-------------|-------------------|
| **Area by class** | Per-class area for each year | `area_by_class.csv` |
| **Net/Gross change** | Gain, loss, net, gross per class per interval | `net_gross_change_*.csv` |
| **Transition matrix** | Full from-to matrix per interval | `transition_matrix_*.csv` |
| **Transition (first/last)** | Matrix comparing first and last year only | `transition_matrix_first_last_*.csv` |
| **Top transitions** | Ranked transitions by area | `top_transitions_*.csv` |
| **Change intensity** | Interval and annualized intensity | `change_intensity.csv` |

#### Raster Outputs

| Option | Description | File(s) Generated |
|--------|-------------|-------------------|
| **Change frequency** | Count of changes per pixel | `change_frequency.tif` |
| **Change hotspots** | Kernel density heatmap per interval | `change_hotspot_*.tif` |

#### Chart Outputs

| Option | Description |
|--------|-------------|
| **Generate charts** | Interactive HTML visualizations for all enabled outputs |

!!! note "Charts Require Plotly.js"
    Charts use the bundled Plotly.js library. If the library is missing, charts will be skipped but other outputs proceed normally.

### Output CRS

Set the coordinate reference system for raster outputs:

1. Click the CRS selector button
2. Choose from:
    - **Project CRS** (default)
    - **Layer CRS** from any loaded layer
    - **Custom CRS** by EPSG code or definition

!!! info "CSV Not Affected"
    The output CRS only affects raster outputs. CSV files contain values in the units specified, regardless of CRS.

### Output Units

Choose how area values are expressed:

| Unit | Description | Best For |
|------|-------------|----------|
| **Pixels** | Raw pixel counts | Quick analysis, debugging |
| **Square meters (m²)** | Area in square meters | Local/regional studies |
| **Square kilometers (km²)** | Area in square kilometers | Large-scale studies |

The selected unit affects:

- All area columns in CSV files
- Chart axis labels
- Legend values in visualizations

### Default Settings

All options are enabled by default with these settings:

- Output CRS: Project CRS
- Output Units: Square kilometers

---

## Configuration Best Practices

### For Complete Analysis

Keep all outputs enabled to generate a comprehensive change report:

- [x] Area by class
- [x] Net/Gross change
- [x] Transition matrix
- [x] Transition (first/last)
- [x] Top transitions
- [x] Change intensity
- [x] Change frequency
- [x] Change hotspots
- [x] Generate charts

### For Quick Assessment

Disable intensive outputs for faster processing:

- [x] Area by class
- [x] Net/Gross change
- [x] Top transitions
- [x] Change intensity
- [ ] Transition matrix
- [ ] Transition (first/last)
- [ ] Change frequency
- [ ] Change hotspots
- [ ] Generate charts

### For Spatial Focus

Enable spatial outputs for mapping change patterns:

- [ ] Area by class
- [ ] Net/Gross change
- [ ] Transition matrix
- [ ] Top transitions
- [ ] Change intensity
- [x] Change frequency
- [x] Change hotspots
- [ ] Generate charts

---

## Configuration Checklist

Before running analysis, verify:

- [ ] Output directory is set (Inputs tab)
- [ ] Legend entries added (if desired)
- [ ] Appropriate outputs selected
- [ ] Output CRS is correct
- [ ] Output units are appropriate for your study

## Next Steps

Once configured:

1. Return to [Validation](validation.md) to verify inputs
2. Proceed to [Running Analysis](running-analysis.md)
