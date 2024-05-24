import PythonQt
import os
import vtk, qt, ctk, slicer
import sys
import unittest

from Utilities.UtilsIOXml import *
from Utilities.UtilsFilesIO import *
from Utilities.UtilsMsgs import *

from PythonQt import QtCore, QtGui

import QuizzerEditorLib
from QuizzerEditorLib import EditUtil

from slicer.util import EXIT_SUCCESS


##########################################################################
#
# class CoreWidgets
#
##########################################################################

class CoreWidgets:
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #-------------------------------------------
    #        Custom Widgets
    #-------------------------------------------
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, oSession):
        self.sClassName = type(self).__name__
        
        self.oUtilsMsgs = UtilsMsgs()

        self.oSession = oSession

        self._dictTabIndices = {'Quiz':0, 'ExtraTools':-1, 'SegmentEditor':-1}  #defaults
        self._iPreviousTabIndex = 0

        self._sSessionContourVisibility = 'Outline'
        self._sSessionContourOpacity = 1.0
        
        self._bResetView = False

    #-------------------------------------------
    #        Getters / Setters
    #-------------------------------------------
        
    #----------
    def SetFilesIO(self, oFilesIO):
        self.oFilesIO = oFilesIO
        
    #----------
    def SetIOXml(self, oIOXml):
        self.oIOXml = oIOXml
        
    #----------
    def SetCustomWidgets(self, oCustomWidgets):
        self.oCustomWidgets = oCustomWidgets

    #----------
    def SetImageView(self, oImageView):
        self.oImageView = oImageView
        
    #----------
    def SetTabIndex(self, sTabName, iTabIndex):
        self._dictTabIndices[sTabName] = iTabIndex
        
    #----------
    def GetTabIndex(self, sTabName):
        return self._dictTabIndices[sTabName]
        
    #----------
    def SetPreviousTabIndex(self, iTabIndex):
        self._iPreviousTabIndex = iTabIndex
        
    #----------
    def GetPreviousTabIndex(self):
        return self._iPreviousTabIndex

    #----------
    def ResetExtraToolsDefaults(self):
        self.ResetContourVisibilityToSessionDefault()
        self.SetViewLinesOnAllDisplays(False)
        self.SetMeasurementVisibility(True)
        
    #----------
    def SetResetView(self, bTF):
        self._bResetView = bTF
        
    #----------
    def GetResetView(self):
        return self._bResetView
        
    #----------
    def AddExtraToolsTab(self):
 
        # add extra tools tab to quiz widget
        self.tabExtraTools = qt.QWidget()
        self.oSlicerInterface.qTabWidget.addTab(self.tabExtraTools,"Extra Tools")
        self.SetTabIndex('ExtraTools',self.oSlicerInterface.qTabWidget.count - 1)
        self.oSlicerInterface.qTabWidget.setTabEnabled(self.GetTabIndex('ExtraTools'), True)
         
        widget = self.SetupExtraToolsButtons()
        self.tabExtraTools.setLayout(widget)

    #----------
    def InitializeTabSettings(self):
        self.slEditorMasterVolume = None
        self.slEditorCurrentTool = 'DefaultTool'
        self.SetPreviousTabIndex(0)
        
        self.btnWindowLevel.setChecked(False)
        self.onWindowLevelClicked()
        self.btnCrosshairs.setChecked(False)
        self.onCrosshairsClicked()

    #----------
    def SetGoToBookmarkRequestButton(self, iPageIndex):

        lsBookmarkRequest = self.oCustomWidgets.GetGoToBookmarkRequest(iPageIndex)

        if lsBookmarkRequest !=[] :
            
            if len(lsBookmarkRequest) > 1:
                    self._btnGoToBookmark.text = lsBookmarkRequest[1]
            else:
                self._btnGoToBookmark.text = "Return"

            self._btnGoToBookmark.visible = True
            self._btnGoToBookmark.enabled = True
        else:
            self._btnGoToBookmark.visible = False
            self._btnGoToBookmark.enabled = False
            
    #----------
    #----------   Segment editor
    #----------

    #----------
    def AddSegmentationModule(self, bTF):

        if bTF == True:
            # add segment editor tab to quiz widget
            self.oSlicerInterface.qTabWidget.addTab(slicer.modules.quizzereditor.widgetRepresentation(),"Segment Editor")
            self.SetTabIndex('SegmentEditor', self.oSlicerInterface.qTabWidget.count - 1)
            self.oSlicerInterface.qTabWidget.setTabEnabled(self.GetTabIndex('SegmentEditor'), True)
            self.InitializeTabSettings()
            
    #----------
    def InitializeNullEditorSettings(self):
        
        slicer.modules.quizzereditor.widgetRepresentation().self().toolsBox.selectEffect('DefaultTool')
        slicer.modules.quizzereditor.widgetRepresentation().self().updateLabelFrame(None)
        slicer.modules.quizzereditor.widgetRepresentation().self().helper.setMasterVolume(None)

    #----------
    def CaptureEditorSettings(self):
        
        self.slEditorCurrentTool = EditUtil.getCurrentEffect()
        self.slEditorMasterVolume = slicer.modules.quizzereditor.widgetRepresentation().self().helper.masterSelector.currentNode()
        self.fCurrentContourRadius = EditUtil.getParameterNode().GetParameter("PaintEffect,radius")
        
    #----------
    def ResetEditorSettings(self):
        
        if self.slEditorMasterVolume != None:
            # note : this order is important
            slicer.modules.quizzereditor.widgetRepresentation().self().helper.setMasterVolume(self.slEditorMasterVolume)
            slicer.modules.quizzereditor.widgetRepresentation().self().updateLabelFrame(True)
            EditUtil.setCurrentEffect(self.slEditorCurrentTool)
            EditUtil.getParameterNode().SetParameter("PaintEffect,radius", self.fCurrentContourRadius)
            
        else:
            self.InitializeNullEditorSettings()
            
    #----------
    def SetEditorContourToolRadius(self, fRadius):
        
        slicer.modules.quizzereditor.widgetRepresentation().self().SetContourToolRadius(fRadius)
        
    
    #----------
    #----------   NPlanes View
    #----------
    
    #----------
    def GetNPlanesImageComboBoxSelection(self):
        ''' return the index and image view object to the xml image that matches the image name and 
            orientation selected in the combo boxes
        '''
        
        # orientation has been defined in the NPlanes orientation-destination variable
        if len(self.GetNPlanesView()) > 1:
            sSelectedOrientation = 'All'   # all 3 planes was selected
        else:
            sSelectedOrientation = self.GetNPlanesViewOrientation(0)  # 1 Plane in a specific orientation
        
        # get selected image name from combo box
        sImageName = self.qComboImageList.currentText
        iQuizIndex = 0
        oImageViewNode = None
        bFoundFirstNameMatch = False
        bFoundOrientationMatch = False
        
        # determine which image is to be displayed in an alternate viewing mode (3 Planes or 1 Plane)
        loImageViewNodes = self.oImageView.GetImageViewList()
        for oImageViewNode in loImageViewNodes:
            if oImageViewNode.sNodeName == sImageName:
                if not bFoundFirstNameMatch:
                    bFoundFirstNameMatch = True
                    iQuizFirstNameMatch = iQuizIndex
                    oImageViewNodeFirstNameMatch = oImageViewNode
                if sSelectedOrientation == 'All':
                    break
                else:
                    if sSelectedOrientation == oImageViewNode.sOrientation:
                        bFoundOrientationMatch = True
                        break
                    else:
                        iQuizIndex = iQuizIndex + 1

            
            else:
                iQuizIndex = iQuizIndex + 1
        
        # There may not have been an xml element with the selected orientation view
        #    Reset to the first name match
        if not bFoundOrientationMatch:
            iQuizIndex = iQuizFirstNameMatch
            oImageViewNode = oImageViewNodeFirstNameMatch
            
        return oImageViewNode, iQuizIndex
        
    #----------
    def GetNPlanesComboBoxCount(self):
        return self.qComboImageList.count
    
    #----------
    def SetNPlanesView(self):
        
        self.oSession.sViewingMode = self.qComboNPlanesList.currentText

       
        self.oSession.lsLayoutWidgets = []  # widgets for contour visibility list
        self.oSession.lsLayoutWidgets.append('Red')

        
        if self.oSession.sViewingMode == "1 Plane Axial":
            self.llsNPlanesOrientDest = [["Axial","Red"]]
        elif self.oSession.sViewingMode == "1 Plane Sagittal":
            self.llsNPlanesOrientDest = [["Sagittal","Red"]]
        elif self.oSession.sViewingMode == "1 Plane Coronal":
            self.llsNPlanesOrientDest = [["Coronal","Red"]]
        elif self.oSession.sViewingMode == "3 Planes":
            self.llsNPlanesOrientDest = [["Axial","Red"],["Coronal","Green"],["Sagittal","Yellow"]]
            self.oSession.lsLayoutWidgets.append('Green')
            self.oSession.lsLayoutWidgets.append('Yellow')
            

        
    #----------
    def GetNPlanesView(self):
        return self.llsNPlanesOrientDest
                
    #----------
    def GetNPlanesViewOrientation(self, indPlane):

        return self.llsNPlanesOrientDest[indPlane][0]

    #----------
    def SetNPlanesComboBoxImageNames(self):
        
        self.qComboImageList.clear()
        
        lNamesAdded = []
        loImageViewNodes = self.oImageView.GetImageViewList()
        for oImageViewNode in loImageViewNodes:
            if oImageViewNode.sViewLayer == 'Background' or oImageViewNode.sViewLayer == 'Foreground':
                if oImageViewNode.sNodeName in lNamesAdded:
                    pass
                else:
                    lNamesAdded.append(oImageViewNode.sNodeName)
                    self.qComboImageList.addItem(oImageViewNode.sNodeName)
                    

    #----------
    #----------   Contours outline/fill and opacity
    #----------

    #----------
    def SetContourVisibilityCheckBox(self, sVisibility): 
        # set the contour visibility widget in Extra Tools 
            
        if sVisibility == 'Fill':
            self.qChkBoxFillOrOutline.setChecked(True)
        else:
            self.qChkBoxFillOrOutline.setChecked(False)

    #----------
    def GetSessionContourOpacityDefault(self):
        # default for opacity for the session
        
        return self._sSessionContourOpacity

    #----------
    def GetContourDisplayState(self):
        # get current settings from the extra tools widgets describing the contour display state
        
        bFill = self.qChkBoxFillOrOutline.checked
        if bFill:
            sFillOrOutline = 'Fill'
        else:
            sFillOrOutline = 'Outline'

        iSliderValue = self.qVisibilityOpacity.value
        if self.qVisibilityOpacity.maximum > self.qVisibilityOpacity.minimum:
            fOpacity = iSliderValue / (self.qVisibilityOpacity.maximum - self.qVisibilityOpacity.minimum)
        else:
            fOpacity = self.GetSessionContourOpacityDefault()
        
        return sFillOrOutline, iSliderValue, fOpacity
    
    #----------
    def ResetContourDisplayState(self, sFillOrOutline, iSliderValue, fOpacity):
        
        self.SetContourVisibilityCheckBox(sFillOrOutline)           # tool widget Fill/Outline
        self.SetSliderToolFromContourOpacity(fOpacity)              # tool widget Opacity
        self.SetContourOpacityFromSliderValue(iSliderValue)         # image view property
        
    #----------
    def SetContourOpacityFromSliderValue(self, iSliderValue):
        # set the ContourOpacity property of the image view object based on slider value for opacity
        
        if self.oImageView != None:
            if self.qVisibilityOpacity.maximum > self.qVisibilityOpacity.minimum:  # no div by zero
                self.oImageView.SetContourOpacity(iSliderValue / (self.qVisibilityOpacity.maximum - self.qVisibilityOpacity.minimum))
            else:
                self.oImageView.SetContourOpacity(self.GetSessionContourOpacityDefault())
                
            # reset outline or fill
            self.onContourDisplayStateChanged()
        
    #----------
    def SetSliderToolFromContourOpacity(self, fOpacity):
        # set Slider widget position for opacity
        
        iSliderValue = int(fOpacity * (self.qVisibilityOpacity.maximum - self.qVisibilityOpacity.minimum))    
        self.qVisibilityOpacity.setValue(iSliderValue)

    #----------
    def ResetContourVisibilityToSessionDefault(self):
        # reset widgets and the imageView property to the session default of contour visibility 
        
        self.SetContourVisibilityCheckBox(self.oCustomWidgets.GetSessionContourVisibilityDefault())    # tool widget Fill/Outline
        self.SetSliderToolFromContourOpacity(self.GetSessionContourOpacityDefault())    # tool widget Opacity
        self.SetContourOpacityFromSliderValue(self.qVisibilityOpacity.value)            # image view property

    
    #----------
    #----------   Quiz tabs
    #----------

    #----------
    def SegmentationTabEnabler(self, bTF):

        self.oSlicerInterface.qTabWidget.setTabEnabled(self.GetTabIndex('SegmentEditor') , bTF)
        
    #----------
    def GetSegmentationTabEnabled(self):
        bTF = self.oSlicerInterface.qTabWidget.isTabEnabled(self.GetTabIndex('SegmentEditor') )
        return bTF
    
    #----------
    def EnableTabBar(self, bTF):
        self.oSlicerInterface.qTabWidget.tabBar().setEnabled(bTF)
        

    #----------
    #----------   Markup lines
    #----------

    #----------
    def EnableMarkupLinesTF(self, bTF):
        
        self.btnAddMarkupsLine.enabled = bTF
        self.btnClearLines.enabled = bTF
        if bTF:
            self.btnAddMarkupsLine.setStyleSheet("QPushButton{ background-color: rgb(0,179,246); color: black }")
            self.btnClearLines.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: black }")
        else:
            self.btnAddMarkupsLine.setStyleSheet("QPushButton{ background-color: rgb(0,179,246); color: white }")
            self.btnClearLines.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: white }")

    #----------
    def SetMeasurementVisibility(self, bTF):
        self.qChkBoxMeasurementVisibility.setChecked(bTF)
        self.onMeasurementVisibilityStateChanged()
        
    #----------
    def SetViewLinesOnAllDisplays(self, bTF):
        self.qChkBoxViewOnAllDisplays.setChecked(bTF)
        self.onViewLinesOnAllDisplaysStateChanged()
        

    #-------------------------------------------
    #        Functions
    #-------------------------------------------
    

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetupWidgets(self, slicerMainLayout):

        self.oSlicerInterface = SlicerInterface(self.oFilesIO)
        self.oSlicerInterface.CreateLeftLayoutAndWidget()

        self.SetupButtons()
        self.oSlicerInterface.qLeftLayout.addWidget(self.qButtonGrpBox)

        self.oSlicerInterface.AddQuizLayoutWithTabs()
        self.oSlicerInterface.qTabWidget.currentChanged.connect(self.onTabChanged)
       
        slicerMainLayout.addWidget(self.oSlicerInterface.qLeftWidget)  

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetupButtons(self):
        
        qProgressLabel = qt.QLabel('Progress ')
        self.progress = qt.QProgressBar()
        self.progress.setGeometry(0, 0, 100, 20)
        self.progress.setStyleSheet("QProgressBar{ text-align: center } QProgressBar::chunk{ background-color: rgb(0,179,246) }")
 

        # create buttons
        
        # add horizontal layout
        self.qButtonGrpBox = qt.QGroupBox()
        self.qButtonGrpBox.setTitle('Baines Image Quizzer')
        self.qButtonGrpBox.setStyleSheet("QGroupBox{ font-size: 14px; font-weight: bold}")
        self.qButtonGrpBoxLayout = qt.QHBoxLayout()
        self.qButtonGrpBox.setLayout(self.qButtonGrpBoxLayout)

        # Next button
        self._btnNext = qt.QPushButton("Next")
        self._btnNext.toolTip = "Save responses and display next set of questions."
        self._btnNext.enabled = True
        self._btnNext.setStyleSheet("QPushButton{ background-color: rgb(0,179,246); color: black }")
        self._btnNext.clicked.connect(self.onNextButtonClicked)
        
        # Back button
        self._btnPrevious = qt.QPushButton("Previous")
        self._btnPrevious.toolTip = "Display previous set of questions."
        self._btnPrevious.enabled = True
        self._btnPrevious.setStyleSheet("QPushButton{ background-color: rgb(255,149,0); color: black }")
        self._btnPrevious.clicked.connect(self.onPreviousButtonClicked)


        # Exit button
        self._btnExit = qt.QPushButton("Exit")
        self._btnExit.toolTip = "Save quiz and exit Slicer."
        self._btnExit.enabled = True
        self._btnExit.setStyleSheet("QPushButton{ background-color: rgb(255,0,0); color: black; font-weight: bold }")
        # use lambda to pass argument to this PyQt slot without invoking the function on setup
        self._btnExit.clicked.connect(lambda: self.onExitButtonClicked('ExitBtn'))

        # Repeat button
        self._btnRepeat = qt.QPushButton("Repeat")
        self._btnRepeat.toolTip = "Save current responses and repeat."
        self._btnRepeat.enabled = False
        self._btnRepeat.visible = False
        self._btnRepeat.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: black}")
        self._btnRepeat.clicked.connect(self.onRepeatButtonClicked)


        # Bookmark button
        self._btnGoToBookmark = qt.QPushButton("Return")
        self._btnGoToBookmark.toolTip = "Returns to pre-defined page"
        self._btnGoToBookmark.enabled = True
        self._btnGoToBookmark.visible = True
        self._btnGoToBookmark.setStyleSheet("QPushButton{ background-color: rgb(136, 82, 191); color: white; font-weight: bold}")
        self._btnGoToBookmark.clicked.connect(self.onGoToBookmarkButtonClicked)
        

        self.qButtonGrpBoxLayout.addWidget(self._btnExit)
        self.qButtonGrpBoxLayout.addWidget(qProgressLabel)
        self.qButtonGrpBoxLayout.addWidget(self.progress)
        self.qButtonGrpBoxLayout.addWidget(self._btnPrevious)
        self.qButtonGrpBoxLayout.addWidget(self._btnNext)
        self.qButtonGrpBoxLayout.addWidget(self._btnRepeat)
        self.qButtonGrpBoxLayout.addWidget(self._btnGoToBookmark)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetupExtraToolsButtons(self):
        
        # create buttons

        self.tabExtraToolsLayout = qt.QVBoxLayout()

        

        # >>>>>>>>>>>>>>>>>>>>
        # Window/Level interactive mode
        self.qDisplayMgrGrpBox = qt.QGroupBox()
        self.qDisplayMgrGrpBox.setTitle("Interactive Modes")
        self.qDisplayMgrGrpBox.setStyleSheet("QGroupBox{ font-size: 11px; font-weight: bold}")
        self.qDisplayMgrGrpBoxLayout = qt.QGridLayout()
        self.qDisplayMgrGrpBoxLayout.addLayout(0,0,1,3)
        self.qDisplayMgrGrpBox.setLayout(self.qDisplayMgrGrpBoxLayout)
        
        self.tabExtraToolsLayout.addWidget(self.qDisplayMgrGrpBox)

        btnHidden = qt.QPushButton('')
        btnHidden.enabled = False
        btnHidden.setStyleSheet("QPushButton{ border:none }")
        self.qDisplayMgrGrpBoxLayout.addWidget(btnHidden,0,0)
        
        
        self.btnWindowLevel = qt.QPushButton('Window / Level')
        self.btnWindowLevel.enabled = True
        self.btnWindowLevel.setCheckable(True)
        self.btnWindowLevel.setStyleSheet("QPushButton{ background-color: rgb(173,220,237); color: black }")
        self.btnWindowLevel.clicked.connect(self.onWindowLevelClicked)
        self.qDisplayMgrGrpBoxLayout.addWidget(self.btnWindowLevel,0,1)

        btnHidden = qt.QPushButton('')
        btnHidden.enabled = False
        btnHidden.setStyleSheet("QPushButton{ border:none }")
        self.qDisplayMgrGrpBoxLayout.addWidget(btnHidden,0,2)


        # >>>>>>>>>>>>>>>>>>>>
        # Crosshairs
        
        self.btnCrosshairs = qt.QPushButton('Crosshairs - use Shift key')
        self.btnCrosshairs.enabled = True
        self.btnCrosshairs.setCheckable(True)
        self.btnCrosshairs.setStyleSheet("QPushButton{ background-color: rgb(173,220,237); color: black }")
        self.btnCrosshairs.clicked.connect(self.onCrosshairsClicked)
        self.qDisplayMgrGrpBoxLayout.addWidget(self.btnCrosshairs,0,3)


        btnHidden = qt.QPushButton('')
        btnHidden.enabled = False
        btnHidden.setStyleSheet("QPushButton{ border:none }")
        self.qDisplayMgrGrpBoxLayout.addWidget(btnHidden,0,4)

        
        # >>>>>>>>>>>>>>>>>>>>
        # Viewing modes
        self.qDisplayOptionsGrpBox = qt.QGroupBox()
        self.qDisplayOptionsGrpBox.setTitle('Viewing Display Options')
        self.qDisplayOptionsGrpBox.setStyleSheet("QGroupBox{ font-size: 11px; font-weight: bold}")
        self.qDisplayOptionsGrpBoxLayout = qt.QGridLayout()
        self.qDisplayOptionsGrpBox.setLayout(self.qDisplayOptionsGrpBoxLayout)
        
        qViewImageLabel = qt.QLabel("Select image:")
        self.qDisplayOptionsGrpBoxLayout.addWidget(qViewImageLabel,0,0)
        
        self.qComboImageList = qt.QComboBox()
        qSize = qt.QSizePolicy()
        qSize.setHorizontalPolicy(qt.QSizePolicy.Ignored)
        self.qComboImageList.setSizePolicy(qSize)
        self.qDisplayOptionsGrpBoxLayout.addWidget(self.qComboImageList,0,1)

        qViewNPlanesLabel = qt.QLabel("Select view mode:")
        self.qDisplayOptionsGrpBoxLayout.addWidget(qViewNPlanesLabel,1,0)
        
        self.qComboNPlanesList = qt.QComboBox()
        self.qDisplayOptionsGrpBoxLayout.addWidget(self.qComboNPlanesList,1,1)
        self.qComboNPlanesList.addItem("3 Planes")
        self.qComboNPlanesList.addItem("1 Plane Axial")
        self.qComboNPlanesList.addItem("1 Plane Sagittal")
        self.qComboNPlanesList.addItem("1 Plane Coronal")

        
        self.btnNPlanesView = qt.QPushButton('Display view')
        self.btnNPlanesView.enabled = True
        self.btnNPlanesView.setStyleSheet("QPushButton{ background-color: rgb(0,179,246); color: black }")
        self.btnNPlanesView.clicked.connect(self.onNPlanesViewClicked)
        self.qDisplayOptionsGrpBoxLayout.addWidget(self.btnNPlanesView,0,2)

        
        self.btnResetView = qt.QPushButton('Reset to default')
        self.btnResetView.enabled = True
        self.btnResetView.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: black }")
        self.btnResetView.clicked.connect(lambda: self.onResetViewClicked('NPlanes'))
        self.qDisplayOptionsGrpBoxLayout.addWidget(self.btnResetView,1,2)

        self.tabExtraToolsLayout.addWidget(self.qDisplayOptionsGrpBox)
        

        # >>>>>>>>>>>>>>>>>>>>
        # Ruler tools
        self.qLineToolsGrpBox = qt.QGroupBox()
        self.qLineToolsGrpBox.setTitle('Line Measurement')
        self.qLineToolsGrpBox.setStyleSheet("QGroupBox{ font-size: 11px; font-weight: bold}")
        self.qLineToolsGrpBoxLayout = qt.QGridLayout()
        self.qLineToolsGrpBox.setLayout(self.qLineToolsGrpBoxLayout)


 
        self.slMarkupsLineWidget = slicer.qSlicerMarkupsPlaceWidget()
        # Hide all buttons and only show delete button
        self.slMarkupsLineWidget.buttonsVisible=False
        self.slMarkupsLineWidget.deleteButton().show()
        self.qLineToolsGrpBoxLayout.addWidget(self.slMarkupsLineWidget,0,0)

        # remove the last point of markup line created
        qLineToolLabelTrashPt = qt.QLabel('Remove last point')
        qLineToolLabelTrashPt.setAlignment(QtCore.Qt.AlignCenter)
        self.qLineToolsGrpBoxLayout.addWidget(qLineToolLabelTrashPt,1,0)
        
        # Clear all markup lines
        self.btnClearLines = qt.QPushButton("Clear all")
        self.btnClearLines.toolTip = "Remove all markup lines."
        self.btnClearLines.enabled = True
        self.btnClearLines.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: black }")
        self.btnClearLines.clicked.connect(self.onClearLinesButtonClicked)
        self.qLineToolsGrpBoxLayout.addWidget(self.btnClearLines,0,1)

        self.btnAddMarkupsLine = qt.QPushButton("Add new line")
        self.btnAddMarkupsLine.enabled = True
        self.btnAddMarkupsLine.setStyleSheet("QPushButton{ background-color: rgb(0,179,246); color: black }")
        self.btnAddMarkupsLine.clicked.connect(self.onAddLinesButtonClicked)
        self.qLineToolsGrpBoxLayout.addWidget(self.btnAddMarkupsLine,0,2)
        
        # Markup display view visibility
        self.qChkBoxViewOnAllDisplays = qt.QCheckBox('Display in all views')
        self.qChkBoxViewOnAllDisplays.setChecked(False)
        self.qChkBoxViewOnAllDisplays.setStyleSheet("margin-left:75%")
        self.qChkBoxViewOnAllDisplays.stateChanged.connect(self.onViewLinesOnAllDisplaysStateChanged)
        self.qLineToolsGrpBoxLayout.addWidget(self.qChkBoxViewOnAllDisplays,1,2)
        
        # Markup measurement visibility
        self.qChkBoxMeasurementVisibility = qt.QCheckBox('Show length')
        self.qChkBoxMeasurementVisibility.setChecked(True)
        self.qChkBoxMeasurementVisibility.setStyleSheet("margin-left:75%")
        self.qChkBoxMeasurementVisibility.stateChanged.connect(self.onMeasurementVisibilityStateChanged)
        self.qLineToolsGrpBoxLayout.addWidget(self.qChkBoxMeasurementVisibility,2,2)
 
        
        
        self.tabExtraToolsLayout.addWidget(self.qLineToolsGrpBox)

        # >>>>>>>>>>>>>>>>>>>>
        # Contour visibility tools
        self.qContourVisibilityGrpBox = qt.QGroupBox()
        self.qContourVisibilityGrpBox.setTitle('Contour Visibility - Fill/Outline and Opacity')
        self.qContourVisibilityGrpBox.setStyleSheet("QGroupBox{ font-size: 11px; font-weight: bold}")
        self.qContourVisibilityGrpBoxLayout = qt.QHBoxLayout()
        self.qContourVisibilityGrpBox.setLayout(self.qContourVisibilityGrpBoxLayout)

        qLabelOpacity = qt.QLabel(' Opacity')
        qLabelOpacity.setMinimumWidth(200)
        qLabelOpacity.setAlignment(QtCore.Qt.AlignRight)
        self.qContourVisibilityGrpBoxLayout.addWidget(qLabelOpacity)
        
        self.qVisibilityOpacity = qt.QSlider(QtCore.Qt.Horizontal)
        self.qVisibilityOpacity.setMinimum(0)
        self.qVisibilityOpacity.setMaximum(100)
        self.qVisibilityOpacity.setValue(50)
        self.qVisibilityOpacity.setPageStep(1)
        self.qVisibilityOpacity.connect("valueChanged(int)", self.SetContourOpacityFromSliderValue)
        self.qContourVisibilityGrpBoxLayout.addWidget(self.qVisibilityOpacity)
        self.qContourVisibilityGrpBoxLayout.addSpacing(30)

        self.qChkBoxFillOrOutline = qt.QCheckBox('Fill')
        self.qChkBoxFillOrOutline.stateChanged.connect(self.onContourDisplayStateChanged)
        self.qContourVisibilityGrpBoxLayout.addWidget(self.qChkBoxFillOrOutline)
        self.qContourVisibilityGrpBoxLayout.addSpacing(30)


        self.tabExtraToolsLayout.addWidget(self.qContourVisibilityGrpBox)
        
        self.tabExtraToolsLayout.addStretch()
        

        return self.tabExtraToolsLayout
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def EnableButtons(self):
        
        
        # for Repeat button
        if self.oCustomWidgets.GetPageLooping(self.oSession.GetCurrentPageIndex()):
            self._btnRepeat.visible = True
            
            
            # only enable Repeat button in looping if the page is not complete and the user is on the last question set
            
            if self.oCustomWidgets.GetPageCompleteAttribute(self.oSession.GetCurrentPageIndex()) == False:
                if self.oSession.CheckForLastQuestionSetForPage() == True:
                    self._btnRepeat.enabled = True
                    self._btnRepeat.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: black}")
                    
                    # check if button script rerun is required
                    if self.oCustomWidgets.GetButtonScriptRerunRequired(self.oSession.GetCurrentPageIndex()):
                        if self.oSession.CheckIfLastRepAndNextPageIncomplete() == True:
                            self._btnRepeat.enabled = True
                            self._btnRepeat.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: black}")
                        else: # force user to step through subsequent reps
                            self._btnRepeat.enabled = False
                            self._btnRepeat.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: white}")
                            
                else:
                    self._btnRepeat.enabled = False
                    self._btnRepeat.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: white}")
            else:
                self._btnRepeat.enabled = False
                self._btnRepeat.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: white}")
                    

        else:
            self._btnRepeat.visible = False
            self._btnRepeat.enabled = False
            self._btnRepeat.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: white}")

            
            
        # assign button description           
        if (self.oSession.GetCurrentNavigationIndex() == len(self.oSession.GetNavigationList()) - 1):
            self._btnNext.setText("Finish")
        else:
            self._btnNext.setText("Next")
        
        # beginning of quiz
        if (self.oSession.GetCurrentNavigationIndex() == 0):
            self._btnNext.enabled = True
            self._btnPrevious.enabled = False

        # end of quiz
        elif (self.oSession.GetCurrentNavigationIndex() == len(self.oSession.GetNavigationList()) - 1):
            self._btnNext.enabled = True
            self._btnPrevious.enabled = True

        # somewhere in middle
        else:
            self._btnNext.enabled = True
            self._btnPrevious.enabled = True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def DisableButtons(self):
        self._btnNext.enabled = False
        self._btnPrevious.enabled = False
        self._btnRepeat.enabled = False




    #-------------------------------------------
    #        Event Handlers
    #-------------------------------------------
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onTabChanged(self):
        ''' When changing tabs reset segment editor interface.
            Ensure window/level tool is turned off.
        '''

        self.btnWindowLevel.setChecked(False)
        self.onWindowLevelClicked()
    
    
        # when moving off the Segment Editor tab
        if self.GetPreviousTabIndex() == self.GetTabIndex('SegmentEditor'):
            self.CaptureEditorSettings()
            self.InitializeNullEditorSettings()
            
        # when returning to the Segment Editor tab
        if self.oSlicerInterface.qTabWidget.currentIndex == self.GetTabIndex('SegmentEditor'):
            self.ResetEditorSettings()

        self.SetPreviousTabIndex(self.oSlicerInterface.qTabWidget.currentIndex)
    
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onNextButtonClicked(self):

        try:        
            if self._btnRepeat.enabled == True:
                if self._btnNext.text == 'Finish':
                    sNextPhrase = 'Finish'
                else:
                    sNextPhrase = 'move to Next set'
                sMsg = "You have the option to repeat this set of images and questions." +\
                        "\nClick 'OK' to " + sNextPhrase + " otherwise click 'Cancel'."
                
                qtAns = self.oUtilsMsgs.DisplayOkCancel(sMsg)
                if qtAns == qt.QMessageBox.Cancel:
                    return

            sMsg = ''
            sCompletedMsg = ''
            sSaveMsg = ''
            sInteractionMsg = 'Next'
                    
            self.oSession.SetInteractionLogOnOff('Off',sInteractionMsg)
                
            self.DisableButtons()    
            if self.oSession.sViewingMode != 'Default':
                self.onResetViewClicked('Next')
    
            if self.oSession.GetCurrentNavigationIndex() + 1 == len(self.oSession.GetNavigationList()):
    
                # the last question was answered - check if user is ready to exit
                self.onExitButtonClicked('Finish') # a save is done in here
                
                # the user may have cancelled the 'finish'
                # bypass remainder of the 'next' button code
    
            else:
                # this is not end of quiz, do a save and display the next page
                
                bSuccess, sSaveMsg = self.oSession.PerformSave('NextBtn') 
                if bSuccess:
                    
                    bSuccess, sCompletedMsg = self.oSession.UpdateCompletions('NextBtn')
                    if bSuccess:
                        
                        self.oSession.CaptureAndSaveImageState()
    
                        ########################################    
                        # set up for next page
                        ########################################    
                        
                        # if last question set, clear list and scene
                        if self.oSession.CheckForLastQuestionSetForPage() == True:
                            self.oSession.ClearQuestionSetList()
                            slicer.mrmlScene.Clear()
                            bChangeXmlPageIndex = True
                        else:
                            # clear quiz widgets only
                            self.oSlicerInterface.ClearLayout(self.oSlicerInterface.qQuizLayout)
                            bChangeXmlPageIndex = False
    
    
                        self.oSession.SetCurrentNavigationIndex(self.oSession.GetCurrentNavigationIndex() + 1 )
                        self.progress.setValue(self.oSession.GetCurrentNavigationIndex())
                        self.oSession.InitializeImageDisplayOrderIndices(self.oSession.GetCurrentPageIndex())
                        
                        if bChangeXmlPageIndex:
                            self.oSession.SetupPageState(self.oSession.GetCurrentPageIndex())
                            if self.oCustomWidgets.GetButtonScriptRerunRequired(self.oSession.GetCurrentPageIndex()):
                                self.oCustomWidgets.SetPageIncomplete(self.oSession.GetCurrentPageIndex())
                            
                        self.InitializeTabSettings()
                        self.oSession.DisplayQuizLayout()
                        self.oSession.DisplayImageLayout()

                        
            sInteractionMsg = sInteractionMsg + sSaveMsg + sCompletedMsg

            self.oSession.SetInteractionLogOnOff('On',sInteractionMsg)
            self.EnableButtons()
                
        except:
            iPage = self.oSession.GetCurrentPageIndex() + 1
            tb = traceback.format_exc()
            sMsg = "onNextButtonClicked: Error moving to next page. Current page: " + str(iPage) \
                   + "\n\n" + tb 
            self.oUtilsMsgs.DisplayError(sMsg)
                
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onPreviousButtonClicked(self):
        
            
        sMsg = ''
        try:
 
            self.SaveAndGoToPreviousPageDisplay('Previous', self.oSession.GetCurrentNavigationIndex() - 1)
 
 
        except:
            iPage = self.oSession.GetCurrentPageIndex() + 1
            tb = traceback.format_exc()
            sMsg = "onPreviousButtonClicked: Error moving to previous page. Current page: " + str(iPage) \
                   + "\n\n" + tb 
            self.oUtilsMsgs.DisplayError(sMsg)
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onExitButtonClicked(self,sCaller):
        ''' this Exit function can be triggered by pressing 'Exit' button or by pressing 'Finish'
        '''

        try:
            bExit = False
            sMsg = ''
            sCompletedMsg = ''
            sSaveMsg = ''
            sCancelExitMsg = ''
            sInteractionMsg = 'Exit'
            
            sPageID = self.oCustomWidgets.GetPageID(self.oSession.GetCurrentPageIndex())
            sPageDescriptor = self.oCustomWidgets.GetPageDescriptor(self.oSession.GetCurrentPageIndex())
                    
            
            self.progress.setValue(self.oSession.GetCurrentNavigationIndex() + 1)
            if len(self.oSession.GetNavigationList()) >0:
                iProgressPercent = int((self.oSession.GetCurrentNavigationIndex() + 1) / len(self.oSession.GetNavigationList()) * 100)
            else:
                # error in creating the composite navigation index - assign percent to 100 for exiting
                self.oUtilsMsgs.DisplayError('ERROR creating quiz indices - Exiting')
            self.progress.setFormat(sPageID + '  ' + sPageDescriptor + '    ' + str(iProgressPercent) + '%')
            
            sMsg = 'Do you wish to exit?'
            if sCaller == 'ExitBtn':
                sMsg = sMsg + ' \nYour responses will be saved. Quiz may be resumed.'
            else:
                if sCaller == 'Finish':
                    sMsg = sMsg + " \nYour quiz is complete and your responses will be locked." \
                                + " \n\nIf you wish to resume at a later time, press 'Cancel' here, then use the 'Exit' button."
    
            qtAns = self.oUtilsMsgs.DisplayOkCancel(sMsg)
            if qtAns == qt.QMessageBox.Ok:

                self.oSession.SetInteractionLogOnOff('Off',sInteractionMsg)
                self.DisableButtons()    

                bSuccess, sSaveMsg = self.oSession.PerformSave(sCaller)
                if bSuccess:
                    
                    bSuccess, sCompletedMsg = self.oSession.UpdateCompletions(sCaller)
                    if bSuccess:

                        self.oSession.CaptureAndSaveImageState()
            
                        self.oSession.QueryThenSendEmailResults()
                        
                        # update shutdown batch file to remove SlicerDICOMDatabase
                        self.oFilesIO.CreateShutdownBatchFile()
                
                        slicer.util.exit(status=EXIT_SUCCESS)
                        bExit = True    # added for delay in slicer closing down - prevent remaining code from executing
    
            
            else:
                sCancelExitMsg = ' ... cancelled Exit to continue with quiz'
                
            sInteractionMsg = sInteractionMsg + sSaveMsg + sCompletedMsg + sCancelExitMsg
                
            # if code reaches here, either the exit was cancelled or there was 
            # an error in the save
            
            if not(bExit):
                self.oSession.SetInteractionLogOnOff('On',sInteractionMsg)
                self.EnableButtons() 
        
                self.progress.setValue(self.oSession.GetCurrentNavigationIndex())
                iProgressPercent = int(self.oSession.GetCurrentNavigationIndex() / len(self.oSession.GetNavigationList()) * 100)
                self.progress.setFormat(sPageID + '  ' + sPageDescriptor + '    ' + str(iProgressPercent) + '%')
    
    
        except:
            iPage = self.oSession.GetCurrentPageIndex() + 1
            tb = traceback.format_exc()
            sMsg = "onExitButtonClicked: Error exiting quiz. Current page: " + str(iPage) \
                   + "\n\n" + tb 
            self.oUtilsMsgs.DisplayError(sMsg)
            
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onRepeatButtonClicked(self):
        ''' Function to manage repeating a page node when user requests a repeat (looping).
            This is generally used for multiple lesions.
        '''
        
        try:        
            qtAns = self.oUtilsMsgs.DisplayOkCancel(\
                                "Are you sure you want to repeat this set of images and questions?" +\
                                "\nIf No, click 'Cancel' and press 'Next' to continue.")
            if qtAns == qt.QMessageBox.Ok:
                sMsg = ''
                sCompletedMsg = ''
                sSaveMsg = ''
                sInteractionMsg = 'Repeat'

                self.oSession.SetInteractionLogOnOff('Off', sInteractionMsg)
                
                self.DisableButtons()    
                if self.oSession.sViewingMode != 'Default':
                    self.onResetViewClicked('Repeat')

                bSuccess, sSaveMsg = self.oSession.PerformSave('NextBtn')
                if bSuccess:

                    bSuccess, sCompletedMsg = self.oSession.UpdateCompletions('NextBtn')
                    if bSuccess:
    
                        self.oSession.CaptureAndSaveImageState()
                        
                        self.oSession.CreateRepeatedPageNode()
    
                        # cleanup
                        self.oSession.ClearQuestionSetList()
                        slicer.mrmlScene.Clear()
                
                        
                        self.progress.setMaximum(len(self.oSession.GetNavigationList()))
                        self.progress.setValue(self.oSession.GetCurrentNavigationIndex())
                        
                        self.oSession.SetupPageState(self.oSession.GetCurrentPageIndex())
                        if self.oCustomWidgets.GetButtonScriptRerunRequired(self.oSession.GetCurrentPageIndex()):
                            self.oCustomWidgets.SetPageIncomplete(self.oSession.GetCurrentPageIndex())

                        self.InitializeTabSettings()
                        self.oSession.DisplayQuizLayout()
                        self.oSession.DisplayImageLayout()
                        

                sInteractionMsg = sInteractionMsg + sSaveMsg + sCompletedMsg
   
                self.oSession.SetInteractionLogOnOff('On', sInteractionMsg)
                self.EnableButtons()
                
        except:
            iPage = self.oSession.GetCurrentPageIndex() + 1
            tb = traceback.format_exc()
            sMsg = "onRepeatButtonClicked: Error repeating this page. Current page: " + str(iPage) \
                   + "\n\n" + tb 
            self.oUtilsMsgs.DisplayError(sMsg)
    
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onAddLinesButtonClicked(self):
        ''' Add a new markup line - using the PlaceMode functionality
        '''
        self.slMarkupsLineWidget.setMRMLScene(slicer.mrmlScene)
        markupsNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode")
        self.slMarkupsLineWidget.setCurrentNode(slicer.mrmlScene.GetNodeByID(markupsNode.GetID()))
        self.slMarkupsLineWidget.setPlaceModeEnabled(True)

        markupsNode.AddObserver(slicer.vtkMRMLMarkupsLineNode.PointModifiedEvent, self.onMarkupInteraction)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onClearLinesButtonClicked(self):
        ''' A function to clear all markup line nodes from the scene.
        '''
        sMsg = ''
        xPageNode = self.oCustomWidgets.GetNthPageNode(self.oSession.GetCurrentPageIndex())
        bPageComplete = self.oCustomWidgets.GetPageCompleteAttribute(self.oSession.GetCurrentPageIndex())

        if bPageComplete and not self.oCustomWidgets.GetMultipleResponseAllowed():
            sMsg = '\nThis page has already been completed. You cannot remove the markup lines.'
            self.oUtilsMsgs.DisplayWarning(sMsg)
        else:
            try:           
                slLineNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLMarkupsLineNode')
                for node in slLineNodes:
                    slicer.mrmlScene.RemoveNode(node)
                
                # remove all markup line elements stored in xml for this page node
                # and delete the markup line file stored in folder
                lxImages = self.oIOXml.GetChildren(xPageNode, 'Image')
                for xImage in lxImages:
                    lxMarkupLines = self.oIOXml.GetChildren(xImage, 'MarkupLinePath')
                    for xMarkupLine in lxMarkupLines:
                        sPath = self.oIOXml.GetDataInNode(xMarkupLine)
                        sAbsolutePath = self.oFilesIO.GetAbsoluteUserPath(sPath)
                        if os.path.exists(sAbsolutePath):    # same path may exist in multiple xml Image elements
                            os.remove(sAbsolutePath)
                
                    self.oIOXml.RemoveAllElements(xImage, 'MarkupLinePath')
                self.oIOXml.SaveXml(self.oFilesIO.GetUserQuizResultsPath())
            
            except:
                tb = traceback.format_exc()
                sMsg = "onClearLinesButtonClicked: Error clearing all markup lines.  \n\n" + tb 
                self.oUtilsMsgs.DisplayError(sMsg)
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onMarkupInteraction(self, caller, event):
        ''' adjust display once the full markups line is completed
        '''
        markupsNode = caller
        markupIndex = markupsNode.GetDisplayNode().GetActiveControlPoint()

        if markupIndex == 1:        
            self.SetViewLinesOnAllDisplays(self.qChkBoxViewOnAllDisplays.isChecked())
            self.SetMeasurementVisibility(self.qChkBoxMeasurementVisibility.isChecked())
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onWindowLevelClicked(self):
        
        if self.btnWindowLevel.isChecked():
            self.btnWindowLevel.setStyleSheet("QPushButton{ background-color: rgb(0,179,246); color: black }")
            slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(slicer.vtkMRMLInteractionNode.AdjustWindowLevel)
        else:
            self.btnWindowLevel.setStyleSheet("QPushButton{ background-color: rgb(173,220,237); color: black }")
            slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(slicer.vtkMRMLInteractionNode.ViewTransform)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onCrosshairsClicked(self):
        ''' activate the crosshairs tool
        '''
        if self.btnCrosshairs.isChecked():
            
            self.btnCrosshairs.setStyleSheet("QPushButton{ background-color: rgb(0,179,246); color: black }")
            slCrosshairNode = slicer.mrmlScene.GetNodeByID('vtkMRMLCrosshairNodedefault')
            slCrosshairNode.SetCrosshairBehavior(1) # offset jump slice
            slCrosshairNode.SetCrosshairMode(2)     # basic intersection
        else:
            self.btnCrosshairs.setStyleSheet("QPushButton{ background-color: rgb(173,220,237); color: black }")
            slCrosshairNode = slicer.mrmlScene.GetNodeByID('vtkMRMLCrosshairNodedefault')
            slCrosshairNode.SetCrosshairBehavior(1) # offset jump slice
            slCrosshairNode.SetCrosshairMode(0)     # basic intersection
    
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def onNPlanesViewClicked(self):
        ''' display the requested image in the requested viewing mode
        '''
        try:
            self.oSession.SetInteractionLogOnOff('Off','Changing View - Display View Button - NPlanes')

            if self.GetNPlanesComboBoxCount() > 0:
                self.oSession.CaptureAndSaveImageState()
                
                self.SetNPlanesView()
                oImageNodeOverride, iQuizImageIndex = self.GetNPlanesImageComboBoxSelection()
                self.oSession.liImageDisplayOrder = self.oSession.ReorderImageIndexToEnd(iQuizImageIndex)
                self.oImageView.AssignNPlanes(oImageNodeOverride, self.llsNPlanesOrientDest)
                self.oSession.bNPlanesViewingMode = True
        
                #    the current image node being displayed in an alternate view may have been 
                #    repeated in different orientations in the quiz file
                self.oSession.loCurrentQuizImageViewNodes = self.oCustomWidgets.GetMatchingQuizImageNodes(oImageNodeOverride.sImagePath, self.oImageView)
                self.oSession.ApplySavedImageState()
            else:
                sMsg = 'No images have been loaded to display in an alternate viewing mode.'
                self.oUtilsMsgs.DisplayWarning(sMsg)
                
            self.oUtilsMsgs.DisplayTimedMessage('***','Waiting',100) #force Slicer to refresh display before logging resumes
            self.oSession.SetInteractionLogOnOff('On','Changing View - Display View Button - ' + self.qComboNPlanesList.currentText)

        except:
            tb = traceback.format_exc()
            sMsg = "onNPlanesViewClicked: Error setting the NPlanes view (closeup) request.  \n\n" + tb 
            self.oUtilsMsgs.DisplayError(sMsg)
            
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onResetViewClicked(self, sCaller=None):
        ''' Capture responses in the current state (may not be completed) before 
            resetting the viewing nodes to original layout for this page.
            Restore the current responses.
        '''
        
        lsCurrentResponses = []

        try:

            self.SetResetView(True)    
            self.oSession.SetInteractionLogOnOff('Off','Changing View - Reset Button')
            
            sCaptureSuccessLevel, lsCurrentResponses, sMsg = self.oSession.CaptureNewResponses()
            self.oSession.CaptureAndSaveImageState()
            
            sFillOrOutline, iOpacitySliderValue, fOpacity = self.GetContourDisplayState()
            self.oSession.AdjustToCurrentQuestionSet()
            self.oSession.bNPlanesViewingMode = False
            self.oSession.sViewingMode = "Default"
            self.oSession.loCurrentQuizImageViewNodes = []
            self.oSession.DisplayQuizLayout()
            self.oSession.DisplayImageLayout('ResetView')
            
            self.ResetContourDisplayState(sFillOrOutline, iOpacitySliderValue, fOpacity)
            slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(slicer.vtkMRMLInteractionNode.ViewTransform)
            
            # Populate quiz with current responses
            self.oSession.DisplayCurrentResponsesOnResetView(lsCurrentResponses)
            self.oSession.ApplySavedImageState()
            

            if sCaller == 'NPlanes':
                self.oUtilsMsgs.DisplayTimedMessage('***','Waiting',100) #force Slicer to refresh display before logging resumes
                self.oSession.SetInteractionLogOnOff('On','Changing View - Reset Button - caller: ' + sCaller)
                
            self.SetResetView(False)    

        except:
            tb = traceback.format_exc()
            sMsg = "onResetViewClicked: Error resetting the view after NPlanes (closeup) request.  \n\n" + tb 
            self.oUtilsMsgs.DisplayError(sMsg)
            

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onContourDisplayStateChanged(self):
        # when user changes a contour visibility widget setting in the extra tools tab,
        #    adjust the image view property and turn on fill/outline for label maps and segmentations
        
        if self.oImageView != None:
            if self.qChkBoxFillOrOutline.isChecked():
                self.oImageView.SetContourVisibility('Fill')
            else:
                self.oImageView.SetContourVisibility('Outline')
            
            self.oImageView.SetLabelMapOutlineOrFill(self.oSession.lsLayoutWidgets)
    
            xPageNode = self.oCustomWidgets.GetNthPageNode(self.oSession.GetCurrentPageIndex())
            loImageViewNodes = self.oImageView.GetImageViewList()
            for oViewNode in loImageViewNodes:
                if oViewNode.sViewLayer == 'Segmentation':
                    slSegDisplayNode, slSegDataNode = oViewNode.GetSegmentationNodes(xPageNode)
                    self.oImageView.SetSegmentationOutlineOrFill(oViewNode, slSegDisplayNode)
                
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onViewLinesOnAllDisplaysStateChanged(self):
        ''' function to turn on/off display of markup lines in all viewing windows
            or on just the windows displaying the image linked with the viewing window
            where it was created
        '''
        
        dictViewNodes = {"Red":"vtkMRMLSliceNodeRed", "Green":"vtkMRMLSliceNodeGreen", "Yellow":"vtkMRMLSliceNodeYellow", "Slice4":"vtkMRMLSliceNodeSlice4"}


        slMarkupNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLMarkupsLineNode')
        
        for slMarkupNode in slMarkupNodes:
            slMarkupDisplayNode = slMarkupNode.GetDisplayNode()
            lViewNodes = []
            
            if self.qChkBoxViewOnAllDisplays.isChecked():
                slMarkupDisplayNode.SetViewNodeIDs(list(dictViewNodes.values()))
                
            else:
                slAssociatedNodeID = slMarkupNode.GetNthMarkupAssociatedNodeID(0)
                
                
                for oViewNode in self.oImageView.GetImageViewList():

                    if oViewNode.slNode.GetID() == slAssociatedNodeID:                
                        slViewNode = oViewNode.sDestination
                        lViewNodes.append(dictViewNodes[slViewNode])
                        slMarkupDisplayNode.SetViewNodeIDs(lViewNodes)

        slMarkupNodes.UnRegister(slicer.mrmlScene)    #cleanup memory

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onMeasurementVisibilityStateChanged(self):
        # display line measurements on/off
        slMarkupNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLMarkupsLineNode')
        
        for slNode in slMarkupNodes:
            slDisplayNode = slNode.GetDisplayNode()
            if self.qChkBoxMeasurementVisibility.isChecked():
                slDisplayNode.PropertiesLabelVisibilityOn()
            else:
                slDisplayNode.PropertiesLabelVisibilityOff()

        slMarkupNodes.UnRegister(slicer.mrmlScene)    #cleanup memory

        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onGoToBookmarkButtonClicked(self):
        ''' Function to change to previous bookmarked page
            The user will be taken to the most recent Page that has the specified 'BookmarkID'
            Quiz validation checks to see if the GoToBookmark and BookmarkID have the same
            PageGroup number if randomization is turned on. 
            Quiz validation also checks if there is an historical BookmarkID for the GoToBookmark 
        '''
        # find previous page with the BookmarkID match
        xPageNode = self.oCustomWidgets.GetNthPageNode(self.oSession.GetCurrentPageIndex())

        sGoToBookmark = ''
        sGoToBookmarkRequest = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'GoToBookmark')
        if sGoToBookmarkRequest != '':
            sGoToBookmark = sGoToBookmarkRequest.split()[0]

        # set up dictionary with value to match in historical pages
        dictAttribToMatchInHistory = {}
        dictAttribToMatchInHistory['BookmarkID'] = sGoToBookmark
        
        # all page nodes that match - ordered with most recent first
        dictPgNodeAndPgIndex = self.oIOXml.GetMatchingXmlPagesFromAttributeHistory(self.oSession.GetCurrentNavigationIndex(), self.oSession.GetNavigationList(), dictAttribToMatchInHistory)
        lPageIndices = list(dictPgNodeAndPgIndex.values())
        if len(lPageIndices) > 0:
            iBookmarkedPageIndex = lPageIndices[0]
            iBookmarkedNavigationIndex = self.oIOXml.GetNavigationIndexForPage(self.oSession.GetNavigationList(), iBookmarkedPageIndex)
            
            
