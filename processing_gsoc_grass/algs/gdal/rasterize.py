# -*- coding: utf-8 -*-

"""
***************************************************************************
    rasterize.py
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

from qgis.core import (QgsRasterFileWriter,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterExtent,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterRasterDestination)
from processing.algs.gdal.GdalAlgorithm import GdalAlgorithm
from processing.algs.gdal.GdalUtils import GdalUtils

pluginPath = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]


class rasterize(GdalAlgorithm):

    INPUT = 'INPUT'
    FIELD = 'FIELD'
    BURN = 'BURN'
    WIDTH = 'WIDTH'
    HEIGHT = 'HEIGHT'
    UNITS = 'UNITS'
    NODATA = 'NODATA'
    EXTENT = 'EXTENT'
    INIT = 'INIT'
    INVERT = 'INVERT'
    ALL_TOUCH = 'ALL_TOUCH'
    OPTIONS = 'OPTIONS'
    DATA_TYPE = 'DATA_TYPE'
    OUTPUT = 'OUTPUT'

    TYPES = ['Byte', 'Int16', 'UInt16', 'UInt32', 'Int32', 'Float32', 'Float64', 'CInt16', 'CInt32', 'CFloat32', 'CFloat64']

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.units = [self.tr("Pixels"),
                      self.tr("Georeferenced units")]

        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT,
                                                              self.tr('Input layer')))
        self.addParameter(QgsProcessingParameterField(self.FIELD,
                                                      self.tr('Field to use for a burn-in value'),
                                                      None,
                                                      self.INPUT,
                                                      QgsProcessingParameterField.Numeric,
                                                      optional=True))
        self.addParameter(QgsProcessingParameterNumber(self.BURN,
                                                       self.tr('A fixed value to burn'),
                                                       type=QgsProcessingParameterNumber.Double,
                                                       defaultValue=0.0,
                                                       optional=True))
        self.addParameter(QgsProcessingParameterEnum(self.UNITS,
                                                     self.tr('Output raster size units'),
                                                     self.units))
        self.addParameter(QgsProcessingParameterNumber(self.WIDTH,
                                                       self.tr('Width/Horizontal resolution'),
                                                       type=QgsProcessingParameterNumber.Double,
                                                       minValue=0.0,
                                                       defaultValue=0.0))
        self.addParameter(QgsProcessingParameterNumber(self.HEIGHT,
                                                       self.tr('Height/Vertical resolution'),
                                                       type=QgsProcessingParameterNumber.Double,
                                                       minValue=0.0,
                                                       defaultValue=0.0))
        self.addParameter(QgsProcessingParameterExtent(self.EXTENT,
                                                       self.tr('Output extent')))
        self.addParameter(QgsProcessingParameterNumber(self.NODATA,
                                                       self.tr('Assign a specified nodata value to output bands'),
                                                       type=QgsProcessingParameterNumber.Double,
                                                       defaultValue=0.0,
                                                       optional=True))

        options_param = QgsProcessingParameterString(self.OPTIONS,
                                                     self.tr('Additional creation parameters'),
                                                     defaultValue='',
                                                     optional=True)
        options_param.setFlags(options_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        options_param.setMetadata({
            'widget_wrapper': {
                'class': 'processing.algs.gdal.ui.RasterOptionsWidget.RasterOptionsWidgetWrapper'}})
        self.addParameter(options_param)

        dataType_param = QgsProcessingParameterEnum(self.DATA_TYPE,
                                                    self.tr('Output data type'),
                                                    self.TYPES,
                                                    allowMultiple=False,
                                                    defaultValue=5)
        dataType_param.setFlags(dataType_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(dataType_param)

        init_param = QgsProcessingParameterNumber(self.INIT,
                                                  self.tr('Pre-initialize the output image with value'),
                                                  type=QgsProcessingParameterNumber.Double,
                                                  defaultValue=0.0,
                                                  optional=True)
        init_param.setFlags(init_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(init_param)

        invert_param = QgsProcessingParameterBoolean(self.INVERT,
                                                     self.tr('Invert rasterization'),
                                                     defaultValue=False)
        invert_param.setFlags(invert_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(invert_param)

        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT,
                                                                  self.tr('Rasterized')))

    def name(self):
        return 'rasterize'

    def displayName(self):
        return self.tr('Rasterize (vector to raster)')

    def group(self):
        return self.tr('Vector conversion')

    def groupId(self):
        return 'vectorconversion'

    def icon(self):
        return QIcon(os.path.join(pluginPath, 'images', 'gdaltools', 'rasterize.png'))

    def commandName(self):
        return 'gdal_rasterize'

    def getConsoleCommands(self, parameters, context, feedback, executing=True):
        ogrLayer, layerName = self.getOgrCompatibleSource(self.INPUT, parameters, context, feedback, executing)

        arguments = ['-l']
        arguments.append(layerName)

        fieldName = self.parameterAsString(parameters, self.FIELD, context)
        if fieldName:
            arguments.append('-a')
            arguments.append(fieldName)
        else:
            arguments.append('-burn')
            arguments.append(self.parameterAsDouble(parameters, self.BURN, context))

        units = self.parameterAsEnum(parameters, self.UNITS, context)
        if units == 0:
            arguments.append('-ts')
        else:
            arguments.append('-tr')
        arguments.append(self.parameterAsDouble(parameters, self.WIDTH, context))
        arguments.append(self.parameterAsDouble(parameters, self.HEIGHT, context))

        initValue = self.parameterAsDouble(parameters, self.INIT, context)
        if initValue:
            arguments.append('-init')
            arguments.append(initValue)

        if self.parameterAsBool(parameters, self.INVERT, context):
            arguments.append('-i')

        if self.parameterAsBool(parameters, self.ALL_TOUCH, context):
            arguments.append('-at')

        if self.NODATA in parameters and parameters[self.NODATA] is not None:
            nodata = self.parameterAsDouble(parameters, self.NODATA, context)
            arguments.append('-a_nodata')
            arguments.append(nodata)

        extent = self.parameterAsExtent(parameters, self.EXTENT, context)
        if not extent.isNull():
            arguments.append('-te')
            arguments.append(extent.xMinimum())
            arguments.append(extent.yMinimum())
            arguments.append(extent.xMaximum())
            arguments.append(extent.yMaximum())

        arguments.append('-ot')
        arguments.append(self.TYPES[self.parameterAsEnum(parameters, self.DATA_TYPE, context)])

        out = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        arguments.append('-of')
        arguments.append(QgsRasterFileWriter.driverForExtension(os.path.splitext(out)[1]))
        options = self.parameterAsString(parameters, self.OPTIONS, context)

        if options:
            arguments.extend(GdalUtils.parseCreationOptions(options))

        arguments.append(ogrLayer)
        arguments.append(out)

        return ['gdal_rasterize', GdalUtils.escapeAndJoin(arguments)]
