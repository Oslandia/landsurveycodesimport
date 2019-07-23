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

import yaml
import csv
import os

from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination,
                       QgsVectorLayer, QgsWkbTypes)

from .land_survey_utils import verifyCodification


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
        pathname, layername = layersource.split('|')
        layername = layername[len('layername='):]

        return (pathname, os.path.dirname(pathname), os.path.basename(pathname), layername)

    def __geometryFromSource(self, layersource):
        l = QgsVectorLayer(layersource)
        return QgsWkbTypes.geometryDisplayString(l.geometryType())

    def __attributesToString(self, attributes):
        return r'\n'.join([str(t) for t in attributes])

    def qlsc2csv(self, qlsc_path, csv_path):
        with open(qlsc_path, 'r') as stream:
            code = yaml.full_load(stream)
            # include verif
            codif = code['Codification']
            with open(csv_path, 'w') as csv_file:
                csv_writer = csv.writer(csv_file, dialect='excel-tab')
                csv_writer.writerow(['code', 'source', 'pathname', 'dirname', 'basename', 'layername', 'internaltype', 'geometrytype', 'description', 'attributes'])
                for k in codif.keys():
                    codification = codif[k]
                    csv_writer.writerow([k, codification['Layer'], *(self.__explodeSource(codification['Layer'])), codification['GeometryType'], self.__geometryFromSource(codification['Layer']), codification['Description'], self.__attributesToString(codification['Attributes']) ] )


    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        self.addParameter(
            QgsProcessingParameterFile(
                self.QLSC,
                self.tr('QLSC file'),
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

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        qlscfile = self.parameterAsFile(parameters, self.QLSC, context)
        csvfile = self.parameterAsFile(parameters, self.OUTPUT, context)

        self.qlsc2csv(qlscfile, csvfile)
        
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
        return 'Convert QLSC file to CSV file'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

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
        return self.tr('Land survey')

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return landsurveyQLSC2CSV()
