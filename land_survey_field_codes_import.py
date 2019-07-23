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

from qgis.core import (QgsPoint, QgsCircle, QgsGeometry, QgsRegularPolygon, QgsQuadrilateral, QgsCompoundCurve,
                       QgsFeature, QgsVectorLayer, QgsWkbTypes,
                       QgsExpressionContext, QgsExpressionContextScope,
                       QgsExpression, QgsField,
                       QgsPolygon, QgsLineString, QgsCurvePolygon, QgsCircularString)

from PyQt5.QtCore import QVariant
import csv
import yaml

from land_survey_field_codes_available_code import AVAILABLE_CODE

CODE_POSITION = 4
PARAM_POSITION = 5
ATTRS_POSITION = 6

CODES = set()


def geomFromType(points, parameters, geomtype, layerType):
    """
    Returns the geometry from a points list, with parameters for the specific
    geometry type to the layer type

    Parameters
    ----------

    points: list of coordinates
        Contains at least one point
    parameters: list
        Can be empty, else it's a string needed for some geometry type
    geomtype: int
        Identifiant of the type of geometry
        (Circle from 2 points, Circle from center and diameter, etc.)
    layerType: int
        QGIS identifiant of the layer type
        (0: Point, 1: LineString, 2: Polygon)
    """
    if (geomtype == "Circle2Points"):
        try:
            geom = QgsCircle.from2Points(QgsPoint(*[float(f) for
                                                    f in points[0]]),
                                         QgsPoint(*[float(f) for
                                                    f in points[1]]))
            if layerType == 0:
                return QgsGeometry(geom.center())
            elif layerType == 1:
                return QgsGeometry(geom.toLineString())
            else:
                return QgsGeometry(geom.toPolygon())
        except:
            return None

    elif (geomtype == "Circle3Points"):
        try:
            geom = QgsCircle.from3Points(QgsPoint(*[float(f) for
                                                    f in points[0]]),
                                         QgsPoint(*[float(f) for
                                                    f in points[1]]),
                                         QgsPoint(*[float(f) for
                                                    f in points[2]]))
            if layerType == 0:
                return QgsGeometry(geom.center())
            elif layerType == 1:
                return QgsGeometry(geom.toLineString())
            else:
                return QgsGeometry(geom.toPolygon())
        except:
            return None

    elif (geomtype == "CircleCenterRadius"):
        try:
            geom = QgsCircle.fromCenterDiameter(QgsPoint(*[float(f) for
                                                           f in points[0]]),
                                                float(parameters[0]) * 2.0)
            if layerType == 0:
                return QgsGeometry(geom.center())
            elif layerType == 1:
                return QgsGeometry(geom.toLineString())
            else:
                return QgsGeometry(geom.toPolygon())
        except:
            return None
    
    elif (geomtype == "CircleCenterDiameter"):
        try:
            geom = QgsCircle.fromCenterDiameter(QgsPoint(*[float(f) for
                                                           f in points[0]]),
                                                float(parameters[0]))
            if layerType == 0:
                return QgsGeometry(geom.center())
            elif layerType == 1:
                return QgsGeometry(geom.toLineString())
            else:
                return QgsGeometry(geom.toPolygon())
        except:
            return None
    
    elif (geomtype == "Square2Points"):
        try:
            geom = QgsRegularPolygon(QgsPoint(*[float(f) for f in points[0]]),
                                     QgsPoint(*[float(f) for f in points[1]]),
                                     4)
            if layerType == 0:
                return QgsGeometry(geom.center())
            elif layerType == 1:
                return QgsGeometry(geom.toLineString())
            else:
                return QgsGeometry(geom.toPolygon())
        except:
            return None
    elif (geomtype == "Square2Diagonal"):
        try:
            geom = QgsQuadrilateral.squareFromDiagonal(QgsPoint(*[float(f) for f in points[0]]),
                                     QgsPoint(*[float(f) for f in points[1]])
                                     )
            if layerType == 0:
                return QgsGeometry(geom.toPolygon().centroid())
            elif layerType == 1:
                return QgsGeometry(geom.toLineString())
            else:
                return QgsGeometry(geom.toPolygon())
        except:
            return None
    elif (geomtype == "Rectangle2PointsHeight"):
        try:
            p0 = QgsPoint(*[float(f) for f in points[0]])
            p1 = QgsPoint(*[float(f) for f in points[1]])
            azimuth = p0.azimuth(p1)
            distance = float(parameters[0])
            geom = QgsQuadrilateral(p0, p1, p1.project(distance, azimuth + 90.0), p0.project(distance, azimuth + 90.0))
            if layerType == 0:
                return QgsGeometry(geom.toPolygon().centroid())
            elif layerType == 1:
                return QgsGeometry(geom.toLineString())
            else:
                return QgsGeometry(geom.toPolygon())
        except Exception as e:
            print(e)
            return None
    elif (geomtype == "Rectangle3PointsDistance"):
        try:
            geom = QgsQuadrilateral.rectangleFrom3Points(QgsPoint(*[float(f) for f in points[0]]),
                                     QgsPoint(*[float(f) for f in points[1]]),
                                     QgsPoint(*[float(f) for f in points[2]]),
                                     QgsQuadrilateral.Distance
                                     )
            if layerType == 0:
                return QgsGeometry(geom.toPolygon().centroid())
            elif layerType == 1:
                return QgsGeometry(geom.toLineString())
            else:
                return QgsGeometry(geom.toPolygon())
        except:
            return None
    elif (geomtype == "Rectangle3PointsProjected"):
        try:
            geom = QgsQuadrilateral.rectangleFrom3Points(QgsPoint(*[float(f) for f in points[0]]),
                                     QgsPoint(*[float(f) for f in points[1]]),
                                     QgsPoint(*[float(f) for f in points[2]]),
                                     QgsQuadrilateral.Projected
                                     )
            if layerType == 0:
                return QgsGeometry(geom.toPolygon().centroid())
            elif layerType == 1:
                return QgsGeometry(geom.toLineString())
            else:
                return QgsGeometry(geom.toPolygon())
        except:
            return None
    elif (geomtype == "Line"):
        if layerType == 0:
            return None

        nb = len(points)

        if nb < 2:
            return (None, nb)

        line = []
        arc = []
        arcBefore = False
        curve = QgsCompoundCurve()
        for i, p in enumerate(points):
            if parameters[i] != '3':
                if len(arc) > 0: # Arc haven't 3 points so points go in the straight line
                    # TODO : LOG
                    line += arc
                    arc = []
                if (len(line) == 0 and i+1 == len(points)) or arcBefore: # The final point, is a single point and must be a linestring, so we take the last point
                    line.append(QgsPoint(*[float(f) for f in points[i-1]]))
                line.append(QgsPoint(*[float(f) for f in p]))
                arcBefore = False
            else:
                # get first point to the junction
                if len(line) > 0:
                    line.append(QgsPoint(*[float(f) for f in p]))
                    curve.addCurve(QgsLineString(line))
                    line = []
                arc.append(QgsPoint(*[float(f) for f in p]))
                if len(arc) == 3:
                    curve.addCurve(QgsCircularString(*arc))
                    arc = []
                arcBefore = True
       
        if line: # Oh, only a linestring not yet parsed
            curve.addCurve(QgsLineString(line))

        if layerType == 1:
            return (QgsGeometry(curve), arc)
        else:
            p = QgsCurvePolygon()
            curve.close()
            p.setExteriorRing(curve)
            return (QgsGeometry(p), arc)
        return (None, arc)
    elif (geomtype == "Point"):
        try:
            if layerType == 0:
                return QgsGeometry(QgsPoint(*[float(f) for f in points[0]]))
            else:
                return None
        except:
            return None

    return None


