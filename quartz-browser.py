#!/usr/bin/env python
"""
Name = Quartz Browser
version = 1.7.2
Dependency = python-qt4
Description = A Light Weight Internet Browser
Features =  Change User agent to mobile/desktop
            Print Page to PDF
            Save page as JPG, html
            Turn Javascript, Load Images on/off
            Find Text inside page
            Easy accessible toolbar
            Tabbed browsing
            Download Manager with pause/resume support
Last Update : 
            Window is shrinkable
            Added maximize on startup option.
            progressbar is narrow and its length is same as page width.
            Removed statusbar
            Bookmarks dialog width increased.

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
# TODO : 
#       multiple search engines
#       About/Help dialog

import sys, shlex
from os.path import abspath, exists
from os import environ, mkdir
from subprocess import Popen
from time import strftime

from PyQt4.QtCore import QUrl, pyqtSignal, Qt, QStringList, QSettings, QSize, QPoint
from PyQt4.QtCore import QFileInfo, QByteArray, QEventLoop, QTimer

from PyQt4.QtGui import QApplication, QMainWindow, QWidget, QPrintDialog, QFileDialog, QDialog, QStringListModel, QListView
from PyQt4.QtGui import QLineEdit, QCompleter, QComboBox, QPushButton, QToolButton, QAction, QMenu
from PyQt4.QtGui import QGridLayout, QIcon, QPrinter, QProgressBar, QMessageBox, QInputDialog, QLabel
from PyQt4.QtGui import QPainter, QPixmap, QFont, QTabWidget
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
"""
from PyQt4.QtWebKit import QWebView, QWebPage, QWebSettings
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkCookieJar, QNetworkCookie, QNetworkRequest

from settings_dialog import Ui_SettingsDialog
from bookmarks_dialog import Bookmarks_Dialog, Add_Bookmark_Dialog, History_Dialog
from bookmarkparser import parsebookmarks, writebookmarks, parseDownloads, writeDownloads
from download_manager import Download, DownloadsModel, Downloads_Dialog
import quartz_common


homedir = environ['HOME']
downloaddir = homedir+"/Downloads/"
docdir = homedir+"/Documents/"
configdir = homedir+"/.config/quartz-browser/"

def validUrl(url_str):
    """ This checks if the url is valid. Used in GoTo() func"""
    validurl = False
    for each in ("http://", "https://", "ftp://", "ftps://", "file://"):
        if url_str.startswith(each):
            validurl = True
    return validurl


class MyCookieJar(QNetworkCookieJar):
    """ Reimplemented QNetworkCookieJar to get cookie import/export feature"""
    def __init__(self, parent=None):
        super(MyCookieJar, self).__init__(parent)
    def importCookies(self, window):
        """ Window object must contain QSetting object 'self.settings' before calling this"""
        cookiesValue = window.settings.value("cookies").toByteArray()
        if cookiesValue:
            cookiesList = QNetworkCookie.parseCookies(cookiesValue)
            self.setAllCookies(cookiesList)
    def clearCookies(self):
        self.setAllCookies([])

class NetworkAccessManager(QNetworkAccessManager):
    def __init__(self, *args, **kwargs):
        super(NetworkAccessManager, self).__init__(*args, **kwargs)
        self.authenticationRequired.connect(self.provideAuthentication)
        self.block_fonts = False
    def provideAuthentication(self, reply, auth):
        username = QInputDialog.getText(None, "Authentication", "Enter your username:", QLineEdit.Normal)
        if username[1]:
            auth.setUser(username[0])
            password = QInputDialog.getText(None, "Authentication", "Enter your password:", QLineEdit.Password)
            if password[1]:
                auth.setPassword(password[0])
    def createRequest(self, op, request, device=None):
        """ Reimplemented to enable adblock/url-block """
        url = request.url().toString()
        block = False
        for each in ['.ttf', '.woff']:
            if url.endsWith(each):
              block = True
        if block and self.block_fonts and op==self.GetOperation:
#            print "Blocked: "+url
            return QNetworkAccessManager.createRequest(self, op, QNetworkRequest(QUrl()))

#        request.setAttribute(QNetworkRequest.CacheLoadControlAttribute, 2)
        return QNetworkAccessManager.createRequest(self, op, request, device)
        """reply.metaDataChanged.connect(self.printdata)
        return reply
    def printdata(self):
        ''' Prints raw Headers of requested url '''
        reply = self.sender()
        print(reply.rawHeader('Accept-Ranges'))"""


