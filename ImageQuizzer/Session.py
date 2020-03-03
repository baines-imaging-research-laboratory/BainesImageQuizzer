import PythonQt
import os
import vtk, qt, ctk, slicer
import sys
import unittest
# from UtilsIOXml import *
from Utilities import *
from Question import *
from ImageView import *

import xml
from xml.dom import minidom
from slicer.util import EXIT_SUCCESS

#-----------------------------------------------

class Session:
    
    def __init__(self,  parent=None):
        self.sClassName = type(self).__name__
        self.parent = parent
        print('Constructor for Session')
        
        self.oIOXml = UtilsIOXml()
        self.oUtils = Utilities()
        self.lCompositeIndices = []
        self.iCompIndex = 0
        self.xRootNode = None
        
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

    #-----------------------------------------------

    def RunSetup(self, sXmlFilename, sUsername, mainLayout, quizLayout):
        self.sXmlFilename = sXmlFilename
        self.sUsername = sUsername
        self.quizLayout = quizLayout
        self.mainLayout = mainLayout
#         print(self.sXmlFilename)
#         print(self.sUsername)
        
        # TODO: create and add user-timestamp node
        # TODO: determine study status based on recorded answers
        
        
        # open xml and check for root node
        bSuccess, xRootNode = self.oIOXml.OpenXml(self.sXmlFilename,'Session')
        if not bSuccess:
            sErrorMsg = "ERROR", "Not a valid quiz - Root node name was not 'Session'"
            self.oUtils.DisplayError(sErrorMsg)

        else:
            self.xRootNode = xRootNode
            self.mainLayout.addWidget(self.btnNext)
            self.mainLayout.addWidget(self.btnPrevious)
            
            self.BuildCompositeIndexList()
            self.EnableButtons()
            self.DisplayPage()

            
            
    #-----------------------------------------------

    def BuildCompositeIndexList(self):
        # given the root of the xml document build composite list 
        # of indexes for each page and the question sets within
        oIOXml = UtilsIOXml()
        
        # get Page nodes
        xPages = oIOXml.GetChildren(self.xRootNode, 'Page')

        for iPageIndex in range(len(xPages)):
            # for each page - get number of question sets
            xPageNode = oIOXml.GetNthChild(self.xRootNode, 'Page', iPageIndex)
            xQuestionSets = oIOXml.GetChildren(xPageNode,'QuestionSet')
            
            for iQuestionSetIndex in range(len(xQuestionSets)):
                self.lCompositeIndices.append([iPageIndex, iQuestionSetIndex])
        

    #-----------------------------------------------

    def DisplayPage(self):
        # extract page and question set indices from the current composite index
        
        iPageIndex = self.lCompositeIndices[self.iCompIndex][0]
        iQuestionSetIndex = self.lCompositeIndices[self.iCompIndex][1]

        xNodePage = self.oIOXml.GetNthChild(self.xRootNode, 'Page', iPageIndex)
        xNodeQuestionSet = self.oIOXml.GetNthChild(xNodePage, 'QuestionSet', iQuestionSetIndex)
        
        oQuestionSet = QuestionSet()
        oQuestionSet.ExtractQuestionsFromXML(xNodeQuestionSet)
        
        # first clear any previous widgets (except push buttons)
        for i in reversed(range(self.quizLayout.count())):
#             x = self.quizLayout.itemAt(i).widget()
#             if not(isinstance(x, qt.QPushButton)):
            self.quizLayout.itemAt(i).widget().setParent(None)

        
        bBuildSuccess, qQuizWidget = oQuestionSet.BuildQuestionSetForm()
        if bBuildSuccess:
            self.quizLayout.addWidget(qQuizWidget)
        
        
        oImageView = ImageView()
        oImageView.RunSetup(xNodePage, qQuizWidget)
    
    #-----------------------------------------------
    
    def EnableButtons(self):
        
        # beginning of quiz
        if (self.iCompIndex == 0):
            self.btnNext.enabled = True
            self.btnPrevious.enabled = False

        # end of quiz
        elif (self.iCompIndex == len(self.lCompositeIndices) - 1):
            self.btnNext.enabled = True
            self.btnPrevious.enabled = True

        # somewhere in middle
        else:
            self.btnNext.enabled = True
            self.btnPrevious.enabled = True

        # assign button description           
        if (self.iCompIndex == len(self.lCompositeIndices) - 1):
            # last question of last image view
            self.btnNext.setText("Save and Finish")

        else:
            # assume multiple questions in the question set
            self.btnNext.setText("Next")
            # if last question in the question set - save answers and continue to next
            if not( self.lCompositeIndices[self.iCompIndex][0] == self.lCompositeIndices[self.iCompIndex + 1][0]):
                self.btnNext.setText("Save and Continue")

    #-----------------------------------------------

    def onNextButtonClicked(self):

        
        self.iCompIndex = self.iCompIndex + 1
        
        if self.iCompIndex > len(self.lCompositeIndices) -1:
            # the last question was answered - exit Slicer
            self.oUtils.DisplayInfo("Quiz complete .... Exit")
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

   
        
