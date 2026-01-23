# Formulas

This page provides the mathematical formulas used in the Spatiotemporal LULC Analysis plugin.

## Notation

| Symbol | Definition |
|--------|------------|
| $\Omega_t$ | Set of valid pixels at time $t$ (after NoData and AOI masking) |
| $L_t(p)$ | Class label of pixel $p$ at time $t$ |
| $A_{px}$ | Area per pixel in selected units |
| $\mathbf{1}[\cdot]$ | Indicator function (1 if condition true, 0 otherwise) |

---

## Area by Class

### Pixel Count

The number of pixels belonging to class $k$ at time $t$:

$$A_{k,t} = \sum_{p \in \Omega_t} \mathbf{1}[L_t(p) = k]$$

This counts all valid pixels where the class label equals $k$.

### Area

Convert pixel count to area using the pixel area factor:

$$\text{Area}_{k,t} = A_{k,t} \cdot A_{px}$$

Where $A_{px}$ depends on output units:

| Units | $A_{px}$ Value |
|-------|---------------|
| Pixels | 1 |
| Square meters | pixel width × pixel height (in meters) |
| Square kilometers | pixel area in m² ÷ 1,000,000 |

### Percentage

Class percentage of total valid area:

$$\text{Percent}_{k,t} = \frac{A_{k,t}}{\sum_k A_{k,t}} \times 100$$

---

## Interval Metrics

### Valid Pixel Set

For interval $t_0 \to t_1$, only pixels valid in both years are analyzed:

$$\Omega = \Omega_{t_0} \cap \Omega_{t_1}$$

### Total Pixels

$$\text{Total} = |\Omega|$$

### Changed Pixels

Count pixels where the class differs between years:

$$\text{Changed} = \sum_{p \in \Omega} \mathbf{1}[L_{t_0}(p) \ne L_{t_1}(p)]$$

### Unchanged Pixels

$$\text{Unchanged} = \text{Total} - \text{Changed}$$

---

## Gain and Loss

### Gain

Pixels that transitioned **into** class $k$:

$$\text{Gain}_k = \sum_{p \in \Omega} \mathbf{1}[L_{t_1}(p) = k \land L_{t_0}(p) \ne L_{t_1}(p)]$$

Only pixels that actually changed class are counted as gains.

### Loss

Pixels that transitioned **out of** class $k$:

$$\text{Loss}_k = \sum_{p \in \Omega} \mathbf{1}[L_{t_0}(p) = k \land L_{t_0}(p) \ne L_{t_1}(p)]$$

### Net Change

$$\text{Net}_k = \text{Gain}_k - \text{Loss}_k$$

- Positive: Class expanded
- Negative: Class contracted
- Zero: Balanced turnover

### Gross Change

$$\text{Gross}_k = \text{Gain}_k + \text{Loss}_k$$

Total turnover for the class, regardless of direction.

---

## Transition Matrix

### Matrix Definition

The transition matrix $M$ counts pixel movements between classes:

$$M_{i,j} = \sum_{p \in \Omega} \mathbf{1}[L_{t_0}(p) = i \land L_{t_1}(p) = j]$$

Where:

- $i$ = class at time $t_0$ (row index)
- $j$ = class at time $t_1$ (column index)
- $M_{i,j}$ = count of pixels moving from $i$ to $j$

### Matrix Properties

**Diagonal elements** ($M_{i,i}$): Pixels that stayed in class $i$ (persistence)

**Off-diagonal elements** ($M_{i,j}$ where $i \ne j$): Pixels that changed from $i$ to $j$

**Row sum**: Total area of class $i$ at $t_0$

$$\sum_j M_{i,j} = A_{i,t_0}$$

**Column sum**: Total area of class $j$ at $t_1$

$$\sum_i M_{i,j} = A_{j,t_1}$$

### Relationship to Gain/Loss

$$\text{Gain}_k = \sum_{i \ne k} M_{i,k}$$

