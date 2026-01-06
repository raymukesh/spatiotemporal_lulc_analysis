# -*- coding: utf-8 -*-
import numpy as np
from osgeo import gdal
from qgis.core import QgsFeature, QgsGeometry, QgsPointXY, QgsVectorLayer, QgsField
from qgis.PyQt.QtCore import QVariant
import processing

from .raster_reader import iter_blocks, read_block


def _valid_mask(array, nodata):
    if nodata is None:
        return np.ones(array.shape, dtype=bool)
    return array != nodata


def _write_blank_raster(layer, output_path):
    width = layer.width()
    height = layer.height()
    extent = layer.extent()
    px_x = layer.rasterUnitsPerPixelX()
    px_y = abs(layer.rasterUnitsPerPixelY())

    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(output_path, width, height, 1, gdal.GDT_Float32)
    dataset.SetGeoTransform((extent.xMinimum(), px_x, 0.0, extent.yMaximum(), 0.0, -px_y))
    dataset.SetProjection(layer.crs().toWkt())
    band = dataset.GetRasterBand(1)
    band.Fill(0)
    band.FlushCache()
    dataset.FlushCache()
    dataset = None


def build_hotspot_raster(layer0, layer1, nodata0, nodata1, mask_layer, output_path, max_points=50000, progress=None):
    authid = layer0.crs().authid()
    crs = authid if authid else layer0.crs().toWkt()
    vlayer = QgsVectorLayer('Point?crs={}'.format(crs), 'change_points', 'memory')
    provider = vlayer.dataProvider()
    provider.addAttributes([QgsField('weight', QVariant.Int)])
    vlayer.updateFields()

    width = layer0.width()
    height = layer0.height()
    extent = layer0.extent()
    px_x = layer0.rasterUnitsPerPixelX()
    px_y = abs(layer0.rasterUnitsPerPixelY())
    x_min = extent.xMinimum()
    y_max = extent.yMaximum()

    points_added = 0
    for col, row, array0 in iter_blocks(layer0, on_block=progress):
        array1 = read_block(layer1, col, row, array0.shape[1], array0.shape[0])
        valid = _valid_mask(array0, nodata0) & _valid_mask(array1, nodata1)
        if mask_layer is not None:
            mask = read_block(mask_layer, col, row, array0.shape[1], array0.shape[0])
            valid &= mask == 1
        changed = valid & (array0 != array1)
        if not changed.any():
            continue

        indices = np.argwhere(changed)
        if indices.shape[0] == 0:
            continue

        remaining = max_points - points_added
        if remaining <= 0:
            break

        if indices.shape[0] > remaining:
            choice = np.random.choice(indices.shape[0], remaining, replace=False)
            indices = indices[choice]

        feats = []
        for r, c in indices:
            x = x_min + (col + c + 0.5) * px_x
            y = y_max - (row + r + 0.5) * px_y
            feat = QgsFeature(vlayer.fields())
            feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))
            feat.setAttribute('weight', 1)
            feats.append(feat)
        provider.addFeatures(feats)
        points_added += len(feats)

    if points_added == 0:
        _write_blank_raster(layer0, output_path)
        return

    authid = layer0.crs().authid()
    extent_str = '{},{},{},{}'.format(extent.xMinimum(), extent.xMaximum(), extent.yMinimum(), extent.yMaximum())
    if authid:
        extent_str = '{} [{}]'.format(extent_str, authid)
    params = {
        'INPUT': vlayer,
        'RADIUS': 1000.0,
        'PIXEL_SIZE': px_x,
        'WEIGHT_FIELD': 'weight',
        'KERNEL': 0,
        'DECAY': 0,
        'EXTENT': extent_str,
        'OUTPUT': output_path,
    }
    processing.run('qgis:heatmapkerneldensityestimation', params)