class MyWebPage(QWebPage):
    """Reimplemented QWebPage to get User Agent Changing and multiple file uploads facility"""
    def __init__(self):
        QWebPage.__init__(self)
        self.setForwardUnsupportedContent(True)
        self.setNetworkAccessManager(networkmanager)
        self.useragent = ""
    def userAgentForUrl(self, url):
        """ This is called when it loads any page, to get useragent string"""
        return self.useragent
    def setUserAgentForUrl(self, useragent):
        self.useragent = useragent
    def clearUserAgent(self):
        """ Resets the useragent to default value"""
        self.useragent = QWebPage.userAgentForUrl(self, QUrl(""))
    def extension(self, extension, option, output):
        """ Allows to upload files where multiple selections are allowed"""
        if extension == QWebPage.ChooseMultipleFilesExtension:
            output.fileNames = QFileDialog.getOpenFileNames(self.view(), "Select Files to Upload", homedir)
            return True
        return False

class MyWebView(QWebView):
    """ Many signals are reimplemented to support multi-tab feature"""
    loadingStarted = pyqtSignal()
    loadingFinished = pyqtSignal()
    loadingProgress = pyqtSignal(int, QWebView)
    urlchanged = pyqtSignal(str, QWebView)
    titlechanged = pyqtSignal(str, QWebView)
    windowCreated = pyqtSignal(QWebView)

    def __init__(self, parent=None):
        QWebView.__init__(self, parent)
        self.setPage(MyWebPage())
        self.edit_mode_on = False
        self.loading = False
        self.progressVal = 0
        self.loadStarted.connect(self.loadstarted)
        self.loadFinished.connect(self.loadfinished)
        self.loadProgress.connect(self.loadprogress)
        self.urlChanged.connect(self.UrlChanged)
        self.titleChanged.connect(self.TitleChanged)
    def loadstarted(self):
        self.loading = True
        self.loadingStarted.emit()
    def loadfinished(self):
        self.loading = False
        self.loadingFinished.emit()
    def loadprogress(self, progress):
        self.progressVal = progress
        self.loadingProgress.emit(progress, self)
    def UrlChanged(self, url):
        url = url.toString()
        self.urlchanged.emit(url, self)
    def TitleChanged(self, title):
        self.titlechanged.emit(title, self)
    def createWindow(self, windowtype):
        """This function is internally called when new window is requested.
           This will must return a QWebView object"""
        webview = MyWebView(self.parent())
        self.windowCreated.emit(webview)
        return webview
    def contextMenuEvent(self, event):
        """ Overrides the default context menu"""
        result = self.page().mainFrame().hitTestContent(event.pos())
        self.rel_pos = event.pos()
        menu = QMenu(self)
        if result.isContentSelected():
          menu.addAction(self.pageAction(QWebPage.Copy))
        if not result.imageUrl().isEmpty():
          menu.addAction("Save Image", self.saveImageToDisk)
          download_image_action = self.pageAction(QWebPage.DownloadImageToDisk)
          download_image_action.setText("Download Image")
          menu.addAction(download_image_action)
          menu.addSeparator()
        if not result.linkUrl().isEmpty():
          menu.addAction(self.pageAction(QWebPage.OpenLinkInNewWindow))
          menu.addAction(self.pageAction(QWebPage.CopyLinkToClipboard))
          menu.addAction(self.pageAction(QWebPage.DownloadLinkToDisk))
        if result.imageUrl().isEmpty() and result.linkUrl().isEmpty():
          edit_page_action = QAction("Edit Page", self)
          edit_page_action.setCheckable(True)
          edit_page_action.setChecked(self.edit_mode_on)
          edit_page_action.triggered.connect(self.toggleEditMode)
          menu.addAction(edit_page_action)
        menu.exec_(self.mapToGlobal(event.pos()))
    def saveImageToDisk(self):
        """ This saves an image in page directly without downloading"""
        pm = self.page().mainFrame().hitTestContent(self.rel_pos).pixmap()
        url = self.page().mainFrame().hitTestContent(self.rel_pos).imageUrl()
        url.setQueryItems([])
        name = QFileInfo(url.toString()).fileName()
        filepath = QFileDialog.getSaveFileName(self,
                                      "Select Image to Save", downloaddir + name,
                                      "Image Files (*.jpg *.png *.jpeg)" )
        if not filepath.isEmpty():
          if not (filepath.endsWith(".jpg",0) or filepath.endsWith(".png",0) or filepath.endsWith(".jpeg",0)):
            filepath += ".jpg"
          if pm.save(filepath):
            QMessageBox.information(None, "Successful !","Image has been successfully saved!")
    def toggleEditMode(self, checked):
        if checked:
            self.page().setContentEditable(True)
            self.edit_mode_on = True
        else:
            self.page().setContentEditable(False)
            self.edit_mode_on = False

