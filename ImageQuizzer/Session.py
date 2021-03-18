import PythonQt
import os
import vtk, qt, ctk, slicer
import sys
import unittest

from Utilities import *
from Question import *
from ImageView import *
from UtilsIO import *
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
#         print('Constructor for Session')
        
        self._sLoginTime = ''

        self._iCurrentCompositeIndex = 0
        self._l2iPageQuestionCompositeIndices = []

        self._xPageNode = None
        self.sPageName = ''
        self.sPageDescriptor = ''
        
        self._loQuestionSets = []
        self._lsPreviousResponses = []
        self._lsNewResponses = []
        
        
        self._bFirstResponsesRecordedInXml = False
        self._bQuizComplete = False
        self._bAllowMultipleResponseInQuiz = True
        self._bAllowMultipleResponseInQSet = True      # for question set
        self._bSegmentationModule = False
        self._iSegmentationTabIndex = -1   # default
        
        self.oFilesIO = None
        self.oIOXml = UtilsIOXml()
        self.oUtilsMsgs = UtilsMsgs()

        self.oImageView = None
        
        self._btnNext = None
        self._btnPrevious = None


    def __del__(self):
        if not self.QuizComplete():
            self.oIOXml.SaveXml(self.oFilesIO.GetUserQuizResultsPath())
            self.oUtilsMsgs.DisplayInfo(' Image Quizzer Exiting - User file is saved.')

        # clean up of editor observers and nodes that may cause memory leaks (color table?)
        if self.GetSegmentationTabIndex() > 0:
            slicer.modules.quizzereditor.widgetRepresentation().self().exit()

        
    #-------------------------------------------
    #        Getters / Setters
    #-------------------------------------------

    #----------
    def SetFilesIO(self, oFilesIO):
        self.oFilesIO = oFilesIO

    #----------
#     def SetIOXml(self, oIOXml):
#         self.oIOXml = oIOXml

    #----------
    def SetQuizComplete(self, bInput):
        self._bQuizComplete = bInput
        
    #----------
    def QuizComplete(self):
        return self._bQuizComplete
            
    #----------
    def SetLoginTime(self, sTime):
        self._sLoginTime = sTime
        
    #----------
    def LoginTime(self):
        return self._sLoginTime
    
    #----------
    def SetCompositeIndicesList(self, lIndices):
        self._l2iPageQuestionCompositeIndices = lIndices
        
    #----------
    def CompositeIndicesList(self):
        return self._l2iPageQuestionCompositeIndices

    #----------
    def SetMultipleResponsesInQSetAllowed(self, bInput):
        
        self._bAllowMultipleResponseInQSet = bInput

    #----------
    def GetMultipleResponsesInQsetAllowed(self):
        return self._bAllowMultipleResponseInQSet
            
        
    #----------
    def SetMultipleResponsesInQuiz(self, bTF):
        # flag for quiz if any question sets allowed for multiple responses
        # this is used for 'resuming' after quiz was completed     
        self._bAllowMultipleResponseInQuiz = bTF
            
    #----------
    def GetMultipleResponsesInQuiz(self):
        return self._bAllowMultipleResponseInQuiz
            

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
    def GetNthQuestionSetForPage(self, idx):
        xPageNode = self.GetCurrentPageNode()
        xQuestionSetNode = self.oIOXml.GetNthChild(xPageNode, 'QuestionSet', idx)
        
        return xQuestionSetNode
        
    #----------
    def GetCurrentPageNode(self):
        iPageIndex = self._l2iPageQuestionCompositeIndices[self._iCurrentCompositeIndex][0]
        xPageNode = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', iPageIndex)
        
        return xPageNode
    
    #----------
    def GetCurrentPageIndex(self):
        return self._l2iPageQuestionCompositeIndices[self._iCurrentCompositeIndex][0]
    
    #----------
    def GetCurrentQuestionSetIndex(self):
        return self._l2iPageQuestionCompositeIndices[self._iCurrentCompositeIndex][1]
    
    #----------
    def GetCurrentQuestionSetNode(self):
        iQSetIndex = self._l2iPageQuestionCompositeIndices[self._iCurrentCompositeIndex][1]
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
    #----------

    #-------------------------------------------
    #        Functions
    #-------------------------------------------

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def RunSetup(self, oFilesIO, slicerMainLayout):
        
#         self.oIOXml = UtilsIOXml()
        self.SetFilesIO(oFilesIO)

        # open xml and check for root node
        bSuccess, xRootNode = self.oIOXml.OpenXml(self.oFilesIO.GetUserQuizResultsPath(),'Session')

        if not bSuccess:
            sErrorMsg = "ERROR", "Not a valid quiz - Root node name was not 'Session'"
            self.oUtilsMsgs.DisplayError(sErrorMsg)

        else:

#             self.AddSessionLoginTimestamp()

            self.SetupWidgets(slicerMainLayout)
            self.oQuizWidgets.qLeftWidget.activateWindow()

            
            # turn on functionality if any of the question set attributes indicated they are required
            self.SetMultipleResponsesInQuiz( \
                self.oIOXml.CheckForRequiredFunctionalityInAttribute( \
                './/Page/QuestionSet', 'AllowMultipleResponse','Y'))
            self.AddSegmentationModule( \
                self.oIOXml.CheckForRequiredFunctionalityInAttribute( \
                './/Page/QuestionSet', 'SegmentRequired','Y'))
            
            # set up ROI colors for segmenting
