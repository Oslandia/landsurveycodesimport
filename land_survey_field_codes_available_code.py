# -*- coding: utf-8 -*-

"""
/***************************************************************************
                                 A QGIS plugin
 This plugin allows you to easily import data from a land survey (GPS or total station) to draw automatically in a database using a codification (aka Field Codes).
                             -------------------
        begin                : 2018-04-05
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Loïc Bartoletti (Oslandia)
        email                : loic.bartoletti@oslandia.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.core import QgsMapLayerProxyModel
from PyQt5.QtCore import QCoreApplication


def tr(message):
    return QCoreApplication.translate('LandSurveyFieldCodes', message)


AVAILABLE_CODE = [
    {"name": tr("Circle from 2 points"),
     "filter": QgsMapLayerProxyModel.PolygonLayer |
     QgsMapLayerProxyModel.LineLayer |
     QgsMapLayerProxyModel.PointLayer,
     "nbpoints": 2,
     "nbparams": 0,
     "available": True,
     "code": "Circle2Points"},
    {"name": tr("Circle from 3 points"),
     "filter": QgsMapLayerProxyModel.PolygonLayer |
     QgsMapLayerProxyModel.LineLayer |
     QgsMapLayerProxyModel.PointLayer,
     "nbpoints": 3,
     "nbparams": 0,
     "available": True,
     "code": "Circle3Points"},
    {"name": tr("Circle from center and radius"),
     "filter": QgsMapLayerProxyModel.PolygonLayer |
     QgsMapLayerProxyModel.LineLayer |
     QgsMapLayerProxyModel.PointLayer,
     "nbpoints": 1,
     "nbparams": 1,
     "available": True,
     "code": "CircleCenterRadius"},
    {"name": tr("Circle from center and diameter"),
     "filter": QgsMapLayerProxyModel.PolygonLayer |
     QgsMapLayerProxyModel.LineLayer |
     QgsMapLayerProxyModel.PointLayer,
     "nbpoints": 1,
     "nbparams": 1,
     "available": True,
     "code": "CircleCenterDiameter"},
    {"name": tr("Square from 2 points"),
     "filter": QgsMapLayerProxyModel.PolygonLayer |
     QgsMapLayerProxyModel.LineLayer |
     QgsMapLayerProxyModel.PointLayer,
     "nbpoints": 2,
     "nbparams": 0,
     "available": True,
     "code": "Square2Points"},
    {"name": tr("Square from 2 diagonal points"),
     "filter": QgsMapLayerProxyModel.PolygonLayer |
     QgsMapLayerProxyModel.LineLayer |
     QgsMapLayerProxyModel.PointLayer,
     "nbpoints": 2,
     "nbparams": 0,
     "available": True,
     "code": "Square2Diagonal"},
    {"name": tr("Rectangle from 2 points and height"),
     "filter": QgsMapLayerProxyModel.PolygonLayer |
     QgsMapLayerProxyModel.LineLayer |
     QgsMapLayerProxyModel.PointLayer,
     "nbpoints": 2,
     "nbparams": 1,
     "available": True,
     "code": "Rectangle2PointsHeight"},
    {"name": tr("Rectangle from 3 points (3rd point = distance)"),
     "filter": QgsMapLayerProxyModel.PolygonLayer |
     QgsMapLayerProxyModel.LineLayer |
     QgsMapLayerProxyModel.PointLayer,
     "nbpoints": 3,
     "nbparams": 0,
     "available": True,
     "code": "Rectangle3PointsDistance"},
    {"name": tr("Rectangle from 3 points (3rd point = projected orthogonal)"),
     "filter": QgsMapLayerProxyModel.PolygonLayer |
     QgsMapLayerProxyModel.LineLayer |
     QgsMapLayerProxyModel.PointLayer,
     "nbpoints": 3,
     "nbparams": 0,
     "available": True,
     "code": "Rectangle3PointsProjected"},
    {"name": tr("Line"),
     "filter": QgsMapLayerProxyModel.PolygonLayer |
     QgsMapLayerProxyModel.LineLayer,
     "nbpoints": -1,
     "nbparams": 0,
     "available": True,
     "code": "Line"},
    {"name": tr("Point"),
     "filter": QgsMapLayerProxyModel.PointLayer,
     "nbpoints": 1,
     "nbparams": 0,
     "available": True,
     "code": "Point"}]