class QurlEdit(QLineEdit):
    """ Reimplemented QLineEdit to get all selected when double clicked"""
    downloadRequested = pyqtSignal(QNetworkRequest)
    def __init__(self, parent=None):
        super(QurlEdit, self).__init__(parent)
    def mouseDoubleClickEvent(self, event):
        self.selectAll()
    def contextMenuEvent(self,event):
        menu = self.createStandardContextMenu()
        menu.addSeparator()
        menu.addAction("Download Link", self.downloadLink)
        menu.exec_(self.mapToGlobal(event.pos()))
    def downloadLink(self):
        request = QNetworkRequest(QUrl.fromUserInput(self.text()))
        self.downloadRequested.emit(request)

class Main(QMainWindow):
    def __init__(self): 
        QMainWindow.__init__(self)
        if not exists(configdir):
            mkdir(configdir)
        # Import Settings
        self.setAttribute(Qt.WA_DeleteOnClose)
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
        self.websettings.setAttribute(QWebSettings.DnsPrefetchEnabled, True)
        self.websettings.setMaximumPagesInCache(10)
#        self.websettings.setAttribute(QWebSettings.PrintElementBackgrounds, False)
        self.downloads = []
        self.dwnldsmodel = DownloadsModel(self.downloads, QApplication.instance())
        imported_downloads = parseDownloads(configdir+"downloads.txt")
        for [filepath, url, totalsize] in imported_downloads:
            incomplt_download = Download(networkmanager)
            incomplt_download.loadDownload(filepath, url, long(totalsize))
            incomplt_download.datachanged.connect(self.dwnldsmodel.datachanged)
            self.downloads.append(incomplt_download)
        self.history = []
        self.bookmarks = parsebookmarks(configdir+"bookmarks.txt")
        cookiejar.importCookies(self)
        self.findmodeon = False
        self.initUI()
        self.resize(1024,714)

    def initUI(self):
###############################  Create  Actions ##############################
        self.loadimagesaction = QAction("Load Images",self)
        self.loadimagesaction.setCheckable(True)
        self.loadimagesaction.triggered.connect(self.loadimages)

        self.javascriptmode = QAction("Enable Javascript",self)
        self.javascriptmode.setCheckable(True)
        self.javascriptmode.triggered.connect(self.setjavascript)

        self.zoominaction = QAction("Zoom  In",self)
        self.zoominaction.setShortcut("Ctrl++")
        self.zoominaction.triggered.connect(self.zoomin)

        self.zoomoutaction = QAction("Zoom  Out",self)
        self.zoomoutaction.setShortcut("Ctrl+-")
        self.zoomoutaction.triggered.connect(self.zoomout)

        self.fullscreenaction = QAction("Toggle Fullscreen",self)
        self.fullscreenaction.setShortcut("F11")
        self.fullscreenaction.triggered.connect(self.fullscreenmode)

        self.websettingsaction = QAction("Settings",self)
        self.websettingsaction.setShortcut("Ctrl+,")
        self.websettingsaction.triggered.connect(self.settingseditor)

        self.downloadsaction = QAction("Downloads", self)
        self.downloadsaction.triggered.connect(self.download_manager)

        self.saveasimageaction = QAction("Save as Image",self)
        self.saveasimageaction.setShortcut("Ctrl+Shift+S")
        self.saveasimageaction.triggered.connect(self.saveasimage)

        self.saveashtmlaction = QAction("Save as Html",self)
        self.saveashtmlaction.setShortcut("Ctrl+S")
        self.saveashtmlaction.triggered.connect(self.saveashtml)

        self.printaction = QAction("Print",self)
        self.printaction.setShortcut("Ctrl+P")
        self.printaction.triggered.connect(self.printpage)

        self.quitaction = QAction("Quit",self)
        self.quitaction.setShortcut("Ctrl+Q")
        self.quitaction.triggered.connect(self.close)

################ Add Actions to Menu ####################
        self.menu = QMenu(self)
        self.menu.addAction(self.zoominaction)
        self.menu.addAction(self.zoomoutaction)
        self.menu.addAction(self.fullscreenaction)
        self.menu.addSeparator()

        self.menu.addAction(self.loadimagesaction)
        self.menu.addAction(self.javascriptmode)
        self.menu.addAction(self.websettingsaction)
        self.menu.addSeparator()

        self.menu.addAction(self.downloadsaction)
        self.menu.addAction(self.saveasimageaction)
        self.menu.addAction(self.saveashtmlaction)
        self.menu.addAction(self.printaction)
        self.menu.addSeparator()
        self.menu.addAction(self.quitaction)


