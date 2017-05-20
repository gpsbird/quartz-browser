#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __init__ import __version__
import sys, shlex, os, re
from os.path import abspath, exists
from subprocess import Popen
from time import time, strftime

from PyQt4.QtCore import QUrl, pyqtSignal, Qt, QStringList, QSettings, QSize, QPoint
from PyQt4.QtCore import QFileInfo, QByteArray, QEventLoop, QTimer

from PyQt4.QtGui import QApplication, QMainWindow, QWidget, QPrintPreviewDialog, QFileDialog, QDialog, QStringListModel, QListView
from PyQt4.QtGui import QLineEdit, QCompleter, QComboBox, QPushButton, QToolButton, QAction, QMenu
from PyQt4.QtGui import QGridLayout, QIcon, QPrinter, QProgressBar, QMessageBox, QInputDialog, QLabel
from PyQt4.QtGui import QPainter, QPixmap, QFont, QTabWidget

from PyQt4.QtWebKit import QWebView, QWebPage, QWebSettings
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkCookieJar, QNetworkCookie, QNetworkRequest

from settings_dialog import Ui_SettingsDialog
from bookmarks_dialog import Bookmarks_Dialog, Add_Bookmark_Dialog, History_Dialog
from import_export import parsebookmarks, writebookmarks, parseDownloads, writeDownloads, jsPrintFriendly
from download_manager import Download, DownloadsModel, Downloads_Dialog
import dwnld_confirm_dialog, youtube_dialog
import resources
from pytube.api import YouTube

homedir = os.environ['HOME']
downloaddir = homedir+"/Downloads/"
docdir = homedir+"/Documents/"
configdir = homedir+"/.config/quartz-browser/"
downloads_list_file = configdir+"downloads.txt"

block_popups = False
js_debug_mode = False
#useragent_string = ""
video_player_command = 'mplayer --fs'

def validUrl(url_str):
    """ This checks if the url is valid. Used in GoTo() func"""
    validurl = False
    for each in ("http://", "https://", "ftp://", "ftps://", "file://"):
        if url_str.startswith(each):
            validurl = True
    return validurl

youtube_regex = re.compile('http(s)?\:\/\/(((m\.|www\.)?youtube\.com\/watch\?v=)|(youtu.be\/))([a-zA-Z0-9\-_])+')

def validYoutubeUrl(url):
    if youtube_regex.match(url):
        return True

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
            if url.endsWith(each) and self.block_fonts:
              block = True
              break
        #global blocklist
        #for each in blocklist:
        #    if url.startsWith(each):
        #      block = True
        #      break
        if block and op==self.GetOperation:
#            print("Blocked: "+url)
            return QNetworkAccessManager.createRequest(self, op, QNetworkRequest(QUrl()))

#        request.setAttribute(QNetworkRequest.CacheLoadControlAttribute, 2)
        #print("Loading : "+ url)
        return QNetworkAccessManager.createRequest(self, op, request, device)
        """reply = QNetworkAccessManager.createRequest(self, op, request, device)
        reply.metaDataChanged.connect(self.printdata)
        return reply

    def printdata(self):
        ''' Prints raw Headers of requested url '''
        reply = self.sender()
        print(reply.rawHeader('Accept-Ranges'))"""


