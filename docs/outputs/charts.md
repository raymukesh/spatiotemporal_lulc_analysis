# Chart Outputs

The plugin generates interactive HTML charts using Plotly.js. These charts provide visual representations of the tabular outputs.

## Chart Technology

All charts are:

- **Standalone HTML files** - No server required
- **Interactive** - Zoom, pan, hover for details
- **Self-contained** - Plotly.js is embedded in each file
- **Responsive** - Resize with the browser window

!!! info "Opening Charts"
    Double-click any `.html` file to open it in your default web browser.

---

## Area by Class Chart

**File:** `charts/area_by_class.html`

Multi-line chart showing area trends for each class over time.

### Features

- One line per class
- X-axis: Years
- Y-axis: Area in selected units
- Legend: Click to show/hide classes
- Hover: Exact values for each point

### Interactions

| Action | Result |
|--------|--------|
| Hover | Show exact area value |
| Click legend | Toggle class visibility |
| Double-click legend | Isolate single class |
| Drag | Zoom to selection |
| Double-click plot | Reset zoom |

### Use Cases

- Visualize expansion/contraction trends
- Compare class trajectories
- Identify inflection points
- Present temporal patterns

---

## Net/Gross Change Charts

**Files:**
- `charts/net_gross_change.html` - Per-interval bar charts
- `charts/net_gross_combined.html` - Multi-interval comparison

### Per-Interval Chart

Paired bar chart showing:

- **Green bars**: Gain (area acquired from other classes)
- **Red bars**: Loss (area converted to other classes)
- One pair per class

### Combined Chart

Grouped bar chart comparing all intervals:

- Groups by class
- Bars for each interval's net change
- Useful for comparing change patterns across periods

### Interactions

| Action | Result |
|--------|--------|
| Hover | Show exact gain/loss value |
| Click legend | Toggle gain/loss visibility |
| Drag | Zoom to selection |

---

## Transition Matrix Heatmaps

**Files:** `charts/transition_matrix_{year0}_{year1}.html`

Heatmap visualization of the transition matrix.

### Features

- Rows: "From" classes
- Columns: "To" classes
- Color intensity: Area converted
- Diagonal: Persistence (typically darkest)

### Color Scale

- **Light colors**: Low transition area
- **Dark colors**: High transition area
- Diagonal often dominates (high persistence)

### Interactions

| Action | Result |
|--------|--------|
| Hover | Show exact transition value |
| Drag | Zoom to region |
| Double-click | Reset view |

### Tips

- Hover over cells to see exact values
- Compare off-diagonal cells to identify key conversions
- Large diagonal values indicate stable landscapes

---

## Top Transitions Chart

**Files:** `charts/top_transitions_{year0}_{year1}.html`

Horizontal bar chart showing the 20 largest transitions.

### Features

- Bars ranked by area (largest at top)
- Labels show "From → To" classes
- Length proportional to area converted
- Excludes persistence (diagonal)

### Interactions

| Action | Result |
|--------|--------|
| Hover | Show area and percentage |
| Drag Y-axis | Scroll through transitions |
| Drag X-axis | Zoom area scale |

### Use Cases

- Quickly identify dominant conversions
- Support narratives about change drivers
- Compare transition magnitudes

---

## Change Intensity Chart

**File:** `charts/intensity.html`

Line chart showing change intensity across intervals.

### Features

- Two metrics plotted:
  - **Interval intensity**: Fraction changed per interval
  - **Annual intensity**: Annualized rate
- X-axis: Interval midpoint or label
- Y-axis: Intensity value (0 to 1)

### Interpretation

- Higher values = more change
- Increasing trend = accelerating change
- Decreasing trend = stabilizing landscape

---

## Sankey Diagram

**File:** `charts/sankey.html`

Flow diagram showing all transitions across all intervals.

### Features

- Nodes: Classes (repeated for each year)
- Links: Flows between classes
- Link width: Proportional to area
- Colors: Match class colors

### Reading the Sankey

- Left to right: Time progression
- Vertical bands: Class areas at each time point
- Connecting flows: Transitions between classes
- Thick flows: Large conversions
- Thin flows: Small conversions

### Interactions

| Action | Result |
|--------|--------|
| Hover on node | Highlight connected flows |
| Hover on link | Show exact transition value |
| Drag node | Reposition for clarity |

### Limitations

- Limited to 5,000 links for performance
- Very complex time series may be hard to read
- Consider using transition matrices for detailed analysis

---

## Working with Charts

### Embedding in Reports

**Screenshot method:**

1. Open chart in browser
2. Zoom/configure as needed
3. Take screenshot
4. Paste into document

**HTML embed method:**

```html
<iframe src="charts/area_by_class.html" width="100%" height="500"></iframe>
```

### Exporting as Images

Plotly charts have a built-in camera icon:

1. Hover over the chart
2. Click the camera icon in the toolbar
3. PNG image downloads automatically

### Customizing Charts

For advanced customization, edit the HTML files:

```html
<!-- Find the layout configuration -->
<script>
var layout = {
    title: 'Area by Class',
    xaxis: { title: 'Year' },
    yaxis: { title: 'Area (km²)' }
};
// Modify title, colors, fonts, etc.
</script>
```

### Sharing Charts

Options for sharing:

1. **Email**: Attach HTML file (recipient opens in browser)
2. **Web hosting**: Upload to any web server
3. **Local network**: Share file path
4. **Screenshots**: Export as PNG images

---

## Troubleshooting Charts

### Charts Not Generated

**Check:**

- "Generate charts" enabled in Options?
- Does `vendor/js/plotly.min.js` exist?
- Any errors in the log panel?

### Charts Load Slowly

**Causes:**

- Large Plotly.js file (~5MB) embedded in each HTML
- Browser caching helps after first load
- Consider using relative references (advanced)

### Charts Display Incorrectly

**Try:**

- Open in different browser
- Clear browser cache
- Check for JavaScript console errors

### Missing Classes in Charts

**Check:**

- Classes with zero area may be omitted
- NoData class excluded by default
- Verify legend mappings in plugin