###############################  Create Gui Parts ##############################
        grid = QGridLayout()
        grid.setSpacing(2)
        grid.setContentsMargins(0,2,0,0)
        self.centralwidget = QWidget(self)
        self.centralwidget.setLayout(grid)
        self.setCentralWidget(self.centralwidget)

        self.line = QurlEdit(self) 
        self.line.returnPressed.connect(self.Enter)
        self.line.textEdited.connect(self.urlsuggestions)

        self.addtabBtn = QPushButton(QIcon(":/add-tab.png"), "",self)
        self.addtabBtn.setToolTip("New Tab\n[Ctrl+Tab]")
        self.addtabBtn.setShortcut("Ctrl+Tab")
        self.addtabBtn.clicked.connect(self.addTab)

        self.reload = QPushButton(QIcon(":/refresh.png"), "",self) 
        self.reload.setMinimumSize(35,26) 
        self.reload.setToolTip("Reload/Stop\n  [Space]")
        self.reload.setShortcut("Space")
        self.reload.clicked.connect(self.Reload)

        self.back = QPushButton(QIcon(":/prev.png"), "", self) 
        self.back.setToolTip("Previous Page\n [Backspace]")
        self.back.setMinimumSize(35,26) 
        self.back.clicked.connect(self.Back)

        self.forw = QPushButton(QIcon(":/next.png"), "",self) 
        self.forw.setToolTip("Next Page\n [Shift+Backspace]")
        self.forw.setMinimumSize(35,26) 
        self.forw.clicked.connect(self.Forward)

        self.addbookmarkBtn = QPushButton(QIcon(":/add-bookmark.png"), "", self)
        self.addbookmarkBtn.setShortcut("Ctrl+D")
        self.addbookmarkBtn.setToolTip("Add Bookmark\n   [Ctrl+D]")
        self.addbookmarkBtn.clicked.connect(self.addbookmark)

        self.menuBtn = QToolButton(self)
        self.menuBtn.setIcon(QIcon(":/menu.png"))
        self.menuBtn.setMenu(self.menu)
        self.menuBtn.setPopupMode(QToolButton.InstantPopup)

        self.bookmarkBtn = QPushButton(QIcon(":/bookmarks.png"), "", self)
        self.bookmarkBtn.setToolTip("Manage Bookmarks\n         [Alt+B]")
        self.bookmarkBtn.setShortcut("Alt+B")
        self.bookmarkBtn.clicked.connect(self.managebookmarks)
        self.historyBtn = QPushButton(QIcon(":/history.png"), "", self)
        self.historyBtn.setShortcut("Alt+H")
        self.historyBtn.setToolTip("View History\n     [Alt+H]")
        self.historyBtn.clicked.connect(self.viewhistory)

        self.findBtn = QPushButton(QIcon(":/search.png"), "", self)
        self.findBtn.setToolTip("Find Text in \n This Page\n [Ctrl+F]")
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
        self.pbar.setTextVisible(False)
        self.pbar.setMaximumHeight(5)
        self.pbar.setStyleSheet("QProgressBar::chunk { background-color: #7e83a6; }")
        self.pbar.hide()

        self.statusbar = QLabel(self)
        self.statusbar.setStyleSheet("QLabel { font-size: 12px; border-radius: 2px; padding: 2px; background: palette(highlight); color: palette(highlighted-text); }")
        self.statusbar.setMaximumHeight(16)
        self.statusbar.hide()

        self.tabWidget = QTabWidget(self)
#        self.tabWidget.setMovable(True)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setDocumentMode(True)
        self.tabWidget.tabBar().setExpanding(True)
        self.tabWidget.tabBar().setElideMode(Qt.ElideMiddle)
        self.tabWidget.currentChanged.connect(self.onTabSwitch)
        self.tabWidget.tabCloseRequested.connect(self.closeTab)
        self.addTab()
#       

        for index, widget in enumerate([self.addtabBtn, self.back, self.forw, self.reload, self.line, self.find,
                self.findprev, self.cancelfind, self.addbookmarkBtn, self.menuBtn,
                self.bookmarkBtn, self.historyBtn, self.findBtn]):
            grid.addWidget(widget, 0,index,1,1)
        grid.addWidget(self.pbar, 3,0,1,13)
        grid.addWidget(self.tabWidget, 2, 0, 1, 13)
#-----------------------Window settings --------------------------------
        self.setWindowIcon(QIcon(":/view-refresh.png")) 
        self.setWindowTitle("Quartz Browser")
#        self.line.setStyleSheet("background-image:url(:/search.png);background-repeat:no-repeat;\
#                                padding: 2 2 2 24 ;font-size:15px;") 