def addRowInLayer(row, errTable, table_codif):
    """
    Rows will be converted in a geometry thanks to codification.
    All attributes will be added thanks to QgsExpressionContext.

    Parameters
    ----------
    row: list of list
        A row contains one or many list of points.
    errTable: list of list
        Contains points in error.
        Some points can be added after the end of this function.
    table_codif: dictionnary
        The codification file. See the information about qlsc format.
    """

    #  TODO: assert?
    code = row[CODE_POSITION][0]
    parameters = row[PARAM_POSITION]

    codif = table_codif['Codification'][code]
    layerName = codif['Layer']

    layer = QgsVectorLayer(layerName)

    dim = 4 if QgsWkbTypes.hasZ(layer.dataProvider().wkbType()) else 3

    geom = geomFromType(list(zip(*row[1:dim])), parameters,
                        codif['GeometryType'], layer.geometryType())
  
    if codif['GeometryType'] == 'Line':
        orphanNodes = geom[1]
        geom = geom[0]

    if geom:
        if codif['GeometryType'] == 'Line':
            arc = list(zip(*row))
            for r in arc[len(arc)-len(orphanNodes):]:
                errTable.append(r)

        layer.startEditing()

        fields = layer.fields()
        newFeature = QgsFeature(fields)

        newFeature.setGeometry(geom)

        for e in codif['Attributes']:
            # print(e, e[1], e[1].startswith('_att'))
            if e[1].startswith('_att'):
                # len('_att') == 4
                try:
                    nb = int(e[1][4:]) - 1
                    assert(nb >= 0)
                    val = row[ATTRS_POSITION + nb][0]
                    newFeature[e[0]] = val
                except:
                    print("attributes error")
                    pass
            else:
                context = QgsExpressionContext()
                scope = QgsExpressionContextScope()
                try:
                    exp = QgsExpression(e[1])
                    scope.setFeature(newFeature)
                    context.appendScope(scope)
                    newFeature[e[0]] = exp.evaluate(context)
                except:
                    print('key error')
                    pass

        ret = layer.addFeature(newFeature)
        if not ret:
           print(ret)

        ret = layer.commitChanges()
        if not ret:
            print(layer.commitErrors())
            for err in list(zip(*row)):
                errTable.append(err)

        layer.updateExtents()
    else:
        for err in list(zip(*row)):
            errTable.append(err)


