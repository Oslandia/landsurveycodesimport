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
__date__ = '2018-04-05'
__copyright__ = '(C) 2018 by Loïc Bartoletti'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFile)

from .land_survey_field_codes_import import landsurveyImport 

class landsurveyAlgorithm(QgsProcessingAlgorithm):
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
    INPUT = 'INPUT'

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT,
                self.tr('Input CSV'),
                extension='csv'
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFile(
                self.QLSC,
                self.tr('QLSC file'),
                extension='qlsc'
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsFile(parameters, self.INPUT, context)
        qlscfile = self.parameterAsFile(parameters, self.QLSC, context)

        # with open('/home/lbartoletti/qsdf.qlsc', 'w') as f:
        #    f.write(source)
        #    f.write(qlscfile)
        landsurveyImport(source, qlscfile)
        #(sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT,
        #        context, source.fields(), source.wkbType(), source.sourceCrs())

        # Compute the number of steps to display within the progress bar and
        # get features from source
        #total = 100.0 / source.featureCount() if source.featureCount() else 0
        #features = source.getFeatures()

        #for current, feature in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
        #    if feedback.isCanceled():
        #        break

            # Add a feature in the sink
        #    sink.addFeature(feature, QgsFeatureSink.FastInsert)

            # Update the progress bar
        #    feedback.setProgress(int(current * total))

        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output name 
        ret = dict()
        ret['INPUT'] = source
        ret['QLSC'] = qlscfile
        return ret #{self.OUTPUT: dest_id}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Import land survey fields'

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
        return landsurveyAlgorithm()
