import PythonQt
import os
import vtk, qt, ctk, slicer
import sys
import unittest

from Utilities import *
from Question import *
from ImageView import *
#from ImageQuizzer import *

from slicer.util import EXIT_SUCCESS
from datetime import datetime


#-----------------------------------------------

class Session:
    
    def __init__(self,  parent=None):
        self.sClassName = type(self).__name__
        self.parent = parent
#         print('Constructor for Session')
        
        self._oMsgUtil = UtilsMsgs()
        self._sLoginTime = ''
        self.sTimestampFormat = "%Y%m%d_%H:%M:%S"

        self._iCurrentCompositeIndex = 0
        self._l2iPageQuestionCompositeIndices = []

        self._xPageNode = None
        
        self._loQuestionSets = []
        self._lsPreviousResponses = []
        self._lsNewResponses = []
        
        self._loImageViews = []
        
        self._bStartOfSession = True
        self._bQuizComplete = False
        self._bAllowMultipleResponseInQuiz = False
        self._bAllowMultipleResponseInQSet = False      # for question set
        self._bSegmentationModule = False
        self._iSegmentationTabIndex = -1   # default
        
        self._oIOXml = None
        self._oFilesIO = None
        self._oQuizWidgets = None
        
        self._btnNext = None
        self._btnPrevious = None


    def __del__(self):
        if not self.QuizComplete():
            self._oIOXml.SaveXml(self._oFilesIO.GetUserQuizPath(), self._oIOXml.GetXmlTree())
            self._oMsgUtil.DisplayInfo(' Image Quizzer Exiting - User file is saved.')
        
    #-------------------------------------------
    #        Getters / Setters
    #-------------------------------------------

    #----------
    def SetFilesIO(self, oFilesIO):
        self._oFilesIO = oFilesIO

    #----------
    def SetIOXml(self, oIOXml):
        self._oIOXml = oIOXml

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
            self.slicerTabWidget.addTab(slicer.modules.segmenteditor.widgetRepresentation(),"Segment Editor")
            self._bSegmentationModule = True
            self._iSegmentationTabIndex = self.slicerTabWidget.count - 1
            self.slicerTabWidget.setTabEnabled(self._iSegmentationTabIndex, True)
        else:
            self._bSegmentationModule = False
        
    #----------
    def SegmentationTabEnabler(self, bTF):
        self.slicerTabWidget.setTabEnabled(self.GetSegmentationTabIndex(), bTF)

