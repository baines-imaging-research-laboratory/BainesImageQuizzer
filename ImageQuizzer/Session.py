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
        print('Constructor for Session')
        
        self._oMsgUtil = UtilsMsgs()
        self._sLoginTime = ''
        self.sTimestampFormat = "%Y%m%d_%H:%M:%S"

        self._iCurrentCompositeIndex = 0
        self._l2iPageQuestionCompositeIndices = []

        self._xPageNode = None
        
        self._loQuestionSets = []
        
        self._bStartOfSession = True
        self._bQuizComplete = False
        self._bAllowMultipleResponse = False
       
        
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
    def SetMultipleResponsesAllowed(self, sInput):
        if sInput == 'y' or sInput == 'Y':
            self._bAllowMultipleResponse = True
        else:
            self._bAllowMultipleResponse = False
            
    #----------
    def GetAllQuestionSetsForPage(self, iPageIndex):
        self._xPageNode = self._oIOXml.GetNthChild(self._oIOXml.GetRootNode(), 'Page', iPageIndex)
        xNodesAllQuestionSets = self._oIOXml.GetChildren(self._xPageNode, 'QuestionSet')
        
        return xNodesAllQuestionSets

    #----------
    def GetCurrentPage(self):
        iPageIndex = self._l2iPageQuestionCompositeIndices[self._iCurrentCompositeIndex][0]
        xPageNode = self._oIOXml.GetNthChild(self._oIOXml.GetRootNode(), 'Page', iPageIndex)
        
        return xPageNode
    
    #----------
    def GetCurrentQuestionSet(self):
        iQSetIndex = self._l2iPageQuestionCompositeIndices[self._iCurrentCompositeIndex][1]
        xPageNode = self.GetCurrentPage()
        xQuestionSetNode = self._oIOXml.GetNthChild(xPageNode, 'QuestionSet', iQSetIndex)
        
        return xQuestionSetNode
    
    #----------
    def GetAllQuestionsForCurrentQuestionSet(self):
        xCurrentQuestionSetNode = self.GetCurrentQuestionSet()
        xAllQuestionNodes = self._oIOXml.GetChildren(xCurrentQuestionSetNode, 'Question')
        
        return xAllQuestionNodes
    #----------
    #----------
    #----------
    #----------

    def GetNthOptionNode(self, indQuestionSet, indQuestion, indOption):

        # get the element node for the option
        
       
#         xQuestionSetNode = self._oIOXml.GetNthChild(self._xPageNode, 'QuestionSet', indQuestionSet)
        xQuestionSetNode = self.GetCurrentQuestionSet()
        xQuestionNode = self._oIOXml.GetNthChild(xQuestionSetNode, 'Question', indQuestion)
        xOptionNode = self._oIOXml.GetNthChild(xQuestionNode, 'Option', indOption)
        
        
        return xOptionNode
        
    #-----------------------------------------------

    def GetAllOptionNodes(self, indQuestionSet, indQuestion):

        # get the element node for the option
        
#         xQuestionSetNode = self._oIOXml.GetNthChild(self._xPageNode, 'QuestionSet', indQuestionSet)
        xQuestionSetNode = self.GetCurrentQuestionSet()
        xQuestionNode = self._oIOXml.GetNthChild(xQuestionSetNode, 'Question', indQuestion)
        xAllOptionNodes = self._oIOXml.GetChildren(xQuestionNode,'Option')
        
        return xAllOptionNodes
        
            

    #-------------------------------------------
    #        Functions
    #-------------------------------------------

    def RunSetup(self, oFilesIO, oQuizWidgets):
        
        self._oIOXml = UtilsIOXml()
        self.SetFilesIO(oFilesIO)
        self.SetupWidgets(oQuizWidgets)
        self.SetupButtons()

        # open xml and check for root node
        bSuccess, xRootNode = self._oIOXml.OpenXml(self._oFilesIO.GetUserQuizPath(),'Session')

        if not bSuccess:
            sErrorMsg = "ERROR", "Not a valid quiz - Root node name was not 'Session'"
            self.oUtilsMsgs.DisplayError(sErrorMsg)

        else:
