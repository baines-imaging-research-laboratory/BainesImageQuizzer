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
        
        self.oUtilsMsgs = UtilsMsgs()
        self.oIOXml = UtilsIOXml()
        self.oUtilsIO = UtilsIO()
        self.iCompIndex = 0
        
#         self._xRootNode = None
        self._lPageQuestionCompositeIndices = []
        self._xPageNode = None
        
        self._lQuestionSets = []
        
       
        
#         self.oUtilsIO = None
#         self.oQuizWidgets = None


#     def __del__(self):
#         print('Destructor Session')
#         self.RemoveNodes()
        
    #-------------------------------------------
    #        Getters / Setters
    #-------------------------------------------

#     def SetRootNode(self, xNode):
#         self._xRootNode = xNode
#         
#     #----------
#     def GetRootNode(self):
#         return self._xRootNode

    
    #----------
    def SetCompositeIndicesList(self,lIndices):
        self._lPageQuestionCompositeIndices = lIndices
        
    #----------
    def GetCompositeIndicesList(self):
        return self._lPageQuestionCompositeIndices


    #-------------------------------------------
    #        Functions
    #-------------------------------------------

    def RunSetup(self, oUtilsIO_fromLogin, oQuizWidgets):

        self.oUtilsIO = oUtilsIO_fromLogin  # capture IO object
        
        sXmlQuizPath = self.oUtilsIO.GetResourcesQuizPath()
        self.sUsername = self.oUtilsIO.GetQuizUsername()
        self.slicerLeftMainLayout = oQuizWidgets.GetSlicerLeftMainLayout()
        self.slicerQuizLayout = oQuizWidgets.GetSlicerQuizLayout()
#         print(self.sXmlQuizPath)
#         print(self.sUsername)
        
        # TODO: create and add user-timestamp node
        # TODO: determine study status based on recorded answers
        
        # create buttons
        
        # Next button
        self.btnNext = qt.QPushButton("Next")
        self.btnNext.toolTip = "Display next set of questions."
        self.btnNext.enabled = True
        self.btnNext.connect('clicked(bool)',self.onNextButtonClicked)
        
        # Back button
        self.btnPrevious = qt.QPushButton("Previous")
        self.btnPrevious.toolTip = "Display previous set of questions."
        self.btnPrevious.enabled = True
        self.btnPrevious.connect('clicked(bool)',self.onPreviousButtonClicked)

        
        # open xml and check for root node
        bSuccess, xRootNode = self.oIOXml.OpenXml(sXmlQuizPath,'Session')
        if not bSuccess:
            sErrorMsg = "ERROR", "Not a valid quiz - Root node name was not 'Session'"
            self.oUtilsMsgs.DisplayError(sErrorMsg)

        else:
#             self._xRootNode = xRootNode
            
            # add date time stamp to Session element
            self.AddSessionLoginTimestamp()
            
            self.slicerLeftMainLayout.addWidget(self.btnNext)
            self.slicerLeftMainLayout.addWidget(self.btnPrevious)
            
            self.BuildPageQuestionCompositeIndexList()
            self.EnableButtons()
            self.DisplayPage()


            
    #-----------------------------------------------

    def AddSessionLoginTimestamp(self):
        
        now = datetime.now()
        sLoginTime = now.strftime("%b-%d-%Y-%H-%M-%S")
        
#         print(sLoginTime)
        dictAttrib = {}
        dictAttrib = {'time': sLoginTime}
        
        sNullText = ''
        
        sUserQuizPath = self.oUtilsIO.GetUserQuizPath()
        self.oIOXml.AddElement(self.oIOXml.GetRootNode(),'Login', sNullText, dictAttrib)
        
        self.oIOXml.SaveXml(sUserQuizPath, self.oIOXml.GetXmlTree())
            
    #-----------------------------------------------

    def BuildPageQuestionCompositeIndexList(self):
        
        # This function collects the page and question set indices which
        #    are used to coordinate the next and previous buttons
        
        # given the root of the xml document build composite list 
        #     of indexes for each page and the question sets within
#         oIOXml = UtilsIOXml()
        
        # get Page nodes
#         xPages = self.oIOXml.GetChildren(self._xRootNode, 'Page')
        xPages = self.oIOXml.GetChildren(self.oIOXml.GetRootNode(), 'Page')

        for iPageIndex in range(len(xPages)):
            # for each page - get number of question sets
#             xPageNode = self.oIOXml.GetNthChild(self._xRootNode, 'Page', iPageIndex)
            xPageNode = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', iPageIndex)
            xQuestionSets = self.oIOXml.GetChildren(xPageNode,'QuestionSet')
            
            for iQuestionSetIndex in range(len(xQuestionSets)):
                self._lPageQuestionCompositeIndices.append([iPageIndex, iQuestionSetIndex])
        

    #-----------------------------------------------

    def DisplayPage(self):
        # extract page and question set indices from the current composite index
        
        iPageIndex = self._lPageQuestionCompositeIndices[self.iCompIndex][0]
        iQuestionSetIndex = self._lPageQuestionCompositeIndices[self.iCompIndex][1]

