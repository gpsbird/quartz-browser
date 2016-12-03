# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/pi/Desktop/Linux/Programming/Python/quartz-settings.ui'
#
# Created: Thu Dec  1 20:54:06 2016
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

class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        SettingsDialog.setObjectName(_fromUtf8("SettingsDialog"))
        SettingsDialog.resize(673, 466)
        SettingsDialog.setModal(True)
        self.buttonBox = QtGui.QDialogButtonBox(SettingsDialog)
        self.buttonBox.setGeometry(QtCore.QRect(20, 420, 591, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.groupBox = QtGui.QGroupBox(SettingsDialog)
        self.groupBox.setGeometry(QtCore.QRect(30, 20, 281, 211))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.checkLoadImages = QtGui.QCheckBox(self.groupBox)
        self.checkLoadImages.setObjectName(_fromUtf8("checkLoadImages"))
        self.verticalLayout.addWidget(self.checkLoadImages)
        self.checkJavascript = QtGui.QCheckBox(self.groupBox)
        self.checkJavascript.setObjectName(_fromUtf8("checkJavascript"))
        self.verticalLayout.addWidget(self.checkJavascript)
        self.checkFontLoad = QtGui.QCheckBox(self.groupBox)
        self.checkFontLoad.setObjectName(_fromUtf8("checkFontLoad"))
        self.verticalLayout.addWidget(self.checkFontLoad)
        self.checkUserAgent = QtGui.QCheckBox(self.groupBox)
        self.checkUserAgent.setObjectName(_fromUtf8("checkUserAgent"))
        self.verticalLayout.addWidget(self.checkUserAgent)
        self.useragentEdit = QtGui.QLineEdit(self.groupBox)
        self.useragentEdit.setObjectName(_fromUtf8("useragentEdit"))
        self.verticalLayout.addWidget(self.useragentEdit)
        self.groupBox_2 = QtGui.QGroupBox(SettingsDialog)
        self.groupBox_2.setGeometry(QtCore.QRect(30, 270, 611, 128))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.groupBox_2)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.spinFontSize = QtGui.QSpinBox(self.groupBox_2)
        self.spinFontSize.setAlignment(QtCore.Qt.AlignCenter)
        self.spinFontSize.setMinimum(2)
        self.spinFontSize.setMaximum(24)
        self.spinFontSize.setObjectName(_fromUtf8("spinFontSize"))
        self.gridLayout.addWidget(self.spinFontSize, 0, 1, 1, 1)
        self.label_standard = QtGui.QLabel(self.groupBox_2)
        self.label_standard.setObjectName(_fromUtf8("label_standard"))
        self.gridLayout.addWidget(self.label_standard, 1, 0, 1, 1)
        self.standardfontCombo = QtGui.QFontComboBox(self.groupBox_2)
        self.standardfontCombo.setMaxVisibleItems(20)
        self.standardfontCombo.setObjectName(_fromUtf8("standardfontCombo"))
        self.gridLayout.addWidget(self.standardfontCombo, 1, 1, 1, 1)
        self.label_sans = QtGui.QLabel(self.groupBox_2)
        self.label_sans.setObjectName(_fromUtf8("label_sans"))
        self.gridLayout.addWidget(self.label_sans, 1, 2, 1, 1)
        self.sansfontCombo = QtGui.QFontComboBox(self.groupBox_2)
        self.sansfontCombo.setMaxVisibleItems(20)
        self.sansfontCombo.setObjectName(_fromUtf8("sansfontCombo"))
        self.gridLayout.addWidget(self.sansfontCombo, 1, 3, 1, 1)
        self.label_serif = QtGui.QLabel(self.groupBox_2)
        self.label_serif.setObjectName(_fromUtf8("label_serif"))
        self.gridLayout.addWidget(self.label_serif, 2, 0, 1, 1)
        self.seriffontCombo = QtGui.QFontComboBox(self.groupBox_2)
        self.seriffontCombo.setMaxVisibleItems(20)
        self.seriffontCombo.setObjectName(_fromUtf8("seriffontCombo"))
        self.gridLayout.addWidget(self.seriffontCombo, 2, 1, 1, 1)
        self.label_fixed = QtGui.QLabel(self.groupBox_2)
        self.label_fixed.setObjectName(_fromUtf8("label_fixed"))
        self.gridLayout.addWidget(self.label_fixed, 2, 2, 1, 1)
        self.fixedfontCombo = QtGui.QFontComboBox(self.groupBox_2)
        self.fixedfontCombo.setMaxVisibleItems(20)
        self.fixedfontCombo.setObjectName(_fromUtf8("fixedfontCombo"))
        self.gridLayout.addWidget(self.fixedfontCombo, 2, 3, 1, 1)
        self.groupBox_3 = QtGui.QGroupBox(SettingsDialog)
        self.groupBox_3.setGeometry(QtCore.QRect(340, 20, 301, 211))
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.checkDownMan = QtGui.QCheckBox(self.groupBox_3)
        self.checkDownMan.setObjectName(_fromUtf8("checkDownMan"))
        self.verticalLayout_2.addWidget(self.checkDownMan)
        self.downManEdit = QtGui.QLineEdit(self.groupBox_3)
        self.downManEdit.setObjectName(_fromUtf8("downManEdit"))
        self.verticalLayout_2.addWidget(self.downManEdit)
        self.checkHomePage = QtGui.QCheckBox(self.groupBox_3)
        self.checkHomePage.setObjectName(_fromUtf8("checkHomePage"))
        self.verticalLayout_2.addWidget(self.checkHomePage)
        self.homepageEdit = QtGui.QLineEdit(self.groupBox_3)
        self.homepageEdit.setObjectName(_fromUtf8("homepageEdit"))
        self.verticalLayout_2.addWidget(self.homepageEdit)
        self.cookiesButton = QtGui.QPushButton(self.groupBox_3)
        self.cookiesButton.setObjectName(_fromUtf8("cookiesButton"))
        self.verticalLayout_2.addWidget(self.cookiesButton)

        self.retranslateUi(SettingsDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SettingsDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SettingsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SettingsDialog)

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle(_translate("SettingsDialog", "Settings", None))
        self.groupBox.setTitle(_translate("SettingsDialog", "Browsing", None))
        self.checkLoadImages.setText(_translate("SettingsDialog", "Load Images", None))
        self.checkJavascript.setText(_translate("SettingsDialog", "Enable JavaScript", None))
        self.checkFontLoad.setText(_translate("SettingsDialog", "Block loading Fonts", None))
        self.checkUserAgent.setText(_translate("SettingsDialog", "Custom User Agent", None))
        self.useragentEdit.setPlaceholderText(_translate("SettingsDialog", "e.g- Nokia 5130", None))
        self.groupBox_2.setTitle(_translate("SettingsDialog", "Appearance", None))
        self.label.setText(_translate("SettingsDialog", "Min. Font Size :", None))
        self.spinFontSize.setSuffix(_translate("SettingsDialog", " px", None))
        self.label_standard.setText(_translate("SettingsDialog", "Standard Font :", None))
        self.label_sans.setText(_translate("SettingsDialog", "Sans Font :", None))
        self.label_serif.setText(_translate("SettingsDialog", "Serif Font :", None))
        self.label_fixed.setText(_translate("SettingsDialog", "Fixed Font :", None))
        self.groupBox_3.setTitle(_translate("SettingsDialog", "Others", None))
        self.checkDownMan.setText(_translate("SettingsDialog", "External Download Manager", None))
        self.downManEdit.setPlaceholderText(_translate("SettingsDialog", "e.g- wget -c %u", None))
        self.checkHomePage.setText(_translate("SettingsDialog", "Custom Home Page URL", None))
        self.cookiesButton.setText(_translate("SettingsDialog", "Clear Cookies", None))