#             self.oUtilsIO.SetResourcesROIColorFilesDir()
            sColorFileName = self.oIOXml.GetValueOfNodeAttribute(xRootNode, 'ROIColorFile')
            self.oFilesIO.SetupROIColorFile(sColorFileName)


        self.BuildPageQuestionCompositeIndexList()
        # check for partial or completed quiz
        self.SetCompositeIndexIfResumeRequired()
        
        self.progress.setMaximum(len(self._l2iPageQuestionCompositeIndices))
        self.progress.setValue(self._iCurrentCompositeIndex)

        # if quiz is not complete, finish setup
        #    (the check for resuming the quiz may have found it was already complete)
        if not self.QuizComplete():
            # setup buttons and display
            self.EnableButtons()
            self.DisplayPage()


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetupWidgets(self, slicerMainLayout):


        self.oQuizWidgets = QuizWidgets(self.oFilesIO)
        self.oQuizWidgets.CreateLeftLayoutAndWidget()

        
        self.SetupButtons()
        self.oQuizWidgets.qLeftLayout.addWidget(self.qButtonGrpBox)

        self.oQuizWidgets.AddQuizLayoutWithTabs()
        
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
        self._btnNext.setStyleSheet("QPushButton{ background-color: rgb(0,179,246) }")
        self._btnNext.connect('clicked(bool)',self.onNextButtonClicked)
        
        # Back button
        self._btnPrevious = qt.QPushButton("Previous")
        self._btnPrevious.toolTip = "Display previous set of questions."
        self._btnPrevious.enabled = True
        self._btnPrevious.setStyleSheet("QPushButton{ background-color: rgb(255,149,0) }")
        self._btnPrevious.connect('clicked(bool)',self.onPreviousButtonClicked)


        # Exit button
        self._btnExit = qt.QPushButton("Exit")
        self._btnExit.toolTip = "Save quiz and exit Slicer."
        self._btnExit.enabled = True
        self._btnExit.setStyleSheet("QPushButton{ background-color: rgb(255,0,0) }")
        # use lambda to pass argument to this PyQt slot without invoking the function on setup
        self._btnExit.connect('clicked(bool)',lambda: self.onExitButtonClicked('ExitBtn'))


        self.qButtonGrpBoxLayout.addWidget(self._btnExit)
        self.qButtonGrpBoxLayout.addWidget(qProgressLabel)
        self.qButtonGrpBoxLayout.addWidget(self.progress)
        self.qButtonGrpBoxLayout.addWidget(self._btnPrevious)
        self.qButtonGrpBoxLayout.addWidget(self._btnNext)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onNextButtonClicked(self):
        
        bSuccess = True
        sMsg = ''

        if self._iCurrentCompositeIndex + 1 == len(self._l2iPageQuestionCompositeIndices):

            # the last question was answered - check if user is ready to exit
            self.onExitButtonClicked('Finish') # a save is done in here
            
            # the user may have cancelled the 'finish'
            # bypass remainder of the 'next' button code

        else:
            # this is not the last question set, do a save and display the next page
            bSuccess, sMsg = self.PerformSave('NextBtn')
            
            if bSuccess:
    
    
                ########################################    
                # set up for next page
                ########################################    
                
                # if last question set, clear list and scene
                if self.CheckForLastQuestionSetForPage() == True:
                    self._loQuestionSets = []
# REMOVE FOR THREADING??                    slicer.mrmlScene.Clear()
                    slicer.mrmlScene.Clear()
                else:
                    # clear quiz widgets only
                    for i in reversed(range(self.oQuizWidgets.qQuizLayout.count())):
                        self.oQuizWidgets.qQuizLayout.itemAt(i).widget().setParent(None)
            
                self._iCurrentCompositeIndex = self._iCurrentCompositeIndex + 1
                self.progress.setValue(self._iCurrentCompositeIndex)
                    
                self.EnableButtons()
       
                self.DisplayPage()
    
            else:
                if sMsg != '':
                    self.oUtilsMsgs.DisplayWarning( sMsg )
                
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onPreviousButtonClicked(self):
        
        bSuccess = True
        sMsg = ''

        bSuccess, sMsg = self.PerformSave('PreviousBtn')
        
        if bSuccess:

            ########################################    
            # set up for previous page
            ########################################    

# REMOVE FOR THREADING??            slicer.mrmlScene.Clear()
            slicer.mrmlScene.Clear()
            self._iCurrentCompositeIndex = self._iCurrentCompositeIndex - 1
            self.progress.setValue(self._iCurrentCompositeIndex)
    
            if self._iCurrentCompositeIndex < 0:
                # reset to beginning
                self._iCurrentCompositeIndex = 0
            
            self.EnableButtons()
            
            self.AdjustForPreviousQuestionSets()
            
            
            self.DisplayPage()
               
        
        else:
            if sMsg != '':
                self.oUtilsMsgs.DisplayWarning( sMsg )
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onExitButtonClicked(self,sCaller):

        self.progress.setValue(self._iCurrentCompositeIndex + 1)
        iProgressPercent = int((self._iCurrentCompositeIndex + 1) / len(self._l2iPageQuestionCompositeIndices) * 100)
        self.progress.setFormat(self.sPageName + '  ' + self.sPageDescriptor + '    ' + str(iProgressPercent) + '%')
        
        sMsg = 'Do you wish to exit?'
        if sCaller == 'ExitBtn':
            sMsg = sMsg + ' \nYour responses will be saved. Quiz may be resumed.'

        qtAns = self.oUtilsMsgs.DisplayOkCancel(sMsg)
        if qtAns == qt.QMessageBox.Ok:
            bSuccess, sMsg = self.PerformSave(sCaller)
            if bSuccess:
                slicer.util.exit(status=EXIT_SUCCESS)
            else:
                if sMsg != '':
                    self.oUtilsMsgs.DisplayWarning( sMsg )

        # if code reaches here, either the exit was cancelled or there was 
        # an error in the save
        self.progress.setValue(self._iCurrentCompositeIndex)
        iProgressPercent = int(self._iCurrentCompositeIndex / len(self._l2iPageQuestionCompositeIndices) * 100)
        self.progress.setFormat(self.sPageName + '  ' + self.sPageDescriptor + '    ' + str(iProgressPercent) + '%')

        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def EnableButtons(self):
        
        # assume not at the end of the quiz
        self._btnNext.setText("Next")
        
        # beginning of quiz
        if (self._iCurrentCompositeIndex == 0):
            self._btnNext.enabled = True
            self._btnPrevious.enabled = False

        # end of quiz
        elif (self._iCurrentCompositeIndex == len(self._l2iPageQuestionCompositeIndices) - 1):
            self._btnNext.enabled = True
            self._btnPrevious.enabled = True

        # somewhere in middle
        else:
            self._btnNext.enabled = True
            self._btnPrevious.enabled = True


        # assign button description           
        if (self._iCurrentCompositeIndex == len(self._l2iPageQuestionCompositeIndices) - 1):
            # last question of last image view
            self._btnNext.setText("Finish")
