#!/usr/bin/env python

import sys
from PyQt4 import QtCore, QtGui, QtNetwork
from os import environ
homedir = environ['HOME']
downloaddir = homedir+"/Downloads/"

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
    def startDownload(self, networkreply):
        if networkreply.hasRawHeader('Location'):
            url = QtCore.QUrl(str(networkreply.rawHeader('Location')))
            networkreply.abort()
            self.download = self.nam.get(QtNetwork.QNetworkRequest(url))
        else:
            self.download = networkreply
        decoded_url = QtCore.QUrl.fromPercentEncoding(self.download.url().path().toUtf8())
        self.filename = QtCore.QFileInfo(decoded_url).fileName()
        self.updateMetaData()
        if self.download.isFinished():
            self.dataReceived()
            self.downloadStopped()
            return
        self.connect_signals()
    def connect_signals(self):
        self.download.metaDataChanged.connect(self.updateMetaData)
        self.download.readyRead.connect(self.dataReceived)
        self.download.finished.connect(self.downloadStopped)
#        self.download.error.connect(self.downloadfailed)
    def loadDownload(self, filepath, url, size):
        self.filepath = filepath
        self.url = url
        self.totalsize = size
        self.support_resume = True
        self.filename = QtCore.QFileInfo(self.filepath).fileName()
        self.complete = False
    def dataReceived(self):
        self.downloadBuffer += self.download.readAll()
        self.loadedsize = self.downloadBuffer.size()
        if self.totalsize!=0:
          self.progress = "{}%".format(int((float(self.loadedsize)/self.totalsize)*100))
        else:
          self.progress = "Unknown"
        self.datachanged.emit(self)

    def downloadStopped(self):
        """ Auto save when stops"""
        self.progress = "- - -"
        if (self.loadedsize == self.totalsize) or (self.support_resume==False):
            self.complete = True
        else:
            self.complete = False
        self.saveToDisk()

    def retry(self):
        if self.support_resume:
            saved_file = QtCore.QFile( self.filepath )
            saved_file.open(QtCore.QIODevice.ReadOnly)
            self.downloadBuffer += saved_file.readAll()
            saved_file.close()
            self.loadedsize = self.downloadBuffer.size()
        request = QtNetwork.QNetworkRequest(QtCore.QUrl(self.url))
        if self.support_resume:
            request.setRawHeader('Range', 'bytes={}-'.format(self.loadedsize) )
        try:
            self.download.deleteLater()
        except: pass
        self.download = self.nam.get(request)
        self.connect_signals()
        print 'Retry: '+self.url

    def downloadfailed(self, error): # error = 5 if cancelled
        """ at download error """
        if (error==5) or (self.loadedsize == self.totalsize) or (self.support_resume==False):
            return
        print str(error)

    def updateMetaData(self):
        if self.download.hasRawHeader('Location'):
            self.url = str(self.download.rawHeader('Location'))
        else:
            self.url = self.download.url().toString()
        if self.totalsize==0:
            self.totalsize = self.download.header(1).toLongLong()[0]
        if self.download.hasRawHeader('Accept-Ranges') or self.download.hasRawHeader('Content-Range'):
            self.support_resume = True
        else:
            self.support_resume = False
        content_name = str(self.download.rawHeader('Content-Disposition'))
        if content_name.startswith('attachment'):
            self.filename = content_name.split('=')[-1]
        for (title, header) in self.download.rawHeaderPairs():
            print title, header

    def saveToDisk(self):
        try:
            if self.filepath == '': raise AttributeError
        except AttributeError:
            self.filepath = QtGui.QFileDialog.getSaveFileName(None,
                                      "Enter FileName to Save", downloaddir+str(self.filename),
                                      "All Files (*)" )
        if self.filepath != '':
            output = QtCore.QFile( self.filepath )
            output.open(QtCore.QIODevice.WriteOnly)
            output.write( self.downloadBuffer)
            output.close()
            self.filename = QtCore.QFileInfo(self.filepath).fileName()
        self.downloadBuffer.clear()

class DownloadsModel(QtCore.QAbstractTableModel):
    def __init__(self, downloadlist, parent=None):
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
            return "{}".format(self.downloadlist[row].filename)
          elif col==1:
            return "{}k".format(self.downloadlist[row].loadedsize/1024)
          elif col==2:
            return "{}k".format(self.downloadlist[row].totalsize/1024)
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

class DownloadsTable(QtGui.QTableView):
    def __init__(self, model,parent = None):
        QtGui.QTableWidget.__init__(self, parent)
        self.setModel(model)
        model.dataChanged.connect(self.dataChanged)
        self.horizontalHeader().setDefaultSectionSize(120)
        self.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
    def mousePressEvent(self, e):
        self.selectRow(self.rowAt(e.pos().y()))
    def contextMenuEvent(self, e):
        self.rel_pos = e.pos()
        self.rowClicked = self.rowAt(self.rel_pos.y())
        if self.rowClicked == -1: return
        offset = QtCore.QPoint(self.verticalHeader().width()+3,self.horizontalHeader().height()+3)
        menu = QtGui.QMenu(self)
        if self.model().downloadlist[self.rowClicked].progress == '- - -':
            if self.model().downloadlist[self.rowClicked].support_resume:
              menu.addAction("Resume", self.pause_resume)
            else:
              menu.addAction("Restart", self.pause_resume)
        else:
            menu.addAction("Pause", self.pause_resume)
        menu.addAction("Save to Disk", self.save_download)
        menu.addAction("Mark as Complete", self.mark_complete)
        menu.exec_(self.mapToGlobal(self.rel_pos + offset))
    def save_download(self):
        if self.model().downloadlist[self.rowClicked].progress != '- - -':
            self.model().downloadlist[self.rowClicked].download.abort()
            return
        self.model().downloadlist[self.rowClicked].saveToDisk()
    def pause_resume(self):
        if self.model().downloadlist[self.rowClicked].progress == '- - -':
            self.model().downloadlist[self.rowClicked].retry()
        else:
            self.model().downloadlist[self.rowClicked].download.abort()
    def mark_complete(self):
        self.model().downloadlist[self.rowClicked].complete = True

class Downloads_Dialog(object):
    def setupUi(self, Dialog, mymodel):
        Dialog.setObjectName(_fromUtf8("Dialog"))
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


