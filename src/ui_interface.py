# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFrame, QGridLayout, QHBoxLayout, QLabel,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QSpacerItem, QStatusBar, QTabWidget,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1056, 732)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName(u"actionSave")
        self.actionQuit = QAction(MainWindow)
        self.actionQuit.setObjectName(u"actionQuit")
        self.actionStart_Recording = QAction(MainWindow)
        self.actionStart_Recording.setObjectName(u"actionStart_Recording")
        self.actionInformation = QAction(MainWindow)
        self.actionInformation.setObjectName(u"actionInformation")
        self.actionFrequency_Domain = QAction(MainWindow)
        self.actionFrequency_Domain.setObjectName(u"actionFrequency_Domain")
        self.actionTime_Domain = QAction(MainWindow)
        self.actionTime_Domain.setObjectName(u"actionTime_Domain")
        self.actionMain_View = QAction(MainWindow)
        self.actionMain_View.setObjectName(u"actionMain_View")
        self.actionMain_View_2 = QAction(MainWindow)
        self.actionMain_View_2.setObjectName(u"actionMain_View_2")
        self.actionConnected_Device = QAction(MainWindow)
        self.actionConnected_Device.setObjectName(u"actionConnected_Device")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setMinimumSize(QSize(5, 0))
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line, 1, 0, 1, 1)

        self.widget_2 = QWidget(self.centralwidget)
        self.widget_2.setObjectName(u"widget_2")
        sizePolicy.setHeightForWidth(self.widget_2.sizePolicy().hasHeightForWidth())
        self.widget_2.setSizePolicy(sizePolicy)
        self.widget_2.setMinimumSize(QSize(0, 0))
        self.widget_2.setMaximumSize(QSize(16777215, 16777215))
        self.horizontalLayout_8 = QHBoxLayout(self.widget_2)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.widget = QWidget(self.widget_2)
        self.widget.setObjectName(u"widget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy1)
        self.widget.setMaximumSize(QSize(200, 16777215))
        self.widget.setStyleSheet(u"\n"
"background-color:rgb(180, 180, 180)\n"
"\n"
"")
        self.verticalLayout_2 = QVBoxLayout(self.widget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.menubtn = QPushButton(self.widget)
        self.menubtn.setObjectName(u"menubtn")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ApplicationExit))
        self.menubtn.setIcon(icon)
        self.menubtn.setCheckable(True)
        self.menubtn.setAutoExclusive(True)

        self.verticalLayout_2.addWidget(self.menubtn, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.GraphWid = QWidget(self.widget)
        self.GraphWid.setObjectName(u"GraphWid")
        sizePolicy1.setHeightForWidth(self.GraphWid.sizePolicy().hasHeightForWidth())
        self.GraphWid.setSizePolicy(sizePolicy1)
        self.GraphWid.setMinimumSize(QSize(150, 100))
        self.verticalLayout = QVBoxLayout(self.GraphWid)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.ViewWid = QWidget(self.GraphWid)
        self.ViewWid.setObjectName(u"ViewWid")
        self.ViewWid.setMinimumSize(QSize(180, 150))
        self.ViewWid.setMaximumSize(QSize(100, 80))
        self.ViewWid.setStyleSheet(u"\n"
"background-color:rgb(140, 140, 140)\n"
"\n"
"")
        self.gridLayout_3 = QGridLayout(self.ViewWid)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.frame_2 = QFrame(self.ViewWid)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_7 = QLabel(self.frame_2)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_7.addWidget(self.label_7)

        self.FFTcomb_2 = QComboBox(self.frame_2)
        self.FFTcomb_2.setObjectName(u"FFTcomb_2")

        self.horizontalLayout_7.addWidget(self.FFTcomb_2)


        self.gridLayout_3.addWidget(self.frame_2, 2, 0, 1, 1)

        self.label = QLabel(self.ViewWid)
        self.label.setObjectName(u"label")
        self.label.setMaximumSize(QSize(16777215, 30))

        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1, Qt.AlignmentFlag.AlignHCenter)

        self.frame = QFrame(self.ViewWid)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.frame)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_6 = QLabel(self.frame)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_6.addWidget(self.label_6)

        self.FFTcomb = QComboBox(self.frame)
        self.FFTcomb.setObjectName(u"FFTcomb")

        self.horizontalLayout_6.addWidget(self.FFTcomb)


        self.gridLayout_3.addWidget(self.frame, 1, 0, 1, 1)


        self.verticalLayout.addWidget(self.ViewWid, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.TriggerWid = QWidget(self.GraphWid)
        self.TriggerWid.setObjectName(u"TriggerWid")
        self.TriggerWid.setMinimumSize(QSize(180, 150))
        self.TriggerWid.setMaximumSize(QSize(100, 180))
        self.TriggerWid.setStyleSheet(u"\n"
"background-color:rgb(140, 140, 140)\n"
"\n"
"")
        self.gridLayout_4 = QGridLayout(self.TriggerWid)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.label_2 = QLabel(self.TriggerWid)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMaximumSize(QSize(100, 30))

        self.gridLayout_4.addWidget(self.label_2, 3, 0, 1, 1)

        self.Negfr = QFrame(self.TriggerWid)
        self.Negfr.setObjectName(u"Negfr")
        self.Negfr.setMaximumSize(QSize(16777215, 40))
        self.Negfr.setFrameShape(QFrame.Shape.StyledPanel)
        self.Negfr.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.Negfr)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_4 = QLabel(self.Negfr)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout_2.addWidget(self.label_4)

        self.NegativeEdgech = QCheckBox(self.Negfr)
        self.NegativeEdgech.setObjectName(u"NegativeEdgech")

        self.horizontalLayout_2.addWidget(self.NegativeEdgech, 0, Qt.AlignmentFlag.AlignRight)


        self.gridLayout_4.addWidget(self.Negfr, 5, 0, 1, 1)

        self.Posfr = QFrame(self.TriggerWid)
        self.Posfr.setObjectName(u"Posfr")
        self.Posfr.setMaximumSize(QSize(16777215, 40))
        self.Posfr.setFrameShape(QFrame.Shape.StyledPanel)
        self.Posfr.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.Posfr)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_3 = QLabel(self.Posfr)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout.addWidget(self.label_3)

        self.PositiveEdgech = QCheckBox(self.Posfr)
        self.PositiveEdgech.setObjectName(u"PositiveEdgech")

        self.horizontalLayout.addWidget(self.PositiveEdgech, 0, Qt.AlignmentFlag.AlignRight)


        self.gridLayout_4.addWidget(self.Posfr, 4, 0, 1, 1)


        self.verticalLayout.addWidget(self.TriggerWid, 0, Qt.AlignmentFlag.AlignLeft)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.TimeVolDivWid = QWidget(self.GraphWid)
        self.TimeVolDivWid.setObjectName(u"TimeVolDivWid")
        self.TimeVolDivWid.setMinimumSize(QSize(180, 180))
        self.TimeVolDivWid.setMaximumSize(QSize(16777215, 180))
        self.TimeVolDivWid.setStyleSheet(u"\n"
"background-color:rgb(140, 140, 140)\n"
"\n"
"")
        self.verticalLayout_3 = QVBoxLayout(self.TimeVolDivWid)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.VolDivFr = QFrame(self.TimeVolDivWid)
        self.VolDivFr.setObjectName(u"VolDivFr")
        self.VolDivFr.setMinimumSize(QSize(150, 50))
        self.VolDivFr.setMaximumSize(QSize(16777215, 90))
        self.VolDivFr.setFrameShape(QFrame.Shape.StyledPanel)
        self.VolDivFr.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.VolDivFr)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_9 = QLabel(self.VolDivFr)
        self.label_9.setObjectName(u"label_9")

        self.horizontalLayout_5.addWidget(self.label_9, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.selframe1 = QFrame(self.VolDivFr)
        self.selframe1.setObjectName(u"selframe1")
        self.selframe1.setMinimumSize(QSize(0, 60))
        self.selframe1.setMaximumSize(QSize(70, 60))
        self.selframe1.setFrameShape(QFrame.Shape.StyledPanel)
        self.selframe1.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.selframe1)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.voltdiv_spbx = QDoubleSpinBox(self.selframe1)
        self.voltdiv_spbx.setObjectName(u"voltdiv_spbx")
        self.voltdiv_spbx.setMinimumSize(QSize(50, 20))
        self.voltdiv_spbx.setMaximumSize(QSize(50, 20))

        self.verticalLayout_5.addWidget(self.voltdiv_spbx)

        self.voltdiv_cb = QComboBox(self.selframe1)
        self.voltdiv_cb.setObjectName(u"voltdiv_cb")
        self.voltdiv_cb.setMinimumSize(QSize(50, 20))
        self.voltdiv_cb.setMaximumSize(QSize(50, 22))

        self.verticalLayout_5.addWidget(self.voltdiv_cb)


        self.horizontalLayout_5.addWidget(self.selframe1, 0, Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)


        self.verticalLayout_3.addWidget(self.VolDivFr)

        self.TimeDiv = QFrame(self.TimeVolDivWid)
        self.TimeDiv.setObjectName(u"TimeDiv")
        self.TimeDiv.setMinimumSize(QSize(150, 50))
        self.TimeDiv.setMaximumSize(QSize(16777215, 90))
        self.TimeDiv.setFrameShape(QFrame.Shape.StyledPanel)
        self.TimeDiv.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.TimeDiv)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_8 = QLabel(self.TimeDiv)
        self.label_8.setObjectName(u"label_8")

        self.horizontalLayout_4.addWidget(self.label_8, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.selframe2 = QFrame(self.TimeDiv)
        self.selframe2.setObjectName(u"selframe2")
        self.selframe2.setMinimumSize(QSize(0, 60))
        self.selframe2.setMaximumSize(QSize(70, 60))
        self.selframe2.setFrameShape(QFrame.Shape.StyledPanel)
        self.selframe2.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.selframe2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.timediv_spbx = QDoubleSpinBox(self.selframe2)
        self.timediv_spbx.setObjectName(u"timediv_spbx")
        self.timediv_spbx.setMinimumSize(QSize(50, 20))
        self.timediv_spbx.setMaximumSize(QSize(50, 20))

        self.verticalLayout_4.addWidget(self.timediv_spbx)

        self.timediv_cb = QComboBox(self.selframe2)
        self.timediv_cb.setObjectName(u"timediv_cb")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.timediv_cb.sizePolicy().hasHeightForWidth())
        self.timediv_cb.setSizePolicy(sizePolicy2)
        self.timediv_cb.setMinimumSize(QSize(50, 20))
        self.timediv_cb.setMaximumSize(QSize(50, 22))

        self.verticalLayout_4.addWidget(self.timediv_cb, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop)


        self.horizontalLayout_4.addWidget(self.selframe2, 0, Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)


        self.verticalLayout_3.addWidget(self.TimeDiv)


        self.verticalLayout.addWidget(self.TimeVolDivWid)


        self.verticalLayout_2.addWidget(self.GraphWid, 0, Qt.AlignmentFlag.AlignHCenter)


        self.horizontalLayout_8.addWidget(self.widget, 0, Qt.AlignmentFlag.AlignHCenter)

        self.tabWidget = QTabWidget(self.widget_2)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_1 = QWidget()
        self.tab_1.setObjectName(u"tab_1")
        self.tabWidget.addTab(self.tab_1, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.tabWidget.addTab(self.tab_4, "")

        self.horizontalLayout_8.addWidget(self.tabWidget)


        self.gridLayout.addWidget(self.widget_2, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1056, 33))
        self.menuFILE = QMenu(self.menubar)
        self.menuFILE.setObjectName(u"menuFILE")
        self.menuEDIT = QMenu(self.menubar)
        self.menuEDIT.setObjectName(u"menuEDIT")
        self.menuVIEW = QMenu(self.menubar)
        self.menuVIEW.setObjectName(u"menuVIEW")
        self.menuDomain_Type = QMenu(self.menuVIEW)
        self.menuDomain_Type.setObjectName(u"menuDomain_Type")
        self.menuVoltage_Division = QMenu(self.menuVIEW)
        self.menuVoltage_Division.setObjectName(u"menuVoltage_Division")
        self.menuTime_Division = QMenu(self.menuVIEW)
        self.menuTime_Division.setObjectName(u"menuTime_Division")
        self.menuRECORD = QMenu(self.menubar)
        self.menuRECORD.setObjectName(u"menuRECORD")
        self.menuHELP = QMenu(self.menubar)
        self.menuHELP.setObjectName(u"menuHELP")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFILE.menuAction())
        self.menubar.addAction(self.menuEDIT.menuAction())
        self.menubar.addAction(self.menuVIEW.menuAction())
        self.menubar.addAction(self.menuRECORD.menuAction())
        self.menubar.addAction(self.menuHELP.menuAction())
        self.menuFILE.addAction(self.actionSave)
        self.menuFILE.addAction(self.actionQuit)
        self.menuEDIT.addAction(self.actionConnected_Device)
        self.menuVIEW.addAction(self.menuDomain_Type.menuAction())
        self.menuVIEW.addAction(self.menuVoltage_Division.menuAction())
        self.menuVIEW.addAction(self.menuTime_Division.menuAction())
        self.menuDomain_Type.addAction(self.actionFrequency_Domain)
        self.menuDomain_Type.addAction(self.actionTime_Domain)
        self.menuVoltage_Division.addAction(self.actionMain_View)
        self.menuTime_Division.addAction(self.actionMain_View_2)
        self.menuRECORD.addAction(self.actionStart_Recording)
        self.menuHELP.addAction(self.actionInformation)

        self.retranslateUi(MainWindow)
        self.menubtn.toggled.connect(self.GraphWid.setVisible)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionSave.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.actionQuit.setText(QCoreApplication.translate("MainWindow", u"Quit", None))
        self.actionStart_Recording.setText(QCoreApplication.translate("MainWindow", u"Start Recording", None))
        self.actionInformation.setText(QCoreApplication.translate("MainWindow", u"Information", None))
        self.actionFrequency_Domain.setText(QCoreApplication.translate("MainWindow", u"Frequency Domain", None))
        self.actionTime_Domain.setText(QCoreApplication.translate("MainWindow", u"Time Domain", None))
        self.actionMain_View.setText(QCoreApplication.translate("MainWindow", u"Main View", None))
        self.actionMain_View_2.setText(QCoreApplication.translate("MainWindow", u"Main View", None))
        self.actionConnected_Device.setText(QCoreApplication.translate("MainWindow", u"Connected Device", None))
        self.menubtn.setText("")
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Channel 2", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"View", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Channel 1", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"          Trigger", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Negative Edge", None))
        self.NegativeEdgech.setText("")
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Positive Edge", None))
        self.PositiveEdgech.setText("")
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Volt/Div", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Time/Div", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), QCoreApplication.translate("MainWindow", u"Tab 1", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"Tab 2", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("MainWindow", u"Tab 3", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QCoreApplication.translate("MainWindow", u"Tab 4", None))
        self.menuFILE.setTitle(QCoreApplication.translate("MainWindow", u"FILE", None))
        self.menuEDIT.setTitle(QCoreApplication.translate("MainWindow", u"DEVICE", None))
        self.menuVIEW.setTitle(QCoreApplication.translate("MainWindow", u"VIEW", None))
        self.menuDomain_Type.setTitle(QCoreApplication.translate("MainWindow", u"Domain Type", None))
        self.menuVoltage_Division.setTitle(QCoreApplication.translate("MainWindow", u"Voltage Division", None))
        self.menuTime_Division.setTitle(QCoreApplication.translate("MainWindow", u"Time Division", None))
        self.menuRECORD.setTitle(QCoreApplication.translate("MainWindow", u"RECORD", None))
        self.menuHELP.setTitle(QCoreApplication.translate("MainWindow", u"HELP", None))
    # retranslateUi

