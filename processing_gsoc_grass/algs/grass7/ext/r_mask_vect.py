# -*- coding: utf-8 -*-

"""
***************************************************************************
    r_mask_vect.py
    --------------
    Date                 : February 2016
    Copyright            : (C) 2016 by Médéric Ribreux
    Email                : medspx at medspx dot fr
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Médéric Ribreux'
__date__ = 'February 2016'
__copyright__ = '(C) 2016, Médéric Ribreux'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from processing.algs.grass7.Grass7Utils import Grass7Utils


def processCommand(alg, parameters, context, feedback):
    # Remove input
    alg.removeParameter('input')
    alg.processCommand(parameters, context, feedback, True)


def processOutputs(alg, parameters, context, feedback):
    createOpt = alg.parameterAsString(parameters, alg.GRASS_RASTER_FORMAT_OPT, context)
    metaOpt = alg.parameterAsString(parameters, alg.GRASS_RASTER_FORMAT_META, context)

    # We need to export the raster with all its bands and its color table
    fileName = alg.parameterAsOutputLayer(parameters, 'output', context)
    outFormat = Grass7Utils.getRasterFormatFromFilename(fileName)
    grassName = alg.exportedLayers['input']
    alg.exportRasterLayer(grassName, fileName, True,
                          outFormat, createOpt, metaOpt)
