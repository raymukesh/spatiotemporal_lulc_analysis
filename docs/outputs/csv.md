# CSV Outputs

The plugin generates several CSV files containing quantitative metrics about land use/land cover change.

## Area by Class

**File:** `area_by_class.csv`

Contains the area and percentage of each class for every input year.

### Columns

| Column | Description |
|--------|-------------|
| `class_id` | Numeric class identifier |
| `class_label` | Class name (from legend, or class ID if no legend) |
| `{year}_area` | Area in selected units for that year |
| `{year}_pct` | Percentage of total valid area for that year |

### Example

```csv
class_id,class_label,2010_area,2010_pct,2015_area,2015_pct,2020_area,2020_pct
1,Forest,450.250,45.025,420.100,42.010,395.500,39.550
2,Agriculture,320.500,32.050,345.200,34.520,360.800,36.080
3,Urban,125.750,12.575,145.300,14.530,168.200,16.820
4,Water,85.000,8.500,75.400,7.540,62.500,6.250
5,Barren,18.500,1.850,14.000,1.400,13.000,1.300
```

### Use Cases

- Track class expansion or contraction over time
- Calculate percentage change between years
- Create time series charts
- Document baseline and final conditions

---

## Net/Gross Change

**File:** `net_gross_change_{year0}_{year1}.csv` (one per interval)

Contains gain, loss, net change, and gross change for each class within an interval.

### Columns

| Column | Description |
|--------|-------------|
| `class_id` | Numeric class identifier |
| `class_label` | Class name |
| `gain` | Area gained by this class (from other classes) |
| `loss` | Area lost by this class (to other classes) |
| `net_change` | Gain minus loss (positive = expansion) |
| `gross_change` | Gain plus loss (total turnover) |

### Example

```csv
class_id,class_label,gain,loss,net_change,gross_change
1,Forest,5.200,35.350,-30.150,40.550
2,Agriculture,28.500,3.800,24.700,32.300
3,Urban,22.100,2.550,19.550,24.650
4,Water,0.500,10.100,-9.600,10.600
5,Barren,3.200,7.700,-4.500,10.900
```

### Interpretation

- **Positive net change**: Class is expanding
- **Negative net change**: Class is contracting
- **High gross with low net**: Class has high turnover but stable total area
- **Gain**: Other classes converting TO this class
- **Loss**: This class converting TO other classes

---

## Transition Matrix

**File:** `transition_matrix_{year0}_{year1}.csv` (one per interval)

Full from-to transition matrix showing area converted between every class pair.

### Structure

|  | To Class 1 | To Class 2 | To Class 3 | ... |
|--|------------|------------|------------|-----|
| **From Class 1** | Persistence | Transition | Transition | ... |
| **From Class 2** | Transition | Persistence | Transition | ... |
| **From Class 3** | Transition | Transition | Persistence | ... |

### Example

```csv
,Forest,Agriculture,Urban,Water,Barren
Forest,420.100,25.200,15.600,2.100,2.450
Agriculture,3.200,295.500,18.500,1.200,2.100
Urban,0.500,1.500,123.200,0.050,0.500
Water,1.200,0.800,0.100,72.300,0.600
Barren,0.300,1.700,0.500,0.150,15.850
```

### Reading the Matrix

- **Rows**: "From" class (original class in year 0)
- **Columns**: "To" class (final class in year 1)
- **Diagonal**: Area that remained in the same class (persistence)
- **Off-diagonal**: Area that changed from one class to another

### Use Cases

- Identify specific conversion pathways
- Calculate persistence rates
- Build Sankey diagrams
- Support detailed change accounting

---

## Transition Matrix (First to Last)

**File:** `transition_matrix_first_last_{year0}_{yearN}.csv`

Single transition matrix comparing only the first and last year of the time series, ignoring intermediate years.

### Purpose

- Summarize total change over the entire study period
- Avoid double-counting intermediate transitions
- Provide a clean "before and after" comparison

### Format

Same structure as interval transition matrices.

---

## Top Transitions

**File:** `top_transitions_{year0}_{year1}.csv` (one per interval)

Ranked list of the largest class-to-class conversions, excluding persistence.

### Columns

| Column | Description |
|--------|-------------|
| `rank` | Rank by area (1 = largest) |
| `from_class` | Original class label |
| `to_class` | Final class label |
| `area` | Area converted |
| `percent` | Percentage of total changed area |

### Example

```csv
rank,from_class,to_class,area,percent
1,Forest,Agriculture,25.200,31.25
2,Agriculture,Urban,18.500,22.93
3,Forest,Urban,15.600,19.33
4,Water,Forest,1.200,1.49
5,Agriculture,Barren,2.100,2.60
```

### Notes

- Only shows actual transitions (excludes diagonal/persistence)
- Limited to top 20 transitions
- Ranked by area in descending order
- Percentages sum to 100% (of total change, not total area)

---

## Change Intensity

**File:** `change_intensity.csv`

Change intensity metrics for each interval.

### Columns

| Column | Description |
|--------|-------------|
| `interval` | Year range (e.g., "2010-2015") |
| `years` | Number of years in interval |
| `total_pixels` | Total valid pixels analyzed |
| `changed_pixels` | Pixels that changed class |
| `interval_intensity` | Fraction of pixels that changed |
| `annual_intensity` | Interval intensity divided by years |

### Example

```csv
interval,years,total_pixels,changed_pixels,interval_intensity,annual_intensity
2010-2015,5,1000000,85000,0.085,0.017
2015-2020,5,1000000,92000,0.092,0.0184
```

### Interpretation

- **Interval intensity**: Proportion of landscape that changed
- **Annual intensity**: Average per-year change rate
- Use to compare change rates across intervals
- Values range from 0 (no change) to 1 (complete change)

---

## Working with CSV Outputs

### Opening in Spreadsheet Software

All CSVs are compatible with:

- Microsoft Excel
- Google Sheets
- LibreOffice Calc
- Any CSV-capable software

### Importing into Analysis Tools

```python
import pandas as pd

# Read area by class
area_df = pd.read_csv('area_by_class.csv')

# Read transition matrix
transition_df = pd.read_csv('transition_matrix_2010_2015.csv', index_col=0)

# Calculate persistence rate
diagonal = transition_df.values.diagonal().sum()
total = transition_df.values.sum()
persistence_rate = diagonal / total
```

### Combining with Other Data

CSV outputs can be joined with:

- External attribute data
- Socioeconomic indicators
- Climate data
- Other GIS analysis results
