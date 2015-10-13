# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SLTRPlugin
                                 A QGIS plugin
 This plugin extends SOLA's functionality using QGIS
                             -------------------
        begin                : 2015-04-20
        copyright            : (C) 2015 by SOLA
        email                : samuel.okoroafor@gems3nigeria.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load SLTRPlugin class from file SolaPlugin.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from sltr import SLTRPlugin
    return SLTRPlugin(iface)
