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
            #     - create page object - with page node as variable
                oPage = Page()
                oPage.RunSetup(xPageNode)
                
        
        
#-----------------------------------------------


# functions:
    # RunSession (not RunSetup?)
    # Create XML for writing
    # Process Page nodes
    # Create Status report
    # setup Tab Widget : Question set, Patient Info, Status
    # End Session, close any open files
    
        
