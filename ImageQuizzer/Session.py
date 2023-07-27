import PythonQt
import os
import vtk, qt, ctk, slicer
import sys
import unittest
import random
import traceback
from copy import deepcopy

from Utilities.UtilsIOXml import *
from Utilities.UtilsMsgs import *
from Utilities.UtilsFilesIO import *
from Utilities.UtilsEmail import *

from Question import *
from ImageView import *
from PageState import *
#from ImageQuizzer import *

import EditorLib
from EditorLib import EditUtil

from PythonQt import QtCore, QtGui

from slicer.util import EXIT_SUCCESS
from datetime import datetime


##########################################################################
#
# class Session
#
##########################################################################

class Session:
    
    def __init__(self,  parent=None):
        self.sClassName = type(self).__name__
        self.parent = parent
        
        self._sLoginTime = ''

        self._iCurrentNavigationIndex = 0
        self._l4iNavigationIndices = []

        self._xPageNode = None
        self.sPageID = ''
        self.sPageDescriptor = ''
        
        self._loQuestionSets = []
        self._lsPreviousResponses = []
        self._lsNewResponses = []
        
        
        self._bFirstResponsesRecordedInXml = False
        self._bQuizComplete = False
        self._bQuizResuming = False
        self._bAllowMultipleResponse = False
        self._bRequestToEnableSegmentEditor = False
        self._bSegmentationModule = False
        self._iSegmentationTabIndex = -1   # default
        self._bPageLooping = False
        self._sSessionContourVisibility = 'Outline'
        self._sSessionContourOpacity = 1.0
        self._bEmailResults = False
        self._bRandomizeRequired = False
        
        self.oFilesIO = None
        self.oIOXml = UtilsIOXml()
        self.oUtilsMsgs = UtilsMsgs()
        self.oPageState = PageState()
        self.oUtilsEmail = UtilsEmail()

        self.oImageView = None
        
        self._btnNext = None
        self._btnPrevious = None
        
        self.bNPlanesViewingMode = False
        self.sViewingMode = "Default"
        self.loCurrentXMLImageViewNodes = []
        self.liImageDisplayOrder = []

        self.setupTestEnvironment()

    #----------
    def __del__(self):

        # clean up of editor observers and nodes that may cause memory leaks (color table?)
        if self.GetSegmentationTabIndex() > 0:
            slicer.modules.quizzereditor.widgetRepresentation().self().exit()

    #----------
    def setupTestEnvironment(self):
        # check if function is being called from unit testing
        if "testing" in os.environ:
            self.sTestMode = os.environ.get("testing")
        else:
            self.sTestMode = "0"
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #-------------------------------------------
    #        Getters / Setters
    #-------------------------------------------
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #----------
    def SetFilesIO(self, oFilesIO):
        self.oFilesIO = oFilesIO

    #----------
    def SetIOXml(self, oIOXml):
        self.oIOXml = oIOXml

    #----------
    def SetQuizComplete(self, bInput):
        self._bQuizComplete = bInput
        
    #----------
    def GetQuizComplete(self):
        return self._bQuizComplete
            
    #----------
    def SetQuizResuming(self, bInput):
        self._bQuizResuming = bInput
        
    #----------
    def GetQuizResuming(self):
        return self._bQuizResuming
            
    #----------
    def SetLoginTime(self, sTime):
        self._sLoginTime = sTime
        
    #----------
    def LoginTime(self):
        return self._sLoginTime
    
    #----------
    def SetEmailResultsRequest(self, bInput):
        self._bEmailResults = bInput
        
    #----------
    def GetEmailResultsRequest(self):
        return self._bEmailResults
    #----------
    def SetPreviousResponses(self, lInputResponses):
        self._lsPreviousResponses = lInputResponses
        
    #----------
    def GetPreviousResponses(self):
        return self._lsPreviousResponses
    
    #----------
    def GetNavigationList(self):
        return self._l4iNavigationIndices

    #----------
    def SetNavigationList(self, lIndices):
        self._l4iNavigationIndices = lIndices
        
    #----------
    def ClearNavigationList(self):
        self._l4iNavigationIndices = []
    #----------
    def GetCurrentNavigationIndex(self):
        return self._iCurrentNavigationIndex
    
    #----------
    def SetCurrentNavigationIndex(self, iInd):
        self._iCurrentNavigationIndex = iInd
        
    #----------
    def GetNavigationPage(self, iNavInd):
        return self._l4iNavigationIndices[iNavInd][0]
    
    #----------
    def GetNavigationQuestionSet(self, iNavInd):
        return self._l4iNavigationIndices[iNavInd][1]
    
    #----------
    def GetNavigationPageGroup(self, iNavInd):
        return self._l4iNavigationIndices[iNavInd][2]
    
    #----------
    def GetNavigationRepNum(self, iNavInd):
        return self._l4iNavigationIndices[iNavInd][3]
    #----------
    #----------
    def GetNavigationIndicesAtIndex(self, iNavInd):
        return self._l4iNavigationIndices[iNavInd]
    
    #----------
    def NavigationListAppend(self, lNavIndices):
        self._l4iNavigationIndices.append(lNavIndices)
    
    #----------
    def NavigationListInsertBeforeIndex(self, iNavInd, lNavIndices):
        self._l4iNavigationIndices.insert(iNavInd, lNavIndices)
        
    #----------
    #----------
    def SetMultipleResponseAllowed(self, sYN):
        
        if sYN == 'y' or sYN == 'Y':
            self._bAllowMultipleResponse = True
        else: # default
            self._bAllowMultipleResponse = False

    #----------
    def GetMultipleResponseAllowed(self):
        return self._bAllowMultipleResponse
            
    #----------
    def SetRequestToEnableSegmentEditorTF(self, sYN):
        if sYN == 'y' or sYN == 'Y':
            self._bRequestToEnableSegmentEditor = True
        else:
            self._bRequestToEnableSegmentEditor = False
        
    #----------
    def GetRequestToEnableSegmentEditorTF(self):
        return self._bRequestToEnableSegmentEditor
    
    #----------
    def GetPageCompleteAttribute(self, iNavigationIndex):
        iPageIndex = self.GetNavigationPage(iNavigationIndex)
        xPageNode = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', iPageIndex)

        sPageComplete = self.oIOXml.GetValueOfNodeAttribute(xPageNode,'PageComplete')
        
        return sPageComplete
        
    #----------
    def SetupPageState(self, iPgIndex):
        ''' Initialize a new page state object for the page.
            XML specifics for the input page index are used for initializing.
        '''
        xPageNode = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', iPgIndex)
        self.oPageState.InitializeStates(self, xPageNode)
    
    #----------
    def AddExtraToolsTab(self):

        # add extra tools tab to quiz widget
        self.tabExtraTools = qt.QWidget()
        self.oQuizWidgets.qTabWidget.addTab(self.tabExtraTools,"Extra Tools")
        self._iExtraToolsTabIndex = self.oQuizWidgets.qTabWidget.count - 1
        self.oQuizWidgets.qTabWidget.setTabEnabled(self._iExtraToolsTabIndex, True)
        
        widget = self.SetupExtraToolsButtons()
        self.tabExtraTools.setLayout(widget)


    #----------
    def AddSegmentationModule(self, bTF):

        if bTF == True:
            # add segment editor tab to quiz widget
            self.oQuizWidgets.qTabWidget.addTab(slicer.modules.quizzereditor.widgetRepresentation(),"Segment Editor")
            self._bSegmentationModule = True
            self._iSegmentationTabIndex = self.oQuizWidgets.qTabWidget.count - 1
            self.oQuizWidgets.qTabWidget.setTabEnabled(self._iSegmentationTabIndex, True)
            
        else:
            self._bSegmentationModule = False
        
    #----------
    def SegmentationTabEnabler(self, bTF):

        self.oQuizWidgets.qTabWidget.setTabEnabled(self.GetSegmentationTabIndex(), bTF)
        
    #----------
    def GetSegmentationTabIndex(self):
        return self._iSegmentationTabIndex
        
    #----------
    def GetSegmentationTabEnabled(self):
        bTF = self.oQuizWidgets.qTabWidget.isTabEnabled(self.GetSegmentationTabIndex())
        return bTF
    
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
    def GetAllQuestionSetsForNthPage(self, iPageIndex):
        self._xPageNode = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', iPageIndex)
        xNodesAllQuestionSets = self.oIOXml.GetChildren(self._xPageNode, 'QuestionSet')
        
        return xNodesAllQuestionSets

    #----------
    def GetAllQuestionSetNodesForCurrentPage(self):
        xPageNode = self.GetCurrentPageNode()
        xAllQuestionSetNodes = self.oIOXml.GetChildren(xPageNode, 'QuestionSet')
        
        return xAllQuestionSetNodes
    #----------
    def GetNthQuestionSetForCurrentPage(self, idx):
        xPageNode = self.GetCurrentPageNode()
        xQuestionSetNode = self.oIOXml.GetNthChild(xPageNode, 'QuestionSet', idx)
        
        return xQuestionSetNode
        
    #----------
    def GetCurrentPageNode(self):
        ''' From the current navigation index in the composite indices list, get the page index.
            Return the nth page node (using the page index) from the root.
        '''
        iPageIndex = self.GetNavigationPage(self.GetCurrentNavigationIndex())
        xPageNode = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', iPageIndex)
        
        return xPageNode
    
    #----------
    def GetCurrentPageIndex(self):
        return self.GetNavigationPage(self.GetCurrentNavigationIndex())
    
    #----------
    def GetCurrentQuestionSetIndex(self):
        return self.GetNavigationQuestionSet(self.GetCurrentNavigationIndex())
    
    #----------
    def GetCurrentQuestionSetNode(self):
        iQSetIndex = self.GetNavigationQuestionSet(self.GetCurrentNavigationIndex())
        xPageNode = self.GetCurrentPageNode()
        xQuestionSetNode = self.oIOXml.GetNthChild(xPageNode, 'QuestionSet', iQSetIndex)
        
        return xQuestionSetNode
    
 
    #----------
    def GetAllQuestionsForCurrentQuestionSet(self):
        xCurrentQuestionSetNode = self.GetCurrentQuestionSetNode()
        xAllQuestionNodes = self.oIOXml.GetChildren(xCurrentQuestionSetNode, 'Question')
        
        return xAllQuestionNodes
    
    #----------
    def GetNthOptionNode(self, indQuestion, indOption):

        xQuestionSetNode = self.GetCurrentQuestionSetNode()
        xQuestionNode = self.oIOXml.GetNthChild(xQuestionSetNode, 'Question', indQuestion)
        xOptionNode = self.oIOXml.GetNthChild(xQuestionNode, 'Option', indOption)
        
        return xOptionNode
        
    #----------
    def GetAllOptionNodes(self, indQuestion):

        xQuestionSetNode = self.GetCurrentQuestionSetNode()
        xQuestionNode = self.oIOXml.GetNthChild(xQuestionSetNode, 'Question', indQuestion)
        xAllOptionNodes = self.oIOXml.GetChildren(xQuestionNode,'Option')
        
        return xAllOptionNodes
        
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
        iXmlIndex = 0
        oImageViewNode = None
        bFoundFirstNameMatch = False
        bFoundOrientationMatch = False
        
        # determine which image is to be displayed in an alternate viewing mode (3 Planes or 1 Plane)
        loImageViewNodes = self.oImageView.GetImageViewList()
        for oImageViewNode in loImageViewNodes:
            if oImageViewNode.sNodeName == sImageName:
                if not bFoundFirstNameMatch:
                    bFoundFirstNameMatch = True
                    iXmlFirstNameMatch = iXmlIndex
                    oImageViewNodeFirstNameMatch = oImageViewNode
                if sSelectedOrientation == 'All':
                    break
                else:
                    if sSelectedOrientation == oImageViewNode.sOrientation:
                        bFoundOrientationMatch = True
                        break
                    else:
                        iXmlIndex = iXmlIndex + 1

            
            else:
                iXmlIndex = iXmlIndex + 1
        
        # There may not have been an xml element with the selected orientation view
        #    Reset to the first name match
        if not bFoundOrientationMatch:
            iXmlIndex = iXmlFirstNameMatch
            oImageViewNode = oImageViewNodeFirstNameMatch
            
        return oImageViewNode, iXmlIndex
        
    #----------
    def GetNPlanesComboBoxCount(self):
        return self.qComboImageList.count
    
    #----------
    def SetNPlanesView(self):
        
        self.sViewingMode = self.qComboNPlanesList.currentText
        
        if self.sViewingMode == "3 Planes":
            self.llsNPlanesOrientDest = [["Axial","Red"],["Coronal","Green"],["Sagittal","Yellow"]]
        elif self.sViewingMode == "1 Plane Axial":
            self.llsNPlanesOrientDest = [["Axial","Red"]]
        elif self.sViewingMode == "1 Plane Sagittal":
            self.llsNPlanesOrientDest = [["Sagittal","Red"]]
        elif self.sViewingMode == "1 Plane Coronal":
            self.llsNPlanesOrientDest = [["Coronal","Red"]]
            
        # add widget to contour visibility list
        self.lsLayoutWidgets = []
        self.lsLayoutWidgets.append('Red')
        
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
    def GetPageLooping(self):
        return self._bPageLooping

    #----------
    def SetPageLooping(self, bTF):
        self._bPageLooping = bTF

    #----------
    def ReorderImageIndexToEnd(self, iIndexToMove):
        ''' Move index to end of list to prioritize the image state of
            the last viewed image in the 1 or 3 Planes view mode.
            This is used in the apply image state function.
            (It prevents the state being overridden because of the order of images read in from the xml file.)
        '''

        liRearrangedOrder = []
        
        for i in range(len(self.liImageDisplayOrder)):
            if self.liImageDisplayOrder[i] != iIndexToMove:
                liRearrangedOrder.append(self.liImageDisplayOrder[i])
                
        liRearrangedOrder.append(iIndexToMove)
        
        return liRearrangedOrder
                
    #----------
    def InitializeImageDisplayOrderIndices(self):
        ''' default to the original order for Images to be displayed based on image elements
            stored in the XML file
        '''
        self.liImageDisplayOrder = []
        lxImageElements = self.oIOXml.GetChildren(self.GetCurrentPageNode(), 'Image')
        for i in range(len(lxImageElements)):
            self.liImageDisplayOrder.append(i)
            
    #----------
    def GetImageDisplayOrderIndices(self):
        return self.liImageDisplayOrder
    
    #----------
    #----------   Contours outline/fill and opacity
    #----------
    def GetSessionContourVisibilityDefault(self):
        return self._sSessionContourVisibility
    
    #----------
    def SetSessionContourVisibilityDefault(self, xRootNode):
        # quiz validation checked for valid values
        # if no attribute exists, set with the default
        self._sSessionContourVisibility = self.oIOXml.GetValueOfNodeAttribute(xRootNode, 'ContourVisibility')
        if self._sSessionContourVisibility == '':
            self._sSessionContourVisibility = 'Outline'  # default
            
        self.SetContourVisibilityCheckBox(self._sSessionContourVisibility)
        
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
        
        #
        # if self.qVisibilityOpacity.maximum > self.qVisibilityOpacity.minimum:
        #     fOpacity = self.GetSessionContourOpacityDefault()
            
        iSliderValue = int(fOpacity * (self.qVisibilityOpacity.maximum - self.qVisibilityOpacity.minimum))    
        self.qVisibilityOpacity.setValue(iSliderValue)

    #----------
    def ResetContourVisibilityToSessionDefault(self):
        # reset widgets and the imageView property to the session default of contour visibility 
        
        self.SetContourVisibilityCheckBox(self.GetSessionContourVisibilityDefault())    # tool widget Fill/Outline
        self.SetSliderToolFromContourOpacity(self.GetSessionContourOpacityDefault())    # tool widget Opacity
        self.SetContourOpacityFromSliderValue(self.qVisibilityOpacity.value)            # image view property

    #----------
    def SetRandomizeRequired(self, sYN=None):
        # set randomize required to input value (from unit tests) or from the stored xml attribute
        if sYN == None:
            sYN = self.oIOXml.GetValueOfNodeAttribute(self.oIOXml.GetRootNode(),'RandomizePageGroups')
        if sYN == 'Y':
            self._bRandomizeRequired = True
        else:
            self._bRandomizeRequired = False
            
    #----------
    def GetRandomizeRequired(self):
        return self._bRandomizeRequired

    #----------
    #----------
    #----------

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #-------------------------------------------
    #        GUI Setup
    #-------------------------------------------
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetupWidgets(self, slicerMainLayout):

        self.oQuizWidgets = QuizWidgets(self.oFilesIO)
        self.oQuizWidgets.CreateLeftLayoutAndWidget()

        self.SetupButtons()
        self.oQuizWidgets.qLeftLayout.addWidget(self.qButtonGrpBox)

        self.oQuizWidgets.AddQuizLayoutWithTabs()
        self.oQuizWidgets.qTabWidget.currentChanged.connect(self.onTabChanged)
       
        slicerMainLayout.addWidget(self.oQuizWidgets.qLeftWidget)  

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetupButtons(self):
        
        qProgressLabel = qt.QLabel('Progress ')
        self.progress = QtGui.QProgressBar()
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
        self._btnNext.connect('clicked(bool)',self.onNextButtonClicked)
        
        # Back button
        self._btnPrevious = qt.QPushButton("Previous")
        self._btnPrevious.toolTip = "Display previous set of questions."
        self._btnPrevious.enabled = True
        self._btnPrevious.setStyleSheet("QPushButton{ background-color: rgb(255,149,0); color: black }")
        self._btnPrevious.connect('clicked(bool)',self.onPreviousButtonClicked)


        # Exit button
        self._btnExit = qt.QPushButton("Exit")
        self._btnExit.toolTip = "Save quiz and exit Slicer."
        self._btnExit.enabled = True
        self._btnExit.setStyleSheet("QPushButton{ background-color: rgb(255,0,0); color: black; font-weight: bold }")
        # use lambda to pass argument to this PyQt slot without invoking the function on setup
        self._btnExit.connect('clicked(bool)',lambda: self.onExitButtonClicked('ExitBtn'))

        # Repeat button
        self._btnRepeat = qt.QPushButton("Repeat")
        self._btnRepeat.toolTip = "Save current responses and repeat."
        self._btnRepeat.enabled = False
        self._btnRepeat.visible = False
        self._btnRepeat.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: black}")
        self._btnRepeat.connect('clicked(bool)', self.onRepeatButtonClicked)
        

        self.qButtonGrpBoxLayout.addWidget(self._btnExit)
        self.qButtonGrpBoxLayout.addWidget(qProgressLabel)
        self.qButtonGrpBoxLayout.addWidget(self.progress)
        self.qButtonGrpBoxLayout.addWidget(self._btnPrevious)
        self.qButtonGrpBoxLayout.addWidget(self._btnNext)
        self.qButtonGrpBoxLayout.addWidget(self._btnRepeat)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetupExtraToolsButtons(self):
        
        # create buttons

        self.tabExtraToolsLayout = qt.QVBoxLayout()

        

        # >>>>>>>>>>>>>>>>>>>>
        # Window/Level interactive mode
        self.qDisplayMgrGrpBox = qt.QGroupBox()
        self.qDisplayMgrGrpBox.setTitle("Interactive Mode")
        self.qDisplayMgrGrpBox.setStyleSheet("QGroupBox{ font-size: 11px; font-weight: bold}")
        self.qDisplayMgrGrpBoxLayout = qt.QHBoxLayout()
        self.qDisplayMgrGrpBox.setLayout(self.qDisplayMgrGrpBoxLayout)
        
        qWindowLevelLabel = qt.QLabel("Window/Level: ")
        self.qDisplayMgrGrpBoxLayout.addWidget(qWindowLevelLabel)
        
        self.btnWindowLevelOn = qt.QPushButton('On')
        self.btnWindowLevelOn.enabled = True
        self.btnWindowLevelOn.setStyleSheet("QPushButton{ background-color: rgb(0,179,246); color: black }")
        self.btnWindowLevelOn.connect('clicked(bool)',self.onWindowLevelOnClicked)
        self.qDisplayMgrGrpBoxLayout.addWidget(self.btnWindowLevelOn)


        self.btnWindowLevelOff = qt.QPushButton('Default Cursor')
        self.btnWindowLevelOff.enabled = True
        self.btnWindowLevelOff.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: black }")
        self.btnWindowLevelOff.connect('clicked(bool)',self.onWindowLevelOffClicked)
        self.qDisplayMgrGrpBoxLayout.addWidget(self.btnWindowLevelOff)
        
        self.tabExtraToolsLayout.addWidget(self.qDisplayMgrGrpBox)
        
        # >>>>>>>>>>>>>>>>>>>>
        # Crosshairs
        self.qCrossHairsGrpBox = qt.QGroupBox()
        self.qCrossHairsGrpBox.setTitle('Crosshairs')
        self.qCrossHairsGrpBox.setStyleSheet("QGroupBox{ font-size: 11px; font-weight: bold}")
        self.qCrossHairsGrpBoxLayout = qt.QHBoxLayout()
        self.qCrossHairsGrpBox.setLayout(self.qCrossHairsGrpBoxLayout)
        
        qCrosshairsLabel = qt.QLabel("Use Shift key to display: ")
        self.qCrossHairsGrpBoxLayout.addWidget(qCrosshairsLabel)
        
        self.btnCrosshairsOn = qt.QPushButton('On')
        self.btnCrosshairsOn.enabled = True
        self.btnCrosshairsOn.setStyleSheet("QPushButton{ background-color: rgb(0,179,246); color: black }")
        self.btnCrosshairsOn.connect('clicked(bool)',self.onCrosshairsOnClicked)
        self.qCrossHairsGrpBoxLayout.addWidget(self.btnCrosshairsOn)


        self.btnCrosshairsOff = qt.QPushButton('Off')
        self.btnCrosshairsOff.enabled = True
        self.btnCrosshairsOff.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: black }")
        self.btnCrosshairsOff.connect('clicked(bool)',self.onCrosshairsOffClicked)
        self.qCrossHairsGrpBoxLayout.addWidget(self.btnCrosshairsOff)

        self.chkSliceIntersections = qt.QCheckBox('Slice Intersections')
        self.chkSliceIntersections.stateChanged.connect(self.SliceIntersectionsStateChange)
        self.qCrossHairsGrpBoxLayout.addWidget(self.chkSliceIntersections)

        self.tabExtraToolsLayout.addWidget(self.qCrossHairsGrpBox)

        
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
        self.btnNPlanesView.connect('clicked(bool)', self.onNPlanesViewClicked)
        self.qDisplayOptionsGrpBoxLayout.addWidget(self.btnNPlanesView,0,2)

        
        self.btnResetView = qt.QPushButton('Reset to default')
        self.btnResetView.enabled = True
        self.btnResetView.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: black }")
        self.btnResetView.connect('clicked(bool)', self.onResetViewClicked)
        self.qDisplayOptionsGrpBoxLayout.addWidget(self.btnResetView,1,2)

        self.tabExtraToolsLayout.addWidget(self.qDisplayOptionsGrpBox)
        

        # >>>>>>>>>>>>>>>>>>>>
        # Ruler tools
        self.qLineToolsGrpBox = qt.QGroupBox()
        self.qLineToolsGrpBox.setTitle('Line Measurement')
        self.qLineToolsGrpBox.setStyleSheet("QGroupBox{ font-size: 11px; font-weight: bold}")
        self.qLineToolsGrpBoxLayout = qt.QHBoxLayout()
        self.qLineToolsGrpBox.setLayout(self.qLineToolsGrpBoxLayout)

        qLineToolLabel = qt.QLabel('Ruler:')
        self.qLineToolsGrpBoxLayout.addWidget(qLineToolLabel)
        self.qLineToolsGrpBoxLayout.addSpacing(10)
        
        self.btnAddMarkupsLine = qt.QPushButton("Add new line")
        self.btnAddMarkupsLine.enabled = True
        self.btnAddMarkupsLine.setStyleSheet("QPushButton{ background-color: rgb(0,179,246); color: black }")
        self.btnAddMarkupsLine.connect('clicked(bool)', self.onAddLinesButtonClicked)
        self.qLineToolsGrpBoxLayout.addWidget(self.btnAddMarkupsLine)
        self.qLineToolsGrpBoxLayout.addSpacing(10)
        
        # remove the last point of markup line created
        qLineToolLabelTrashPt = qt.QLabel('Remove last point:')
        self.qLineToolsGrpBoxLayout.addWidget(qLineToolLabelTrashPt)
 
        self.slMarkupsLineWidget = slicer.qSlicerMarkupsPlaceWidget()
        # Hide all buttons and only show delete button
        self.slMarkupsLineWidget.buttonsVisible=False
        self.slMarkupsLineWidget.deleteButton().show()
        self.qLineToolsGrpBoxLayout.addWidget(self.slMarkupsLineWidget)
        self.qLineToolsGrpBoxLayout.addSpacing(10)
        
        # Clear all markup lines
        self.btnClearLines = qt.QPushButton("Clear all")
        self.btnClearLines.toolTip = "Remove all markup lines."
        self.btnClearLines.enabled = True
        self.btnClearLines.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: black }")
        self.btnClearLines.connect('clicked(bool)',self.onClearLinesButtonClicked)
        self.qLineToolsGrpBoxLayout.addWidget(self.btnClearLines)

        self.tabExtraToolsLayout.addWidget(self.qLineToolsGrpBox)

        # >>>>>>>>>>>>>>>>>>>>
        # Contour visibility tools
        self.qContourVisibilityGrpBox = qt.QGroupBox()
        self.qContourVisibilityGrpBox.setTitle('Contour Visibility - Fill/Outline and Opacity')
        self.qContourVisibilityGrpBox.setStyleSheet("QGroupBox{ font-size: 11px; font-weight: bold}")
        self.qContourVisibilityGrpBoxLayout = qt.QHBoxLayout()
        self.qContourVisibilityGrpBox.setLayout(self.qContourVisibilityGrpBoxLayout)

        self.qChkBoxFillOrOutline = qt.QCheckBox('Fill')
        self.qChkBoxFillOrOutline.stateChanged.connect(self.onContourDisplayStateChanged)
        self.qContourVisibilityGrpBoxLayout.addWidget(self.qChkBoxFillOrOutline)
        self.qContourVisibilityGrpBoxLayout.addSpacing(30)

        self.qVisibilityOpacity = qt.QSlider(QtCore.Qt.Horizontal)
        self.qVisibilityOpacity.setMinimum(0)
        self.qVisibilityOpacity.setMaximum(100)
        self.qVisibilityOpacity.setValue(50)
        self.qVisibilityOpacity.setPageStep(1)
        self.qVisibilityOpacity.connect("valueChanged(int)", self.SetContourOpacityFromSliderValue)
        self.qContourVisibilityGrpBoxLayout.addWidget(self.qVisibilityOpacity)
        self.qContourVisibilityGrpBoxLayout.addSpacing(30)

        qLabelOpacity = qt.QLabel('Opacity')
        qLabelOpacity.setMinimumWidth(200)
        self.qContourVisibilityGrpBoxLayout.addWidget(qLabelOpacity)
        

        self.tabExtraToolsLayout.addWidget(self.qContourVisibilityGrpBox)
        
        # >>>>>>>>>>>>>>>>>>>>
        # >>>>>>>>>>>>>>>>>>>>
        # >>>>>>>>>>>>>>>>>>>>
        self.tabExtraToolsLayout.addStretch()
        

        return self.tabExtraToolsLayout
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def EnableButtons(self):
        
        xPageNode = self.GetCurrentPageNode()
        if self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'Loop') == "Y":
            self.SetPageLooping(True)
            self._btnRepeat.visible = True
            self._btnRepeat.enabled = False
            self._btnRepeat.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: white}")
            # only enable Repeat button in looping if the page is not complete and the user is on the last question set
            # if self.GetPageCompleteAttribute(self.GetCurrentNavigationIndex()) != "Y":
            #     if self.CheckForLastQuestionSetForPage() == True:
            #         self._btnRepeat.enabled = True
            #         self._btnRepeat.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: black}")
            # else:
            #     # page is complete - enable if multiple responses are allowed
            #     if self.GetMultipleResponseAllowed() == True:
            #         self._btnRepeat.enabled = True
            #         self._btnRepeat.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: black}")
                    
            if self.CheckForLastQuestionSetForPage() == True:
                self._btnRepeat.enabled = True
                self._btnRepeat.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: black}")

        else:
            self.SetPageLooping(False)
            self._btnRepeat.visible = False
            self._btnRepeat.enabled = False
            self._btnRepeat.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: white}")
            
            
        # assign button description           
        if (self.GetCurrentNavigationIndex() == len(self.GetNavigationList()) - 1):
            self._btnNext.setText("Finish")
        else:
            self._btnNext.setText("Next")
        
        # beginning of quiz
        if (self.GetCurrentNavigationIndex() == 0):
            self._btnNext.enabled = True
            self._btnPrevious.enabled = False

        # end of quiz
        elif (self.GetCurrentNavigationIndex() == len(self.GetNavigationList()) - 1):
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



    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #-------------------------------------------
    #        GUI Events
    #-------------------------------------------
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onTabChanged(self):
        ''' When changing tabs reset segment editor interface
            to force user to reset the volume to be contoured.
        '''
        self.SetSegmentationTabDefaults()
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onNextButtonClicked(self):

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
        
        try:        
            bSaveComplete = True
            sMsg = ''
            
            self.DisableButtons()    
            if self.sViewingMode != 'Default':
                self.onResetViewClicked()
    
            if self.GetCurrentNavigationIndex() + 1 == len(self.GetNavigationList()):
    
                # the last question was answered - check if user is ready to exit
                self.onExitButtonClicked('Finish') # a save is done in here
                
                # the user may have cancelled the 'finish'
                # bypass remainder of the 'next' button code
    
            else:
                # this is not the last question set, do a save and display the next page
                bNewPage = True
                if self.GetNavigationPage(self.GetCurrentNavigationIndex()) == self.GetNavigationPage(self.GetCurrentNavigationIndex() + 1):
                    bNewPage = False
                bSaveComplete, sMsg = self.PerformSave('NextBtn')
                
                if bSaveComplete:
        
        
                    ########################################    
                    # set up for next page
                    ########################################    
                    
                    # if last question set, clear list and scene
                    if self.CheckForLastQuestionSetForPage() == True:
                        self._loQuestionSets = []
                        slicer.mrmlScene.Clear()
                    else:
                        # clear quiz widgets only
                        for i in reversed(range(self.oQuizWidgets.qQuizLayout.count())):
                            self.oQuizWidgets.qQuizLayout.itemAt(i).widget().setParent(None)
                
                    self.SetCurrentNavigationIndex(self.GetCurrentNavigationIndex() + 1 )
                    self.progress.setValue(self.GetCurrentNavigationIndex())
                    self.InitializeImageDisplayOrderIndices()
                    
                    if bNewPage:
                        self.SetupPageState(self.GetCurrentPageIndex())
                    self.DisplayQuizLayout()
                    self.DisplayImageLayout()
                            
                else:
                    if sMsg != '':
                        self.oUtilsMsgs.DisplayWarning( sMsg )

            self.EnableButtons()
                
        except:
            iPage = self.GetCurrentPageIndex() + 1
            tb = traceback.format_exc()
            sMsg = "onNextButtonClicked: Error moving to next page. Current page: " + str(iPage) \
                   + "\n\n" + tb 
            self.oUtilsMsgs.DisplayError(sMsg)
                
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onPreviousButtonClicked(self):
        
        try:
            bSaveComplete = True
            sMsg = ''

            self.DisableButtons()    
            if self.sViewingMode != 'Default':
                self.onResetViewClicked()
                
            bNewPage = True
            if self.GetCurrentNavigationIndex() > 0:
                if self.GetNavigationPage(self.GetCurrentNavigationIndex()) == self.GetNavigationPage(self.GetCurrentNavigationIndex() - 1):
                    bNewPage = False
    
            bSaveComplete, sMsg = self.PerformSave('PreviousBtn')
            
            if bSaveComplete:
    
                ########################################    
                # set up for previous page
                ########################################    
    
                slicer.mrmlScene.Clear()
                self.SetCurrentNavigationIndex(self.GetCurrentNavigationIndex() - 1)
                self.progress.setValue(self.GetCurrentNavigationIndex())
                self.InitializeImageDisplayOrderIndices()
        
                if self.GetCurrentNavigationIndex() < 0:
                    # reset to beginning
                    self.SetCurrentNavigationIndex( 0 )
                
                self.AdjustToCurrentQuestionSet()
                
                if bNewPage:
                    self.SetupPageState(self.GetCurrentPageIndex())
                self.DisplayQuizLayout()
                self.DisplayImageLayout()
                   
            
            else:
                if sMsg != '':
                    self.oUtilsMsgs.DisplayWarning( sMsg )

            self.EnableButtons()


        except:
            iPage = self.GetCurrentPageIndex() + 1
            tb = traceback.format_exc()
            sMsg = "onPreviousButtonClicked: Error moving to previous page. Current page: " + str(iPage) \
                   + "\n\n" + tb 
            self.oUtilsMsgs.DisplayError(sMsg)
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onExitButtonClicked(self,sCaller):

        try:
            self.progress.setValue(self.GetCurrentNavigationIndex() + 1)
            if len(self.GetNavigationList()) >0:
                iProgressPercent = int((self.GetCurrentNavigationIndex() + 1) / len(self.GetNavigationList()) * 100)
            else:
                # error in creating the composite navigation index - assign percent to 100 for exiting
                self.oUtilsMsgs.DisplayError('ERROR creating quiz indices - Exiting')
            self.progress.setFormat(self.sPageID + '  ' + self.sPageDescriptor + '    ' + str(iProgressPercent) + '%')
            
            sMsg = 'Do you wish to exit?'
            if sCaller == 'ExitBtn':
                sMsg = sMsg + ' \nYour responses will be saved. Quiz may be resumed.'
            else:
                if sCaller == 'Finish':
                    sMsg = sMsg + " \nYour quiz is complete and your responses will be locked." \
                                + " \n\nIf you wish to resume at a later time, press 'Cancel' here, then use the 'Exit' button."
    
            qtAns = self.oUtilsMsgs.DisplayOkCancel(sMsg)
            if qtAns == qt.QMessageBox.Ok:
                bSaveComplete, sMsg = self.PerformSave(sCaller)
                if bSaveComplete:
                    
                    self.QueryThenSendEmailResults()
                            
                    # update shutdown batch file to remove SlicerDICOMDatabase
                    self.oFilesIO.CreateShutdownBatchFile()
            
                    slicer.util.exit(status=EXIT_SUCCESS)
                else:
                    if sMsg != '':
                        self.oUtilsMsgs.DisplayWarning( sMsg )
                    self.EnableButtons()
    
            # if code reaches here, either the exit was cancelled or there was 
            # an error in the save
            self.progress.setValue(self.GetCurrentNavigationIndex())
            iProgressPercent = int(self.GetCurrentNavigationIndex() / len(self.GetNavigationList()) * 100)
            self.progress.setFormat(self.sPageID + '  ' + self.sPageDescriptor + '    ' + str(iProgressPercent) + '%')
    
        except:
            iPage = self.GetCurrentPageIndex() + 1
            tb = traceback.format_exc()
            sMsg = "onExitButtonClicked: Error exiting quiz. Current page: " + str(iPage) \
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
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onClearLinesButtonClicked(self):
        ''' A function to clear all markup line nodes from the scene.
        '''
        sMsg = ''
        xPageNode = self.GetCurrentPageNode()
        sPageComplete = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'PageComplete')
        if sPageComplete == "Y":
            sMsg = '\nThis page has already been completed. You cannot remove the markup lines.'
            self.oUtilsMsgs.DisplayWarning(sMsg)
        else:            
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
                    os.remove(sAbsolutePath)
            
                self.oIOXml.RemoveAllElements(xImage, 'MarkupLinePath')
            self.oIOXml.SaveXml(self.oFilesIO.GetUserQuizResultsPath())

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onCrosshairsOnClicked(self):
        ''' activate the crosshairs tool
        '''
        slCrosshairNode = slicer.mrmlScene.GetNodeByID('vtkMRMLCrosshairNodedefault')
        slCrosshairNode.SetCrosshairBehavior(1) # offset jump slice
        slCrosshairNode.SetCrosshairMode(2)     # basic intersection
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onCrosshairsOffClicked(self):
        ''' activate the crosshairs tool
        '''
        slCrosshairNode = slicer.mrmlScene.GetNodeByID('vtkMRMLCrosshairNodedefault')
        slCrosshairNode.SetCrosshairBehavior(1) # offset jump slice
        slCrosshairNode.SetCrosshairMode(0)     # basic intersection
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SliceIntersectionsStateChange(self, int):
        viewNodeRed = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceCompositeNodeRed')
        viewNodeGreen = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceCompositeNodeGreen')
        viewNodeYellow = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceCompositeNodeYellow')
        
        if self.chkSliceIntersections.isChecked():
            viewNodeRed.SetSliceIntersectionVisibility(1)
            viewNodeGreen.SetSliceIntersectionVisibility(1)
            viewNodeYellow.SetSliceIntersectionVisibility(1)
        else:
            viewNodeRed.SetSliceIntersectionVisibility(0)
            viewNodeGreen.SetSliceIntersectionVisibility(0)
            viewNodeYellow.SetSliceIntersectionVisibility(0)

        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onResetViewClicked(self):
        ''' Capture responses in the current state (may not be completed) before 
            resetting the viewing nodes to original layout for this page.
            Restore the current responses.
        '''
        
        lsCurrentResponses = []

        try:
            sCaptureSuccessLevel, lsCurrentResponses, sMsg = self.CaptureNewResponses()
            self.CaptureAndSaveImageState()
            
            sFillOrOutline, iOpacitySliderValue, fOpacity = self.GetContourDisplayState()
            self.AdjustToCurrentQuestionSet()
            self.bNPlanesViewingMode = False
            self.sViewingMode = "Default"
            self.loCurrentXMLImageViewNodes = []
            self.DisplayQuizLayout()
            self.DisplayImageLayout()
            
            self.ResetContourDisplayState(sFillOrOutline, iOpacitySliderValue, fOpacity)
            
            # Populate quiz with current responses
            self.DisplayCurrentResponses(lsCurrentResponses)
            self.ApplySavedImageState()

        except:
            tb = traceback.format_exc()
            sMsg = "onResetViewClicked: Error resetting the view after NPlanes (closeup) request.  \n\n" + tb 
            self.oUtilsMsgs.DisplayError(sMsg)
            

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onNPlanesViewClicked(self):
        ''' display the requested image in the requested viewing mode
        '''
        try:
            if self.GetNPlanesComboBoxCount() > 0:
                self.CaptureAndSaveImageState()
                
                self.SetNPlanesView()
                oImageNodeOverride, iXmlImageIndex = self.GetNPlanesImageComboBoxSelection()
                self.liImageDisplayOrder = self.ReorderImageIndexToEnd(iXmlImageIndex)
                self.oImageView.AssignNPlanes(oImageNodeOverride, self.llsNPlanesOrientDest)
                self.bNPlanesViewingMode = True
        
                #    the current image node being displayed in an alternate view may have been 
                #    repeated in different orientations in the xml
                self.loCurrentXMLImageViewNodes = self.GetMatchingXMLImageNodes(oImageNodeOverride.sImagePath)
                self.ApplySavedImageState()
            else:
                sMsg = 'No images have been loaded to display in an alternate viewing mode.'
                self.oUtilsMsgs.DisplayWarning(sMsg)
        except:
            tb = traceback.format_exc()
            sMsg = "onNPlanesViewClicked: Error setting the NPlanes view (closeup) request.  \n\n" + tb 
            self.oUtilsMsgs.DisplayError(sMsg)
            
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onWindowLevelOnClicked(self):
        slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(slicer.vtkMRMLInteractionNode.AdjustWindowLevel)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onWindowLevelOffClicked(self):
        slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(slicer.vtkMRMLInteractionNode.ViewTransform)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onRepeatButtonClicked(self):
        ''' Function to manage repeating a page node when user requests a repeat (looping).
            This is generally used for multiple lesions.
        '''
        
        qtAns = self.oUtilsMsgs.DisplayOkCancel(\
                            "Are you sure you want to repeat this set of images and questions?" +\
                            "\nIf No, click 'Cancel' and press 'Next' to continue.")
        if qtAns == qt.QMessageBox.Ok:
            try:        
                bSaveComplete = True
                sMsg = ''

                self.DisableButtons()    
                bSaveComplete, sMsg = self.PerformSave('NextBtn')
                if bSaveComplete:
                    
                    self.CreateRepeatedPageNode()

                    # cleanup
                    self._loQuestionSets = []
                    slicer.mrmlScene.Clear()
            
                    
                    self.progress.setMaximum(len(self.GetNavigationList()))
                    self.progress.setValue(self.GetCurrentNavigationIndex())
                    
                    self.SetupPageState(self.GetCurrentPageIndex())
                    self.DisplayQuizLayout()
                    self.DisplayImageLayout()
                    
                else:
                    if sMsg != '':
                        self.oUtilsMsgs.DisplayWarning( sMsg )
    
                self.EnableButtons()
                
            except:
                iPage = self.GetCurrentPageIndex() + 1
                tb = traceback.format_exc()
                sMsg = "onRepeatButtonClicked: Error repeating this page. Current page: " + str(iPage) \
                       + "\n\n" + tb 
                self.oUtilsMsgs.DisplayError(sMsg)
    
    #----------
    def onContourDisplayStateChanged(self):
        # when user changes a contour visibility widget setting in the extra tools tab,
        #    adjust the image view property and turn on fill/outline for label maps and segmentations
        
        if self.oImageView != None:
            if self.qChkBoxFillOrOutline.isChecked():
                self.oImageView.SetContourVisibility('Fill')
            else:
                self.oImageView.SetContourVisibility('Outline')
            
            self.oImageView.SetLabelMapOutlineOrFill(self.lsLayoutWidgets)
    
            xPageNode = self.GetCurrentPageNode()
            loImageViewNodes = self.oImageView.GetImageViewList()
            for oViewNode in loImageViewNodes:
                if oViewNode.sViewLayer == 'Segmentation':
                    slSegDisplayNode, slSegDataNode = oViewNode.GetSegmentationNodes(xPageNode)
                    self.oImageView.SetSegmentationOutlineOrFill(oViewNode, slSegDisplayNode)
                
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def FindNewRepeatedPosition(self, iSearchPageNum, iSearchRepNum):
        ''' this function scans the navigation composite indices to match 
            the Page and Rep numbers of the new repeated page that was inserted
            into the xml file. If there is more than one question set, 
            the navigation index of the first question set is returned.
        '''

        indFound = -1
        
        for iNavInd in range(len(self.GetNavigationList())):
            iPgNum = self.GetNavigationPage(iNavInd)
            iRepNum = self.GetNavigationRepNum(iNavInd)
            
            if iPgNum == iSearchPageNum and iRepNum == iSearchRepNum :
                indFound = iNavInd
                break

                
        return indFound
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #-------------------------------------------
    #        Session Setup
    #-------------------------------------------
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def RunSetup(self, oFilesIO, slicerMainLayout):
        
        try:
            self.SetFilesIO(oFilesIO)
    
            sMsg = ''
            # open xml and check for root node
            bSuccess, xRootNode = self.oIOXml.OpenXml(self.oFilesIO.GetUserQuizResultsPath(),'Session')
    
            if not bSuccess:
                sMsg = "ERROR", "Not a valid quiz - Trouble with XML syntax."
                raise
    
            else:
                
                bEmailRequest, sMsg = self.oUtilsEmail.SetupEmailResults(self.oFilesIO, \
                                self.oIOXml.GetValueOfNodeAttribute(xRootNode, 'EmailResultsTo'))
                
                self.SetEmailResultsRequest(bEmailRequest)
                if sMsg != '':
                    raise

                self.SetupWidgets(slicerMainLayout)
                self.oQuizWidgets.qLeftWidget.activateWindow()
                
                self.AddExtraToolsTab()
    
                
                # turn on functionality if any page contains the attribute
                self.AddSegmentationModule( \
                    self.oIOXml.CheckForRequiredFunctionalityInAttribute( \
                    './/Page', 'EnableSegmentEditor','Y'))
                
                # set up and initialize Session attributes
                sColorFileName = self.oIOXml.GetValueOfNodeAttribute(xRootNode, 'ROIColorFile')
                self.oFilesIO.SetupROIColorFile(sColorFileName)
                self.SetSessionContourVisibilityDefault(xRootNode)
                self.SetRandomizeRequired()
                
                self.oFilesIO.SetupLoopingInitialization(xRootNode)
                self.oFilesIO.SetupPageGroupInitialization(xRootNode)
                
    
                # build the list of indices page/questionset as read in by the XML 
                #    list is shuffled if randomizing is requested
                self.BuildNavigationList()
                self.InitializeImageDisplayOrderIndices()
                
                # check for partial or completed quiz
                self.SetNavigationIndexIfResumeRequired()
                            

                self.progress.setMaximum(len(self.GetNavigationList()))
                self.progress.setValue(self.GetCurrentNavigationIndex())
        
                self.DisplayQuizLayout()
                self.DisplayImageLayout()
    
                
                if self.GetQuizResuming():
                    # page has been displayed - reset Quiz Resuming to false
                    self.SetQuizResuming(False)
                else:
                    self.SetupPageState(self.GetCurrentPageIndex())     # create new state object
                    
                if not self.GetQuizComplete():
                    self.AddSessionLoginTimestamp()
                    self.AddUserNameAttribute()
                    
                self.EnableButtons()

        except:
            if self.GetNavigationList() == []:
                iPage = 0
            else:
                iPage = self.GetCurrentPageIndex() + 1
                
            tb = traceback.format_exc()
            sMsg = sMsg + "RunSetup: Error trying to set up the quiz. Page: " + str(iPage) \
                   + "\n\n" + tb 
            self.oUtilsMsgs.DisplayError(sMsg)
            
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #-------------------------------------------
    #        Functions
    #-------------------------------------------
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def BuildNavigationList(self):
        ''' This function sets up the page and question set indices which
            are used to coordinate the next and previous buttons.
            The information is gathered by querying the XML quiz.
        '''
        # given the root of the xml document build composite navigation list 
        #     of indices for each page, question sets, page group and rep number
        
        self.ClearNavigationList()
        # get Page nodes
        xPages = self.oIOXml.GetChildren(self.oIOXml.GetRootNode(), 'Page')

        iPageNum = 0
        for iPageIndex in range(len(xPages)):
            iPageNum = iPageNum + 1
            # for each page - get number of question sets
            xPageNode = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', iPageIndex)
            xQuestionSets = self.oIOXml.GetChildren(xPageNode,'QuestionSet')

            sPageGroup = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'PageGroup')
            # if there is no request to randomize the page groups, there may not be a page group number
            try:
                iPageGroup = int(sPageGroup)
            except:
                # assign a unique page number if no group number exists
                iPageGroup = iPageNum
                
            sRepNum = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'Rep')
            try:
                iRepNum = int(sRepNum)
            except:
                iRepNum = 0
            
            # if there are no question sets for the page, insert a blank shell
            #    - this allows images to load
            if len(xQuestionSets) == 0:
                self.oIOXml.AddElement(xPageNode,'QuestionSet', 'Blank Quiz',{})
                xQuestionSets = self.oIOXml.GetChildren(xPageNode, 'QuestionSet')
            
            # append to composite indices list
            #    - if there are 2 pages and the 1st page has 2 question sets, 2nd page has 1 question set,
            #        and each page is in a different page group
            #        the indices will look like this:
            #        Page    QS    PageGroup  Rep
            #        0        0        1       0
            #        0        1        1       0
            #        1        0        2       0
            #    - there can be numerous questions in each question set
            for iQuestionSetIndex in range(len(xQuestionSets)):
                self.NavigationListAppend([iPageIndex,iQuestionSetIndex, iPageGroup, iRepNum])
                
                
        # if randomization is requested - shuffle the page/questionset list
        if self.GetRandomizeRequired():
            # check if xml already holds a set of randomized indices otherwise, call randomizing function
            liRandIndices = self.GetStoredRandomizedIndices()
            if liRandIndices == []:
                # get the unique list  of all Page Group numbers to randomize
                #    this was set during xml validation during the initial read
                liIndicesToRandomize = self.oFilesIO.GetListUniquePageGroups()
                liRandIndices = self.RandomizePageGroups(liIndicesToRandomize)
                self.AddRandomizedIndicesToXML(liRandIndices)
             
            self.SetNavigationList( self.ShuffleNavigationList(liRandIndices) )
    
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ShuffleNavigationList(self, lRandIndices):
        ''' This function will shuffle the original list as read in from the quiz xml,  that holds the
            "[page number,questionset number, page group number, rep number]" according to the randomized index list input.
            The question sets always remain in the same order as read in with the page, they are never randomized.
            The page groups are randomized. 
                 If more than one page has the same group number, they will remain in the order they were read in.
                 
            e.g. Randomized Page Group order : 2,3,1
            
                     Original XML List                Randomized Page           Shuffled Composite List
                       Page   QS   Grp   Rep             Groups                   Page   QS   Grp   Rep
                       0      0     1     0                 2                       2     0     2     0
                       0      1     1     0                 3                       2     1     2     0
                       1      0     1     0                 1                       3     0     2     0
                       2      0     2     0                                         4     0     3     0
                       2      1     2     0                                         4     1     3     0
                       3      0     2     0                                         0     0     1     0
                       4      0     3     0                                         0     1     1     0
                       4      1     3     0                                         1     0     1     0
        '''
    
        lShuffledCompositeIndices = []
        
        for indRand in range(len(lRandIndices)):
            for indOrig in range(len(self.GetNavigationList())):
                if self.GetNavigationPageGroup(indOrig) == lRandIndices[indRand] :
                    lShuffledCompositeIndices.append( self.GetNavigationIndicesAtIndex(indOrig))
        
        return lShuffledCompositeIndices
   
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def RandomizePageGroups(self, liIndicesToRandomize, iSeed=None):
        ''' Function to take a list of indices and randomize them.
            If there is a '0', it is removed prior to randomizing and inserted back to the
            beginning of the list.
        '''
        
        bPageGroup0 = False
        # remove PageGroup 0 before reandomizing since these represent pages  
        # that will always appear at the beginning of the quiz
        if 0 in liIndicesToRandomize:
            liIndicesToRandomize.remove(0)
            bPageGroup0 = True
        
        ###### iSeed = 100 # for debug
        if iSeed != None:     # used for testing
            random.seed(iSeed)
        else:
            random.seed()
            
        random.shuffle(liIndicesToRandomize)
        liRandIndices = liIndicesToRandomize

        # reset the first PageGroup number to 0 if it was in the quiz
        if bPageGroup0:
            liRandIndices.insert(0,0)
        
        return liRandIndices
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddRandomizedIndicesToXML(self,liIndices):
        ''' Function to coordinate adding the randomized indices into the user's XML.
        '''
        # convert indices into a string
        sIndicesToStore = ''
        iCounter = 0
        
        for iNum in liIndices:
            iCounter = iCounter + 1
            sIndicesToStore = sIndicesToStore + str(iNum)
            if iCounter < len(liIndices):
                sIndicesToStore = sIndicesToStore + ','
                
        dictAttrib = {}     # no attributes for this element
        self.oIOXml.AddElement(self.oIOXml.GetRootNode(),'RandomizedPageGroupIndices',sIndicesToStore, dictAttrib)
        
                
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetStoredRandomizedIndices(self):
        ''' This function will check for existing element of randomized indices.
            If no element exists, a new list will be created.
        '''

        liRandIndices = []
        liStoredRandIndices = []
        
        xRandIndicesNode = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'RandomizedPageGroupIndices', 0)
        if xRandIndicesNode != None:
            sStoredRandIndices = self.oIOXml.GetDataInNode(xRandIndicesNode)
            liStoredRandIndices = [int(s) for s in sStoredRandIndices.split(",")]
        
        return liStoredRandIndices
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CheckForLastQuestionSetForPage(self):
        bLastQuestionSet = False
        
        # check if at the end of the quiz
        if (self.GetCurrentNavigationIndex() == len(self.GetNavigationList()) - 1):
            bLastQuestionSet = True

        else:
            # we are not at the end of the quiz
            # assume multiple question sets for the page
            # check if next page in the composite index is different than the current page
            #    if yes - we have reached the last question set
            if not( self.GetNavigationPage(self.GetCurrentNavigationIndex())) == self.GetNavigationPage(self.GetCurrentNavigationIndex() + 1):
                bLastQuestionSet = True            
           
            
        return bLastQuestionSet
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AdjustToCurrentQuestionSet(self):
        '''
            if there are multiple question sets for a page, the list of question sets must
               include all previous question sets - up to the one being displayed
               (eg. if a page has 4 Qsets, and we are going back to Qset 3,
               we need to collect question set indices 0, and 1 first,
               then continue processing for index 2 which will be appended in DisplayQuestionSet function)
            
            This function is called 
               - when the previous button is pressed or
               - if a resume is required into a question set that is not the first for the page
               - if the ResetView button in Extra Tools is pressed  
        '''
        
        self._loQuestionSets = [] # initialize
        indQSet = self.GetCurrentQuestionSetIndex()

        if indQSet > 0:

            for idx in range(indQSet):
                xNodeQuestionSet = self.GetNthQuestionSetForCurrentPage(idx)
                oQuestionSet = QuestionSet(self.oFilesIO)
                oQuestionSet.ExtractQuestionsFromXML(xNodeQuestionSet)
                self._loQuestionSets.append(oQuestionSet)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def DisplayQuizLayout(self):
        
        try:
            # extract page and question set indices from the current composite index
            xNodeQuestionSet = self.GetCurrentQuestionSetNode()
            oQuestionSet = QuestionSet(self.oFilesIO)
            oQuestionSet.ExtractQuestionsFromXML(xNodeQuestionSet)
            
    
            # first clear any previous widgets (except push buttons)
            for i in reversed(range(self.oQuizWidgets.qQuizLayout.count())):
                self.oQuizWidgets.qQuizLayout.itemAt(i).widget().setParent(None)
    
            
            bBuildSuccess, qWidgetQuestionSetForm = oQuestionSet.BuildQuestionSetForm()
            
            if bBuildSuccess:
                self.slMarkupsLineWidget.setPlaceModeEnabled(True)
                self.oQuizWidgets.qQuizLayout.addWidget(qWidgetQuestionSetForm)
                self._loQuestionSets.append(oQuestionSet)
                qWidgetQuestionSetForm.setEnabled(True) # initialize
    
    
                # if sSavedResponseCompletionLevel == 'AllResponses' or sSavedResponseCompletionLevel == 'PartialResponses':
                #     self.DisplaySavedResponse()
                self.DisplaySavedResponse()
                self.SetPreviousResponses([]) # reset for new Question Set
                
            ################################################
            ''' Enable tabs and update the progress bar.
                This is done after displaying questions and prior to loading images to provide a smooth transition
                when widgets need to be disabled.
            '''
                
            xPageNode = self.GetCurrentPageNode()
            self.SetMultipleResponseAllowed(self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'AllowMultipleResponse'))
            self.SetRequestToEnableSegmentEditorTF(self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'EnableSegmentEditor'))
            
            if self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'Loop') == "Y":
                self.SetPageLooping(True)
            else:
                self.SetPageLooping(False)
    
            if self.GetQuizComplete():
                self.SetMultipleResponseAllowed('N') #read only
                qWidgetQuestionSetForm.setEnabled(False)
                self.SegmentationTabEnabler(False)
            else:
                
                #enable tabs
                if self.GetMultipleResponseAllowed() or self.GetQuizResuming():
                    qWidgetQuestionSetForm.setEnabled(True)
                    self.SegmentationTabEnabler(self.GetRequestToEnableSegmentEditorTF())
                    self.EnableMarkupLinesTF(True)
                else:
                    # Multiple Responses are not allowed AND this is not a Quiz Resuming state
                    sSavedResponseCompletionLevel = self.oPageState.GetSavedResponseCompletionLevel(self.GetCurrentQuestionSetNode())
                    sPageComplete = self.GetPageCompleteAttribute(self.GetCurrentNavigationIndex())
                    if sPageComplete == 'Y':
                        qWidgetQuestionSetForm.setEnabled(False)
                        self.SegmentationTabEnabler(False)
                        self.EnableMarkupLinesTF(False)
                    else:
                        # page not complete - check for question and segmentation completion
                        qWidgetQuestionSetForm.setEnabled(True)
                        self.SegmentationTabEnabler(self.GetRequestToEnableSegmentEditorTF())
                        self.EnableMarkupLinesTF(True)  # no maximum number of lines
    
                        if sSavedResponseCompletionLevel == 'AllResponses':
                            qWidgetQuestionSetForm.setEnabled(False)
                        if self.oPageState.GetSegmentationsCompletedState():
                            self.SegmentationTabEnabler(False)
                        
                if self.GetSegmentationTabIndex() > 0:
                    # clear Master and Merge selector boxes
                    oQuizzerEditorHelperBox = slicer.modules.quizzereditor.widgetRepresentation().self().GetHelperBox()
                    oQuizzerEditorHelperBox.setMasterVolume(None)

            ################################################
                
            # add page ID/descriptor to the progress bar
            xmlPageNode = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', self.GetCurrentPageIndex())
            self.sPageDescriptor = self.oIOXml.GetValueOfNodeAttribute(xmlPageNode, 'Descriptor')
            self.sPageID = self.oIOXml.GetValueOfNodeAttribute(xmlPageNode, 'ID')
            iProgressPercent = int(self.GetCurrentNavigationIndex() / len(self.GetNavigationList()) * 100)
            self.progress.setFormat(self.sPageID + '  ' + self.sPageDescriptor + '    ' + str(iProgressPercent) + '%')
                
        except:
            iPage = self.GetCurrentPageIndex() + 1
            tb = traceback.format_exc()
            sMsg = "DisplayQuizLayout: Error trying to display questions. Page: " + str(iPage) \
                   + "\n\n" + tb 
            self.oUtilsMsgs.DisplayError(sMsg)
            
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def DisplayImageLayout(self):

        try:
            xmlPageNode = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', self.GetCurrentPageIndex())
            self.SetViewingLayout(xmlPageNode)
    
            # set up the images on the page
            self.oImageView = ImageView()
            self.oImageView.RunSetup(self.GetCurrentPageNode(), self.oFilesIO.GetDataParentDir())
            self.ResetContourVisibilityToSessionDefault()
    
            # load label maps and markup lines if a path has been stored in the xml for the images on this page
            self.oFilesIO.LoadSavedLabelMaps(self)
            self.oFilesIO.LoadSavedMarkupLines(self)
    
            # assign each image node and its label map (if applicable) to the viewing widget
            self.oImageView.AssignNodesToView()
            
            self.SetNPlanesComboBoxImageNames()
    
            self.ApplySavedImageState()
        
        except:
            iPage = self.GetCurrentPageIndex() + 1
            tb = traceback.format_exc()
            sMsg = "DisplayImageLayout: Error trying to display images. Page: " + str(iPage) \
                   + "\n\n" + tb 
            self.oUtilsMsgs.DisplayError(sMsg)
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetViewingLayout(self, xmlPageNode):
        
        # clear combo box
        self.lsLayoutWidgets = []
        # set the requested layout for images
        self.sPageLayout = self.oIOXml.GetValueOfNodeAttribute(xmlPageNode, 'Layout')
        if self.sPageLayout == 'TwoOverTwo' :
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutTwoOverTwoView)
            self.lsLayoutWidgets.append('Red')
            self.lsLayoutWidgets.append('Green')
            self.lsLayoutWidgets.append('Yellow')
            self.lsLayoutWidgets.append('Slice4')
        elif self.sPageLayout == 'OneUpRedSlice' :
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)
            self.lsLayoutWidgets.append('Red')
        elif self.sPageLayout == 'FourUp' :
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
            self.lsLayoutWidgets.append('Red')
            self.lsLayoutWidgets.append('Green')
            self.lsLayoutWidgets.append('Yellow')
        elif self.sPageLayout == 'SideBySideRedYellow' :
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutSideBySideView)
            self.lsLayoutWidgets.append('Red')
            self.lsLayoutWidgets.append('Yellow')
        else:
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
            self.lsLayoutWidgets.append('Red')
            self.lsLayoutWidgets.append('Green')
            self.lsLayoutWidgets.append('Yellow')
                    
    

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def DisplayCurrentResponses(self, lsCurrentResponses):

        indQSet = self.GetCurrentQuestionSetIndex()
 
        oQuestionSet = self._loQuestionSets[indQSet]
        loQuestions = oQuestionSet.GetQuestionList()
         
        for indQuestion in range(len(loQuestions)):
            oQuestion = loQuestions[indQuestion]
            oQuestion.PopulateQuestionWithResponses(lsCurrentResponses[indQuestion])

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def DisplaySavedResponse(self):

        xNodeQuestionSet = self.GetCurrentQuestionSetNode()
        indQSet = self.GetCurrentQuestionSetIndex()
 
        oQuestionSet = self._loQuestionSets[indQSet]
        loQuestions = oQuestionSet.GetQuestionList()
         
        # for each question and each option, extract any existing responses from the XML
         
        lsAllResponsesForQuestions = []
        for indQuestion in range(len(loQuestions)):
            oQuestion = loQuestions[indQuestion]
            xQuestionNode = self.oIOXml.GetNthChild(xNodeQuestionSet, 'Question', indQuestion)
             
                 
            lsResponseValues = []                  
            xAllOptions = self.oIOXml.GetChildren(xQuestionNode, 'Option')


            xAllOptions = self.GetAllOptionNodes(indQuestion)
            for xOptionNode in xAllOptions:
                
                                            
                sLatestResponse = ''
                xLatestResponseNode = self.oIOXml.GetLatestChildElement(xOptionNode, 'Response')
                if xLatestResponseNode != None:
                    sLatestResponse = self.oIOXml.GetDataInNode(xLatestResponseNode)
    
                # search for 'latest' response completed - update the list
                lsResponseValues.append(sLatestResponse)
                
            oQuestion.PopulateQuestionWithResponses(lsResponseValues)

            # only InfoBox type of question can have all responses equal to null string
            if self.oIOXml.GetValueOfNodeAttribute(xQuestionNode, 'Type') != "InfoBox" \
                    and (all(elem == '' for elem in lsResponseValues)):
                lsResponseValues = []   # reset if all are empty

            lsAllResponsesForQuestions.append(lsResponseValues)
            
    
            lsResponseValues = []  # clear for next set of options 

        self.SetPreviousResponses(lsAllResponsesForQuestions)
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def PerformSave(self, sCaller):
        """ Actions performed here include:
            - save the label maps (done before saving the collected quiz responses)
            - write the collected responses to the xml
            - capture and write the state of the images (window/level and slice offset) to xml
        """
        
        sMsg = ''
        bSaveComplete = True
        try:
            
            if not self.GetQuizComplete():
            
                if sCaller != 'ResetView':
                    self.oQuizWidgets.qTabWidget.setCurrentIndex(0)
                self.SetSegmentationTabDefaults()
                    
                idxQuestionSet = self.GetCurrentQuestionSetIndex()
                iNumQSets = len(self.GetAllQuestionSetNodesForCurrentPage())

                
                self.oFilesIO.SaveLabelMaps(self, sCaller)
                self.oFilesIO.SaveMarkupLines(self)
   
                sCaptureSuccessLevel, self._lsNewResponses, sMsg = self.CaptureNewResponses()
                
                if sCaller == 'NextBtn' or sCaller == 'Finish':
                    # only write to xml if all responses were captured
                    if sCaptureSuccessLevel == 'AllResponses':
                        self.WriteResponsesToXml()
                    else:
                        sMsg = sMsg + '\n All questions must be answered to proceed'
                        bSaveComplete = False
                        
                else:  
                    # Caller must have been the Previous or Exit buttons or a close was 
                    #     requested (which triggers the event filter)
                    # Only write if there were responses captured
                    if sCaptureSuccessLevel == 'AllResponses' or sCaptureSuccessLevel == 'PartialResponses':
                        self.WriteResponsesToXml()
                    else:
                        # if no responses were captured 
                        if sCaptureSuccessLevel == 'NoResponses':
                            # this isn't the Next button so it is allowed
                            bSaveComplete = True
                        
                ################################################
                ##########  Updating completion flags ##########        
                ################################################

                if bSaveComplete:
                    #after writing responses, update page states and record the image state
                    self.oPageState.UpdateCompletionLists(self.GetCurrentPageNode())
                    self.CaptureAndSaveImageState()
                    
                    if sCaller == 'NextBtn' or sCaller == 'Finish':
                        # if this was the last question set for the page, check for completion
                        if idxQuestionSet == iNumQSets - 1:
                            
                            sCompletionFlagMsg = self.oPageState.UpdateCompletedFlags(self.GetCurrentPageNode())
                            sMsg = sMsg + sCompletionFlagMsg
                            
                            if self.oPageState.GetPageCompletedTF():
                                bSaveComplete = True
                                self.AddPageCompleteAttribute(self.GetCurrentPageIndex())
                                if sCaller == 'Finish':
                                    self.AddQuizCompleteAttribute()
                                    self.SetQuizComplete(True)
                            else:
                                bSaveComplete = False
                                    
        except Exception:
            tb = traceback.format_exc()
            sMsg = sMsg + '\nPerformSave error \n\n' + tb
            raise Exception(sMsg)                
    
        return bSaveComplete, sMsg
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetSegmentationTabDefaults(self):
        
        if self.GetSegmentationTabIndex() > 0:
            slicer.modules.quizzereditor.widgetRepresentation().self().updateLabelFrame(None)
            slicer.modules.quizzereditor.widgetRepresentation().self().toolsBox.selectEffect('DefaultTool')
            slicer.modules.quizzereditor.widgetRepresentation().self().helper.setMasterVolume(None)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CaptureNewResponses(self):
        ''' When moving to another display of Images and QuestionSet (from pressing Next or Previous)
            the new responses that were entered must be captured ready to do the save to XML.
            A check for any missing responses to the questions is done and passed back to the calling function.
        '''
        
        # sMsg may be set in Question class function to capture the response
        sMsg = ''
        sAllMsgs = ''
        
        # get list of questions from current question set
        indQSet = self.GetCurrentQuestionSetIndex()
        oQuestionSet = self._loQuestionSets[indQSet]
        loQuestions = oQuestionSet.GetQuestionList()
            
        lsAllResponses = []
        lsResponsesForOptions = []
        iNumMissingResponses = 0
        
        for indQuestion in range(len(loQuestions)):
            oQuestion = loQuestions[indQuestion]
            bResponseCaptured = False
            
            bResponseCaptured, lsResponsesForOptions, sMsg = oQuestion.CaptureResponse()


            # append all captured lists - even if it was empty (partial responses)
            lsAllResponses.append(lsResponsesForOptions)
            
            # string together all missing response messages
            if sMsg != '':
                if sAllMsgs == '':
                    sAllMsgs = sMsg
                else:
                    sAllMsgs = sAllMsgs + '\n' + sMsg 
            
            # keep track if a question was missed
            if bResponseCaptured == False:
                iNumMissingResponses = iNumMissingResponses + 1
                
        # define success level
        sCaptureSuccessLevel = self.oPageState.CategorizeResponseCompletionLevel(len(loQuestions), len(loQuestions)-iNumMissingResponses)
                
        return sCaptureSuccessLevel, lsAllResponses, sAllMsgs
       
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetMatchingXMLImageNodes(self, sImagePathToSearch):
        ''' Search the xml image nodes for the current page that have the same
            path as the image node input to this function
        '''
        loMatchingImageNodes = []
        
        loImageViewNodes = self.oImageView.GetImageViewList()
        for oImageViewNode in loImageViewNodes:
            if oImageViewNode.sImagePath == sImagePathToSearch:
                loMatchingImageNodes.append(oImageViewNode)
                
        return loMatchingImageNodes    
                
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CaptureAndSaveImageState(self):
        ''' Save the current image state (window/level, slice number) to the XML.
            This state is reset if the user revisits this page.
            Special case: User has entered a viewing mode. The widgets no
            longer hold the default list of images and orientations.
        '''

        sMsg = ''
        bSuccess = True
        bAddedNewElement = False
        
        try:
            if not self.GetQuizComplete():
                lsDestOrientNode = []
                llsNodeProperties = []
                
                if not self.bNPlanesViewingMode:
                    # quizzer is in the default view mode - get state from assigned widgets
                    for oImageNode in self.oImageView.GetImageViewList():
                        if (oImageNode.sImageType == 'Volume' or oImageNode.sImageType == 'VolumeSequence'):
                            lsDestOrientNode = [oImageNode.sDestination, oImageNode.sOrientation, oImageNode]
                            llsNodeProperties.append(lsDestOrientNode)
                else:
                    # quizzer was in alternate viewing mode - set up the list to hold current view's orientation, destination and image node
                    for oImageNode in self.loCurrentXMLImageViewNodes:
                        
                        for i in range(len(self.llsNPlanesOrientDest)):
                            llsNodeProperties.append([self.llsNPlanesOrientDest[i][1], self.llsNPlanesOrientDest[i][0], oImageNode])
                
                
                # for each image, capture the slice, window and level settings of the current mode being displayed 
                #        before changing the selection or resetting to default
                #        (eg. what was the state for the images in 1-Plane Axial view before changing to default view)
                for idx in range(len(llsNodeProperties)):
                    sWidgetName = llsNodeProperties[idx][0]
                    sOrientation = llsNodeProperties[idx][1]
                    oImageNode = llsNodeProperties[idx][2]
    
                    if (oImageNode.sImageType == 'Volume' or oImageNode.sImageType == 'VolumeSequence'):
        
                        dictAttribState = self.oImageView.GetViewState(oImageNode.slNode, sWidgetName)
                        dictViewModeAttributes = {"Orientation": sOrientation, "Destination": sWidgetName, "ViewingMode": self.sViewingMode}
                        dictAttribState.update(dictViewModeAttributes)
                        
                        if oImageNode.sImageType == 'VolumeSequence':
                            slAssociatedSequenceBrowserNode = oImageNode.GetAssociatedSequenceBrowserNode()
                            if slAssociatedSequenceBrowserNode != None:
                                sFrameNumber = str(slAssociatedSequenceBrowserNode.GetSelectedItemNumber())
                                dictFrameAttribute = {'Frame':sFrameNumber}
                                dictAttribState.update(dictFrameAttribute)
        
                        # check if xml State element exists
                        xImage = oImageNode.GetXmlImageElement()
                        # add image state element (tagged with response time)
                        self.AddImageStateElement(xImage, dictAttribState)
                        bAddedNewElement = True     # at least one element added
                            
                if bAddedNewElement:
                    self.oIOXml.SaveXml(self.oFilesIO.GetUserQuizResultsPath())
    
        except:
            bSuccess = False
            iPage = self.GetCurrentPageIndex() + 1
            tb = traceback.format_exc()
            sMsg = "CaptureAndSaveImageState: Error saving the image state. Current page: " + str(iPage) \
                   + "\n\n" + tb 
            self.oUtilsMsgs.DisplayError(sMsg)
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ApplySavedImageState(self):
        """ From the xml file, get the image state elements. 
            Based on the viewing mode, define the state orientations that need to be searched for and set.
            Check the xml for the current page for state elements. If the required orientations are
            not found, search for a previously stored state for this image in the required orientation.
            (eg. if clinician set the window/level for an image on one page, and that same image is 
            loaded on a subsequent page, the same window/level should be applied.)
            
        """
        
        loImageNodes = []
        lsRequiredOrientations = []
        dictNPlanesOrientDest = {}
        dictBackgroundWidgetsToResetWithOffsets = {}
        idxCurrentPage = self.GetCurrentPageIndex()
        
        if not self.bNPlanesViewingMode:
            loImageNodes = self.oImageView.GetImageViewList()
        else:
            oImageNodeOverride, iXmlImageIndex = self.GetNPlanesImageComboBoxSelection()
            loImageNodes.append(oImageNodeOverride)
            for i in range(len(self.llsNPlanesOrientDest)):
                lsRequiredOrientations.append(self.llsNPlanesOrientDest[i][0])
                dictNPlanesOrientDest.update({self.llsNPlanesOrientDest[i][0] : self.llsNPlanesOrientDest[i][1]})
            
        for ind in range(len(loImageNodes)):
            if self.bNPlanesViewingMode:
                oImageNode = loImageNodes[ind]
            else:
                oImageNode = loImageNodes[self.GetImageDisplayOrderIndices()[ind]]
                
            dictImageState = {}
            
            if (oImageNode.sImageType == "Volume" or oImageNode.sImageType == "VolumeSequence"):

                if self.sViewingMode == "Default":
                    lsRequiredOrientations = [oImageNode.sOrientation]
                    
                bLatestWindowLevelFound = False
                ldictAllImageStateItems =\
                    self.GetStateElementsForMatchingImagePath(self.oFilesIO.GetRelativeDataPath(oImageNode.sImagePath))
    
                for sRequiredOrientation in lsRequiredOrientations:
                    bFoundOrientation = False
                    
                    for idxImageStateElement in reversed(range(len(ldictAllImageStateItems))):
