# -*- coding: utf-8 -*-

"""
***************************************************************************
    RandomSelection.py
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
import random

from qgis.PyQt.QtGui import QIcon
from qgis.core import (QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingUtils,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingOutputVectorLayer)

from processing_gsoc_grass.algs.qgis.QgisAlgorithm import QgisAlgorithm

pluginPath = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]


class RandomSelection(QgisAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    METHOD = 'METHOD'
    NUMBER = 'NUMBER'

    def icon(self):
        return QIcon(os.path.join(pluginPath, 'images', 'ftools', 'random_selection.png'))

    def group(self):
        return self.tr('Vector selection')

    def groupId(self):
        return 'vectorselection'

    def flags(self):
        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.methods = [self.tr('Number of selected features'),
                        self.tr('Percentage of selected features')]

        self.addParameter(QgsProcessingParameterVectorLayer(self.INPUT,
                                                            self.tr('Input layer')))
        self.addParameter(QgsProcessingParameterEnum(self.METHOD,
                                                     self.tr('Method'), self.methods, False, 0))
        self.addParameter(QgsProcessingParameterNumber(self.NUMBER,
                                                       self.tr('Number/percentage of selected features'), QgsProcessingParameterNumber.Integer,
                                                       10, False, 0.0, 999999999999.0))
        self.addOutput(QgsProcessingOutputVectorLayer(self.OUTPUT, self.tr('Selected (random)')))

    def name(self):
        return 'randomselection'

    def displayName(self):
        return self.tr('Random selection')

    def processAlgorithm(self, parameters, context, feedback):
        layer = self.parameterAsVectorLayer(parameters, self.INPUT, context)
        method = self.parameterAsEnum(parameters, self.METHOD, context)

        featureCount = layer.featureCount()
        value = self.parameterAsInt(parameters, self.NUMBER, context)

        if method == 0:
            if value > featureCount:
                raise QgsProcessingException(
                    self.tr('Selected number is greater than feature count. '
                            'Choose a lower value and try again.'))
        else:
            if value > 100:
                raise QgsProcessingException(
                    self.tr("Percentage can't be greater than 100. Set a "
                            "different value and try again."))
            value = int(round(value / 100.0, 4) * featureCount)

        selran = random.sample(list(range(featureCount)), value)

        layer.selectByIds(selran)
        return {self.OUTPUT: parameters[self.INPUT]}
