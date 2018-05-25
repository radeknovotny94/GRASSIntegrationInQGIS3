# -*- coding: utf-8 -*-

"""
***************************************************************************
    GdalAlgorithmDialog.py
    ---------------------
    Date                 : May 2015
    Copyright            : (C) 2015 by Victor Olaya
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
__date__ = 'May 2015'
__copyright__ = '(C) 2015, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import (QWidget,
                                 QVBoxLayout,
                                 QPushButton,
                                 QLabel,
                                 QPlainTextEdit,
                                 QLineEdit,
                                 QComboBox,
                                 QCheckBox,
                                 QSizePolicy,
                                 QDialogButtonBox)

from qgis.core import (QgsProcessingFeedback,
                       QgsProcessingParameterDefinition)
from qgis.gui import (QgsMessageBar,
                      QgsProjectionSelectionWidget,
                      QgsProcessingAlgorithmDialogBase)

from processing_gsoc_grass.gui.AlgorithmDialog import AlgorithmDialog
from processing_gsoc_grass.gui.AlgorithmDialogBase import AlgorithmDialogBase
from processing_gsoc_grass.gui.ParametersPanel import ParametersPanel
from processing_gsoc_grass.gui.MultipleInputPanel import MultipleInputPanel
from processing_gsoc_grass.gui.NumberInputPanel import NumberInputPanel
from processing_gsoc_grass.tools.dataobjects import createContext


class GdalAlgorithmDialog(AlgorithmDialog):

    def __init__(self, alg):
        super().__init__(alg)
        self.mainWidget().parametersHaveChanged()

    def getParametersPanel(self, alg, parent):
        return GdalParametersPanel(parent, alg)


class GdalParametersPanel(ParametersPanel):

    def __init__(self, parent, alg):
        ParametersPanel.__init__(self, parent, alg)

        w = QWidget()
        layout = QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(6)
        label = QLabel()
        label.setText(self.tr("GDAL/OGR console call"))
        layout.addWidget(label)
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)
        w.setLayout(layout)
        self.layoutMain.addWidget(w)

        self.connectParameterSignals()
        self.parametersHaveChanged()

    def connectParameterSignals(self):
        for wrapper in list(self.wrappers.values()):
            w = wrapper.widget
            self.connectWidgetChangedSignals(w)
            for c in w.findChildren(QWidget):
                self.connectWidgetChangedSignals(c)

    def connectWidgetChangedSignals(self, w):
        if isinstance(w, QLineEdit):
            w.textChanged.connect(self.parametersHaveChanged)
        elif isinstance(w, QComboBox):
            w.currentIndexChanged.connect(self.parametersHaveChanged)
        elif isinstance(w, QgsProjectionSelectionWidget):
            w.crsChanged.connect(self.parametersHaveChanged)
        elif isinstance(w, QCheckBox):
            w.stateChanged.connect(self.parametersHaveChanged)
        elif isinstance(w, MultipleInputPanel):
            w.selectionChanged.connect(self.parametersHaveChanged)
        elif isinstance(w, NumberInputPanel):
            w.hasChanged.connect(self.parametersHaveChanged)

    def parametersHaveChanged(self):
        context = createContext()
        feedback = QgsProcessingFeedback()
        try:
            parameters = self.parent.getParameterValues()
            for output in self.alg.destinationParameterDefinitions():
                if not output.name() in parameters or parameters[output.name()] is None:
                    parameters[output.name()] = self.tr("[temporary file]")
            for p in self.alg.parameterDefinitions():
                if (not p.name() in parameters and not p.flags() & QgsProcessingParameterDefinition.FlagOptional) \
                        or (not p.checkValueIsAcceptable(parameters[p.name()])):
                    # not ready yet
                    self.text.setPlainText('')
                    return

            commands = self.alg.getConsoleCommands(parameters, context, feedback, executing=False)
            commands = [c for c in commands if c not in ['cmd.exe', '/C ']]
            self.text.setPlainText(" ".join(commands))
        except AlgorithmDialogBase.InvalidParameterValue as e:
            self.text.setPlainText(self.tr("Invalid value for parameter '{0}'").format(e.parameter.description()))