class MyWebPage(QWebPage):
    """Reimplemented QWebPage to get User Agent Changing and multiple file uploads facility"""
    def __init__(self, parent):
        QWebPage.__init__(self, parent)
        self.setForwardUnsupportedContent(True)
        self.setLinkDelegationPolicy(2)
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
        """ Allows to upload files where multiple selections are allowed """
        if extension == QWebPage.ChooseMultipleFilesExtension:
            output.fileNames = QFileDialog.getOpenFileNames(self.view(), "Select Files to Upload", homedir)
            return True
        elif extension == QWebPage.ErrorPageExtension:
            error_dict = {'0':'QtNetwork', '1':'HTTP', '2':'Webkit'}
            print("URL : {}".format(option.url.toString()))
            print("{} Error {} : {}".format(error_dict[str(option.domain)], option.error, option.errorString))
        return False

    def supportsExtension(self, extension):
        return True

    def javaScriptConsoleMessage(self, msg, line_no, source_id):
        global js_debug_mode
        if js_debug_mode:
            print("Line : {} , Source ID - {}".format(line_no, source_id))
            print(msg)

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
        page = MyWebPage(self)
        self.setPage(page)
        self.edit_mode_on = False
        self.loading = False
        self.progressVal = 0
        self.loadStarted.connect(self.loadstarted)
        self.loadFinished.connect(self.loadfinished)
        self.loadProgress.connect(self.loadprogress)
        self.urlChanged.connect(self.UrlChanged)
        self.titleChanged.connect(self.TitleChanged)
        self.linkClicked.connect(self.openLink)

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

    def openLink(self, url):
        addr = url.toString()
        # This supports rtsp video play protocol
        if addr.startsWith('rtsp://'):
            global video_player_command
            cmd = unicode(video_player_command + ' ' + addr)
            Popen(shlex.split(cmd))
            return
        self.load(url)

    def createWindow(self, windowtype):
        """This function is internally called when new window is requested.
           This will must return a QWebView object"""
        global block_popups
        if block_popups:
            return self
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
        filepath = url.toString()
        if QFileInfo(filepath).suffix() not in ['jpg', 'jpeg', 'png'] :
            filepath = os.path.splitext(unicode(filepath))[0] + '.jpg'
        filepath = QFileDialog.getSaveFileName(self,
                                      "Select Image to Save", downloaddir + QFileInfo(filepath).fileName(),
                                      "All Images (*.jpg *.jpeg *.png);;JPEG File (*.jpg *.jpeg);;PNG File (*.png)" )
        if not filepath.isEmpty():
          if pm.save(filepath):
            QMessageBox.information(self, "Successful !","Image %s \nhas been successfully saved!"%QFileInfo(filepath).fileName())

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
        self.setFocusPolicy(Qt.StrongFocus)

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

    def setText(self, string):
        QLineEdit.setText(self, string)
        self.setCursorPosition(0)

class Main(QMainWindow):
    def __init__(self): 
        global downloads_list_file
        QMainWindow.__init__(self)
        self.setWindowIcon(QIcon(":/quartz.png")) 
        self.setWindowTitle("Quartz Browser - "+__version__)
        if not exists(configdir):
            os.mkdir(configdir)
        # Import Settings
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.settings = QSettings("quartz-browser","quartz")
        self.opensettings()
        self.websettings = QWebSettings.globalSettings()
        self.websettings.setAttribute(QWebSettings.DnsPrefetchEnabled, True)
        self.websettings.setMaximumPagesInCache(10)
#        self.websettings.setAttribute(QWebSettings.JavascriptCanOpenWindows, False)
        self.downloads = []
        self.dwnldsmodel = DownloadsModel(self.downloads, QApplication.instance())
        self.dwnldsmodel.deleteDownloadsRequested.connect(self.deleteDownloads)
        imported_downloads = parseDownloads(downloads_list_file)
        for [filepath, url, totalsize, timestamp] in imported_downloads:
            try :                                                  # Check if downloads.txt is valid
                totalsize, time = long(totalsize), float(timestamp)
            except :
                self.downloads = []
                writeDownloads(downloads_list_file, [])
                print("Error in importing Downloads.")
                break
            old_download = Download(networkmanager)
            old_download.loadDownload(filepath, url, totalsize, timestamp)
            old_download.datachanged.connect(self.dwnldsmodel.datachanged)
            self.downloads.append(old_download)
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