# 
#         else:
#             # assume multiple questions in the question set
#             self._btnNext.setText("Next")
#             # if last question in the question set - save answers and continue to next
#             if not( self._l2iPageQuestionCompositeIndices[self._iCurrentCompositeIndex][0] == self._l2iPageQuestionCompositeIndices[self._iCurrentCompositeIndex + 1][0]):
#                 self._btnNext.setText("Save and Continue")

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def BuildPageQuestionCompositeIndexList(self):
        
        # This function sets up the page and question set indices which
        #    are used to coordinate the next and previous buttons.
        #    The information is gathered by querying the XML quiz.
        
        # given the root of the xml document build composite list 
        #     of indeces for each page and the question sets within
        
        # get Page nodes
        xPages = self.oIOXml.GetChildren(self.oIOXml.GetRootNode(), 'Page')

        for iPageIndex in range(len(xPages)):
            
            # for each page - get number of question sets
            xPageNode = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', iPageIndex)
            xQuestionSets = self.oIOXml.GetChildren(xPageNode,'QuestionSet')
            
            # append to composite indices list
            for iQuestionSetIndex in range(len(xQuestionSets)):
                self._l2iPageQuestionCompositeIndices.append([iPageIndex, iQuestionSetIndex])
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def DisplayPage(self):

        # extract page and question set indices from the current composite index
        
        xNodeQuestionSet = self.GetCurrentQuestionSetNode()
        oQuestionSet = QuestionSet()
        oQuestionSet.ExtractQuestionsFromXML(xNodeQuestionSet)
        
        sQuestionsWithRecordedResponses = self.GetQuestionSetResponseCompletionLevel()
        self.SetMultipleResponsesInQSetAllowed(oQuestionSet.GetMultipleResponseTF())

        if self.GetSegmentationTabIndex() > 0:
            
            if oQuestionSet.GetMultipleResponseTF() == True:
                self.SegmentationTabEnabler(oQuestionSet.GetSegmentRequiredTF())
            else:
                # When multiple responses are not allowed, 
                #    enable the segmentation tab only if the segments are required and
                #    the number of questions with responses is not All (ie. either None or Partial)
                
                if (sQuestionsWithRecordedResponses == 'All'):
                    self.SegmentationTabEnabler(False)
                else:
                    self.SegmentationTabEnabler(oQuestionSet.GetSegmentRequiredTF())


        # first clear any previous widgets (except push buttons)
        for i in reversed(range(self.oQuizWidgets.qQuizLayout.count())):
#             x = self.slicerQuizLayout.itemAt(i).widget()
#             if not(isinstance(x, qt.QPushButton)):
            self.oQuizWidgets.qQuizLayout.itemAt(i).widget().setParent(None)

        
        bBuildSuccess, qWidgetQuestionSetForm = oQuestionSet.BuildQuestionSetForm()
        
        if bBuildSuccess:
            self.oQuizWidgets.qQuizLayout.addWidget(qWidgetQuestionSetForm)
            self._loQuestionSets.append(oQuestionSet)
            qWidgetQuestionSetForm.setEnabled(True) # initialize



            # enable widget if not all questions have responses or if user is allowed to 
            # input multiple responses
            if sQuestionsWithRecordedResponses == 'All':
                qWidgetQuestionSetForm.setEnabled(self.GetMultipleResponsesInQsetAllowed())
            if sQuestionsWithRecordedResponses == 'All' or sQuestionsWithRecordedResponses == 'Partial':
                self.DisplaySavedResponse()

                   
        # set the layout to default view 
