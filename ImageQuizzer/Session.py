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
        self.sLoginTime = ''
        self.sTimestampFormat = "%Y%m%d_%H:%M"

        self._iCompIndex = 0
        
#         self._xRootNode = None
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
        if not self._bQuizComplete == True:
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
        
        
#     def SetRootNode(self, xNode):
#         self._xRootNode = xNode
#           
#     #----------
#     def GetRootNode(self):
#         return self._xRootNode

    
    #----------
    def SetCompositeIndicesList(self,lIndices):
        self._l2iPageQuestionCompositeIndices = lIndices
        
    #----------
    def GetCompositeIndicesList(self):
        return self._l2iPageQuestionCompositeIndices

    #----------
    def SetMultipleResponsesAllowed(self, sInput):
        if sInput == 'y' or sInput == 'Y':
            self._bAllowMultipleResponse = True
        else:
            self._bAllowMultipleResponse = False
            

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
        if (self._bQuizComplete == False):
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
        self.sLoginTime = now.strftime(self.sTimestampFormat)
        
#         print(sLoginTime)
        dictAttrib = {}
        dictAttrib = {'time': self.sLoginTime}
        
        sNullText = ''
        
        sUserQuizPath = self._oFilesIO.GetUserQuizPath()
        self._oIOXml.AddElement(self._oIOXml.GetRootNode(),'Login', sNullText, dictAttrib)
        
        self._oIOXml.SaveXml(sUserQuizPath, self._oIOXml.GetXmlTree())
            
    #-----------------------------------------------

    def BuildPageQuestionCompositeIndexList(self):
        
        # This function collects the page and question set indices which
        #    are used to coordinate the next and previous buttons
        
        # given the root of the xml document build composite list 
        #     of indexes for each page and the question sets within
        
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
        
        iPageIndex = self._l2iPageQuestionCompositeIndices[self._iCompIndex][0]
        iQuestionSetIndex = self._l2iPageQuestionCompositeIndices[self._iCompIndex][1]

        self._xPageNode = self._oIOXml.GetNthChild(self._oIOXml.GetRootNode(), 'Page', iPageIndex)
        xNodeQuestionSet = self._oIOXml.GetNthChild(self._xPageNode, 'QuestionSet', iQuestionSetIndex)
        
        oQuestionSet = QuestionSet()
        oQuestionSet.ExtractQuestionsFromXML(xNodeQuestionSet)
        
        # first clear any previous widgets (except push buttons)
        for i in reversed(range(self.slicerQuizLayout.count())):
#             x = self.slicerQuizLayout.itemAt(i).widget()
#             if not(isinstance(x, qt.QPushButton)):
            self.slicerQuizLayout.itemAt(i).widget().setParent(None)

        
        bBuildSuccess, qQuizWidget = oQuestionSet.BuildQuestionSetForm()
        if bBuildSuccess:
            self.slicerQuizLayout.addWidget(qQuizWidget)
            self._loQuestionSets.append(oQuestionSet)
        
        oImageView = ImageView()
        oImageView.RunSetup(self._xPageNode, qQuizWidget)
    
    #-----------------------------------------------
    
    def EnableButtons(self):
        
        # beginning of quiz
        if (self._iCompIndex == 0):
            self._btnNext.enabled = True
            self._btnPrevious.enabled = False

        # end of quiz
        elif (self._iCompIndex == len(self._l2iPageQuestionCompositeIndices) - 1):
            self._btnNext.enabled = True
            self._btnPrevious.enabled = True

        # somewhere in middle
        else:
            self._btnNext.enabled = True
            self._btnPrevious.enabled = True

        # assign button description           
        if (self._iCompIndex == len(self._l2iPageQuestionCompositeIndices) - 1):
            # last question of last image view
            self._btnNext.setText("Save and Finish")

        else:
            # assume multiple questions in the question set
            self._btnNext.setText("Next")
            # if last question in the question set - save answers and continue to next
            if not( self._l2iPageQuestionCompositeIndices[self._iCompIndex][0] == self._l2iPageQuestionCompositeIndices[self._iCompIndex + 1][0]):
                self._btnNext.setText("Save and Continue")

    #-----------------------------------------------

    def onNextButtonClicked(self):

        sMsg = ''
        # check if a save is required before displaying next page
        sPrevText = self._btnNext.text
            

        bResponsesCapturedForPage, sMsg = self.CaptureResponsesForPage()
        
        if (bResponsesCapturedForPage == False):

            self._oMsgUtil.DisplayWarning(sMsg)

        else:
            
            # Responses have been captured, if it's the first set of responses
            #    for the session, add in the login timestamp
            #    This timestamp is added here in case the user exited without responding to anything,
            #    allowing for the resume check to function properly
            if self._bStartOfSession == True:
                self.AddSessionLoginTimestamp()
            
            self.WriteResponses()
            self._oIOXml.SaveXml(self._oFilesIO.GetUserQuizPath(), self._oIOXml.GetXmlTree())
            self._bStartOfSession = False
            
            if "Save" in sPrevText:
                self._loQuestionSets = []
                
        
            self._iCompIndex = self._iCompIndex + 1
                
            if self._iCompIndex > len(self._l2iPageQuestionCompositeIndices) -1:
                # the last question was answered - exit Slicer
                self.ExitOnQuizComplete("Quiz complete .... Exit")
    
            self.EnableButtons()
   
            self.DisplayPage()
        
    #-----------------------------------------------
            
    def ExitOnQuizComplete(self, sMsg):

        self._oIOXml.SaveXml(self._oFilesIO.GetUserQuizPath(), self._oIOXml.GetXmlTree())
        self._bQuizComplete = True
        self._oMsgUtil.DisplayInfo(sMsg)
        slicer.util.exit(status=EXIT_SUCCESS)

    
    
    #-----------------------------------------------

    def onPreviousButtonClicked(self):


        self._iCompIndex = self._iCompIndex - 1
        if self._iCompIndex < 0:
            # reset to beginning
            self._iCompIndex = 0
        
        self.EnableButtons()
        
        self.DisplayPage()


    #-----------------------------------------------

    def CaptureResponsesForPage(self):
        
        # set defaults 
        bResponsesCapturedForPage = True
        sMsg = ''
            

        for indQSet in range(len(self._loQuestionSets)):
            oQuestionSet = self._loQuestionSets[indQSet]
            loQuestions = []
            loQuestions = oQuestionSet.GetQuestionList()
            
            lsResponsesForOptions = []
            for indQuestion in range(len(loQuestions)):
                oQuestion = loQuestions[indQuestion]
                bResponseCapturedForQuestion = False
                
                bResponseCapturedForQuestion, lsResponsesForOptions, sMsg = oQuestion.CaptureResponse()


                if bResponseCapturedForQuestion == True:                
                    # add response element to proper node
                    for indOption in range(len(lsResponsesForOptions)):
                        xOptionNode = self.GetOptionNode( indQSet, indQuestion, indOption)
                        