################ Add Actions to Menu ####################
        self.menu = QMenu(self)
        self.menu.addAction("Find Text", self.findmode, "Ctrl+F")
        self.menu.addAction("Zoom In", self.zoomin, "Ctrl++")
        self.menu.addAction("Zoom Out", self.zoomout, "Ctrl+-")
        self.menu.addAction("Toggle Fullscreen", self.fullscreenmode, "F11")
        self.menu.addSeparator()

        self.menu.addAction(self.loadimagesaction)
        self.menu.addAction(self.javascriptmode)
        self.menu.addAction("Settings", self.settingseditor, "Ctrl+,")
        self.menu.addSeparator()

        self.menu.addAction("Save as Image", self.saveasimage, "Shift+Ctrl+S")
        self.menu.addAction("Save as HTML", self.saveashtml, "Ctrl+S")
        self.menu.addAction("Print to PDF", self.printpage, "Ctrl+P")
        self.menu.addAction("Print Friendly", self.printFriendly, "Ctrl+Shift+P")
        self.menu.addSeparator()
        self.menu.addAction("Quit", self.close, "Ctrl+Q")


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

        self.youtubeBtn = QPushButton(QIcon(":/youtube-dwnld.png"), "", self)
        self.youtubeBtn.setToolTip("Download this Youtube Video")
        self.youtubeBtn.clicked.connect(self.downloadYoutubeVideo)
        self.youtubeBtn.hide()

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

        self.downloadsBtn = QPushButton(QIcon(":/download.png"), "", self)
        self.downloadsBtn.setToolTip("Download Manager")
        self.downloadsBtn.clicked.connect(self.download_manager)

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

        self.listmodel = QStringListModel(self)
        self.completer = QCompleter(self.listmodel, self.line)
        self.completer.setCompletionMode(1)
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

        for index, widget in enumerate([self.addtabBtn, self.back, self.forw, self.reload, self.youtubeBtn, self.line, self.find,
                self.findprev, self.cancelfind, self.addbookmarkBtn, self.bookmarkBtn,
                self.menuBtn, self.historyBtn, self.downloadsBtn]):
            grid.addWidget(widget, 0,index,1,1)
        grid.addWidget(self.tabWidget, 2, 0, 1, 14)
        grid.addWidget(self.pbar, 3,0,1,14)
#-----------------------Window settings --------------------------------
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
        if validYoutubeUrl(url):
            self.youtubeBtn.show()
        else:
            self.youtubeBtn.hide()

    def Enter(self): 
        url = unicode(self.line.text())
        if validUrl(url):
            self.GoTo(url)
            return
        if ( "." not in url) or (" " in url): # If text is not valid url
            url = "https://www.google.com/search?q="+url 
        self.GoTo(url)

    def GoTo(self, url):
        URL = QUrl.fromUserInput(unicode(url))
        self.tabWidget.currentWidget().openLink(URL)
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
            if validYoutubeUrl(url):
                self.youtubeBtn.show()
            else:
                self.youtubeBtn.hide()
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