#         slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
        slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutTwoOverTwoView)
        
        # add page name/descriptor to the progress bar
        xmlPageNode = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', self.GetCurrentPageIndex())
        self.sPageDescriptor = self.oIOXml.GetValueOfNodeAttribute(xmlPageNode, 'Descriptor')
        self.sPageName = self.oIOXml.GetValueOfNodeAttribute(xmlPageNode, 'Name')
        iProgressPercent = int(self._iCurrentCompositeIndex / len(self._l2iPageQuestionCompositeIndices) * 100)
        self.progress.setFormat(self.sPageName + '  ' + self.sPageDescriptor + '    ' + str(iProgressPercent) + '%')
                    
        # set up the images on the page
        self.oImageView = ImageView()
        self.oImageView.RunSetup(self.GetCurrentPageNode(), qWidgetQuestionSetForm, self.oFilesIO.GetDataParentDir())

        # load label maps if a labelmap path has been stored in the xml for the images on this page
        self.oFilesIO.LoadSavedLabelMaps(self)

        # assign each image node and its label map (if applicable) to the viewing widget
        self.oImageView.AssignNodesToView()
        
        self.SetSavedImageState() # after loading label maps and setting assigning views
        
        if self.GetSegmentationTabIndex() > 0:
            # clear Master and Merge selector boxes
            oQuizzerEditorHelperBox = slicer.modules.quizzereditor.widgetRepresentation().self().GetHelperBox()
            oQuizzerEditorHelperBox.setMasterVolume(None)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CheckForLastQuestionSetForPage(self):
        bLastQuestionSet = False
        
        # check if at the end of the quiz
        if (self._iCurrentCompositeIndex == len(self._l2iPageQuestionCompositeIndices) - 1):
            bLastQuestionSet = True

        else:
            # we are not at the end of the quiz
            # assume multiple question sets for the page
            # check if next page in the composite index is different than the current page
            #    if yes - we have reached the last question set
            if not( self._l2iPageQuestionCompositeIndices[self._iCurrentCompositeIndex][0] == self._l2iPageQuestionCompositeIndices[self._iCurrentCompositeIndex + 1][0]):
                bLastQuestionSet = True            
           
            
        return bLastQuestionSet
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AdjustForPreviousQuestionSets(self):
        
        # if there are multiple question sets for a page, the list of question sets must
        #    include all previous question sets - up to the one being displayed
        #    (eg. if a page has 4 Qsets, and we are going back to Qset 3,
        #    we need to collect question set indices 0, and 1 first,
        #    then continue processing for index 2 which will be appended in Display Page)
        
        # This function is called when the previous button is pressed or if a
        # resume is required into a question set that is not the first for the page.
        
        self._loQuestionSets = [] # initialize
        indQSet = self.GetCurrentQuestionSetIndex()

        if indQSet > 0:

            for idx in range(indQSet):
                xNodeQuestionSet = self.GetNthQuestionSetForPage(idx)
                oQuestionSet = QuestionSet()
                oQuestionSet.ExtractQuestionsFromXML(xNodeQuestionSet)
                self._loQuestionSets.append(oQuestionSet)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def PerformSave(self, sCaller):
        """ Actions performed here include:
            - save the label maps (done before saving the collected quiz responses)
            - write the collected responses to the xml
            - capture and write the state of the images (window/level and slice offset) to xml
        """
        
        sMsg = ''
        bSuccess = True
        
        bSuccess, sMsg = self.ResetDisplay()
        
        if bSuccess:
            
            # Saving the label maps becomes part of the success level ('all', 'partial' 
            # or 'none) for capturing all of the required pieces for the question set
            # (responses and label maps). The label maps therefore must be saved
            # prior to capturing the responses
            bSuccess, sMsg = self.oFilesIO.SaveLabelMaps(self, sCaller)
        

            if bSuccess:
                sCaptureSuccessLevel, self._lsNewResponses, sMsg = self.CaptureResponsesForQuestionSet(sCaller)

                if sCaller == 'NextBtn' or sCaller == 'Finish':
                    # only write to xml if all responses were captured
                    if sCaptureSuccessLevel == 'All':
                        bSuccess, sMsg = self.WriteResponsesToXml()
                    else:
                        bSuccess = False
                        
                else:  
                    # Caller must have been the Previous or Exit buttons or a close was 
                    #     requested (which triggers the event filter)
                    # Only write if there were responses captured
                    if sCaptureSuccessLevel == 'All' or sCaptureSuccessLevel == 'Partial':
                        bSuccess, sMsg = self.WriteResponsesToXml()
                    else:
                        # if no responses were captured 
                        if sCaptureSuccessLevel == 'None':
                            # this isn't the Next button so it is allowed
                            bSuccess = True
                        
                if bSuccess:
                    #after writing responses, record the image state
                    bSuccess, sMsg = self.CaptureAndSaveImageState()

        # let calling program handle display of message if not successful            
        return bSuccess, sMsg
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ResetDisplay(self):
        
        bSuccess = True
        sMsg = ''

        try:
            # before leaving the page, if the segmentation is enabled, restore mouse to default cursor
            if self.GetSegmentationTabIndex() > 0:
                # if Segmentation editor tab exists
                
                #collapse label editor to encourage selection of master volume
                slicer.modules.quizzereditor.widgetRepresentation().self().updateLabelFrame(None)
    #             oQuizzerEditorHelperBox.SetCustomColorTable()
                
                # reset display to quiz tab
                self.oQuizWidgets.qTabWidget.setCurrentIndex(0)
                slicer.modules.quizzereditor.widgetRepresentation().self().toolsBox.selectEffect('DefaultTool')
            
        except:
            bSuccess = False
            sMsg = 'Reset segmentation state error'
            
        return bSuccess, sMsg
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CaptureAndSaveImageState(self):

        sMsg = ''
        bSuccess = True
        
        try:
            # for each image, capture the slice, window and level settings
            for oImageNode in self.oImageView.GetImageViewList():
                if (oImageNode.sImageType == 'Volume' or oImageNode.sImageType == 'VolumeSequence'):
    
                    dictAttribState = oImageNode.GetViewState()
    
                    # check if xml State element exists
                    xImage = oImageNode.GetXmlImageElement()
                    iNumStateElements = self.oIOXml.GetNumChildrenByName(xImage, 'State')

                    # add image state element (tagged with response time)
                    self.AddImageStateElement(xImage, dictAttribState)
                        
            self.oIOXml.SaveXml(self.oFilesIO.GetUserQuizResultsPath())
    
        except:
            bSuccess = False
            sMsg = 'Error saving the image state'
            
        return bSuccess, sMsg
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetSavedImageState(self):
        """ From the xml file, get the image state element. If there was no state element, 
            check the xml for a previously stored state for this image. (eg. if clinician
            set the window/level for an image on one page, and that same image is loaded on a subsequent page,
            the same window/level should be applied. 
        """
        
        for oImageNode in self.oImageView.GetImageViewList():
            dictImageState = {}
            if (oImageNode.sImageType == 'Volume' or oImageNode.sImageType == 'VolumeSequence'):
        
                xStateElement = self.oIOXml.GetLatestChildElement(oImageNode.GetXmlImageElement(), 'State')
                
                if xStateElement != None:
                    dictImageState = self.oIOXml.GetAttributes(xStateElement)
                else:
                    xHistoricalStateElement = self.CheckXmlImageHistoryForMatch(oImageNode.GetXmlImageElement(), 'State')
                    if xHistoricalStateElement != None:
                        dictImageState = self.oIOXml.GetAttributes(xHistoricalStateElement)
                    
                if len(dictImageState) > 0:
                    oImageNode.SetImageState(dictImageState)
            
            
    

            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CaptureResponsesForQuestionSet(self, sCaller):
        
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
        if iNumMissingResponses == 0:
            sCaptureSuccessLevel = 'All'
        elif iNumMissingResponses == len(lsAllResponses):
            sCaptureSuccessLevel = 'None'
        else:
            sCaptureSuccessLevel = 'Partial'
            
                
        return sCaptureSuccessLevel, lsAllResponses, sAllMsgs
       

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CheckForSavedResponse(self):

        """ Check through all questions for the question set looking for a response.
            If the Question Set has a "SegmentRequired='Y'" attribute, 
            check for a saved label map path element. 

            Assume: All options have a response if the question was answered so we just query the first.
        """
        bLabelMapRequirementFilled = False
        iNumAnsweredQuestions = 0
        
        xNodeQuestionSet = self.GetCurrentQuestionSetNode()
        xNodePage = self.GetCurrentPageNode()
        
        sLabelMapRequired = self.oIOXml.GetValueOfNodeAttribute(xNodeQuestionSet, 'SegmentRequired')

        # search for labelmap path in the xml image nodes if segmentation was required
        if sLabelMapRequired == 'y':
            iNumImages = self.oIOXml.GetNumChildrenByName(xNodePage, 'Image')
            for indImage in range(iNumImages):
                xImageNode = self.oIOXml.GetNthChild(xNodePage, 'Image', indImage)
                iNumLabelMapPaths = self.oIOXml.GetNumChildrenByName(xImageNode, 'LabelMapPath')
                if iNumLabelMapPaths > 0:
                    bLabelMapRequirementFilled = True
                    break
        else:
            bLabelMapRequirementFilled = True   # user not required to create label map
        


        iNumQuestions = self.oIOXml.GetNumChildrenByName(xNodeQuestionSet, 'Question')

        for indQuestion in range(iNumQuestions):
             
            xOptionNode = self.GetNthOptionNode( indQuestion, 0)
         
            iNumResponses = self.oIOXml.GetNumChildrenByName(xOptionNode,'Response')
            if iNumResponses >0:
                iNumAnsweredQuestions = iNumAnsweredQuestions + 1
                 
                
        if iNumAnsweredQuestions == 0:
            sQuestionswithResponses = 'None'
        elif  iNumAnsweredQuestions < iNumQuestions:
            sQuestionswithResponses = 'Partial'
        elif iNumAnsweredQuestions == iNumQuestions and bLabelMapRequirementFilled == True:
            sQuestionswithResponses = 'All'
        else:
            if iNumAnsweredQuestions == iNumQuestions and bLabelMapRequirementFilled == False:
                sQuestionswithResponses = 'Partial'
            
        return sQuestionswithResponses
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetQuestionSetResponseCompletionLevel(self, indCI=None):
        
        """ Check through all questions for the question set looking for a response.
            If the Question Set has a "SegmentRequired='Y'" attribute, 
            check for a saved label map path element. 

            Assumption: All options have a response if the question was answered
            so we just query the first. 
            eg: Radio Question     Success?
                    Opt 1            yes
                        response:       y (checked)
                    Opt 2            no
                        response:       n (not checked)
        """
        
        if indCI == None:
            indCI = self._iCurrentCompositeIndex
        
        bLabelMapRequirementFilled = False
        iNumAnsweredQuestions = 0
        
        indPage = self._l2iPageQuestionCompositeIndices[indCI][0]
        indQuestionSet = self._l2iPageQuestionCompositeIndices[indCI][1]
        
        xPageNode = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', indPage)
        xQuestionSetNode = self.oIOXml.GetNthChild(xPageNode, 'QuestionSet', indQuestionSet)
        
        
        sLabelMapRequired = self.oIOXml.GetValueOfNodeAttribute(xQuestionSetNode, 'SegmentRequired')

        # search for labelmap path in the xml image nodes if segmentation was required
        if sLabelMapRequired == 'y':
            iNumImages = self.oIOXml.GetNumChildrenByName(xPageNode, 'Image')
            for indImage in range(iNumImages):
                xImageNode = self.oIOXml.GetNthChild(xPageNode, 'Image', indImage)
                iNumLabelMapPaths = self.oIOXml.GetNumChildrenByName(xImageNode, 'LabelMapPath')
                if iNumLabelMapPaths > 0:
                    bLabelMapRequirementFilled = True
                    break
        else:
            bLabelMapRequirementFilled = True   # user not required to create label map
        


        iNumQuestions = self.oIOXml.GetNumChildrenByName(xQuestionSetNode, 'Question')

        for indQuestion in range(iNumQuestions):
            # get first option for the question (all (or none) options have a response so just check the first)
            xQuestionNode = self.oIOXml.GetNthChild(xQuestionSetNode, 'Question', indQuestion)
            xOptionNode = self.oIOXml.GetNthChild(xQuestionNode, 'Option', 0)
         
            iNumResponses = self.oIOXml.GetNumChildrenByName(xOptionNode,'Response')
            if iNumResponses >0:
                iNumAnsweredQuestions = iNumAnsweredQuestions + 1
                 
                
        if iNumAnsweredQuestions == 0:
            sQuestionswithResponses = 'None'
        elif  iNumAnsweredQuestions < iNumQuestions:
            sQuestionswithResponses = 'Partial'
        elif iNumAnsweredQuestions == iNumQuestions and bLabelMapRequirementFilled == True:
            sQuestionswithResponses = 'All'
        else:
            if iNumAnsweredQuestions == iNumQuestions and bLabelMapRequirementFilled == False:
                sQuestionswithResponses = 'Partial'
            
        return sQuestionswithResponses
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetFolderNameForLabelMaps(self):
        """ Label maps are stored in a directory where the name is derived from the 
            current page of the Session.
        """
        
        # get page info to create directory
        xPageNode = self.GetCurrentPageNode()
        sPageIndex = str(self.GetCurrentPageIndex() + 1)
        sPageName = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'Name')
        sPageDescriptor = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'Descriptor')
         
        sDirName = os.path.join(self.oFilesIO.GetUserQuizResultsDir(), 'Pg'+ sPageIndex + '_' + sPageName + '_' + sPageDescriptor)

        return sDirName
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CheckXmlImageHistoryForMatch(self, xImageNodeToMatch, sChildTagName):  
        """ Start searching the xml file for a matching image on a previous page
            (based on path and series instance UID (if applicable),
            and extract the required child.
            The most recent element will be returned.
        """
        xHistoricalChildElement = None
        
        xPathElement = self.oIOXml.GetNthChild(xImageNodeToMatch, 'Path', 0)
        sPathToMatch = self.oIOXml.GetDataInNode(xPathElement)
        
        # check if there is a SeriesInstanceUID element (in the case of a dicom type of image)
        sSeriesInstanceUIDToMatch = ''
        xSeriesInstanceUIDElement = self.oIOXml.GetNthChild(xImageNodeToMatch, 'SeriesInstanceUID', 0)
        if xSeriesInstanceUIDElement != None:
            sSeriesInstanceUIDToMatch = self.oIOXml.GetDataInNode(xSeriesInstanceUIDElement)
        
        
        # start searching pages in reverse order - to get most recent setting
        # first match will end the search
        bHistoricalElementFound = False
        for iPageIndex in range(self.GetCurrentPageIndex()-1, -1, -1):
            xPageNode = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', iPageIndex)
            
            if bHistoricalElementFound == False:
                #get all Image children
                lxImageElementsToSearch = self.oIOXml.GetChildren(xPageNode, 'Image')
                if len(lxImageElementsToSearch) > 0:
    
                    for xImageNode in lxImageElementsToSearch:
    
                        xPotentialPathElement = self.oIOXml.GetNthChild(xImageNode, 'Path', 0)
                        sPotentialPath = self.oIOXml.GetDataInNode(xPotentialPathElement)
                        
                        # get series instance UID if it exists
                        sPotentialSeriesInstanceUID = ''
                        xPotentialSeriesInstanceUID = self.oIOXml.GetNthChild(xImageNode, 'SeriesInstanceUID', 0)
                        if xPotentialSeriesInstanceUID != None:
                            sPotentialSeriesInstanceUID = self.oIOXml.GetDataInNode(xPotentialSeriesInstanceUID)
                        
                        # test for match of both the Path and Series Instance UID
                        if sPotentialPath == sPathToMatch and sPotentialSeriesInstanceUID == sSeriesInstanceUIDToMatch:
