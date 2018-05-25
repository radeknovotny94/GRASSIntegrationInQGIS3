# -*- coding: utf-8 -*-

"""
***************************************************************************
    general.py
    ---------------------
    Date                 : April 2013
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
__date__ = 'April 2013'
__copyright__ = '(C) 2013, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import configparser

from qgis.core import (QgsApplication,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingOutputLayerDefinition,
                       QgsProject)
from processing.core.Processing import Processing
from processing.gui.Postprocessing import handleAlgorithmResults
from processing.gui.AlgorithmDialog import AlgorithmDialog
from qgis.utils import iface


def algorithmHelp(id):
    """Prints algorithm parameters with their types. Also
    provides information about options if any.
    """
    alg = QgsApplication.processingRegistry().algorithmById(id)
    if alg is not None:
        print('{} ({})\n'.format(alg.displayName(), alg.id()))
        print(alg.shortHelpString())
        print('\n----------------')
        print('Input parameters')
        print('----------------')
        for p in alg.parameterDefinitions():
            print('\n{}:  <{}>'.format(p.name(), p.__class__.__name__))
            if p.description():
                print('\t' + p.description())

            if isinstance(p, QgsProcessingParameterEnum):
                opts = []
                for i, o in enumerate(p.options()):
                    opts.append('\t\t{} - {}'.format(i, o))
                print('\n'.join(opts))

        print('\n----------------')
        print('Outputs')
        print('----------------')

        for o in alg.outputDefinitions():
            print('\n{}:  <{}>'.format(o.name(), o.__class__.__name__))
            if o.description():
                print('\t' + o.description())

    else:
        print('Algorithm "{}" not found.'.format(id))


def run(algOrName, parameters, onFinish=None, feedback=None, context=None):
    """Executes given algorithm and returns its outputs as dictionary
    object.
    """
    return Processing.runAlgorithm(algOrName, parameters, onFinish, feedback, context)


def runAndLoadResults(algOrName, parameters, feedback=None, context=None):
    """Executes given algorithm and load its results into QGIS project
    when possible.
    """
    if isinstance(algOrName, QgsProcessingAlgorithm):
        alg = algOrName
    else:
        alg = QgsApplication.processingRegistry().createAlgorithmById(algOrName)

    # output destination parameters to point to current project
    for param in alg.parameterDefinitions():
        if not param.name() in parameters:
            continue

        if isinstance(param, (QgsProcessingParameterFeatureSink, QgsProcessingParameterVectorDestination, QgsProcessingParameterRasterDestination)):
            p = parameters[param.name()]
            if not isinstance(p, QgsProcessingOutputLayerDefinition):
                parameters[param.name()] = QgsProcessingOutputLayerDefinition(p, QgsProject.instance())
            else:
                p.destinationProject = QgsProject.instance()
                parameters[param.name()] = p

    return Processing.runAlgorithm(alg, parameters=parameters, onFinish=handleAlgorithmResults, feedback=feedback, context=context)


def createAlgorithmDialog(algOrName, parameters={}):
    """Creates and returns an algorithm dialog for the specified algorithm, prepopulated
    with a given set of parameters. It is the caller's responsibility to execute
    and delete this dialog.
    """
    if isinstance(algOrName, QgsProcessingAlgorithm):
        alg = algOrName
    else:
        alg = QgsApplication.processingRegistry().createAlgorithmById(algOrName)

    if alg is None:
        return False

    dlg = alg.createCustomParametersWidget(iface.mainWindow())

    if not dlg:
        dlg = AlgorithmDialog(alg)

    dlg.setParameters(parameters)

    return dlg


def execAlgorithmDialog(algOrName, parameters={}):
    """Executes an algorithm dialog for the specified algorithm, prepopulated
    with a given set of parameters.

    Returns the algorithm's results.
    """
    dlg = createAlgorithmDialog(algOrName, parameters)
    if dlg is None:
        return {}

    canvas = iface.mapCanvas()
    prevMapTool = canvas.mapTool()
    dlg.show()
    dlg.exec_()
    if canvas.mapTool() != prevMapTool:
        try:
            canvas.mapTool().reset()
        except:
            pass
        canvas.setMapTool(prevMapTool)

    results = dlg.results()
    # make sure the dialog is destroyed and not only hidden on pressing Esc
    dlg.close()
    return results