#             ### for debug ###            
#             sMsg = 'Leaving current screen - return to Bookmark page'\
#                     + '\nCurrentNavigationIndex: ' + str(self.oSession.GetCurrentNavigationIndex()) \
#                     + '\nCurrentPage (0-based): ' + str( self.oSession.GetCurrentPageIndex()) \
#                     + '\nPageIndex: ' + str(iBookmarkedPageIndex)\
#                     + '\nNavigationIndex: ' + str(iBookmarkedNavigationIndex)
#             self.oUtilsMsgs.DisplayWarning(sMsg)
             
    
    
            try:
                sMsg = ''
    
                self.SaveAndGoToPreviousPageDisplay('GoToBookmark', iBookmarkedNavigationIndex)
    
            except:
                iPage = self.oSession.GetCurrentPageIndex() + 1
                tb = traceback.format_exc()
                sMsg = "onGoToBookmarkButtonClicked: Error moving to bookmarked page. Current page: " + str(iPage) \
                       + "\n\n" + tb 
                self.oUtilsMsgs.DisplayError(sMsg)
            
        
        
        
    

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SaveAndGoToPreviousPageDisplay(self, sCaller, iNewNavigationIndex):
        ''' Function will save current state of questions and images.
            Called when going to Previous page or if the GoToBookmark button is clicked. 
 
            During the 'UpdateCompletions' function, only the completion requirement lists
            (not the completed flags) are updated allowing the user to return 
            to the current page to complete it.
        '''
        
        sSaveMsg = ''
        sInteractionMsg = sCaller
        sCompletedMsg = ''

        iNewPageIndex = self.oIOXml.GetNavigationIndexForPage(self.oSession.GetNavigationList(), iNewNavigationIndex)
        self.oSession.SetInteractionLogOnOff('Off',sCaller)
        
           
        self.DisableButtons()    
        if self.oSession.sViewingMode != 'Default':
            self.onResetViewClicked(sCaller)

        bChangeXmlPageIndex = True

        if self.oSession.GetCurrentNavigationIndex() > 0:
            if self.oSession.GetCurrentPageIndex() == iNewPageIndex:
                bChangeXmlPageIndex = False  
        
        bSuccess, sSaveMsg = self.oSession.PerformSave(sCaller)
        if bSuccess:
            
            bSuccess, sCompletedMsg = self.oSession.UpdateCompletions(sCaller)
            if bSuccess:

                self.oSession.CaptureAndSaveImageState()
    
                ########################################    
                # set up for new display page
                ########################################    
        
                self.oSession.SetCurrentNavigationIndex(iNewNavigationIndex)
                self.progress.setValue(self.oSession.GetCurrentNavigationIndex())
                self.oSession.InitializeImageDisplayOrderIndices(self.oSession.GetCurrentPageIndex())
        
                if self.oSession.GetCurrentNavigationIndex() < 0:
                    # reset to beginning
                    self.oSession.SetCurrentNavigationIndex( 0 )
                
                self.oSession.AdjustToCurrentQuestionSet()
                
                if bChangeXmlPageIndex:
                    slicer.mrmlScene.Clear()
                    self.oSession.SetupPageState(self.oSession.GetCurrentPageIndex())
                    if self.oCustomWidgets.GetButtonScriptRerunRequired(self.oSession.GetCurrentPageIndex()):
                        self.oCustomWidgets.SetPageIncomplete(self.oSession.GetCurrentPageIndex())
        
                self.InitializeTabSettings()
                self.oSession.DisplayQuizLayout()
                self.oSession.DisplayImageLayout()
            
        sInteractionMsg = sInteractionMsg + sSaveMsg + sCompletedMsg

        self.oSession.SetInteractionLogOnOff('On', sInteractionMsg)
        self.EnableButtons()

        


        

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


