"""
Author: Sang-tak Lee
Website: https://tak.ta-note.com
Created: 09/11/2020
Updated: 05/27/2021
"""

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

import xgenm as xg
import xgenm.xgGlobal as xgg
import xgenm.XgExternalAPI as xge
import xgenm.ui as xgui
import xgenm.xmaya.xgmConvertPrimToPolygon as cpp
import pymel.core as pm
import maya.OpenMayaUI as omui

from shiboken2 import wrapInstance
import os


XGEN_ICON_PATH = __file__.split('takXgenManager')[0] + 'takXgenManager/icons'
ICON_SIZE = 48


def getMayaMainWin():
    mayaWinPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(mayaWinPtr), QWidget)


class XGenManager(QMainWindow):
    INSTANCE = None

    @classmethod
    def showUI(cls):
        if cls.INSTANCE:
            cls.INSTANCE.close()
            cls.INSTANCE.deleteLater()
        cls.INSTANCE = XGenManager()
        cls.INSTANCE.show()

    def __init__(self):
        super(XGenManager, self).__init__()
        self.de = xgg.DescriptionEditor

        self.setWindowTitle('XGen Manager')
        self.setParent(getMayaMainWin())
        self.setWindowFlags(Qt.Tool)

        self.buildUI()
        self.setMinimumWidth(250)

    def buildUI(self):
        centralWidget = QWidget()

        self.setCentralWidget(centralWidget)

        mainLayout = QVBoxLayout()
        centralWidget.setLayout(mainLayout)

        # Guide tools section
        guideToolGrpBox = QGroupBox('Guide Tools')
        mainLayout.addWidget(guideToolGrpBox)

        guideMainLayout = QVBoxLayout()
        guideToolGrpBox.setLayout(guideMainLayout)

        guideToolBar = QToolBar()
        guideToolBar.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
        guideMainLayout.addWidget(guideToolBar)

        addGuideAction = QAction(QIcon(os.path.join(XGEN_ICON_PATH, 'xgGuideContext_200.png')), 'Add or Move Guides', self)
        guideToolBar.addAction(addGuideAction)

        sculptGuideAction = QAction(QIcon(os.path.join(XGEN_ICON_PATH, 'fx_sculpt_200.png')), 'Sculpt Guides', self)
        guideToolBar.addAction(sculptGuideAction)

        copyGuideAction = QAction(QIcon(os.path.join(XGEN_ICON_PATH, 'tool_copyGuides_200.png')), 'Copy source guide shape to target guide.', self)
        guideToolBar.addAction(copyGuideAction)

        mirrorGuideAction = QAction(QIcon(os.path.join(XGEN_ICON_PATH, 'xgFlipGuides_200.png')), 'Mirror selected guides across the X-Axis.', self)
        guideToolBar.addAction(mirrorGuideAction)

        convertToPolyAction = QAction(QIcon(os.path.join(XGEN_ICON_PATH, 'xgConvertToPoly_200.png')), 'Convert Primitives to Polygons', self)
        guideToolBar.addAction(convertToPolyAction)

        guideLayout = QGridLayout()
        guideMainLayout.addLayout(guideLayout)

        numOfCVsLabel = QLabel('Number of CP')
        guideLayout.addWidget(numOfCVsLabel, 0, 0)

        minusButton = QPushButton('-')
        guideLayout.addWidget(minusButton, 0, 1)

        plusButton = QPushButton('+')
        guideLayout.addWidget(plusButton, 0, 2)

        normalizeButton = QPushButton('Normalize')
        guideLayout.addWidget(normalizeButton, 1, 0)

        bakeButton = QPushButton('Bake')
        guideLayout.addWidget(bakeButton, 1, 1, 1, 2)

        # Description section
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        mainLayout.addWidget(scrollArea)

        scrollWidget = QWidget()
        scrollWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        scrollWidget.setContentsMargins(0, 0, 0, 0)
        scrollArea.setWidget(scrollWidget)

        scrollLayout = QVBoxLayout()
        scrollWidget.setLayout(scrollLayout)

        collections = xg.palettes()
        for collection in collections:
            descriptions = xg.descriptions(collection)
            for description in descriptions:
                descriptionWidget = DescriptionWidget(collection, description)

                if xgui.currentDescription() == description:
                    descriptionWidget.descriptionGrpBox.setTitleColor()
                    self.setGuidesVisibility(description, True)
                else:
                    self.setGuidesVisibility(description, False)

                descriptionWidget.onActive.connect(self.onDescriptionActive)
                scrollLayout.addWidget(descriptionWidget)

        # Connections
        addGuideAction.triggered.connect(lambda: pm.mel.eval('XgGuideTool;'))
        sculptGuideAction.triggered.connect(lambda: xgui.createDescriptionEditor(False).guideSculptContext(False))
        copyGuideAction.triggered.connect(self.copyGuideShape)
        mirrorGuideAction.triggered.connect(self.mirrorGuide)
        convertToPolyAction.triggered.connect(XGenManager.showWarningDialog)
        minusButton.clicked.connect(lambda: XGenManager.editNumGuideCP('decrease'))
        plusButton.clicked.connect(lambda: XGenManager.editNumGuideCP('increase'))
        normalizeButton.clicked.connect(lambda: pm.mel.eval('xgmNormalizeGuides();'))
        bakeButton.clicked.connect(lambda: pm.mel.eval('xgmBakeGuideVertices;'))

    def onDescriptionActive(self):
        descWidgets = self.findChildren(DescriptionWidget)
        for descWidget in descWidgets:
            if descWidget != self.sender():
                descWidget.descriptionGrpBox.removeTitleColor()
                self.setGuidesVisibility(descWidget.description, False)
            else:
                self.setGuidesVisibility(descWidget.description, True)

    def setGuidesVisibility(self, description, value):
        guides = xg.descriptionGuides(description)
        for guide in guides:
            pm.PyNode(guide).v.set(value)

    def copyGuideShape(self):
        selGuides = pm.selected()
        pm.select(selGuides[0], r=True)
        pm.mel.eval('xgmCopyGuides("copy");')
        pm.select(selGuides[1], r=True)
        pm.mel.eval('xgmCopyGuides("paste");')

    def mirrorGuide(self):
        sourceGuide = pm.selected()[0]
        curDescription = self.de.currentDescription()
        pm.mel.eval('xgmFlipGuides("{0}");'.format(curDescription))
        mirrorGuide = sourceGuide.getParent().getChildren()[-1]
        pm.select(mirrorGuide, r=True)

    @staticmethod
    def showWarningDialog():
        warningDialog = QMessageBox()
        warningDialog.setWindowTitle('Warning')
        warningDialog.setIcon(QMessageBox.Warning)
        warningDialog.setText('Primitives are converted to polygons!\nAre you sure?')
        warningDialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        result = warningDialog.exec_()

        if result == QMessageBox.Ok:
            cpp.convertPrimToPolygon(False)

    @staticmethod
    def editNumGuideCP(command):
        guides = pm.selected()
        minCPCount = 5
        for guide in guides:
            currentNumOfCPs = guide.getShape().controlPoints.numElements()
            addingValue = 2 if command == 'increase' else -2
            val = max(minCPCount, currentNumOfCPs+addingValue)
            pm.mel.eval('xgmChangeCVCount({0});'.format(val))
        pm.select(guides, r=True)


