from abc import ABC, abstractmethod

import PythonQt
import os
import unittest
import vtk, qt, ctk, slicer
import sys
import warnings
#import urllib.request # import submodule directly


#-----------------------------------------------

class Page(ABC):
    """ Inherits from ABC - Abstract Base Class
    """
    
    def __init__(self):
        self.sClassName = 'undefinedClassName'
        self.sFnName = 'undefinedFunctionName'

    
    @abstractmethod        
    def loadImage(self, sTargetPath, dictProperties): pass
    
    def displayImage(self, sTargetPath):
        print('Displaying Page')
        slicer.util.loadVolume(sTargetPath)

    
#-----------------------------------------------

class Contour(Page):
    # Create a group box and add radio buttons based on the options provided
    # Inputs : lOptions - list of labels for each radio button
    # Outputs: exitCode - boolean describing whether function exited successfully
    #          qGrpBox  - group box widget holding radio buttons
    
    def __init__(self):
        self.sClassName = type(self).__name__
        self.tupContourPoints = []
       
    def loadImage(self, sImagePath, dictProperties):
        self.sFnName = sys._getframe().f_code.co_name
        print('Loading image:  Contour')
        return True

#-----------------------------------------------

class DataVolume(Page):
    
    def __init__(self):
        self.sClassName = type(self).__name__
       
    def loadImage(self, sImagePath, dictProperties):
        self.sFnName = sys._getframe().f_code.co_name

        try:
            oNodeLoadedVolume = slicer.util.loadVolume(sImagePath, dictProperties)
            return oNodeLoadedVolume
        except:
            print(self.sFnName , ': ' ,sys.exc_info()[0],\
                  '\n   *** ERROR - Either the file does not exist or there was a load error.\n   *** File: ',\
                  sImagePath)
            return False
            