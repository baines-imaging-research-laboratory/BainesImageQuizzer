import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from Session import *
from TestingStatus import *

import os
import sys


##########################################################################
#
# TestSession
#
##########################################################################

class TestSession(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    #------------------------------------------- 

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Test Session" 
        self.parent.categories = ["Testing.ImageQuizzer"]
        self.parent.dependencies = []
        self.parent.contributors = ["Carol Johnson (Baines Imaging Research Laboratories)"] 
        self.parent.helpText = """
        This tests building a session - reading in instructions how the session will be run 
        through an xml file.
        """
        self.parent.helpText += self.getDefaultModuleDocumentationLink()
        self.parent.acknowledgementText = """
        This file was originally developed by Carol Johnson of the Baines Imaging Research Laboratories, 
        under the supervision of Dr. Aaron Ward
        """ 


##########################################################################
#
# TestQuestionSet_ModuleWidget
#
##########################################################################

class TestSessionWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    #------------------------------------------- 
    def setup(self):
        self.developerMode = True
        ScriptedLoadableModuleWidget.setup(self)


##########################################################################
#
# TestSession_ModuleLogic
#
##########################################################################

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
        self.sessionTestStatus = TestingStatus()


##########################################################################
#
# TestSession_ModuleTest
#
##########################################################################

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

        
        logic.sessionTestStatus.DisplayTestResults(tupResults)
 

    #------------------------------------------- 

    def test_NoErrors_BuildSession(self):
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name
        
        self.oSession = Session()
        bTestResult = self.oSession.readPresentationInstructions()
        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 

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