# -*- coding: utf-8 -*-

import os
from subprocess import Popen
from PyQt4 import QtCore, QtGui, QtNetwork

_fromUtf8 = QtCore.QString.fromUtf8

class Download(QtCore.QObject):
    datachanged = QtCore.pyqtSignal(QtCore.QObject)
    def __init__(self, networkmanager):
        super(Download, self).__init__(networkmanager)
        self.downloadBuffer = QtCore.QByteArray()
        self.nam = networkmanager
        self.totalsize = 0
        self.loadedsize = 0
        self.progress = '- - -'
    def startDownload(self, networkreply, filepath, timestamp):
        """ Browser starts a new download """
        self.download = networkreply
        self.filepath = unicode(filepath)
        self.timestamp = timestamp
        self.updateMetaData()
        self.file = QtCore.QFile(self.filepath)
        if self.support_resume == True and self.file.exists():
            confirm = QtGui.QMessageBox.question(QtGui.QApplication.desktop(), "Overwrite File ?", 
            "The file already exists.\nDo you want to Overwrite old file?", "Continue Remaining", "Replace Old", "Rename")
            if confirm == 0:
                self.download.abort()
                self.download.deleteLater()
                self.retry()
            elif confirm == 1:
                self.file.resize(0)
            else:
                self.filepath = os.path.splitext(self.filepath)[0] + '1' + os.path.splitext(self.filepath)[1]
                self.file = QtCore.QFile(self.filepath)
        else:
            self.file.resize(0)
        self.file.open(QtCore.QIODevice.Append)
        self.filename = QtCore.QFileInfo(self.filepath).fileName()
        if self.download.isFinished():
            self.dataReceived()
            self.downloadStopped()
            return
        self.connect_signals()
    def connect_signals(self):
        self.download.metaDataChanged.connect(self.updateMetaData)
        self.download.readyRead.connect(self.dataReceived)
        self.download.finished.connect(self.downloadStopped)
        self.download.error.connect(self.downloadfailed)
    def loadDownload(self, filepath, url, size, timestamp):
        """ old downloads are created when browser is opened """
        self.filepath = filepath
        self.url = url
        self.totalsize = size
        self.timestamp = timestamp
        self.support_resume = True
        self.filename = QtCore.QFileInfo(self.filepath).fileName()
    def dataReceived(self):
        """ Add data to download buffer whenever data from network is received """
        self.loadedsize += self.download.size()
        self.downloadBuffer += self.download.readAll()
        if self.totalsize!=0:
          self.progress = "{}%".format(int((float(self.loadedsize)/self.totalsize)*100))
        else:
          self.progress = "Unknown"
        self.datachanged.emit(self)
        if self.downloadBuffer.size()>307200 :
            self.saveToDisk()
    def downloadStopped(self):
        """ Auto save when stops"""
        self.progress = "- - -"
        self.saveToDisk()
        self.file.close()
        self.download.deleteLater()
        if self.loadedsize==self.totalsize:
            QtGui.QMessageBox.information(None, 'Download Complete', "File %s \nhas been downloaded successfully"%self.filename)

    def retry(self):
        """ Start download from breakpoint or from beginning(if not resume supported)"""
        self.file = QtCore.QFile(self.filepath)
        self.file.open(QtCore.QIODevice.Append)
        request = QtNetwork.QNetworkRequest(QtCore.QUrl(self.url))
        if self.support_resume:
            self.loadedsize = self.file.size()
            if self.loadedsize == self.totalsize : return
            request.setRawHeader('Range', 'bytes={}-'.format(self.loadedsize) )
        else:
            self.loadedsize = 0
            self.file.resize(0)
        self.download = self.nam.get(request)
        self.connect_signals()
        print('Retry: '+self.url)

    def downloadfailed(self, error): # error = 5 if cancelled
        """ at download error """
        if (error==5):
            return
        QtGui.QMessageBox.warning(QtGui.QApplication.desktop(), "Download Stopped !","Download has suddenly stopped.\n You may try again\n Error : "+str(error))

    def updateMetaData(self):
        """ Updates download header data in download (Resume support, url, Size)"""
        # Update Url path
        if self.download.hasRawHeader('Location'):
            self.url = str(self.download.rawHeader('Location'))
        else:
            self.url = self.download.url().toString()
        # Update total size
        if self.totalsize==0:
            self.totalsize = self.download.header(1).toLongLong()[0]
        # Update pause/resume support
        if self.download.hasRawHeader('Accept-Ranges') or self.download.hasRawHeader('Content-Range'):
            self.support_resume = True
        else:
            self.support_resume = False

    def saveToDisk(self):
        """ Appends data to file, when download finished or ByteArray data exceeds 48kB"""
        self.file.write( self.downloadBuffer)
        self.downloadBuffer.clear()

