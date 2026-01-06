# -*- coding: utf-8 -*-
import numpy as np
from osgeo import gdal
from .raster_reader import iter_blocks, read_block


def _valid_mask(array, nodata):
    if nodata is None:
        return np.ones(array.shape, dtype=bool)
    return array != nodata


def write_change_frequency(layers, nodata_list, mask_layer, output_path, progress=None):
    base = layers[0]
    width = base.width()
    height = base.height()
    extent = base.extent()
    px_x = base.rasterUnitsPerPixelX()
    px_y = abs(base.rasterUnitsPerPixelY())

    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(output_path, width, height, 1, gdal.GDT_Int16)
    dataset.SetGeoTransform((extent.xMinimum(), px_x, 0.0, extent.yMaximum(), 0.0, -px_y))
    dataset.SetProjection(base.crs().toWkt())
    band = dataset.GetRasterBand(1)
    band.SetNoDataValue(-1)

    for col, row, array0 in iter_blocks(base, on_block=progress):
        rows = array0.shape[0]
        cols = array0.shape[1]
        valid_all = _valid_mask(array0, nodata_list[0])
        if mask_layer is not None:
            mask = read_block(mask_layer, col, row, cols, rows)
            valid_all &= mask == 1
        change_count = np.zeros_like(array0, dtype=np.int16)
        prev = array0

        for idx in range(1, len(layers)):
            curr = read_block(layers[idx], col, row, cols, rows)
            valid = _valid_mask(curr, nodata_list[idx])
            if mask_layer is not None:
                mask = read_block(mask_layer, col, row, cols, rows)
                valid &= mask == 1
            valid_all &= valid
            changed = (prev != curr) & valid_all
            change_count[changed] += 1
            prev = curr

        change_count[~valid_all] = -1
        band.WriteArray(change_count, xoff=col, yoff=row)

    band.FlushCache()
    dataset.FlushCache()
    dataset = None
