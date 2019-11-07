from abc import ABC, abstractmethod

import PythonQt
import os
import unittest
import vtk, qt, ctk, slicer
import sys
import warnings
#import urllib.request # import submodule directly


#-----------------------------------------------

class TargetItem(ABC):
    """ Inherits from ABC - Abstract Base Class
    """
    
    def __init__(self):
        self.sClassName = 'undefinedClassName'
        self.sFnName = 'undefinedFunctionName'

    
    @abstractmethod        
    def loadTarget(self, sTargetPath, dictProperties): pass
    
    def displayTarget(self, sTargetPath):
        print('Displaying Target Item')
        slicer.util.loadVolume(sTargetPath)

    
class Contour(TargetItem):
    # Create a group box and add radio buttons based on the options provided
    # Inputs : lOptions - list of labels for each radio button
    # Outputs: exitCode - boolean describing whether function exited successfully
    #          qGrpBox  - group box widget holding radio buttons
    
    def __init__(self):
        self.sClassName = type(self).__name__
        self.tupContourPoints = []
       
    def loadTarget(self, sTargetPath, dictProperties):
        self.sFnName = sys._getframe().f_code.co_name
        print('Loading target specific for Contour')
        return True

#-----------------------------------------------

class DataVolume(TargetItem):
    
    def __init__(self):
        self.sClassName = type(self).__name__
       
    def loadTarget(self, sTargetPath, dictProperties):
        self.sFnName = sys._getframe().f_code.co_name

        try:
            oNodeLoadedVolume = slicer.util.loadVolume(sTargetPath, dictProperties)
            return oNodeLoadedVolume
        except:
            print(self.sFnName , ': ' ,sys.exc_info()[0],\
                  '\n   *** ERROR - Either the file does not exist or there was a load error.\n   *** File: ',\
                  sTargetPath)
            return False
            