def parseTable(table, errTable, table_codif, parameterSeparator='-'):
    """
    This is the principal function. From a separated table from ``separeTable``
    the function traverse all rows in the table, look at the code. If a code
    require several points, traverse as required to get all necessary points
    and create the desired geometry. If the number of points is not available,
    for example only two points with the code for a circle with 3 points, the
    points are sended in the error table.
    TODO: linestring

    Parameters
    ----------
    table: list of list
        The table contains survey points, separated before.
        It's a list of list with same lengths.
    errTable: list of list
        Contains points in error.
        Some points can be added after the end of this function.
    table_codif: dictionnary
        The codification file. See the information about qlsc format.
    parameterSeparator: str
        The separator for parameter

    Returns
    -------
        Nothing
        rows in error will be added in errTable

    Examples
    --------
    table = [['2', '1980244.900', '5190520.938', '1002.461', '300'],
            ['2', '1980244.900', '5190520.938', '1002.461', '200'],
            ['3', '1980249.438', '5190515.953', '1002.329', '101'],
            ['1', '1980242.941', '5190519.460', '1002.521', '200'],
            ['1', '1980242.941', '5190519.460', '1002.521', '300']]
    errTable = [['4', '1980243.653', '5190516.354', '1002.369', '42-50']]
    # Simplified for the example
    # GeometryType are:
    #     10: a point
    #      0: circle by 2 points
    #      1: circle by 3 points
    table_codif = {'Codification': {'101': {'GeometryType': 10},
                                    '200': {'GeometryType': 1},
                                    '300': {'GeometryType': 0}}}
    parseTable(table, errTable, table_codif)
    # works of addRowInLayer
    print(errTable)
    >>> [['4', '1980243.653', '5190516.354', '1002.369', '42-50'],
         ['2', '1980244.900', '5190520.938', '1002.461', '200'],
         ['1', '1980242.941', '5190519.460', '1002.521', '200']]]
    """

    # sorted is stable
    # [['3', '1980249.438', '5190515.953', '1002.329', '101'],
    #  ['2', '1980244.900', '5190520.938', '1002.461', '200'],
    #  ['1', '1980242.941', '5190519.460', '1002.521', '200'],
    #  ['2', '1980244.900', '5190520.938', '1002.461', '300'],
    #  ['1', '1980242.941', '5190519.460', '1002.521', '300']]
    w_table = sorted(table, key=lambda t: t[CODE_POSITION])
    j = 0
    while j < len(w_table):
        row = w_table[j]
        code = row[CODE_POSITION]
        try:
            codif = table_codif['Codification'][code]
            idx = [v["code"] for v in AVAILABLE_CODE].index(codif['GeometryType'])
            nbPoints = AVAILABLE_CODE[idx]['nbpoints']
        except:
            #print('key error')
            break

        initRow = []
        initRow.append(row)
        n = 0
        if nbPoints < 0: # Special case for line
            run = True
            arc = []
            while run:
                if j+n+1 >= len(w_table):
                    break
                tmp_row = w_table[j+n+1]
                tmp_code = tmp_row[CODE_POSITION]
                if tmp_code == code:
                    tsep = tmp_row[PARAM_POSITION][0]
                    if tsep == '1':
                        run = False
                    else:
                        initRow.append(tmp_row)
                        n += 1
                        if tsep == '9':
                            run = False
                else:
                    run = False
            if len(initRow) < 2:
                for r in list(zip(*initRow)):
                    errTable.append(r)
                initRow = None
        else:
            for n in range(1, nbPoints):
                # special case when a geometry require multiple points
                # and we have traverse the table
                if j+n >= len(w_table):
                    errTable.append(initRow)
                    break
                tmp_row = w_table[j+n]
                initRow.append(tmp_row)
                if tmp_row[CODE_POSITION] != code:
                    initRow.pop()
                    n -= 1
                    errTable.append(initRow)
                    break
        j += n
        j += 1

        # Play with me
        if initRow:
            addRowInLayer(list(zip(*initRow)), errTable, table_codif)