#     #----------
#     def QuizTabEnabler(self,bTF):
#         self.slicerTabWidget.setTabEnabled(0, bTF)
#     
    #----------
    def GetSegmentationTabIndex(self):
        return self._iSegmentationTabIndex
        
        
    #----------
    #----------
    def GetAllQuestionSetsForNthPage(self, iPageIndex):
        self._xPageNode = self._oIOXml.GetNthChild(self._oIOXml.GetRootNode(), 'Page', iPageIndex)
        xNodesAllQuestionSets = self._oIOXml.GetChildren(self._xPageNode, 'QuestionSet')
        
        return xNodesAllQuestionSets

    #----------
    def GetAllQuestionSetNodesForCurrentPage(self):
        xPageNode = self.GetCurrentPageNode()
        xAllQuestionSetNodes = self._oIOXml.GetChildren(xPageNode, 'QuestionSet')
        
        return xAllQuestionSetNodes
    #----------
    def GetNthQuestionSetForPage(self, idx):
        xPageNode = self.GetCurrentPageNode()
        xQuestionSetNode = self._oIOXml.GetNthChild(xPageNode, 'QuestionSet', idx)
        
        return xQuestionSetNode
        
    #----------
        
    def GetCurrentPageNode(self):
        iPageIndex = self._l2iPageQuestionCompositeIndices[self._iCurrentCompositeIndex][0]
        xPageNode = self._oIOXml.GetNthChild(self._oIOXml.GetRootNode(), 'Page', iPageIndex)
        
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
        xQuestionSetNode = self._oIOXml.GetNthChild(xPageNode, 'QuestionSet', iQSetIndex)
        
        return xQuestionSetNode
    
 
    #----------
    def GetAllQuestionsForCurrentQuestionSet(self):
        xCurrentQuestionSetNode = self.GetCurrentQuestionSetNode()
        xAllQuestionNodes = self._oIOXml.GetChildren(xCurrentQuestionSetNode, 'Question')
        
        return xAllQuestionNodes
    
    #----------
    def GetNthOptionNode(self, indQuestion, indOption):

        xQuestionSetNode = self.GetCurrentQuestionSetNode()
        xQuestionNode = self._oIOXml.GetNthChild(xQuestionSetNode, 'Question', indQuestion)
        xOptionNode = self._oIOXml.GetNthChild(xQuestionNode, 'Option', indOption)
        
        return xOptionNode
        
    #----------
    def GetAllOptionNodes(self, indQuestion):

        xQuestionSetNode = self.GetCurrentQuestionSetNode()
        xQuestionNode = self._oIOXml.GetNthChild(xQuestionSetNode, 'Question', indQuestion)
        xAllOptionNodes = self._oIOXml.GetChildren(xQuestionNode,'Option')
        
        return xAllOptionNodes
        
    #----------
    def SetImageViewList(self, lInput):
        self._loImageViews = lInput

    #-------------------------------------------
    #        Functions
    #-------------------------------------------

    def RunSetup(self, oFilesIO, oQuizWidgets):
        
        self._oIOXml = UtilsIOXml()
        self.SetFilesIO(oFilesIO)
        self.SetupButtons()
        self.SetupWidgets(oQuizWidgets)

        # open xml and check for root node
        bSuccess, xRootNode = self._oIOXml.OpenXml(self._oFilesIO.GetUserQuizPath(),'Session')

        if not bSuccess:
            sErrorMsg = "ERROR", "Not a valid quiz - Root node name was not 'Session'"
            self.oUtilsMsgs.DisplayError(sErrorMsg)

        else:

            # turn on functionality if any of the question set attributes indicated they are required
            self.SetMultipleResponsesInQuiz( \
                self._oIOXml.CheckForRequiredFunctionalityInAttribute( \
                './/Page/QuestionSet', 'allowmultipleresponse','y'))
            self.AddSegmentationModule( \
                self._oIOXml.CheckForRequiredFunctionalityInAttribute( \
                './/Page/QuestionSet', 'segmentrequired','y'))
            
            self.slicerLeftMainLayout.addWidget(self._btnNext)
            self.slicerLeftMainLayout.addWidget(self._btnPrevious)



        self.BuildPageQuestionCompositeIndexList()
        # check for partial or completed quiz
        self.SetCompositeIndexIfResumeRequired()

        # if quiz is not complete, finish setup
        #    (the check for resuming the quiz may have found it was already complete)
        if not self.QuizComplete():
            # setup buttons and display
            self.EnableButtons()
            self.DisplayPage()


    #-----------------------------------------------

    def SetupWidgets(self, oQuizWidgets_Input):
        
        self._oQuizWidgets = oQuizWidgets_Input
    
        self.slicerLeftMainLayout = self._oQuizWidgets.GetSlicerLeftMainLayout()
        self.slicerQuizLayout = self._oQuizWidgets.GetSlicerQuizLayout()
        self.slicerTabWidget = self._oQuizWidgets.GetSlicerTabWidget()
        
    
    #-----------------------------------------------
    
    def SetupButtons(self):
        
        # create buttons
        
        # Next button
        self._btnNext = qt.QPushButton("Save and Next")
        self._btnNext.toolTip = "Save responses and display next set of questions."
        self._btnNext.enabled = True
        self._btnNext.connect('clicked(bool)',self.onNextButtonClicked)
        
        # Back button
        self._btnPrevious = qt.QPushButton("Previous")
        self._btnPrevious.toolTip = "Display previous set of questions."
        self._btnPrevious.enabled = True
        self._btnPrevious.connect('clicked(bool)',self.onPreviousButtonClicked)


    #-----------------------------------------------

    def onNextButtonClicked(self):

        sMsg = ''
        
        ############################################    
        # work on saving responses for current page
        ############################################    

        bResponsesCaptured, self._lsNewResponses, sMsg = self.CaptureResponsesForQuestionSet()
        self.CaptureAndSaveImageState()
        
        if (bResponsesCaptured == False):

            self._oMsgUtil.DisplayWarning(sMsg)

        else:
            
            # only allow for writing of responses under certain conditions
            #    - allow if the question set is marked for multiple responses
            #    - allow if no responses were recorded yet
            
