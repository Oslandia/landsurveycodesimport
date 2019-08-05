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

__author__ = 'Loïc Bartoletti'
__date__ = '2019-07-23'
__copyright__ = '(C) 2019 by Loïc Bartoletti'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import csv
import os

import yaml
try:
    yaml_load = yaml.full_load
except:
    yaml_load = yaml.load

from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFileDestination,
                       QgsVectorLayer, QgsWkbTypes)

from LandSurveyCodesImport.land_survey_utils import verifyCodification
from LandSurveyCodesImport.land_survey_field_codes_available_code import translatedNameFromGeometryType

class landsurveyQLSC2CSV(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    QLSC = 'QLSC'
    OUTPUT = 'OUTPUT'

    def __explodeSource(self, layersource):
        try:
            pathname, layername = layersource.split('|')
            layername = layername[len('layername='):]

            return (pathname, os.path.dirname(pathname), os.path.basename(pathname), layername)
        except:
            return ('', '', '', '')

    def __geometryFromSource(self, layersource):
        l = QgsVectorLayer(layersource)
        return QgsWkbTypes.geometryDisplayString(l.geometryType())

    def qlsc2csv(self, qlsc_path, csv_path, parameters):
        with open(qlsc_path, 'r') as stream:
            code = yaml_load(stream)
            # include verif
            codif = code['Codification']
            with open(csv_path, 'w') as csv_file:
                csv_writer = csv.writer(csv_file, dialect='excel-tab', lineterminator="\n")
                row = ['code']
                for p in ['source', 'pathname', 'dirname', 'basename', 'layername', 'internaltype', 'displaytype', 'geometrytype', 'description', 'attributes']:
                    if parameters[p]:
                        row.append(p)
                csv_writer.writerow(row)
                for k in codif.keys():
                    codification = codif[k]
                    row = [k]
                    if parameters['source']:
                        row.append(codification['Layer'])
                        
                    pathname, dirname, basename, layername = self.__explodeSource(codification['Layer'])
                    if parameters['pathname']:
                        row.append(pathname)
                    if parameters['dirname']:
                        row.append(dirname)
                    if parameters['basename']:
                        row.append(basename)
                    if parameters['layername']:
                        row.append(layername)
                    if parameters['internaltype']:
                        row.append(codification['GeometryType'])
                    if parameters['displaytype']:
                        row.append(translatedNameFromGeometryType(codification['GeometryType']))
                    if parameters['geometrytype']:
                        row.append(self.__geometryFromSource(codification['Layer']))
                    if parameters['description']:
                        row.append(codification['Description'])
                    if parameters['attributes']:               
                        row.append(codification['Attributes'])
                    csv_writer.writerow(row)

                # special points
                param = code['AllPoints']
                csv_writer.writerow(['', param['Layer'], *(self.__explodeSource(param['Layer'])), "AllPoints", self.tr("All points"), '', self.tr("Parameter for all points"), param["isChecked"]])
                param = code['ErrorPoints']
                csv_writer.writerow(['', param['Layer'], *(self.__explodeSource(param['Layer'])), "ErrorPoints", self.tr("Error points"), '', self.tr("Parameter for error points"), param["isChecked"]])
                # code separator
                param = code['CodeSeparator']
                csv_writer.writerow(['', '', '', '', '', '', "CodeSeparator", self.tr("Code separator"), '', self.tr("Parameter for code separator"), param])
                param = code['ParameterSeparator']
                csv_writer.writerow(['', '', '', '', '', '', "ParameterSeparator", self.tr("Parameter separator"), '', self.tr("Parameter for parameter separator"), param])


    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        self.addParameter(
            QgsProcessingParameterFile(
                self.QLSC,
                self.tr('Codification file'),
                extension='qlsc'
            )
        )


        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                self.tr('Output CSV'),
                fileFilter='csv'
            )
        )
        self.addParameter(QgsProcessingParameterBoolean('source', 'source', defaultValue=True, optional=True))
        self.addParameter(QgsProcessingParameterBoolean('pathname', 'pathname', defaultValue=True, optional=True))
        self.addParameter(QgsProcessingParameterBoolean('dirname', 'dirname', defaultValue=True, optional=True))
        self.addParameter(QgsProcessingParameterBoolean('basename', 'basename', defaultValue=True, optional=True))
        self.addParameter(QgsProcessingParameterBoolean('layername', 'layername', defaultValue=True, optional=True))
        self.addParameter(QgsProcessingParameterBoolean('internaltype', 'internaltype', defaultValue=True, optional=True))
        self.addParameter(QgsProcessingParameterBoolean('displaytype', 'displaytype', defaultValue=True, optional=True))
        self.addParameter(QgsProcessingParameterBoolean('geometrytype', 'geometrytype', defaultValue=True, optional=True))
        self.addParameter(QgsProcessingParameterBoolean('description', 'description', defaultValue=True, optional=True))
        self.addParameter(QgsProcessingParameterBoolean('attributes', 'attributes', defaultValue=True, optional=True))

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        qlscfile = self.parameterAsFile(parameters, self.QLSC, context)
        csvfile = self.parameterAsFile(parameters, self.OUTPUT, context)

        self.qlsc2csv(qlscfile, csvfile, parameters)
        
        ret = dict()
        ret['OUTPUT'] = csvfile
        ret['QLSC'] = qlscfile
        return ret

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'qlsc2csv'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Convert QLSC file to CSV file')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return self.tr('Export')

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return landsurveyQLSC2CSV()
