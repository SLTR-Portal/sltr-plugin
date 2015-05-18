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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication,QFileInfo, QVariant
from PyQt4.QtGui import QAction, QIcon, QMessageBox

from qgis.core import QgsDataSourceURI,QgsRasterLayer,QgsMapLayerRegistry,QgsMapRenderer,QgsFeature,QgsField,QgsVectorDataProvider,QgsFeatureRequest
from qgis.gui import QgsMessageBar
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from login_dialog import LoginDialog
from sola_dialog import SolaPluginDialog
import os.path
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

        # Declare instance attributes
        self.actions = []
        self.user=''
        self.fid=0
        self.parcel_id=''
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
            username=self.dlg.userNameBox.text()
            password=self.dlg.pswdBox.text()
            if self.authUser(username,password)==True:
                self.user=username
                self.iface.messageBar().pushMessage("Success", "Login Successful! Welcome "+self.dlg.userNameBox.text(), level=QgsMessageBar.INFO,duration=5)

                self.createLGALayer()
                self.createRasterLayer()
                self.createWardLayer()
                self.createParcelLayer()
                layer=self.iface.activeLayer()
                canvas=self.iface.mapCanvas()
                extent=layer.extent()
                canvas.setExtent(extent)
                self.dlg.close()
            else:
                self.iface.messageBar().pushMessage("Error", "Your Login attempt was unsuccessful. Please try again", level=QgsMessageBar.CRITICAL,duration=5)
            # tryout

            #END TRY'''
    def captureFeatures(self, fid):
        print 'Feature Added'
        print fid
        self.fid=fid
        self.initDialog()
        #self.getUUID()
        self.saveEdit(self.parcel_id)
        # Check if there are edited features

        #self.initDialog()

    def startEdit(self):
        print 'Edit started'
    def finishEdit(self):
        print 'Yes boss!'
        #self.initDialog()
        layer=self.iface.activeLayer()
        self.initDialog()
    def initDialog(self):
        self.dlg2=SolaPluginDialog()
        self.dlg2.show()
        result = self.dlg2.exec_()
        if result:
            print 'Done!'
            print result
            print self.dlg2.parcel_id.text()
            self.parcel_id=self.dlg2.parcel_id.text()

    def createParcelLayer(self):
            uri = QgsDataSourceURI()
            uri.setConnection("localhost", "5432", "sola", "postgres", "solakogi")
            uri.setDataSource("cadastre", "cadastre_object", "geom_polygon")
            uri.uri()
            print uri.uri()

            rlayer = self.iface.addVectorLayer(uri.uri(), "Parcels", "postgres")
            self.iface.setActiveLayer(rlayer)

            rlayer.loadNamedStyle(self.plugin_dir+'/style.qml')

            rlayer.featureAdded.connect(self.captureFeatures)

    def createWardLayer(self):
            uri = QgsDataSourceURI()
            uri.setConnection("localhost", "5432", "sola", "postgres", "solakogi")
            uri.setDataSource("cadastre", "spatial_unit_group", "geom","hierarchy_level=3")
            uri.uri()
            print uri.uri()
            rlayer = self.iface.addVectorLayer(uri.uri(), "Ward", "postgres")
            rlayer.loadNamedStyle(self.plugin_dir+'/ward.qml')

    def createLGALayer(self):
            uri = QgsDataSourceURI()
            uri.setConnection("localhost", "5432", "sola", "postgres", "solakogi")
            uri.setDataSource("cadastre", "spatial_unit_group", "geom","hierarchy_level=2")
            uri.uri()
            print uri.uri()
            rlayer = self.iface.addVectorLayer(uri.uri(), "LGA", "postgres")
            rlayer.loadNamedStyle(self.plugin_dir+'/lga.qml')

    def createRasterLayer(self):
        urlWithParams = 'url=http://localhost:8085/geoserver/lokoja/wms?service=WMS&version=1.1.0&request=GetMap&layers=Lokoja&styles=&crs=EPSG:32632&format=image/png'
        rlayer = QgsRasterLayer(urlWithParams, 'MA-ALUS', 'wms')
        QgsMapLayerRegistry.instance().addMapLayer(rlayer)
        urlWithParams = 'url=http://localhost:8085/geoserver/lokoja/wms?service=WMS&version=1.1.0&request=GetMap&layers=Lokoja_Mos_Nov2011_50cm_Color&styles=&crs=EPSG:32632&format=image/png'
        rlayer = QgsRasterLayer(urlWithParams, 'lokoja:Lokoja', 'wms')
        QgsMapLayerRegistry.instance().addMapLayer(rlayer)

    def authUser(self,username,pswd):
        db = QSqlDatabase('QPSQL')
        if db.isValid():
            db.setHostName('localhost')
            # string
            db.setDatabaseName('sola')
            # string
            db.setUserName('postgres')
            # string
            db.setPassword('solakogi')
            # integer e.g. 5432
            db.setPort(5432)
            if db.open():
                # assume you have a table called 'appuser'
                query = db.exec_("select * from system.appuser where username='"+username+"'")
                #No password implementations yet
                # iterate over the rows
                if query.size()==1:
                    return True
                else: return False

        pass

    def saveEdit(self,values):

        layer=self.iface.activeLayer()
        fid=self.fid
        print fid
        # print feature.id()
        # print feature.geometry()
        # dataProvider=layer.dataProvider()
        caps = layer.dataProvider().capabilities()
        if caps & QgsVectorDataProvider.AddAttributes:
            feature = layer.getFeatures(QgsFeatureRequest(fid)).next()
            transaction_id=self.getTransactionId()
            layer.changeAttributeValue(fid, feature.fieldNameIndex('id'),self.getUUID())
            layer.changeAttributeValue(fid, feature.fieldNameIndex('type_code'),'parcel')
            layer.changeAttributeValue(fid, feature.fieldNameIndex('name_firstpart'),values)
            layer.changeAttributeValue(fid, feature.fieldNameIndex('name_lastpart'),'KG/LKJ/8')
            layer.changeAttributeValue(fid, feature.fieldNameIndex('status_code'),'pending')
            layer.changeAttributeValue(fid, feature.fieldNameIndex('change_action'),'i')
            layer.changeAttributeValue(fid, feature.fieldNameIndex('change_user'),self.user)
            layer.changeAttributeValue(fid, feature.fieldNameIndex('transaction_id'), transaction_id)
            layer.changeAttributeValue(fid, feature.fieldNameIndex('land_use_code'), 'residential')
            # feat.setGeometry()
            layer.commitChanges()
            (res,outFeat)=layer.dataProvider().addFeatures([feature])

            print res;

        pass
    def checkParcelNumberExists(self,parcelNumber):
        # Check the forms table to verify the existence of the parcel number in the form table
        db = QSqlDatabase('QPSQL')
        if db.isValid():
            db.setHostName('localhost')
            # string
            db.setDatabaseName('sola')
            # string
            db.setUserName('postgres')
            # string
            db.setPassword('solakogi')
            # integer e.g. 5432
            db.setPort(5432)
            if db.open():
                # assume you have a table called 'appuser'
                query = db.exec_("select nr from public.form where nr='"+parcelNumber+"'")
                #
                # iterate over the rows to see if there is atleast one record
                if query.size()==1:
                    return True
                else: return False
        pass

    # Implementation to standardize db calls
    def getDb(self):
        pass
    def getTransactionId(self):
        return '010656ad-1725-41e6-b172-064e9b89b323'
    def getUUID(self):
        db = QSqlDatabase('QPSQL')
        if db.isValid():
            db.setHostName('localhost')
            # string
            db.setDatabaseName('sola')
            # string
            db.setUserName('postgres')
            # string
            db.setPassword('solakogi')
            # integer e.g. 5432
            db.setPort(5432)
            if db.open():
                # assume you have a table called 'appuser'
                query = db.exec_("select uuid_generate_v1()")
                #No password implementations yet
                # iterate over the rows
                if query.size()==1:
                    query.next()
                    return str(query.value(0))
                else: return False

        pass
