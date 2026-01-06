# -*- coding: utf-8 -*-
import numpy as np
from .raster_reader import iter_blocks, read_block


def _valid_mask(array, nodata):
    if nodata is None:
        return np.ones(array.shape, dtype=bool)
    return array != nodata


def compute_max_class(layers, nodata_list, mask_layer=None, progress=None):
    max_class = 0
    for layer, nodata in zip(layers, nodata_list):
        for col, row, array in iter_blocks(layer, on_block=progress):
            valid = _valid_mask(array, nodata)
            if mask_layer is not None:
                mask = read_block(mask_layer, col, row, array.shape[1], array.shape[0])
                valid &= mask == 1
            if valid.any():
                local_max = int(np.max(array[valid]))
                if local_max > max_class:
                    max_class = local_max
    return max_class


def compute_area_by_class(layer, nodata, mask_layer=None, progress=None):
    counts = {}
    for col, row, array in iter_blocks(layer, on_block=progress):
        valid = _valid_mask(array, nodata)
        if mask_layer is not None:
            mask = read_block(mask_layer, col, row, array.shape[1], array.shape[0])
            valid &= mask == 1
        if not valid.any():
            continue
        values = array[valid].astype(np.int64)
        bincount = np.bincount(values)
        for class_id, count in enumerate(bincount):
            if count:
                counts[class_id] = counts.get(class_id, 0) + int(count)
    return counts


def compute_interval_metrics(layer0, layer1, nodata0, nodata1, mask_layer, max_class, progress=None):
    gain = np.zeros(max_class + 1, dtype=np.int64)
    loss = np.zeros(max_class + 1, dtype=np.int64)
    matrix = np.zeros((max_class + 1, max_class + 1), dtype=np.int64)
    changed_pixels = 0
    total_pixels = 0

    for col, row, array0 in iter_blocks(layer0, on_block=progress):
        array1 = read_block(layer1, col, row, array0.shape[1], array0.shape[0])
        valid = _valid_mask(array0, nodata0) & _valid_mask(array1, nodata1)
        if mask_layer is not None:
            mask = read_block(mask_layer, col, row, array0.shape[1], array0.shape[0])
            valid &= mask == 1
        if not valid.any():
            continue
        t0 = array0[valid].astype(np.int64)
        t1 = array1[valid].astype(np.int64)
        changed = t0 != t1
        total_pixels += int(valid.sum())
        changed_pixels += int(changed.sum())

        if changed.any():
            gain += np.bincount(t1[changed], minlength=max_class + 1)
            loss += np.bincount(t0[changed], minlength=max_class + 1)

        pair_code = t0 * (max_class + 1) + t1
        counts = np.bincount(pair_code, minlength=(max_class + 1) ** 2)
        matrix += counts.reshape((max_class + 1, max_class + 1))

    return {
        'gain': gain,
        'loss': loss,
        'matrix': matrix,
        'changed_pixels': changed_pixels,
        'total_pixels': total_pixels,
    }


def build_top_transitions(matrix, layer):
    pixel_area_km2 = layer.rasterUnitsPerPixelX() * layer.rasterUnitsPerPixelY() / 1e6
    matrix = matrix.copy()
    np.fill_diagonal(matrix, 0)
    total_change = matrix.sum()
    rows = []
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            count = int(matrix[i, j])
            if count:
                area_km2 = count * abs(pixel_area_km2)
                percent = (count / total_change * 100.0) if total_change else 0.0
                rows.append([i, j, count, area_km2, percent])
    rows.sort(key=lambda r: r[3], reverse=True)
    return rows
