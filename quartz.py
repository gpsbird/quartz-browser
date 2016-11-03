#!/usr/bin/env python
"""
Name = Quartz Browser
version = 1.3
Dependency = python-qt4
Usage = A Light Weight Internet Browser
Features = Unified Search/Url Bar
           Turn Javascript, Load Images on/off
           Find Text inside page
           Print Page
           Save page as JPG
Last Update : Settings Dialog added.
            Length of progress bar increased.
            Fixed confusion between search and goto fixed for UrlEdit Box.

   Copyright (C) 2016 Arindam Chaudhuri <ksharindam@gmail.com>
  
   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.
  
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
  
   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import configparser
from os.path import abspath
from subprocess import Popen
from PyQt4.QtCore import QUrl, pyqtSignal, Qt

from PyQt4.QtGui import QApplication, QMainWindow, QWidget, QPrintDialog, QDialog
from PyQt4.QtGui import QLineEdit, QComboBox, QPushButton, QToolButton, QAction, QMenu
from PyQt4.QtGui import QGridLayout, QSizePolicy, QIcon, QPrinter, QHeaderView, QProgressBar
from PyQt4.QtGui import QPainter, QPixmap, QFont

from PyQt4.QtWebKit import QWebView, QWebPage, QWebFrame, QWebSettings
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkCookieJar
import common_files
from settings_dialog import Ui_Dialog


class MyWebPage(QWebPage):
    def __init__(self):
        QWebPage.__init__(self)
        self.setForwardUnsupportedContent(True)
        self.useragent = "Mozilla/5.0 (X11; Linux armv7l) AppleWebKit/601.1 (KHTML, like Gecko) Version/8.0 Safari/601.1 Chrome/34.0.1847.116"
#       TODO : Change Default User Agent, (this is in another place)
    def userAgentForUrl(self, url):
        return self.useragent
    def setUserAgentForUrl(self, useragent):
        self.useragent = useragent

class MyWebView(QWebView):
    _windows = set()
    def __init__(self, **kargs):
        QWebView.__init__(self, **kargs)
        self.setPage(MyWebPage())
    def createWindow(self, windowtype):
        return self
#        window = self.newWindow()
#        window.show()
#        return window.web
#    def newWindow(cls):
#        window = Main()
#        window.setAttribute(Qt.WA_DeleteOnClose)
#        cls._windows.add(window)
#        return window

class QurlEdit(QLineEdit):
    def __init__(self, parent=None):
        super(QurlEdit, self).__init__(parent)
    def mouseDoubleClickEvent(self, event):
        self.selectAll()
#        mouseDoubleClicked = pyqtSignal()
#        self.mouseDoubleClicked.emit()


class Main(QMainWindow):
    def __init__(self): 
        QMainWindow.__init__(self)
        try:
            self.opensettings()
        except:
            self.defaultsettings()
        self.settings = QWebSettings.globalSettings()
        self.settings.setMaximumPagesInCache(6)
        self.initUI()
    def initUI(self):
        self.loadimagesaction = QAction(self)
        self.loadimagesaction.setText("Load Images")
        self.loadimagesaction.setCheckable(True)
        self.loadimagesaction.triggered.connect(self.loadimages)
        self.javascriptmode = QAction(self)
        self.javascriptmode.setText("Enable Javascript")
        self.javascriptmode.setCheckable(True)
        self.javascriptmode.triggered.connect(self.setjavascript)
        self.zoominaction = QAction(self)
        self.zoominaction.setText("Zoom  In")
        self.zoominaction.setShortcut("Ctrl++")
        self.zoominaction.triggered.connect(self.zoomin)
        self.zoomoutaction = QAction(self)
        self.zoomoutaction.setText("Zoom  Out")
        self.zoomoutaction.setShortcut("Ctrl+-")
        self.zoomoutaction.triggered.connect(self.zoomout)
        self.fullscreenaction = QAction(self)
        self.fullscreenaction.setText("Toggle Fullscreen")
        self.fullscreenaction.setShortcut("F11")
        self.fullscreenaction.triggered.connect(self.fullscreenmode)
        self.settingsaction = QAction(self)
        self.settingsaction.setText("Settings")
#        self.settingsaction.setShortcut("Ctrl+")
        self.settingsaction.triggered.connect(self.settingstweek)
        self.saveasimageaction = QAction(self)
        self.saveasimageaction.setText("Save as Image")
        self.saveasimageaction.setShortcut("Ctrl+S")
        self.saveasimageaction.triggered.connect(self.saveasimage)
        self.printaction = QAction(self)
        self.printaction.setText("Print")
        self.printaction.setShortcut("Ctrl+P")
        self.printaction.triggered.connect(self.printpage)
        self.findaction = QAction(self)
        self.findaction.setText("Find Text")
        self.findaction.setShortcut("Ctrl+F")
        self.findaction.triggered.connect(self.findmode)
        self.quitaction = QAction(self)
        self.quitaction.setText("Quit")
        self.quitaction.setShortcut("Ctrl+Q")
        self.quitaction.triggered.connect(self.close)

        self.menu = QMenu(self)
        self.menu.addAction(self.findaction)
        self.menu.addAction(self.javascriptmode)
        self.menu.addAction(self.loadimagesaction)
        self.menu.addAction(self.zoominaction)
        self.menu.addAction(self.zoomoutaction)
        self.menu.addAction(self.fullscreenaction)
        self.menu.addAction(self.settingsaction)
        self.menu.addAction(self.saveasimageaction)
        self.menu.addAction(self.printaction)
        self.menu.addAction(self.quitaction)


#       Create Gui Part
        grid = QGridLayout()
        grid.setSpacing(2)
        grid.setContentsMargins(2,2,2,2)
        self.centralwidget = QWidget(self)
        self.centralwidget.setLayout(grid)
        self.setCentralWidget(self.centralwidget)

        self.line = QurlEdit(self) 
        self.line.setStyleSheet("font-size:15px;")
        self.line.returnPressed.connect(self.Enter)
        self.reload = QPushButton(QIcon(":/view-refresh.png"), "",self) 
        self.reload.setMinimumSize(35,26) 
        self.reload.setShortcut("F5") 
        self.reload.setStyleSheet("font-size:23px;") 
        self.reload.clicked.connect(self.Reload)
        self.back = QPushButton(QIcon(":/go-previous.png"), "", self) 
        self.back.setMinimumSize(35,26) 
        self.back.setStyleSheet("font-size:23px;") 
        self.back.clicked.connect(self.Back)
        self.forw = QPushButton(QIcon(":/go-next.png"), "",self) 
        self.forw.setMinimumSize(35,26) 
        self.forw.setStyleSheet("font-size:23px;") 
        self.forw.clicked.connect(self.Forward)
        self.menuBtn = QToolButton(self)
        self.menuBtn.setIcon(QIcon(":/menu.png"))
        self.menuBtn.setMenu(self.menu)
        self.menuBtn.setPopupMode(QToolButton.InstantPopup)

        self.findBtn = QPushButton(QIcon(":/search.png"), "", self)
        self.findBtn.setToolTip("Find Text in \n This Page")
        self.findBtn.clicked.connect(self.findmode)
        self.find = QPushButton(self)
        self.find.setText("Find/Next")
        self.find.clicked.connect(self.findnext)
        self.find.hide()
        self.findprev = QPushButton(self)
        self.findprev.setText("Backward")
        self.findprev.clicked.connect(self.findback)
        self.findprev.hide()
        self.cancelfind = QPushButton(self)
        self.cancelfind.setText("Cancel")
        self.cancelfind.clicked.connect(self.cancelfindmode)
        self.cancelfind.hide()

        self.pbar = QProgressBar() 
        self.pbar.setMaximumWidth(480)
        self.pbar.hide()

        self.web = MyWebView(loadProgress = self.pbar.setValue, loadFinished = self.pbar.hide, loadStarted = self.pbar.show, titleChanged = self.setWindowTitle) 
        self.web.setMinimumSize(1000,640)
        self.applysettings()
#       
        self.web.urlChanged.connect(self.UrlChanged)
        self.web.loadStarted.connect(self.startedloading) 
        self.web.loadFinished.connect(self.finishedloading) 
        self.web.page().linkHovered.connect(self.LinkHovered)
        self.web.page().printRequested.connect(self.printpage)
        self.web.page().downloadRequested.connect(self.download_file)
        self.web.page().unsupportedContent.connect(self.download_file)

        self.cookiejar = QNetworkCookieJar()
        self.networkmanager = QNetworkAccessManager()
        self.networkmanager.setCookieJar(self.cookiejar)
        self.web.page().setNetworkAccessManager(self.networkmanager)

        grid.addWidget(self.back,0,0, 1, 1) 
        grid.addWidget(self.forw,0,1, 1, 1) 
        grid.addWidget(self.reload,0,2, 1, 1) 
        grid.addWidget(self.line,0,3, 1, 1) 
        grid.addWidget(self.find, 0,4, 1, 1)
        grid.addWidget(self.findprev, 0,5, 1, 1)
        grid.addWidget(self.cancelfind, 0,6, 1, 1)
        grid.addWidget(self.menuBtn,0,7, 1, 1) 
        grid.addWidget(self.findBtn,0,8, 1, 1) 
        grid.addWidget(self.web, 2, 0, 1, 9)
#---------Window settings --------------------------------
        self.setWindowTitle("PySurf") 
        self.setWindowIcon(QIcon("")) 
        self.setStyleSheet("background-color:") 
        self.status = self.statusBar()
        self.status.setMaximumHeight(18)
        self.status.addPermanentWidget(self.pbar) 
    def Enter(self): 
        url = str(self.line.text())
        http = "http://" 
        if ("://" not in url and "." not in url) or (" " in url): 
            url = "http://www.google.com/search?q="+url 
        elif url.startswith("file:///"):
            url = url[7:]
        elif not (url.startswith(http) or url.startswith("https://")): 
            url = http + url 
        self.GoTo(url)
    def GoTo(self, url):
        self.line.setText(url)
        if url.startswith("http://") or url.startswith("https://"):
            URL = QUrl(url)
            self.web.load(URL)
        elif url.startswith("/"):
            main.web.load(QUrl.fromLocalFile(url))
        else:
            main.web.load(QUrl.fromLocalFile(abspath(url)))
        self.line.setText(url)
    def Bookmark(self): 
        global url 
        self.list.addItem(url) 
#        self.book.setIcon(QIcon(":/add-bookmark.png"))
    def handleBookmarks(self,choice): 
        global url
        url = choice 
        self.line.setText(url) 
        self.Enter()
    def Back(self): 
        self.web.back() 
    def Forward(self): 
        self.web.forward()
    def Reload(self):
        if self.loading:
            self.web.stop()
        else: 
            self.web.reload()
    def UrlChanged(self): 
        self.line.setText(self.web.url().toString())
    def LinkHovered(self,l): 
        self.status.showMessage(l)
    def startedloading(self):
        self.reload.setIcon(QIcon(":/process-stop.png"))
        self.loading = True
    def finishedloading(self, ok):
#        if not ok:
#            main.web.load(QUrl("qrc:///error.html"))
        self.reload.setIcon(QIcon(":/view-refresh.png"))
        self.loading = False

    def fullscreenmode(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    def saveasimage(self):
        viewportsize = self.web.page().viewportSize()
        contentsize = self.web.page().mainFrame().contentsSize()
        self.web.page().setViewportSize(contentsize)
        img = QPixmap(contentsize)
        painter = QPainter()
        painter.begin(img)
        self.web.page().mainFrame().render(painter, QWebFrame.AllLayers)
        painter.end()
        img.save("html.png")
        self.web.page().setViewportSize(viewportsize)
    def printpage(self, page):
        printer = QPrinter(mode=QPrinter.HighResolution)
        print_dialog = QPrintDialog(printer, self)
        if print_dialog.exec_() == QDialog.Accepted:
          if page != 0:
            page.print_(printer)
          else:
            self.web.print_(printer)

    def findmode(self):
        self.line.clear()
        self.find.show()
        self.findprev.show()
        self.cancelfind.show()
    def cancelfindmode(self):
        self.web.findText("")
        self.find.hide()
        self.findprev.hide()
        self.cancelfind.hide()
        self.line.setText(self.web.url().toString())
    def findnext(self):
        text = self.line.text()
        self.web.findText(text)
    def findback(self):
        text = self.line.text()
        self.web.findText(text, QWebPage.FindBackward)

    def download_file(self, networkrequest):
        url = str(networkrequest.url().toString())
        Popen(["uget-gtk", url])
    def zoomin(self):
        zoomlevel = self.web.textSizeMultiplier()
        self.web.setTextSizeMultiplier(zoomlevel+0.1) # Use setZoomFactor() to zoom text and images
    def zoomout(self):
        zoomlevel = self.web.textSizeMultiplier()
        self.web.setTextSizeMultiplier(zoomlevel-0.1)
    def loadimages(self, state):
        self.settings.setAttribute(QWebSettings.AutoLoadImages, state)
        if state:
            self.loadimagesval = True
        else:
            self.loadimagesval = False
        self.savesettings()
    def setjavascript(self, state):
        self.settings.setAttribute(QWebSettings.JavascriptEnabled, state)
        if state:
            self.javascriptenabledval = True
        else:
            self.javascriptenabledval = False
        self.savesettings()

######### Settings Portion ##########
    def settingstweek(self):
        self.dialog = QDialog(self)
        self.settingsdialog = Ui_Dialog()
        self.settingsdialog.setupUi(self.dialog)
        if self.loadimagesval:
            self.settingsdialog.checkLoadImages.setChecked(True)
        if self.javascriptenabledval:
            self.settingsdialog.checkJavascript.setChecked(True)
        if self.customuseragentval :
            self.settingsdialog.checkUserAgent.setChecked(True)
        self.settingsdialog.useragentEdit.setText(self.useragentval)
        if self.customhomepageurlval:
            self.settingsdialog.checkHomePage.setChecked(True)
        self.settingsdialog.homepageEdit.setText(self.homepageurlval)
        self.settingsdialog.spinFontSize.setValue(self.minfontsizeval)
        self.settingsdialog.standardfontCombo.setCurrentFont(QFont(self.standardfontval))
        self.settingsdialog.sansfontCombo.setCurrentFont(QFont(self.sansfontval))
        self.settingsdialog.seriffontCombo.setCurrentFont(QFont(self.seriffontval))
        self.settingsdialog.fixedfontCombo.setCurrentFont(QFont(self.fixedfontval))
        self.dialog.accepted.connect(self.changesettings)
        self.dialog.show()
    def changesettings(self):
        if self.settingsdialog.checkLoadImages.isChecked():
            self.loadimagesval = True
        else:
            self.loadimagesval = False
        if self.settingsdialog.checkJavascript.isChecked():
            self.javascriptenabledval = True
        else:
            self.javascriptenabledval = False
        if self.settingsdialog.checkUserAgent.isChecked():
            self.customuseragentval = True
        else:
            self.customuseragentval = False
        self.useragentval = self.settingsdialog.useragentEdit.text()
        if self.settingsdialog.checkHomePage.isChecked():
            self.customhomepageurlval = True
        else:
            self.customhomepageurlval = False
        self.homepageurlval = self.settingsdialog.homepageEdit.text()
        self.minfontsizeval = self.settingsdialog.spinFontSize.value()
        self.standardfontval = self.settingsdialog.standardfontCombo.currentText()
        self.sansfontval = self.settingsdialog.sansfontCombo.currentText()
        self.seriffontval = self.settingsdialog.seriffontCombo.currentText()
        self.fixedfontval = self.settingsdialog.fixedfontCombo.currentText()
        self.applysettings()
        self.savesettings()
    def defaultsettings(self):
        self.loadimagesval = True
        self.javascriptenabledval = True
        self.customuseragentval = False
        self.useragentval = "Nokia 5130"
        self.customhomepageurlval = False
        self.homepageurlval = "/usr/share/doc/python-qt4-doc/html/classes.html"
        self.minfontsizeval = 12
        self.standardfontval = "Sans"
        self.sansfontval = "Sans"
        self.seriffontval = "Serif"
        self.fixedfontval = "Monospace"
    def opensettings(self):
        Config = configparser.ConfigParser()
        Config.read("settings.ini")
        self.loadimagesval = Config.getboolean('Browsing', 'LoadImages')
        self.javascriptenabledval = Config.getboolean('Browsing', 'JavaScriptEnabled')
        self.customuseragentval = Config.getboolean('Browsing', 'CustomUserAgent')
        self.useragentval = Config.get('Browsing', 'UserAgent')
        self.customhomepageurlval = Config.getboolean('HomePage', 'CustomHomePageUrl')
        self.homepageurlval = Config.get('HomePage', 'HomePageUrl')
        self.minfontsizeval = Config.getint('Appearance', 'MinFontSize')
        self.standardfontval = Config.get('Appearance', 'StandardFont')
        self.sansfontval = Config.get('Appearance', 'SansFont')
        self.seriffontval = Config.get('Appearance', 'SerifFont')
        self.fixedfontval = Config.get('Appearance', 'FixedFont')
    def savesettings(self):
        Config = configparser.ConfigParser()
        Config.add_section('Browsing')
        Config.set('Browsing', 'LoadImages', str(self.loadimagesval))
        Config.set('Browsing', 'JavaScriptEnabled', str(self.javascriptenabledval))
        Config.set('Browsing', 'CustomUserAgent', str(self.customuseragentval))
        Config.set('Browsing', 'UserAgent', str(self.useragentval))
        Config.add_section('HomePage')
        Config.set('HomePage', 'CustomHomePageUrl', str(self.customhomepageurlval))
        Config.set('HomePage', 'HomePageUrl', str(self.homepageurlval))
        Config.add_section('Appearance')
        Config.set('Appearance', 'MinFontSize', str(self.minfontsizeval))
        Config.set('Appearance', 'StandardFont', str(self.standardfontval))
        Config.set('Appearance', 'SansFont', str(self.sansfontval))
        Config.set('Appearance', 'SerifFont', str(self.seriffontval))
        Config.set('Appearance', 'FixedFont', str(self.fixedfontval))
        cfgfile = open("settings.ini", 'w')
        Config.write(cfgfile)
        cfgfile.close()
    def applysettings(self):
        if self.customuseragentval == True:
            self.web.page().setUserAgentForUrl(self.useragentval)
        else:
            self.web.page().setUserAgentForUrl("Mozilla/5.0 (X11; Linux armv7l) AppleWebKit/601.1 (KHTML, like Gecko) Version/8.0 Safari/601.1 Chrome/34.0.1847.116")
        if self.customhomepageurlval:
            self.homepageurl = self.homepageurlval
        else:
            self.homepageurl = "http://www.google.com"
        self.settings.setAttribute(QWebSettings.AutoLoadImages, self.loadimagesval)
        if self.loadimagesval:
            self.loadimagesaction.setChecked(True)
        else:
            self.loadimagesaction.setChecked(False)
        self.settings.setAttribute(QWebSettings.JavascriptEnabled, self.javascriptenabledval)
        if self.javascriptenabledval:
            self.javascriptmode.setChecked(True)
        else:
            self.javascriptmode.setChecked(False)
        self.settings.setFontSize(QWebSettings.MinimumFontSize, self.minfontsizeval)
        self.settings.setFontFamily(QWebSettings.StandardFont, self.standardfontval)
        self.settings.setFontFamily(QWebSettings.SansSerifFont, self.sansfontval)
        self.settings.setFontFamily(QWebSettings.SerifFont, self.seriffontval)
        self.settings.setFontFamily(QWebSettings.FixedFont, self.fixedfontval)
#        self.settings.setFontSize(QWebSettings.DefaultFontSize, 14)
#        self.settings.setAttribute(QWebSettings.DnsPrefetchEnabled, True)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    main= Main() 
    main.show()
    if len(sys.argv)> 1:
        main.GoTo(sys.argv[1])
    else:
        main.GoTo(main.homepageurl)
    sys.exit(app.exec_())
