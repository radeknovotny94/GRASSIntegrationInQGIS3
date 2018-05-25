# -*- coding: utf-8 -*-

"""
***************************************************************************
    ExtentSelectionPanel.py
    ---------------------
    Date                 : August 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QMenu, QAction, QInputDialog
from qgis.PyQt.QtGui import QCursor

from qgis.gui import QgsMessageBar
from qgis.utils import iface
from qgis.core import (QgsProcessingUtils,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameters,
                       QgsProject,
                       QgsCoordinateReferenceSystem,
                       QgsRectangle,
                       QgsReferencedRectangle)
from processing_gsoc_grass.gui.RectangleMapTool import RectangleMapTool
from processing_gsoc_grass.core.ProcessingConfig import ProcessingConfig
from processing_gsoc_grass.tools.dataobjects import createContext

pluginPath = os.path.split(os.path.dirname(__file__))[0]
WIDGET, BASE = uic.loadUiType(
    os.path.join(pluginPath, 'ui', 'widgetBaseSelector.ui'))


class ExtentSelectionPanel(BASE, WIDGET):

    def __init__(self, dialog, param):
        super(ExtentSelectionPanel, self).__init__(None)
        self.setupUi(self)

        self.dialog = dialog
        self.param = param
        self.crs = QgsProject.instance().crs()

        if self.param.flags() & QgsProcessingParameterDefinition.FlagOptional:
            if hasattr(self.leText, 'setPlaceholderText'):
                self.leText.setPlaceholderText(
                    self.tr('[Leave blank to use min covering extent]'))

        self.btnSelect.clicked.connect(self.selectExtent)

        if iface is not None:
            canvas = iface.mapCanvas()
            self.prevMapTool = canvas.mapTool()
            self.tool = RectangleMapTool(canvas)
            self.tool.rectangleCreated.connect(self.updateExtent)
        else:
            self.prevMapTool = None
            self.tool = None

        if param.defaultValue() is not None:
            context = createContext()
            rect = QgsProcessingParameters.parameterAsExtent(param, {param.name(): param.defaultValue()}, context)
            crs = QgsProcessingParameters.parameterAsExtentCrs(param, {param.name(): param.defaultValue()}, context)
            if not rect.isNull():
                try:
                    s = '{},{},{},{}'.format(
                        rect.xMinimum(), rect.xMaximum(), rect.yMinimum(), rect.yMaximum())
                    if crs.isValid():
                        s += ' [' + crs.authid() + ']'
                        self.crs = crs
                    self.leText.setText(s)
                except:
                    pass

    def selectExtent(self):
        popupmenu = QMenu()
        useLayerExtentAction = QAction(
            self.tr('Use layer/canvas extent'), self.btnSelect)
        selectOnCanvasAction = QAction(
            self.tr('Select extent on canvas'), self.btnSelect)

        popupmenu.addAction(useLayerExtentAction)
        popupmenu.addAction(selectOnCanvasAction)

        selectOnCanvasAction.triggered.connect(self.selectOnCanvas)
        useLayerExtentAction.triggered.connect(self.useLayerExtent)

        if self.param.flags() & QgsProcessingParameterDefinition.FlagOptional:
            useMincoveringExtentAction = QAction(
                self.tr('Use min covering extent from input layers'),
                self.btnSelect)
            useMincoveringExtentAction.triggered.connect(
                self.useMinCoveringExtent)
            popupmenu.addAction(useMincoveringExtentAction)

        popupmenu.exec_(QCursor.pos())

    def useMinCoveringExtent(self):
        self.leText.setText('')

    def useLayerExtent(self):
        CANVAS_KEY = 'Use canvas extent'
        extentsDict = {}
        extentsDict[CANVAS_KEY] = {"extent": iface.mapCanvas().extent(),
                                   "authid": iface.mapCanvas().mapSettings().destinationCrs().authid()}
        extents = [CANVAS_KEY]
        layers = QgsProcessingUtils.compatibleLayers(QgsProject.instance())
        for layer in layers:
            authid = layer.crs().authid()
            if ProcessingConfig.getSetting(ProcessingConfig.SHOW_CRS_DEF) \
                    and authid is not None:
                layerName = u'{} [{}]'.format(layer.name(), authid)
            else:
                layerName = layer.name()
            extents.append(layerName)
            extentsDict[layerName] = {"extent": layer.extent(), "authid": authid}
        (item, ok) = QInputDialog.getItem(self, self.tr('Select Extent'),
                                          self.tr('Use extent from'), extents, False)
        if ok:
            self.setValueFromRect(QgsReferencedRectangle(extentsDict[item]["extent"], QgsCoordinateReferenceSystem(extentsDict[item]["authid"])))

    def selectOnCanvas(self):
        canvas = iface.mapCanvas()
        canvas.setMapTool(self.tool)
        self.dialog.showMinimized()

    def updateExtent(self):
        r = self.tool.rectangle()
        self.setValueFromRect(r)

    def setValueFromRect(self, r):
        s = '{},{},{},{}'.format(
            r.xMinimum(), r.xMaximum(), r.yMinimum(), r.yMaximum())

        try:
            self.crs = r.crs()
        except:
            self.crs = QgsProject.instance().crs()
        if self.crs.isValid():
            s += ' [' + self.crs.authid() + ']'

        self.leText.setText(s)
        self.tool.reset()
        canvas = iface.mapCanvas()
        canvas.setMapTool(self.prevMapTool)
        self.dialog.showNormal()
        self.dialog.raise_()
        self.dialog.activateWindow()

    def getValue(self):
        if str(self.leText.text()).strip() != '':
            return str(self.leText.text())
        else:
            return None

    def setExtentFromString(self, s):
        self.leText.setText(s)