#             # add date time stamp to Session element
#             self.AddSessionLoginTimestamp()
            # set the boolean allowing multiple responses
            sMultiplesAllowed = self._oIOXml.GetValueOfNodeAttribute(xRootNode, 'allowmultipleresponses')
            self.SetMultipleResponsesAllowed(sMultiplesAllowed)
            
            self.slicerLeftMainLayout.addWidget(self._btnNext)
            self.slicerLeftMainLayout.addWidget(self._btnPrevious)



        self.BuildPageQuestionCompositeIndexList()
        # check for partial or completed quiz
        self.SetCompositeIndexIfResumeRequired()

        # if quiz is not complete, finish setup
        #    check for resuming the quiz may have found it was already complete
        if not self.QuizComplete():
            # setup buttons and display
            self.EnableButtons()
            self.DisplayPage()


    #-----------------------------------------------

    def SetupWidgets(self, oQuizWidgets_Input):
        
        self._oQuizWidgets = oQuizWidgets_Input
    
        self.slicerLeftMainLayout = self._oQuizWidgets.GetSlicerLeftMainLayout()
        self.slicerQuizLayout = self._oQuizWidgets.GetSlicerQuizLayout()
    
    #-----------------------------------------------
    
    def SetupButtons(self):
        
        # create buttons
        
        # Next button
        self._btnNext = qt.QPushButton("Next")
        self._btnNext.toolTip = "Display next set of questions."
        self._btnNext.enabled = True
        self._btnNext.connect('clicked(bool)',self.onNextButtonClicked)
        
        # Back button
        self._btnPrevious = qt.QPushButton("Previous")
        self._btnPrevious.toolTip = "Display previous set of questions."
        self._btnPrevious.enabled = True
        self._btnPrevious.connect('clicked(bool)',self.onPreviousButtonClicked)


    #-----------------------------------------------

    def AddSessionLoginTimestamp(self):
        

        now = datetime.now()
#         self.sLoginTime = now.strftime("%b-%d-%Y-%H-%M-%S")
        self.SetLoginTime( now.strftime(self.sTimestampFormat) )
        
        dictAttrib = {}
        dictAttrib = {'logintime': self.LoginTime()}
        
        sNullText = ''
        
        sUserQuizPath = self._oFilesIO.GetUserQuizPath()
        self._oIOXml.AddElement(self._oIOXml.GetRootNode(),'Login', sNullText, dictAttrib)
        
        self._oIOXml.SaveXml(sUserQuizPath, self._oIOXml.GetXmlTree())
            
    #-----------------------------------------------

    def BuildPageQuestionCompositeIndexList(self):
        
        # This function collects the page and question set indices which
        #    are used to coordinate the next and previous buttons
        
        # given the root of the xml document build composite list 
        #     of indeces for each page and the question sets within
        
        # get Page nodes
        xPages = self._oIOXml.GetChildren(self._oIOXml.GetRootNode(), 'Page')

        for iPageIndex in range(len(xPages)):
            # for each page - get number of question sets
            xPageNode = self._oIOXml.GetNthChild(self._oIOXml.GetRootNode(), 'Page', iPageIndex)
            xQuestionSets = self._oIOXml.GetChildren(xPageNode,'QuestionSet')
            
            for iQuestionSetIndex in range(len(xQuestionSets)):
                self._l2iPageQuestionCompositeIndices.append([iPageIndex, iQuestionSetIndex])
        

    #-----------------------------------------------

    def DisplayPage(self):
        # extract page and question set indices from the current composite index
        
        iPageIndex = self._l2iPageQuestionCompositeIndices[self._iCurrentCompositeIndex][0]
        iQuestionSetIndex = self._l2iPageQuestionCompositeIndices[self._iCurrentCompositeIndex][1]

        self._xPageNode = self._oIOXml.GetNthChild(self._oIOXml.GetRootNode(), 'Page', iPageIndex)
        xNodeCurrentQuestionSet = self._oIOXml.GetNthChild(self._xPageNode, 'QuestionSet', iQuestionSetIndex)
        
        # get all question sets for the page
        xNodesAllQuestionSets = self.GetAllQuestionSetsForPage(iPageIndex)
        for xNodeQuestionSet in xNodesAllQuestionSets:
            oQuestionSet = QuestionSet()
            oQuestionSet.ExtractQuestionsFromXML(xNodeQuestionSet)
            self._loQuestionSets.append(oQuestionSet)
        
        
        oCurrentQuestionSet = QuestionSet()
#         oQuestionSet.ExtractQuestionsFromXML(xNodeQuestionSet)
        oCurrentQuestionSet = self._loQuestionSets[iQuestionSetIndex]
        
        # first clear any previous widgets (except push buttons)
        for i in reversed(range(self.slicerQuizLayout.count())):
#             x = self.slicerQuizLayout.itemAt(i).widget()
#             if not(isinstance(x, qt.QPushButton)):
            self.slicerQuizLayout.itemAt(i).widget().setParent(None)

        
        bBuildSuccess, qQuizWidget = oCurrentQuestionSet.BuildQuestionSetForm()
        if bBuildSuccess:
            self.slicerQuizLayout.addWidget(qQuizWidget)