#             if ( self._bAllowMultipleResponse == True)  or \
#                 ((self._bAllowMultipleResponse == False) and (self.CheckForSavedResponse() == False) ):
            if ( self.GetMultipleResponsesInQsetAllowed() == True)  or \
                ((self.GetMultipleResponsesInQsetAllowed() == False) and (self.CheckForSavedResponse() == False) ):

                # check to see if the responses for the question set match 
                #    what was previously captured
                #    -only write responses if they have changed
                if not self._lsNewResponses == self._lsPreviousResponses:
                    # Responses have been captured, if it's the first set of responses
                    #    for the session, add in the login timestamp
                    #    The timestamp is added here in case the user exited without responding to anything,
                    #    allowing for the resume check to function properly
                    if self._bStartOfSession == True:
                        self.AddSessionLoginTimestamp()
                    
                    self.WriteResponses()
                    self._oIOXml.SaveXml(self._oFilesIO.GetUserQuizPath(), self._oIOXml.GetXmlTree())
                    self._bStartOfSession = False
            

            ########################################    
            # set up for next page
            ########################################    
            
            # if last question set, clear list
            if self.CheckForLastQuestionSetForPage() == True:
                self._loQuestionSets = []
        
            self._iCurrentCompositeIndex = self._iCurrentCompositeIndex + 1
                
            if self._iCurrentCompositeIndex > len(self._l2iPageQuestionCompositeIndices) -1:
                # the last question was answered - exit Slicer
                self.ExitOnQuizComplete("Quiz complete .... Exit")
    
            
            self.EnableButtons()
   
            self.DisplayPage()

        
    #-----------------------------------------------

    def onPreviousButtonClicked(self):



        self._iCurrentCompositeIndex = self._iCurrentCompositeIndex - 1
        if self._iCurrentCompositeIndex < 0:
            # reset to beginning
            self._iCurrentCompositeIndex = 0
        
        self.EnableButtons()
        
        # if there are multiple question sets for a page, the list of question sets must
        #    include all previous question sets - up to the one being displayed
        #    (eg. if a page has 4 Qsets, and we are going back to Qset 3,
        #    we need to collect question set indices 0, and 1 first,
        #    then continue processing for index 2 which will be appended in Display Page)
        
        self._loQuestionSets = [] # initialize
        indQSet = self.GetCurrentQuestionSetIndex()
        if indQSet > 0:
            self.CollectPreviousQuestionSetsToIndex(indQSet)
        
        
        
        self.DisplayPage()
#         self.DisplaySavedResponse() # ALREADY IN DISPLAY PAGE??
        
        

    #-----------------------------------------------
    
    def EnableButtons(self):
        
        # assume not at the end of the quiz
        self._btnNext.setText("Save and Next")
        
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
            self._btnNext.setText("Save and Finish")
# 
#         else:
#             # assume multiple questions in the question set
#             self._btnNext.setText("Next")
#             # if last question in the question set - save answers and continue to next
#             if not( self._l2iPageQuestionCompositeIndices[self._iCurrentCompositeIndex][0] == self._l2iPageQuestionCompositeIndices[self._iCurrentCompositeIndex + 1][0]):
#                 self._btnNext.setText("Save and Continue")

    #-----------------------------------------------

    def BuildPageQuestionCompositeIndexList(self):
        
        # This function sets up the page and question set indices which
        #    are used to coordinate the next and previous buttons.
        #    The information is gathered by querying the XML quiz.
        
        # given the root of the xml document build composite list 
        #     of indeces for each page and the question sets within
        
        # get Page nodes
        xPages = self._oIOXml.GetChildren(self._oIOXml.GetRootNode(), 'Page')

        for iPageIndex in range(len(xPages)):
            
            # for each page - get number of question sets
            xPageNode = self._oIOXml.GetNthChild(self._oIOXml.GetRootNode(), 'Page', iPageIndex)
            xQuestionSets = self._oIOXml.GetChildren(xPageNode,'QuestionSet')
            
            # append to composite indices list
            for iQuestionSetIndex in range(len(xQuestionSets)):
                self._l2iPageQuestionCompositeIndices.append([iPageIndex, iQuestionSetIndex])
        

    #-----------------------------------------------

    def DisplayPage(self):
        # extract page and question set indices from the current composite index
        

        xNodeQuestionSet = self.GetCurrentQuestionSetNode()
        oQuestionSet = QuestionSet()
        oQuestionSet.ExtractQuestionsFromXML(xNodeQuestionSet)
        
        if self.GetSegmentationTabIndex() > 0:
            self.SegmentationTabEnabler(oQuestionSet.GetSegmentRequiredTF())

        self.SetMultipleResponsesInQSetAllowed(oQuestionSet.GetMultipleResponseTF())
        
        

        
        # first clear any previous widgets (except push buttons)
        for i in reversed(range(self.slicerQuizLayout.count())):
