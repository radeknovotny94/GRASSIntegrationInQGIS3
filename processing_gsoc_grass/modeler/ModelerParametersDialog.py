# -*- coding: utf-8 -*-

"""
***************************************************************************
    ModelerParametersDialog.py
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

import webbrowser

from qgis.PyQt.QtCore import (Qt,
                              QUrl,
                              QMetaObject,
                              QByteArray)
from qgis.PyQt.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QLineEdit,
                                 QFrame, QPushButton, QSizePolicy, QVBoxLayout,
                                 QHBoxLayout, QWidget)

from qgis.core import (Qgis,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterPoint,
                       QgsProcessingParameterExtent,
                       QgsProcessingModelAlgorithm,
                       QgsProcessingModelOutput,
                       QgsProcessingModelChildAlgorithm,
                       QgsProcessingModelChildParameterSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingOutputDefinition,
                       QgsSettings)

from qgis.gui import (QgsMessageBar,
                      QgsScrollArea,
                      QgsFilterLineEdit,
                      QgsHelp)

from processing_gsoc_grass.gui.wrappers import WidgetWrapperFactory
from processing_gsoc_grass.gui.wrappers import InvalidParameterValue
from processing_gsoc_grass.gui.MultipleInputPanel import MultipleInputPanel


class ModelerParametersDialog(QDialog):
    ENTER_NAME = '[Enter name if this is a final result]'
    NOT_SELECTED = '[Not selected]'
    USE_MIN_COVERING_EXTENT = '[Use min covering extent]'

    def __init__(self, alg, model, algName=None):
        QDialog.__init__(self)
        self.setModal(True)
        # The algorithm to define in this dialog. It is an instance of QgsProcessingModelAlgorithm
        self._alg = alg
        # The model this algorithm is going to be added to
        self.model = model
        # The name of the algorithm in the model, in case we are editing it and not defining it for the first time
        self.childId = algName
        self.setupUi()
        self.params = None
        settings = QgsSettings()
        self.restoreGeometry(settings.value("/Processing/modelParametersDialogGeometry", QByteArray()))

    def closeEvent(self, event):
        settings = QgsSettings()
        settings.setValue("/Processing/modelParametersDialogGeometry", self.saveGeometry())
        super(ModelerParametersDialog, self).closeEvent(event)

    def setupUi(self):
        self.labels = {}
        self.widgets = {}
        self.checkBoxes = {}
        self.showAdvanced = False
        self.wrappers = {}
        self.valueItems = {}
        self.dependentItems = {}
        self.resize(650, 450)
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok | QDialogButtonBox.Help)
        self.setSizePolicy(QSizePolicy.Expanding,
                           QSizePolicy.Expanding)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setMargin(20)

        self.bar = QgsMessageBar()
        self.bar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.verticalLayout.addWidget(self.bar)

        hLayout = QHBoxLayout()
        hLayout.setSpacing(5)
        hLayout.setMargin(0)
        descriptionLabel = QLabel(self.tr("Description"))
        self.descriptionBox = QLineEdit()
        self.descriptionBox.setText(self._alg.displayName())
        hLayout.addWidget(descriptionLabel)
        hLayout.addWidget(self.descriptionBox)
        self.verticalLayout.addLayout(hLayout)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.verticalLayout.addWidget(line)

        for param in self._alg.parameterDefinitions():
            if param.flags() & QgsProcessingParameterDefinition.FlagAdvanced:
                self.advancedButton = QPushButton()
                self.advancedButton.setText(self.tr('Show advanced parameters'))
                self.advancedButton.clicked.connect(
                    self.showAdvancedParametersClicked)
                advancedButtonHLayout = QHBoxLayout()
                advancedButtonHLayout.addWidget(self.advancedButton)
                advancedButtonHLayout.addStretch()
                self.verticalLayout.addLayout(advancedButtonHLayout)
                break
        for param in self._alg.parameterDefinitions():
            if param.isDestination() or param.flags() & QgsProcessingParameterDefinition.FlagHidden:
                continue
            desc = param.description()
            if isinstance(param, QgsProcessingParameterExtent):
                desc += self.tr('(xmin, xmax, ymin, ymax)')
            if isinstance(param, QgsProcessingParameterPoint):
                desc += self.tr('(x, y)')
            if param.flags() & QgsProcessingParameterDefinition.FlagOptional:
                desc += self.tr(' [optional]')
            label = QLabel(desc)
            self.labels[param.name()] = label

            wrapper = WidgetWrapperFactory.create_wrapper(param, self)
            self.wrappers[param.name()] = wrapper

            widget = wrapper.widget
            if widget is not None:
                self.valueItems[param.name()] = widget
                tooltip = param.description()
                label.setToolTip(tooltip)
                widget.setToolTip(tooltip)
                if param.flags() & QgsProcessingParameterDefinition.FlagAdvanced:
                    label.setVisible(self.showAdvanced)
                    widget.setVisible(self.showAdvanced)
                    self.widgets[param.name()] = widget

                self.verticalLayout.addWidget(label)
                self.verticalLayout.addWidget(widget)

        for dest in self._alg.destinationParameterDefinitions():
            if dest.flags() & QgsProcessingParameterDefinition.FlagHidden:
                continue
            if isinstance(dest, (QgsProcessingParameterRasterDestination, QgsProcessingParameterVectorDestination,
                                 QgsProcessingParameterFeatureSink, QgsProcessingParameterFileDestination, QgsProcessingParameterFolderDestination)):
                label = QLabel(dest.description())
                item = QgsFilterLineEdit()
                if hasattr(item, 'setPlaceholderText'):
                    item.setPlaceholderText(ModelerParametersDialog.ENTER_NAME)
                self.verticalLayout.addWidget(label)
                self.verticalLayout.addWidget(item)
                self.valueItems[dest.name()] = item

        label = QLabel(' ')
        self.verticalLayout.addWidget(label)
        label = QLabel(self.tr('Parent algorithms'))
        self.dependenciesPanel = self.getDependenciesPanel()
        self.verticalLayout.addWidget(label)
        self.verticalLayout.addWidget(self.dependenciesPanel)
        self.verticalLayout.addStretch(1000)

        self.setPreviousValues()
        self.setWindowTitle(self._alg.displayName())
        self.verticalLayout2 = QVBoxLayout()
        self.verticalLayout2.setSpacing(2)
        self.verticalLayout2.setMargin(0)

        self.paramPanel = QWidget()
        self.paramPanel.setLayout(self.verticalLayout)
        self.scrollArea = QgsScrollArea()
        self.scrollArea.setWidget(self.paramPanel)
        self.scrollArea.setWidgetResizable(True)

        self.verticalLayout2.addWidget(self.scrollArea)
        self.verticalLayout2.addWidget(self.buttonBox)
        self.setLayout(self.verticalLayout2)
        self.buttonBox.accepted.connect(self.okPressed)
        self.buttonBox.rejected.connect(self.cancelPressed)
        self.buttonBox.helpRequested.connect(self.openHelp)
        QMetaObject.connectSlotsByName(self)

        for wrapper in list(self.wrappers.values()):
            wrapper.postInitialize(list(self.wrappers.values()))

    def getAvailableDependencies(self):  # spellok
        if self.childId is None:
            dependent = []
        else:
            dependent = list(self.model.dependentChildAlgorithms(self.childId))
            dependent.append(self.childId)
        opts = []
        for alg in list(self.model.childAlgorithms().values()):
            if alg.childId() not in dependent:
                opts.append(alg)
        return opts

    def getDependenciesPanel(self):
        return MultipleInputPanel([alg.description() for alg in self.getAvailableDependencies()])  # spellok

    def showAdvancedParametersClicked(self):
        self.showAdvanced = not self.showAdvanced
        if self.showAdvanced:
            self.advancedButton.setText(self.tr('Hide advanced parameters'))
        else:
            self.advancedButton.setText(self.tr('Show advanced parameters'))
        for param in self._alg.parameterDefinitions():
            if param.flags() & QgsProcessingParameterDefinition.FlagAdvanced:
                self.labels[param.name()].setVisible(self.showAdvanced)
                self.widgets[param.name()].setVisible(self.showAdvanced)

    def getAvailableValuesOfType(self, paramType, outTypes=[], dataTypes=[]):
        # upgrade paramType to list
        if paramType is None:
            paramType = []
        elif not isinstance(paramType, (tuple, list)):
            paramType = [paramType]
        if outTypes is None:
            outTypes = []
        elif not isinstance(outTypes, (tuple, list)):
            outTypes = [outTypes]

        return self.model.availableSourcesForChild(self.childId, [p.typeName() for p in paramType if
                                                                  issubclass(p, QgsProcessingParameterDefinition)],
                                                   [o.typeName() for o in outTypes if
                                                    issubclass(o, QgsProcessingOutputDefinition)], dataTypes)

    def resolveValueDescription(self, value):
        if isinstance(value, QgsProcessingModelChildParameterSource):
            if value.source() == QgsProcessingModelChildParameterSource.StaticValue:
                return value.staticValue()
            elif value.source() == QgsProcessingModelChildParameterSource.ModelParameter:
                return self.model.parameterDefinition(value.parameterName()).description()
            elif value.source() == QgsProcessingModelChildParameterSource.ChildOutput:
                alg = self.model.childAlgorithm(value.outputChildId())
                return self.tr("'{0}' from algorithm '{1}'").format(
                    alg.algorithm().outputDefinition(value.outputName()).description(), alg.description())

        return value

    def setPreviousValues(self):
        if self.childId is not None:
            alg = self.model.childAlgorithm(self.childId)
            self.descriptionBox.setText(alg.description())
            for param in alg.algorithm().parameterDefinitions():
                if param.isDestination() or param.flags() & QgsProcessingParameterDefinition.FlagHidden:
                    continue
                value = None
                if param.name() in alg.parameterSources():
                    value = alg.parameterSources()[param.name()]
                    if isinstance(value, list) and len(value) == 1:
                        value = value[0]
                    elif isinstance(value, list) and len(value) == 0:
                        value = None
                if value is None:
                    value = param.defaultValue()

                if isinstance(value,
                              QgsProcessingModelChildParameterSource) and value.source() == QgsProcessingModelChildParameterSource.StaticValue:
                    value = value.staticValue()

                self.wrappers[param.name()].setValue(value)
            for name, out in list(alg.modelOutputs().items()):
                if out.childOutputName() in self.valueItems:
                    self.valueItems[out.childOutputName()].setText(out.name())

            selected = []
            dependencies = self.getAvailableDependencies()  # spellok
            for idx, dependency in enumerate(dependencies):
                if dependency.childId() in alg.dependencies():
                    selected.append(idx)

            self.dependenciesPanel.setSelectedItems(selected)

    def createAlgorithm(self):
        alg = QgsProcessingModelChildAlgorithm(self._alg.id())
        if not self.childId:
            alg.generateChildId(self.model)
        else:
            alg.setChildId(self.childId)
        alg.setDescription(self.descriptionBox.text())
        for param in self._alg.parameterDefinitions():
            if param.isDestination() or param.flags() & QgsProcessingParameterDefinition.FlagHidden:
                continue
            try:
                val = self.wrappers[param.name()].value()
            except InvalidParameterValue:
                self.bar.pushMessage(self.tr("Error"),
                                     self.tr("Wrong or missing value for parameter '{}'").format(param.description()),
                                     level=Qgis.Warning)
                return None

            if isinstance(val, QgsProcessingModelChildParameterSource):
                val = [val]
            elif not (isinstance(val, list) and all(
                    [isinstance(subval, QgsProcessingModelChildParameterSource) for subval in val])):
                val = [QgsProcessingModelChildParameterSource.fromStaticValue(val)]
            for subval in val:
                if (isinstance(subval, QgsProcessingModelChildParameterSource) and
                    subval.source() == QgsProcessingModelChildParameterSource.StaticValue and
                        not param.checkValueIsAcceptable(subval.staticValue())) \
                        or (subval is None and not param.flags() & QgsProcessingParameterDefinition.FlagOptional):
                    self.bar.pushMessage(self.tr("Error"), self.tr("Wrong or missing value for parameter '{}'").format(
                        param.description()),
                        level=Qgis.Warning)
                    return None
            alg.addParameterSources(param.name(), val)

        outputs = {}
        for dest in self._alg.destinationParameterDefinitions():
            if not dest.flags() & QgsProcessingParameterDefinition.FlagHidden:
                name = str(self.valueItems[dest.name()].text())
                if name.strip() != '' and name != ModelerParametersDialog.ENTER_NAME:
                    output = QgsProcessingModelOutput(name, name)
                    output.setChildId(alg.childId())
                    output.setChildOutputName(dest.name())
                    outputs[name] = output
        alg.setModelOutputs(outputs)

        selectedOptions = self.dependenciesPanel.selectedoptions
        availableDependencies = self.getAvailableDependencies()  # spellok
        dep_ids = []
        for selected in selectedOptions:
            dep_ids.append(availableDependencies[selected].childId())  # spellok
        alg.setDependencies(dep_ids)

        #try:
        #    self._alg.processBeforeAddingToModeler(alg, self.model)
        #except:
        #    pass

        return alg

    def okPressed(self):
        alg = self.createAlgorithm()
        if alg is not None:
            self.accept()

    def cancelPressed(self):
        self.reject()

    def openHelp(self):
        algHelp = self._alg.helpUrl()
        if not algHelp:
            algHelp = QgsHelp.helpUrl("processing_algs/{}/{}.html#{}".format(
                self._alg.provider().helpId(), self._alg.groupId(), "{}{}".format(self._alg.provider().helpId(), self._alg.name()))).toString()

        if algHelp not in [None, ""]:
            webbrowser.open(algHelp)
