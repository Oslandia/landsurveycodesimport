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

import shutil
import os
import tempfile
import processing

from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingMultiStepFeedback,
                       QgsProcessingParameterEnum,
                       QgsProject,
                       QgsLayoutExporter,
                       Qgis)
from qgis.gui import QgsMessageBar
from qgis.utils import iface

class landsurveyQLSC2PDF(QgsProcessingAlgorithm):
    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        self.addParameter(QgsProcessingParameterFile('qlsc', 'qlsc', behavior=QgsProcessingParameterFile.File, extension='qlsc', defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('project', 'project', behavior=QgsProcessingParameterFile.File, extension='qgz', defaultValue=None))
        self.addParameter(QgsProcessingParameterFileDestination('outputpdf', 'output_pdf', fileFilter='.pdf', defaultValue=None))
        self.options=['detailed','simple']
        self.addParameter(QgsProcessingParameterEnum('layout', 'layout', self.options, allowMultiple=False, defaultValue=1))

    def generatePDF(self, project_path, layout_name, report_path):
        if not QgsProject.instance().read(project_path):
            return (False, self.tr("Cannot open the file '{}'".format(project_path)))

        layout = QgsProject.instance().layoutManager().layoutByName(
            layout_name)
        if not layout:
            return (False, self.tr("Cannot find layout '{}'".format(layout_name)))

        exporter = QgsLayoutExporter(layout)
        res = exporter.exportToPdf(report_path,
                                   QgsLayoutExporter.PdfExportSettings())
        if res != QgsLayoutExporter.Success:
            
            return (False, self.tr("Cannot export to pdf"))

        return (True,)


    def processAlgorithm(self, parameters, context, ofeedback):
        """
        Here is where the processing itself takes place.
        """
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        ret = dict()
        ret['QLSC'] = parameters['qlsc']
        ret['OUTPUT'] = ''

        # Algorithm will open a new project, some verifications:
        if QgsProject.instance().isDirty():
            iface.messageBar().pushMessage(self.tr("Unsaved project:"), self.tr("Save your works before run this algorithm"), level = Qgis.Critical)
            return ret

        actualProject = QgsProject.instance().absoluteFilePath()

        feedback = QgsProcessingMultiStepFeedback(2, ofeedback)
        results = {}
        outputs = {}
        
        with tempfile.TemporaryDirectory() as tmpdirname:
           
            project_path =os.path.join(tmpdirname, 'project.qgz') 
            csv_path =os.path.join(tmpdirname, 'codification.csv') 
            shutil.copyfile(parameters['project'], project_path)
            shutil.copyfile(os.path.join(os.path.dirname(parameters['project']), 'logo.svg'), os.path.join(tmpdirname, 'logo.svg'))
            
            alg_params = {
                'QLSC': parameters['qlsc'],
                'OUTPUT': csv_path
            }
            outputs['ConvertQlscFileToCsvFile'] = processing.run('landsurvey:qlsc2csv', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

            feedback.setCurrentStep(1)
            if feedback.isCanceled():
                return {}

            r = self.generatePDF(project_path, self.options[parameters['layout']], parameters['outputpdf'])
       
        if actualProject != '':
            QgsProject.instance().read(actualProject)
        else:
            QgsProject.instance().clear()

        if r[0]:
            ret['OUTPUT'] = parameters['outputpdf']
        else:
            iface.messageBar().pushMessage(self.tr("Cannot print layout"), r[1], level = Qgis.Critical)
        
        return ret

    def flags(self):
        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'qlsc2pdf'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Convert QLSC file to PDF file')

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
        return landsurveyQLSC2PDF()