#                             print('found prior image instance: ', iPageIndex, ' ', sPotentialPath)
                            
                            # capture most recent (based on response time) historical element of interest
                            xHistoricalChildElement = self.oIOXml.GetLatestChildElement(xImageNode, sChildTagName)
                            bHistoricalElementFound = True
                        
        
        return xHistoricalChildElement

        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def DisplaySavedResponse(self):


        xNodeQuestionSet = self.GetCurrentQuestionSetNode()
        indQSet = self.GetCurrentQuestionSetIndex()
 
        oQuestionSet = self._loQuestionSets[indQSet]


        loQuestions = oQuestionSet.GetQuestionList()
         
        # for each question and each option, extract any existing responses from the XML
         
        lsAllResponsesForQuestion = []
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
#                 print('************Data...%s***END***' % sLatestResponse)
                lsResponseValues.append(sLatestResponse)
                
            oQuestion.PopulateQuestionWithResponses(lsResponseValues)

            lsAllResponsesForQuestion.append(lsResponseValues)
            
    
            lsResponseValues = []  # clear for next set of options 

        self._lsPreviousResponses = lsAllResponsesForQuestion
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def WriteResponsesToXml(self):
        """ Write captured responses to xml. If this is the first write to the xml
            with responses, the login timestamp is also added.
            After responses are added, record the image state in the xml file.
        """
        
        bSuccess = True
        sMsg = ''
        
        try:
            
            # only allow for writing of responses under certain conditions
            #    - allow if the question set is marked for multiple responses allowed
            #    - OR allow if the number of questions with responses already 
            #      recorded is 'none' or 'partial' (not 'all')
            
