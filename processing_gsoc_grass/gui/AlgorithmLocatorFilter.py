# -*- coding: utf-8 -*-

"""
***************************************************************************
    AlgorithmLocatorFilter.py
    -------------------------
    Date                 : May 2017
    Copyright            : (C) 2017 by Nyall Dawson
    Email                : nyall dot dawson at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Nyall Dawson'
__date__ = 'May 2017'
__copyright__ = '(C) 2017, Nyall Dawson'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'


from qgis.core import (QgsApplication,
                       QgsProcessingAlgorithm,
                       QgsLocatorFilter,
                       QgsLocatorResult)
from processing.gui.MessageDialog import MessageDialog
from processing.gui.AlgorithmDialog import AlgorithmDialog
from qgis.utils import iface


class AlgorithmLocatorFilter(QgsLocatorFilter):

    def __init__(self, parent=None):
        super(AlgorithmLocatorFilter, self).__init__(parent)

    def clone(self):
        return AlgorithmLocatorFilter()

    def name(self):
        return 'processing_alg'

    def displayName(self):
        return self.tr('Processing Algorithms')

    def priority(self):
        return QgsLocatorFilter.Low

    def prefix(self):
        return 'a'

    def flags(self):
        return QgsLocatorFilter.FlagFast

    def fetchResults(self, string, context, feedback):
        # collect results in main thread, since this method is inexpensive and
        # accessing the processing registry is not thread safe
        for a in QgsApplication.processingRegistry().algorithms():
            if a.flags() & QgsProcessingAlgorithm.FlagHideFromToolbox:
                continue

            if QgsLocatorFilter.stringMatches(a.displayName(), string) or [t for t in a.tags() if QgsLocatorFilter.stringMatches(t, string)] or \
                    (context.usingPrefix and not string):
                result = QgsLocatorResult()
                result.filter = self
                result.displayString = a.displayName()
                result.icon = a.icon()
                result.userData = a.id()
                if string and QgsLocatorFilter.stringMatches(a.displayName(), string):
                    result.score = float(len(string)) / len(a.displayName())
                else:
                    result.score = 0
                self.resultFetched.emit(result)

    def triggerResult(self, result):
        alg = QgsApplication.processingRegistry().createAlgorithmById(result.userData)
        if alg:
            ok, message = alg.canExecute()
            if not ok:
                dlg = MessageDialog()
                dlg.setTitle(self.tr('Missing dependency'))
                dlg.setMessage(message)
                dlg.exec_()
                return
            dlg = alg.createCustomParametersWidget(None)
            if not dlg:
                dlg = AlgorithmDialog(alg)
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
