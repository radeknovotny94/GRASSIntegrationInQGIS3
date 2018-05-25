# -*- coding: utf-8 -*-

"""
***************************************************************************
    ProcessingConfig.py
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

from qgis.PyQt.QtCore import QCoreApplication, QObject, pyqtSignal
from qgis.core import (NULL,
                       QgsApplication,
                       QgsSettings,
                       QgsVectorFileWriter,
                       QgsRasterFileWriter)
from processing_gsoc_grass.tools.system import defaultOutputFolder
import processing_gsoc_grass.tools.dataobjects


class SettingsWatcher(QObject):
    settingsChanged = pyqtSignal()


settingsWatcher = SettingsWatcher()


class ProcessingConfig:

    OUTPUT_FOLDER = 'OUTPUTS_FOLDER'
    RASTER_STYLE = 'RASTER_STYLE'
    VECTOR_POINT_STYLE = 'VECTOR_POINT_STYLE'
    VECTOR_LINE_STYLE = 'VECTOR_LINE_STYLE'
    VECTOR_POLYGON_STYLE = 'VECTOR_POLYGON_STYLE'
    SHOW_RECENT_ALGORITHMS = 'SHOW_RECENT_ALGORITHMS'
    FILTER_INVALID_GEOMETRIES = 'FILTER_INVALID_GEOMETRIES'
    USE_FILENAME_AS_LAYER_NAME = 'USE_FILENAME_AS_LAYER_NAME'
    KEEP_DIALOG_OPEN = 'KEEP_DIALOG_OPEN'
    SHOW_DEBUG_IN_DIALOG = 'SHOW_DEBUG_IN_DIALOG'
    RECENT_ALGORITHMS = 'RECENT_ALGORITHMS'
    PRE_EXECUTION_SCRIPT = 'PRE_EXECUTION_SCRIPT'
    POST_EXECUTION_SCRIPT = 'POST_EXECUTION_SCRIPT'
    SHOW_CRS_DEF = 'SHOW_CRS_DEF'
    WARN_UNMATCHING_CRS = 'WARN_UNMATCHING_CRS'
    DEFAULT_OUTPUT_RASTER_LAYER_EXT = 'DEFAULT_OUTPUT_RASTER_LAYER_EXT'
    DEFAULT_OUTPUT_VECTOR_LAYER_EXT = 'DEFAULT_OUTPUT_VECTOR_LAYER_EXT'
    SHOW_PROVIDERS_TOOLTIP = 'SHOW_PROVIDERS_TOOLTIP'
    MODELS_SCRIPTS_REPO = 'MODELS_SCRIPTS_REPO'

    settings = {}
    settingIcons = {}

    @staticmethod
    def initialize():
        icon = QgsApplication.getThemeIcon("/processingAlgorithm.svg")
        ProcessingConfig.settingIcons['General'] = icon
        ProcessingConfig.addSetting(Setting(
            ProcessingConfig.tr('General'),
            ProcessingConfig.SHOW_DEBUG_IN_DIALOG,
            ProcessingConfig.tr('Show extra info in Log panel'), True))
        ProcessingConfig.addSetting(Setting(
            ProcessingConfig.tr('General'),
            ProcessingConfig.KEEP_DIALOG_OPEN,
            ProcessingConfig.tr('Keep dialog open after running an algorithm'), True))
        ProcessingConfig.addSetting(Setting(
            ProcessingConfig.tr('General'),
            ProcessingConfig.USE_FILENAME_AS_LAYER_NAME,
            ProcessingConfig.tr('Use filename as layer name'), False))
        ProcessingConfig.addSetting(Setting(
            ProcessingConfig.tr('General'),
            ProcessingConfig.SHOW_RECENT_ALGORITHMS,
            ProcessingConfig.tr('Show recently executed algorithms'), True))
        ProcessingConfig.addSetting(Setting(
            ProcessingConfig.tr('General'),
            ProcessingConfig.SHOW_PROVIDERS_TOOLTIP,
            ProcessingConfig.tr('Show tooltip when there are disabled providers'), True))
        ProcessingConfig.addSetting(Setting(
            ProcessingConfig.tr('General'),
            ProcessingConfig.OUTPUT_FOLDER,
            ProcessingConfig.tr('Output folder'), defaultOutputFolder(),
            valuetype=Setting.FOLDER))
        ProcessingConfig.addSetting(Setting(
            ProcessingConfig.tr('General'),
            ProcessingConfig.SHOW_CRS_DEF,
            ProcessingConfig.tr('Show layer CRS definition in selection boxes'), True))
        ProcessingConfig.addSetting(Setting(
            ProcessingConfig.tr('General'),
            ProcessingConfig.WARN_UNMATCHING_CRS,
            ProcessingConfig.tr("Warn before executing if parameter CRS's do not match"), True))
        ProcessingConfig.addSetting(Setting(
            ProcessingConfig.tr('General'),
            ProcessingConfig.RASTER_STYLE,
            ProcessingConfig.tr('Style for raster layers'), '',
            valuetype=Setting.FILE))
        ProcessingConfig.addSetting(Setting(
            ProcessingConfig.tr('General'),
            ProcessingConfig.VECTOR_POINT_STYLE,
            ProcessingConfig.tr('Style for point layers'), '',
            valuetype=Setting.FILE))
        ProcessingConfig.addSetting(Setting(
            ProcessingConfig.tr('General'),
            ProcessingConfig.VECTOR_LINE_STYLE,
            ProcessingConfig.tr('Style for line layers'), '',
            valuetype=Setting.FILE))
        ProcessingConfig.addSetting(Setting(
            ProcessingConfig.tr('General'),
            ProcessingConfig.VECTOR_POLYGON_STYLE,
            ProcessingConfig.tr('Style for polygon layers'), '',
            valuetype=Setting.FILE))
        ProcessingConfig.addSetting(Setting(
            ProcessingConfig.tr('General'),
            ProcessingConfig.PRE_EXECUTION_SCRIPT,
            ProcessingConfig.tr('Pre-execution script'), '',
            valuetype=Setting.FILE))
        ProcessingConfig.addSetting(Setting(
            ProcessingConfig.tr('General'),
            ProcessingConfig.POST_EXECUTION_SCRIPT,
            ProcessingConfig.tr('Post-execution script'), '',
            valuetype=Setting.FILE))
        ProcessingConfig.addSetting(Setting(
            ProcessingConfig.tr('General'),
            ProcessingConfig.RECENT_ALGORITHMS,
            ProcessingConfig.tr('Recent algorithms'), '', hidden=True))
        ProcessingConfig.addSetting(Setting(
            ProcessingConfig.tr('General'),
            ProcessingConfig.MODELS_SCRIPTS_REPO,
            ProcessingConfig.tr('Scripts and models repository'),
            'https://raw.githubusercontent.com/qgis/QGIS-Processing/master'))

        invalidFeaturesOptions = [ProcessingConfig.tr('Do not filter (better performance)'),
                                  ProcessingConfig.tr('Ignore features with invalid geometries'),
                                  ProcessingConfig.tr('Stop algorithm execution when a geometry is invalid')]
        ProcessingConfig.addSetting(Setting(
            ProcessingConfig.tr('General'),
            ProcessingConfig.FILTER_INVALID_GEOMETRIES,
            ProcessingConfig.tr('Invalid features filtering'),
            invalidFeaturesOptions[2],
            valuetype=Setting.SELECTION,
            options=invalidFeaturesOptions))

        extensions = QgsVectorFileWriter.supportedFormatExtensions()
        ProcessingConfig.addSetting(Setting(
            ProcessingConfig.tr('General'),
            ProcessingConfig.DEFAULT_OUTPUT_VECTOR_LAYER_EXT,
            ProcessingConfig.tr('Default output vector layer extension'),
            extensions[0],
            valuetype=Setting.SELECTION,
            options=extensions))

        extensions = QgsRasterFileWriter.supportedFormatExtensions()
        ProcessingConfig.addSetting(Setting(
            ProcessingConfig.tr('General'),
            ProcessingConfig.DEFAULT_OUTPUT_RASTER_LAYER_EXT,
            ProcessingConfig.tr('Default output raster layer extension'),
            extensions[0],
            valuetype=Setting.SELECTION,
            options=extensions))

    @staticmethod
    def setGroupIcon(group, icon):
        ProcessingConfig.settingIcons[group] = icon

    @staticmethod
    def getGroupIcon(group):
        if group == ProcessingConfig.tr('General'):
            return QgsApplication.getThemeIcon("/processingAlgorithm.svg")
        if group in ProcessingConfig.settingIcons:
            return ProcessingConfig.settingIcons[group]
        else:
            return QgsApplication.getThemeIcon("/processingAlgorithm.svg")

    @staticmethod
    def addSetting(setting):
        ProcessingConfig.settings[setting.name] = setting

    @staticmethod
    def removeSetting(name):
        del ProcessingConfig.settings[name]

    @staticmethod
    def getSettings():
        '''Return settings as a dict with group names as keys and lists of settings as values'''
        settings = {}
        for setting in list(ProcessingConfig.settings.values()):
            if setting.group not in settings:
                group = []
                settings[setting.group] = group
            else:
                group = settings[setting.group]
            group.append(setting)
        return settings

    @staticmethod
    def readSettings():
        for setting in list(ProcessingConfig.settings.values()):
            setting.read()

    @staticmethod
    def getSetting(name, readable=False):
        if name in list(ProcessingConfig.settings.keys()):
            v = ProcessingConfig.settings[name].value
            try:
                if v == NULL:
                    v = None
            except:
                pass
            if ProcessingConfig.settings[name].valuetype == Setting.SELECTION:
                if readable:
                    return v
                return ProcessingConfig.settings[name].options.index(v)
            else:
                return v
        else:
            return None

    @staticmethod
    def setSettingValue(name, value):
        if name in list(ProcessingConfig.settings.keys()):
            if ProcessingConfig.settings[name].valuetype == Setting.SELECTION:
                ProcessingConfig.settings[name].setValue(ProcessingConfig.settings[name].options[value])
            else:
                ProcessingConfig.settings[name].setValue(value)
            ProcessingConfig.settings[name].save()

    @staticmethod
    def tr(string, context=''):
        if context == '':
            context = 'ProcessingConfig'
        return QCoreApplication.translate(context, string)


class Setting:

    """A simple config parameter that will appear on the config dialog.
    """
    STRING = 0
    FILE = 1
    FOLDER = 2
    SELECTION = 3
    FLOAT = 4
    INT = 5
    MULTIPLE_FOLDERS = 6

    def __init__(self, group, name, description, default, hidden=False, valuetype=None,
                 validator=None, options=None):
        self.group = group
        self.name = name
        self.qname = "Processing/Configuration/" + self.name
        self.description = description
        self.default = default
        self.hidden = hidden
        self.valuetype = valuetype
        self.options = options

        if self.valuetype is None:
            if isinstance(default, int):
                self.valuetype = self.INT
            elif isinstance(default, float):
                self.valuetype = self.FLOAT

        if validator is None:
            if self.valuetype == self.FLOAT:
                def checkFloat(v):
                    try:
                        float(v)
                    except ValueError:
                        raise ValueError(self.tr('Wrong parameter value:\n{0}').format(v))
                validator = checkFloat
            elif self.valuetype == self.INT:
                def checkInt(v):
                    try:
                        int(v)
                    except ValueError:
                        raise ValueError(self.tr('Wrong parameter value:\n{0}').format(v))
                validator = checkInt
            elif self.valuetype in [self.FILE, self.FOLDER]:
                def checkFileOrFolder(v):
                    if v and not os.path.exists(v):
                        raise ValueError(self.tr('Specified path does not exist:\n{0}').format(v))
                validator = checkFileOrFolder
            elif self.valuetype == self.MULTIPLE_FOLDERS:
                def checkMultipleFolders(v):
                    folders = v.split(';')
                    for f in folders:
                        if f and not os.path.exists(f):
                            raise ValueError(self.tr('Specified path does not exist:\n{0}').format(f))
                validator = checkMultipleFolders
            else:
                def validator(x):
                    return True
        self.validator = validator
        self.value = default

    def setValue(self, value):
        self.validator(value)
        self.value = value

    def read(self, qsettings=QgsSettings()):
        value = qsettings.value(self.qname, None)
        if value is not None:
            if isinstance(self.value, bool):
                value = str(value).lower() == str(True).lower()

            if self.valuetype == self.SELECTION:
                try:
                    self.value = self.options[int(value)]
                except:
                    self.value = self.options[0]
            else:
                self.value = value

    def save(self, qsettings=QgsSettings()):
        if self.valuetype == self.SELECTION:
            qsettings.setValue(self.qname, self.options.index(self.value))
        else:
            qsettings.setValue(self.qname, self.value)

    def __str__(self):
        return self.name + '=' + str(self.value)

    def tr(self, string, context=''):
        if context == '':
            context = 'ProcessingConfig'
        return QCoreApplication.translate(context, string)
