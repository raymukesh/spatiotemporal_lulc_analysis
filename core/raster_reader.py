# -*- coding: utf-8 -*-
import numpy as np
from qgis.core import QgsRectangle, Qgis


def get_nodata_value(layer):
    provider = layer.dataProvider()
    try:
        if provider.sourceHasNoDataValue(1):
            return provider.sourceNoDataValue(1)
    except Exception:
        pass
    return None


def iter_blocks(layer, block_cols=256, block_rows=256, on_block=None):
    provider = layer.dataProvider()
    extent = layer.extent()
    width = layer.width()
    height = layer.height()
    px_x = layer.rasterUnitsPerPixelX()
    px_y = abs(layer.rasterUnitsPerPixelY())
    x_min = extent.xMinimum()
    y_max = extent.yMaximum()

    for row in range(0, height, block_rows):
        for col in range(0, width, block_cols):
            cols = min(block_cols, width - col)
            rows = min(block_rows, height - row)
            x0 = x_min + col * px_x
            x1 = x_min + (col + cols) * px_x
            y1 = y_max - row * px_y
            y0 = y_max - (row + rows) * px_y
            rect = QgsRectangle(x0, y0, x1, y1)
            block = provider.block(1, rect, cols, rows)
            array = _block_to_array(block)
            if on_block:
                on_block()
            yield col, row, array


def read_block(layer, col, row, cols, rows):
    provider = layer.dataProvider()
    extent = layer.extent()
    px_x = layer.rasterUnitsPerPixelX()
    px_y = abs(layer.rasterUnitsPerPixelY())
    x_min = extent.xMinimum()
    y_max = extent.yMaximum()
    x0 = x_min + col * px_x
    x1 = x_min + (col + cols) * px_x
    y1 = y_max - row * px_y
    y0 = y_max - (row + rows) * px_y
    rect = QgsRectangle(x0, y0, x1, y1)
    block = provider.block(1, rect, cols, rows)
    return _block_to_array(block)


def _block_to_array(block):
    if hasattr(block, 'readArray'):
        return block.readArray()
    data = None
    if hasattr(block, 'read'):
        data = block.read()
    elif hasattr(block, 'data'):
        data = block.data()
    if data is None:
        raise AttributeError('QgsRasterBlock has no readable buffer')
    if not isinstance(data, (bytes, bytearray)):
        try:
            data = bytes(data)
        except Exception:
            data = bytearray(data)
    width = block.width()
    height = block.height()
    dtype = _qgis_dtype_to_numpy(block.dataType())
    array = np.frombuffer(data, dtype=dtype)
    return array.reshape((height, width))


def _qgis_dtype_to_numpy(qgis_type):
    if qgis_type == Qgis.Byte:
        return np.uint8
    if qgis_type == Qgis.UInt16:
        return np.uint16
    if qgis_type == Qgis.Int16:
        return np.int16
    if qgis_type == Qgis.UInt32:
        return np.uint32
    if qgis_type == Qgis.Int32:
        return np.int32
    if qgis_type == Qgis.Float32:
        return np.float32
    if qgis_type == Qgis.Float64:
        return np.float64
    return np.float32
