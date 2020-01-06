import PythonQt
import os
import vtk, qt, ctk, slicer
import sys
import unittest
from UtilsIOXml import *
from Page import *

import xml
from xml.dom import minidom

#-----------------------------------------------

class Session:
    
    def __init__(self,  parent=None):
        self.sClassName = type(self).__name__
        self.parent = parent
        print('Constructor for Session')
        
        self.iPageIndex = 0
        self.iNumPages = 0

        # Next button
        self.btnNextPage = qt.QPushButton("Next Page - new images and question sets")
        self.btnNextPage.toolTip = "Display next page."
        self.btnNextPage.enabled = True
        self.btnNextPage.connect('clicked(bool)',self.onNextPageButtonClicked)
        

    def RunSetup(self, sXmlFilename, sUsername, mainLayout, quizLayout):
        self.sXmlFilename = sXmlFilename
        self.sUsername = sUsername
        self.quizLayout = quizLayout
        self.mainLayout = mainLayout
        print(self.sXmlFilename)
        print(self.sUsername)
        
        # TODO: create and add user-timestamp node
        # TODO: determine study status based on recorded answers
        
        
        self.oIOXml = UtilsIOXml()
        self.msgBox = qt.QMessageBox()
        # open xml and check for root node
        
        bSuccess, xRootNode = self.oIOXml.OpenXml(self.sXmlFilename,'Session')
        if not bSuccess:
            self.msgBox.critical(0,"ERROR", "Not a valid quiz - Root node name was not 'Session'")
        else:
        
            # get # of 'Pages'
            self.iNumPages = self.oIOXml.GetNumChildren(xRootNode, 'Page')
            print('Number of Pages %s' % self.iNumPages)
        
            
            # get Page nodes
            self.xPages = self.oIOXml.GetChildren(xRootNode, 'Page')
            xNodePage = self.oIOXml.GetNthChild(xRootNode, 'Page', self.iPageIndex)
            self.DisplayPage(xNodePage)
            self.EnablePageButtons()
            
            
#             # Back button
#             self.backButton = qt.QPushButton("Previous Page")
#             self.backButton.toolTip = "Display previous page."
#             self.backButton.enabled = True
#             self.quizLayout.addWidget(self.backButton)

    #-----------------------------------------------

    def DisplayPage(self, xNodePage):    
        # given a question set node, extract the information from the xml document
        # and add the widget to the layout
        
        # first clear any previous widgets (except push buttons)
        for i in reversed(range(self.quizLayout.count())):
#             x = self.quizLayout.itemAt(i).widget()
#             if not(isinstance(x, qt.QPushButton)):
            self.quizLayout.itemAt(i).widget().setParent(None)

        oPage = Page()
        oPage.RunSetup(xNodePage, self.quizLayout)
        
    #-----------------------------------------------

    def EnablePageButtons(self):
        # using the question set index display/enable the relevant buttons
         
        self.btnNextPage.enabled = True
#        self.btnNextQuestionSet.setvisible(True)
        self.mainLayout.addWidget(self.btnNextPage)

    #-----------------------------------------------

    def onNextPageButtonClicked(self):

        # enable buttons dependent on case

        # increase the question set index
        self.iPageIndex = self.iPageIndex + 1
        print('---Page Number %s' % self.iPageIndex)

        # display next set of questions
        if (self.iPageIndex < self.iNumPages):
            self.DisplayPage(self.xPages[self.iPageIndex])
            self.EnablePageButtons()
        else:
            self.btnNextPage.enabled = False






#-----------------------------------------------


# functions:
    # RunSession (not RunSetup?)
    # Create XML for writing
    # Process Page nodes
    # Create Status report
    # setup Tab Widget : Question set, Patient Info, Status
    # End Session, close any open files
    
        
