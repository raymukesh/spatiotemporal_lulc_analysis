# -*- coding: utf-8 -*-
from qgis.core import QgsCoordinateReferenceSystem


class ValidationError(Exception):
    pass


def validate_rasters(layers):
    if len(layers) < 1:
        raise ValidationError('No raster layers provided.')

    base = layers[0]
    base_crs = base.crs()
    base_extent = base.extent()
    base_px_x = base.rasterUnitsPerPixelX()
    base_px_y = base.rasterUnitsPerPixelY()
    base_width = base.width()
    base_height = base.height()

    for layer in layers[1:]:
        if layer.crs() != base_crs:
            raise ValidationError('CRS mismatch: {}'.format(layer.name()))
        if abs(layer.rasterUnitsPerPixelX() - base_px_x) > 1e-9 or abs(layer.rasterUnitsPerPixelY() - base_px_y) > 1e-9:
            raise ValidationError('Pixel size mismatch: {}'.format(layer.name()))
        if layer.width() != base_width or layer.height() != base_height:
            raise ValidationError('Raster dimensions mismatch: {}'.format(layer.name()))
        if layer.extent() != base_extent:
            raise ValidationError('Extent mismatch: {}'.format(layer.name()))

    if not base_crs.isValid():
        raise ValidationError('Invalid CRS on base raster.')

    return True
