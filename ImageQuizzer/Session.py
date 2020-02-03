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

#-----------------------------------------------

class Session:
    
    def __init__(self,  parent=None):
        self.sClassName = type(self).__name__
        self.parent = parent
        print('Constructor for Session')
        
#         self.iPageIndex = 0
#         self.iNumPages = 0
#         self.iQuestionSetIndex = 0
#         self.iNumQuestionSets = 0
#         self.lQuestionSets = []

        self.oIOXml = UtilsIOXml()
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

        # Save button
        self.btnSave = qt.QPushButton("Save")
        self.btnSave.toolTip = "Save responses."
        self.btnSave.enabled = True
        self.btnSave.connect('clicked(bool)',self.onSaveButtonClicked)


    def RunSetup(self, sXmlFilename, sUsername, mainLayout, quizLayout):
        self.sXmlFilename = sXmlFilename
        self.sUsername = sUsername
        self.quizLayout = quizLayout
        self.mainLayout = mainLayout
        print(self.sXmlFilename)
        print(self.sUsername)
        
        # TODO: create and add user-timestamp node
        # TODO: determine study status based on recorded answers
        
        
        self.msgBox = qt.QMessageBox()
        # open xml and check for root node
        
        bSuccess, xRootNode = self.oIOXml.OpenXml(self.sXmlFilename,'Session')
        if not bSuccess:
            self.msgBox.critical(0,"ERROR", "Not a valid quiz - Root node name was not 'Session'")
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
        self.btnNext.enabled = True
        self.btnPrevious.enabled = True
        self.btnSave.enabled = True

    #-----------------------------------------------

    def onNextButtonClicked(self):

        
        self.iCompIndex = self.iCompIndex + 1

        self.EnableButtons()

        if self.iCompIndex < len(self.lCompositeIndices):
            self.DisplayPage()

    #-----------------------------------------------

    def onPreviousButtonClicked(self):


        self.iCompIndex = self.iCompIndex - 1
        
        self.EnableButtons()
        
        if self.iCompIndex  >= 0:
            self.DisplayPage()


    #-----------------------------------------------

    def onSaveButtonClicked(self):

        print('---Saving responses')
        #TODO: perform save ???
        
        # clear widget for Next Page
        for i in reversed(range(self.quizLayout.count())):
            self.quizLayout.itemAt(i).widget().setParent(None)

    #-----------------------------------------------
    #-----------------------------------------------
# 
#     def BuildQuestionSetList(self,xNodePage):
#         # given a question set node, extract the information from the xml document
#         # and add the widget to the layout
# 
#         # get number of Question sets
#         self.iNumQuestionSets = self.oIOXml.GetNumChildren(xNodePage, 'QuestionSet')
#         #for each question set
#         for iIndex in range(self.iNumQuestionSets):
#             print('   *** Question set # %d' % iIndex)
#             xNodeQuestionSet = self.oIOXml.GetNthChild(xNodePage, 'QuestionSet', iIndex)
#             oQuestionSet = QuestionSet()
#             oQuestionSet.ExtractQuestionsFromXML(xNodeQuestionSet)
#             #append to list
#             self.lQuestionSets.append(oQuestionSet)
#         
#         
#     #-----------------------------------------------
# 
#     def DisplayQuestionSet(self):    
#         
#         # first clear any previous widgets (except push buttons)
#         for i in reversed(range(self.quizLayout.count())):
# #             x = self.quizLayout.itemAt(i).widget()
# #             if not(isinstance(x, qt.QPushButton)):
#             self.quizLayout.itemAt(i).widget().setParent(None)
# 
#         bBuildSuccess = False
#         bBuildSuccess, qQuizWidget = self.lQuestionSets[self.iQuestionSetIndex].BuildQuestionSetForm()
#         if bBuildSuccess:
#             self.quizLayout.addWidget(qQuizWidget)
# 
# 
# 
#     #-----------------------------------------------
# 
#     def EnableQuestionSetButtons(self):
#         # using the question set index display/enable the relevant buttons
#          
# 
# 
#         print('---Question Set Number %s' % self.iQuestionSetIndex)
#         # Case : only one Question Set
#         if (self.iQuestionSetIndex == 0 and self.iNumQuestionSets == 1):
#             self.btnNext.enabled = False
#             self.btnPrevious.enabled = False
#             self.btnSave.enabled = True
#         else:
#             # Case : first Question Set and more to follow
#             if (self.iQuestionSetIndex == 0 and self.iNumQuestionSets > 1):
#                 self.btnNext.enabled = True
#                 self.btnPrevious.enabled = False
#                 self.btnSave.enabled = False
#             else:
#                 # Case : last Question Set with a number of previous sets
#                 if (self.iQuestionSetIndex == self.iNumQuestionSets - 1 and self.iNumQuestionSets > 1):
#                     self.btnNext.enabled = False
#                     self.btnPrevious.enabled = True
#                     self.btnSave.enabled = True
#                 else:
#                     # Case : middle of number of Question Sets
#                     if (self.iQuestionSetIndex > 0 and self.iQuestionSetIndex < self.iNumQuestionSets):
#                         self.btnNext.enabled = True
#                         self.btnPrevious.enabled = True
#                         self.btnSave.enabled = False
#                         



# functions:
    # RunSession (not RunSetup?)
    # Create XML for writing
    # Process Page nodes
    # Create Status report
    # setup Tab Widget : Question set, Patient Info, Status
    # End Session, close any open files
    
        
