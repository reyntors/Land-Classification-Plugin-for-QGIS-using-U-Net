# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'lcp_dialog_base.ui'
##
## Created by: Qt User Interface Compiler version 6.4.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QGraphicsView,
    QLabel, QLineEdit, QPushButton, QRadioButton,
    QSizePolicy, QTabWidget, QWidget)

from qgsfilewidget import QgsFileWidget

class Ui_LandClassificationPluginDialogBase(object):
    def setupUi(self, LandClassificationPluginDialogBase):
        if not LandClassificationPluginDialogBase.objectName():
            LandClassificationPluginDialogBase.setObjectName(u"LandClassificationPluginDialogBase")
        LandClassificationPluginDialogBase.resize(397, 297)
        self.tabWidget = QTabWidget(LandClassificationPluginDialogBase)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(0, 0, 401, 301))
        self.Clip = QWidget()
        self.Clip.setObjectName(u"Clip")
        self.label = QLabel(self.Clip)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 190, 101, 16))
        self.mQgsFileWidget = QgsFileWidget(self.Clip)
        self.mQgsFileWidget.setObjectName(u"mQgsFileWidget")
        self.mQgsFileWidget.setGeometry(QRect(120, 180, 251, 27))
        self.mQgsFileWidget.setStorageMode(QgsFileWidget.GetDirectory)
        self.line = QFrame(self.Clip)
        self.line.setObjectName(u"line")
        self.line.setWindowModality(Qt.NonModal)
        self.line.setGeometry(QRect(20, 10, 351, 16))
        self.line.setAutoFillBackground(False)
        self.line.setFrameShadow(QFrame.Raised)
        self.line.setLineWidth(1)
        self.line.setMidLineWidth(15)
        self.line.setFrameShape(QFrame.HLine)
        self.label_2 = QLabel(self.Clip)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(30, 10, 181, 16))
        self.graphicsView = QGraphicsView(self.Clip)
        self.graphicsView.setObjectName(u"graphicsView")
        self.graphicsView.setGeometry(QRect(180, 40, 191, 131))
        self.clip = QPushButton(self.Clip)
        self.clip.setObjectName(u"clip")
        self.clip.setGeometry(QRect(290, 240, 75, 23))
        self.line_2 = QFrame(self.Clip)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setWindowModality(Qt.NonModal)
        self.line_2.setGeometry(QRect(20, 220, 351, 16))
        self.line_2.setAutoFillBackground(False)
        self.line_2.setFrameShadow(QFrame.Raised)
        self.line_2.setLineWidth(1)
        self.line_2.setMidLineWidth(15)
        self.line_2.setFrameShape(QFrame.HLine)
        self.label_3 = QLabel(self.Clip)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(30, 220, 47, 13))
        self.Upxlon = QLineEdit(self.Clip)
        self.Upxlon.setObjectName(u"Upxlon")
        self.Upxlon.setGeometry(QRect(50, 60, 101, 20))
        self.Upxlon.setReadOnly(False)
        self.Upylat = QLineEdit(self.Clip)
        self.Upylat.setObjectName(u"Upylat")
        self.Upylat.setGeometry(QRect(50, 90, 101, 20))
        self.lrxlon = QLineEdit(self.Clip)
        self.lrxlon.setObjectName(u"lrxlon")
        self.lrxlon.setGeometry(QRect(50, 120, 101, 20))
        self.lrxlon.setReadOnly(False)
        self.lrylat = QLineEdit(self.Clip)
        self.lrylat.setObjectName(u"lrylat")
        self.lrylat.setGeometry(QRect(50, 150, 101, 20))
        self.lrylat.setReadOnly(False)
        self.label_4 = QLabel(self.Clip)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(20, 60, 47, 13))
        self.label_6 = QLabel(self.Clip)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(20, 120, 47, 13))
        self.drawButton = QPushButton(self.Clip)
        self.drawButton.setObjectName(u"drawButton")
        self.drawButton.setGeometry(QRect(114, 30, 31, 23))
        self.drawButton.setIconSize(QSize(16, 16))
        self.radioButton = QRadioButton(self.Clip)
        self.radioButton.setObjectName(u"radioButton")
        self.radioButton.setGeometry(QRect(50, 31, 51, 20))
        self.tabWidget.addTab(self.Clip, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.label_5 = QLabel(self.tab_2)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(30, 20, 71, 16))
        self.mQgsFileWidget_2 = QgsFileWidget(self.tab_2)
        self.mQgsFileWidget_2.setObjectName(u"mQgsFileWidget_2")
        self.mQgsFileWidget_2.setGeometry(QRect(110, 10, 251, 27))
        self.mQgsFileWidget_2.setStorageMode(QgsFileWidget.GetFile)
        self.graphicsView_2 = QGraphicsView(self.tab_2)
        self.graphicsView_2.setObjectName(u"graphicsView_2")
        self.graphicsView_2.setGeometry(QRect(210, 70, 161, 141))
        self.graphicsView_3 = QGraphicsView(self.tab_2)
        self.graphicsView_3.setObjectName(u"graphicsView_3")
        self.graphicsView_3.setGeometry(QRect(20, 70, 161, 141))
        self.pushButton = QPushButton(self.tab_2)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(300, 240, 75, 23))
        self.line_3 = QFrame(self.tab_2)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setWindowModality(Qt.NonModal)
        self.line_3.setGeometry(QRect(20, 45, 161, 21))
        self.line_3.setAutoFillBackground(False)
        self.line_3.setFrameShadow(QFrame.Raised)
        self.line_3.setLineWidth(1)
        self.line_3.setMidLineWidth(15)
        self.line_3.setFrameShape(QFrame.HLine)
        self.label_7 = QLabel(self.tab_2)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(80, 50, 47, 13))
        self.line_4 = QFrame(self.tab_2)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setWindowModality(Qt.NonModal)
        self.line_4.setGeometry(QRect(210, 40, 161, 31))
        self.line_4.setAutoFillBackground(False)
        self.line_4.setFrameShadow(QFrame.Raised)
        self.line_4.setLineWidth(1)
        self.line_4.setMidLineWidth(15)
        self.line_4.setFrameShape(QFrame.HLine)
        self.label_8 = QLabel(self.tab_2)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(260, 45, 81, 21))
        self.tabWidget.addTab(self.tab_2, "")

        self.retranslateUi(LandClassificationPluginDialogBase)

        self.tabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(LandClassificationPluginDialogBase)
    # setupUi

    def retranslateUi(self, LandClassificationPluginDialogBase):
        LandClassificationPluginDialogBase.setWindowTitle(QCoreApplication.translate("LandClassificationPluginDialogBase", u"Land Classification Plugin", None))
        self.label.setText(QCoreApplication.translate("LandClassificationPluginDialogBase", u"Select file directory:", None))
        self.label_2.setText(QCoreApplication.translate("LandClassificationPluginDialogBase", u"Search Parameters", None))
        self.clip.setText(QCoreApplication.translate("LandClassificationPluginDialogBase", u"CLIP", None))
        self.label_3.setText(QCoreApplication.translate("LandClassificationPluginDialogBase", u"Run", None))
        self.Upxlon.setInputMask("")
        self.Upxlon.setText("")
        self.Upxlon.setPlaceholderText(QCoreApplication.translate("LandClassificationPluginDialogBase", u"X (Lon)", None))
        self.Upylat.setText("")
        self.Upylat.setPlaceholderText(QCoreApplication.translate("LandClassificationPluginDialogBase", u"Y (Lat)", None))
        self.lrxlon.setText("")
        self.lrxlon.setPlaceholderText(QCoreApplication.translate("LandClassificationPluginDialogBase", u"X (Lon)", None))
        self.lrylat.setText("")
        self.lrylat.setPlaceholderText(QCoreApplication.translate("LandClassificationPluginDialogBase", u"Y (Lat)", None))
        self.label_4.setText(QCoreApplication.translate("LandClassificationPluginDialogBase", u"UL", None))
        self.label_6.setText(QCoreApplication.translate("LandClassificationPluginDialogBase", u"LR", None))
        self.drawButton.setText(QCoreApplication.translate("LandClassificationPluginDialogBase", u"+", None))
        self.radioButton.setText(QCoreApplication.translate("LandClassificationPluginDialogBase", u"Show", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Clip), QCoreApplication.translate("LandClassificationPluginDialogBase", u"Clip", None))
        self.label_5.setText(QCoreApplication.translate("LandClassificationPluginDialogBase", u"Select the file:", None))
        self.pushButton.setText(QCoreApplication.translate("LandClassificationPluginDialogBase", u"RUN", None))
        self.label_7.setText(QCoreApplication.translate("LandClassificationPluginDialogBase", u"INPUT", None))
        self.label_8.setText(QCoreApplication.translate("LandClassificationPluginDialogBase", u"GENERATED", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("LandClassificationPluginDialogBase", u"LandClassification", None))
    # retranslateUi

