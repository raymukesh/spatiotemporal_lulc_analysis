# -*- coding: utf-8 -*-
import csv
import os
import processing
from qgis.core import QgsProject, QgsRasterLayer


def _format_value(value):
    if isinstance(value, float):
        return '{:.3f}'.format(value)
    return value


def write_csv(path, headers, rows):
    with open(path, 'w', newline='', encoding='utf-8') as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        for row in rows:
            writer.writerow([_format_value(v) for v in row])


def add_raster_to_project(path):
    layer = QgsRasterLayer(path, path)
    if layer.isValid():
        QgsProject.instance().addMapLayer(layer)


def reproject_raster(path, source_crs, target_crs):
    if target_crs is None or not target_crs.isValid():
        return path
    if source_crs == target_crs:
        return path

    temp_path = os.path.splitext(path)[0] + '_reprojected.tif'
    params = {
        'INPUT': path,
        'SOURCE_CRS': source_crs,
        'TARGET_CRS': target_crs,
        'RESAMPLING': 0,
        'NODATA': None,
        'TARGET_RESOLUTION': None,
        'OPTIONS': '',
        'DATA_TYPE': 0,
        'TARGET_EXTENT': None,
        'TARGET_EXTENT_CRS': None,
        'MULTITHREADING': False,
        'EXTRA': '',
        'OUTPUT': temp_path,
    }
    processing.run('gdal:warpreproject', params)
    os.replace(temp_path, path)
    return path
