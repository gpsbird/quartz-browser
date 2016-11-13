from PyQt4.QtGui import QMessageBox
from PyQt4.QtCore import QByteArray, QFile, QIODevice
#from PyQt4.QtNetwork import QNetworkRequest

class DownloadManager(object):
    def __init__(self, networkmanager):
        self.networkmanager = networkmanager
    def download(self, networkrequest, filepath):
#        networkrequest.setAttribute(QNetworkRequest.CacheLoadControlAttribute, QNetworkRequest.PreferCache)
        self.downloadBuffer = QByteArray()
        self.downloadpath = filepath
        self.download = self.networkmanager.get(networkrequest)
        self.download.readyRead.connect(self.appendData)
        self.download.finished.connect(self.saveToDisk)

    def appendData(self):
        self.downloadBuffer += self.download.readAll()

    def saveToDisk(self):
        output = QFile( self.downloadpath )
        try:
          output.open(QIODevice.WriteOnly)
          output.write( self.downloadBuffer)
          output.close()
        except:
          QMessageBox.critical(None, "Download Error !","Error saving file!")
          return
        QMessageBox.information(None, "Successful !","File has been successfully saved!")



