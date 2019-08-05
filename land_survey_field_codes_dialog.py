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

from .land_survey_field_codes_available_code import AVAILABLE_CODE, translatedName

import os
from pathlib import Path

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import QDir, QCoreApplication
from qgis.core import QgsMapLayerProxyModel, QgsProject
from qgis.gui import QgsFieldExpressionWidget
import yaml

import sys
sys.path.append(os.path.dirname(__file__))

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'land_survey_field_codes_dialog_base.ui'),
    resource_suffix='')

WINDOWTITLE = 'Codification - '


def tr(message):
    return QCoreApplication.translate('LandSurveyFieldCodes', message)


class LayerError(Exception):
    """Exception raised for errors in the layer set in the combobox.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, box, message):
        self.box = box
        self.message = message


class LandSurveyFieldCodesDialog(QtWidgets.QMainWindow, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(LandSurveyFieldCodesDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.isSaved = True
        self.saveName = None
        self.savedCodes = dict()
        self.__new()

        for item in AVAILABLE_CODE:
            if item['available']:
                self.mGeometry.addItem(translatedName(item['name']), item)
                self.__geometryChanged()

        self.mLayerAllPoints.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.mLayerErrorPoints.setFilters(QgsMapLayerProxyModel.PointLayer)

        self.mAllPoints.stateChanged.connect(
            lambda: self.__specialPoints(self.mAllPoints,
                                         self.mGeoPackageAllPoints,
                                         self.mLayerAllPoints))
        self.mErrorPoints.stateChanged.connect(
            lambda: self.__specialPoints(self.mErrorPoints,
                                         self.mGeoPackageErrorPoints,
                                         self.mLayerErrorPoints))

        self.mComboCodeSeparator.currentIndexChanged.connect(
            lambda: self.__checkSeparator(self.mComboCodeSeparator,
                                          self.mComboParameterSeparator))
        self.mComboParameterSeparator.currentIndexChanged.connect(
            lambda: self.__checkSeparator(self.mComboParameterSeparator,
                                          self.mComboCodeSeparator))

        self.mGeoPackage.fileChanged.connect(lambda: self.__changedGeoPackage(
            self.mGeoPackage.filePath(), self.mLayerOutput))
        self.mGeoPackageAllPoints.fileChanged.connect(lambda: self.__changedGeoPackage(
            self.mGeoPackageAllPoints.filePath(), self.mLayerAllPoints))
        self.mGeoPackageErrorPoints.fileChanged.connect(lambda: self.__changedGeoPackage(
            self.mGeoPackageErrorPoints.filePath(), self.mLayerErrorPoints))

        self.mGeometry.currentIndexChanged.connect(self.__geometryChanged)
        self.mLayerOutput.currentIndexChanged.connect(self.__emptyRow)

        self.mAddColumnPushButton.clicked.connect(self.__addRow)
        self.mRemoveColumnPushButton.clicked.connect(self.__removeRow)
        self.mEmptyColumnsPushButton.clicked.connect(self.__emptyRow)
        self.mSaveCode.clicked.connect(self.__saveCode)
        self.mDeleteCode.clicked.connect(self.__delCode)
        self.mComboCode.editTextChanged.connect(self.__codeChanged)
        self.mComboCode.currentIndexChanged.connect(self.__codeChanged)

        self.actionClose.triggered.connect(
            self.close)
        self.action_New.triggered.connect(
            self.__new)
        self.action_Save.triggered.connect(
            self.__saveCodificationFile)
        self.actionSaveAs.triggered.connect(
            lambda: self.__saveCodificationFileAs(
                QtWidgets.QFileDialog.getSaveFileName(
                    None, tr("Save File"),
                    QDir.homePath(),
                    "Qgis LandSurvey Code Config (*.qlsc)")))

        self.action_Open.triggered.connect(self.__openCodification)

        self.__changedGeoPackage('', self.mLayerOutput)
        self.__changedGeoPackage('', self.mLayerAllPoints)
        self.__changedGeoPackage('', self.mLayerErrorPoints)

    def __testLayer(self, layer):
        """
        Convenient method to return the source of a layer into a combobox
        or an empty string.
        """
        try:
            testedLayer = layer.currentLayer()
            testedLayer_source = testedLayer.publicSource()
        except:
            testedLayer_source = ''

        return testedLayer_source

    def __new(self):
        """
        Create a new empty Codification's table.
        """
        if self.__confirmClose():
            self.mErrorPoints.setChecked(False)
            self.mAllPoints.setChecked(False)
            self.__cleanCodification()
            self.mDescription.clear()
            self.mComboCode.clear()
            self.mGeometry.setCurrentIndex(0)
            self.mGeoPackage.setFilePath('')
            self.__changedGeoPackage('', self.mLayerOutput)
            self.mGeoPackageAllPoints.setFilePath('')
            self.__changedGeoPackage('', self.mLayerAllPoints)
            self.mGeoPackageErrorPoints.setFilePath('')
            self.__changedGeoPackage('', self.mLayerErrorPoints)
            self.mComboCodeSeparator.setCurrentIndex(0)
            self.mComboParameterSeparator.setCurrentIndex(1)
            self.savedCodes.clear()
            self.isSaved = True
            self.saveName = None
            self.setWindowTitle(WINDOWTITLE + tr('New codification'))
            return True
        return False

    def __confirmClose(self):
        """
        Checks if you really want to close the current table edition.
        """
        if self.isSaved:
            return True

        choice = QtWidgets.QMessageBox.question(
            self,
            tr('Save the project?'),
            tr("Do you want to save the project?"),
            QtWidgets.QMessageBox.Yes |
            QtWidgets.QMessageBox.No |
            QtWidgets.QMessageBox.Cancel)
        if choice == QtWidgets.QMessageBox.Yes:
            self.__saveCodificationFile()
        elif choice == QtWidgets.QMessageBox.Cancel:
            return False

        return True

    def __openCodification(self):
        """
        Open a codification's table.
        """
        if not self.__new():
            return

        codification = QtWidgets.QFileDialog.getOpenFileName(
            None, tr("Open File"),
            QDir.homePath(),
            "Qgis LandSurvey Code Config (*.qlsc)")

        saveName = codification[0]

        if not Path(saveName).is_file():
            # TODO: erreur
            print('erreur open codification')
            return
        try:
            with open(saveName, 'r') as stream:
                code = yaml.load(stream)
        except:
            QtWidgets.QMessageBox.warning(
                self,
                tr('Error opening the file'),
                tr("Can't open the file {}".format(saveName)))
            return

        try:
            checked = code['AllPoints']['isChecked']
            self.mAllPoints.setChecked(checked)
            if checked:
                try:
                    layerAllPoints = self.__getPath(code['AllPoints']['Layer'])
                    self.mGeoPackageAllPoints.setFilePath(layerAllPoints)
                    self.__changedGeoPackage(
                        layerAllPoints, self.mLayerAllPoints)

                    layers = self.__getLayersFromProject()
                    sources = [s.publicSource() for
                               s in layers]
                    index = sources.index(code['AllPoints']['Layer'])
                    self.mLayerAllPoints.setCurrentText(layers[index].name())

                except LayerError as err:
                    print(err)
                    self.mAllPoints.setChecked(False)

            checked = code['ErrorPoints']['isChecked']
            self.mErrorPoints.setChecked(checked)
            if checked:
                try:
                    layerErrorPoints = self.__getPath(
                        code['ErrorPoints']['Layer'])
                    self.mGeoPackageErrorPoints.setFilePath(layerErrorPoints)
                    self.__changedGeoPackage(
                        layerErrorPoints, self.mLayerErrorPoints)

                    layers = self.__getLayersFromProject()
                    sources = [s.publicSource() for
                               s in layers]
                    index = sources.index(code['ErrorPoints']['Layer'])
                    self.mLayerErrorPoints.setCurrentText(layers[index].name())

                except LayerError as err:
                    print(err)
                    self.mErrorPoints.setChecked(False)

            self.mComboParameterSeparator.setCurrentText(
                code['ParameterSeparator'])
            self.mComboCodeSeparator.setCurrentText(
                code['CodeSeparator'])

            savedCode = code['Codification']
            keysList = list(savedCode.keys())
            for i in keysList:
                if not all(x in ['Attributes', 'Description',
                                 'GeometryType', 'Layer']
                           for x in savedCode[i].keys()):
                    raise KeyError(i)
                    # TODO: check errors
                self.mComboCode.insertItem(0, i)

            self.savedCodes = savedCode

            if len(keysList) > 0:
                self.__codeChanged(i)

            self.isSaved = True
            self.saveName = saveName

            self.setWindowTitle(
                WINDOWTITLE +
                os.path.splitext(os.path.basename(saveName))[0])

            self.mComboCode.setCurrentIndex(0)
            self.__codeChanged(self.mComboCode.currentText())

        except KeyError as err:
            print("clef non trouvée", err)
        except LayerError as err:
            print(err)

    def __saveFile(self, saveName):
        """
        Save the codification's table into the file saveName.
        """
        parameters = {'CodeSeparator':
                      self.mComboCodeSeparator.currentText(),
                      'ParameterSeparator':
                      self.mComboParameterSeparator.currentText(),
                      'AllPoints': {
                          'isChecked':
                          self.mAllPoints.isChecked(),
                          'Layer':
                          self.__testLayer(self.mLayerAllPoints) if
                          self.mAllPoints.isChecked() else ''},
                      'ErrorPoints': {
                          'isChecked':
                          self.mErrorPoints.isChecked(),
                          'Layer':
                          self.__testLayer(self.mLayerErrorPoints) if
                          self.mErrorPoints.isChecked() else ''},
                      'Codification': self.savedCodes}

        try:
            with open(saveName, 'w') as stream:
                yaml.dump(parameters, stream)

            self.isSaved = True
            self.saveName = saveName

            self.setWindowTitle(
                WINDOWTITLE +
                os.path.splitext(os.path.basename(saveName))[0])
        except:
            QtWidgets.QMessageBox.warning(
                self,
                tr('Error saving the file'),
                tr("Can't save the file {}".format(saveName)))

    def __saveCodificationFile(self):
        """
        When the codification's table is opened, save in its filename.
        """
        if self.saveName is None:
            self.__saveCodificationFileAs(
                QtWidgets.QFileDialog.getSaveFileName(
                    None, tr("Save File"),
                    QDir.homePath(),
                    "Qgis LandSurvey Code Config (*.qlsc)"))
        else:
            self.__saveFile(self.saveName)

    def __saveCodificationFileAs(self, codificationFile):
        """
        Save the codification's table as a new file.
        """
        self.__saveFile(codificationFile[0])

    def __changeTitle(self):
        """
        Method used whenever a change is made to the codification's table.
        """
        if self.windowTitle()[-1] != '*':
            self.setWindowTitle(self.windowTitle() + '*')
        self.isSaved = False

    def __checkSeparator(self, comboChanged, otherCombo):
        """
        Code and parameter separators can't be the same.
        So, if their comboboxes have the same index,
        the index of the last modified combobox will be increased.
        The behavior of a combobox is like a circular array.
        """
        curInd = comboChanged.currentIndex()
        if curInd == otherCombo.currentIndex():
            if comboChanged.count() == curInd + 1:
                curInd = -1
            comboChanged.setCurrentIndex(curInd + 1)
        self.__changeTitle()

    def __getLayersFromProject(self):
        """
        Convenient method to return layers from the project
        """
        return list(QgsProject().instance().mapLayers().values())

    def __changedGeoPackage(self, gpkg, comboLayers):
        """
        The codification's table accepts multiple geopackage.
        If the geopackage line is modified, it updates available output layers.
        """
        if os.access(gpkg, os.W_OK):
            layers = self.__getLayersFromProject()
            exclude = [s for s in layers if
                       self.__getPath(s.publicSource()) !=
                       gpkg.replace('\\', '/')]

            comboLayers.setExceptedLayerList(exclude)
            comboLayers.setEnabled(True)
            comboLayers.setCurrentIndex(0)
            self.__checkIfYouCanEnable()
        else:
            comboLayers.setCurrentIndex(-1)
            comboLayers.setEnabled(False)

    def __checkIfYouCanEnable(self):
        """
        Only enable some widgets when the output layers and
        name of codification is correct.
        """
        enable = (self.mLayerOutput.count() > 0 and
                  len(self.mComboCode.currentText()) != 0)
        self.mSaveCode.setEnabled(enable)
        self.mAddColumnPushButton.setEnabled(enable)

    def __getPath(self, sourceName):
        """
        Convenient method to return a PublicSource as a path.
        """
        return sourceName[:sourceName.find('|')]

    def __addRow(self):
        """
        Add a row for the fields
        """
        count = self.mTableWidget.rowCount()
        self.mTableWidget.insertRow(count)
        comboBox = QtWidgets.QComboBox()
        layer = self.mLayerOutput.currentLayer()
        comboBox.insertItems(0, [f.displayName() for f in layer.fields()])
        self.mTableWidget.setCellWidget(count, 0, comboBox)
        expr = QgsFieldExpressionWidget()
        expr.setLayer(layer)
        self.mTableWidget.setCellWidget(count, 1, expr)

    def __removeRow(self):
        """
        Remove a row
        """
        self.mTableWidget.removeRow(self.mTableWidget.currentRow())

    def __emptyRow(self):
        """
        Empty the fields table
        """
        self.mTableWidget.setRowCount(0)

    def __geometryChanged(self):
        """
        Update available output layers when a code is changed.
        """
        # Check why filter doesn't works directly
        # filter returns int and not filters type
        code = self.__getDataGeometry('code')
        idx = [c['code'] for c in AVAILABLE_CODE].index(code)
        filter = AVAILABLE_CODE[idx]['filter']
        self.mLayerOutput.setFilters(filter)

    def __specialPoints(self, check, gpkg, combo):
        """
        Enable layer combobox for a special point option.
        """
        gpkg.setEnabled(check.isChecked())
        self.__changedGeoPackage(gpkg.filePath(), combo)
        self.__changeTitle()

    def __getTableContents(self):
        """
        Convenient method to return the contents of the fields table.
        """
        contents = []
        for i in range(self.mTableWidget.rowCount()):
            contents.append((self.mTableWidget.cellWidget(i, 0).currentText(),
                             self.mTableWidget.cellWidget(i, 1).currentText()))
        return contents

    def __setTableContents(self, contents):
        """
        Convenient method to set the contents of the fields table.
        """
        self.__emptyRow()
        for i, c in enumerate(contents):
            self.__addRow()
            self.mTableWidget.cellWidget(i, 0).setCurrentText(c[0])
            self.mTableWidget.cellWidget(i, 1).setExpression(c[1])

    def __cleanCodification(self):
        """
        Convenient method called when a codification is saved or deleted.
        """
        self.mDescription.clear()
        self.mComboCode.setCurrentIndex(-1)
        self.__emptyRow()

    def __getDataGeometry(self, name):
        """
        Convenient method to return the data of the mGeometry combobox
        """
        return self.mGeometry.itemData(self.mGeometry.currentIndex())[name]

    def __saveCode(self):
        """
        Save the current codification into the dictionnary.
        """
        code = {
            'Description': self.mDescription.text(),
            'GeometryType': self.__getDataGeometry('code'),
            'Layer': self.__testLayer(self.mLayerOutput),
            'Attributes': self.__getTableContents()}
        self.savedCodes[self.mComboCode.currentText()] = code

        if self.mComboCode.findText(self.mComboCode.currentText()) == -1:
            self.mComboCode.insertItem(self.mComboCode.count(),
                                       self.mComboCode.currentText())
        self.__cleanCodification()
        self.__changeTitle()

    def __delCode(self):
        """
        Delete the current codification from the dictionnary.
        """
        if self.mComboCode.currentText() in self.savedCodes:
            del self.savedCodes[self.mComboCode.currentText()]
            index = self.mComboCode.findText(self.mComboCode.currentText())
            self.mComboCode.removeItem(index)
        self.__cleanCodification()
        self.__changeTitle()

    def __setGeoPackage(self, path):
        """
        Convenient method used when a name is changed to set the geopackage
        for the codification's name.
        """
        self.mGeoPackage.setFilePath(path)
        self.__changedGeoPackage(path, self.mLayerOutput)

    def __getIndexGeometryType(self, geometryType):
        """
        Convenient method to return the index of the geometryType in the combobox
        """
        for i in range(self.mGeometry.count()):
            if geometryType == self.mGeometry.itemData(i)['code']:
                return i

        return -1

    def __codeChanged(self, code):
        """
        Update the GUI when a name is changed.
        If it exists, sets the saved values.
        """
        self.__checkIfYouCanEnable()
        if code in self.savedCodes:
            code = self.savedCodes[code]
            try:
                layers = self.__getLayersFromProject()
                sources = [s.publicSource() for
                           s in layers]
                index = sources.index(code['Layer'])
                self.__setGeoPackage(self.__getPath(code['Layer']))
                self.mDescription.setText(code['Description'])
                self.mGeometry.setCurrentIndex(
                    self.__getIndexGeometryType(code['GeometryType']))
                self.mLayerOutput.setCurrentText(layers[index].name())
                self.__setTableContents(code['Attributes'])
            except ValueError:
                QtWidgets.QMessageBox.warning(
                    self,
                    tr('Error changing the code'),
                    tr("Can't change the code."))
