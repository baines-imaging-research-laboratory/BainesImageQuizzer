import PythonQt
import os
import vtk, qt, ctk, slicer
import sys

import xml
from xml.dom import minidom

from Utilities import *


class ViewingNode:
    
    def __init__(self,  parent=None):
        self.sClassName = type(self).__name__
        self.parent = parent
        
        self.slViewNode = None
        self.sName = ''
        self.sDescriptor = ''
        self.sOrientation = ''
        self.sDestinationWindow = ''
        self.sImageType = ''
        self.sFormat = ''
        
    def RunSetup(self, xImages):

        self.oIOXml = UtilsIOXml()
        
    #-----------------------------------------------
    #         Manage Viewing Nodes
    #-----------------------------------------------

#     def BuildViewNode(self, xImage):
#         
#         
#         pass
    
    
        
        
        
