# -*- coding: utf-8 -*-

"""
***************************************************************************
    ScriptAlgorithmProvider.py
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

from qgis.core import (QgsApplication,
                       QgsProcessingProvider)

from processing_gsoc_grass.core.ProcessingConfig import ProcessingConfig, Setting

from processing_gsoc_grass.gui.ProviderActions import (ProviderActions,
                                            ProviderContextMenuActions)

from processing_gsoc_grass.script.AddScriptFromFileAction import AddScriptFromFileAction
from processing_gsoc_grass.script.CreateNewScriptAction import CreateNewScriptAction
from processing_gsoc_grass.script.AddScriptFromTemplateAction import AddScriptFromTemplateAction
from processing_gsoc_grass.script.DeleteScriptAction import DeleteScriptAction
from processing_gsoc_grass.script.EditScriptAction import EditScriptAction
from processing_gsoc_grass.script import ScriptUtils


class ScriptAlgorithmProvider(QgsProcessingProvider):

    def __init__(self):
        super().__init__()
        self.algs = []
        self.folder_algorithms = []
        self.actions = [CreateNewScriptAction(),
                        AddScriptFromTemplateAction(),
                        AddScriptFromFileAction()
                        ]
        self.contextMenuActions = [EditScriptAction(),
                                   DeleteScriptAction()]

    def load(self):
        ProcessingConfig.settingIcons[self.name()] = self.icon()
        ProcessingConfig.addSetting(Setting(self.name(),
                                            ScriptUtils.SCRIPTS_FOLDERS,
                                            self.tr("Scripts folder(s)"),
                                            ScriptUtils.defaultScriptsFolder(),
                                            valuetype=Setting.MULTIPLE_FOLDERS))

        ProviderActions.registerProviderActions(self, self.actions)
        ProviderContextMenuActions.registerProviderContextMenuActions(self.contextMenuActions)

        ProcessingConfig.readSettings()
        self.refreshAlgorithms()

        return True

    def unload(self):
        ProcessingConfig.removeSetting(ScriptUtils.SCRIPTS_FOLDERS)

        ProviderActions.deregisterProviderActions(self)
        ProviderContextMenuActions.deregisterProviderContextMenuActions(self.contextMenuActions)

    def icon(self):
        return QgsApplication.getThemeIcon("/processingScript.svg")

    def svgIconPath(self):
        return QgsApplication.iconPath("processingScript.svg")

    def id(self):
        return "script"

    def name(self):
        return self.tr("Scripts")

    def supportsNonFileBasedOutput(self):
        # TODO - this may not be strictly true. We probably need a way for scripts
        # to indicate whether individual outputs support non-file based outputs,
        # but for now allow it. At best we expose nice features to users, at worst
        # they'll get an error if they use them with incompatible outputs...
        return True

    def loadAlgorithms(self):
        self.algs = []
        folders = ScriptUtils.scriptsFolders()
        for folder in folders:
            items = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
            for entry in items:
                if entry.lower().endswith(".py"):
                    moduleName = os.path.splitext(os.path.basename(entry))[0]
                    filePath = os.path.abspath(os.path.join(folder, entry))
                    alg = ScriptUtils.loadAlgorithm(moduleName, filePath)
                    if alg is not None:
                        self.algs.append(alg)

        for a in self.algs:
            self.addAlgorithm(a)