#             x = self.slicerQuizLayout.itemAt(i).widget()
#             if not(isinstance(x, qt.QPushButton)):
            self.slicerQuizLayout.itemAt(i).widget().setParent(None)

        
        bBuildSuccess, qQuizWidget = oQuestionSet.BuildQuestionSetForm()
        
        if bBuildSuccess:
            self.slicerQuizLayout.addWidget(qQuizWidget)
            self._loQuestionSets.append(oQuestionSet)
            qQuizWidget.setEnabled(True) # initialize


            # enable widget if no response exists or if user is allowed to 
            # input multiple responses
            if self.CheckForSavedResponse() == True:
                qQuizWidget.setEnabled(self.GetMultipleResponsesInQsetAllowed())
                self.DisplaySavedResponse()

                   
                    
        oImageView = ImageView()
        oImageView.RunSetup(self.GetCurrentPageNode(), qQuizWidget)

        self.SetImageViewList(oImageView.GetImageViewList())
        self.SetSavedImageState()
    
    #-----------------------------------------------

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
        
    #-----------------------------------------------

    def CollectPreviousQuestionSetsToIndex(self, iIndex):
        
        for idx in range(iIndex):
            xNodeQuestionSet = self.GetNthQuestionSetForPage(idx)
            oQuestionSet = QuestionSet()
            oQuestionSet.ExtractQuestionsFromXML(xNodeQuestionSet)
            self._loQuestionSets.append(oQuestionSet)


    #-----------------------------------------------

    def CaptureAndSaveImageState(self):

        # for each image, capture the slice, window and level settings
        for oImageNode in self._loImageViews:
            if (oImageNode.sImageType == 'Volume'):
#                 fLevel, fWindow = oImageNode.GetViewState()
#                 print(fLevel,'...',fWindow, '...', oImageNode.sDestination)
#                 dictAttrib = { 'window': str(fWindow), 'level':  str(fLevel)}
                dictAttribState = oImageNode.GetViewState()

                # check if xml State element exists
                xImage = oImageNode.GetXmlImageElement()
                iNumStateElements = self._oIOXml.GetNumChildrenByName(xImage, 'State')
                if iNumStateElements >0:
                    # update xml image/state element (first child)
                    xStateElement = self._oIOXml.GetNthChild(xImage, 'State', 0)
                    self.UpdateAtributesInElement(xStateElement, dictAttribState)
                # if no State element, add one
                else:
                    self.AddImageStateElement(xImage, dictAttribState)
                    
        self._oIOXml.SaveXml(self._oFilesIO.GetUserQuizPath(), self._oIOXml.GetXmlTree())
    
    #-----------------------------------------------
