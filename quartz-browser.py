#!/usr/bin/env python
"""
Name = Quartz Browser
version = 1.4.3
Dependency = python-qt4, uget-gtk
Usage = A Light Weight Internet Browser
Features = Unified Google_Search & Url Bar
           Turn Javascript, Load Images on/off
           Find Text inside page
           Print Page
           Save page as JPG, html
Last Update : 
            Save as HTML added.
            Dependency on python-configparser has been removed.
            Now cookies are saved.

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
# TODO : Auto complete username password
#        remove Some menu items
#        Use of internal download manager

import sys
from os.path import abspath, exists
from os import environ, mkdir
from subprocess import Popen
from time import strftime

from PyQt4.QtCore import QUrl, pyqtSignal, Qt, QStringList, QSettings
from PyQt4.QtCore import QFileInfo, QByteArray

from PyQt4.QtGui import QApplication, QMainWindow, QWidget, QPrintDialog, QFileDialog, QDialog, QStringListModel, QListView
from PyQt4.QtGui import QLineEdit, QCompleter, QComboBox, QPushButton, QToolButton, QAction, QMenu
from PyQt4.QtGui import QGridLayout, QIcon, QPrinter, QHeaderView, QProgressBar
from PyQt4.QtGui import QPainter, QPixmap, QFont

from PyQt4.QtWebKit import QWebView, QWebPage, QWebFrame, QWebSettings
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkCookieJar, QNetworkCookie, QNetworkRequest

from settings_dialog import Ui_Dialog
from bookmarks_dialog import Bookmarks_Dialog, Add_Bookmark_Dialog, History_Dialog
from bookmarkparser import parsebookmarks, writebookmarks
from download_manager import DownloadManager
import quartz_common


userhomedir = environ['HOME']
configdir = userhomedir+"/.config/quartz-browser/"

class MyCookieJar(QNetworkCookieJar):
    """ Reimplemented QNetworkCookieJar to get cookie import/export feature"""
    def __init__(self, parent=None):
        super(MyCookieJar, self).__init__(parent)
        self.window = parent
        cookiesValue = self.window.settings.value("cookies").toByteArray()
        if cookiesValue:
            cookiesList = QNetworkCookie.parseCookies(cookiesValue)
            self.setAllCookies(cookiesList)

class MyWebPage(QWebPage):
    """Reimplemented QWebPage to get User Agent Changing facility"""
    def __init__(self):
        QWebPage.__init__(self)
        self.setForwardUnsupportedContent(True)
        self.useragent = "Mozilla/5.0 (X11; Linux armv7l) AppleWebKit/601.1 (KHTML, like Gecko) Version/8.0 Safari/601.1"
    def userAgentForUrl(self, url):
        return self.useragent
    def setUserAgentForUrl(self, useragent):
        self.useragent = useragent

class MyWebView(QWebView):
#    _windows = set()
    def __init__(self, **kargs):
        QWebView.__init__(self, **kargs)
        self.setPage(MyWebPage())
    def createWindow(self, windowtype):
        """This function is internally called when new window is requested.
           This will must return an window object"""
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
    """ Reimplemented QLineEdit to get all selected when double clicked"""
#    mouseDoubleClicked = pyqtSignal()
    def __init__(self, parent=None):
        super(QurlEdit, self).__init__(parent)
    def mouseDoubleClickEvent(self, event):
        self.selectAll()
#        self.mouseDoubleClicked.emit()


class Main(QMainWindow):
    def __init__(self): 
        QMainWindow.__init__(self)
        if not exists(configdir):
            mkdir(configdir)
        # Import Settings
        self.settings = QSettings("quartz-browser","quartz")
        haveallsettings = True
        for key in ['LoadImages', 'JavaScriptEnabled', 'CustomUserAgent', 'UserAgent', 'CustomHomePageUrl', 'HomePageUrl',
                    'MinFontSize', 'StandardFont', 'SansFont', 'SerifFont', 'FixedFont']:
            haveallsettings = haveallsettings and self.settings.contains(key)
        if haveallsettings:
            self.opensettings()
        else:
            self.defaultsettings()
        self.websettings = QWebSettings.globalSettings()
        self.websettings.setMaximumPagesInCache(10)
        self.websettings.setAttribute(QWebSettings.DnsPrefetchEnabled, True)
        self.history = []
        self.bookmarks = parsebookmarks(configdir+"bookmarks.txt")
        self.findmodeon = False
        self.initUI()

    def initUI(self):
###############################  Create Menu and Actions ##############################
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
        self.websettingsaction = QAction(self)
        self.websettingsaction.setText("Settings")
        self.websettingsaction.setShortcut("Ctrl+,")
        self.websettingsaction.triggered.connect(self.settingseditor)
        self.saveasimageaction = QAction(self)
        self.saveasimageaction.setText("Save as Image")
        self.saveasimageaction.setShortcut("Ctrl+Shift+S")
        self.saveasimageaction.triggered.connect(self.saveasimage)
        self.saveashtmlaction = QAction(self)
        self.saveashtmlaction.setText("Save as Html")
        self.saveashtmlaction.setShortcut("Ctrl+S")
        self.saveashtmlaction.triggered.connect(self.saveashtml)
        self.printaction = QAction(self)
        self.printaction.setText("Print")
        self.printaction.setShortcut("Ctrl+P")
        self.printaction.triggered.connect(self.printpage)
        self.quitaction = QAction(self)
        self.quitaction.setText("Quit")
        self.quitaction.setShortcut("Ctrl+Q")
        self.quitaction.triggered.connect(self.close)

        self.menu = QMenu(self)
        self.menu.addAction(self.loadimagesaction)
        self.menu.addAction(self.javascriptmode)
        self.menu.addAction(self.websettingsaction)
        self.menu.addSeparator()
        self.menu.addAction(self.zoominaction)
        self.menu.addAction(self.zoomoutaction)
        self.menu.addAction(self.fullscreenaction)
        self.menu.addSeparator()
        self.menu.addAction(self.saveasimageaction)
        self.menu.addAction(self.saveashtmlaction)
        self.menu.addAction(self.printaction)
        self.menu.addAction(self.quitaction)


###############################  Create Gui Parts ##############################
        grid = QGridLayout()
        grid.setSpacing(2)
        grid.setContentsMargins(2,2,2,2)
        self.centralwidget = QWidget(self)
        self.centralwidget.setLayout(grid)
        self.setCentralWidget(self.centralwidget)

        self.line = QurlEdit(self) 
        self.line.setStyleSheet("font-size:15px;")
        self.line.returnPressed.connect(self.Enter)
        self.line.textEdited.connect(self.urlsuggestions)
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
        self.addbookmarkBtn = QPushButton(QIcon(":/add-bookmark.png"), "", self)
        self.addbookmarkBtn.setToolTip("Add Bookmark")
        self.addbookmarkBtn.clicked.connect(self.addbookmark)
        self.menuBtn = QToolButton(self)
        self.menuBtn.setIcon(QIcon(":/menu.png"))
        self.menuBtn.setMenu(self.menu)
        self.menuBtn.setPopupMode(QToolButton.InstantPopup)

        self.bookmarkBtn = QPushButton(QIcon(":/bookmarks.png"), "", self)
        self.bookmarkBtn.setToolTip("Manage Bookmarks")
        self.bookmarkBtn.clicked.connect(self.managebookmarks)
        self.historyBtn = QPushButton(QIcon(":/history.png"), "", self)
        self.historyBtn.setToolTip("View History")
        self.historyBtn.clicked.connect(self.viewhistory)

        self.findBtn = QPushButton(QIcon(":/search.png"), "", self)
        self.findBtn.setToolTip("Find Text in \n This Page")
        self.findBtn.setShortcut("Ctrl+F")
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

        self.completer = QCompleter()
        self.completer.setCompletionMode(1)
        self.listmodel = QStringListModel(self)
        self.completer.setModel(self.listmodel)
        self.completer.setMaxVisibleItems(10)
        self.line.setCompleter(self.completer)

        self.pbar = QProgressBar() 
        self.pbar.setMaximumWidth(480)
        self.pbar.hide()

        self.web = MyWebView(loadProgress = self.pbar.setValue, loadFinished = self.pbar.hide, loadStarted = self.pbar.show, titleChanged = self.setWindowTitle) 
        self.web.setMinimumSize(1024,640)
        self.applysettings()
#       
        self.web.urlChanged.connect(self.UrlChanged)
        self.web.loadStarted.connect(self.startedloading) 
        self.web.loadFinished.connect(self.finishedloading) 
        self.web.page().linkHovered.connect(self.LinkHovered)
        self.web.page().printRequested.connect(self.printpage)
        self.web.page().downloadRequested.connect(self.download_requested_file)
        self.web.page().unsupportedContent.connect(self.download_file)

        self.cookiejar = MyCookieJar(self)
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
        grid.addWidget(self.addbookmarkBtn,0,7, 1, 1) 
        grid.addWidget(self.menuBtn,0,8, 1, 1) 
        grid.addWidget(self.bookmarkBtn,0,9, 1, 1) 
        grid.addWidget(self.historyBtn,0,10, 1, 1) 
        grid.addWidget(self.findBtn,0,11, 1, 1) 
        grid.addWidget(self.web, 2, 0, 1, 12)
#---------Window settings --------------------------------
        self.setWindowIcon(QIcon(":/view-refresh.png")) 
        self.setStyleSheet("background-color:") 
        self.status = self.statusBar()
        self.status.setMaximumHeight(18)
        self.status.addPermanentWidget(self.pbar) 
    def Enter(self): 
        url = str(self.line.text())
        if ("://" not in url and "." not in url) or (" " in url): # If text is not valid url
            url = "http://www.google.com/search?q="+url 
        self.GoTo(url)
    def GoTo(self, url):
        url = str(url)
        validurl = False
        for each in ("http://", "https://", "ftp://", "ftps://", "file://"):
            if url.startswith(each):
                validurl = True
        if not validurl:
            url = "http://"+url
        self.web.load(QUrl(url))
        self.line.setText(url)
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
        url =  self.web.url().toString()
        self.line.setText(url)
        for item in self.history:  # Removes the old item, inserts new same item on the top
            if url in item[1]:
                self.history.remove(item)
        self.history.insert(0, [strftime("%b %d, %H:%M"),url])
    def LinkHovered(self,l): 
        self.status.showMessage(l)
    def startedloading(self):
        self.reload.setIcon(QIcon(":/process-stop.png"))
        self.loading = True   # Required for reload button
    def finishedloading(self, ok):
        if not ok:
            self.status.showMessage("Error  : Problem Occured in loading Page !")
        self.reload.setIcon(QIcon(":/view-refresh.png"))
        self.loading = False
    def download_file(self, networkrequest):
        url = str(networkrequest.url().toString())
        Popen(["uget-gtk", url])
    def download_requested_file(self, networkrequest):
        filename = QFileInfo(networkrequest.url().path()).fileName()
        filepath = QFileDialog.getSaveFileName(self,
                                      "Enter FileName to Save", "/home/pi/Downloads/"+str(filename),
                                      "All Files (*)" )
        if not filepath.isEmpty():
            self.newdownload = DownloadManager(self.networkmanager)
            self.newdownload.download(networkrequest, filepath)

    def urlsuggestions(self, text):
        """ Creates the list of url suggestions for URL box """
        suggestions = []
        if self.findmodeon == False:
            for [time, url] in self.history:
                if text in url:
                    suggestions.insert(0, url)
            for [title, address] in self.bookmarks:
                if str(text) in address:
                    suggestions.insert(0, address)
        self.listmodel.setStringList( QStringList(suggestions) )


    def saveasimage(self):
        filename = QFileDialog.getSaveFileName(self,
                                      "Select Image to Save", userhomedir + "/Documents/" + self.web.page().mainFrame().title() +".png",
                                      "PNG Image (*.png)" )
        if not filename.isEmpty():
            viewportsize = self.web.page().viewportSize()
            contentsize = self.web.page().mainFrame().contentsSize()
            self.web.page().setViewportSize(contentsize)
            img = QPixmap(contentsize)
            painter = QPainter()
            painter.begin(img)
            self.web.page().mainFrame().render(painter, QWebFrame.AllLayers)
            painter.end()
            img.save(filename)
            self.web.page().setViewportSize(viewportsize)
    def saveashtml(self):
        html = self.web.page().mainFrame().toHtml()
        filename = QFileDialog.getSaveFileName(self,
                                      "Enter HTML File Name", userhomedir + "/Documents/" + self.web.page().mainFrame().title()+".html",
                                      "HTML Document (*.html)" )
        if not filename.isEmpty():
            htmlfile = open(filename, 'w')
            htmlfile.write(html)
            htmlfile.close()
    def printpage(self, page):
        printer = QPrinter(mode=QPrinter.HighResolution)
        printer.setOutputFileName(userhomedir + "/Documents/" + self.web.page().mainFrame().title() + ".pdf")
        print_dialog = QPrintDialog(printer, self)
        if print_dialog.exec_() == QDialog.Accepted:
          if page != 0:
            page.print_(printer)
          else:
            self.web.print_(printer)

    def addbookmark(self):
        dialog = QDialog(self)
        addbmkdialog = Add_Bookmark_Dialog()
        addbmkdialog.setupUi(dialog)
        addbmkdialog.titleEdit.setText(self.windowTitle())
        addbmkdialog.addressEdit.setText(self.line.text())
        if (dialog.exec_() == QDialog.Accepted):
            self.bookmarks.insert(0, [str(addbmkdialog.titleEdit.text()), str(addbmkdialog.addressEdit.text())])
            self.status.showMessage("Bookmark has been Saved")
    def managebookmarks(self):
        dialog = QDialog(self)
        bmk_dialog = Bookmarks_Dialog()
        bmk_dialog.setupUi(dialog, self.bookmarks)
        bmk_dialog.tableView.doubleclicked.connect(self.GoTo)
        if (dialog.exec_() == QDialog.Accepted):
            self.bookmarks = bmk_dialog.tableView.data
    def viewhistory(self):
        dialog = QDialog(self)
        history_dialog = History_Dialog()
        history_dialog.setupUi(dialog, self.history)
        history_dialog.tableView.doubleclicked.connect(self.GoTo)
        dialog.show()

    def findmode(self):
        self.findmodeon = True
        self.line.clear()
        self.find.show()
        self.findprev.show()
        self.cancelfind.show()
        self.line.setFocusPolicy(Qt.StrongFocus)
        self.line.setFocus()
    def cancelfindmode(self):
        self.findmodeon = False
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

#####################  View Settings  ###################
    def zoomin(self):
        zoomlevel = self.web.textSizeMultiplier()
        self.web.setTextSizeMultiplier(zoomlevel+0.1) # Use setZoomFactor() to zoom text and images
    def zoomout(self):
        zoomlevel = self.web.textSizeMultiplier()
        self.web.setTextSizeMultiplier(zoomlevel-0.1)
    def fullscreenmode(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def loadimages(self, state):
        self.websettings.setAttribute(QWebSettings.AutoLoadImages, state)
        if state:
            self.loadimagesval = True
        else:
            self.loadimagesval = False
    def setjavascript(self, state):
        self.websettings.setAttribute(QWebSettings.JavascriptEnabled, state)
        if state:
            self.javascriptenabledval = True
        else:
            self.javascriptenabledval = False

########################## Settings Portion #########################
    def settingseditor(self):  
        """ Opens the settings manager dialog, then applies the change"""
        dialog = QDialog(self)
        websettingsdialog = Ui_Dialog()
        websettingsdialog.setupUi(dialog)
        if self.loadimagesval:
            websettingsdialog.checkLoadImages.setChecked(True)
        if self.javascriptenabledval:
            websettingsdialog.checkJavascript.setChecked(True)
        if self.customuseragentval :
            websettingsdialog.checkUserAgent.setChecked(True)
        websettingsdialog.useragentEdit.setText(self.useragentval)
        if self.customhomepageurlval:
            websettingsdialog.checkHomePage.setChecked(True)
        websettingsdialog.homepageEdit.setText(self.homepageurlval)
        websettingsdialog.spinFontSize.setValue(self.minfontsizeval)
        websettingsdialog.standardfontCombo.setCurrentFont(QFont(self.standardfontval))
        websettingsdialog.sansfontCombo.setCurrentFont(QFont(self.sansfontval))
        websettingsdialog.seriffontCombo.setCurrentFont(QFont(self.seriffontval))
        websettingsdialog.fixedfontCombo.setCurrentFont(QFont(self.fixedfontval))

        if dialog.exec_() == QDialog.Accepted:
            if websettingsdialog.checkLoadImages.isChecked():
                self.loadimagesval = True
            else:
                self.loadimagesval = False
            if websettingsdialog.checkJavascript.isChecked():
                self.javascriptenabledval = True
            else:
                self.javascriptenabledval = False
            if websettingsdialog.checkUserAgent.isChecked():
                self.customuseragentval = True
            else:
                self.customuseragentval = False
            self.useragentval = websettingsdialog.useragentEdit.text()
            if websettingsdialog.checkHomePage.isChecked():
                self.customhomepageurlval = True
            else:
                self.customhomepageurlval = False
            self.homepageurlval = websettingsdialog.homepageEdit.text()
            self.minfontsizeval = websettingsdialog.spinFontSize.value()
            self.standardfontval = websettingsdialog.standardfontCombo.currentText()
            self.sansfontval = websettingsdialog.sansfontCombo.currentText()
            self.seriffontval = websettingsdialog.seriffontCombo.currentText()
            self.fixedfontval = websettingsdialog.fixedfontCombo.currentText()
            self.applysettings()
    def defaultsettings(self): 
        """ This is used when settings can not be imported"""
        self.loadimagesval = True
        self.javascriptenabledval = True
        self.customuseragentval = False
        self.useragentval = "Nokia 5130"
        self.customhomepageurlval = False
        self.homepageurlval = "file:///usr/share/doc/python-qt4-doc/html/classes.html"
        self.minfontsizeval = 12
        self.standardfontval = "Sans"
        self.sansfontval = "Sans"
        self.seriffontval = "Serif"
        self.fixedfontval = "Monospace"
    def opensettings(self): 
        """ Reads settings file in ~/.config/quartz-browser/ directory and
            saves values in settings variables"""
        self.loadimagesval = self.settings.value('LoadImages').toBool()
        self.javascriptenabledval = self.settings.value('JavaScriptEnabled').toBool()
        self.customuseragentval = self.settings.value('CustomUserAgent').toBool()
        self.useragentval = self.settings.value('UserAgent').toString()
        self.customhomepageurlval = self.settings.value('CustomHomePageUrl').toBool()
        self.homepageurlval = self.settings.value('HomePageUrl').toString()
        self.minfontsizeval = int(self.settings.value('MinFontSize').toString())
        self.standardfontval = self.settings.value('StandardFont').toString()
        self.sansfontval = self.settings.value('SansFont').toString()
        self.seriffontval = self.settings.value('SerifFont').toString()
        self.fixedfontval = self.settings.value('FixedFont').toString()
    def savesettings(self):
        """ Writes setings to disk in ~/.config/quartz-browser/ directory"""
        self.settings.setValue('LoadImages', self.loadimagesval)
        self.settings.setValue('JavaScriptEnabled', self.javascriptenabledval)
        self.settings.setValue('CustomUserAgent', self.customuseragentval)
        self.settings.setValue('UserAgent', self.useragentval)
        self.settings.setValue('CustomHomePageUrl', self.customhomepageurlval)
        self.settings.setValue('HomePageUrl', self.homepageurlval)
        self.settings.setValue('MinFontSize', self.minfontsizeval)
        self.settings.setValue('StandardFont', self.standardfontval)
        self.settings.setValue('SansFont', self.sansfontval)
        self.settings.setValue('SerifFont', self.seriffontval)
        self.settings.setValue('FixedFont', self.fixedfontval)
    def applysettings(self):
        """ Reads settings variables, and changes browser settings.This is run after
            changing settings by Settings Dialog"""
        if self.customuseragentval == True:
            self.web.page().setUserAgentForUrl(self.useragentval)
        else:
            self.web.page().setUserAgentForUrl("Mozilla/5.0 (X11; Linux armv7l) AppleWebKit/601.1 (KHTML, like Gecko) Version/8.0 Safari/601.1")
        if self.customhomepageurlval:
            self.homepageurl = self.homepageurlval
        else:
            self.homepageurl = "http://www.google.com"
        self.websettings.setAttribute(QWebSettings.AutoLoadImages, self.loadimagesval)
        if self.loadimagesval:
            self.loadimagesaction.setChecked(True)
        else:
            self.loadimagesaction.setChecked(False)
        self.websettings.setAttribute(QWebSettings.JavascriptEnabled, self.javascriptenabledval)
        if self.javascriptenabledval:
            self.javascriptmode.setChecked(True)
        else:
            self.javascriptmode.setChecked(False)
        self.websettings.setFontSize(QWebSettings.MinimumFontSize, self.minfontsizeval)
        self.websettings.setFontFamily(QWebSettings.StandardFont, self.standardfontval)
        self.websettings.setFontFamily(QWebSettings.SansSerifFont, self.sansfontval)
        self.websettings.setFontFamily(QWebSettings.SerifFont, self.seriffontval)
        self.websettings.setFontFamily(QWebSettings.FixedFont, self.fixedfontval)
#        self.websettings.setFontSize(QWebSettings.DefaultFontSize, 14)
    def closeEvent(self, event):
        """This saves all settings, bookmarks, cookies etc. during window close"""
        self.savesettings()
        writebookmarks(configdir+"bookmarks.txt", self.bookmarks)
        cookiesArray = QByteArray()
        cookieList = self.cookiejar.allCookies()
        for cookie in cookieList:
            cookiesArray.append( cookie.toRawForm() + "\n" )
        self.settings.setValue("cookies", cookiesArray)
        super(Main, self).closeEvent(event)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    main= Main() 
    main.show()
    if len(sys.argv)> 1:
        if sys.argv[1].startswith("/"):
            url = "file://"+sys.argv[1]
        main.GoTo(url)

    else:
        main.GoTo(main.homepageurl)
    sys.exit(app.exec_())
