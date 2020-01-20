import PythonQt
import os
import vtk, qt, ctk, slicer
import sys
import unittest
# from UtilsIOXml import *
from Utilities import *
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
        
        # Back button
        self.btnPreviousPage = qt.QPushButton("Previous Page")
        self.btnPreviousPage.toolTip = "Display previous page."
        self.btnPreviousPage.enabled = True
        self.btnPreviousPage.connect('clicked(bool)',self.onPreviousPageButtonClicked)


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
        
            self.mainLayout.addWidget(self.btnNextPage)
            self.mainLayout.addWidget(self.btnPreviousPage)

            # get # of 'Pages'
            self.iNumPages = self.oIOXml.GetNumChildren(xRootNode, 'Page')
            print('Number of Pages %s' % self.iNumPages)
        
            
            # get Page nodes
            self.xPages = self.oIOXml.GetChildren(xRootNode, 'Page')
            xNodePage = self.oIOXml.GetNthChild(xRootNode, 'Page', self.iPageIndex)
           
        
            self.DisplayPage(xNodePage)
            self.EnablePageButtons()
            
            

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
         


        print('---Page Number %s' % self.iPageIndex)
        # Case : only one Page
        if (self.iPageIndex == 0 and self.iNumPages == 1):
            self.btnNextPage.enabled = False
            self.btnPreviousPage.enabled = False
#             self.btnSavePage.enabled = True
        else:
            # Case : first Page and more to follow
            if (self.iPageIndex == 0 and self.iNumPages > 1):
                self.btnNextPage.enabled = True
                self.btnPreviousPage.enabled = False
#                 self.btnSavePage.enabled = False
            else:
                # Case : last Page with a number of previous sets
                if (self.iPageIndex == self.iNumPages - 1 and self.iNumPages > 1):
                    self.btnNextPage.enabled = False
                    self.btnPreviousPage.enabled = True
#                     self.btnSavePage.enabled = True
                else:
                    # Case : middle of number of pages
                    if (self.iPageIndex > 0 and self.iPageIndex < self.iNumPages):
                        self.btnNextPage.enabled = True
                        self.btnPreviousPage.enabled = True
#                         self.btnSavePage.enabled = False
                        



    #-----------------------------------------------

    def onNextPageButtonClicked(self):

        # increase the question set index
        self.iPageIndex = self.iPageIndex + 1

#         # display next set of questions
#         if (self.iPageIndex < self.iNumPages):
#             self.DisplayPage(self.xPages[self.iPageIndex])
#             self.EnablePageButtons()
#         else:
#             self.btnNextPage.enabled = False


        # enable buttons dependent on case
        self.EnablePageButtons()

        # display the page
        if (self.iPageIndex < self.iNumPages):
            self.DisplayPage(self.xPages[self.iPageIndex])
        


    #-----------------------------------------------

    def onPreviousPageButtonClicked(self):

        # decrease the question set index
        self.iPageIndex = self.iPageIndex - 1

        # enable buttons dependent on case
        self.EnablePageButtons()

        # display the page
        if (self.iPageIndex >= 0):
            self.DisplayPage(self.xPages[self.iPageIndex])



#-----------------------------------------------


# functions:
    # RunSession (not RunSetup?)
    # Create XML for writing
    # Process Page nodes
    # Create Status report
    # setup Tab Widget : Question set, Patient Info, Status
    # End Session, close any open files
    
        