# 
#     def GetSavedImageState(self):
# 
#         xStateElement = None
#         dictStateAttribs = {}
#         
#         for oImageNode in self._loImageViews:
#             if (oImageNode.sImageType == 'Volume'):
#                 xImage = oImageNode.GetXmlImageElement()
#                 xStateElement = self._oIOXml.GetNthChild(xImage, 'State', 0)
#                 if not xStateElement == None:
#                     dictStateAttribs = self._oIOXml.GetAttributes(xStateElement)
#                     
#                 for sKey, sValue in dictStateAttribs.items():
#                     print(sKey,':',sValue)
#                     
#         return dictStateAttribs
    
    #-----------------------------------------------

    def SetSavedImageState(self):
        
        for oImageView in self._loImageViews:
            if (oImageView.sImageType == 'Volume'):
        
                xStateElement = self._oIOXml.GetNthChild(oImageView.GetXmlImageElement(), 'State', 0)
                dictImageState = self._oIOXml.GetAttributes(xStateElement)
                
                oImageView.SetImageState(dictImageState)
            
            
    
    #-----------------------------------------------

    def CaptureResponsesForQuestionSet(self):
        
        # sMsg may be set in Question class function to capture the response
        sMsg = ''
        
        # get list of questions from current question set
        
        indQSet = self.GetCurrentQuestionSetIndex()
 
        oQuestionSet = self._loQuestionSets[indQSet]

        loQuestions = oQuestionSet.GetQuestionList()
            
        lsAllResponses = []
        lsResponsesForOptions = []
        for indQuestion in range(len(loQuestions)):
            oQuestion = loQuestions[indQuestion]
            bResponseCaptured = False
            
            bResponseCaptured, lsResponsesForOptions, sMsg = oQuestion.CaptureResponse()

            if bResponseCaptured == False:
                break   # exit from loop - question is missing response
            else:
                lsAllResponses.append(lsResponsesForOptions)

                
        return bResponseCaptured, lsAllResponses, sMsg
       
    #-----------------------------------------------

    def CheckForSavedResponse(self):
        
        bResponseExists = False
        
        # get option node for the current question set , 1st question, 1st otpion
        xOptionNode = self.GetNthOptionNode( 0, 0)
        
        iNumResponses = self._oIOXml.GetNumChildrenByName(xOptionNode,'Response')
#         print ('Number of responses: %i' %iNumResponses)
        if iNumResponses >0:
            bResponseExists = True
        
        return bResponseExists
    
    #-----------------------------------------------

    def DisplaySavedResponse(self):


        xNodeQuestionSet = self.GetCurrentQuestionSetNode()
        indQSet = self.GetCurrentQuestionSetIndex()
 
        oQuestionSet = self._loQuestionSets[indQSet]


        loQuestions = oQuestionSet.GetQuestionList()
         
        # for each question and each option, extract any existing responses from the XML
         
        lsAllResponsesForQuestion = []
        for indQuestion in range(len(loQuestions)):
            oQuestion = loQuestions[indQuestion]
            xQuestionNode = self._oIOXml.GetNthChild(xNodeQuestionSet, 'Question', indQuestion)
             
                 
            lsResponseValues = []                  
            xAllOptions = self._oIOXml.GetChildren(xQuestionNode, 'Option')


            xAllOptions = self.GetAllOptionNodes(indQuestion)
            for xOptionNode in xAllOptions:
                
                
                dtLatestTimestamp = ''    # timestamp of type 'datetime'
                sLatestResponse = ''

                xAllResponseNodes = self._oIOXml.GetChildren(xOptionNode, 'Response')
                for xResponseNode in xAllResponseNodes:
                    sResponseTime = self._oIOXml.GetValueOfNodeAttribute(xResponseNode, 'responsetime')
                    dtResponseTimestamp = datetime.strptime(sResponseTime, self.sTimestampFormat)
#                     print('*** TIME : %s' % sResponseTime)
                     
                    if dtLatestTimestamp == '':
                        dtLatestTimestamp = dtResponseTimestamp
                        sLatestResponse = self._oIOXml.GetDataInNode(xResponseNode)
                    else:
                        # compare with >= in order to capture 'last' response 
                        #    in case there are responses with the same timestamp
                        if dtResponseTimestamp >= dtLatestTimestamp:
                            dtLatestTimestamp = dtResponseTimestamp
                            sLatestResponse = self._oIOXml.GetDataInNode(xResponseNode)
                            
                    
    
                # search for 'latest' response completed - update the list
