# Raster Outputs

The plugin generates two types of GeoTIFF rasters: change frequency and change hotspots.

## Change Frequency Raster

**File:** `change_frequency.tif`

A single raster showing how many times each pixel changed class across all time intervals.

### Specifications

| Property | Value |
|----------|-------|
| Data type | Int16 |
| NoData value | -1 |
| Value range | 0 to (n-1), where n = number of input rasters |
| CRS | As specified in Options |
| Resolution | Same as input rasters |

### Values

| Value | Meaning |
|-------|---------|
| -1 | NoData (pixel invalid in one or more years) |
| 0 | No change (same class across all years) |
| 1 | Changed once |
| 2 | Changed twice |
| ... | ... |
| n-1 | Changed in every interval |

### Example

For a 3-raster analysis (2010, 2015, 2020):

- **0**: Pixel was class X in 2010, 2015, and 2020
- **1**: Pixel changed either 2010→2015 OR 2015→2020
- **2**: Pixel changed both 2010→2015 AND 2015→2020

### Styling in QGIS

Recommended symbology for visualization:

1. Right-click the layer → **Properties** → **Symbology**
2. Choose **Singleband pseudocolor**
3. Set **Min** to 0 and **Max** to your maximum change count
4. Choose a sequential color ramp (e.g., Viridis, YlOrRd)
5. Click **Classify**

Example color scheme:

| Value | Color | Description |
|-------|-------|-------------|
| 0 | Light gray | Stable/persistent |
| 1 | Yellow | Low change |
| 2 | Orange | Moderate change |
| 3+ | Red | High change |

### Use Cases

- **Identify stable areas**: Pixels with value 0
- **Find dynamic zones**: Pixels with high values
- **Prioritize monitoring**: Focus on frequently changing areas
- **Validate classifications**: High change frequency might indicate classification errors

---

## Change Hotspot Rasters

**File:** `change_hotspot_{year0}_{year1}.tif` (one per interval)

Kernel density surfaces showing concentrations of change locations.

### Specifications

| Property | Value |
|----------|-------|
| Data type | Float32 |
| NoData value | -9999 |
| Value range | 0 to maximum density |
| CRS | As specified in Options |
| Resolution | Same as input rasters |
| Kernel | Gaussian |
| Radius | 1000 map units |

### How Hotspots Are Generated

1. All pixels that changed class are identified
2. Their centroids are converted to point locations
3. Up to 50,000 points are sampled (for performance)
4. Kernel Density Estimation (KDE) is applied
5. Result is a smooth density surface

### Values

- **0**: No nearby change
- **Higher values**: Greater concentration of change
- Values are not normalized between intervals

!!! note "Relative Comparison"
    Hotspot values are relative within each raster. To compare across intervals, consider normalizing or using consistent symbology.

### Styling in QGIS

Recommended visualization:

1. Right-click the layer → **Properties** → **Symbology**
2. Choose **Singleband pseudocolor**
3. Set interpolation to **Linear**
4. Use a heat-style color ramp (e.g., Magma, Inferno)
5. Set **Min** to 0 and let QGIS calculate **Max**

For consistent comparison across intervals:

- Note the maximum value across all hotspot rasters
- Set the same Min/Max for all layers
- Use identical color ramp settings

### Use Cases

- **Visualize change clusters**: See where change is concentrated
- **Identify change fronts**: Urban expansion, deforestation edges
- **Compare intervals**: Which period had more concentrated change?
- **Support narratives**: "Change was concentrated in the northeast"

---

## Working with Raster Outputs

### Viewing in QGIS

Rasters are automatically added to your QGIS project. If not visible:

1. **Layer** → **Add Layer** → **Add Raster Layer**
2. Navigate to output directory
3. Select the `.tif` file

### Exporting for Other Software

GeoTIFF is widely compatible:

- ArcGIS Pro / ArcMap
- Google Earth Engine
- R (raster, terra packages)
- Python (rasterio, GDAL)

### Combining with Other Data

```python
import rasterio
import numpy as np

# Read change frequency
with rasterio.open('change_frequency.tif') as src:
    freq = src.read(1)
    meta = src.meta

# Create binary mask of high-change areas
high_change = np.where(freq >= 2, 1, 0)
high_change = np.where(freq == -1, -1, high_change)

# Write output
meta.update(dtype='int16')
with rasterio.open('high_change_mask.tif', 'w', **meta) as dst:
    dst.write(high_change.astype('int16'), 1)
```

### Zonal Statistics

Combine with polygon boundaries:

1. Load change frequency raster
2. Load administrative boundaries (polygon layer)
3. Use **Processing** → **Raster Analysis** → **Zonal Statistics**
4. Calculate mean change frequency per zone

### Creating Maps

For publication-quality maps:

1. Style raster layers appropriately
2. Add basemap or context layers
3. Use **Project** → **New Print Layout**
4. Add map, legend, scale bar, north arrow
5. Export as PDF or image

---

## Technical Notes

### Memory and Performance

- Block-based processing keeps memory usage bounded
- Large rasters process in chunks (256×256 pixels)
- Hotspot generation samples up to 50,000 points for performance

### Coordinate Reference System

Raster outputs use the CRS specified in Options:

- Default: Project CRS
- Can be set to any valid CRS
- Reprojection uses nearest-neighbor (preserves categorical values)

### NoData Handling

- Pixels that are NoData in ANY input year get NoData in change frequency
- Hotspots only consider pixels valid in both years of the interval