##################### Downloading and Printing  ########################
    def download_requested_file(self, networkrequest):
        """ Gets called when the page requests a file to be downloaded """
        reply = networkmanager.get(networkrequest)
        self.handleUnsupportedContent(reply)

    def handleUnsupportedContent(self, reply, force_filename=None):
        """ This is called when url content is a downloadable file. e.g- pdf,mp3,mp4 """
        global downloads_list_file
        if reply.rawHeaderList() == []:
            loop = QEventLoop()
            reply.metaDataChanged.connect(loop.quit)
            QTimer.singleShot(20000, loop.quit)
            loop.exec_()
        for (title, header) in reply.rawHeaderPairs():
            print( title+"->"+header )
        # Get filename
        content_name = str(reply.rawHeader('Content-Disposition'))
        if force_filename:
            filename = force_filename
        elif content_name.startswith('attachment') and '=' in content_name:
            if content_name.count('"') >= 2: # Extracts texts inside quotes when two quotes are present
                start = content_name.find('"')+1
                end = content_name.rfind('"')
                filename = content_name[start:end]
            else:
                filename = content_name.split('=')[-1]
        else:
            if reply.hasRawHeader('Location'):
                decoded_url = QUrl.fromPercentEncoding(str(reply.rawHeader('Location')))
            else:
                decoded_url = QUrl.fromPercentEncoding(str(reply.url().toString()))
            decoded_url = QUrl(decoded_url).toString(QUrl.RemoveQuery)
            filename = QFileInfo(decoded_url).fileName()
        # Create downld Confirmation dialog
        dlDialog = DownloadDialog(self)
        dlDialog.filenameEdit.setText(filename)
        # Get filesize
        if reply.hasRawHeader('Content-Length'):
            filesize = reply.header(1).toLongLong()[0]
            if len(str(filesize))>7:
                file_size = "{}M".format(round(float(filesize)/1048576, 2))
            else:
                file_size = "{}k".format(filesize/1024)
            dlDialog.labelFileSize.setText(file_size)
        else:
            filesize = 0
        # Get filetype and resume support info
        if reply.hasRawHeader('Content-Type'):
            dlDialog.labelFileType.setText(str(reply.rawHeader('Content-Type')))
        if reply.hasRawHeader('Accept-Ranges') or reply.hasRawHeader('Content-Range'):
            dlDialog.labelResume.setText("True")
        # Execute dialog and get confirmation
        if dlDialog.exec_()== QDialog.Accepted:
            filepath = dlDialog.folder+dlDialog.filenameEdit.text()
            url = reply.url().toString()
            if self.useexternaldownloader:
                download_externally(url, self.externaldownloader)
                reply.abort()
                return
            if reply.hasRawHeader('Location'):
                url = str(reply.rawHeader('Location'))
                reply.abort()
                reply = networkmanager.get(QNetworkRequest(QUrl(url)))

            timestamp = str(time())
            imported_downloads = parseDownloads(downloads_list_file)
            imported_downloads.insert(0, [filepath, url, str(filesize), timestamp])
            writeDownloads(downloads_list_file, imported_downloads)
            newdownload = Download(networkmanager)
            newdownload.startDownload(reply, filepath, timestamp)
            newdownload.datachanged.connect(self.dwnldsmodel.datachanged)
            self.downloads.insert(0, newdownload)
        else:
            reply.abort()

    def download_manager(self):
        """ Opens download manager dialog """
        dialog = QDialog(self)
        downloads_dialog = Downloads_Dialog()
        downloads_dialog.setupUi(dialog, self.dwnldsmodel)
        dialog.exec_()

    def deleteDownloads(self, timestamps):
        global downloads_list_file
        imported_downloads = parseDownloads(downloads_list_file)
        exported_downloads = []
        for download in imported_downloads:
            if download[-1] not in timestamps:
                exported_downloads.append(download)
        writeDownloads(downloads_list_file, exported_downloads)

    def downloadYoutubeVideo(self):
        url = unicode(self.line.text())
        yt = YouTube(url)
        videos = yt.get_videos()
        dialog = youtube_dialog.YoutubeDialog(videos, self)
        if dialog.exec_() == 1 :
            index = abs(dialog.buttonGroup.checkedId())-2
            vid = videos[index]
            reply = networkmanager.get( QNetworkRequest(QUrl.fromUserInput(vid.url)) )
            self.handleUnsupportedContent(reply, vid.filename + '.' + vid.extension)
            
    def saveasimage(self):
        """ Saves the whole page as PNG/JPG image"""
        filename = QFileDialog.getSaveFileName(self,
                                      "Select Image to Save", downloaddir + self.tabWidget.currentWidget().page().mainFrame().title() +".png",
                                      "PNG Image (*.png);;JPEG Image (*.jpg)" )
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
                QMessageBox.information(self, "Successful !","Page has been successfully saved as\n"+filename)
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

    def printpage(self, page=None):
        """ Prints current/requested page """
        if not page:
            page = self.tabWidget.currentWidget().page().currentFrame()
        printer = QPrinter(mode=QPrinter.HighResolution)
        printer.setCreator("Quartz Browser")
        printer.setDocName(self.tabWidget.currentWidget().page().mainFrame().title())
        printer.setOutputFileName(docdir + self.tabWidget.currentWidget().page().mainFrame().title() + ".pdf")
        print_dialog = QPrintPreviewDialog(printer, self)
        print_dialog.paintRequested.connect(page.print_)
        print_dialog.exec_()

    def printFriendly(self):
        """ Create a printfriendly version of the page using http://www.printfriendly.com"""
        self.tabWidget.currentWidget().page().mainFrame().evaluateJavaScript(jsPrintFriendly)
        loop = QEventLoop()
        QTimer.singleShot(5000, loop.quit)
        loop.exec_()
        self.tabWidget.currentWidget().page().mainFrame().evaluateJavaScript('window.print()')

