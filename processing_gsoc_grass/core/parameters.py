# -*- coding: utf-8 -*-

"""
***************************************************************************
    Parameters.py
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

import sys

from qgis.core import (QgsRasterLayer,
                       QgsVectorLayer,
                       QgsMapLayer,
                       QgsCoordinateReferenceSystem,
                       QgsExpression,
                       QgsProject,
                       QgsRectangle,
                       QgsVectorFileWriter,
                       QgsProcessing,
                       QgsProcessingUtils,
                       QgsProcessingParameters,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterCrs,
                       QgsProcessingParameterRange,
                       QgsProcessingParameterPoint,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterExtent,
                       QgsProcessingParameterMatrix,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterField,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterString,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterNumber)


def getParameterFromString(s):
    # Try the parameter definitions used in description files
    if '|' in s and (s.startswith("QgsProcessingParameter") or s.startswith("*QgsProcessingParameter") or s.startswith('Parameter') or s.startswith('*Parameter')):
        isAdvanced = False
        if s.startswith("*"):
            s = s[1:]
            isAdvanced = True
        tokens = s.split("|")
        params = [t if str(t) != str(None) else None for t in tokens[1:]]

        if True:
            clazz = getattr(sys.modules[__name__], tokens[0])
            # convert to correct type
            if clazz == QgsProcessingParameterRasterLayer:
                if len(params) > 3:
                    params[3] = True if params[3].lower() == 'true' else False
            elif clazz == QgsProcessingParameterVectorLayer:
                if len(params) > 2:
                    params[2] = [int(p) for p in params[2].split(';')]
                if len(params) > 4:
                    params[4] = True if params[4].lower() == 'true' else False
            elif clazz == QgsProcessingParameterBoolean:
                if len(params) > 2:
                    params[2] = True if params[2].lower() == 'true' else False
                if len(params) > 3:
                    params[3] = True if params[3].lower() == 'true' else False
            elif clazz == QgsProcessingParameterPoint:
                if len(params) > 3:
                    params[3] = True if params[3].lower() == 'true' else False
            elif clazz == QgsProcessingParameterCrs:
                if len(params) > 3:
                    params[3] = True if params[3].lower() == 'true' else False
            elif clazz == QgsProcessingParameterRange:
                if len(params) > 2:
                    try:
                        params[2] = int(params[2])
                    except:
                        params[2] = getattr(QgsProcessingParameterNumber, params[2].split(".")[1])
                if len(params) > 4:
                    params[4] = True if params[4].lower() == 'true' else False
            elif clazz == QgsProcessingParameterExtent:
                if len(params) > 3:
                    params[3] = True if params[3].lower() == 'true' else False
            elif clazz == QgsProcessingParameterEnum:
                if len(params) > 2:
                    params[2] = params[2].split(';')
                if len(params) > 3:
                    params[3] = True if params[3].lower() == 'true' else False
                if len(params) > 4:
                    # For multiple values; default value is a list of int
                    if params[3] == True:
                        params[4] = [int(v) for v in params[4].split(',')] if params[4] is not None else None
                    else:
                        params[4] = int(params[4]) if params[4] is not None else None
                if len(params) > 5:
                    params[5] = True if params[5].lower() == 'true' else False
            elif clazz == QgsProcessingParameterFeatureSource:
                if len(params) > 2:
                    try:
                        params[2] = [int(p) for p in params[2].split(';')]
                    except:
                        params[2] = [getattr(QgsProcessing, p.split(".")[1]) for p in params[2].split(';')]
                if len(params) > 4:
                    params[4] = True if params[4].lower() == 'true' else False
            elif clazz == QgsProcessingParameterMultipleLayers:
                if len(params) > 2:
                    try:
                        params[2] = int(params[2])
                    except:
                        params[2] = getattr(QgsProcessing, params[2].split(".")[1])
                if len(params) > 4:
                    params[4] = True if params[4].lower() == 'true' else False
            elif clazz == QgsProcessingParameterMatrix:
                if len(params) > 2:
                    params[2] = int(params[2])
                if len(params) > 3:
                    params[3] = True if params[3].lower() == 'true' else False
                if len(params) > 4:
                    params[4] = params[4].split(';')
                if len(params) > 6:
                    params[6] = True if params[6].lower() == 'true' else False
            elif clazz == QgsProcessingParameterField:
                if len(params) > 4:
                    try:
                        params[4] = int(params[4])
                    except:
                        params[4] = getattr(QgsProcessingParameterField, params[4].split(".")[1])
                if len(params) > 5:
                    params[5] = True if params[5].lower() == 'true' else False
                if len(params) > 6:
                    params[6] = True if params[6].lower() == 'true' else False
            elif clazz == QgsProcessingParameterFile:
                if len(params) > 2:
                    try:
                        params[2] = int(params[2])
                    except:
                        params[2] = getattr(QgsProcessingParameterFile, params[2].split(".")[1])
                if len(params) > 5:
                    params[5] = True if params[5].lower() == 'true' else False
            elif clazz == QgsProcessingParameterNumber:
                if len(params) > 2:
                    try:
                        params[2] = int(params[2])
                    except:
                        params[2] = getattr(QgsProcessingParameterNumber, params[2].split(".")[1])
                if len(params) > 3:
                    params[3] = float(params[3].strip()) if params[3] is not None else None
                if len(params) > 4:
                    params[4] = True if params[4].lower() == 'true' else False
                if len(params) > 5:
                    params[5] = float(params[5].strip()) if params[5] is not None else -sys.float_info.max + 1
                if len(params) > 6:
                    params[6] = float(params[6].strip()) if params[6] is not None else sys.float_info.max - 1
            elif clazz == QgsProcessingParameterString:
                if len(params) > 3:
                    params[3] = True if params[3].lower() == 'true' else False
                if len(params) > 4:
                    params[4] = True if params[4].lower() == 'true' else False
            elif clazz == QgsProcessingParameterFileDestination:
                if len(params) > 4:
                    params[4] = True if params[4].lower() == 'true' else False
            elif clazz == QgsProcessingParameterFolderDestination:
                if len(params) > 3:
                    params[3] = True if params[3].lower() == 'true' else False
            elif clazz == QgsProcessingParameterRasterDestination:
                if len(params) > 3:
                    params[3] = True if params[3].lower() == 'true' else False
            elif clazz == QgsProcessingParameterVectorDestination:
                if len(params) > 2:
                    try:
                        params[2] = int(params[2])
                    except:
                        params[2] = getattr(QgsProcessing, params[2].split(".")[1])
                if len(params) > 4:
                    params[4] = True if params[4].lower() == 'true' else False

            param = clazz(*params)
            if isAdvanced:
                param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)

            return param
        else:
            return None
    else:  # try script syntax

        # try native method
        param = QgsProcessingParameters.parameterFromScriptCode(s)
        if param:
            return param