#                 print('************Data...%s***END***' % sLatestResponse)
                lsResponseValues.append(sLatestResponse)
                
            oQuestion.PopulateQuestionWithResponses(lsResponseValues)

            lsAllResponsesForQuestion.append(lsResponseValues)
            
    
            lsResponseValues = []  # clear for next set of options 

        self._lsPreviousResponses = lsAllResponsesForQuestion
            
    
    #-----------------------------------------------

    #-----------------------------------------------

    def WriteResponses(self):
        
        
        indQSet = self.GetCurrentQuestionSetIndex()
 
        oQuestionSet = self._loQuestionSets[indQSet]


        loQuestions = oQuestionSet.GetQuestionList()
        
        lsResponsesForOptions = []
        for indQuestion in range(len(loQuestions)):
            oQuestion = loQuestions[indQuestion]
            bResponseCaptured = False
            
            bResponseCaptured, lsResponsesForOptions, sMsg = oQuestion.CaptureResponse()


            if bResponseCaptured == True:                
                # add response element to proper option node
                for indOption in range(len(lsResponsesForOptions)):
                    xOptionNode = self.GetNthOptionNode( indQuestion, indOption)
                    
                    if not xOptionNode == None:
                        self.AddResponseElement(xOptionNode, lsResponsesForOptions[indOption])

            
    #-----------------------------------------------

    def AddResponseElement(self, xOptionNode, sResponse):
        
        now = datetime.now()
        sResponseTime = now.strftime(self.sTimestampFormat)
        
        dictAttrib = { 'logintime': self.LoginTime(), 'responsetime': sResponseTime}
        
        self._oIOXml.AddElement(xOptionNode,'Response', sResponse, dictAttrib)
        
    #-----------------------------------------------

    def AddImageStateElement(self, xImageNode, dictAttrib):
        
        sNullData = ''

        self._oIOXml.AddElement(xImageNode,'State', sNullData, dictAttrib)
        
        
    #-----------------------------------------------
        
    def UpdateAtributesInElement(self, xElement, dictAttrib):
        
        # for each key, value in the dictionary, update the element attributes
        for sKey, sValue in dictAttrib.items():
            self._oIOXml.UpdateAttribute(xElement, sKey, sValue)
        
    #-----------------------------------------------

    def AddSessionLoginTimestamp(self):
        

        now = datetime.now()
#         self.sLoginTime = now.strftime("%b-%d-%Y-%H-%M-%S")
        self.SetLoginTime( now.strftime(self.sTimestampFormat) )
        
        dictAttrib = {'logintime': self.LoginTime()}
        
        sNullText = ''
        
        sUserQuizPath = self._oFilesIO.GetUserQuizPath()
        self._oIOXml.AddElement(self._oIOXml.GetRootNode(),'Login', sNullText, dictAttrib)
        
        self._oIOXml.SaveXml(sUserQuizPath, self._oIOXml.GetXmlTree())
            
    #-----------------------------------------------

    def SetCompositeIndexIfResumeRequired(self):
        # Scan the user's quiz file for existing responses in case the user
        #     exited the quiz prematurely (before it was complete) on the last login
        #
        # The following assumptions are made based on the quiz flow:
        #    - the quiz pages and question sets are presented sequentially 
        #        as laid out in the quiz file
        #    - during one session login, if any questions in the question set were unanswered,
        #        no responses for that question set were saved (so we only have
        #        to inspect the first option of the first question in the question set)
        #
        # By looping through the page/question set indices stored in the
        #    composite index array in reverse, we look for the first question with an existing response
        #    that matches the last login session time.
        #    Add one to the current index to resume.
        

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
            xPageNode = self._oIOXml.GetNthChild(self._oIOXml.GetRootNode(), 'Page', indPage)
            xQuestionSetNode = self._oIOXml.GetNthChild(xPageNode, 'QuestionSet', indQuestionSet)