#             sQuestionsWithRecordedResponses = self.CheckForSavedResponse()
            sQuestionsWithRecordedResponses = self.GetQuestionSetResponseCompletionLevel()

            if ( self.GetMultipleResponsesInQsetAllowed() == True)  or \
                ((self.GetMultipleResponsesInQsetAllowed() == False) and (sQuestionsWithRecordedResponses != 'All') ):

                # check to see if the responses for the question set match 
                #    what was previously captured
                #    -only write responses if they have changed
                if not self._lsNewResponses == self._lsPreviousResponses:
                    # Responses have been captured, if it's the first set of responses
                    #    for the session, add in the login timestamp
                    #    The timestamp is added here in case the user exited without responding to anything,
                    #    allowing for the resume check to function properly
                    if self._bFirstResponsesRecordedInXml == False:
                        self.AddSessionLoginTimestamp()
                        self._bFirstResponsesRecordedInXml = True
                    self.AddXmlElements()
                    self.oIOXml.SaveXml(self.oFilesIO.GetUserQuizResultsPath())
                    
        
        except:
            bSuccess = False
            sMsg = 'Error writing responses to Xml'
            
        return bSuccess, sMsg
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddXmlElements(self):
        
        # using the list of question set responses, isolate respones for each question
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
#             Only add if user has already made a change to the quiz responses. 
#             (ie. ignore if user briefly opens quiz and closes it again)
#         """
#         if self._bFirstChangeRecordedInXml:

        sNullData = ''

        # add login and response times to the existing state attributes
        now = datetime.now()
        sResponseTime = now.strftime(self.oIOXml.sTimestampFormat)
        
        dictTimeAttributes = { 'LoginTime': self.LoginTime(), 'ResponseTime': sResponseTime} 
        dictAttrib.update(dictTimeAttributes)

        self.oIOXml.AddElement(xImageNode,'State', sNullData, dictAttrib)
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddLabelMapPathElement(self, xImageNode, sInputPath):
        
        # add login and response times to the label map path element
        now = datetime.now()
        sResponseTime = now.strftime(self.oIOXml.sTimestampFormat)
        
        dictAttrib = { 'LoginTime': self.LoginTime(), 'ResponseTime': sResponseTime} 
        
        self.oIOXml.AddElement(xImageNode,'LabelMapPath',sInputPath, dictAttrib)
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddSessionLoginTimestamp(self):
        

        now = datetime.now()

        self.SetLoginTime( now.strftime(self.oIOXml.sTimestampFormat) )
        
        dictAttrib = {'LoginTime': self.LoginTime()}
        
        sNullText = ''
        
        self.oIOXml.AddElement(self.oIOXml.GetRootNode(),'Login', sNullText, dictAttrib)
        
        self.oIOXml.SaveXml(self.oFilesIO.GetUserQuizResultsPath())
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetCompositeIndexIfResumeRequired(self):
        # Scan the user's quiz file for existing responses in case the user
        #     exited the quiz prematurely (before it was complete) on the last login
        #
        # The following assumptions are made based on the quiz flow:
        #    - the quiz pages and question sets are presented sequentially 
        #        as laid out in the quiz file
        #    - it is possible to exit the quiz with not all questions answered (a partial response)
        #        we have to find the first question set that has all questions answered
        #    - if a question was answered, all options within the question have a response tag
        #        but, there may be more than one response tag
        #
        # By looping through the page/question set indices stored in the
        #    composite index array in reverse, we scan all questions for an existing response
        #    that matches the last login session time.
        #    If the number of questions with the correct response times = total number of questions,
        #    add one to the current index to resume (all questions were answered).
        #    Otherwise, only a partial number of questions were answered so stay on this index.



        # initialize
        dtLastLogin = self.GetLastLoginTimestamp() # value in datetime format
        iResumeCompIndex = 0
        
        
        # loop through composite index in reverse, to search for existing responses that match
        #    last login time (prior to current login)

        for indCI in reversed(range(len(self._l2iPageQuestionCompositeIndices))):