def insertSpecialPoints(table, layerFile):
    """
    Insert "special" points of error or all table in is specific layer.

    Parameters
    ----------
    table: list of list
        The table contains, all or in error, survey points.
    layerFile: Path to the QgsVectorLayer
        The specific layer where points will go.
    """

    layer = QgsVectorLayer(layerFile)
    if layer.geometryType() != QgsWkbTypes.PointGeometry:
        return

    layer.startEditing()
    fieldsList = ['point_id', 'point_x', 'point_y', 'point_z', 'point_code']

    for f in fieldsList:
        if layer.fields().indexFromName(f) == -1:
            layer.dataProvider().addAttributes([QgsField(f, QVariant.String)])
    for i in range(max([len(t) for t in table]) - ATTRS_POSITION):
        f = 'point_att'+str(i+1)
        if layer.fields().indexFromName(f) == -1:
            layer.dataProvider().addAttributes([QgsField(f, QVariant.String)])

    layer.updateFields()
    fields = layer.fields()

    for row in table:
        newFeature = QgsFeature(fields)
        if QgsWkbTypes.Point == layer.dataProvider().wkbType():
            wkt_point = 'POINT({} {})'.format(row[1], row[2])
        else:
            wkt_point = 'POINT({} {} {})'.format(row[1], row[2], row[3])
        newFeature.setGeometry(QgsGeometry.fromWkt(wkt_point))
        newFeature['point_id'] = row[0]
        newFeature['point_x'] = row[1]
        newFeature['point_y'] = row[2]
        newFeature['point_z'] = row[3]
        newFeature['point_code'] = row[4]
        for i in range(len(row[ATTRS_POSITION:])):
            newFeature['point_att'+str(i+1)] = row[ATTRS_POSITION+i]
        ret = layer.addFeature(newFeature)
        #if not ret:
       #     print(ret)
    layer.commitChanges()