##########################################################################
#
# class SlicerInterface
#
##########################################################################

class SlicerInterface:
    
    def __init__(self, oFilesIOInput, parent=None):
        self.sClassName = type(self).__name__
        self.parent = parent
#         print('Constructor for SlicerInterface')
        
        self.oFilesIO = oFilesIOInput
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ClearLayout(self, layout):
        # remove widgets from layout - ready for new widgets
        for i in reversed(range(layout.count())):
            widget = layout.takeAt(i).widget()
            if widget != None:
                widget.deleteLater()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CreateLeftLayoutAndWidget(self):
        
        # create a layout for the quiz to go in Slicer's left widget
        self.qLeftLayout = qt.QVBoxLayout()
        
        # add the quiz main layout to Slicer's left widget
        self.qLeftWidget = qt.QWidget()
        self.qLeftWidget.setLayout(self.qLeftLayout)

    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddQuizTitle(self):
        
        qTitleGroupBox = qt.QGroupBox()
        qTitleGroupBoxLayout = qt.QHBoxLayout()
        qTitleGroupBox.setLayout(qTitleGroupBoxLayout)
                                
        qLogoImg = qt.QLabel(self)
        sLogoName = 'BainesChevrons.png'
        sLogoPath = os.path.join(self.oFilesIO.GetScriptedModulesPath(),'Resources','Icons',sLogoName)
        pixmap = qt.QPixmap(sLogoPath)
        qLogoImg.setPixmap(pixmap)
        qLogoImg.setAlignment(QtCore.Qt.AlignCenter)

        qTitle = qt.QLabel('Baines Image Quizzer')
        qTitle.setFont(qt.QFont('Arial',12, qt.QFont.Bold))
        qTitle.setAlignment(QtCore.Qt.AlignCenter)

        qTitleGroupBoxLayout.addWidget(qLogoImg)
        qTitleGroupBoxLayout.addWidget(qTitle)
        
        qTitleGroupBoxLayout.setSpacing(20)
        qTitleGroupBoxLayout.addStretch()
        
        
        return qTitleGroupBox
        
 
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddQuizLayoutWithTabs(self):

        # setup the tab widget
        self.qTabWidget = qt.QTabWidget()
        qTabQuiz = qt.QWidget()
        self.qTabWidget.addTab(qTabQuiz,"Quiz")
        self.qTabWidget.setStyleSheet("QTabBar{ font: bold 9pt}")
        
        
        # Layout within the tab widget - form needs a frame
        self.qQuizLayout = qt.QFormLayout(qTabQuiz)
        quizFrame = qt.QFrame(qTabQuiz)
        quizFrame.setLayout(qt.QVBoxLayout())
        self.qQuizLayout.addWidget(quizFrame)
    
        # add to left layout
        self.qLeftLayout.addWidget(self.qTabWidget)








    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>



##########################################################################
#
# class SlicerWindowSize
#
##########################################################################
 
class SlicerWindowSize:
     
    def __init__(self, parent=None):
        self.slMainWindowPos = None
        self.slMainWindowWidth = 0
        self.slMainWindowHeight = 0
         
        self.CaptureWindowSize()
         
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CaptureWindowSize(self):
        slMainWindow = slicer.util.mainWindow()
        self.slMainWindowPos = slMainWindow.pos
        self.slMainWindowWidth = slMainWindow.geometry.width()
        self.slMainWindowHeight = slMainWindow.geometry.height()
