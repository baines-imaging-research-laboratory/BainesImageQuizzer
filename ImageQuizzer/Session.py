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

        self.iCompIndex = 0
        
#         self._xRootNode = None
        self._lPageQuestionCompositeIndices = []
        self._xPageNode = None
        
        self._lQuestionSets = []
        
       
        
        self._oIOXml = None
        self._oFilesIO = None
        self._oQuizWidgets = None
        
        self._btnNext = None
        self._btnPrevious = None


#     def __del__(self):
#         print('Destructor Session')
#         self.RemoveNodes()
        
    #-------------------------------------------
    #        Getters / Setters
    #-------------------------------------------

    #----------
    def SetFilesIO(self, oFilesIO):
        self._oFilesIO = oFilesIO

    #----------
    def SetIOXml(self, oIOXml):
        self._oIOXml = oIOXml

#     #----------
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

    def RunSetup(self, oFilesIO, oQuizWidgets):
        
        self._oIOXml = UtilsIOXml()
        self.SetFilesIO(oFilesIO)
        self.SetupWidgets(oQuizWidgets)
        self.SetupButtons()

        # open xml and check for root node
        bSuccess, xRootNode = self._oIOXml.OpenXml(self._oFilesIO.GetResourcesQuizPath(),'Session')

        if not bSuccess:
            sErrorMsg = "ERROR", "Not a valid quiz - Root node name was not 'Session'"
            self.oUtilsMsgs.DisplayError(sErrorMsg)

        else:
            # add date time stamp to Session element
            self.AddSessionLoginTimestamp()
            
            self.slicerLeftMainLayout.addWidget(self._btnNext)
            self.slicerLeftMainLayout.addWidget(self._btnPrevious)



        self.BuildPageQuestionCompositeIndexList()
        self.EnableButtons()
        self.DisplayPage()


    #-----------------------------------------------

   
    
    
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
        sLoginTime = now.strftime("%b-%d-%Y-%H-%M-%S")
        
#         print(sLoginTime)
        dictAttrib = {}
        dictAttrib = {'time': sLoginTime}
        
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
                self._lPageQuestionCompositeIndices.append([iPageIndex, iQuestionSetIndex])
        

    #-----------------------------------------------

    def DisplayPage(self):
        # extract page and question set indices from the current composite index
        
        iPageIndex = self._lPageQuestionCompositeIndices[self.iCompIndex][0]
        iQuestionSetIndex = self._lPageQuestionCompositeIndices[self.iCompIndex][1]

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
            self._lQuestionSets.append(oQuestionSet)
        
        oImageView = ImageView()
        oImageView.RunSetup(self._xPageNode, qQuizWidget)
    
    #-----------------------------------------------
    
    def EnableButtons(self):
        
        # beginning of quiz
        if (self.iCompIndex == 0):
            self._btnNext.enabled = True
            self._btnPrevious.enabled = False

        # end of quiz
        elif (self.iCompIndex == len(self._lPageQuestionCompositeIndices) - 1):
            self._btnNext.enabled = True
            self._btnPrevious.enabled = True

        # somewhere in middle
        else:
            self._btnNext.enabled = True
            self._btnPrevious.enabled = True

        # assign button description           
        if (self.iCompIndex == len(self._lPageQuestionCompositeIndices) - 1):
            # last question of last image view
            self._btnNext.setText("Save and Finish")

        else:
            # assume multiple questions in the question set
            self._btnNext.setText("Next")
            # if last question in the question set - save answers and continue to next
            if not( self._lPageQuestionCompositeIndices[self.iCompIndex][0] == self._lPageQuestionCompositeIndices[self.iCompIndex + 1][0]):
                self._btnNext.setText("Save and Continue")

    #-----------------------------------------------

    def onNextButtonClicked(self):

        # check if a save is required before displaying next page
        sPrevText = self._btnNext.text
#         print('(((((((( Prev Text: %s' %sPrevText)
        if "Save" in sPrevText:
            self.CaptureResponsesForPage()
            self._lQuestionSets = []
            
        
        self.iCompIndex = self.iCompIndex + 1
        
        if self.iCompIndex > len(self._lPageQuestionCompositeIndices) -1:
            # the last question was answered - exit Slicer
            self._oIOXml.SaveXml(self._oFilesIO.GetUserQuizPath(), self._oIOXml.GetXmlTree())
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
        
#         print("                  SAVING Current respones for page %i )))))))" %self._lPageQuestionCompositeIndices[self.iCompIndex][0])
        i = self._oIOXml.GetNumChildrenByName(self._xPageNode, 'QuestionSet')
#         print('---------- %i QuestionSets' % i)
        
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
        
        xQuestionSetNode = self._oIOXml.GetNthChild(self._xPageNode, 'QuestionSet', indQuestionSet)
        xQuestionNode = self._oIOXml.GetNthChild(xQuestionSetNode, 'Question', indQuestion)
        xOptionNode = self._oIOXml.GetNthChild(xQuestionNode, 'Option', indResponse)
        
        
        return xOptionNode
        
    #-----------------------------------------------
    def AddResponseElement(self, xOptionNode, sResponse):
        
        now = datetime.now()
        sLoginTime = now.strftime("%b-%d-%Y-%H-%M-%S")
        
        dictAttrib = {}
        dictAttrib = {'time': sLoginTime}
        
        sUserQuizPath = self._oFilesIO.GetUserQuizPath()
        self._oIOXml.AddElement(xOptionNode,'Response', sResponse, dictAttrib)
        
#         self.oIOXml.SaveXml(sUserQuizPath, self.oIOXml.GetXmlTree())
        