#             self._loQuestionSets.append(oQuestionSet)

            # enable widget if no response exists or if user is allowed to 
            # input multiple responses
            if self.CheckForPreviousResponse() == True:
                if self._bAllowMultipleResponse == False:
                    qQuizWidget.setEnabled(False)
                    self.DisplayPreviousResponses()
                else:
                    qQuizWidget.setEnabled(True)
                    
                    
        oImageView = ImageView()
        oImageView.RunSetup(self._xPageNode, qQuizWidget)
    
    #-----------------------------------------------
    
    def EnableButtons(self):
        
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

    def onNextButtonClicked(self):

        sMsg = ''
            

        bResponsesCaptured, sMsg = self.CaptureResponses()
        
        if (bResponsesCaptured == False):

            self._oMsgUtil.DisplayWarning(sMsg)

        else:
            
            
            # only allow for writing of responses under certain conditions
            
            if ( self._bAllowMultipleResponse == True)  or \
                ((self._bAllowMultipleResponse == False) and (self.CheckForPreviousResponse() == False) ):

                # Responses have been captured, if it's the first set of responses
                #    for the session, add in the login timestamp
                #    This timestamp is added here in case the user exited without responding to anything,
                #    allowing for the resume check to function properly
                if self._bStartOfSession == True:
                    self.AddSessionLoginTimestamp()

                self.WriteResponses()
                self._oIOXml.SaveXml(self._oFilesIO.GetUserQuizPath(), self._oIOXml.GetXmlTree())
                self._bStartOfSession = False
            
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
            
    def ExitOnQuizComplete(self, sMsg):

        self._oIOXml.SaveXml(self._oFilesIO.GetUserQuizPath(), self._oIOXml.GetXmlTree())
        self.SetQuizComplete(True)
        self._oMsgUtil.DisplayInfo(sMsg)
        slicer.util.exit(status=EXIT_SUCCESS)

    
    
    #-----------------------------------------------

    def onPreviousButtonClicked(self):



        self._iCurrentCompositeIndex = self._iCurrentCompositeIndex - 1
        if self._iCurrentCompositeIndex < 0:
            # reset to beginning
            self._iCurrentCompositeIndex = 0
        
        self.EnableButtons()
        
        self._loQuestionSets = []
        self.DisplayPage()
        self.DisplayPreviousResponses()
        
        


    #-----------------------------------------------

    def CaptureResponses(self):
        
        # set defaults 
        sMsg = ''
        # get list of questions from current question set
        
            
        indQSet = self._l2iPageQuestionCompositeIndices[self._iCurrentCompositeIndex][1]

        oQuestionSet = self._loQuestionSets[indQSet]
        loQuestions = []
        loQuestions = oQuestionSet.GetQuestionList()
            
        self._lsResponsesForOptions = []
        for indQuestion in range(len(loQuestions)):
            oQuestion = loQuestions[indQuestion]
            bResponseCaptured = False
            
            bResponseCaptured, self._lsResponsesForOptions, sMsg = oQuestion.CaptureResponse()

            if bResponseCaptured == False:
                break   # exit from loop - question is missing response

                
        return bResponseCaptured, sMsg
       
    #-----------------------------------------------

    def CheckForPreviousResponse(self):
        
        bResponseExists = False
        
        iQuestionSetIndex = self._l2iPageQuestionCompositeIndices[self._iCurrentCompositeIndex][1]
        
        # get option node for the current question set , 1st question, 1st otpion
        xOptionNode = self.GetNthOptionNode(iQuestionSetIndex, 0, 0)
        
        iNumResponses = self._oIOXml.GetNumChildrenByName(xOptionNode,'Response')
#         print ('Number of responses: %i' %iNumResponses)
        if iNumResponses >0:
            bResponseExists = True
        
        return bResponseExists
    
    #-----------------------------------------------

    def DisplayPreviousResponses(self):

        iPageIndex = self._l2iPageQuestionCompositeIndices[self._iCurrentCompositeIndex][0]
        iQuestionSetIndex = self._l2iPageQuestionCompositeIndices[self._iCurrentCompositeIndex][1]
         
#         print('Indices ... Page: %i' % iPageIndex)
#         print('              QS: %i' % iQuestionSetIndex)
 
        self._xPageNode = self._oIOXml.GetNthChild(self._oIOXml.GetRootNode(), 'Page', iPageIndex)
        xQuestionSetNode = self._oIOXml.GetNthChild(self._xPageNode, 'QuestionSet', iQuestionSetIndex)
 
         
 
        oQuestionSet = self._loQuestionSets[iQuestionSetIndex]
        loQuestions = []
        loQuestions = oQuestionSet.GetQuestionList()
         
        # for each question and each option, extract any existing responses from the XML
         
        for indQuestion in range(len(loQuestions)):
            oQuestion = loQuestions[indQuestion]
            xQuestionNode = self._oIOXml.GetNthChild(xQuestionSetNode, 'Question', indQuestion)
             
                 
            lsResponseValues = []                  
            xAllOptions = self._oIOXml.GetChildren(xQuestionNode, 'Option')