#             print(indCI)
            
            bLastLoginResponseFound = False # default
            
            # get page and question set nodes from indices
            indPage = self._l2iPageQuestionCompositeIndices[indCI][0]
            indQuestionSet = self._l2iPageQuestionCompositeIndices[indCI][1]
            xPageNode = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', indPage)
            xQuestionSetNode = self.oIOXml.GetNthChild(xPageNode, 'QuestionSet', indQuestionSet)
#             print(indCI, 'Page:', indPage, 'QS:', indQuestionSet)
            


            # get number of questions in the question set node
            iNumQuestions = self.oIOXml.GetNumChildrenByName(xQuestionSetNode, 'Question')
            iNumLastLoginResponses = 0
            
            # scan all questions
            for indQuestion in range(iNumQuestions):

                # get first Option node of each Question
                xQuestionNode = self.oIOXml.GetNthChild(xQuestionSetNode, 'Question', indQuestion)
                xOptionNode = self.oIOXml.GetNthChild(xQuestionNode, 'Option', 0)
                
                # get number of Response nodes in the option
                iNumResponses = self.oIOXml.GetNumChildrenByName(xOptionNode, 'Response')
            
                
                # check each response tag for the time
                for indResp in range(iNumResponses):
                    xResponseNode = self.oIOXml.GetNthChild(xOptionNode, 'Response', indResp)
                    sTimestamp = self.oIOXml.GetValueOfNodeAttribute(xResponseNode, 'LoginTime')
    
                    dtLoginTimestamp = datetime.strptime(sTimestamp, self.oIOXml.sTimestampFormat)
                    if dtLoginTimestamp == dtLastLogin:
                        # found a response for last login at this composite index
                        bLastLoginResponseFound = True
                        iNumLastLoginResponses = iNumLastLoginResponses + 1
                        break   # exit checking each response
                
                
                
            if bLastLoginResponseFound == True:
                break   # exit the reversed loop through the composite indices



            
        if bLastLoginResponseFound == True:
            
            sQSetCompletionState = self.GetQuestionSetResponseCompletionLevel(indCI)
            
            # check if the last response found was entered on the last question set. 
            #    (i.e. was the quiz completed)
            if indCI == (len(self._l2iPageQuestionCompositeIndices) - 1) and\
                sQSetCompletionState == 'All':
                
                # if one question set allows a multiple response, user has option to redo response
                if self.GetMultipleResponsesInQuiz() == True:

                    sMsg = 'Quiz has already been completed. \nClick Yes to begin again. Click No to exit.'
                    qtAns = self.oUtilsMsgs.DisplayYesNo(sMsg)

                    if qtAns == qt.QMessageBox.Yes:
                        iResumeCompIndex = 0
                    else:
                        # user decided not to change responses - exit
                        self.ExitOnQuizComplete("This quiz was already completed. Exiting")
                        
                else:
                    # quiz does not allow for changing responses - exit
                    self.ExitOnQuizComplete("This quiz was already completed. Exiting")
            else:
