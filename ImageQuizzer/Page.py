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
        self.iQuestionSetIndex = 0
        self.iNumQuestionSets = 0
        
        # Next button
        self.btnNextQuestionSet = qt.QPushButton("Next Question Set - same images")
        self.btnNextQuestionSet.toolTip = "Display next question set."
        self.btnNextQuestionSet.enabled = False
        self.btnNextQuestionSet.connect('clicked(bool)', self.onNextQuestionSetClicked)

        # Back button
#         self.btnPreviousQuestionSet = qt.QPushButton("Back")
#         self.btnPreviousQuestionSet.toolTip = "Display previous question set."
#         self.btnPreviousQuestionSet.enabled = False
#         self.btnNextQuestionSet.hide()
#         self.quizLayout.addWidget(self.btnPreviousQuestionSet)


    #-----------------------------------------------

    def RunSetup(self, xPageNode, quizLayout):

        self.quizLayout = quizLayout
        self.oIOXml = UtilsIOXml()

        # get name and descriptor
        sName = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'name')
        sDescriptor = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'descriptor')
        print(sName, '    ' , sDescriptor)

        # get Question Sets

        # get Question Set nodes
        self.xQuestionSets = self.oIOXml.GetChildren(xPageNode, 'QuestionSet')

        # for each 'outstanding' page (questions not yet answered)

        # display Images

        # display Question set
        # get number of question sets
        
        # display one set with next / back / save buttons
        self.iNumQuestionSets = self.oIOXml.GetNumChildren(xPageNode, 'QuestionSet')
        
        
        print('~~~~~Question Set ID~~~~~')
        print(self.oIOXml.GetValueOfNodeAttribute(self.xQuestionSets[self.iQuestionSetIndex],'id'))
        
        # first clear any previous widgets from the layout
        self.DisplayQuestionSet(self.xQuestionSets[self.iQuestionSetIndex])
        self.EnableQuestionSetButtons()
        
            
        
    #-----------------------------------------------

    def DisplayQuestionSet(self, xNodeQuestionSet):    
        # given a question set node, extract the information from the xml document
        # and add the widget to the layout
        
        # first clear any previous widgets
            for i in reversed(range(self.quizLayout.count())):
                self.quizLayout.itemAt(i).widget().setParent(None)

            oQuestionSet = QuestionSet()
            ltupQuestionSet = oQuestionSet.ExtractQuestionsFromXML(xNodeQuestionSet)
            bTestResultTF, qQuizWidget = oQuestionSet.BuildQuestionSetForm(ltupQuestionSet)
            self.quizLayout.addWidget(qQuizWidget)
        
    #-----------------------------------------------

    def EnableQuestionSetButtons(self):
        # using the question set index display/enable the relevant buttons
         
        self.btnNextQuestionSet.enabled = True
#        self.btnNextQuestionSet.setvisible(True)
        self.quizLayout.addWidget(self.btnNextQuestionSet)

    #-----------------------------------------------

    def onNextQuestionSetClicked(self):

        # enable buttons dependent on case

        # increase the question set index
        self.iQuestionSetIndex = self.iQuestionSetIndex + 1
        print('---Question Set Number %s' % self.iQuestionSetIndex)

        # display next set of questions
        if (self.iQuestionSetIndex < self.iNumQuestionSets):
            self.DisplayQuestionSet(self.xQuestionSets[self.iQuestionSetIndex])
            self.EnableQuestionSetButtons()
        else:
            self.btnNextQuestionSet.enabled = False