#                         if not xOptionNode == None:
#                             self.AddResponseElement(xOptionNode, lsResponsesForOptions[indOption])
                else:
                    # something on the page was not entered
                    bResponsesCapturedForPage = False
                    break
                
        return bResponsesCapturedForPage, sMsg
                
       
    #-----------------------------------------------

    def WriteResponses(self):
        
        
        for indQSet in range(len(self._loQuestionSets)):
            oQuestionSet = self._loQuestionSets[indQSet]
            loQuestions = []
            loQuestions = oQuestionSet.GetQuestionList()
            
            lsResponsesForOptions = []
            for indQuestion in range(len(loQuestions)):
                oQuestion = loQuestions[indQuestion]
                bResponseCapturedForQuestion = False
                
                bResponseCapturedForQuestion, lsResponsesForOptions, sMsg = oQuestion.CaptureResponse()


                if bResponseCapturedForQuestion == True:                
                    # add response element to proper option node
                    for indOption in range(len(lsResponsesForOptions)):
                        xOptionNode = self.GetOptionNode( indQSet, indQuestion, indOption)
                        
                        if not xOptionNode == None:
                            self.AddResponseElement(xOptionNode, lsResponsesForOptions[indOption])

            
    #-----------------------------------------------

    def GetOptionNode(self, indQuestionSet, indQuestion, indOption):

        # get the element node for the option
        
        xOptionNode = None
        
        xQuestionSetNode = self._oIOXml.GetNthChild(self._xPageNode, 'QuestionSet', indQuestionSet)
        xQuestionNode = self._oIOXml.GetNthChild(xQuestionSetNode, 'Question', indQuestion)
        xOptionNode = self._oIOXml.GetNthChild(xQuestionNode, 'Option', indOption)
        
        
        return xOptionNode
        
    #-----------------------------------------------
    def AddResponseElement(self, xOptionNode, sResponse):
        
        
        dictAttrib = {}
        dictAttrib = {'time': self.sLoginTime}
        
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
            print(indCI)
            
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
                sTimestamp = self._oIOXml.GetValueOfNodeAttribute(xResponseNode, 'time')

                dtResponseTimestamp = datetime.strptime(sTimestamp, self.sTimestampFormat)
                if dtResponseTimestamp == dtLastLogin:
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
        if not iResumeCompIndex == self._iCompIndex:
            self._oMsgUtil.DisplayInfo('Resuming quiz from previous login session.')
            
        self._iCompIndex = iResumeCompIndex


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

            sTimestamp = self._oIOXml.GetValueOfNodeAttribute(xmlLoginNode, 'time')
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
            