#                 if iNumLastLoginResponses == iNumQuestions:
                if sQSetCompletionState == 'All':
                    iResumeCompIndex = indCI + 1    # all questions were answered
                else:
                    iResumeCompIndex = indCI        # not all questions were answered - stay here
                    
#                 print(iResumeCompIndex, '...', self._l2iPageQuestionCompositeIndices[iResumeCompIndex][0], '...',self._l2iPageQuestionCompositeIndices[iResumeCompIndex][1] )
            
        # Display a message to user if resuming
        if not iResumeCompIndex == self._iCurrentCompositeIndex:
            self.oUtilsMsgs.DisplayInfo('Resuming quiz from previous login session.')
            
        self._iCurrentCompositeIndex = iResumeCompIndex
        
        # adjust if the resume question set is not the first on the page
        self.AdjustForPreviousQuestionSets()


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
    def ExitOnQuizComplete(self, sMsg):

        # the last index in the composite indices list was reached
        # the quiz was completed - exit
        
        self.oIOXml.SaveXml(self.oFilesIO.GetUserQuizResultsPath())
        self.SetQuizComplete(True)
        
        self.oUtilsMsgs.DisplayInfo('Quiz Complete - Exiting')
        slicer.util.exit(status=EXIT_SUCCESS)
        
    
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



#########################################################
#    NOTE: This was the layout before restructuring with tabs
#    If we go back to no tabs, some of these details must change
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
#         self._slicerLeftMainLayout = None
#         self._slicerQuizLayout = None
#         self._slicerLeftWidget = None
#         self._slicerTabWidget = None
#     def GetSlicerLeftMainLayout(self):
#         return self._slicerLeftMainLayout
# 
#     def GetSlicerQuizLayout(self):
#         return self._slicerQuizLayout
#     
#     def GetSlicerLeftWidget(self):
#         return self._slicerLeftWidget
#     
#     def GetSlicerTabWidget(self):
#         return self._slicerTabWidget

# #     def CreateQuizzerLayout(self):
# # 
# #         print ("-------ImageQuizzer Widget SetUp--------")
# # 
# #         #-------------------------------------------
# #         # set up quiz widget
# #         self._slicerLeftWidget = qt.QWidget()
# #         self._slicerLeftMainLayout = qt.QVBoxLayout()
# #         self._slicerLeftWidget.setLayout(self._slicerLeftMainLayout)
# #          
# #         
# #         
# #         #-------------------------------------------
# #         # Collapsible button
# #         self.quizCollapsibleButton = ctk.ctkCollapsibleButton()
# #         self.quizCollapsibleButton.text = "Baines Image Quizzer"
# #         self._slicerLeftMainLayout.addWidget(self.quizCollapsibleButton)
# #         
# # 
# #         
# #         # Layout within the sample collapsible button - form needs a frame
# #         self._slicerQuizLayout = qt.QFormLayout(self.quizCollapsibleButton)
# #         self.quizFrame = qt.QFrame(self.quizCollapsibleButton)
# #         self.quizFrame.setLayout(qt.QVBoxLayout())
# #         self._slicerQuizLayout.addWidget(self.quizFrame)

##################################################
#    DON'T WANT TO LOSE THIS SEQUENCE - may come in handy
#     #----------
#     def SearchForChildWidget(self, oParent, sSearchType, sSearchName):
# 
# 
#         if oParent != None:
# #             print(oParent.className(), '.....', oParent.name)
#             
#             iNumChildren = len(oParent.children())
# 
#             # drill down through children recursively until the search object has been found
#             for idx in range(iNumChildren):
#                 oChildren = oParent.children()
#                 oChild = oChildren[idx]
# #                 print ('..............', oChild.className(),'...', oChild.name)
#                 if oChild.className() == sSearchType:
#                     if oChild.name == sSearchName:
#                         return True, oChild
#                         
#                 self.iRecursiveCounter = self.iRecursiveCounter + 1
#                 if self.iRecursiveCounter == 100:    # safeguard in recursive procedure
#                     return False, None
#                     
#                 
#                 if len(oChild.children()) > 0:
#                     bFound, oFoundChild = self.SearchForChildWidget(oChild, sSearchType, sSearchName)
#                     if bFound:
#                         return True, oFoundChild
#             
#         else:
#             return False, None
#     
            