class DownloadsModel(QtCore.QAbstractTableModel):
    updateRequested = QtCore.pyqtSignal()
    deleteDownloadsRequested = QtCore.pyqtSignal(QtCore.QStringList)
    def __init__(self, downloadlist, parent=QtGui.QApplication.instance()):
        super(DownloadsModel, self).__init__(parent)
        self.headers = ["File Name", "Loaded Size", "Total Size", "Progress"]
        self.downloadlist = downloadlist
    def rowCount(self, index):
        return len(self.downloadlist)
    def columnCount(self, index):
        return 4
    def data(self, index, role=QtCore.Qt.DisplayRole):
        row = index.row()
        col = index.column()
        if role==QtCore.Qt.DisplayRole:
          if col==0:
            return unicode(self.downloadlist[row].filename)
          elif col==1:
            return self.formatFileSize(self.downloadlist[row].loadedsize)
          elif col==2:
            return self.formatFileSize(self.downloadlist[row].totalsize)
          elif col==3:
            return self.downloadlist[row].progress
        elif role==QtCore.Qt.TextAlignmentRole:
          if col!=0:
            return QtCore.Qt.AlignCenter
        return QtCore.QVariant()
    def headerData(self,index,orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole and orientation==1:
          return QtCore.QVariant(self.headers[index])
        return QtCore.QVariant()
    def datachanged(self, download):
        updatedrow = self.downloadlist.index(download)
        self.dataChanged.emit(self.index(updatedrow,0), self.index(updatedrow,3) )
    def formatFileSize(self, filesize):
        if len(str(filesize))>7:
            filesize = "{}M".format(round(float(filesize)/1048576, 2))
        else:
            filesize = "{}k".format(filesize/1024)
        return filesize
    def removeDownloads(self, selected_rows):
        timestamps = []
        for row in selected_rows:
          timestamps.append(self.downloadlist[row-selected_rows.index(row)].timestamp)
          if self.downloadlist[row - selected_rows.index(row)].progress != '- - -':
            self.downloadlist[row - selected_rows.index(row)].download.abort()
          self.downloadlist.pop(row - selected_rows.index(row)).deleteLater()
        self.updateRequested.emit()
        self.deleteDownloadsRequested.emit(timestamps)
    def deleteDownloads(self, selected_rows):
        for row in selected_rows:
          if os.path.exists(self.downloadlist[row].filepath):
            os.remove(self.downloadlist[row].filepath)

class DownloadsTable(QtGui.QTableView):
    def __init__(self, model,parent = None):
        QtGui.QTableWidget.__init__(self, parent)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(1) # Select Rows
        self.setModel(model)
        model.dataChanged.connect(self.dataChanged)
        model.updateRequested.connect(self.update)
        self.horizontalHeader().setDefaultSectionSize(120)
        self.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
    def contextMenuEvent(self, e):
        self.rel_pos = e.pos()
        self.rowClicked = self.rowAt(self.rel_pos.y())
        if self.rowClicked == -1: return
        offset = QtCore.QPoint(self.verticalHeader().width()+3,self.horizontalHeader().height()+3)
        menu = QtGui.QMenu(self)
        if len(self.selectedIndexes())==4:
            if self.model().downloadlist[self.rowClicked].progress == '- - -':
                if self.model().downloadlist[self.rowClicked].support_resume:
                  menu.addAction("Resume", self.pause_resume)
                else:
                  menu.addAction("Restart", self.pause_resume)
            else:
                if self.model().downloadlist[self.rowClicked].support_resume:
                    menu.addAction("Pause", self.pause_resume)
                else:
                    menu.addAction("Stop", self.pause_resume)
            menu.addAction("Copy Address", self.copy_address)
        menu.addAction("Remove Download", self.remove_selected)
        menu.addAction("Delete File(s)", self.delete_selected)
        menu.exec_(self.mapToGlobal(self.rel_pos + offset))
    def pause_resume(self):
        if self.model().downloadlist[self.rowClicked].progress == '- - -':
            self.model().downloadlist[self.rowClicked].retry()
        else:
            self.model().downloadlist[self.rowClicked].download.abort()
    def copy_address(self):
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(self.model().downloadlist[self.rowClicked].url)
    def remove_selected(self):
        rows = self.selectionModel().selectedRows()
        selected_rows = [item.row() for item in rows]
        selected_rows.sort()
        self.model().removeDownloads(selected_rows)
        self.clearSelection()
    def delete_selected(self):
        rows = self.selectionModel().selectedRows()
        selected_rows = [item.row() for item in rows]
        self.model().deleteDownloads(selected_rows)

class Downloads_Dialog(object):
    def setupUi(self, Dialog, mymodel):
        Dialog.setObjectName(_fromUtf8("Downloads_Dialog"))
        Dialog.resize(740, 440)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tableView = DownloadsTable(mymodel)
        self.tableView.setObjectName(_fromUtf8("tableView"))
        self.verticalLayout.addWidget(self.tableView)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle("Download Manager")


