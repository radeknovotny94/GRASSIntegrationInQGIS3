# -*- coding: utf-8 -*-

"""
***************************************************************************
    SpatialIndex.py
    ---------------------
    Date                 : January 2016
    Copyright            : (C) 2016 by Alexander Bruy
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
__date__ = 'January 2016'
__copyright__ = '(C) 2016, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import re

from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterCrs,
                       QgsProcessingOutputVectorLayer)

from processing.algs.qgis.QgisAlgorithm import QgisAlgorithm

pluginPath = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]


class DefineProjection(QgisAlgorithm):

    INPUT = 'INPUT'
    CRS = 'CRS'

    def group(self):
        return self.tr('Vector general')

    def groupId(self):
        return 'vectorgeneral'

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer(self.INPUT,
                                                            self.tr('Input Layer'), types=[QgsProcessing.TypeVectorAnyGeometry]))
        self.addParameter(QgsProcessingParameterCrs(self.CRS, 'Output CRS'))
        self.addOutput(QgsProcessingOutputVectorLayer(self.INPUT,
                                                      self.tr('Layer with projection')))

    def name(self):
        return 'definecurrentprojection'

    def displayName(self):
        return self.tr('Define current projection')

    def flags(self):
        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading

    def processAlgorithm(self, parameters, context, feedback):
        layer = self.parameterAsVectorLayer(parameters, self.INPUT, context)
        crs = self.parameterAsCrs(parameters, self.CRS, context)

        provider = layer.dataProvider()
        ds = provider.dataSourceUri()
        p = re.compile('\|.*')
        dsPath = p.sub('', ds)

        if dsPath.lower().endswith('.shp'):
            dsPath = dsPath[:-4]

        wkt = crs.toWkt()
        with open(dsPath + '.prj', 'w') as f:
            f.write(wkt)

        qpjFile = dsPath + '.qpj'
        if os.path.exists(qpjFile):
            with open(qpjFile, 'w') as f:
                f.write(wkt)

        layer.setCrs(crs)
        layer.triggerRepaint()

        return {self.INPUT: layer}