class DescriptionWidget(QWidget):
    onActive = Signal()

    def __init__(self, collection, description):
        super(DescriptionWidget, self).__init__()
        self.collection = collection
        self.description = description
        self.de = xgg.DescriptionEditor

        self.renderableButton = None
        self.renderableIcon = None
        self.disRenderableIcon = None

        # self.setDefaultSettings()
        self.buildUI()

        self.de.refresh('Description')

    def buildUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.descriptionGrpBox = DescriptionGroupBox(self.description)
        layout.addWidget(self.descriptionGrpBox)

        descriptionGrpBoxLayout = QVBoxLayout()
        self.descriptionGrpBox.setLayout(descriptionGrpBoxLayout)

        # Description Toolbar
        descriptionToolBar = QToolBar()
        descriptionToolBar.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
        descriptionGrpBoxLayout.addWidget(descriptionToolBar)

        guideDisplayToggleAction = QAction(QIcon(os.path.join(XGEN_ICON_PATH, 'xgToggleGuide_200.png')), 'Guide Display Toggle', self)
        descriptionToolBar.addAction(guideDisplayToggleAction)

        xgPreviewRefreshAction = QAction(QIcon(os.path.join(XGEN_ICON_PATH, 'xgPreviewRefresh_200.png')), 'Refresh Primitive', self)
        descriptionToolBar.addAction(xgPreviewRefreshAction)

        xgPreviewClearAction = QAction(QIcon(os.path.join(XGEN_ICON_PATH, 'xgPreviewClear_200.png')), 'Clear Primitive', self)
        descriptionToolBar.addAction(xgPreviewClearAction)

        # Density Widget
        densityLayout = QHBoxLayout()
        descriptionGrpBoxLayout.addLayout(densityLayout)

        densityLabel = QLabel('Density')
        densityLayout.addWidget(densityLabel)

        densityValue = xg.getAttr("density", self.collection, self.description, "RandomGenerator")

        densityLineEdit = QLineEdit()
        densityLineEdit.setText(densityValue)
        densityLineEditValidator = QDoubleValidator(0.000, 3000.000, 6, densityLineEdit)
        densityLineEdit.setValidator(densityLineEditValidator)
        densityLayout.addWidget(densityLineEdit)

        # Connect Widgets
        guideDisplayToggleAction.triggered.connect(lambda: xg.toggleGuideDisplay(self.description))
        xgPreviewRefreshAction.triggered.connect(lambda: pm.mel.eval('xgmPreview -progress {"%s"};' % self.description))
        xgPreviewClearAction.triggered.connect(lambda: pm.mel.eval('xgmPreview -clean {"%s"};' % self.description))
        densityLineEdit.returnPressed.connect(lambda: self.setDensity(densityLineEdit.text()))
        self.descriptionGrpBox.onActive.connect(self.onActive.emit)

    def setDensity(self, val):
        xg.setAttr("density", xge.prepForAttribute(str(val)), self.collection, self.description, "RandomGenerator")
        pm.mel.eval('xgmPreview -progress {"%s"};' % self.description)
        self.de.refresh('Description')

    def setDefaultSettings(self):
        xg.setAttr("inCameraOnly", xge.prepForAttribute(str(False)), self.collection, self.description, "GLRenderer")
        xg.setAttr("splineSegments", xge.prepForAttribute(str(1)), self.collection, self.description, "GLRenderer")
        xg.setAttr("renderer", xge.prepForAttribute('Arnold Renderer'), self.collection, self.description, "RendermanRenderer")
        xg.setAttr("custom__arnold_rendermode", xge.prepForAttribute(str(1)), self.collection, self.description, "RendermanRenderer")
        xg.setAttr("custom__arnold_minPixelWidth", xge.prepForAttribute(str(0.5)), self.collection, self.description, "RendermanRenderer")



class DescriptionGroupBox(QGroupBox):
    onActive = Signal()

    def __init__(self, title='Untitled'):
        super(DescriptionGroupBox, self).__init__(title)

        self.setAttribute(Qt.WA_Hover)

    def mousePressEvent(self, event):
        super(DescriptionGroupBox, self).mousePressEvent(event)

        xgg.DescriptionEditor.setCurrentDescription(str(self.title()))
        self.setTitleColor()
        self.onActive.emit()

    def setTitleColor(self):
        self.setStyleSheet('QGroupBox:title {color: rgb(255, 255, 0);}')

    def removeTitleColor(self):
        self.setStyleSheet('QGroupBox:title {color: rgb(187, 187, 187);}')

    def enterEvent(self, event):
        super(DescriptionGroupBox, self).enterEvent(event)

        self.setTitleColor()

    def leaveEvent(self, event):
        super(DescriptionGroupBox, self).leaveEvent(event)

        if not xgui.currentDescription() == self.title():
            self.removeTitleColor()
        else:
            self.setTitleColor()