#        Must be at the end, otherwise cause segmentation fault
#       self.status = self.statusBar() 

    def addTab(self, tab=None):
        """ Creates a new tab and add to QTableWidget
            applysettings() must be called after adding each tab"""
        if not tab:
            tab = MyWebView(self.tabWidget) 
        tab.windowCreated.connect(self.addTab)
        tab.loadingStarted.connect(self.startedloading) 
        tab.loadingFinished.connect(self.finishedloading) 
        tab.loadingProgress.connect(self.onProgress)
        tab.urlchanged.connect(self.onUrlChange)
        tab.titlechanged.connect(self.onTitleChange)
        tab.page().printRequested.connect(self.printpage)
        self.line.downloadRequested.connect(self.download_requested_file)
        tab.page().downloadRequested.connect(self.download_requested_file)
        tab.page().unsupportedContent.connect(self.handleUnsupportedContent)
        tab.page().linkHovered.connect(self.onLinkHover)

        self.tabWidget.addTab(tab, "( Untitled )")
        if self.tabWidget.count()==1:
            self.tabWidget.tabBar().hide()
        else:
            self.tabWidget.tabBar().show()
        self.tabWidget.setCurrentIndex(self.tabWidget.count()-1)
        self.applysettings()
    def closeTab(self, index=None):
        """ Closes tab, hides tabbar if only one tab remains"""
        if index==None:
            index = self.tabWidget.currentIndex()
        widget = self.tabWidget.widget(index)
        self.tabWidget.removeTab(index)
        widget.deleteLater()
        if self.tabWidget.count()==1:
            self.tabWidget.tabBar().hide()
    def onTabSwitch(self, index):
        """ Updates urlbox, refresh icon, progress bar on switching tab"""
        if self.tabWidget.currentWidget().loading == True:
            self.reload.setIcon(QIcon(":/stop.png"))
            self.pbar.setValue(self.tabWidget.currentWidget().progressVal)
            self.pbar.show()
        else:
            self.reload.setIcon(QIcon(":/refresh.png"))
            self.pbar.hide()
        url =  self.tabWidget.currentWidget().url().toString()
        self.line.setText(url)
    def Enter(self): 
        url = str(self.line.text())
        if validUrl(url):
            self.GoTo(url)
            return
        if ( "." not in url) or (" " in url): # If text is not valid url
            url = "https://www.google.com/search?q="+url 
        self.GoTo(url)
    def GoTo(self, url):
        if not validUrl(str(url)): # This func returns true if url is valid
            url = "http://"+url
        self.tabWidget.currentWidget().load(QUrl(url))
        self.line.setText(url)
    def Back(self): 
        self.tabWidget.currentWidget().back() 
    def Forward(self): 
        self.tabWidget.currentWidget().forward()
    def Reload(self):
        if self.tabWidget.currentWidget().loading:
            self.tabWidget.currentWidget().stop()
        else: 
            self.tabWidget.currentWidget().reload()

    def onUrlChange(self,url, webview):
        if webview is self.tabWidget.currentWidget():
            self.line.setText(url)
            for item in self.history:  # Removes the old item, inserts new same item on the top
                if url in item[1]:
                    self.history.remove(item)
            self.history.insert(0, [strftime("%b %d, %H:%M"),url])
    def onTitleChange(self, title, webview):
        index = self.tabWidget.indexOf(webview)
        if not title.isEmpty():
            self.tabWidget.tabBar().setTabText(index, title)
    def startedloading(self, webview=None):
        if self.tabWidget.currentWidget().loading == True:
          self.reload.setIcon(QIcon(":/stop.png"))
          self.pbar.show()
    def finishedloading(self, webview=None):
        if self.tabWidget.currentWidget().loading == False:
          self.reload.setIcon(QIcon(":/refresh.png"))
          self.pbar.hide()
    def onProgress(self, progress, webview):
        if webview is self.tabWidget.currentWidget():
            self.pbar.setValue(progress)
    def onLinkHover(self, url):
        if url=="":
            self.statusbar.hide()
#            self.repaint()
            return
        self.statusbar.setText(url)
        self.statusbar.adjustSize()
        self.statusbar.show()
        self.statusbar.move(QPoint(0, self.height()-self.statusbar.height()))
#        self.repaint()

