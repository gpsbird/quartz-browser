# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'bookmarks.ui'
#
# Created: Mon Nov  7 11:15:32 2016
#      by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class BookmarksTable(QtGui.QTableWidget):
    doubleclicked = QtCore.pyqtSignal(str)
    def __init__(self, bookmark_list):
        QtGui.QTableWidget.__init__(self, len(bookmark_list), 2)
        self.setHorizontalHeaderLabels(["Title", "Address"])
        self.horizontalHeader().setDefaultSectionSize(240)
        self.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        self.data = bookmark_list
        self.setmydata()
    def setmydata(self):
        for m, row in enumerate (self.data):
            for n, item in enumerate(self.data[m]):
                newitem = QtGui.QTableWidgetItem(item)
                self.setItem(m, n, newitem)
    def mousePressEvent(self, e):
        self.selectRow(self.rowAt(e.pos().y()))
    def mouseDoubleClickEvent(self, e):
        url = self.data[self.rowAt(e.pos().y())][1]
        self.doubleclicked.emit(url)
    def contextMenuEvent(self, e):
        self.rel_pos = e.pos()
        menu = QtGui.QMenu(self)
        menu.addAction("Delete", self.deleteitem)
        menu.exec_(self.mapToGlobal(self.rel_pos))
    def deleteitem(self):
        del self.data[self.rowAt(self.rel_pos.y())]
        self.removeRow(self.rowAt(self.rel_pos.y()))


class Bookmarks_Dialog(object):
    def setupUi(self, Dialog, bookmark_data):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(740, 440)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tableView = BookmarksTable(bookmark_data)
        self.tableView.setObjectName(_fromUtf8("tableView"))
        self.verticalLayout.addWidget(self.tableView)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.tableView.doubleclicked.connect(Dialog.reject)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Bookmarks", None))

class Add_Bookmark_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(640, 165)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.titleEdit = QtGui.QLineEdit(Dialog)
        self.titleEdit.setObjectName(_fromUtf8("titleEdit"))
        self.gridLayout.addWidget(self.titleEdit, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.addressEdit = QtGui.QLineEdit(Dialog)
        self.addressEdit.setObjectName(_fromUtf8("addressEdit"))
        self.gridLayout.addWidget(self.addressEdit, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 2)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Add Bookmark", None))
        self.label.setText(_translate("Dialog", "Title :", None))
        self.label_2.setText(_translate("Dialog", "Address :", None))

class HistoryTable(QtGui.QTableWidget):
    doubleclicked = QtCore.pyqtSignal(str)
    def __init__(self, history_list):
        QtGui.QTableWidget.__init__(self, len(history_list), 2)
        self.setHorizontalHeaderLabels(["Time", "Address"])
        self.horizontalHeader().setDefaultSectionSize(120)
        self.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        self.data = history_list
        self.setmydata()
    def setmydata(self):
        for m, row in enumerate (self.data):
            for n, item in enumerate(self.data[m]):
                newitem = QtGui.QTableWidgetItem(item)
                self.setItem(m, n, newitem)
    def mousePressEvent(self, e):
        self.selectRow(self.rowAt(e.pos().y()))
    def mouseDoubleClickEvent(self, e):
        url = self.data[self.rowAt(e.pos().y())][1]
        self.doubleclicked.emit(url)
#    def contextMenuEvent(self, e):
#        self.rel_pos = e.pos()
#        menu = QtGui.QMenu(self)
#        menu.addAction("Delete", self.deleteitem)
#        menu.exec_(self.mapToGlobal(self.rel_pos))
#    def deleteitem(self):
#        del self.data[self.rowAt(self.rel_pos.y())]
#        self.removeRow(self.rowAt(self.rel_pos.y()))

class History_Dialog(object):
    def setupUi(self, Dialog, history_data):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(740, 440)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tableView = HistoryTable(history_data)
        self.tableView.setObjectName(_fromUtf8("tableView"))
        self.verticalLayout.addWidget(self.tableView)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.tableView.doubleclicked.connect(Dialog.reject)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "History", None))
