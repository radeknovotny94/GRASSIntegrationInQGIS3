# -*- coding: utf-8 -*-

"""
***************************************************************************
    __init__.py
    ---------------------
    Date                 : July 2013
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
__date__ = 'July 2013'
__copyright__ = '(C) 2013, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.core import QgsVectorFileWriter, QgsSettings, QgsProcessingUtils

from processing_gsoc_grass.core.GeoAlgorithm import GeoAlgorithm
from processing_gsoc_grass.core.parameters import ParameterVector
from processing_gsoc_grass.core.outputs import OutputVector
from processing_gsoc_grass.tools import dataobjects


class ExampleAlgorithm(GeoAlgorithm):

    """This is an example algorithm that takes a vector layer and
    creates a new one just with just those features of the input
    layer that are selected.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the GeoAlgorithm class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT_LAYER = 'OUTPUT_LAYER'
    INPUT_LAYER = 'INPUT_LAYER'

    def __init__(self):
        super().__init__()
        """Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector layer. It can have any kind of geometry
        # It is a mandatory (not optional) one, hence the False argument
        self.addParameter(ParameterVector(self.INPUT_LAYER,
                                          self.tr('Input layer'), [dataobjects.TYPE_VECTOR_ANY], False))

        # We add a vector layer as output
        self.addOutput(OutputVector(self.OUTPUT_LAYER,
                                    self.tr('Output layer with selected features')))

    def name(self):
        # Unique (non-user visible) name of algorithm
        return 'create_copy_of_layer'

    def displayName(self):
        # The name that the user will see in the toolbox
        return self.tr('Create copy of layer')

    def group(self):
        return self.tr('Algorithms for vector layers')

    def processAlgorithm(self, parameters, context, feedback):
        """Here is where the processing itself takes place.
        :param parameters:
        :param context:
        """

        # The first thing to do is retrieve the values of the parameters
        # entered by the user
        inputFilename = self.getParameterValue(self.INPUT_LAYER)
        output = self.getOutputValue(self.OUTPUT_LAYER)

        # Input layers vales are always a string with its location.
        # That string can be converted into a QGIS layer (a
        # QgsVectorLayer in this case) using the
        # QgsProcessingUtils.mapLayerFromString() method.
        vectorLayer = QgsProcessingUtils.mapLayerFromString(inputFilename, context)

        # And now we can process

        # First we create the output layer. The output value entered by
        # the user is a string containing a filename, so we can use it
        # directly
        settings = QgsSettings()
        systemEncoding = settings.value('/UI/encoding', 'System')
        writer = QgsVectorFileWriter(output,
                                     systemEncoding,
                                     vectorLayer.fields(),
                                     vectorLayer.wkbType(),
                                     vectorLayer.crs())

        # Now we take the features from input layer and add them to the
        # output. Method features() returns an iterator, considering the
        # selection that might exist in layer and the configuration that
        # indicates should algorithm use only selected features or all
        # of them
        features = QgsProcessingUtils.getFeatures(vectorLayer, context)
        for f in features:
            writer.addFeature(f)

        # There is nothing more to do here. We do not have to open the
        # layer that we have created. The framework will take care of
        # that, or will handle it if this algorithm is executed within
        # a complex model