#         self._xPageNode = self.oIOXml.GetNthChild(self._xRootNode, 'Page', iPageIndex)
        self._xPageNode = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', iPageIndex)
        xNodeQuestionSet = self.oIOXml.GetNthChild(self._xPageNode, 'QuestionSet', iQuestionSetIndex)
        
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
            self._lQuestionSets.append(oQuestionSet)
        
        oImageView = ImageView()
        oImageView.RunSetup(self._xPageNode, qQuizWidget)
    
    #-----------------------------------------------
    
    def EnableButtons(self):
        
        # beginning of quiz
        if (self.iCompIndex == 0):
            self.btnNext.enabled = True
            self.btnPrevious.enabled = False

        # end of quiz
        elif (self.iCompIndex == len(self._lPageQuestionCompositeIndices) - 1):
            self.btnNext.enabled = True
            self.btnPrevious.enabled = True

        # somewhere in middle
        else:
            self.btnNext.enabled = True
            self.btnPrevious.enabled = True

        # assign button description           
        if (self.iCompIndex == len(self._lPageQuestionCompositeIndices) - 1):
            # last question of last image view
            self.btnNext.setText("Save and Finish")

        else:
            # assume multiple questions in the question set
            self.btnNext.setText("Next")
            # if last question in the question set - save answers and continue to next
            if not( self._lPageQuestionCompositeIndices[self.iCompIndex][0] == self._lPageQuestionCompositeIndices[self.iCompIndex + 1][0]):
                self.btnNext.setText("Save and Continue")

    #-----------------------------------------------

    def onNextButtonClicked(self):

        # check if a save is required before displaying next page
        sPrevText = self.btnNext.text
        print('(((((((( Prev Text: %s' %sPrevText)
        if "Save" in sPrevText:
            self.CaptureResponsesForPage()
            self._lQuestionSets = []
            
        
        self.iCompIndex = self.iCompIndex + 1
        
        if self.iCompIndex > len(self._lPageQuestionCompositeIndices) -1:
            # the last question was answered - exit Slicer
            self.oUtilsMsgs.DisplayInfo("Quiz complete .... Exit")
            slicer.util.exit(status=EXIT_SUCCESS)


        self.EnableButtons()

        self.DisplayPage()

    #-----------------------------------------------

    def onPreviousButtonClicked(self):


        self.iCompIndex = self.iCompIndex - 1
        if self.iCompIndex < 0:
            # reset to beginning
            self.iCompIndex = 0
        
        self.EnableButtons()
        
        self.DisplayPage()


    #-----------------------------------------------

    def CaptureResponsesForPage(self):
        
        print("                  SAVING Current respones for page %i )))))))" %self._lPageQuestionCompositeIndices[self.iCompIndex][0])
        i = self.oIOXml.GetNumChildrenByName(self._xPageNode, 'QuestionSet')
        print('---------- %i QuestionSets' % i)
        
        # for the given page in the composite index, access all question set nodes
        
        
        # for each Question set, iterate over all questions and capture responses
#         xQuestionSets = self.oIOXml.GetChildren(self._xPageNode,'QuestionSet')
        
#         for indexQSet in range(len(xQuestionSets)):
#             iNumQuestions = self.oIOXml.GetNumChildrenByName(xQuestionSets, 'Question', indexQSet)
#             xQuestions = self.oIOXml.GetChildren(xQuestionSets, 'Question')
#             for indexQuestion in range(len(xQuestions)):
#                 xQ = self.oIOXml.GetNthChild(xQuestionSets, 'Question', indexQuestion)
#                 lResponses = xQ.CaptureResponse()
#                 print(lResponses)

        for qsIndex in range(len(self._lQuestionSets)):
            qs = self._lQuestionSets[qsIndex]
            lQuestions = []
            lQuestions = qs.GetQuestionList()
            
            lResponses = []
            for qIndex in range(len(lQuestions)):
                q = lQuestions[qIndex]
                lResponses = q.CaptureResponse()
                
                # add response element to proper node
                for rIndex in range(len(lResponses)):
                    xOptionNode = self.GetOptionNode( qsIndex, qIndex, rIndex)
                    
                    if not xOptionNode == None:
                        self.AddResponseElement(xOptionNode, lResponses[rIndex])
                
       
            
    #-----------------------------------------------
    def GetOptionNode(self, indQuestionSet, indQuestion, indResponse):

        # get the element node for the option
        
        xOptionNode = None
        
        xQuestionSetNode = self.oIOXml.GetNthChild(self._xPageNode, 'QuestionSet', indQuestionSet)
        xQuestionNode = self.oIOXml.GetNthChild(xQuestionSetNode, 'Question', indQuestion)
        xOptionNode = self.oIOXml.GetNthChild(xQuestionNode, 'Option', indResponse)
        
        
        return xOptionNode
        
    #-----------------------------------------------
    def AddResponseElement(self, xOptionNode, sResponse):
        
        now = datetime.now()
        sLoginTime = now.strftime("%b-%d-%Y-%H-%M-%S")
        
#         print(sLoginTime)
        dictAttrib = {}
        dictAttrib = {'time': sLoginTime}
        
        sUserQuizPath = self.oUtilsIO.GetUserQuizPath()
        self.oIOXml.AddElement(xOptionNode,'Response', sResponse, dictAttrib)
        
        self.oIOXml.SaveXml(sUserQuizPath, self.oIOXml.GetXmlTree())
        
