# Output Overview

The Spatiotemporal LULC Analysis plugin generates three types of outputs: CSV tables, GeoTIFF rasters, and interactive HTML charts.

## Output Summary

| Type | Format | Purpose |
|------|--------|---------|
| **Tabular** | CSV | Quantitative metrics and statistics |
| **Spatial** | GeoTIFF | Mapped change patterns |
| **Visual** | HTML | Interactive charts and diagrams |

## Output Directory Structure

All outputs are saved to your specified output directory:

```
output_directory/
│
├── area_by_class.csv                    # Area per class per year
├── net_gross_change_2010_2015.csv       # Gain/loss per interval
├── net_gross_change_2015_2020.csv
├── transition_matrix_2010_2015.csv      # Full from-to matrix
├── transition_matrix_2015_2020.csv
├── transition_matrix_first_last_2010_2020.csv
├── top_transitions_2010_2015.csv        # Ranked transitions
├── top_transitions_2015_2020.csv
├── change_intensity.csv                 # Intensity metrics
│
├── change_frequency.tif                 # Change count raster
├── change_hotspot_2010_2015.tif         # Hotspot per interval
├── change_hotspot_2015_2020.tif
│
└── charts/                              # Interactive visualizations
    ├── area_by_class.html
    ├── net_gross_change.html
    ├── net_gross_combined.html
    ├── transition_matrix_2010_2015.html
    ├── transition_matrix_2015_2020.html
    ├── top_transitions_2010_2015.html
    ├── intensity.html
    └── sankey.html
```

## Output Types at a Glance

### CSV Outputs

Tabular data for quantitative analysis and reporting:

| File | Content | Use Case |
|------|---------|----------|
| `area_by_class.csv` | Area and percentage per class for each year | Track class trends over time |
| `net_gross_change_*.csv` | Gain, loss, net, and gross change per class | Understand class dynamics |
| `transition_matrix_*.csv` | Full from-to transition counts | Detailed change accounting |
| `top_transitions_*.csv` | Top 20 transitions ranked by area | Identify dominant conversions |
| `change_intensity.csv` | Interval and annualized change rates | Compare change rates |

[Detailed CSV documentation →](csv.md)

### Raster Outputs

Spatial data for mapping and further GIS analysis:

| File | Content | Use Case |
|------|---------|----------|
| `change_frequency.tif` | Count of changes per pixel (0 to n-1) | Map persistent vs. dynamic areas |
| `change_hotspot_*.tif` | Kernel density of change locations | Identify change concentrations |

[Detailed raster documentation →](rasters.md)

### Chart Outputs

Interactive HTML visualizations powered by Plotly.js:

| File | Visualization | Use Case |
|------|---------------|----------|
| `area_by_class.html` | Multi-line chart | Visualize area trends |
| `net_gross_change.html` | Bar charts | Compare gain vs. loss |
| `transition_matrix_*.html` | Heatmaps | Visualize transition patterns |
| `top_transitions_*.html` | Horizontal bars | Show dominant transitions |
| `intensity.html` | Line chart | Plot change intensity |
| `sankey.html` | Sankey diagram | Show all flows across intervals |

[Detailed chart documentation →](charts.md)

## Units and Formatting

### Area Units

Depending on your configuration, area values appear as:

| Setting | Example Value | Description |
|---------|---------------|-------------|
| Pixels | `125000` | Raw pixel count |
| Square meters | `112500000.000` | Area in m² |
| Square kilometers | `112.500` | Area in km² |

### Number Formatting

- Float values: 3 decimal places
- Integer counts: No decimal places
- Percentages: 3 decimal places

### Missing Data

- Empty cells in CSV indicate no data or not applicable
- `-1` in rasters indicates NoData
- Charts omit NoData classes

## Interpreting Outputs

### For Land Cover Reporting

Use these outputs to document LULC changes:

1. **`area_by_class.csv`** - Establish baseline and final class distributions
2. **`net_gross_change_*.csv`** - Document net expansion or contraction per class
3. **`transition_matrix_first_last_*.csv`** - Summarize total conversions

### For Change Pattern Analysis

Use these outputs to understand spatial patterns:

1. **`change_frequency.tif`** - Map areas of repeated change
2. **`change_hotspot_*.tif`** - Identify change clusters
3. **`top_transitions_*.csv`** - Understand dominant conversion types

### For Presentation and Sharing

Use these outputs for reports and presentations:

1. **`charts/*.html`** - Embed or screenshot for reports
2. **`sankey.html`** - Show comprehensive flow diagram
3. **Styled rasters** - Add symbology in QGIS and export maps

## Next Steps

- [CSV Outputs](csv.md) - Detailed tabular output documentation
- [Raster Outputs](rasters.md) - Spatial output documentation
- [Chart Outputs](charts.md) - Interactive visualization documentation
