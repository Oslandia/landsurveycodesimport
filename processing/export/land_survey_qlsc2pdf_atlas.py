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
import copy

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtXml import QDomDocument
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingMultiStepFeedback,
                       QgsProcessingParameterString,
                       QgsProcessingParameterBoolean,
                       QgsProject,
                       QgsLayoutExporter,
                       QgsPrintLayout,
                       QgsVectorLayer,
                       QgsReadWriteContext,
                       Qgis)
from qgis.gui import QgsMessageBar
from qgis.utils import iface


class landsurveyQLSC2PDF(QgsProcessingAlgorithm):
    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        self.addParameter(QgsProcessingParameterFile('qlsc', self.tr('Codification file'),
                          behavior=QgsProcessingParameterFile.File, extension='qlsc', defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('layout', self.tr(
            'Template layout'), behavior=QgsProcessingParameterFile.File, extension='qpt', defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('atlas', self.tr('Export the layout as an atlas?'), defaultValue=False))
        self.addParameter(QgsProcessingParameterFile('logo', self.tr('Logo'), behavior=QgsProcessingParameterFile.File, extension='svg', defaultValue=None, optional=True))
        self.addParameter(QgsProcessingParameterFileDestination(
            'outputpdf', self.tr('Output PDF'), fileFilter='.pdf', defaultValue=None))

    def generatePDF(self, csv_path, layout_path, logo_path, report_path, isAtlas):
        project = QgsProject.instance()

        uri = "file://" + csv_path + "?type=csv&delimiter=%5Ct&detectTypes=yes&geomType=none&subsetIndex=no&watchFile=yes"
        vl = QgsVectorLayer(uri, "codification", "delimitedtext")

        project.addMapLayer(vl)

        composition = QgsPrintLayout(project)
        document = QDomDocument()

        # read template content
        template_file = open(layout_path)
        template_content = template_file.read()
        template_file.close()
        document.setContent(template_content)

        # load layout from template and add to Layout Manager
        elem, ret = composition.loadFromTemplate(document, QgsReadWriteContext())
        try:
            idx = [e.id() for e in elem].index('logo')
            elem[idx].setPicturePath(logo_path)
        except:
            print("no logo")

        project.layoutManager().addLayout(composition)
        layout = project.layoutManager().layouts()[0]

        exporter = QgsLayoutExporter(layout)

        ret = None
        if isAtlas:
            atlas = layout.atlas()
            atlas.setCoverageLayer(vl)
            ret = exporter.exportToPdf(atlas, report_path, QgsLayoutExporter.PdfExportSettings())
        else:
            try:
                idx = [e.id() for e in elem].index('dataframe')
                elem[idx].multiFrame().setVectorLayer(vl)

                idx = [e.id() for e in elem].index('html')
                source = elem[idx].multiFrame().html()
                elem[idx].multiFrame().setHtml(source.replace('codification_8b7feba4_2907_46ca_a5fb_a51daad66b27', vl.id()))
                elem[idx].multiFrame().refresh()
            except Exception as e:
                print(e)
                return (False, str(e))
            ret = exporter.exportToPdf(report_path, QgsLayoutExporter.PdfExportSettings())

        return ret

    def processAlgorithm(self, parameters, context, ofeedback):
        """
        Here is where the processing itself takes place.
        """
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        results=dict()
        results['QLSC']=parameters['qlsc']
        results['OUTPUT']=''
        outputs={}

        # Algorithm will open a new project, some verifications:
        if QgsProject.instance().isDirty():
            iface.messageBar().pushMessage(self.tr("Unsaved project:"), self.tr(
                "Save your works before run this algorithm"), level=Qgis.Critical)
            return results

        actualProject=QgsProject.instance().absoluteFilePath()

        feedback=QgsProcessingMultiStepFeedback(2, ofeedback)

        ret = []
        with tempfile.TemporaryDirectory() as tmpdirname:
            csv_path=os.path.join(tmpdirname, 'codification.csv')

            alg_params={
                'QLSC': parameters['qlsc'],
                'OUTPUT': csv_path,
                'source': False,
                'pathname': False,
                'dirname': False,
                'basename': True,
                'layername': True,
                'internaltype': False,
                'displaytype': True,
                'geometrytype': True,
                'description': True,
                'attributes': False
            }
            outputs['ConvertQlscFileToCsvFile']=processing.run(
                'landsurvey:qlsc2csv', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

            feedback.setCurrentStep(1)
            if feedback.isCanceled():
                return {}

            ret=self.generatePDF(
                csv_path, parameters['layout'], parameters['logo'], parameters['outputpdf'], parameters['atlas'])

        if actualProject != '':
            QgsProject.instance().read(actualProject)
        else:
            QgsProject.instance().clear()

        # Atlas return a tuple
        msg = ""
        if isinstance(ret, tuple):
            ret, msg = ret

        print(ret, type(ret))
        if ret == QgsLayoutExporter.Success:
            results['OUTPUT']=parameters['outputpdf']
        else:
            iface.messageBar().pushMessage(
                    self.tr("Cannot print layout: {}".format(msg)), level=Qgis.Critical)

        return results

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