#                         xState = lxAllStateElements[idxImageStateElement]
#                         dictImageState = self.oIOXml.GetAttributes(xState)
                        
                        dictImageStateItems = ldictAllImageStateItems[idxImageStateElement]
                        dictImageState = self.oIOXml.GetAttributes(ldictAllImageStateItems[idxImageStateElement]['StateElement'])

                        # get first instance in the reversed search for the window/level
                        # then continue search for matching orientation to get the slice offset
                        if not bLatestWindowLevelFound:
                            sLevel = dictImageState['Level']
                            sWindow = dictImageState['Window']
                            bLatestWindowLevelFound = True


                        if dictImageState["Orientation"] == sRequiredOrientation and\
                                dictImageStateItems["DefaultOrientation"] == dictImageState["Orientation"]:
                            bFoundOrientation = True
                            break
                    
                    # capture the destination and offset if this was a background layer for later reset to center the field of view
                    #    - this is necessary because a foreground layer for a widget may be processed
                    #      after the background layer (depending on xml order) which may change the slice offset
                    #    (This is particularly important for Background layers that have an image with
                    #     only one slice (eg. histology) )

                    # work with destination depending on the viewing mode        
                    if not self.bNPlanesViewingMode:
                        sDestination = oImageNode.sDestination
                    else:
                        sDestination = dictNPlanesOrientDest[sRequiredOrientation]
                        
                    if dictImageState != {} :

                        if oImageNode.sViewLayer == 'Background' and idxCurrentPage != int(dictImageStateItems['Page']):
                            # image state element was from a previous page
                            #    update slice offset with current page initial offset if defined
                            if oImageNode.fInitialSliceOffset != None:
                                dictBackgroundWidgetsToResetWithOffsets[sDestination] = oImageNode.fInitialSliceOffset
                            else:
                                dictBackgroundWidgetsToResetWithOffsets[sDestination] = float(dictImageState['SliceOffset'])
                        else:
                            if oImageNode.sViewLayer == 'Background' and idxCurrentPage == int(dictImageStateItems['Page']):
                                # image state element was from current page
                                #    update slice offset with saved offset
                                dictBackgroundWidgetsToResetWithOffsets[sDestination] = float(dictImageState['SliceOffset'])

                            
                            
                    if bFoundOrientation:
                        # update with most recent window/level
                        if bLatestWindowLevelFound:
                            dictImageState["Window"] = sWindow
                            dictImageState["Level"] = sLevel
                            
                        if not self.bNPlanesViewingMode:
                            oImageNode.SetImageState(dictImageState)
                        else:
                            # for NPlanes viewing mode, adjust with the destination override
                            sDestinationOverride = dictNPlanesOrientDest[sRequiredOrientation]
                            oImageNode.SetImageState(dictImageState, sDestinationOverride)
                    
                    else:
                        # no state element was found - 
                        #    capture destination and assign the offset to the initial if defined 
                        #    (will be None if not defined)
                        if oImageNode.sViewLayer == 'Background':
                            dictBackgroundWidgetsToResetWithOffsets[sDestination] = oImageNode.fInitialSliceOffset
                                            
            # first reset identified widgets to the default - fit to the background
            for key in dictBackgroundWidgetsToResetWithOffsets:
                slWidget = slicer.app.layoutManager().sliceWidget(key)
                slWidget.fitSliceToBackground() # default

            # re-adjust with captured offset
            for key in dictBackgroundWidgetsToResetWithOffsets:
                slWidget = slicer.app.layoutManager().sliceWidget(key)
                slWindowLogic = slWidget.sliceLogic()
                if dictBackgroundWidgetsToResetWithOffsets[key] != None :
                    slWindowLogic.SetSliceOffset(dictBackgroundWidgetsToResetWithOffsets[key])

        # reset field of view if zoom was requested (not applicable for NPlanes mode
        for ind in range(len(loImageNodes)):
            if not self.bNPlanesViewingMode:
                oImageNode = loImageNodes[self.GetImageDisplayOrderIndices()[ind]]
                
                oImageNode.SetFieldOfViewAndOrigin()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetStateElementsForMatchingImagePath(self, sCurrentImagePath):
        
        ldictAllImageStateItems = []
        
        lxPages = self.oIOXml.GetChildren(self.oIOXml.GetRootNode(), 'Page')
        
        # for each page in the xml (up to and including  the current page) get all image elements
        for iPageIdx in range(len(lxPages)):
            if iPageIdx <= self.GetCurrentPageIndex():
                xPage = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', iPageIdx)
                lxImageElements = self.oIOXml.GetChildren(xPage, 'Image')
                
                # for all images on the page, if a volume type image, collect the State elements
                for xImage in lxImageElements:
                    sImageType = self.oIOXml.GetValueOfNodeAttribute(xImage, 'Type')
                    if sImageType == 'Volume' or sImageType == 'VolumeSequence':
                        

                        sPath = self.oIOXml.GetDataFromLastChild(xImage, 'Path')
                        if sPath == sCurrentImagePath:
                            
                            
                            sImageDefaultOrientation = self.oIOXml.GetDataFromLastChild(xImage, 'DefaultOrientation')
                                
                            if self.oIOXml.GetNumChildrenByName(xImage, 'State') > 0:
                                lStateElements = self.oIOXml.GetChildren(xImage, 'State')
                                for xState in lStateElements:
                                    
                                    dictImageStateItems = {'DefaultOrientation':sImageDefaultOrientation, 'Page':str(iPageIdx),'StateElement':xState}
                                    ldictAllImageStateItems.append(dictImageStateItems)

                        
        return ldictAllImageStateItems
                
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetXmlElementFromAttributeHistory(self, sPageChildrenToSearch, sImageAttributeToMatch, sAttributeValue):
        ''' Function will return the historical element that contains the attribute requested for the search.
            This attribute is associated with a child of the 'Page' element.
            The search goes through the pages in reverse. 
                For each page, the requested children are searched (forward) for the requested attribute.
            When found, the xml element that contains the attribute is returned.
        '''
        
        xHistoricalChildElement = None
        
        # start searching pages in reverse order - to get most recent setting
        # first match will end the search
        bHistoricalElementFound = False
        for iPageIndex in range(self.GetCurrentPageIndex()-1, -1, -1):
            xPageNode = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', iPageIndex)
        
            if bHistoricalElementFound == False:
                
                #get all requested children
                lxChildElementsToSearch = self.oIOXml.GetChildren(xPageNode, sPageChildrenToSearch)
                if len(lxChildElementsToSearch) > 0:
    
                    for xImageNode in lxChildElementsToSearch:
                        
                        # get image attribute
                        sPotentialAttributeValue = self.oIOXml.GetValueOfNodeAttribute(xImageNode, sImageAttributeToMatch)
                        if sPotentialAttributeValue == sAttributeValue:
                            xHistoricalChildElement = xImageNode
                            bHistoricalElementFound = True
                            break
            else:
                break
        
        return xHistoricalChildElement
    

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def WriteResponsesToXml(self):
        """ Write captured responses to xml. If this is the first write to the xml
            with responses, the login timestamp is also added.
            After responses are added, record the image state in the xml file.
        """
        
        try:
            # only allow for writing of responses under certain conditions
            #    - allow if the question set is marked for multiple responses allowed
            #    - OR allow if the number of questions with responses already 
            #      recorded is 'NoResponses' or 'PartialResponses' (not 'AllResponses')
            
            # get from xml, the category of saved recorded responses to 
            #    determine whether the newly captured responses are to be written
            sQuestionsWithRecordedResponses = self.oPageState.GetSavedResponseCompletionLevel(self.GetCurrentQuestionSetNode())
            

            if ( self.GetMultipleResponseAllowed() == True)  or \
                ((self.GetMultipleResponseAllowed() == False) and (sQuestionsWithRecordedResponses != 'AllResponses') ):

                # check to see if the responses for the question set match 
                #    what was previously captured
                #    -only write responses if they have changed
                if not self._lsNewResponses == self.GetPreviousResponses():
                        
                    self.AddXmlElements()
                    
                    # potential exit of quiz - update logout time with each write
                    self.UpdateSessionLogoutTimestamp()
                    
                    self.oIOXml.SaveXml(self.oFilesIO.GetUserQuizResultsPath())
                    
        
        except Exception:
            tb = traceback.format_exc()
            sMsg = 'Error writing responses to Xml' + '\n Does this file exist? : \n' \
                + self.oFilesIO.GetUserQuizResultsPath()\
                + '\n\n' + tb
            # critical error - exit
            self.oUtilsMsgs.DisplayError( sMsg )
            
        return 
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CreateRepeatedPageNode(self, sXmlFilePath = None):
        ''' Function to copy the current page into the xml allowing the user to create new segments or  
            measurement lines for the same image. 
        '''
        # allow for testing environment to use a pre-set testing file path
        if sXmlFilePath == None:
            sXmlFilePath = self.oFilesIO.GetUserQuizResultsPath()   # for live run
        
        indXmlPageToRepeat = self.GetCurrentPageIndex()
        
        
        xCopyOfXmlPageToRepeatNode = self.oIOXml.CopyElement(self.GetCurrentPageNode())
        iCopiedRepNum = int(self.oIOXml.GetValueOfNodeAttribute(xCopyOfXmlPageToRepeatNode, "Rep"))
        
        # find the next xml page that has Rep 0 (move past all repeated pages for this loop)
        indNextXmlPageWithRep0 = self.oIOXml.GetIndexOfNextChildWithAttributeValue(self.oIOXml.GetRootNode(), "Page", indXmlPageToRepeat + 1, "Rep", "0")

        if indNextXmlPageWithRep0 != -1:
            self.oIOXml.InsertElementBeforeIndex(self.oIOXml.GetRootNode(), xCopyOfXmlPageToRepeatNode, indNextXmlPageWithRep0)
        else:
            # attribute was not found
            self.oIOXml.AppendElement(self.oIOXml.GetRootNode(), xCopyOfXmlPageToRepeatNode)
            indNextXmlPageWithRep0 = self.oIOXml.GetNumChildrenByName(self.oIOXml.GetRootNode(), 'Page') - 1
        
        self.oIOXml.SaveXml(sXmlFilePath)    # for debug
        self.BuildNavigationList() # update after adding xml page
        
        iNewNavInd = self.FindNewRepeatedPosition(indNextXmlPageWithRep0, iCopiedRepNum)
        self.SetCurrentNavigationIndex(iNewNavInd)
    
        # update the repeated page
        self.AdjustXMLForRepeatedPage()
        self.oIOXml.SaveXml(sXmlFilePath)    # for debug
        self.BuildNavigationList()  # repeated here to pick up attribute adjustments for Rep#
        self.oIOXml.SaveXml(sXmlFilePath)

    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AdjustXMLForRepeatedPage(self):
        ''' Function to update the newly repeated Page node.
            The Page ID attribute will have '-Rep#' appended.
            Any previously stored label map and markup line paths are removed.
            Ay previously stored responses to questions will be removed.
        '''
        
        sMsg = ''
        try:
            
            xNewRepeatPage = self.GetCurrentPageNode()
            
            # get last rep number to increment current rep
            xPreviousPage = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), "Page", self.GetNavigationPage( self.GetCurrentNavigationIndex() -1 ) )
            sPreviousRepNum = self.oIOXml.GetValueOfNodeAttribute(xPreviousPage, "Rep")
            sPreviousPageID = self.oIOXml.GetValueOfNodeAttribute(xPreviousPage, 'ID')
            
            
            self.oIOXml.UpdateAttributesInElement(xNewRepeatPage, {"PageComplete":"N"})
            iPreviousRepNum = int(sPreviousRepNum)
            sNewRepNum = str(iPreviousRepNum + 1)
            self.oIOXml.UpdateAttributesInElement(xNewRepeatPage, {"Rep":sNewRepNum})
            
            iSubIndex = sPreviousPageID.find('-Rep')
            if iSubIndex >=0:
                sStrippedPageID = sPreviousPageID[0:iSubIndex]
            else:
                sStrippedPageID = sPreviousPageID
            
            sNewPageID = sStrippedPageID + '-Rep' + str(sNewRepNum)
            self.oIOXml.UpdateAttributesInElement(xNewRepeatPage, {"ID":sNewPageID})
            
            
                
            # remove LabelmapPath and MarkupLinePath elements
            lxImages = self.oIOXml.GetChildren(xNewRepeatPage, 'Image')
            for xImage in lxImages:
                self.oIOXml.RemoveAllElements(xImage, "LabelMapPath")
                self.oIOXml.RemoveAllElements(xImage, "MarkupLinePath")
                
            # remove Response elements
            lxQuestionSets = self.oIOXml.GetChildren(xNewRepeatPage, "QuestionSet")
            for xQuestionSet in lxQuestionSets:
                lxQuestions = self.oIOXml.GetChildren(xQuestionSet, "Question")
                for xQuestion in lxQuestions:
                    lxOptions = self.oIOXml.GetChildren(xQuestion, "Option")
                    for xOption in lxOptions:
                        self.oIOXml.RemoveAllElements(xOption, "Response")
        
        except:
            tb = traceback.format_exc()
            iPage = self.GetCurrentPageIndex() + 1
            sMsg = 'AdjustXMLForRepeatedPage: Trouble updating repeated page.' + \
                    'Previous page rep number should be a string that can be converted to an integer.' +\
                    'Check the functionality of CopyPage.' \
                    '\nSee Page: ' + str(iPage) + '\n\n' + tb
            self.oUtilsMsgs.DisplayError(sMsg)
        
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddXmlElements(self):
        
        # using the list of question set responses, isolate responses for each question
        iNumQuestions = len(self._lsNewResponses)

        # for each question in the question set responses        
        for indQuestion in range(len(self._lsNewResponses)):
            
            # get the option responses for that question 
            #    (eg. for a checkbox question, there may be 3 options 'yes' 'no' 'maybe')
            lsQuestionResponses = self._lsNewResponses[indQuestion]


            # if the list of responses was empty (only a partial number of questions were answered), don't write
            if len(lsQuestionResponses) > 0:
            
                # for each option in the question
                for indOption in range(len(lsQuestionResponses)):
                    
                    # capture the xml node for the option
                    xOptionNode = self.GetNthOptionNode( indQuestion, indOption)
                     
                    if not xOptionNode == None:
                        # write the response to the xml 
                        self.AddResponseElement(xOptionNode, lsQuestionResponses[indOption])
                
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddResponseElement(self, xOptionNode, sResponse):
        
        now = datetime.now()
        sResponseTime = now.strftime(self.oIOXml.sTimestampFormat)
        
        dictAttrib = { 'LoginTime': self.LoginTime(), 'ResponseTime': sResponseTime}
        
        self.oIOXml.AddElement(xOptionNode,'Response', sResponse, dictAttrib)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddImageStateElement(self, xImageNode, dictAttrib):
        """ Add the image state element to the xml file including window/level
            and slice offset. 
        """

        sNullData = ''

        # add login and response times to the existing state attributes
        now = datetime.now()
        sResponseTime = now.strftime(self.oIOXml.sTimestampFormat)
        
        dictTimeAttributes = { 'LoginTime': self.LoginTime(), 'ResponseTime': sResponseTime} 
        dictAttrib.update(dictTimeAttributes)

        self.oIOXml.AddElement(xImageNode,'State', sNullData, dictAttrib)
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddPathElement(self, sElementName, xImageNode, sInputPath):
        
        # add login and response times to the label map path element
        now = datetime.now()
        sResponseTime = now.strftime(self.oIOXml.sTimestampFormat)
        
        dictAttrib = { 'LoginTime': self.LoginTime(), 'ResponseTime': sResponseTime} 
        
        self.oIOXml.AddElement(xImageNode, sElementName, sInputPath, dictAttrib)
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddSessionLoginTimestamp(self):
        ''' Function to add an element holding the login time for the session.
            Set up the logout time attribute to be updated on each write.
            Also - record the user's name
        '''

        now = datetime.now()

        self.SetLoginTime( now.strftime(self.oIOXml.sTimestampFormat) )
        
        dictAttrib = {'LoginTime': self.LoginTime(), 'LogoutTime': self.LoginTime()}
        
        sNullText = ''
        
        self.oIOXml.AddElement(self.oIOXml.GetRootNode(),'Login', sNullText, dictAttrib)
        
        self.oIOXml.SaveXml(self.oFilesIO.GetUserQuizResultsPath())
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def UpdateSessionLogoutTimestamp(self):
        ''' This function will add the attribute LogoutTime to the last entry of the Login element.
            Each time a 'Save' is done to the XML file, this Logout time will be overwritten.
            Then when the exit finally happens, it will reflect the last time a write was performed.
        '''

        now = datetime.now()

        sLogoutTime = now.strftime(self.oIOXml.sTimestampFormat)
        
        # get existing attributes from the Login element
        xLoginNode = self.oIOXml.GetLastChild(self.oIOXml.GetRootNode(), "Login")
        
        if xLoginNode != None:
            # update logout time if login element exists
            dictAttrib = self.oIOXml.GetAttributes(xLoginNode)
    
            dictAttrib['LogoutTime'] = sLogoutTime
                
            # reset the Login element
            self.oIOXml.UpdateAttributesInElement(xLoginNode, dictAttrib)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetNavigationIndexIfResumeRequired(self):
        ''' Scan the user's quiz file for existing responses in case the user
            exited the quiz prematurely (before it was complete) on the last login
        '''
        # We assume the quiz pages and question sets are presented sequentially as stored in the
        # composite navigation index (which takes into account randomization of the pages if requested)

            
        # initialize
        iResumeNavigationIndex = 0
        self.SetQuizResuming(False)
        iPageIndex = 0
        xPageNode = None
        # get last login - this will set if QuizComplete is true
        dtLastLogin = self.GetLastLoginTimestamp() # value in datetime format

        
        if self.GetQuizComplete():
            # quiz does not allow for changing responses - review is allowed
            sMsg = 'Quiz has already been completed and responses cannot be modified.'\
                    + ' \nWould you like to review the quiz? '
            if self.GetEmailResultsRequest():
                sMsg = sMsg + '\n\nClick No to exit. You will have the option to email results.'
            else:
                sMsg = sMsg + '\n\nClick No to exit.'
                
            qtAns = self.oUtilsMsgs.DisplayYesNo(sMsg)

            if qtAns == qt.QMessageBox.Yes:
                iResumeNavigationIndex = 0
                iPageIndex = self.GetNavigationPage(iResumeNavigationIndex)
                self.SetupPageState(iPageIndex)
                
            else:
                self.ExitOnQuizComplete()
        else:        
    
            # loop through composite navigation index to search for the first page without a "PageComplete='Y'"
            for indNav in range(len(self.GetNavigationList())):
                if not self.GetQuizResuming():
                    iPageIndex = self.GetNavigationPage(indNav)
                    xPageNode = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', iPageIndex)
                    self.SetupPageState(iPageIndex)
                    
                    sPageComplete = self.oIOXml.GetValueOfNodeAttribute(xPageNode,'PageComplete')
                    if sPageComplete != 'Y':    # found first page that was not complete
                        iResumeNavigationIndex = indNav
                        self.SetQuizResuming(True)
            
            self.oPageState.UpdateCompletionLists(xPageNode)
            # adjust resuming index based on completion state of the first incomplete page
            #    (some question sets, if more than one exists, may have been completed)
            liCompletedQuestionSets = self.oPageState.GetCompletedQuestionSetsList()
            
            for indQSet in range(len(liCompletedQuestionSets)):
                # only advance if there are more question sets
                #    if the last question set has been reached and it is complete then 'PageComplete'
                #    was not set because the segmentation requirements were not met
                if indQSet < len(liCompletedQuestionSets) -1:
                    if liCompletedQuestionSets[indQSet] == 1:
                        iResumeNavigationIndex = iResumeNavigationIndex + 1
                
            # Display a message to user if resuming (special case if resuming on first page)
            # if not iResumeNavigationIndex == self.GetCurrentNavigationIndex():
            if (not iResumeNavigationIndex == self.GetCurrentNavigationIndex()) or\
                (iResumeNavigationIndex == 0 and dtLastLogin != ''):
                self.oUtilsMsgs.DisplayInfo('Resuming quiz from previous login session.')
                self.SetQuizResuming(True)
    
        self.SetCurrentNavigationIndex(iResumeNavigationIndex)
        # adjust if the resume question set is not the first on the page
        self.AdjustToCurrentQuestionSet()
        # reset the default order of image indices based on the new page
        self.InitializeImageDisplayOrderIndices()
    
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetLastLoginTimestamp(self):
        # function to scan the user's quiz file for all session login times
        # return the last session login time

        lsTimestamps = []
        dtLastTimestamp = ''    # timestamp of type 'datetime'

        
        xmlLoginNodes = self.oIOXml.GetChildren(self.oIOXml.GetRootNode(), 'Login')

        # collect all login timestamps (type 'string')
        for indElem in range(len(xmlLoginNodes)):
            # get date/time from attribute
            xmlLoginNode = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Login', indElem)

            sTimestamp = self.oIOXml.GetValueOfNodeAttribute(xmlLoginNode, 'LoginTime')
            lsTimestamps.append(sTimestamp)
            
            # look for Quiz Complete status
            sQuizCompleteStatus = self.oIOXml.GetValueOfNodeAttribute(xmlLoginNode, 'QuizComplete')
            if sQuizCompleteStatus == 'Y':
                self.SetQuizComplete(True)
            

        # loop through timestamps to search for the last login occurrence
        for indTime in range(len(lsTimestamps)):
            
            sNewTimestamp = lsTimestamps[indTime]
            # convert to datetime format for compare
            dtNewTimestamp = datetime.strptime(sNewTimestamp, self.oIOXml.sTimestampFormat)
            
            if dtLastTimestamp == '': # for initial compare
                dtLastTimestamp = dtNewTimestamp
                
            else:

                # update the last time stamp 
                if dtNewTimestamp > dtLastTimestamp:
                    dtLastTimestamp = dtNewTimestamp
                
                            
        return dtLastTimestamp
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ExitOnQuizComplete(self):
        """ the last index in the composite navigation indices list was reached
            the quiz was completed - exit
        """
        self.QueryThenSendEmailResults()
        self.oUtilsMsgs.DisplayInfo('Quiz Complete - Exiting')
        slicer.util.exit(status=EXIT_SUCCESS)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddQuizCompleteAttribute(self):
        ''' add attribute to last login element to indicate user has completed the quiz
        '''
        xmlLastLoginElement = self.oIOXml.GetLastChild(self.oIOXml.GetRootNode(),'Login')
        xmlLastLoginElement.set('QuizComplete','Y')
        self.oIOXml.SaveXml(self.oFilesIO.GetUserQuizResultsPath())

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def QueryThenSendEmailResults(self):
        
        if self.GetEmailResultsRequest() and self.GetQuizComplete():
            sMsg = 'Ready to email results?'
            qtEmailAns = self.oUtilsMsgs.DisplayYesNo(sMsg)
    
            if qtEmailAns == qt.QMessageBox.Yes:
    
                sArchiveFilenameWithPath = os.path.join(self.oFilesIO.GetUserDir(), self.oFilesIO.GetQuizFilenameNoExt())
                sPathToZipFile = self.oIOXml.ZipXml(sArchiveFilenameWithPath, self.oFilesIO.GetUserQuizResultsDir())
                
                if sPathToZipFile != '':
                    self.oUtilsEmail.SendEmail(sPathToZipFile)
                else:
                    sMsg = 'Trouble archiving quiz results: ' + sPathToZipFile
                    self.oUtilsMsgs.DisplayError(sMsg)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddPageCompleteAttribute(self, idxPage):
        ''' add attribute to current page element to indicate all 
            question sets and segmentations have been completed
        '''
        xmlCurrentPageElement = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(),'Page', idxPage)
        xmlCurrentPageElement.set('PageComplete','Y')
        self.oIOXml.SaveXml(self.oFilesIO.GetUserQuizResultsPath())

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddUserNameAttribute(self):
        ''' add attribute to Session to record the user's name
        '''
        xRootNode = self.oIOXml.GetRootNode()
        dictAttrib = self.oIOXml.GetAttributes(xRootNode)

        dictAttrib['UserName'] = self.oFilesIO.GetUsername()
            
        # reset the Login element
        self.oIOXml.UpdateAttributesInElement(xRootNode, dictAttrib)

        self.oIOXml.SaveXml(self.oFilesIO.GetUserQuizResultsPath())
        
##########################################################################
#
# class QuizWidgets
#
##########################################################################

class QuizWidgets:
    
    def __init__(self, oFilesIOInput, parent=None):
        self.sClassName = type(self).__name__
        self.parent = parent
#         print('Constructor for QuizWidgets')
        
        self.oFilesIO = oFilesIOInput
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



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
#         pixmapTarget = pixmap.scaled(pixmap.height()-430, pixmap.width()-430, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation);
#         qLogoImg.setPixmap(pixmapTarget)
        qLogoImg.setPixmap(pixmap)
        qLogoImg.setAlignment(QtCore.Qt.AlignCenter)

        qTitle = qt.QLabel('Baines Image Quizzer')
#         qTitle.setMinimumHeight(pixmap.height())
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

