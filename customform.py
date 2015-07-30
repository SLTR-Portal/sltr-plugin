__author__ = 'Samuel'
# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Sola Login Dialog
                                 A QGIS plugin
 This plugin extends SOLA's functionality using QGIS
                             -------------------
        begin                : 2015-04-20
        git sha              : $Format:%H$
        copyright            : (C) 2015 by SOLA
        email                : samuel.okoroafor@gems3nigeria.com
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
# from PyQt4.QtCore import *
# from PyQt4.QtGui import *
import os

from PyQt4 import QtGui, uic


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'createForm.ui'))


class CreateFormDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(CreateFormDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        # nameField = None
        # myDialog = None
        #
        # def formOpen(dialog,layerid,featureid):
        # global myDialog
        #     myDialog = dialog
        #     global nameField
        #     nameField = dialog.findChild(QLineEdit,"name_firstpart")
        #     buttonBox = dialog.findChild(QDialogButtonBox,"buttonBox")
        #
        #     # Disconnect the signal that QGIS has wired up for the dialog to the button box.
        #     buttonBox.accepted.disconnect(myDialog.accept)
        #     print 'Isong!'
        #     # Wire up our own signals.
        #     buttonBox.accepted.connect(validate)
        #     buttonBox.rejected.connect(myDialog.reject)
        #
        # def validate():
        #   # Make sure that the name field isn't empty.
        #     if not len(nameField.text()) > 0:
        #         msgBox = QMessageBox()
        #         msgBox.setText("Name field can not be null.")
        #         msgBox.exec_()
        #     else:
        #         # Return the form as accpeted to QGIS.
        #         myDialog.accept()