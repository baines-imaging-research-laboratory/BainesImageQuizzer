import PythonQt
import os
import vtk, qt, ctk, slicer
import sys
import unittest

from Utilities import *
from Question import *
from ImageView import *
#from ImageQuizzer import *

import xml
from xml.dom import minidom
from slicer.util import EXIT_SUCCESS

#-----------------------------------------------

class Session:
    
    def __init__(self,  parent=None):
        self.sClassName = type(self).__name__
        self.parent = parent
        print('Constructor for Session')
        
        self.oUtilsMsgs = UtilsMsgs()
        self.oIOXml = UtilsIOXml()
        self.iCompIndex = 0
        
        self._xRootNode = None
        self._lPageQuestionCompositeIndices = []
        
        
#         self.oUtilsIO = None
#         self.oQuizWidgets = None
        
    #-------------------------------------------
    #        Getters / Setters
    #-------------------------------------------

    def SetRootNode(self, xNode):
        self._xRootNode = xNode
        
    #----------
    def SetCompositeIndicesList(self,lIndices):
        self._lPageQuestionCompositeIndices = lIndices
        
    #----------
    def GetCompositeIndicesList(self):
        return self._lPageQuestionCompositeIndices


    #-------------------------------------------
    #        Functions
    #-------------------------------------------

    def RunSetup(self, oUtilsIO, oQuizWidgets):

        self.sXmlQuizPath = oUtilsIO.GetQuizPath()
        self.sUsername = oUtilsIO.GetQuizUsername()
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
        bSuccess, xRootNode = self.oIOXml.OpenXml(self.sXmlQuizPath,'Session')
        if not bSuccess:
            sErrorMsg = "ERROR", "Not a valid quiz - Root node name was not 'Session'"
            self.oUtilsMsgs.DisplayError(sErrorMsg)

        else:
            self._xRootNode = xRootNode
            self.slicerLeftMainLayout.addWidget(self.btnNext)
            self.slicerLeftMainLayout.addWidget(self.btnPrevious)
            
            self.BuildPageQuestionCompositeIndexList()
            self.EnableButtons()
            self.DisplayPage()


            
            
    #-----------------------------------------------

    def BuildPageQuestionCompositeIndexList(self):
        
        # This function collects the page and question set indices which
        #    are used to coordinate the next and previous buttons
        
        # given the root of the xml document build composite list 
        #     of indexes for each page and the question sets within
#         oIOXml = UtilsIOXml()
        
        # get Page nodes
        xPages = self.oIOXml.GetChildren(self._xRootNode, 'Page')

        for iPageIndex in range(len(xPages)):
            # for each page - get number of question sets
            xPageNode = self.oIOXml.GetNthChild(self._xRootNode, 'Page', iPageIndex)
            xQuestionSets = self.oIOXml.GetChildren(xPageNode,'QuestionSet')
            
            for iQuestionSetIndex in range(len(xQuestionSets)):
                self._lPageQuestionCompositeIndices.append([iPageIndex, iQuestionSetIndex])
        

    #-----------------------------------------------

    def DisplayPage(self):
        # extract page and question set indices from the current composite index
        
        iPageIndex = self._lPageQuestionCompositeIndices[self.iCompIndex][0]
        iQuestionSetIndex = self._lPageQuestionCompositeIndices[self.iCompIndex][1]

        xNodePage = self.oIOXml.GetNthChild(self._xRootNode, 'Page', iPageIndex)
        xNodeQuestionSet = self.oIOXml.GetNthChild(xNodePage, 'QuestionSet', iQuestionSetIndex)
        
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
        
        
        oImageView = ImageView()
        oImageView.RunSetup(xNodePage, qQuizWidget)
    
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

   
        