$$\text{Loss}_k = \sum_{j \ne k} M_{k,j}$$

---

## Top Transitions

### Total Changed Area

Sum of all off-diagonal elements:

$$\text{Total}_{\text{change}} = \sum_{i \ne j} M_{i,j}$$

### Transition Percentage

Share of total change for each transition:

$$\text{Percent}_{i,j} = \frac{M_{i,j}}{\text{Total}_{\text{change}}} \times 100$$

### Transition Area

$$\text{Area}_{i,j} = M_{i,j} \cdot A_{px}$$

---

## Change Intensity

### Interval Intensity

Proportion of pixels that changed within the interval:

$$I_{\text{interval}} = \frac{\text{Changed}}{\text{Total}}$$

Range: 0 (no change) to 1 (complete change)

### Annual Intensity

Average per-year change rate:

$$I_{\text{annual}} = \frac{I_{\text{interval}}}{t_1 - t_0}$$

Where $(t_1 - t_0)$ is the number of years in the interval.

---

## Change Frequency Raster

### Per-Pixel Frequency

For a time series with $T$ observations, the change frequency at pixel $p$:

$$F(p) = \sum_{t=1}^{T-1} \mathbf{1}[L_t(p) \ne L_{t+1}(p)]$$

### Conditions

- Computed only if $p$ is valid in all years
- NoData (-1) if $p$ is invalid in any year
- Range: 0 to $T-1$

---

## Change Hotspots

### Point Generation

Changed pixels are converted to point events with unit weight at their centroid locations.

### Kernel Density Estimation

The density at location $(x, y)$ is:

$$\hat{f}(x, y) = \sum_{i=1}^{n} K\left(\frac{d_i}{h}\right)$$

Where:

- $n$ = number of change points (up to 50,000)
- $K$ = Gaussian kernel function
- $d_i$ = distance from $(x, y)$ to point $i$
- $h$ = bandwidth (1000 map units)

### Gaussian Kernel

$$K(u) = \frac{1}{\sqrt{2\pi}} e^{-\frac{u^2}{2}}$$

---

## Unit Conversions

### Area Factor

The area factor $A_{px}$ converts pixel counts to area:

$$A_{px} = |X_{\text{res}}| \times |Y_{\text{res}}| \times S$$

Where:

- $X_{\text{res}}$ = pixel width (from raster metadata)
- $Y_{\text{res}}$ = pixel height (from raster metadata)
- $S$ = scale factor based on CRS units and output units

### Scale Factor

| CRS Units | Output Units | Scale Factor |
|-----------|--------------|--------------|
| Meters | Pixels | 0 (use count) |
| Meters | m² | 1 |
| Meters | km² | 1/1,000,000 |
| Degrees | m² | Requires projection |

---

## Summary Table

| Metric | Formula | Output Type |
|--------|---------|-------------|
| Area by class | $A_{k,t} \cdot A_{px}$ | CSV |
| Percentage | $\frac{A_{k,t}}{\sum_k A_{k,t}} \times 100$ | CSV |
| Gain | $\sum_{i \ne k} M_{i,k}$ | CSV |
| Loss | $\sum_{j \ne k} M_{k,j}$ | CSV |
| Net change | $\text{Gain}_k - \text{Loss}_k$ | CSV |
| Gross change | $\text{Gain}_k + \text{Loss}_k$ | CSV |
| Transition count | $M_{i,j}$ | CSV |
| Interval intensity | $\frac{\text{Changed}}{\text{Total}}$ | CSV |
| Annual intensity | $\frac{I_{\text{interval}}}{t_1 - t_0}$ | CSV |
| Change frequency | $\sum_{t=1}^{T-1} \mathbf{1}[L_t(p) \ne L_{t+1}(p)]$ | Raster |
| Hotspot density | $\sum_{i=1}^{n} K\left(\frac{d_i}{h}\right)$ | Raster |
