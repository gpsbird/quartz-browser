# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/subha/.Linux/Programming/Python/quartz/download-start.ui'
#
# Created: Wed Mar  8 14:47:38 2017
#      by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

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

class Ui_downloadDialog(object):
    def setupUi(self, downloadDialog):
        downloadDialog.setObjectName(_fromUtf8("downloadDialog"))
        downloadDialog.resize(638, 233)
        self.gridLayout = QtGui.QGridLayout(downloadDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_5 = QtGui.QLabel(downloadDialog)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 3, 0, 1, 1)
        self.label_3 = QtGui.QLabel(downloadDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.labelFolder = QtGui.QLabel(downloadDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelFolder.sizePolicy().hasHeightForWidth())
        self.labelFolder.setSizePolicy(sizePolicy)
        self.labelFolder.setObjectName(_fromUtf8("labelFolder"))
        self.gridLayout.addWidget(self.labelFolder, 0, 1, 1, 1)
        self.label_6 = QtGui.QLabel(downloadDialog)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 4, 0, 1, 1)
        self.label = QtGui.QLabel(downloadDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(downloadDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.folderButton = QtGui.QPushButton(downloadDialog)
        self.folderButton.setMaximumSize(QtCore.QSize(80, 16777215))
        self.folderButton.setObjectName(_fromUtf8("folderButton"))
        self.gridLayout.addWidget(self.folderButton, 0, 2, 1, 1)
        self.filenameEdit = QtGui.QLineEdit(downloadDialog)
        self.filenameEdit.setObjectName(_fromUtf8("filenameEdit"))
        self.gridLayout.addWidget(self.filenameEdit, 1, 1, 1, 2)
        self.labelFileSize = QtGui.QLabel(downloadDialog)
        self.labelFileSize.setObjectName(_fromUtf8("labelFileSize"))
        self.gridLayout.addWidget(self.labelFileSize, 2, 1, 1, 2)
        self.labelResume = QtGui.QLabel(downloadDialog)
        self.labelResume.setObjectName(_fromUtf8("labelResume"))
        self.gridLayout.addWidget(self.labelResume, 3, 1, 1, 2)
        self.labelFileType = QtGui.QLabel(downloadDialog)
        self.labelFileType.setObjectName(_fromUtf8("labelFileType"))
        self.gridLayout.addWidget(self.labelFileType, 4, 1, 1, 2)
        self.dialogButtonBox = QtGui.QDialogButtonBox(downloadDialog)
        self.dialogButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.dialogButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.dialogButtonBox.setObjectName(_fromUtf8("dialogButtonBox"))
        self.gridLayout.addWidget(self.dialogButtonBox, 5, 0, 1, 3)

        self.retranslateUi(downloadDialog)
        QtCore.QObject.connect(self.dialogButtonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), downloadDialog.accept)
        QtCore.QObject.connect(self.dialogButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), downloadDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(downloadDialog)

    def retranslateUi(self, downloadDialog):
        downloadDialog.setWindowTitle(_translate("downloadDialog", "Dialog", None))
        self.label_5.setText(_translate("downloadDialog", "Resume Support :", None))
        self.label_3.setText(_translate("downloadDialog", "Size :", None))
        self.labelFolder.setText(_translate("downloadDialog", "~/Downloads", None))
        self.label_6.setText(_translate("downloadDialog", "File Type :", None))
        self.label.setText(_translate("downloadDialog", "Folder :", None))
        self.label_2.setText(_translate("downloadDialog", "File Name :", None))
        self.folderButton.setText(_translate("downloadDialog", "Change...", None))
        self.labelFileSize.setText(_translate("downloadDialog", "Unknown", None))
        self.labelResume.setText(_translate("downloadDialog", "False", None))
        self.labelFileType.setText(_translate("downloadDialog", "Unknown", None))

