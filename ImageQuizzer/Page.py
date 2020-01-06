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
        self.btnPreviousQuestionSet = qt.QPushButton("Back")
        self.btnPreviousQuestionSet.toolTip = "Display previous question set."
        self.btnPreviousQuestionSet.enabled = False
        self.btnPreviousQuestionSet.connect('clicked(bool)', self.onPreviousQuestionSetClicked)

        # Save button
        self.btnSaveQuestionSet = qt.QPushButton("Save")
        self.btnSaveQuestionSet.toolTip = "Save Question Set responses."
        self.btnSaveQuestionSet.enabled = False
        self.btnSaveQuestionSet.connect('clicked(bool)', self.onSaveQuestionSetClicked)
        

    #-----------------------------------------------

    def RunSetup(self, xPageNode, quizLayout):

        self.quizLayout = quizLayout
        self.oIOXml = UtilsIOXml()


        # get name and descriptor
        sName = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'name')
        sDescriptor = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'descriptor')
        print(sName, '    ' , sDescriptor)

        self.quizLayout.addWidget(self.btnNextQuestionSet)
        self.quizLayout.addWidget(self.btnPreviousQuestionSet)
        self.quizLayout.addWidget(self.btnSaveQuestionSet)

        # for each 'outstanding' page (questions not yet answered)

        # display Images


        # get Question Set nodes and number of sets
        self.xQuestionSets = self.oIOXml.GetChildren(xPageNode, 'QuestionSet')
        self.iNumQuestionSets = self.oIOXml.GetNumChildren(xPageNode, 'QuestionSet')

        
        self.DisplayQuestionSet(self.xQuestionSets[self.iQuestionSetIndex])

        # enable buttons
        self.EnableQuestionSetButtons()
        
            
        
    #-----------------------------------------------

    def DisplayQuestionSet(self, xNodeQuestionSet):    
        # given a question set node, extract the information from the xml document
        # and add the widget to the layout
        
        # first clear any previous widgets (except push buttons)
            for i in reversed(range(self.quizLayout.count())):
                x = self.quizLayout.itemAt(i).widget()
                if not(isinstance(x, qt.QPushButton)):
                    self.quizLayout.itemAt(i).widget().setParent(None)

            oQuestionSet = QuestionSet()
            ltupQuestionSet = oQuestionSet.ExtractQuestionsFromXML(xNodeQuestionSet)
            bTestResultTF, qQuizWidget = oQuestionSet.BuildQuestionSetForm(ltupQuestionSet)
            self.quizLayout.addWidget(qQuizWidget)
        
    #-----------------------------------------------

    def EnableQuestionSetButtons(self):
        # using the question set index display/enable the relevant buttons
        
        print('---Question Set Number %s' % self.iQuestionSetIndex)
        # Case : only one Question set
        if (self.iQuestionSetIndex == 0 and self.iNumQuestionSets == 1):
            self.btnNextQuestionSet.enabled = False
            self.btnPreviousQuestionSet.enabled = False
            self.btnSaveQuestionSet.enabled = True
        else:
            # Case : first Question Set and more to follow
            if (self.iQuestionSetIndex == 0 and self.iNumQuestionSets > 1):
                self.btnNextQuestionSet.enabled = True
                self.btnPreviousQuestionSet.enabled = False
                self.btnSaveQuestionSet.enabled = False
            else:
                # Case : last Question Set with a number of previous sets
                if (self.iQuestionSetIndex == self.iNumQuestionSets - 1 and self.iNumQuestionSets > 1):
                    self.btnNextQuestionSet.enabled = False
                    self.btnPreviousQuestionSet.enabled = True
                    self.btnSaveQuestionSet.enabled = True
                else:
                    # Case : middle of number of question sets
                    if (self.iQuestionSetIndex > 0 and self.iQuestionSetIndex < self.iNumQuestionSets):
                        self.btnNextQuestionSet.enabled = True
                        self.btnPreviousQuestionSet.enabled = True
                        self.btnSaveQuestionSet.enabled = False
                        
        
        
         

    #-----------------------------------------------

    def onNextQuestionSetClicked(self):

        # enable buttons dependent on case

        # increase the question set index
        self.iQuestionSetIndex = self.iQuestionSetIndex + 1
        

#         # display next set of questions
#         if (self.iQuestionSetIndex < self.iNumQuestionSets):
#             self.btnPreviousQuestionSet.enabled = True
#             self.DisplayQuestionSet(self.xQuestionSets[self.iQuestionSetIndex])
#             self.EnableQuestionSetButtons()
#         else:
#             self.btnNextQuestionSet.enabled = False

        self.EnableQuestionSetButtons()
        if (self.iQuestionSetIndex < self.iNumQuestionSets - 1):
            self.DisplayQuestionSet(self.xQuestionSets[self.iQuestionSetIndex])
        
    #-----------------------------------------------

    def onPreviousQuestionSetClicked(self):

        # enable buttons dependent on case

        # decrease the question set index
        self.iQuestionSetIndex = self.iQuestionSetIndex - 1

#         # display previous set of questions
#         if (self.iQuestionSetIndex >= 0):
#             self.btnNextQuestionSet.enabled = True
#             self.DisplayQuestionSet(self.xQuestionSets[self.iQuestionSetIndex])
#             self.EnableQuestionSetButtons()
#         else:
#             self.btnPreviousQuestionSetQuestionSet.enabled = False

        self.EnableQuestionSetButtons()
        if (self.iQuestionSetIndex >= 0):
            self.DisplayQuestionSet(self.xQuestionSets[self.iQuestionSetIndex])


    #-----------------------------------------------

    def onSaveQuestionSetClicked(self):

        print('---Saving Question Set responses')
        #TODO: perform save ???
        
        # clear widget for Next Page
        for i in reversed(range(self.quizLayout.count())):
            self.quizLayout.itemAt(i).widget().setParent(None)


