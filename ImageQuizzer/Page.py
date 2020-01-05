import PythonQt
import os
import vtk, qt, ctk, slicer
import sys
import unittest
from UtilsIOXml import *
from Question import *

import xml
from xml.dom import minidom

#-----------------------------------------------

class Page:
    
    def __init__(self,  parent=None):
        self.sClassName = type(self).__name__
        self.parent = parent
        print('Constructor for Page')
        self.name = ''
        self.descriptor = ''
        

    def RunSetup(self, xPageNode, quizLayout):

        self.quizLayout = quizLayout
        self.oIOXml = UtilsIOXml()

        # get name and descriptor
        sName = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'name')
        sDescriptor = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'descriptor')
        print(sName, '    ' , sDescriptor)

        # get Question Sets

        # get Question Set nodes
        xQuestionSets = self.oIOXml.GetChildren(xPageNode, 'QuestionSet')
        iNumQuestionSets = self.oIOXml.GetNumChildren(xPageNode, 'QuestionSet')

        # for each 'outstanding' page (questions not yet answered)

        # display Images

        # display Question set
        # get number of question sets
        
        # display one set with next / back / save buttons
        for xNodeQuestionSet in xQuestionSets:

            oQuestionSet = QuestionSet()
            ltupQuestionSet = oQuestionSet.ExtractQuestionsFromXML(xNodeQuestionSet)
            bTestResultTF, qQuizWidget =oQuestionSet.BuildQuestionSetForm(ltupQuestionSet)
            self.quizLayout.addWidget(qQuizWidget)
        
            # Next button
            self.nextButton = qt.QPushButton("Next Question Set - same images")
            self.nextButton.toolTip = "Display next in series."
            self.nextButton.enabled = True
            self.quizLayout.addWidget(self.nextButton)
#             self.nextButton.connect('clicked(bool)',self.onNextButtonClicked)
            
            # Back button
            self.backButton = qt.QPushButton("Back")
            self.backButton.toolTip = "Display previous series."
            self.backButton.enabled = True
            self.quizLayout.addWidget(self.backButton)
        
        
        
