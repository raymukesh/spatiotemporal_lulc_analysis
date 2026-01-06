# -*- coding: utf-8 -*-

def compute_intensity_rows(interval_results):
    rows = []
    for r0, r1, _, _, result in interval_results:
        total = result['total_pixels']
        changed = result['changed_pixels']
        interval_years = r1.year - r0.year
        interval_intensity = (changed / total) if total else 0.0
        annualized = interval_intensity / interval_years if interval_years else 0.0
        rows.append([
            r0.year,
            r1.year,
            interval_years,
            changed,
            total,
            interval_intensity,
            annualized,
        ])
    return rows
