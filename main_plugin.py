# -*- coding: utf-8 -*-
import os
import re
from collections import namedtuple

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor, QBrush, QIcon
from qgis.PyQt.QtWidgets import QAction, QDockWidget, QFileDialog, QDialog, QListWidget, QPushButton, QVBoxLayout, QMessageBox
from qgis.core import QgsProject, QgsRasterLayer, QgsMapLayerType, QgsMapLayerProxyModel, Qgis
from qgis.gui import QgsMapLayerComboBox, QgsProjectionSelectionWidget
import processing

from .core.validator import validate_rasters, ValidationError
from .core.raster_reader import get_nodata_value
from .core.change_metrics import (
    compute_max_class,
    compute_area_by_class,
    compute_interval_metrics,
    build_top_transitions,
)
from .core.persistence import write_change_frequency
from .core.intensity import compute_intensity_rows
from .core.hotspot import build_hotspot_raster
from .core.exports import write_csv, add_raster_to_project, reproject_raster

RasterItem = namedtuple('RasterItem', ['layer', 'path', 'year', 'nodata'])


class LayerPickerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Select Raster Layers')
        self.list_widget = QListWidget(self)
        self.list_widget.setSelectionMode(QListWidget.MultiSelection)
        self.ok_button = QPushButton('OK', self)
        self.ok_button.clicked.connect(self.accept)
        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)

    def set_layers(self, layers):
        self.list_widget.clear()
        for layer in layers:
            self.list_widget.addItem(layer.name())

    def selected_indexes(self):
        return [item.row() for item in self.list_widget.selectedIndexes()]


class LandChangeAccountingPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.dock = None
        self.action = None
        self.rasters = []

    def initGui(self):
        self.action = QAction('Spatiotemporal LULC Analysis', self.iface.mainWindow())
        icon_path = os.path.join(self.plugin_dir, 'icons', 'icon.png')
        if os.path.exists(icon_path):
            self.action.setIcon(QIcon(icon_path))
        self.action.triggered.connect(self.show_dock)
        self.iface.addPluginToMenu('Spatiotemporal LULC Analysis', self.action)

    def unload(self):
        if self.dock is not None:
            self.iface.removeDockWidget(self.dock)
        if self.action is not None:
            self.iface.removePluginMenu('Spatiotemporal LULC Analysis', self.action)

    def show_dock(self):
        if self.dock is None:
            self.dock = QDockWidget('Spatiotemporal LULC Analysis', self.iface.mainWindow())
            ui_path = os.path.join(self.plugin_dir, 'ui', 'dock.ui')
            self.widget = uic.loadUi(ui_path)
            self.dock.setWidget(self.widget)
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock)
            self._setup_ui()
            self.dock.setFloating(True)
            self.dock.resize(900, 700)
            self._center_dock()
        self.dock.show()
        self.dock.raise_()

    def _center_dock(self):
        main_geom = self.iface.mainWindow().geometry()
        dock_geom = self.dock.frameGeometry()
        center = main_geom.center()
        dock_geom.moveCenter(center)
        self.dock.move(dock_geom.topLeft())

    def _show_about(self):
        text = (
            'Land Change Accounting (MVP)\n'
            'Version: 0.1.0\n'
            'Author: Mukesh Ray\n\n'
            'Purpose\n'
            '  Core land use/land cover change accounting for categorical rasters.\n'
            '  Focus: what changed, where, and how much.\n\n'
            'Outputs\n'
            '  CSV tables and GeoTIFF rasters written to disk and added to the map.\n\n'
            'Limitations\n'
            '  No reprojection or resampling of inputs in MVP.\n'
            '  Inputs must be aligned and share CRS, extent, resolution, and grid.\n'
        )
        QMessageBox.information(self.widget, 'About Land Change Accounting', text)

    def _show_help(self):
        text = (
            'Quick Start\n'
            '  1) Add categorical rasters (same CRS/extent/resolution/alignment).\n'
            '  2) Verify or edit years in the table.\n'
            '  3) Optional: select an AOI polygon mask.\n'
            '  4) Set NoData (use raster value or override).\n'
            '  5) Choose outputs and output folder.\n'
            '  6) Click Run Analysis.\n\n'
            'Inputs\n'
            '  - Rasters must be integer class IDs.\n'
            '  - All rasters must match CRS, pixel size, extent, and grid alignment.\n'
            '  - NoData must be defined or provided.\n\n'
            'Class Legend\n'
            '  - Add Class ID and Label rows to include labels in CSV outputs.\n'
            '  - If a class ID has no label, the label column is left blank.\n\n'
            'Outputs (CSV)\n'
            '  Area by Class: per year counts, area (km2), percent share.\n'
            '  Net/Gross Change: gain, loss, net, gross per class per interval.\n'
            '  Transition Matrix: from-to pixel counts per interval.\n'
            '  Top Transitions: ranked conversions with percent of total change.\n'
            '  Change Intensity: interval and annualized change ratios.\n\n'
            'Outputs (Raster)\n'
            '  Change Frequency: counts how many times each pixel changed across all years.\n'
            '  Hotspots: kernel density heatmap of changed pixels per interval.\n\n'
            'Output CRS\n'
            '  - Raster outputs can be reprojected to a selected CRS.\n'
            '  - CSV outputs are unaffected by CRS choice.\n\n'
            'Validation Panel\n'
            '  - Use Validate Inputs to review CRS, pixel size, extent, alignment,\n'
            '    data type, NoData status, value ranges, and unique class counts.\n\n'
            'Performance\n'
            '  - Processing is block-based; large rasters are supported.\n'
            '  - Hotspot sampling limits points for performance.\n\n'
            'Troubleshooting\n'
            '  - If validation fails, fix input alignment before running.\n'
            '  - Ensure NoData is set correctly to avoid false changes.\n'
        )
        QMessageBox.information(self.widget, 'Help - Land Change Accounting', text)

    def _setup_ui(self):
        self.widget.nodataMode.addItems(['Use raster NoData', 'Use value'])
        self.widget.nodataValue.setEnabled(False)
        self.widget.nodataMode.currentIndexChanged.connect(self._nodata_mode_changed)
        self.widget.browseOutput.clicked.connect(self._browse_output)
        self.widget.addFilesButton.clicked.connect(self._add_files)
        self.widget.addProjectButton.clicked.connect(self._add_from_project)
        self.widget.removeSelectedButton.clicked.connect(self._remove_selected)
        self.widget.addLegendRowButton.clicked.connect(self._add_legend_row)
        self.widget.removeLegendRowButton.clicked.connect(self._remove_legend_rows)
        self.widget.validateButton.clicked.connect(self._run_validation)
        self.widget.aboutButton.clicked.connect(self._show_about)
        self.widget.helpButton.clicked.connect(self._show_help)
        self.widget.runButton.clicked.connect(self._run_analysis)
        self.widget.progressBar.setValue(0)
        self.widget.logText.setReadOnly(True)

        aoi_combo = QgsMapLayerComboBox(self.widget)
        aoi_combo.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.widget.aoiLayout.replaceWidget(self.widget.aoiCombo, aoi_combo)
        self.widget.aoiCombo.deleteLater()
        self.widget.aoiCombo = aoi_combo

        crs_widget = QgsProjectionSelectionWidget(self.widget)
        self.widget.crsLayout.replaceWidget(self.widget.crsWidget, crs_widget)
        self.widget.crsWidget.deleteLater()
        self.widget.crsWidget = crs_widget
        self.widget.crsWidget.setCrs(QgsProject.instance().crs())

        for checkbox in (
            self.widget.areaByClassCheck,
            self.widget.netGrossCheck,
            self.widget.transitionCheck,
            self.widget.topTransitionsCheck,
            self.widget.changeFreqCheck,
            self.widget.intensityCheck,
            self.widget.hotspotCheck,
        ):
            checkbox.setChecked(True)
        self.widget.includeNodataClassCheck.setChecked(False)

        header = self.widget.rasterTable.horizontalHeader()
        header.setSectionResizeMode(0, header.Interactive)
        header.setSectionResizeMode(1, header.Interactive)
        self.widget.rasterTable.setColumnWidth(0, 300)
        self.widget.rasterTable.setColumnWidth(1, 120)

        legend_header = self.widget.legendTable.horizontalHeader()
        legend_header.setSectionResizeMode(0, legend_header.ResizeToContents)
        legend_header.setSectionResizeMode(1, legend_header.Stretch)

        validation_header = self.widget.validationTable.horizontalHeader()
        validation_header.setSectionResizeMode(0, validation_header.ResizeToContents)
        validation_header.setSectionResizeMode(1, validation_header.ResizeToContents)
        validation_header.setSectionResizeMode(2, validation_header.Stretch)

    def _log(self, message):
        self.widget.logText.appendPlainText(message)

    def _nodata_mode_changed(self, idx):
        self.widget.nodataValue.setEnabled(idx == 1)

    def _browse_output(self):
        path = QFileDialog.getExistingDirectory(self.widget, 'Select Output Directory')
        if path:
            self.widget.outputDir.setText(path)

    def _add_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self.widget, 'Select rasters', '', 'Raster (*.tif *.tiff *.img)')
        for path in paths:
            layer = QgsRasterLayer(path, os.path.basename(path))
            if not layer.isValid():
                self._log('Invalid raster: {}'.format(path))
                continue
            year = self._infer_year(path)
            nodata = get_nodata_value(layer)
            self.rasters.append(RasterItem(layer, path, year, nodata))
        self._refresh_table()

    def _add_from_project(self):
        layers = [layer for layer in QgsProject.instance().mapLayers().values() if layer.type() == QgsMapLayerType.RasterLayer]
        if not layers:
            self._log('No raster layers in project.')
            return
        dialog = LayerPickerDialog(self.widget)
        dialog.set_layers(layers)
        if dialog.exec_() != QDialog.Accepted:
            return
        for idx in dialog.selected_indexes():
            layer = layers[idx]
            nodata = get_nodata_value(layer)
            self.rasters.append(RasterItem(layer, layer.source(), self._infer_year(layer.name()), nodata))
        self._refresh_table()

    def _remove_selected(self):
        selected = sorted({idx.row() for idx in self.widget.rasterTable.selectedIndexes()}, reverse=True)
        for row in selected:
            if 0 <= row < len(self.rasters):
                self.rasters.pop(row)
        self._refresh_table()

    def _refresh_table(self):
        self.widget.rasterTable.setRowCount(len(self.rasters))
        for row, item in enumerate(self.rasters):
            label = item.layer.name() or os.path.basename(item.path)
            self.widget.rasterTable.setItem(row, 0, self._make_item(label))
            self.widget.rasterTable.setItem(row, 1, self._make_item(item.year or ''))

    def _make_item(self, text):
        from qgis.PyQt.QtWidgets import QTableWidgetItem
        item = QTableWidgetItem(str(text))
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        return item

    def _add_legend_row(self):
        row = self.widget.legendTable.rowCount()
        self.widget.legendTable.insertRow(row)

    def _remove_legend_rows(self):
        selected = sorted({idx.row() for idx in self.widget.legendTable.selectedIndexes()}, reverse=True)
        for row in selected:
            self.widget.legendTable.removeRow(row)

    def _read_legend_map(self):
        legend = {}
        for row in range(self.widget.legendTable.rowCount()):
            id_item = self.widget.legendTable.item(row, 0)
            label_item = self.widget.legendTable.item(row, 1)
            if not id_item or not id_item.text().strip():
                continue
            try:
                class_id = int(id_item.text().strip())
            except ValueError:
                raise ValueError('Invalid class ID in legend at row {}'.format(row + 1))
            label = label_item.text().strip() if label_item else ''
            legend[class_id] = label
        return legend

    def _clear_validation(self):
        self.widget.validationTable.setRowCount(0)

    def _add_validation_row(self, check, status, details):
        from qgis.PyQt.QtWidgets import QTableWidgetItem
        row = self.widget.validationTable.rowCount()
        self.widget.validationTable.insertRow(row)
        self.widget.validationTable.setItem(row, 0, QTableWidgetItem(check))
        status_item = QTableWidgetItem(status)
        status_item.setForeground(QBrush(QColor('#ffffff')))
        status_item.setBackground(QBrush(QColor(self._status_color(status))))
        self.widget.validationTable.setItem(row, 1, status_item)
        self.widget.validationTable.setItem(row, 2, QTableWidgetItem(details))

    def _status_color(self, status):
        if status == 'PASS':
            return '#2e7d32'
        if status == 'WARN':
            return '#f9a825'
        if status == 'FAIL':
            return '#c62828'
        return '#546e7a'

    def _datatype_name(self, dtype):
        mapping = {
            Qgis.Byte: 'Byte',
            Qgis.UInt16: 'UInt16',
            Qgis.Int16: 'Int16',
            Qgis.UInt32: 'UInt32',
            Qgis.Int32: 'Int32',
            Qgis.Float32: 'Float32',
            Qgis.Float64: 'Float64',
        }
        return mapping.get(dtype, str(int(dtype)))

    def _is_integer_datatype(self, dtype):
        return dtype in (Qgis.Byte, Qgis.UInt16, Qgis.Int16, Qgis.UInt32, Qgis.Int32)

    def _compute_min_max_unique(self, layer, nodata, max_unique=1024, progress=None):
        from .core.raster_reader import iter_blocks
        import numpy as np
        min_val = None
        max_val = None
        unique_vals = set()
        capped = False
        for _, _, array in iter_blocks(layer, on_block=progress):
            if nodata is None:
                valid = np.ones(array.shape, dtype=bool)
            else:
                valid = array != nodata
            if not valid.any():
                continue
            values = array[valid]
            local_min = float(np.min(values))
            local_max = float(np.max(values))
            min_val = local_min if min_val is None else min(min_val, local_min)
            max_val = local_max if max_val is None else max(max_val, local_max)
            if not capped:
                uniques = np.unique(values)
                for val in uniques:
                    unique_vals.add(int(val))
                    if len(unique_vals) >= max_unique:
                        capped = True
                        break
        return min_val, max_val, unique_vals, capped

    def _count_blocks(self, layer, block_size=256):
        import math
        cols = int(math.ceil(layer.width() / float(block_size)))
        rows = int(math.ceil(layer.height() / float(block_size)))
        return cols * rows

    def _init_progress(self, total_steps):
        self.widget.progressBar.setMinimum(0)
        self.widget.progressBar.setMaximum(max(1, total_steps))
        self.widget.progressBar.setValue(0)
        self.widget.progressBar.setTextVisible(True)
        self.widget.progressBar.setFormat('Processing blocks: %v / %m')

    def _progress_callback(self, total_steps):
        progress = {'value': 0}

        def advance():
            progress['value'] += 1
            self.widget.progressBar.setValue(min(progress['value'], total_steps))

        return advance

    def _run_validation(self, output_dir=None, log_errors=True, progress=None):
        self._clear_validation()
        try:
            rasters = self._collect_inputs()
        except ValueError as exc:
            self._add_validation_row('Input selection', 'FAIL', str(exc))
            if log_errors:
                self._log('Error: {}'.format(exc))
            return

        nodata_mode = self.widget.nodataMode.currentIndex()
        nodata_override = None
        if nodata_mode == 1:
            text = self.widget.nodataValue.text().strip()
            if not text:
                self._add_validation_row('NoData value', 'FAIL', 'NoData override selected but value is empty.')
                return
            try:
                nodata_override = float(text)
            except ValueError:
                self._add_validation_row('NoData value', 'FAIL', 'NoData override is not numeric.')
                return

        raster_layers = [item.layer for item in rasters]
        base = raster_layers[0]
        base_crs = base.crs()
        base_extent = base.extent()
        base_px_x = base.rasterUnitsPerPixelX()
        base_px_y = base.rasterUnitsPerPixelY()
        base_width = base.width()
        base_height = base.height()

        mismatched = [layer.name() for layer in raster_layers if layer.crs() != base_crs]
        if mismatched:
            self._add_validation_row('CRS', 'FAIL', 'Mismatch: {}'.format(', '.join(mismatched)))
        else:
            self._add_validation_row('CRS', 'PASS', base_crs.authid())

        size_mismatch = []
        for layer in raster_layers:
            if abs(layer.rasterUnitsPerPixelX() - base_px_x) > 1e-9 or abs(layer.rasterUnitsPerPixelY() - base_px_y) > 1e-9:
                size_mismatch.append(layer.name())
        if size_mismatch:
            self._add_validation_row('Pixel size', 'FAIL', 'Mismatch: {}'.format(', '.join(size_mismatch)))
        else:
            self._add_validation_row('Pixel size', 'PASS', '{} x {}'.format(base_px_x, base_px_y))

        extent_mismatch = [layer.name() for layer in raster_layers if layer.extent() != base_extent]
        if extent_mismatch:
            self._add_validation_row('Extent', 'FAIL', 'Mismatch: {}'.format(', '.join(extent_mismatch)))
        else:
            self._add_validation_row('Extent', 'PASS', 'All match')

        dim_mismatch = []
        for layer in raster_layers:
            if layer.width() != base_width or layer.height() != base_height:
                dim_mismatch.append(layer.name())
        if dim_mismatch:
            self._add_validation_row('Dimensions', 'FAIL', 'Mismatch: {}'.format(', '.join(dim_mismatch)))
        else:
            self._add_validation_row('Dimensions', 'PASS', '{} x {}'.format(base_width, base_height))

        origin_mismatch = []
        for layer in raster_layers:
            if layer.extent().xMinimum() != base_extent.xMinimum() or layer.extent().yMaximum() != base_extent.yMaximum():
                origin_mismatch.append(layer.name())
        if origin_mismatch:
            self._add_validation_row('Grid alignment', 'FAIL', 'Mismatch: {}'.format(', '.join(origin_mismatch)))
        else:
            self._add_validation_row('Grid alignment', 'PASS', 'Origins match')

        datatype_info = []
        any_float = False
        for layer in raster_layers:
            dtype = layer.dataProvider().dataType(1)
            datatype_info.append('{}: {}'.format(layer.name(), self._datatype_name(dtype)))
            if not self._is_integer_datatype(dtype):
                any_float = True
        if any_float:
            self._add_validation_row('Data type', 'WARN', '; '.join(datatype_info))
        else:
            self._add_validation_row('Data type', 'PASS', '; '.join(datatype_info))

        nodata_values = []
        missing_nodata = []
        for item in rasters:
            value = nodata_override if nodata_override is not None else item.nodata
            nodata_values.append(value)
            if value is None:
                missing_nodata.append(item.layer.name())
        if nodata_override is not None:
            self._add_validation_row('NoData', 'INFO', 'Override: {}'.format(nodata_override))
        elif missing_nodata:
            self._add_validation_row('NoData', 'WARN', 'Missing for: {}'.format(', '.join(missing_nodata)))
        else:
            unique_nodata = {v for v in nodata_values}
            if len(unique_nodata) > 1:
                self._add_validation_row('NoData', 'WARN', 'Inconsistent values: {}'.format(', '.join(str(v) for v in unique_nodata)))
            else:
                self._add_validation_row('NoData', 'PASS', 'Value: {}'.format(next(iter(unique_nodata))))

        ranges = []
        uniques = []
        for layer, nodata in zip(raster_layers, nodata_values):
            min_val, max_val, unique_vals, capped = self._compute_min_max_unique(layer, nodata, progress=progress)
            ranges.append('{}: {}..{}'.format(layer.name(), min_val, max_val))
            count_text = '>= {}'.format(len(unique_vals)) if capped else str(len(unique_vals))
            uniques.append('{}: {}'.format(layer.name(), count_text))
        self._add_validation_row('Value range', 'INFO', '; '.join(ranges))
        self._add_validation_row('Unique classes', 'INFO', '; '.join(uniques))

        aoi_layer = self.widget.aoiCombo.currentLayer()
        if aoi_layer is None:
            self._add_validation_row('AOI coverage', 'INFO', 'No AOI selected')
        else:
            out_dir = output_dir or self.widget.outputDir.text().strip()
            if not out_dir:
                self._add_validation_row('AOI coverage', 'WARN', 'Output dir required to build mask')
            else:
                mask_layer = self._build_mask_raster(aoi_layer, base, out_dir)
                from .core.raster_reader import iter_blocks, read_block
                import numpy as np
                total_valid = 0
                covered = 0
                for col, row, array in iter_blocks(base, on_block=progress):
                    if nodata_values[0] is None:
                        valid = np.ones(array.shape, dtype=bool)
                    else:
                        valid = array != nodata_values[0]
                    mask = read_block(mask_layer, col, row, array.shape[1], array.shape[0])
                    total_valid += int(valid.sum())
                    covered += int((valid & (mask == 1)).sum())
                percent = (covered / total_valid * 100.0) if total_valid else 0.0
                self._add_validation_row('AOI coverage', 'INFO', '{:.2f}% of valid pixels'.format(percent))

    def _infer_year(self, text):
        match = re.search(r'(19|20)\d{2}', text)
        return match.group(0) if match else ''

    def _nodata_class(self, nodata0, nodata1):
        if self.widget.includeNodataClassCheck.isChecked():
            return None
        if nodata0 is None or nodata1 is None:
            return None
        if nodata0 != nodata1:
            return None
        value = nodata0
        if isinstance(value, float) and not value.is_integer():
            return None
        value = int(value)
        if value < 0:
            return None
        return value

    def _collect_inputs(self):
        if not self.rasters:
            raise ValueError('No rasters selected.')
        updated = []
        for row, item in enumerate(self.rasters):
            year_item = self.widget.rasterTable.item(row, 1)
            year = year_item.text().strip() if year_item else item.year
            if not year or not year.isdigit():
                raise ValueError('Invalid year for raster at row {}'.format(row + 1))
            updated.append(item._replace(year=int(year)))
        updated.sort(key=lambda r: r.year)
        return updated

    def _build_mask_raster(self, aoi_layer, reference_layer, output_dir):
        if aoi_layer is None:
            return None
        mask_path = os.path.join(output_dir, 'aoi_mask.tif')
        params = {
            'INPUT': aoi_layer,
            'FIELD': None,
            'BURN': 1,
            'UNITS': 1,
            'WIDTH': reference_layer.width(),
            'HEIGHT': reference_layer.height(),
            'EXTENT': reference_layer.extent(),
            'NODATA': 0,
            'OPTIONS': '',
            'DATA_TYPE': 1,
            'INIT': 0,
            'INVERT': False,
            'EXTRA': '',
            'OUTPUT': mask_path,
        }
        processing.run('gdal:rasterize', params)
        mask_layer = QgsRasterLayer(mask_path, 'AOI Mask')
        if not mask_layer.isValid():
            raise ValueError('Failed to create AOI mask raster.')
        return mask_layer

    def _run_analysis(self):
        self.widget.progressBar.setValue(0)
        self.widget.logText.clear()
        try:
            rasters = self._collect_inputs()
            output_dir = self.widget.outputDir.text().strip()
            if not output_dir:
                raise ValueError('Output directory is required.')

            nodata_mode = self.widget.nodataMode.currentIndex()
            nodata_override = None
            if nodata_mode == 1:
                text = self.widget.nodataValue.text().strip()
                if not text:
                    raise ValueError('NoData value is required.')
                nodata_override = float(text)

            aoi_layer = self.widget.aoiCombo.currentLayer()
            raster_layers = [item.layer for item in rasters]
            validate_rasters(raster_layers)
            base_blocks = self._count_blocks(raster_layers[0])

            nodata_list = []
            for item in rasters:
                nodata_list.append(nodata_override if nodata_override is not None else item.nodata)

            steps = [
                self.widget.areaByClassCheck.isChecked(),
                self.widget.netGrossCheck.isChecked(),
                self.widget.transitionCheck.isChecked(),
                self.widget.topTransitionsCheck.isChecked(),
                self.widget.changeFreqCheck.isChecked(),
                self.widget.intensityCheck.isChecked(),
                self.widget.hotspotCheck.isChecked(),
            ]
            intervals = max(0, len(rasters) - 1)
            passes = 0
            passes += len(rasters)  # compute_max_class
            if self.widget.areaByClassCheck.isChecked():
                passes += len(rasters)
            if any(steps[1:4]) or self.widget.intensityCheck.isChecked() or self.widget.hotspotCheck.isChecked():
                passes += intervals  # interval metrics
            if self.widget.changeFreqCheck.isChecked():
                passes += 1
            if self.widget.hotspotCheck.isChecked():
                passes += intervals
            passes += len(rasters)  # validation min/max/unique
            if self.widget.aoiCombo.currentLayer() is not None:
                passes += 1
            total_blocks = max(1, base_blocks * passes)
            self._init_progress(total_blocks)
            progress_cb = self._progress_callback(total_blocks)

            mask_layer = self._build_mask_raster(aoi_layer, rasters[0].layer, output_dir) if aoi_layer else None
            max_class = compute_max_class(raster_layers, nodata_list, mask_layer, progress=progress_cb)
            self._log('Max class id: {}'.format(max_class))
            target_crs = self.widget.crsWidget.crs() if self.widget.crsWidget else None
            if target_crs is None or not target_crs.isValid():
                target_crs = QgsProject.instance().crs()
            legend_map = self._read_legend_map()

            self._run_validation(output_dir=output_dir, log_errors=False, progress=progress_cb)

            if self.widget.areaByClassCheck.isChecked():
                rows = []
                for idx, item in enumerate(rasters):
                    area_counts = compute_area_by_class(item.layer, nodata_list[idx], mask_layer, progress=progress_cb)
                    total_pixels = sum(area_counts.values())
                    pixel_area_km2 = item.layer.rasterUnitsPerPixelX() * item.layer.rasterUnitsPerPixelY() / 1e6
                    for class_id, count in sorted(area_counts.items()):
                        area_km2 = count * abs(pixel_area_km2)
                        percent = (count / total_pixels * 100.0) if total_pixels else 0.0
                        rows.append([item.year, class_id, legend_map.get(class_id, ''), count, area_km2, percent])
                write_csv(os.path.join(output_dir, 'area_by_class.csv'),
                          ['year', 'class_id', 'class_label', 'pixel_count', 'area_km2', 'percent_share'],
                          rows)
                self._log('Wrote area_by_class.csv')

            interval_results = []
            for idx in range(len(rasters) - 1):
                r0 = rasters[idx]
                r1 = rasters[idx + 1]
                result = compute_interval_metrics(r0.layer, r1.layer, nodata_list[idx], nodata_list[idx + 1], mask_layer, max_class, progress=progress_cb)
                interval_results.append((r0, r1, nodata_list[idx], nodata_list[idx + 1], result))

            if self.widget.netGrossCheck.isChecked():
                for r0, r1, _, _, result in interval_results:
                    gain = result['gain']
                    loss = result['loss']
                    pixel_area_km2 = r0.layer.rasterUnitsPerPixelX() * r0.layer.rasterUnitsPerPixelY() / 1e6
                    rows = []
                    for class_id in range(max_class + 1):
                        gain_px = int(gain[class_id])
                        loss_px = int(loss[class_id])
                        net_px = gain_px - loss_px
                        gross_px = gain_px + loss_px
                        rows.append([
                            class_id,
                            legend_map.get(class_id, ''),
                            gain_px,
                            loss_px,
                            net_px,
                            gross_px,
                            net_px * abs(pixel_area_km2),
                            gross_px * abs(pixel_area_km2),
                        ])
                    fname = 'net_gross_change_{}_{}.csv'.format(r0.year, r1.year)
                    write_csv(os.path.join(output_dir, fname),
                              ['class_id', 'class_label', 'gain_pixels', 'loss_pixels', 'net_pixels', 'gross_pixels', 'area_km2_net', 'area_km2_gross'],
                              rows)
                    self._log('Wrote {}'.format(fname))

            if self.widget.transitionCheck.isChecked():
                for r0, r1, nodata0, nodata1, result in interval_results:
                    matrix = result['matrix']
                    fname = 'transition_matrix_{}_{}.csv'.format(r0.year, r1.year)
                    nodata_class = self._nodata_class(nodata0, nodata1)
                    classes = [i for i in range(max_class + 1) if i != nodata_class]
                    rows = []
                    for i in classes:
                        rows.append([i, legend_map.get(i, '')] + [int(matrix[i, j]) for j in classes])
                    header = ['from_class', 'from_label'] + [
                        '{} {}'.format(i, legend_map.get(i, '')).strip() for i in classes
                    ]
                    write_csv(os.path.join(output_dir, fname), header, rows)
                    self._log('Wrote {}'.format(fname))

            if self.widget.topTransitionsCheck.isChecked():
                for r0, r1, _, _, result in interval_results:
                    matrix = result['matrix']
                    rows = build_top_transitions(matrix, r0.layer)
                    fname = 'top_transitions_{}_{}.csv'.format(r0.year, r1.year)
                    labeled = []
                    for row in rows:
                        from_id, to_id, count, area_km2, percent = row
                        labeled.append([
                            from_id,
                            legend_map.get(from_id, ''),
                            to_id,
                            legend_map.get(to_id, ''),
                            count,
                            area_km2,
                            percent,
                        ])
                    write_csv(os.path.join(output_dir, fname),
                              ['from_class', 'from_label', 'to_class', 'to_label', 'pixel_count', 'area_km2', 'percent_of_total_change'],
                              labeled)
                    self._log('Wrote {}'.format(fname))

            if self.widget.changeFreqCheck.isChecked():
                change_path = os.path.join(output_dir, 'change_frequency.tif')
                write_change_frequency(raster_layers, nodata_list, mask_layer, change_path, progress=progress_cb)
                change_path = reproject_raster(change_path, rasters[0].layer.crs(), target_crs)
                add_raster_to_project(change_path)
                self._log('Wrote change_frequency.tif')

            if self.widget.intensityCheck.isChecked():
                rows = compute_intensity_rows(interval_results)
                write_csv(os.path.join(output_dir, 'change_intensity.csv'),
                          ['year0', 'year1', 'interval_years', 'changed_pixels', 'total_pixels', 'interval_intensity', 'annualized_intensity'],
                          rows)
                self._log('Wrote change_intensity.csv')

            if self.widget.hotspotCheck.isChecked():
                for r0, r1, nodata0, nodata1, _ in interval_results:
                    hotspot_path = os.path.join(output_dir, 'change_hotspot_{}_{}.tif'.format(r0.year, r1.year))
                    build_hotspot_raster(r0.layer, r1.layer, nodata0, nodata1, mask_layer, hotspot_path, progress=progress_cb)
                    hotspot_path = reproject_raster(hotspot_path, r0.layer.crs(), target_crs)
                    add_raster_to_project(hotspot_path)
                    self._log('Wrote {}'.format(os.path.basename(hotspot_path)))

            self._log('Done.')
            self.widget.progressBar.setValue(self.widget.progressBar.maximum())
        except (ValidationError, ValueError) as exc:
            self._log('Error: {}'.format(exc))
        except Exception as exc:
            self._log('Unexpected error: {}'.format(exc))
