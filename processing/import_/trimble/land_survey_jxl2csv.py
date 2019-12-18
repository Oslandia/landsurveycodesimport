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

from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterBoolean)

from .jxl2csv import jxl2csv

class landsurveyJXL2CSV(QgsProcessingAlgorithm):
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

    JXL = 'JXL'
    OUTPUT = 'OUTPUT'
    ISREDUCTION = 'ISREDUCTION'
    EXPORTDELETED = 'EXPORTDELETED'

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        self.addParameter(
            QgsProcessingParameterFile(
                self.JXL,
                self.tr('JXL file'),
                extension='jxl'
            )
        )


        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                self.tr('Output CSV'),
                fileFilter='csv'
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ISREDUCTION,
                self.tr('Use only Reductions fields?'),
                True
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.EXPORTDELETED,
                self.tr('Export also deleted points (only available when Reductions is false'),
                False
            )
        )
    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        jxlfile = self.parameterAsFile(parameters, self.JXL, context)
        csvfile = self.parameterAsFile(parameters, self.OUTPUT, context)
        isreduction = self.parameterAsBoolean(parameters, self.ISREDUCTION, context)
        exportdeleted = self.parameterAsBoolean(parameters, self.EXPORTDELETED, context)

        jxl2csv(jxlfile, csvfile, isreduction, exportdeleted)

        ret = dict()
        ret['OUTPUT'] = csvfile
        ret['JXL'] = jxlfile
        return ret

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'jxl2csv'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Convert Trimble JobXML file to CSV file')

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
        return self.tr('Import')

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return landsurveyJXL2CSV()
