import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
from Session import *

import numpy as np

import sys
import warnings
from pathlib import Path
import imp



# ------------------------------------------------------------------------------
# TestSession
#

class TestSession(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Test Session" 
        self.parent.categories = ["Testing.ImageQuizzer"]
        self.parent.dependencies = []
        self.parent.contributors = ["Carol Johnson (Baines Imaging Research Laboratories)"] 
        self.parent.helpText = """
        This is an example of scripted loadable module bundled in an extension.
        It performs a simple thresholding on the input volume and optionally captures a screenshot.
        """
        self.parent.helpText += self.getDefaultModuleDocumentationLink()
        self.parent.acknowledgementText = """
        This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
        and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
        """ # replace with organization, grant and thanks.

        try:
            slicer.selfTests
        except AttributeError:
            slicer.selfTests = {}
        slicer.selfTests['TestSession'] = self.runTest


    #------------------------------------------- 
    def runTest(self, msec=100, **kwargs):
        tester = TestSessionTest()
        tester.runTest()
        


# ------------------------------------------------------------------------------
# TestSessionWidget
#

class TestSessionWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    #------------------------------------------- 
    def setup(self):
        self.developerMode = True
        ScriptedLoadableModuleWidget.setup(self)
        

# ------------------------------------------------------------------------------
# TestSessionLogic
#
class TestSessionLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget
    """

    def __init__(self):
        ScriptedLoadableModuleLogic.__init__(self)
        self.sClassName = type(self).__name__
        print("\n************ Unittesting for class Session ************\n")

    #------------------------------------------- 
    def DisplayTestResults(self, tupResults):
        
        if (len(tupResults) > 0):
            # print the boolean results for each test
            self.tupResults = tupResults
            print('--- Test Results ' + ' --------- ' + self.sClassName + ' functions -----')
            for i in range(len(tupResults)):
                success = False   # assume fail
                sFname, success = tupResults[i]
                if success == True:
                    sDisplay = "Ahh....... test passed.    : "
                else:
                    sDisplay = "!$!*^&#!@$%! Test Failed!! : "
                print(sDisplay, i+1, sFname)
        else:
            print("No results to report")

        print("\n************ Test Complete ************\n")


# ------------------------------------------------------------------------------
# TestSessionTest
#
class TestSessionTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    #------------------------------------------- 
    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear(0)
        self.sClassName = type(self).__name__

        # define path for test data
        moduleName = 'ImageQuizzer'
        scriptedModulesPath = eval('slicer.modules.%s.path' % moduleName.lower())
        scriptedModulesPath = os.path.dirname(scriptedModulesPath)
        self.testDataPath = os.path.join(scriptedModulesPath, 'Testing', 'TestData')

        

       
    #------------------------------------------- 
    def runTest(self ):
        """TODO: for this function to be automatically started with the 
            'Reload and Test' button in Slicer, there cannot be an extra argument here.
            I have the argument 'layout' to be able to display widgets as part of my testing. 
        """
        self.setUp()
        logic = TestSessionLogic()

        tupResults = []
        tupResults.append(self.test_NoErrors_BuildSession())

        
        logic.DisplayTestResults(tupResults)
 

    

    #------------------------------------------- 
    def test_NoErrors_BuildSession(self):
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name
        
        self.oSession = Session()
        bTestResult = self.oSession.readPresentationInstructions()
        tupResult = self.fnName, bTestResult
        return tupResult


##########################################################################################
#                      Launching from main (Reload and Test button)
##########################################################################################

def main(self):
    try:
        logic = TestSessionLogic()
        logic.runTest()
        
    except Exception as e:
        print(e)
    sys.exit(0)


if __name__ == "__main__":
    main()
