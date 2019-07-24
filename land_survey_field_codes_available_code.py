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
from PyQt5.QtCore import QSettings

AVAILABLE_CODE = [
    {"name": "Circle from 2 points",
     "filter": QgsMapLayerProxyModel.PolygonLayer |
     QgsMapLayerProxyModel.LineLayer |
     QgsMapLayerProxyModel.PointLayer,
     "nbpoints": 2,
     "nbparams": 0,
     "available": True,
     "code": "Circle2Points"},
    {"name": "Circle from 3 points",
     "filter": QgsMapLayerProxyModel.PolygonLayer |
     QgsMapLayerProxyModel.LineLayer |
     QgsMapLayerProxyModel.PointLayer,
     "nbpoints": 3,
     "nbparams": 0,
     "available": True,
     "code": "Circle3Points"},
    {"name": "Circle from center and radius",
     "filter": QgsMapLayerProxyModel.PolygonLayer |
     QgsMapLayerProxyModel.LineLayer |
     QgsMapLayerProxyModel.PointLayer,
     "nbpoints": 1,
     "nbparams": 1,
     "available": True,
     "code": "CircleCenterRadius"},
    {"name": "Circle from center and diameter",
     "filter": QgsMapLayerProxyModel.PolygonLayer |
     QgsMapLayerProxyModel.LineLayer |
     QgsMapLayerProxyModel.PointLayer,
     "nbpoints": 1,
     "nbparams": 1,
     "available": True,
     "code": "CircleCenterDiameter"},
    {"name": "Square from 2 points",
     "filter": QgsMapLayerProxyModel.PolygonLayer |
     QgsMapLayerProxyModel.LineLayer |
     QgsMapLayerProxyModel.PointLayer,
     "nbpoints": 2,
     "nbparams": 0,
     "available": True,
     "code": "Square2Points"},
    {"name": "Square from 2 diagonal points",
     "filter": QgsMapLayerProxyModel.PolygonLayer |
     QgsMapLayerProxyModel.LineLayer |
     QgsMapLayerProxyModel.PointLayer,
     "nbpoints": 2,
     "nbparams": 0,
     "available": True,
     "code": "Square2Diagonal"},
    {"name": "Rectangle from 2 points and height",
     "filter": QgsMapLayerProxyModel.PolygonLayer |
     QgsMapLayerProxyModel.LineLayer |
     QgsMapLayerProxyModel.PointLayer,
     "nbpoints": 2,
     "nbparams": 1,
     "available": True,
     "code": "Rectangle2PointsHeight"},
    {"name": "Rectangle from 3 points (3rd point = distance)",
     "filter": QgsMapLayerProxyModel.PolygonLayer |
     QgsMapLayerProxyModel.LineLayer |
     QgsMapLayerProxyModel.PointLayer,
     "nbpoints": 3,
     "nbparams": 0,
     "available": True,
     "code": "Rectangle3PointsDistance"},
    {"name": "Rectangle from 3 points (3rd point = projected orthogonal)",
     "filter": QgsMapLayerProxyModel.PolygonLayer |
     QgsMapLayerProxyModel.LineLayer |
     QgsMapLayerProxyModel.PointLayer,
     "nbpoints": 3,
     "nbparams": 0,
     "available": True,
     "code": "Rectangle3PointsProjected"},
    {"name": "Line",
     "filter": QgsMapLayerProxyModel.PolygonLayer |
     QgsMapLayerProxyModel.LineLayer,
     "nbpoints": -1,
     "nbparams": 0,
     "available": True,
     "code": "Line"},
    {"name": "Point",
     "filter": QgsMapLayerProxyModel.PointLayer,
     "nbpoints": 1,
     "nbparams": 0,
     "available": True,
     "code": "Point"}]

TRANSLATION = {
        "en" : ["Circle from 2 points","Circle from 3 points", "Circle from center and radius", "Circle from center and diameter", "Square from 2 points", "Square from 2 diagonal points","Rectangle from 2 points and height", "Rectangle from 3 points (3rd point = distance)", "Rectangle from 3 points (3rd point = projected orthogonal)", "Line","Point"],
        "fr" : ["Cercle par 2 points", "Cercle par 3 points", "Cercle par le centre et le rayon", "Cercle par le centre et le diamètre", "Carré par 2 points", "Carré par 2 points en diagonale", "Rectangle par 2 points et une hauteur", "Rectangle par 3 points (3ème point = distance)", "Rectangle par 3 points (3ème point = projetée orthogonale)", "Ligne", "Point"]
        }

def translatedName(name):
    locale = QSettings().value('locale/userLocale')[0:2]
    if locale not in TRANSLATION.keys():
        locale = "en"

    idx = TRANSLATION['en'].index(name)
    return TRANSLATION[locale][idx]

def translatedNameFromGeometryType(geometryType):
    for code in AVAILABLE_CODE:
        if code['code'] == geometryType:
            return translatedName(code['name'])

    print("Hmmm... geometryType not found")
    return geometryType
