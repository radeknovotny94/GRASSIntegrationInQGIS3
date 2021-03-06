# -*- coding: utf-8 -*-

"""
***************************************************************************
    __init__.py
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

from processing_gsoc_grass.tools.dataobjects import *          # NOQA
from processing_gsoc_grass.tools.general import *              # NOQA
from processing_gsoc_grass.tools.vector import *               # NOQA
from processing_gsoc_grass.tools.raster import *               # NOQA
from processing_gsoc_grass.tools.system import *               # NOQA


def classFactory(iface):
    from processing_gsoc_grass.ProcessingPlugin import ProcessingPlugin
    return ProcessingPlugin(iface)