##################### Downloading  ########################
    def download_requested_file(self, networkrequest):
        reply = networkmanager.get(networkrequest)
        self.handleUnsupportedContent(reply)
    def handleUnsupportedContent(self, reply):
        """ This is called when url content is a downloadable file. e.g- pdf,mp3,mp4 """
        if reply.rawHeaderList() == []:
            loop = QEventLoop()
            reply.metaDataChanged.connect(loop.quit)
            QTimer.singleShot(30000, loop.quit)
            loop.exec_()
        for (title, header) in reply.rawHeaderPairs():
            print title, header
        content_name = str(reply.rawHeader('Content-Disposition'))
        if content_name.startswith('attachment'):
            filename = content_name.split('=')[-1]
        else:
            if reply.hasRawHeader('Location'):
                decoded_url = QUrl.fromPercentEncoding(str(reply.rawHeader('Location')))
            else:
                decoded_url = QUrl.fromPercentEncoding(str(reply.url().toString()))
            filename = QFileInfo(decoded_url).fileName()
        filepath = QFileDialog.getSaveFileName(self,
                                  "Download File", downloaddir+str(filename),
                                  "All Files (*)" )
        if not filepath.isEmpty():
            if self.useexternaldownloader:
                download_externally(reply.url().toString(), self.externaldownloader)
                reply.abort()
                return
            if reply.hasRawHeader('Location'):
                url = QUrl(str(reply.rawHeader('Location')))
                reply.abort()
                reply = networkmanager.get(QNetworkRequest(url))

            newdownload = Download(networkmanager)
            newdownload.startDownload(reply, filepath)
            newdownload.datachanged.connect(self.dwnldsmodel.datachanged)
            self.downloads.insert(0, newdownload)
        else:
            reply.abort()
    def download_manager(self):
        dialog = QDialog(self)
        downloads_dialog = Downloads_Dialog()
        downloads_dialog.setupUi(dialog, self.dwnldsmodel)
        dialog.exec_()

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
        """ Saves the whole page as PNG image"""
        filename = QFileDialog.getSaveFileName(self,
                                      "Select Image to Save", downloaddir + self.tabWidget.currentWidget().page().mainFrame().title() +".png",
                                      "PNG Image (*.png)" )
        if not filename.isEmpty():
            viewportsize = self.tabWidget.currentWidget().page().viewportSize()
            contentsize = self.tabWidget.currentWidget().page().mainFrame().contentsSize()
            self.tabWidget.currentWidget().page().setViewportSize(contentsize)
            img = QPixmap(contentsize)
            painter = QPainter()
            painter.begin(img)
            self.tabWidget.currentWidget().page().mainFrame().render(painter, 0xff)# 0xff=QWebFrame.AllLayers
            painter.end()
            if img.save(filename):
                Popen(["notify-send","Successful !","Page has been successfully saved as\n"+filename])
            self.tabWidget.currentWidget().page().setViewportSize(viewportsize)
    def saveashtml(self):
        """ Saves current page as HTML , bt does not saves any content (e.g images)"""
        html = self.tabWidget.currentWidget().page().mainFrame().toHtml().toUtf8()
        filename = QFileDialog.getSaveFileName(self,
                                      "Enter HTML File Name", downloaddir + self.tabWidget.currentWidget().page().mainFrame().title()+".html",
                                      "HTML Document (*.html)" )
        if not filename.isEmpty():
            htmlfile = open(filename, 'w')
            htmlfile.write(html)
            htmlfile.close()
    def printpage(self, page):
        printer = QPrinter(mode=QPrinter.HighResolution)
        printer.setOutputFileName(docdir + self.tabWidget.currentWidget().page().mainFrame().title() + ".pdf")
        print_dialog = QPrintDialog(printer, self)
        if print_dialog.exec_() == QDialog.Accepted:
          if page:
            page.print_(printer)
          else:
            self.tabWidget.currentWidget().print_(printer)

    def addbookmark(self):
        dialog = QDialog(self)
        addbmkdialog = Add_Bookmark_Dialog()
        addbmkdialog.setupUi(dialog)
        addbmkdialog.titleEdit.setText(self.tabWidget.currentWidget().page().mainFrame().title())
        addbmkdialog.addressEdit.setText(self.line.text())
        if (dialog.exec_() == QDialog.Accepted):
            self.bookmarks.insert(0, [str(addbmkdialog.titleEdit.text().toUtf8()), addbmkdialog.addressEdit.text()])
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
        dialog.exec_()

    def findmode(self):
        self.findmodeon = True
        self.line.clear()
        self.find.show()
        self.findprev.show()
        self.cancelfind.show()
        self.line.setFocusPolicy(Qt.StrongFocus)
        self.line.setFocus()
    def cancelfindmode(self):
        """ Hides the find buttons, updates urlbox"""
        self.findmodeon = False
        self.tabWidget.currentWidget().findText("")
        self.find.hide()
        self.findprev.hide()
        self.cancelfind.hide()
        self.line.setText(self.tabWidget.currentWidget().url().toString())
    def findnext(self):
        text = self.line.text()
        self.tabWidget.currentWidget().findText(text)
    def findback(self):
        text = self.line.text()
        self.tabWidget.currentWidget().findText(text, QWebPage.FindBackward)

