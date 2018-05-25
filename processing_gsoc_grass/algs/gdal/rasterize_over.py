# -*- coding: utf-8 -*-

"""
***************************************************************************
    rasterize_over.py
    ---------------------
    Date                 : September 2013
    Copyright            : (C) 2013 by Alexander Bruy
    Email                : alexander dot bruy at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Alexander Bruy'
__date__ = 'September 2013'
__copyright__ = '(C) 2013, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.core import QgsProcessingUtils

from qgis.PyQt.QtGui import QIcon

from processing.algs.gdal.GdalAlgorithm import GdalAlgorithm
from processing.algs.gdal.GdalUtils import GdalUtils

from processing.tools import dataobjects

pluginPath = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]


class rasterize_over(GdalAlgorithm):

    INPUT = 'INPUT'
    INPUT_RASTER = 'INPUT_RASTER'
    FIELD = 'FIELD'

    def icon(self):
        return QIcon(os.path.join(pluginPath, 'images', 'gdaltools', 'rasterize.png'))

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(ParameterVector(self.INPUT, self.tr('Input layer')))
        self.addParameter(ParameterTableField(self.FIELD,
                                              self.tr('Attribute field'), self.INPUT))
        self.addParameter(ParameterRaster(self.INPUT_RASTER,
                                          self.tr('Existing raster layer'), False))

    def name(self):
        return 'rasterize_over'

    def displayName(self):
        return self.tr('Rasterize (write over existing raster)')

    def group(self):
        return self.tr('Vector conversion')

    def groupId(self):
        return 'vectorconversion'

    def getConsoleCommands(self, parameters, context, feedback, executing=True):
        context = dataobjects.createContext()
        inLayer = QgsProcessingUtils.mapLayerFromString(self.getParameterValue(self.INPUT), context)
        inRasterLayer = QgsProcessingUtils.mapLayerFromString(self.getParameterValue(self.INPUT_RASTER), context)

        ogrLayer = GdalUtils.ogrConnectionString(inLayer, context)[1:-1]
        ogrRasterLayer = GdalUtils.ogrConnectionString(inRasterLayer, context)[1:-1]

        arguments = []
        arguments.append('-a')
        arguments.append(str(self.getParameterValue(self.FIELD)))

        arguments.append('-l')
        arguments.append(GdalUtils.ogrLayerName(inLayer))
        arguments.append(ogrLayer)
        arguments.append(ogrRasterLayer)

        return ['gdal_rasterize', GdalUtils.escapeAndJoin(arguments)]

    def commandName(self):
        return "gdal_rasterize"