##################################################################################################
    def addbookmark(self):
        """ Opens add bookmark dialog and gets url from url box"""
        dialog = QDialog(self)
        addbmkdialog = Add_Bookmark_Dialog()
        addbmkdialog.setupUi(dialog)
        addbmkdialog.titleEdit.setText(self.tabWidget.currentWidget().page().mainFrame().title())
        addbmkdialog.addressEdit.setText(self.line.text())
        if (dialog.exec_() == QDialog.Accepted):
            bmk = [str(addbmkdialog.titleEdit.text().toUtf8()), addbmkdialog.addressEdit.text()]
            self.bookmarks.insert(0, bmk)
            writebookmarks(configdir+"bookmarks.txt", self.bookmarks)

    def managebookmarks(self):
        """ Opens Bookmarks dialog """
        dialog = QDialog(self)
        bmk_dialog = Bookmarks_Dialog()
        bmk_dialog.setupUi(dialog, self.bookmarks)
        bmk_dialog.tableView.doubleclicked.connect(self.GoTo)
        if (dialog.exec_() == QDialog.Accepted):
            bookmarks = bmk_dialog.tableView.data
            if len(bookmarks) != len(self.bookmarks):
                self.bookmarks = bookmarks
                writebookmarks(configdir+"bookmarks.txt", self.bookmarks)

    def viewhistory(self):
        """ Open history dialog """
        dialog = QDialog(self)
        history_dialog = History_Dialog()
        history_dialog.setupUi(dialog, self.history)
        history_dialog.tableView.doubleclicked.connect(self.GoTo)
        dialog.exec_()

    def findmode(self):
        """ Starts find mode and unhides find buttons"""
        self.findmodeon = True
        self.line.clear()
        self.find.show()
        self.findprev.show()
        self.cancelfind.show()
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
        global block_popups, video_player_command
        dialog = QDialog(self)
        websettingsdialog = Ui_SettingsDialog()
        websettingsdialog.setupUi(dialog)
        # Load Images
        if self.loadimagesval:
            websettingsdialog.checkLoadImages.setChecked(True)
        # JavaScript
        if self.javascriptenabledval:
            websettingsdialog.checkJavascript.setChecked(True)
        # Fonts blocking
        if networkmanager.block_fonts:
            websettingsdialog.checkFontLoad.setChecked(True)
        # Popups blocking
        if block_popups:
            websettingsdialog.checkBlockPopups.setChecked(True)
        # Custom user agent
        if self.customuseragentval :
            websettingsdialog.checkUserAgent.setChecked(True)
        websettingsdialog.useragentEdit.setText(self.useragentval)
        # Home Page Url
        if self.customhomepageurlval:
            websettingsdialog.checkHomePage.setChecked(True)
        websettingsdialog.homepageEdit.setText(self.homepageurlval)
        websettingsdialog.homepageEdit.setCursorPosition(0)
        # External download manager
        if self.useexternaldownloader:
            websettingsdialog.checkDownMan.setChecked(True)
        websettingsdialog.downManEdit.setText(self.externaldownloader)
        # RTSP media player command
        websettingsdialog.mediaPlayerEdit.setText(video_player_command)
        websettingsdialog.mediaPlayerEdit.setCursorPosition(0)
        # Maximize on startup
        if self.maximizeonstartup:
            websettingsdialog.checkMaximize.setChecked(True)
        # Font settings
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
            # Block Popups
            if websettingsdialog.checkBlockPopups.isChecked():
                block_popups = True
            else:
                block_popups = False
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
            # Media Player Command
            video_player_command = websettingsdialog.mediaPlayerEdit.text()
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
            self.savesettings()
    def opensettings(self): 
        """ Reads settings file in ~/.config/quartz-browser/ directory and
            saves values in settings variables"""
        global block_popups, video_player_command
        self.loadimagesval = self.settings.value('LoadImages', True).toBool()
        self.javascriptenabledval = self.settings.value('JavaScriptEnabled', True).toBool()
        networkmanager.block_fonts = self.settings.value('BlockFontLoading', False).toBool()
        block_popups = self.settings.value('BlockPopups', False).toBool()
        self.customuseragentval = self.settings.value('CustomUserAgent', False).toBool()
        self.useragentval = self.settings.value('UserAgent', "Nokia 5130").toString()
        self.customhomepageurlval = self.settings.value('CustomHomePageUrl', False).toBool()
        self.homepageurlval = self.settings.value('HomePageUrl', "file:///usr/share/doc/python-qt4-doc/html/classes.html").toString()
        self.useexternaldownloader = self.settings.value('UseExternalDownloader', False).toBool()
        self.externaldownloader = self.settings.value('ExternalDownloader', "wget -c %u").toString()
        video_player_command = self.settings.value('MediaPlayerCommand', video_player_command).toString()
        self.maximizeonstartup = self.settings.value('MaximizeOnStartup', False).toBool()
        self.minfontsizeval = int(self.settings.value('MinFontSize', 11).toString())
        self.standardfontval = self.settings.value('StandardFont', 'Sans').toString()
        self.sansfontval = self.settings.value('SansFont', 'Sans').toString()
        self.seriffontval = self.settings.value('SerifFont', 'Serif').toString()
        self.fixedfontval = self.settings.value('FixedFont', 'Monospace').toString()
    def savesettings(self):
        """ Writes setings to disk in ~/.config/quartz-browser/ directory"""
        global block_popups, video_player_command
        self.settings.setValue('LoadImages', self.loadimagesval)
        self.settings.setValue('JavaScriptEnabled', self.javascriptenabledval)
        self.settings.setValue('BlockFontLoading', networkmanager.block_fonts)
        self.settings.setValue('BlockPopups', block_popups)
        self.settings.setValue('CustomUserAgent', self.customuseragentval)
        self.settings.setValue('UserAgent', self.useragentval)
        self.settings.setValue('CustomHomePageUrl', self.customhomepageurlval)
        self.settings.setValue('HomePageUrl', self.homepageurlval)
        self.settings.setValue('UseExternalDownloader', self.useexternaldownloader)
        self.settings.setValue('ExternalDownloader', self.externaldownloader)
        self.settings.setValue('MediaPlayerCommand', video_player_command)
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
        cookiesArray = QByteArray()
        cookieList = cookiejar.allCookies()
        for cookie in cookieList:
            cookiesArray.append( cookie.toRawForm() + "\n" )
        self.settings.setValue("cookies", cookiesArray)
        return super(Main, self).closeEvent(event)