#####################  View Settings  ###################
    def zoomin(self):
        zoomlevel = self.tabWidget.currentWidget().textSizeMultiplier()
        self.tabWidget.currentWidget().setTextSizeMultiplier(zoomlevel+0.1) # Use setZoomFactor() to zoom text and images
    def zoomout(self):
        zoomlevel = self.tabWidget.currentWidget().textSizeMultiplier()
        self.tabWidget.currentWidget().setTextSizeMultiplier(zoomlevel-0.1)
    def fullscreenmode(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def loadimages(self, state):
        """ TOggles image loading on/off"""
        self.websettings.setAttribute(QWebSettings.AutoLoadImages, state)
        if state:
            self.loadimagesval = True
        else:
            self.loadimagesval = False
    def setjavascript(self, state):
        """ Toggles js on/off """
        self.websettings.setAttribute(QWebSettings.JavascriptEnabled, state)
        if state:
            self.javascriptenabledval = True
        else:
            self.javascriptenabledval = False
########################## Settings Portion #########################
    def settingseditor(self):  
        """ Opens the settings manager dialog, then applies the change"""
        dialog = QDialog(self)
        websettingsdialog = Ui_SettingsDialog()
        websettingsdialog.setupUi(dialog)
        if self.loadimagesval:
            websettingsdialog.checkLoadImages.setChecked(True)
        if self.javascriptenabledval:
            websettingsdialog.checkJavascript.setChecked(True)
        if networkmanager.block_fonts:
            websettingsdialog.checkFontLoad.setChecked(True)
        if self.customuseragentval :
            websettingsdialog.checkUserAgent.setChecked(True)
        websettingsdialog.useragentEdit.setText(self.useragentval)
        if self.customhomepageurlval:
            websettingsdialog.checkHomePage.setChecked(True)
        websettingsdialog.homepageEdit.setText(self.homepageurlval)
        websettingsdialog.homepageEdit.setCursorPosition(0)
        if self.useexternaldownloader:
            websettingsdialog.checkDownMan.setChecked(True)
        websettingsdialog.downManEdit.setText(self.externaldownloader)
        if self.maximizeonstartup:
            websettingsdialog.checkMaximize.setChecked(True)
        websettingsdialog.spinFontSize.setValue(self.minfontsizeval)
        websettingsdialog.standardfontCombo.setCurrentFont(QFont(self.standardfontval))
        websettingsdialog.sansfontCombo.setCurrentFont(QFont(self.sansfontval))
        websettingsdialog.seriffontCombo.setCurrentFont(QFont(self.seriffontval))
        websettingsdialog.fixedfontCombo.setCurrentFont(QFont(self.fixedfontval))
        websettingsdialog.cookiesButton.clicked.connect(cookiejar.clearCookies)

        if dialog.exec_() == QDialog.Accepted:
            if websettingsdialog.checkLoadImages.isChecked():
                self.loadimagesval = True
            else:
                self.loadimagesval = False
            # JavaScript
            if websettingsdialog.checkJavascript.isChecked():
                self.javascriptenabledval = True
            else:
                self.javascriptenabledval = False
            # Block Fonts
            if websettingsdialog.checkFontLoad.isChecked():
                networkmanager.block_fonts = True
            else:
                networkmanager.block_fonts = False
            # User Agent
            if websettingsdialog.checkUserAgent.isChecked():
                self.customuseragentval = True
            else:
                self.customuseragentval = False
            self.useragentval = websettingsdialog.useragentEdit.text()
            # Home Page
            if websettingsdialog.checkHomePage.isChecked():
                self.customhomepageurlval = True
            else:
                self.customhomepageurlval = False
            self.homepageurlval = websettingsdialog.homepageEdit.text()
            # Download Manager
            if websettingsdialog.checkDownMan.isChecked():
                self.useexternaldownloader = True
            else:
                self.useexternaldownloader = False
            self.externaldownloader = websettingsdialog.downManEdit.text()
            # Maximize on startup
            if websettingsdialog.checkMaximize.isChecked():
                self.maximizeonstartup = True
            else:
                self.maximizeonstartup = False

            self.minfontsizeval = websettingsdialog.spinFontSize.value()
            self.standardfontval = websettingsdialog.standardfontCombo.currentText()
            self.sansfontval = websettingsdialog.sansfontCombo.currentText()
            self.seriffontval = websettingsdialog.seriffontCombo.currentText()
            self.fixedfontval = websettingsdialog.fixedfontCombo.currentText()
            self.applysettings()
    def defaultsettings(self): 
        """ This settings is used when settings can not be imported"""
        print 'Reset Settings'
        self.loadimagesval = True
        self.javascriptenabledval = True
        networkmanager.block_fonts = False
        self.customuseragentval = False
        self.useragentval = "Nokia 5130"
        self.customhomepageurlval = False
        self.homepageurlval = "file:///usr/share/doc/python-qt4-doc/html/classes.html"
        self.useexternaldownloader = False
        self.externaldownloader = ""
        self.maximizeonstartup = False
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
        networkmanager.block_fonts = self.settings.value('BlockFontLoading').toBool()
        self.customuseragentval = self.settings.value('CustomUserAgent').toBool()
        self.useragentval = self.settings.value('UserAgent').toString()
        self.customhomepageurlval = self.settings.value('CustomHomePageUrl').toBool()
        self.homepageurlval = self.settings.value('HomePageUrl').toString()
        self.useexternaldownloader = self.settings.value('UseExternalDownloader').toBool()
        self.externaldownloader = self.settings.value('ExternalDownloader').toString()
        self.maximizeonstartup = self.settings.value('MaximizeOnStartup').toBool()
        self.minfontsizeval = int(self.settings.value('MinFontSize').toString())
        self.standardfontval = self.settings.value('StandardFont').toString()
        self.sansfontval = self.settings.value('SansFont').toString()
        self.seriffontval = self.settings.value('SerifFont').toString()
        self.fixedfontval = self.settings.value('FixedFont').toString()
    def savesettings(self):
        """ Writes setings to disk in ~/.config/quartz-browser/ directory"""
        self.settings.setValue('LoadImages', self.loadimagesval)
        self.settings.setValue('JavaScriptEnabled', self.javascriptenabledval)
        self.settings.setValue('BlockFontLoading', networkmanager.block_fonts)
        self.settings.setValue('CustomUserAgent', self.customuseragentval)
        self.settings.setValue('UserAgent', self.useragentval)
        self.settings.setValue('CustomHomePageUrl', self.customhomepageurlval)
        self.settings.setValue('HomePageUrl', self.homepageurlval)
        self.settings.setValue('UseExternalDownloader', self.useexternaldownloader)
        self.settings.setValue('ExternalDownloader', self.externaldownloader)
        self.settings.setValue('MaximizeOnStartup', self.maximizeonstartup)
        self.settings.setValue('MinFontSize', self.minfontsizeval)
        self.settings.setValue('StandardFont', self.standardfontval)
        self.settings.setValue('SansFont', self.sansfontval)
        self.settings.setValue('SerifFont', self.seriffontval)
        self.settings.setValue('FixedFont', self.fixedfontval)
    def applysettings(self):
        """ Reads settings variables, and changes browser settings.This is run after
            changing settings by Settings Dialog"""
        if self.customuseragentval == True:
            self.tabWidget.currentWidget().page().setUserAgentForUrl(self.useragentval)
        else:
            self.tabWidget.currentWidget().page().clearUserAgent()
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
        writeDownloads(configdir+"downloads.txt", self.downloads)
        cookiesArray = QByteArray()
        cookieList = cookiejar.allCookies()
        for cookie in cookieList:
            cookiesArray.append( cookie.toRawForm() + "\n" )
        self.settings.setValue("cookies", cookiesArray)
        return super(Main, self).closeEvent(event)

def download_externally(url, downloader):
    """ Runs External downloader """
    if "%u" not in str(downloader):
        print "External downloader command must contain %u in place of URL"
        return
    cmd = str(downloader).replace("%u", str(url))
    cmd = shlex.split(cmd)
    try:
        Popen(cmd)
    except OSError:
        Popen(["notify-send", "Download Error", "Downloader command not found"])



if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setOrganizationName("quartz-browser")
    app.setApplicationName("quartz")
    # NetworkAccessManager must be global variable, otherwise cause rendering problem
    cookiejar = MyCookieJar(QApplication.instance())
    networkmanager = NetworkAccessManager(QApplication.instance())
    networkmanager.setCookieJar(cookiejar)
    main= Main()
    # Maximize after startup or Show normal 
    if main.maximizeonstartup:
        main.showMaximized()
    else:
        main.show()
    # Go to url from argument
    if len(sys.argv)> 1:
        if sys.argv[1].startswith("/"):
            url = "file://"+sys.argv[1]
        else:
            url = sys.argv[1]
        main.GoTo(url)
    else:
        main.GoTo(main.homepageurl)
    # App mainloop
    sys.exit(app.exec_())
