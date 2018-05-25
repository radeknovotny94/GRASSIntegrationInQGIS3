# -*- coding: utf-8 -*-

"""
***************************************************************************
    menus.py
    ---------------------
    Date                 : February 2016
    Copyright            : (C) 2016 by Victor Olaya
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
__date__ = 'February 2016'
__copyright__ = '(C) 2016, Victor Olaya'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import os
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QApplication
from processing_gsoc_grass.core.ProcessingConfig import ProcessingConfig, Setting
from processing_gsoc_grass.gui.MessageDialog import MessageDialog
from processing_gsoc_grass.gui.AlgorithmDialog import AlgorithmDialog
from qgis.utils import iface
from qgis.core import QgsApplication
from processing_gsoc_grass.gui.MessageBarProgress import MessageBarProgress
from processing_gsoc_grass.gui.AlgorithmExecutor import execute
from processing_gsoc_grass.gui.Postprocessing import handleAlgorithmResults
from processing_gsoc_grass.core.Processing import Processing
from processing_gsoc_grass.tools import dataobjects

algorithmsToolbar = None
menusSettingsGroup = 'Menus'

defaultMenuEntries = {}
vectorMenu = QApplication.translate('MainWindow', 'Vect&or')
analysisToolsMenu = vectorMenu + "/" + Processing.tr('&Analysis Tools')
defaultMenuEntries.update({'qgis:distancematrix': analysisToolsMenu,
                           'qgis:sumlinelengths': analysisToolsMenu,
                           'qgis:countpointsinpolygon': analysisToolsMenu,
                           'qgis:listuniquevalues': analysisToolsMenu,
                           'qgis:basicstatisticsforfields': analysisToolsMenu,
                           'qgis:nearestneighbouranalysis': analysisToolsMenu,
                           'native:meancoordinates': analysisToolsMenu,
                           'native:lineintersections': analysisToolsMenu})
researchToolsMenu = vectorMenu + "/" + Processing.tr('&Research Tools')
defaultMenuEntries.update({'qgis:creategrid': researchToolsMenu,
                           'qgis:randomselection': researchToolsMenu,
                           'qgis:randomselectionwithinsubsets': researchToolsMenu,
                           'qgis:randompointsinextent': researchToolsMenu,
                           'qgis:randompointsinlayerbounds': researchToolsMenu,
                           'qgis:randompointsinsidepolygons': researchToolsMenu,
                           'qgis:regularpoints': researchToolsMenu,
                           'native:selectbylocation': researchToolsMenu,
                           'qgis:polygonfromlayerextent': researchToolsMenu})

geoprocessingToolsMenu = vectorMenu + "/" + Processing.tr('&Geoprocessing Tools')
defaultMenuEntries.update({'native:buffer': geoprocessingToolsMenu,
                           'native:convexhull': geoprocessingToolsMenu,
                           'qgis:intersection': geoprocessingToolsMenu,
                           'qgis:union': geoprocessingToolsMenu,
                           'qgis:symmetricaldifference': geoprocessingToolsMenu,
                           'native:clip': geoprocessingToolsMenu,
                           'qgis:difference': geoprocessingToolsMenu,
                           'native:dissolve': geoprocessingToolsMenu,
                           'qgis:eliminateselectedpolygons': geoprocessingToolsMenu})
geometryToolsMenu = vectorMenu + "/" + Processing.tr('G&eometry Tools')
defaultMenuEntries.update({'qgis:checkvalidity': geometryToolsMenu,
                           'qgis:exportaddgeometrycolumns': geometryToolsMenu,
                           'native:centroids': geometryToolsMenu,
                           'qgis:delaunaytriangulation': geometryToolsMenu,
                           'qgis:voronoipolygons': geometryToolsMenu,
                           'native:simplifygeometries': geometryToolsMenu,
                           'qgis:densifygeometries': geometryToolsMenu,
                           'native:multiparttosingleparts': geometryToolsMenu,
                           'native:collect': geometryToolsMenu,
                           'qgis:polygonstolines': geometryToolsMenu,
                           'qgis:linestopolygons': geometryToolsMenu,
                           'native:extractvertices': geometryToolsMenu})
managementToolsMenu = vectorMenu + "/" + Processing.tr('&Data Management Tools')
defaultMenuEntries.update({'qgis:definecurrentprojection': managementToolsMenu,
                           'qgis:joinattributesbylocation': managementToolsMenu,
                           'qgis:splitvectorlayer': managementToolsMenu,
                           'native:mergevectorlayers': managementToolsMenu,
                           'qgis:createspatialindex': managementToolsMenu})

rasterMenu = Processing.tr('&Raster')
projectionsMenu = rasterMenu + "/" + Processing.tr('Projections')
defaultMenuEntries.update({'gdal:warpreproject': projectionsMenu,
                           'gdal:assignprojection': projectionsMenu})
conversionMenu = rasterMenu + "/" + Processing.tr('Conversion')
defaultMenuEntries.update({'gdal:rasterize': conversionMenu,
                           'gdal:polygonize': conversionMenu,
                           'gdal:translate': conversionMenu,
                           'gdal:rgbtopct': conversionMenu,
                           'gdal:pcttorgb': conversionMenu})
extractionMenu = rasterMenu + "/" + Processing.tr('Extraction')
defaultMenuEntries.update({'gdal:contour': extractionMenu,
                           'gdal:cliprasterbyextent': extractionMenu,
                           'gdal:cliprasterbymasklayer': extractionMenu})
analysisMenu = rasterMenu + "/" + Processing.tr('Analysis')
defaultMenuEntries.update({'gdal:sieve': analysisMenu,
                           'gdal:nearblack': analysisMenu,
                           'gdal:fillnodata': analysisMenu,
                           'gdal:proximity': analysisMenu,
                           'gdal:griddatametrics': analysisMenu,
                           'gdal:gridaverage': analysisMenu,
                           'gdal:gridinversedistance': analysisMenu,
                           'gdal:gridnearestneighbor': analysisMenu,
                           'gdal:aspect': analysisMenu,
                           'gdal:hillshade': analysisMenu,
                           'gdal:roughness': analysisMenu,
                           'gdal:slope': analysisMenu,
                           'gdal:tpitopographicpositionindex': analysisMenu,
                           'gdal:triterrainruggednessindex': analysisMenu})
miscMenu = rasterMenu + "/" + Processing.tr('Miscellaneous')
defaultMenuEntries.update({'gdal:buildvirtualraster': miscMenu,
                           'gdal:merge': miscMenu,
                           'gdal:gdalinfo': miscMenu,
                           'gdal:overviews': miscMenu,
                           'gdal:tileindex': miscMenu})


def initializeMenus():
    for provider in QgsApplication.processingRegistry().providers():
        for alg in provider.algorithms():
            d = defaultMenuEntries.get(alg.id(), "")
            setting = Setting(menusSettingsGroup, "MENU_" + alg.id(),
                              "Menu path", d)
            ProcessingConfig.addSetting(setting)
            setting = Setting(menusSettingsGroup, "BUTTON_" + alg.id(),
                              "Add button", False)
            ProcessingConfig.addSetting(setting)
            setting = Setting(menusSettingsGroup, "ICON_" + alg.id(),
                              "Icon", "", valuetype=Setting.FILE)
            ProcessingConfig.addSetting(setting)

    ProcessingConfig.readSettings()


def updateMenus():
    removeMenus()
    QCoreApplication.processEvents()
    createMenus()


def createMenus():
    for alg in QgsApplication.processingRegistry().algorithms():
        menuPath = ProcessingConfig.getSetting("MENU_" + alg.id())
        addButton = ProcessingConfig.getSetting("BUTTON_" + alg.id())
        icon = ProcessingConfig.getSetting("ICON_" + alg.id())
        if icon and os.path.exists(icon):
            icon = QIcon(icon)
        else:
            icon = None
        if menuPath:
            paths = menuPath.split("/")
            addAlgorithmEntry(alg, paths[0], paths[-1], addButton=addButton, icon=icon)


def removeMenus():
    for alg in QgsApplication.processingRegistry().algorithms():
        menuPath = ProcessingConfig.getSetting("MENU_" + alg.id())
        if menuPath:
            paths = menuPath.split("/")
            removeAlgorithmEntry(alg, paths[0], paths[-1])


def addAlgorithmEntry(alg, menuName, submenuName, actionText=None, icon=None, addButton=False):
    action = QAction(icon or alg.icon(), actionText or alg.displayName(), iface.mainWindow())
    action.triggered.connect(lambda: _executeAlgorithm(alg))
    action.setObjectName("mProcessingUserMenu_%s" % alg.id())

    if menuName:
        menu = getMenu(menuName, iface.mainWindow().menuBar())
        submenu = getMenu(submenuName, menu)
        submenu.addAction(action)

    if addButton:
        global algorithmsToolbar
        if algorithmsToolbar is None:
            algorithmsToolbar = iface.addToolBar('ProcessingAlgorithms')
        algorithmsToolbar.addAction(action)


def removeAlgorithmEntry(alg, menuName, submenuName, actionText=None, delButton=True):
    if menuName:
        menu = getMenu(menuName, iface.mainWindow().menuBar())
        subMenu = getMenu(submenuName, menu)
        action = findAction(subMenu.actions(), alg, actionText)
        if action is not None:
            subMenu.removeAction(action)

        if len(subMenu.actions()) == 0:
            subMenu.deleteLater()

    if delButton:
        global algorithmsToolbar
        if algorithmsToolbar is not None:
            action = findAction(algorithmsToolbar.actions(), alg, actionText)
            if action is not None:
                algorithmsToolbar.removeAction(action)


def _executeAlgorithm(alg):
    ok, message = alg.canExecute()
    if not ok:
        dlg = MessageDialog()
        dlg.setTitle(Processing.tr('Missing dependency'))
        dlg.setMessage(
            Processing.tr('<h3>Missing dependency. This algorithm cannot '
                          'be run :-( </h3>\n{0}').format(message))
        dlg.exec_()
        return

    if (alg.countVisibleParameters()) > 0:
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
    else:
        feedback = MessageBarProgress()
        context = dataobjects.createContext(feedback)
        parameters = {}
        ret, results = execute(alg, parameters, context, feedback)
        handleAlgorithmResults(alg, context, feedback)
        feedback.close()


def getMenu(name, parent):
    menus = [c for c in parent.children() if isinstance(c, QMenu) and c.title() == name]
    if menus:
        return menus[0]
    else:
        return parent.addMenu(name)


def findAction(actions, alg, actionText=None):
    for action in actions:
        if action.text() in [actionText, alg.displayName(), alg.name()]:
            return action
    return None
