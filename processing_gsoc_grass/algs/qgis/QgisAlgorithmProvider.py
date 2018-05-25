# -*- coding: utf-8 -*-

"""
***************************************************************************
    QgisAlgorithmProvider.py
    ---------------------
    Date                 : December 2012
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
__date__ = 'December 2012'
__copyright__ = '(C) 2012, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

try:
    import plotly  # NOQA
    hasPlotly = True
except:
    hasPlotly = False

from qgis.core import (QgsApplication,
                       QgsProcessingProvider)

from processing.script import ScriptUtils

from .QgisAlgorithm import QgisAlgorithm

from .AddTableField import AddTableField
from .Aggregate import Aggregate
from .Aspect import Aspect
from .BasicStatistics import BasicStatisticsForField
from .CheckValidity import CheckValidity
from .ConcaveHull import ConcaveHull
from .CreateAttributeIndex import CreateAttributeIndex
from .CreateConstantRaster import CreateConstantRaster
from .Datasources2Vrt import Datasources2Vrt
from .DefineProjection import DefineProjection
from .Delaunay import Delaunay
from .DeleteColumn import DeleteColumn
from .DeleteDuplicateGeometries import DeleteDuplicateGeometries
from .DeleteHoles import DeleteHoles
from .DensifyGeometries import DensifyGeometries
from .DensifyGeometriesInterval import DensifyGeometriesInterval
from .Difference import Difference
from .EliminateSelection import EliminateSelection
from .ExecuteSQL import ExecuteSQL
from .Explode import Explode
from .ExportGeometryInfo import ExportGeometryInfo
from .ExtendLines import ExtendLines
from .ExtentFromLayer import ExtentFromLayer
from .ExtractSpecificVertices import ExtractSpecificVertices
from .FieldPyculator import FieldsPyculator
from .FieldsCalculator import FieldsCalculator
from .FieldsMapper import FieldsMapper
from .FindProjection import FindProjection
from .GeometryConvert import GeometryConvert
from .GeometryByExpression import GeometryByExpression
from .Grid import Grid
from .Heatmap import Heatmap
from .Hillshade import Hillshade
from .HubDistanceLines import HubDistanceLines
from .HubDistancePoints import HubDistancePoints
from .HypsometricCurves import HypsometricCurves
from .IdwInterpolation import IdwInterpolation
from .ImportIntoPostGIS import ImportIntoPostGIS
from .ImportIntoSpatialite import ImportIntoSpatialite
from .Intersection import Intersection
from .KeepNBiggestParts import KeepNBiggestParts
from .LinesToPolygons import LinesToPolygons
from .MinimumBoundingGeometry import MinimumBoundingGeometry
from .NearestNeighbourAnalysis import NearestNeighbourAnalysis
from .OffsetLine import OffsetLine
from .Orthogonalize import Orthogonalize
from .PointDistance import PointDistance
from .PointOnSurface import PointOnSurface
from .PointsAlongGeometry import PointsAlongGeometry
from .PointsDisplacement import PointsDisplacement
from .PointsFromLines import PointsFromLines
from .PointsFromPolygons import PointsFromPolygons
from .PointsInPolygon import PointsInPolygon
from .PointsLayerFromTable import PointsLayerFromTable
from .PointsToPaths import PointsToPaths
from .PoleOfInaccessibility import PoleOfInaccessibility
from .Polygonize import Polygonize
from .PolygonsToLines import PolygonsToLines
from .PostGISExecuteSQL import PostGISExecuteSQL
from .RandomExtract import RandomExtract
from .RandomExtractWithinSubsets import RandomExtractWithinSubsets
from .RandomPointsAlongLines import RandomPointsAlongLines
from .RandomPointsExtent import RandomPointsExtent
from .RandomPointsLayer import RandomPointsLayer
from .RandomPointsPolygons import RandomPointsPolygons
from .RandomSelection import RandomSelection
from .RandomSelectionWithinSubsets import RandomSelectionWithinSubsets
from .Rasterize import RasterizeAlgorithm
from .RasterCalculator import RasterCalculator
from .RasterLayerStatistics import RasterLayerStatistics
from .RectanglesOvalsDiamondsFixed import RectanglesOvalsDiamondsFixed
from .RectanglesOvalsDiamondsVariable import RectanglesOvalsDiamondsVariable
from .RegularPoints import RegularPoints
from .Relief import Relief
from .ReverseLineDirection import ReverseLineDirection
from .Ruggedness import Ruggedness
from .SelectByAttribute import SelectByAttribute
from .SelectByExpression import SelectByExpression
from .ServiceAreaFromLayer import ServiceAreaFromLayer
from .ServiceAreaFromPoint import ServiceAreaFromPoint
from .SetMValue import SetMValue
from .SetRasterStyle import SetRasterStyle
from .SetVectorStyle import SetVectorStyle
from .SetZValue import SetZValue
from .ShortestPathLayerToPoint import ShortestPathLayerToPoint
from .ShortestPathPointToLayer import ShortestPathPointToLayer
from .ShortestPathPointToPoint import ShortestPathPointToPoint
from .SingleSidedBuffer import SingleSidedBuffer
from .Slope import Slope
from .SnapGeometries import SnapGeometriesToLayer
from .SpatialiteExecuteSQL import SpatialiteExecuteSQL
from .SpatialIndex import SpatialIndex
from .SpatialJoin import SpatialJoin
from .SpatialJoinSummary import SpatialJoinSummary
from .StatisticsByCategories import StatisticsByCategories
from .SumLines import SumLines
from .SymmetricalDifference import SymmetricalDifference
from .TextToFloat import TextToFloat
from .TinInterpolation import TinInterpolation
from .TopoColors import TopoColor
from .TruncateTable import TruncateTable
from .Union import Union
from .UniqueValues import UniqueValues
from .VariableDistanceBuffer import VariableDistanceBuffer
from .VectorSplit import VectorSplit
from .VoronoiPolygons import VoronoiPolygons
from .ZonalStatistics import ZonalStatistics


pluginPath = os.path.normpath(os.path.join(
    os.path.split(os.path.dirname(__file__))[0], os.pardir))


class QgisAlgorithmProvider(QgsProcessingProvider):

    def __init__(self):
        super().__init__()
        self.algs = []
        self.externalAlgs = []

    def getAlgs(self):
        algs = [AddTableField(),
                Aggregate(),
                Aspect(),
                BasicStatisticsForField(),
                CheckValidity(),
                ConcaveHull(),
                CreateAttributeIndex(),
                CreateConstantRaster(),
                Datasources2Vrt(),
                DefineProjection(),
                Delaunay(),
                DeleteColumn(),
                DeleteDuplicateGeometries(),
                DeleteHoles(),
                DensifyGeometries(),
                DensifyGeometriesInterval(),
                Difference(),
                EliminateSelection(),
                ExecuteSQL(),
                Explode(),
                ExportGeometryInfo(),
                ExtendLines(),
                ExtentFromLayer(),
                ExtractSpecificVertices(),
                FieldsCalculator(),
                FieldsMapper(),
                FieldsPyculator(),
                FindProjection(),
                GeometryByExpression(),
                GeometryConvert(),
                Grid(),
                Heatmap(),
                Hillshade(),
                HubDistanceLines(),
                HubDistancePoints(),
                HypsometricCurves(),
                IdwInterpolation(),
                ImportIntoPostGIS(),
                ImportIntoSpatialite(),
                Intersection(),
                KeepNBiggestParts(),
                LinesToPolygons(),
                MinimumBoundingGeometry(),
                NearestNeighbourAnalysis(),
                OffsetLine(),
                Orthogonalize(),
                PointDistance(),
                PointOnSurface(),
                PointsAlongGeometry(),
                PointsDisplacement(),
                PointsFromLines(),
                PointsFromPolygons(),
                PointsInPolygon(),
                PointsLayerFromTable(),
                PointsToPaths(),
                PoleOfInaccessibility(),
                Polygonize(),
                PolygonsToLines(),
                PostGISExecuteSQL(),
                RandomExtract(),
                RandomExtractWithinSubsets(),
                RandomPointsAlongLines(),
                RandomPointsExtent(),
                RandomPointsLayer(),
                RandomPointsPolygons(),
                RandomSelection(),
                RandomSelectionWithinSubsets(),
                RasterCalculator(),
                RasterizeAlgorithm(),
                RasterLayerStatistics(),
                RectanglesOvalsDiamondsFixed(),
                RectanglesOvalsDiamondsVariable(),
                RegularPoints(),
                Relief(),
                ReverseLineDirection(),
                Ruggedness(),
                SelectByAttribute(),
                SelectByExpression(),
                ServiceAreaFromLayer(),
                ServiceAreaFromPoint(),
                SetMValue(),
                SetRasterStyle(),
                SetVectorStyle(),
                SetZValue(),
                ShortestPathLayerToPoint(),
                ShortestPathPointToLayer(),
                ShortestPathPointToPoint(),
                SingleSidedBuffer(),
                Slope(),
                SnapGeometriesToLayer(),
                SpatialiteExecuteSQL(),
                SpatialIndex(),
                SpatialJoin(),
                SpatialJoinSummary(),
                StatisticsByCategories(),
                SumLines(),
                SymmetricalDifference(),
                TextToFloat(),
                TinInterpolation(),
                TopoColor(),
                TruncateTable(),
                Union(),
                UniqueValues(),
                VariableDistanceBuffer(),
                VectorSplit(),
                VoronoiPolygons(),
                ZonalStatistics()
                ]

        if hasPlotly:
            from .BarPlot import BarPlot
            from .BoxPlot import BoxPlot
            from .MeanAndStdDevPlot import MeanAndStdDevPlot
            from .PolarPlot import PolarPlot
            from .RasterLayerHistogram import RasterLayerHistogram
            from .VectorLayerHistogram import VectorLayerHistogram
            from .VectorLayerScatterplot import VectorLayerScatterplot
            from .VectorLayerScatterplot3D import VectorLayerScatterplot3D

            algs.extend([BarPlot(),
                         BoxPlot(),
                         MeanAndStdDevPlot(),
                         PolarPlot(),
                         RasterLayerHistogram(),
                         VectorLayerHistogram(),
                         VectorLayerScatterplot(),
                         VectorLayerScatterplot3D()])

        # to store algs added by 3rd party plugins as scripts
        #folder = os.path.join(os.path.dirname(__file__), 'scripts')
        #scripts = ScriptUtils.loadFromFolder(folder)
        #for script in scripts:
        #    script.allowEdit = False
        #algs.extend(scripts)

        return algs

    def id(self):
        return 'qgis'

    def name(self):
        return 'QGIS'

    def icon(self):
        return QgsApplication.getThemeIcon("/providerQgis.svg")

    def svgIconPath(self):
        return QgsApplication.iconPath("providerQgis.svg")

    def loadAlgorithms(self):
        self.algs = self.getAlgs()
        for a in self.algs:
            self.addAlgorithm(a)
        for a in self.externalAlgs:
            self.addAlgorithm(a)

    def supportsNonFileBasedOutput(self):
        return True
