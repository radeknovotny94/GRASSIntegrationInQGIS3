# GRASSIntegrationInQGIS3

Goal of this project is create better integration of GRASS GIS in QGIS3.
This project was selected to Google Summer of Code 2018.
For more information see Wiki page: https://trac.osgeo.org/grass/wiki/GSoC/2018/IntegrationInQGIS3

First step is creating parser tool which create UI description for QGIS from GRASS description. For now this implementation is going on other GitHub page, see https://github.com/radeknovotny94/GRASS_Parse_to_QGIS_UI .

In this repository in this moment is working on Processing plugin in QGIS.

How run development version of Processing plugin:
You have to include folder with plugin (processing_gsoc_grass) between core plugins (original Processing plugin is there). e.g. C:\OSGeo4W\apps\qgis\python\plugins\processing_gsoc_grass . After run QGIS are both version of Processing plugin appeared. 