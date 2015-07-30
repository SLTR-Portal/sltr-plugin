# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SolaPlugin
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
from PyQt4.QtCore import *  # QSettings, QTranslator, qVersion, QCoreApplication, QFileInfo, QVariant
from PyQt4.QtGui import *  #QAction, QIcon, QMessageBox

from qgis.core import QgsDataSourceURI, QgsRasterLayer, QgsMapLayerRegistry, QgsVectorDataProvider, QgsFeatureRequest
from qgis.gui import QgsMessageBar
# Initialize Qt resources from file resources.py
# Import the code for the dialog
from login_dialog import LoginDialog
from sola_dialog import SolaPluginDialog
from customform import CreateFormDialog
import os.path
import sys
from PyQt4.QtSql import *
# from datetime import datetime


class SolaPlugin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        if not sys.path.__contains__(self.plugin_dir): sys.path.append(self.plugin_dir)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SolaPlugin_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = LoginDialog()
        self.dlg2 = SolaPluginDialog()
        self.dlg3 = CreateFormDialog()

        # Declare instance attributes
        self.actions = []
        self.fid_array = []
        self.user = ''
        self.fid = 0
        self.parcel_id = ''
        self.transactionId = ''
        self.db_hostName='localhost'
        self.db_databaseName='sola'
        self.db_UserName='postgres'
        self.db_password = 'admin1'
        self.db_Port=5432
        self.menu = self.tr(u'&SLTRPlugin')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'SLTRPlugin')
        self.toolbar.setObjectName(u'SLTRPlugin')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SLTRPlugin', message)


    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = ':/plugins/SolaPlugin/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'SLTR'),
            callback=self.run,
            parent=self.iface.mainWindow())
        # self.toolbar = self.iface.addToolBar("SLTRToolBar")

        # Create actions


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&SLTRPlugin'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            # Capture Login Details
            print self.dlg.userNameBox.text()
            print self.dlg.pswdBox.text()
            # Check User namer and password
            username = self.dlg.userNameBox.text()
            password = self.dlg.pswdBox.text()
            if self.authUser(username, password) == True:
                self.user = username
                self.iface.messageBar().pushMessage("Success",
                                                    "Login Successful! Welcome " + self.dlg.userNameBox.text(),
                                                    level=QgsMessageBar.INFO, duration=3)
                self.transactionId = self.getTransactionId()
                self.createLGALayer()
                self.createRasterLayer()
                self.createWardLayer()
                self.createSectionLayer()
                self.createBlockLayer()
                self.createParcelLayer()
                layer = self.iface.activeLayer()
                canvas = self.iface.mapCanvas()
                extent = layer.extent()
                canvas.setExtent(extent)
                self.dlg.close()
            else:
                self.iface.messageBar().pushMessage("Error", "Your Login attempt was unsuccessful. Please try again",
                                                    level=QgsMessageBar.CRITICAL, duration=5)
                self.run()
                # tryout

                # END TRY'''

    def captureFeatures(self, fid):
        print 'Feature Added'
        print fid
        if fid in self.fid_array:
            print "I saw it there!!"
            pass
        else:
            self.fid = fid
            self.fid_array.append(fid)
            self.initDialog()


    def startEdit(self):
        print 'Edit started'

    def finishEdit(self):
        print 'Yes boss!'
        # self.initDialog()
        layer = self.iface.activeLayer()
        self.initDialog('')

    def initDialog(self, error=''):
        if error != '':
            self.dlg2.error_label.setText(error)
        self.dlg2.show()
        result = self.dlg2.exec_()
        layer = self.iface.activeLayer()
        if result:
            if self.checkParcelNumberExists(self.dlg2.parcel_id.text()):
                self.parcel_id = self.dlg2.parcel_id.text()
                if self.checkParcelExistsAlready(self.parcel_id) == False:
                    # self.dlg2.parcel_id.setText('')
                    layer.featureAdded.disconnect(self.captureFeatures)
                    self.saveEdit(self.parcel_id)
                    layer.featureAdded.connect(self.captureFeatures)
                else:
                    # layer.deleteFeature(fid)
                    # self.resetFid()
                    # layer.commitChanges()
                    # layer.startEditing()
                    self.initDialog('Parcel Number already exists! Please check and try again')
            else:

                # self.resetFid()
                # layer.commitChanges()
                # layer.startEditing()
                self.initDialog('The Parcel Number doesn''t exist for the generated forms. Please try again')
        else:
            layer.deleteFeature(self.fid)
            layer.commitChanges()
            layer.startEditing()
        self.dlg2.parcel_id.setText('')

    def createParcelLayer(self):
        uri = QgsDataSourceURI()
        uri.setConnection(self.db_hostName, str(self.db_Port), self.db_databaseName, self.db_UserName, self.db_password)
        uri.setDataSource("cadastre", "cadastre_object", "geom_polygon")
        uri.uri()
        print uri.uri()

        rlayer = self.iface.addVectorLayer(uri.uri(), "Parcels", "postgres")
        self.iface.setActiveLayer(rlayer)

        rlayer.loadNamedStyle(self.plugin_dir + '/style.qml')
        #rlayer.layerModified.connect(self.captureFeatures)
        rlayer.featureAdded.connect(self.captureFeatures)
        rlayer.setEditForm(self.plugin_dir + os.sep + 'createForm.ui')
        #rlayer.setEditFormInit('.CreateFormDialog.formOpen')
        rlayer.startEditing()

    def createWardLayer(self):
        uri = QgsDataSourceURI()
        uri.setConnection(self.db_hostName, str(self.db_Port), self.db_databaseName, self.db_UserName, self.db_password)
        uri.setDataSource("cadastre", "spatial_unit_group", "geom", "hierarchy_level=3")
        uri.uri()
        print uri.uri()
        rlayer = self.iface.addVectorLayer(uri.uri(), "Ward", "postgres")
        rlayer.loadNamedStyle(self.plugin_dir + '/ward.qml')

    def createLGALayer(self):
        uri = QgsDataSourceURI()
        uri.setConnection(self.db_hostName, str(self.db_Port), self.db_databaseName, self.db_UserName, self.db_password)
        uri.setDataSource("cadastre", "spatial_unit_group", "geom", "hierarchy_level=2")
        uri.uri()
        print uri.uri()
        rlayer = self.iface.addVectorLayer(uri.uri(), "LGA", "postgres")
        rlayer.loadNamedStyle(self.plugin_dir + '/lga.qml')

    def createRasterLayer(self):
        urlWithParams = 'url=http://localhost:8085/geoserver/calabar/wms?service=WMS&version=1.1.0&request=GetMap&layers=Calabar_20Dec2013_50cm_Colr2&styles=&srs=EPSG:4326&format=image/jpeg'
        rlayer = QgsRasterLayer(urlWithParams, 'Orthophoto', 'wms')
        QgsMapLayerRegistry.instance().addMapLayer(rlayer)
        # urlWithParams = 'url=http://localhost:8085/geoserver/lokoja/wms?service=WMS&version=1.1.0&request=GetMap&layers=Lokoja_Mos_Nov2011_50cm_Color&styles=&crs=EPSG:32632&format=image/png'
        # rlayer = QgsRasterLayer(urlWithParams, 'Orthophoto', 'wms')
        # QgsMapLayerRegistry.instance().addMapLayer(rlayer)

    def createSectionLayer(self):
        uri = QgsDataSourceURI()
        uri.setConnection(self.db_hostName, str(self.db_Port), self.db_databaseName, self.db_UserName, self.db_password)
        uri.setDataSource("cadastre", "spatial_unit_group", "geom", "hierarchy_level=4")
        uri.uri()
        print uri.uri()
        rlayer = self.iface.addVectorLayer(uri.uri(), "Section", "postgres")
        rlayer.loadNamedStyle(self.plugin_dir + '/lga.qml')

    def createBlockLayer(self):
        uri = QgsDataSourceURI()
        uri.setConnection(self.db_hostName, str(self.db_Port), self.db_databaseName, self.db_UserName, self.db_password)
        uri.setDataSource("cadastre", "spatial_unit_group", "geom", "hierarchy_level=5")
        uri.uri()
        print uri.uri()
        rlayer = self.iface.addVectorLayer(uri.uri(), "Blocks", "postgres")
        rlayer.loadNamedStyle(self.plugin_dir + '/lga.qml')

    def authUser(self, username, pswd):
        db = QSqlDatabase('QPSQL')
        if db.isValid():
            db.setHostName(self.db_hostName)
            # string
            db.setDatabaseName(self.db_databaseName)
            # string
            db.setUserName(self.db_UserName)
            # string
            db.setPassword(self.db_password)
            # integer e.g. 5432
            db.setPort(self.db_Port)
            if db.open():
                # assume you have a table called 'appuser'
                query = db.exec_("select * from system.appuser where username='" + username + "'")
                # No password implementations yet
                # iterate over the rows
                if query.size() == 1:
                    return True
                else:
                    return False

        pass

    def saveEdit(self, values):

        layer = self.iface.activeLayer()
        fid = self.fid
        print fid
        # print feature.id()
        # print feature.geometry()
        # dataProvider=layer.dataProvider()
        caps = layer.dataProvider().capabilities()
        if caps & QgsVectorDataProvider.AddAttributes:
            feature = layer.getFeatures(QgsFeatureRequest(fid)).next()
            # transaction_id=self.getTransactionId()
            # check that the specified parcel number exists
            print self.transactionId
            print values
            if self.checkParcelExistsAlready(values) == False:
                name_lastpart=self.getNameLastPart(feature.geometry().exportToWkt())
                layer.changeAttributeValue(fid, feature.fieldNameIndex('id'), self.getUUID())
                layer.changeAttributeValue(fid, feature.fieldNameIndex('type_code'), 'parcel')
                layer.changeAttributeValue(fid, feature.fieldNameIndex('source_reference'), values)
                layer.changeAttributeValue(fid, feature.fieldNameIndex('name_firstpart'), values)
                layer.changeAttributeValue(fid, feature.fieldNameIndex('name_lastpart'), name_lastpart)
                layer.changeAttributeValue(fid, feature.fieldNameIndex('status_code'), 'pending')
                layer.changeAttributeValue(fid, feature.fieldNameIndex('change_action'), 'i')
                layer.changeAttributeValue(fid, feature.fieldNameIndex('change_user'), self.user)
                layer.changeAttributeValue(fid, feature.fieldNameIndex('transaction_id'), self.transactionId)
                layer.changeAttributeValue(fid, feature.fieldNameIndex('land_use_code'), 'residential')
                layer.changeAttributeValue(fid, feature.fieldNameIndex('view_id'), 1)
                #self.fid_array.append(fid)
                # feat.setGeometry()
                (res, outFeat) = layer.dataProvider().addFeatures([feature])
                layer.commitChanges()
                layer.startEditing()
                print res
            else:
                self.initDialog('An error has occurred. Duplicate Parcel Number. Please check and try again')


        pass

    def checkParcelNumberExists(self, parcelNumber):
        # Check the forms table to verify the existence of the parcel number in the form table
        db = QSqlDatabase('QPSQL')
        if db.isValid():
            db.setHostName(self.db_hostName)
            # string
            db.setDatabaseName(self.db_databaseName)
            # string
            db.setUserName(self.db_UserName)
            # string
            db.setPassword(self.db_password)
            # integer e.g. 5432
            db.setPort(self.db_Port)
            if db.open():
                # assume you have a table called 'appuser'
                query = db.exec_("select nr from public.form where nr='" + parcelNumber + "'")
                #
                # iterate over the rows to see if there is only one record and it exists
                if query.size() == 1:
                    return True
                else:
                    return False
        pass

    # Implementation to standardize db calls
    def checkParcelExistsAlready(self, parcelNumber):
        db = QSqlDatabase('QPSQL')
        if db.isValid():
            db.setHostName(self.db_hostName)
            # string
            db.setDatabaseName(self.db_databaseName)
            # string
            db.setUserName(self.db_UserName)
            # string
            db.setPassword(self.db_password)
            # integer e.g. 5432
            db.setPort(self.db_Port)
            if db.open():
                query = db.exec_(
                    "select name_firstpart from cadastre.cadastre_object where name_firstpart='" + parcelNumber + "'")
                #
                # iterate over the rows to see if there is only one record and it exists
                if query.size() > 1:
                    return True
                else:
                    return False
        pass

    def getTransactionId(self):
        # return '010656ad-1725-41e6-b172-064e9b89b323'
        # Essentially create a transaction ID in code, insert the transaction entry and store in the session variable
        did = str(self.getUUID())
        db = QSqlDatabase('QPSQL')
        if db.isValid():
            db.setHostName(self.db_hostName)
            # string
            db.setDatabaseName(self.db_databaseName)
            # string
            db.setUserName(self.db_UserName)
            # string
            db.setPassword(self.db_password)
            # integer e.g. 5432
            db.setPort(self.db_Port)
            if db.open():
                # assume you have a table called 'appuser'
                query = db.exec_("insert into transaction.transaction(id,change_action,change_user) VALUES('" + did + "','i','" + self.user + "')")
                # iterate over the rows
                #if query.size() == 1:
                #self.transactionId = did
                print did
                return did
                # else:
                #     self.iface.messageBar().pushMessage("Error",
                #                                         "An error has occurred. Please notify the administrator",
                #                                         level=QgsMessageBar.CRITICAL, duration=5)

    def getUUID(self):
        db = QSqlDatabase('QPSQL')
        if db.isValid():
            db.setHostName(self.db_hostName)
            # string
            db.setDatabaseName(self.db_databaseName)
            # string
            db.setUserName(self.db_UserName)
            # string
            db.setPassword(self.db_password)
            # integer e.g. 5432
            db.setPort(self.db_Port)
            if db.open():
                # assume you have a table called 'appuser'
                query = db.exec_("select uuid_generate_v1()")
                # iterate over the rows
                if query.size() == 1:
                    query.next()
                    return str(query.value(0))
                else:
                    return False

        pass

    def getNameLastPart(self, geom):
        db = QSqlDatabase('QPSQL')

        if db.isValid():
            db.setHostName(self.db_hostName)
            # string
            db.setDatabaseName(self.db_databaseName)
            # string
            db.setUserName(self.db_UserName)
            # string
            db.setPassword(self.db_password)
            # integer e.g. 5432
            db.setPort(self.db_Port)
            if db.open():
                print str(geom)
                query=db.exec_("select cadastre.get_new_cadastre_object_identifier_last_part((SELECT ST_PolygonFromText(('"+str(geom)+"'),32632)),'value')")
                if query.size()==1:
                    query.next()
                    print str(query.value(0))
                    return str(query.value(0))
                else:
                    return ''
            pass
        pass

    def checkOverlaps(self):
        pass

    def resetFid(self):
        self.fid = 0

        # def formOpen(self,layerid,featureid):
        # # global myDialog
        #     #myDialog = dialog
        #     # global nameField
        #     nameField = self.dlg3.findChild(QLineEdit,"name_firstpart")
        #     buttonBox = self.dlg3.findChild(QDialogButtonBox,"buttonBox")
        #
        #     # Disconnect the signal that QGIS has wired up for the dialog to the button box.
        #     buttonBox.accepted.disconnect(self.dlg3.accept)
        #
        #     # Wire up our own signals.
        #     buttonBox.accepted.connect(self.validate)
        #     buttonBox.rejected.connect(self.dlg3.reject)
        #
        # def validate(self):
        #   # Make sure that the name field isn't empty.
        #     if not len(self.dlg3.name_first_part.text()) > 0:
        #         msgBox = QMessageBox()
        #         msgBox.setText("Parcel Number can not be null.")
        #         msgBox.exec_()
        #     else:
        #         # Return the form as expected to QGIS.
        #         self.dlg3.accept()
