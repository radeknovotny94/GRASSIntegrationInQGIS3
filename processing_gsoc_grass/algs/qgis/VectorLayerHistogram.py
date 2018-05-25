# -*- coding: utf-8 -*-

"""
***************************************************************************
    VectorLayerHistogram.py
    ---------------------
    Date                 : January 2013
    Copyright            : (C) 2013 by Victor Olaya
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
__date__ = 'January 2013'
__copyright__ = '(C) 2013, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import plotly as plt
import plotly.graph_objs as go

from qgis.core import (QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterFileDestination)
from processing_gsoc_grass.algs.qgis.QgisAlgorithm import QgisAlgorithm
from processing_gsoc_grass.tools import vector


class VectorLayerHistogram(QgisAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    FIELD = 'FIELD'
    BINS = 'BINS'

    def group(self):
        return self.tr('Graphics')

    def groupId(self):
        return 'graphics'

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT,
                                                              self.tr('Input layer')))
        self.addParameter(QgsProcessingParameterField(self.FIELD,
                                                      self.tr('Attribute'), parentLayerParameterName=self.INPUT,
                                                      type=QgsProcessingParameterField.Numeric))
        self.addParameter(QgsProcessingParameterNumber(self.BINS,
                                                       self.tr('number of bins'), minValue=2, defaultValue=10))

        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT, self.tr('Histogram'), self.tr('HTML files (*.html)')))

    def name(self):
        return 'vectorlayerhistogram'

    def displayName(self):
        return self.tr('Vector layer histogram')

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        fieldname = self.parameterAsString(parameters, self.FIELD, context)
        bins = self.parameterAsInt(parameters, self.BINS, context)

        output = self.parameterAsFileOutput(parameters, self.OUTPUT, context)

        values = vector.values(source, fieldname)

        data = [go.Histogram(x=values[fieldname],
                             nbinsx=bins)]
        plt.offline.plot(data, filename=output, auto_open=False)

        return {self.OUTPUT: output}