def separeTable(table, codesList, CodeSeparator='+', ParameterSeparator='-'):
    """
    From a table separate all rows with a multi code on the same point.

    Parameters
    ----------
    table : list of list
        The table contains survey points is a list of list with same lengths.
    codesList : dict_keys
        Codes allowed in the codification file. Keys are str.
    CodeSeparator : str
        Separator character to separate multi code on a point.
    ParameterSeparator : str
        Parameter character to indicate the parameter for the code.

    Returns
    -------
    tuple with two lists of lists
        First list of list is separate table
        Second list of lists is row inputed in the error table

    Examples
    --------
    >>> table = [['2', '1980244.900', '5190520.938', '1002.461', '300+200'],
                 ['3', '1980249.438', '5190515.953', '1002.329', '101'],
                 ['1', '1980242.941', '5190519.460', '1002.521', '200+300'],
                 ['4', '1980243.653', '5190516.354', '1002.369', '42-50']]
    # simplified for the example
    >>> codesList = {'101': [],
                     '200': [],
                     '300': []}.keys()
    >>> CodeSeparator = '+'
    >>> ParameterSeparator = '-'
    >>> (outTable, errTable) = separeTable(table, codesList,
            CodeSeparator, ParameterSeparator)
    >>> print(outTable)
    [['2', '1980244.900', '5190520.938', '1002.461', '300'],
     ['2', '1980244.900', '5190520.938', '1002.461', '200'],
     ['3', '1980249.438', '5190515.953', '1002.329', '101'],
     ['1', '1980242.941', '5190519.460', '1002.521', '200'],
     ['1', '1980242.941', '5190519.460', '1002.521', '300']]
    >>> print(errTable)
    [['4', '1980243.653', '5190516.354', '1002.369', '42-50']]
    """

    # Pre condition
    # table must be a list
    assert(isinstance(table, list) and
           # of list
           len(table) > 0 and
           all([isinstance(c, list) for c in table]) and
           # with same lenghts
           all([True if len(c) == len(table[0]) else False for c in table]) and
           # minimal lenght 5 (id, x, y, z, codes-parameters)
           len(table[0]) >= 5
           )
    # codesList a dict_keys
    assert(isinstance(codesList, type({}.keys())) and
           all([isinstance(k, str) for k in codesList]))
    # CodeSeparator a character
    assert(isinstance(CodeSeparator, str) and len(CodeSeparator) == 1)
    # ParameterSeparator a character
    assert(isinstance(ParameterSeparator, str) and
           len(ParameterSeparator) == 1)

    outTable = []
    noCodeTable = []
    sep = 0
    err = 0
    for row in table:
        # TODO: Vérifier la structure de la table?
        codes = [x for x in row[CODE_POSITION].split(CodeSeparator)
                 if x.strip()]
        for c in codes:
            sep += 1
            try:
                sp = c.split(ParameterSeparator)
                param = sp[1]
                c = sp[0]
            except:
                param = []

            CODES.add(c)
            line = row[:CODE_POSITION] + [c] + [param] + row[CODE_POSITION+1:]
            # TODO: test avec paramètres?
            if c.split(ParameterSeparator)[0] in codesList:
                outTable.append(line)
            else:
                err += 1
                noCodeTable.append(line)

    # Post condition
    assert(isinstance(outTable, list) and
           isinstance(noCodeTable, list) and
           len(noCodeTable) == err and
           (len(outTable) + len(noCodeTable)) == sep)

    return (outTable, noCodeTable)


def verifyCodification(code_file):
    assert(all([x in code_file for x in
                ['AllPoints', 'ErrorPoints',
                 'ParameterSeparator', 'CodeSeparator',
                 'Codification']]))

    for c in ['CodeSeparator', 'ParameterSeparator']:
        sep = code_file[c]
        # TODO: Code and Parameter check in a predefined list?
        assert(isinstance(sep, str) and len(sep) == 1)

    for c in ['AllPoints', 'ErrorPoints']:
        dict_points = code_file[c]
        assert('Layer' in dict_points and
               isinstance(dict_points['Layer'], str) and
               # TODO: check if layer exists
               'isChecked' in dict_points and
               isinstance(dict_points['isChecked'], bool)
               )

    codif = code_file['Codification']
    assert(isinstance(codif, dict))
    # assert(len(codif.keys()) > 0)
    for k in codif.keys():
        c = codif[k]
        assert(all([x in c for x in
                    ['Attributes', 'Description',
                     'GeometryType', 'Layer']]))
        assert(isinstance(c['Attributes'], list))
        assert(isinstance(c['Description'], str))
        assert(isinstance(c['GeometryType'], str) and
           c['GeometryType'] in [v["code"] for v in AVAILABLE_CODE])
        assert(isinstance(c['Layer'], str)
               # TODO: check if layer exists
               )


def landsurveyImport(FILE, QLSC):
    codesList = []
    with open(QLSC, 'r') as stream:
        code = yaml.load(stream)
        verifyCodification(code)
        codesList = code['Codification'].keys()

    rows = []
    with open(FILE, 'r') as codif:
        reader = csv.reader(codif)
        rows = [r for r in reader if (len(r) >= 5 and r[0][0] != '#')]

    (table, error) = separeTable(rows,
                                 codesList,
                                 code['CodeSeparator'],
                                 code['ParameterSeparator'])
    parseTable(table, error, code)

    if code['AllPoints']['isChecked'] and len(table) > 0:
        insertSpecialPoints(table, code['AllPoints']['Layer'])
    if code['ErrorPoints']['isChecked'] and len(error) > 0:
        insertSpecialPoints(error, code['ErrorPoints']['Layer'])