#             print(indCI, 'Page:', indPage, 'QS:', indQuestionSet)
            
            # get first Option node of the first Question
            xQuestionNode = self._oIOXml.GetNthChild(xQuestionSetNode, 'Question', 0)
            xOptionNode = self._oIOXml.GetNthChild(xQuestionNode, 'Option', 0)
            
            # get number of Response nodes in the option
            iNumResponses = self._oIOXml.GetNumChildrenByName(xOptionNode, 'Response')
            
                
            # check each response tag for the time
            for indResp in range(iNumResponses):
                xResponseNode = self._oIOXml.GetNthChild(xOptionNode, 'Response', indResp)
                sTimestamp = self._oIOXml.GetValueOfNodeAttribute(xResponseNode, 'logintime')

                dtLoginTimestamp = datetime.strptime(sTimestamp, self.sTimestampFormat)
                if dtLoginTimestamp == dtLastLogin:
                    # found a response for last login at this composite index
                    bLastLoginResponseFound = True
                    break   # exit checking each response
            
            if bLastLoginResponseFound == True:
                break   # exit the reversed loop through the composite indices
            
        if bLastLoginResponseFound == True:
            if indCI == (len(self._l2iPageQuestionCompositeIndices) - 1):
                
                # if one question set allows a multiple response, user has option to redo response
                if self.GetMultipleResponsesInQuiz() == True:
                    sMsg = 'Quiz has already been completed. \nClick Yes to begin again. Click No to exit.'
#                     sAns = qt.QMessageBox.question(slicer.util.mainWindow(),'Continue?',sMsg, qt.QMessageBox.Yes, qt.QMessageBox.No)
                    qtAns = self._oMsgUtil.DisplayYesNo(sMsg)

                    if qtAns == qt.QMessageBox.Yes:
                        iResumeCompIndex = 0
                    else:
                        self.ExitOnQuizComplete("This quiz was already completed. Exiting")
                else:
                    self.ExitOnQuizComplete("This quiz was already completed. Exiting")
            else:
                iResumeCompIndex = indCI + 1
#             print(iResumeCompIndex, '...', self._l2iPageQuestionCompositeIndices[iResumeCompIndex][0], '...',self._l2iPageQuestionCompositeIndices[iResumeCompIndex][1] )
            
        # Display a message to user if resuming
        if not iResumeCompIndex == self._iCurrentCompositeIndex:
            self._oMsgUtil.DisplayInfo('Resuming quiz from previous login session.')
            
        self._iCurrentCompositeIndex = iResumeCompIndex


    #-----------------------------------------------

    def GetLastLoginTimestamp(self):
        # function to scan the user's quiz file for all session login times
        # return the last session login time

        lsTimestamps = []
        dtLastTimestamp = ''    # timestamp of type 'datetime'

#         dtCurrentLogin = datetime.strptime(self.sLoginTime, self.sTimestampFormat)
        
        xmlLoginNodes = self._oIOXml.GetChildren(self._oIOXml.GetRootNode(), 'Login')

        # collect all login timestamps (type 'string')
        for indElem in range(len(xmlLoginNodes)):
            # get date/time from attribute
            xmlLoginNode = self._oIOXml.GetNthChild(self._oIOXml.GetRootNode(), 'Login', indElem)

            sTimestamp = self._oIOXml.GetValueOfNodeAttribute(xmlLoginNode, 'logintime')
            lsTimestamps.append(sTimestamp)
            

        # loop through timestamps to search for the last login occurrence
        for indTime in range(len(lsTimestamps)):
            
            sNewTimestamp = lsTimestamps[indTime]
            # convert to datetime format for compare
            dtNewTimestamp = datetime.strptime(sNewTimestamp, self.sTimestampFormat)
            
            if dtLastTimestamp == '': # for initial compare
                dtLastTimestamp = dtNewTimestamp
                
            else:
                # update the last time stamp 
#                 if not (dtNewTimestamp==dtCurrentLogin):
                if dtNewTimestamp > dtLastTimestamp:
                    dtLastTimestamp = dtNewTimestamp
                
                            
        return dtLastTimestamp
            
    #-----------------------------------------------
            
    def ExitOnQuizComplete(self, sMsg):

        # the last index in the composite indices list was reached
        # the quiz was completed - exit
        
        self._oIOXml.SaveXml(self._oFilesIO.GetUserQuizPath(), self._oIOXml.GetXmlTree())
        self.SetQuizComplete(True)
        self._oMsgUtil.DisplayInfo(sMsg)
        slicer.util.exit(status=EXIT_SUCCESS)

    
    
