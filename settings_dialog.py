# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/pi/Desktop/Linux/Programming/Python/quartz-settings.ui'
#
# Created: Wed Nov  2 18:02:08 2016
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(673, 466)
        Dialog.setModal(True)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(20, 420, 591, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(30, 20, 301, 171))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.checkLoadImages = QtGui.QCheckBox(self.groupBox)
        self.checkLoadImages.setGeometry(QtCore.QRect(20, 20, 251, 22))
        self.checkLoadImages.setChecked(False)
        self.checkLoadImages.setObjectName(_fromUtf8("checkLoadImages"))
        self.checkJavascript = QtGui.QCheckBox(self.groupBox)
        self.checkJavascript.setGeometry(QtCore.QRect(20, 50, 261, 22))
        self.checkJavascript.setObjectName(_fromUtf8("checkJavascript"))
        self.checkUserAgent = QtGui.QCheckBox(self.groupBox)
        self.checkUserAgent.setGeometry(QtCore.QRect(20, 90, 261, 22))
        self.checkUserAgent.setChecked(False)
        self.checkUserAgent.setObjectName(_fromUtf8("checkUserAgent"))
        self.useragentEdit = QtGui.QLineEdit(self.groupBox)
        self.useragentEdit.setGeometry(QtCore.QRect(20, 120, 271, 26))
        self.useragentEdit.setObjectName(_fromUtf8("useragentEdit"))
        self.groupBox_2 = QtGui.QGroupBox(Dialog)
        self.groupBox_2.setGeometry(QtCore.QRect(30, 220, 611, 181))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.label = QtGui.QLabel(self.groupBox_2)
        self.label.setGeometry(QtCore.QRect(10, 30, 121, 21))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_standard = QtGui.QLabel(self.groupBox_2)
        self.label_standard.setGeometry(QtCore.QRect(10, 70, 111, 21))
        self.label_standard.setObjectName(_fromUtf8("label_standard"))
        self.label_sans = QtGui.QLabel(self.groupBox_2)
        self.label_sans.setGeometry(QtCore.QRect(310, 70, 91, 21))
        self.label_sans.setObjectName(_fromUtf8("label_sans"))
        self.label_serif = QtGui.QLabel(self.groupBox_2)
        self.label_serif.setGeometry(QtCore.QRect(10, 120, 91, 21))
        self.label_serif.setObjectName(_fromUtf8("label_serif"))
        self.label_fixed = QtGui.QLabel(self.groupBox_2)
        self.label_fixed.setGeometry(QtCore.QRect(310, 120, 91, 21))
        self.label_fixed.setObjectName(_fromUtf8("label_fixed"))
        self.seriffontCombo = QtGui.QFontComboBox(self.groupBox_2)
        self.seriffontCombo.setGeometry(QtCore.QRect(130, 120, 171, 26))
        self.seriffontCombo.setMaxVisibleItems(20)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("DejaVu Serif"))
        self.seriffontCombo.setCurrentFont(font)
        self.seriffontCombo.setObjectName(_fromUtf8("seriffontCombo"))
        self.standardfontCombo = QtGui.QFontComboBox(self.groupBox_2)
        self.standardfontCombo.setGeometry(QtCore.QRect(130, 70, 171, 26))
        self.standardfontCombo.setMaxVisibleItems(20)
        self.standardfontCombo.setObjectName(_fromUtf8("standardfontCombo"))
        self.sansfontCombo = QtGui.QFontComboBox(self.groupBox_2)
        self.sansfontCombo.setGeometry(QtCore.QRect(400, 70, 191, 26))
        self.sansfontCombo.setMaxVisibleItems(20)
        self.sansfontCombo.setObjectName(_fromUtf8("sansfontCombo"))
        self.fixedfontCombo = QtGui.QFontComboBox(self.groupBox_2)
        self.fixedfontCombo.setGeometry(QtCore.QRect(400, 120, 191, 26))
        self.fixedfontCombo.setMaxVisibleItems(20)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("DejaVu Sans Mono"))
        self.fixedfontCombo.setCurrentFont(font)
        self.fixedfontCombo.setObjectName(_fromUtf8("fixedfontCombo"))
        self.spinFontSize = QtGui.QSpinBox(self.groupBox_2)
        self.spinFontSize.setGeometry(QtCore.QRect(140, 30, 151, 26))
        self.spinFontSize.setAlignment(QtCore.Qt.AlignCenter)
        self.spinFontSize.setMinimum(6)
        self.spinFontSize.setMaximum(24)
        self.spinFontSize.setProperty("value", 12)
        self.spinFontSize.setObjectName(_fromUtf8("spinFontSize"))
        self.groupBox_3 = QtGui.QGroupBox(Dialog)
        self.groupBox_3.setGeometry(QtCore.QRect(350, 20, 291, 171))
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.checkHomePage = QtGui.QCheckBox(self.groupBox_3)
        self.checkHomePage.setGeometry(QtCore.QRect(10, 30, 241, 21))
        self.checkHomePage.setObjectName(_fromUtf8("checkHomePage"))
        self.homepageEdit = QtGui.QLineEdit(self.groupBox_3)
        self.homepageEdit.setGeometry(QtCore.QRect(30, 60, 251, 26))
        self.homepageEdit.setObjectName(_fromUtf8("homepageEdit"))

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.groupBox.setTitle(_translate("Dialog", "Browsing", None))
        self.checkLoadImages.setText(_translate("Dialog", "Load Images", None))
        self.checkJavascript.setText(_translate("Dialog", "Enable JavaScript", None))
        self.checkUserAgent.setText(_translate("Dialog", "Custom User Agent", None))
        self.useragentEdit.setText(_translate("Dialog", "Nokia 5130", None))
        self.groupBox_2.setTitle(_translate("Dialog", "Appearance", None))
        self.label.setText(_translate("Dialog", "Min. Font Size :", None))
        self.label_standard.setText(_translate("Dialog", "Standard Font :", None))
        self.label_sans.setText(_translate("Dialog", "Sans Font :", None))
        self.label_serif.setText(_translate("Dialog", "Serif Font :", None))
        self.label_fixed.setText(_translate("Dialog", "Fixed Font :", None))
        self.groupBox_3.setTitle(_translate("Dialog", "Home Page", None))
        self.checkHomePage.setText(_translate("Dialog", "Custom Home Page URL", None))
        self.homepageEdit.setText(_translate("Dialog", "http://www.google.com", None))