def download_externally(url, downloader):
    """ Runs External downloader """
    if "%u" not in str(downloader):
        cmd = downloader + ' ' + url
    else:
        cmd = str(downloader).replace("%u", url)
    cmd = shlex.split(cmd)
    try:
        Popen(cmd)
    except OSError:
        QMessageBox.information(None, "Download Error", "Downloader command not found")

class DownloadDialog(QDialog, dwnld_confirm_dialog.Ui_downloadDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.folder = downloaddir
        self.setupUi(self)
        self.folderButton.clicked.connect(self.changeFolder)
        self.labelFolder.setText(downloaddir)
    def changeFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", homedir)
        if not folder.isEmpty():
            self.folder = folder + "/"
            self.labelFolder.setText(self.folder)

def main():
    global app, networkmanager, cookiejar
    app = QApplication(sys.argv)
    app.setOrganizationName("quartz-browser")
    app.setApplicationName("quartz")
    # NetworkAccessManager must be global variable, otherwise javascript will not be rendered
    cookiejar = MyCookieJar(QApplication.instance())
    networkmanager = NetworkAccessManager(QApplication.instance())
    networkmanager.setCookieJar(cookiejar)
    gui= Main()
    # Maximize after startup or Show normal 
    if gui.maximizeonstartup:
        gui.showMaximized()
    else:
        gui.show()
    # Go to url from argument
    if len(sys.argv)> 1:
        if sys.argv[1].startswith("/"):
            url = "file://"+sys.argv[1]
        else:
            url = sys.argv[1]
        gui.GoTo(url)
    else:
        gui.GoTo(gui.homepageurl)
    # App mainloop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

