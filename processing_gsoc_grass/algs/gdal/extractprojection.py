# -*- coding: utf-8 -*-

"""
***************************************************************************
    extractprojection.py
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

from qgis.PyQt.QtGui import QIcon

from osgeo import gdal, osr

from processing.algs.gdal.GdalAlgorithm import GdalAlgorithm
from processing.core.parameters import ParameterRaster
from processing.core.parameters import ParameterBoolean

pluginPath = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]


class ExtractProjection(GdalAlgorithm):

    INPUT = 'INPUT'
    PRJ_FILE = 'PRJ_FILE'

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(ParameterRaster(self.INPUT, self.tr('Input file')))
        self.addParameter(ParameterBoolean(self.PRJ_FILE,
                                           self.tr('Create also .prj file'), False))

    def name(self):
        return 'extractprojection'

    def displayName(self):
        return self.tr('Extract projection')

    def icon(self):
        return QIcon(os.path.join(pluginPath, 'images', 'gdaltools', 'projection-export.png'))

    def group(self):
        return self.tr('Raster projections')

    def groupId(self):
        return 'rasterprojections'

    def getConsoleCommands(self, parameters, context, feedback, executing=True):
        return ["extractprojection"]

    def processAlgorithm(self, parameters, context, feedback):
        rasterPath = self.getParameterValue(self.INPUT)
        createPrj = self.getParameterValue(self.PRJ_FILE)

        raster = gdal.Open(str(rasterPath))
        crs = raster.GetProjection()
        geotransform = raster.GetGeoTransform()
        raster = None

        outFileName = os.path.splitext(str(rasterPath))[0]

        if crs != '' and createPrj:
            tmp = osr.SpatialReference()
            tmp.ImportFromWkt(crs)
            tmp.MorphToESRI()
            crs = tmp.ExportToWkt()
            tmp = None

            with open(outFileName + '.prj', 'wt') as prj:
                prj.write(crs)

        with open(outFileName + '.wld', 'wt') as wld:
            wld.write('%0.8f\n' % geotransform[1])
            wld.write('%0.8f\n' % geotransform[4])
            wld.write('%0.8f\n' % geotransform[2])
            wld.write('%0.8f\n' % geotransform[5])
            wld.write('%0.8f\n' % (geotransform[0] +
                                   0.5 * geotransform[1] +
                                   0.5 * geotransform[2]))
            wld.write('%0.8f\n' % (geotransform[3] +
                                   0.5 * geotransform[4] +
                                   0.5 * geotransform[5]))
