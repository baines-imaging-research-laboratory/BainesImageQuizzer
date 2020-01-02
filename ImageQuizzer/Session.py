import PythonQt
import os
import vtk, qt, ctk, slicer
import sys
import unittest
from   UtilsIOXml import *

import xml
from xml.dom import minidom

#-----------------------------------------------

class Session:
    
    def __init__(self,  parent=None):
        self.sClassName = type(self).__name__
        self.parent = parent
        print('Constructor for Session')
        

    def RunSetup(self, sXmlFilename, sUsername):
        self.sXmlFilename = sXmlFilename
        self.sUsername = sUsername
        print(self.sXmlFilename)
        print(self.sUsername)
        
        # TODO: create and add user-timestamp node
        # TODO: determine study status based on recorded answers
        
        
        self.oIOXml = UtilsIOXml()
        self.msgBox = qt.QMessageBox()
        # open xml and check for root node
#         xmlQuizDoc = minidom.parse(self.sXmlFilename)
        
        bSuccess, xRootNode = self.oIOXml.OpenXml(self.sXmlFilename,'Session')
        if not bSuccess:
            self.msgBox.critical(0,"ERROR", "Not a valid quiz - Root node name was not 'Session'")
        else:
        
            # get # of 'Pages'
            iNumPages = self.oIOXml.GetNumChildren(xRootNode, 'Page')
            print('Number of Pages %s' % iNumPages)
        
            
            # get Page nodes
            xPages = self.oIOXml.GetChildren(xRootNode, 'Page')
            
            # for each 'outstanding' page
            for xPageNode in xPages:
                sName = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'name')
                sDescriptor = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'descriptor')
                print(sName, '    ' , sDescriptor)
            #     - create page object - with page node as variable
        
        
        
        
    #------------------------------------------- 
#     def readPresentationInstructions(self):
#         #
#         # This function reads in the set of instructions defining the flow of the quiz.
#         # i.e. What target to display and what question set goes with it.
#         #
#         print("Read in quiz flow instructions for the session")
# 
#         #
#         # open xml file and load into a document
# #         mydoc = minidom.parse('D:\\Users\\cjohnson\\Work\\Projects\\SlicerEclipseProjects\\ImageQuizzerProject\\ImageQuizzer\\Testing\\TestData\\InputXmlFiles\\items.xml')
#         mydoc = minidom.parse(self.sXmlFilename)
# #        mydoc = minidom.parse('D:\\BainesWork\\Slicer\\SlicerProjectWeek2019\\ImageQuizzerProject\\ImageQuizzer\\Testing\\TestData\\InputXmlFiles\\items.xml')
#         
#         items = mydoc.getElementsByTagName('infoPiece')
#         
#         print('Item 2 attribute:')
#         print(items[1].attributes['descriptor'].value)
# 
#         # all item attributes
#         print('\nAll attributes:')
#         for elem in items:
#             print(elem.attributes['descriptor'].value)
#         
#         # one specific item's data
#         print('\nItem #2 data:')
#         print(items[1].firstChild.data)
#         print(items[1].childNodes[0].data)
#         
#         # all items data
#         print('\nAll item data:')
#         for elem in items:
#             print(elem.firstChild.data)
# 
#         
# #         mydoc2 = minidom.parse('D:\\Users\\cjohnson\\Work\\Projects\\SlicerEclipseProjects\\ImageQuizzerProject\\ImageQuizzer\\Testing\\TestData\\InputXmlFiles\\Test1.xml')
# # #         mydoc2 = minidom.parse('D:\\BainesWork\\Slicer\\SlicerProjectWeek2019\\ImageQuizzerProject\\ImageQuizzer\\Testing\\TestData\\InputXmlFiles\\Test1.xml')
# #         targets = mydoc2.getElementsByTagName('Target')
# #         print ('\n*******\nTarget attributes:')
# #         print(targets[1].attributes['name'].value)
# #         print(targets[1].attributes['descriptor'].value)
# #         print(targets[0].attributes['name'].value)
# #         print(targets[0].attributes['descriptor'].value)
#         
#         return True