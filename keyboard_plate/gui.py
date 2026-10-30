# Copyright (c) 2026 eco-ergo.com
# SPDX-License-Identifier: MIT
"""Layout import, preview and transactional parameter editing."""
import traceback
import FreeCAD as App
import FreeCADGui as Gui
try:
    from PySide6 import QtWidgets, QtCore, QtGui
except ImportError:
    try:
        from PySide2 import QtWidgets, QtCore, QtGui
    except ImportError:
        from PySide import QtGui as QtWidgets
        from PySide import QtCore, QtGui
from . import __author__, __version__
from .feature import KeyboardPlateProxy, create_plate
from .parameters import LENGTH_PARAMETERS, UNDERSIDE_CLIP_RELIEF, OUTLINE_SHAPES
from .kle import parse_kle
from .preview import layout_preview

_dialog = None


class PlateDialog(QtWidgets.QDialog):
    def __init__(self):
        super(PlateDialog, self).__init__(Gui.getMainWindow())
        self.setWindowTitle('Keyboard Plate Generator %s — %s' % (__version__, __author__))
        self.target = None
        for obj in Gui.Selection.getSelection():
            if 'KLEData' in obj.PropertiesList and 'ClipReliefSpan' in obj.PropertiesList:
                self.target = obj
                break
        self.data = self.target.KLEData if self.target else ''
        form = QtWidgets.QFormLayout(self)
        introduction = QtWidgets.QLabel(
            'Optimized for 3D-printed switch plates for handwired keyboards. '
            'Without a PCB, the plate provides the structural support to hold '
            'the switches securely. The tested 3 mm plate and underside clip '
            'relief combine rigidity with a 1.5 mm retaining lip for '
            'standard full-height Cherry MX-style switches. PCB builds are also possible '
            'when switch positions, plate thickness and component clearances match.'
        )
        introduction.setWordWrap(True)
        introduction.setMaximumWidth(440)
        form.addRow(introduction)
        credits = QtWidgets.QLabel(
            'Layouts: <a href="https://www.keyboard-layout-editor.com/#/">'
            'Keyboard Layout Editor</a> by Ian Prest and contributors'
        )
        credits.setOpenExternalLinks(True)
        credits.setWordWrap(True)
        form.addRow(credits)
        limitations = QtWidgets.QLabel(
            'Mounting holes are not generated; add them manually in FreeCAD. '
            'Stabilizer cutouts are not yet supported; wide keys receive only a switch opening. '
            'Support may be added in a future release. '
            'Developed with AI assistance; see README for print testing and validation details.'
        )
        limitations.setWordWrap(True)
        limitations.setMaximumWidth(440)
        form.addRow(limitations)
        self.info = QtWidgets.QLabel(self.target.Label if self.target else 'Import a KLE JSON layout')
        form.addRow(self.info)
        load = QtWidgets.QPushButton('Import KLE JSON…')
        load.clicked.connect(self.load)
        form.addRow(load)
        self.preview_scene = QtWidgets.QGraphicsScene(self)
        self.preview_view = QtWidgets.QGraphicsView(self.preview_scene)
        self.preview_view.setMinimumSize(440, 220)
        form.addRow(self.preview_view)
        self.dimensions = QtWidgets.QLabel('Import a layout to preview switch positions and plate size.')
        self.dimensions.setWordWrap(True)
        form.addRow(self.dimensions)
        legend = QtWidgets.QLabel('Top view · blue: plate envelopes · dark: switch openings')
        form.addRow(legend)
        self.outline = QtWidgets.QComboBox()
        self.outline.addItems(list(OUTLINE_SHAPES))
        current_outline = str(getattr(self.target, 'OutlineShape', OUTLINE_SHAPES[0]))
        self.outline.setCurrentIndex(max(0, self.outline.findText(current_outline)))
        self.outline.setToolTip('Rectangle encloses the expanded layout in an X/Y-aligned boundary.')
        form.addRow('Outline shape', self.outline)
        self.fields = {}
        for name, label, group, default, description in LENGTH_PARAMETERS:
            field = QtWidgets.QDoubleSpinBox()
            field.setToolTip(description)
            field.setDecimals(3)
            field.setRange(0.0, 10000.0)
            field.setValue(float(getattr(self.target, name).Value) if self.target else default)
            self.fields[name] = field
            form.addRow(label, field)
        for name in ('OutlineMargin', 'SwitchOpening', 'PlateThickness'):
            self.fields[name].valueChanged.connect(self.update_preview)
        self.outline.currentIndexChanged.connect(self.update_preview)
        self.update_preview()
        self.relief = QtWidgets.QCheckBox('Enable underside clip relief')
        self.relief.setToolTip(
            'Creates underside pockets for switch clips. Disabling leaves straight-through '
            'openings at the selected plate thickness; verify clip engagement and PCB clearance.'
        )
        self.relief.setChecked(self.target.UndersideClipRelief if self.target else UNDERSIDE_CLIP_RELIEF)
        form.addRow(self.relief)
        self.generate_button = QtWidgets.QPushButton('Regenerate plate' if self.target else 'Generate plate')
        self.generate_button.clicked.connect(self.generate)
        form.addRow(self.generate_button)

    def update_preview(self, *args):
        self.preview_scene.clear()
        if not self.data:
            return
        try:
            keys = parse_kle(self.data)
            envelopes, holes, bounds = layout_preview(
                keys, self.fields['OutlineMargin'].value(),
                self.fields['SwitchOpening'].value(), self.outline.currentText())
            # Filled polygons overlap to show the same envelope union as generation.
            for polygons, color in ((envelopes, '#a9c7dc'), (holes, '#23313e')):
                for points in polygons:
                    polygon = QtGui.QPolygonF([QtCore.QPointF(x, y) for x, y in points])
                    pen = QtGui.QPen(QtGui.QColor(color))
                    pen.setWidthF(0)
                    self.preview_scene.addPolygon(polygon, pen, QtGui.QBrush(QtGui.QColor(color)))
            left, top, right, bottom = bounds
            self.preview_scene.setSceneRect(left - 3, top - 3, right - left + 6, bottom - top + 6)
            self.preview_view.fitInView(self.preview_scene.sceneRect(), QtCore.Qt.KeepAspectRatio)
            self.dimensions.setText(
                '%d switches · Plate: %.2f × %.2f × %.2f mm (X × Y × thickness)'
                % (len(keys), right - left, bottom - top, self.fields['PlateThickness'].value()))
        except Exception as exc:
            self.dimensions.setText('Preview unavailable: %s' % exc)

    def resizeEvent(self, event):
        super(PlateDialog, self).resizeEvent(event)
        if hasattr(self, 'preview_scene'):
            self.preview_view.fitInView(self.preview_scene.sceneRect(), QtCore.Qt.KeepAspectRatio)

    def load(self):
        selection = QtWidgets.QFileDialog.getOpenFileName(self, 'Select KLE JSON', '', 'KLE data (*.json *.txt);;All files (*)')
        path = selection[0] if isinstance(selection, tuple) else selection
        if not path:
            return
        try:
            with open(path, encoding='utf-8-sig') as stream:
                data = stream.read()
            keys = parse_kle(data)
            self.data = data
            self.info.setText('%d keys: %s' % (len(keys), path))
            self.update_preview()
        except Exception as exc:
            QtWidgets.QMessageBox.critical(self, 'Layout import failed', str(exc))

    def generate(self):
        doc = None
        transaction = False
        try:
            parse_kle(self.data)
            doc = self.target.Document if self.target else (App.ActiveDocument or App.newDocument('KeyboardPlate'))
            doc.openTransaction('Generate keyboard plate')
            transaction = True
            obj = self.target or create_plate(doc, self.data)
            # Attach the proxy first to migrate older features inside the transaction.
            KeyboardPlateProxy(obj)
            obj.OutlineShape = self.outline.currentText()
            obj.KLEData = self.data
            for name, field in self.fields.items():
                setattr(obj, name, field.value())
            obj.UndersideClipRelief = self.relief.isChecked()
            obj.touch()
            doc.recompute()
            if not obj.GenerationStatus.startswith('OK'):
                raise ValueError(obj.GenerationStatus)
            doc.commitTransaction()
            transaction = False
            self.target = obj
            self.generate_button.setText('Regenerate plate')
            obj.ViewObject.Visibility = True
            obj.ViewObject.ShapeColor = (0.68, 0.78, 0.86)
            Gui.activeDocument().activeView().viewAxonometric()
            Gui.activeDocument().activeView().fitAll()
            self.info.setText(obj.GenerationStatus)
        except Exception as exc:
            if transaction:
                doc.abortTransaction()
            App.Console.PrintError(traceback.format_exc() + '\n')
            QtWidgets.QMessageBox.critical(self, 'Plate generation failed', str(exc))


def run():
    global _dialog
    if _dialog is not None:
        _dialog.close()
    _dialog = PlateDialog()
    _dialog.show()