#         iQuestionSetIndex = self._l2iPageQuestionCompositeIndices[self._iCurrentCompositeIndex][1]
#         xAllQuestions = self._oIOXml.GetChildren()

            xAllOptions = self.GetAllOptionNodes(iQuestionSetIndex, indQuestion)
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

#                 sLatestResponse, dtLatestTimestamp = self.GetLatestResponse(xOptionNode)


                # search for 'latest' response completed - update the list
#                 print('************Data...%s***END***' % sLatestResponse)
                lsResponseValues.append(sLatestResponse)
                    
                    
            oQuestion.PopulateQuestionWithResponses(lsResponseValues)
    
#             if bSuccess == False:
#                 sMsg = sMsg + '  Page:' + str(iPageIndex) + '  QSet:' + str(iQuestionSetIndex) + ' Question:' + str(indQuestion) 
#                 self._oMsgUtil.DisplayWarning(sMsg)  
            lsResponseValues = []  # clear for next set of options 
            
    
    #-----------------------------------------------

#     def GetLatestResponse(self, xOptionNode):
#         
#         
#         dtLatestTimestamp = ''    # timestamp of type 'datetime'
#         sLatestResponse = ''
#         
#         xAllResponseNodes = self._oIOXml.GetChildren(xOptionNode, 'Response')
#         for xResponseNode in xAllResponseNodes:
#             sResponseTime = self._oIOXml.GetValueOfNodeAttribute(xResponseNode, 'time')
#             dtResponseTimestamp = datetime.strptime(sResponseTime, self.sTimestampFormat)
#             print('*** TIME : %s' % sResponseTime)
#             
#             if dtLatestTimestamp == '':
#                 dtLatestTimestamp = dtResponseTimestamp
#                 sLatestResponse = self._oIOXml.GetDataInNode(xResponseNode)
#             else:
#                 if dtResponseTimestamp > dtLatestTimestamp:
#                     dtLatestTimestamp = dtResponseTimestamp
#                     sLatestResponse = self._oIOXml.GetDataInNode(xResponseNode)
# 
#         return sLatestResponse, dtLatestTimestamp

    #-----------------------------------------------

    def WriteResponses(self):
        
        
#         for indQSet in range(len(self._loQuestionSets)):
        indQSet = self._l2iPageQuestionCompositeIndices[self._iCurrentCompositeIndex][1]

        oQuestionSet = self._loQuestionSets[indQSet]
        loQuestions = []
        loQuestions = oQuestionSet.GetQuestionList()
        
        lsResponsesForOptions = []
        for indQuestion in range(len(loQuestions)):
            oQuestion = loQuestions[indQuestion]
            bResponseCaptured = False
            
            bResponseCaptured, lsResponsesForOptions, sMsg = oQuestion.CaptureResponse()


            if bResponseCaptured == True:                
                # add response element to proper option node
                for indOption in range(len(lsResponsesForOptions)):
                    xOptionNode = self.GetNthOptionNode( indQSet, indQuestion, indOption)
                    
                    if not xOptionNode == None:
                        self.AddResponseElement(xOptionNode, lsResponsesForOptions[indOption])

            
    #-----------------------------------------------
    def AddResponseElement(self, xOptionNode, sResponse):
        
        now = datetime.now()
        sResponseTime = now.strftime(self.sTimestampFormat)
        
        dictAttrib = {}
        dictAttrib = { 'logintime': self.LoginTime(), 'responsetime': sResponseTime}
        
        sUserQuizPath = self._oFilesIO.GetUserQuizPath()
        self._oIOXml.AddElement(xOptionNode,'Response', sResponse, dictAttrib)
        
    #-----------------------------------------------

    def SetCompositeIndexIfResumeRequired(self):
        # Scan the user's quiz file for existing responses in case the user
        #     exited the quiz prematurely (before it was complete) on the last login
        #
        # The following assumptions are made based on the quiz flow:
        #    - the quiz pages and question sets are presented sequentially 
        #        as laid out in the quiz file
        #    - during one session login, if any questions in the question set were unanswered,
        #        no responses for that question set were captured (so we only have
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
            print(indCI, 'Page:', indPage, 'QS:', indQuestionSet)
            
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
                if self._bAllowMultipleResponse == True:
                    iResumeCompIndex = 0
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
        # return the last session login time prior to the current session

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
                # update the last time stamp (if not current)
#                 if not (dtNewTimestamp==dtCurrentLogin):
                if dtNewTimestamp > dtLastTimestamp:
                    dtLastTimestamp = dtNewTimestamp
                
                            
        return dtLastTimestamp
            
