import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from ImageQuizzer import *
from TestingStatus import *
from Utilities import *

import os
import sys

from pip._vendor.distlib._backport.shutil import copyfile

##########################################################################
#
# TestImageQuizzer
#
##########################################################################

class TestImageQuizzer(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    #------------------------------------------- 

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Test ImageQuizzer" 
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

class TestImageQuizzerWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """


    #------------------------------------------- 
    def setup(self):
        self.developerMode = True
        ScriptedLoadableModuleWidget.setup(self)


##########################################################################
#
# TestImageQuizzer_ModuleLogic
#
##########################################################################

class TestImageQuizzerLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget
    """

    def __init__(self):
        ScriptedLoadableModuleLogic.__init__(self)
        self.sClassName = type(self).__name__
        print("\n************ Unittesting for class ImageQuizzer ************\n")
        self.sessionTestStatus = TestingStatus()


##########################################################################
#
# TestImageQuizzer_ModuleTest
#
##########################################################################

class TestImageQuizzerTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self):
        
        moduleName = 'ImageQuizzer'

        self.ScriptedModulesPath = eval('slicer.modules.%s.path' % moduleName.lower())
        self.ScriptedModulesPath = os.path.dirname(self.ScriptedModulesPath)
        self.sXmlTestDataPath = os.path.join(self.ScriptedModulesPath, 'Testing', 'TestData', 'InputXmlFiles')
        self.sUsersBasePath = os.path.join(self.ScriptedModulesPath, 'Users','Tests')
        
        # check that a Test folder exists - if not, create it
        if not os.path.exists(self.sUsersBasePath):
            os.makedirs(self.sUsersBasePath)
        
        
    #------------------------------------------- 

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear(0)
        self.sClassName = type(self).__name__

        self.oUtilsMsgs = UtilsMsgs()
        sMsg = 'Under Construction'
        self.oUtilsMsgs.DisplayWarning(sMsg)
        

       
    #------------------------------------------- 

    def runTest(self ):
        """TODO: for this function to be automatically started with the 
            'Reload and Test' button in Slicer, there cannot be an extra argument here.
            I have the argument 'layout' to be able to display widgets as part of my testing. 
        """
        self.setUp()
        logic = TestImageQuizzerLogic()

        tupResults = []
#         tupResults.append(self.test_NoErrors_BuildImageQuizzer())

        
        logic.sessionTestStatus.DisplayTestResults(tupResults)
 

    #------------------------------------------- 

    def test_NoErrors_BuildImageQuizzer(self):
        bTestResult = True
        self.fnName = sys._getframe().f_code.co_name
        
#         # copy test file to user area
#         sTestFilename = 'Test_Laptop.xml'
#         sUserName = 'Tests'
#         sTestPath = os.path.join(self.sXmlTestDataPath, sTestFilename)
#         sNewPath = os.path.join(self.sUsersBasePath, sTestFilename)
#         
#         print(sTestPath)
#         print(sNewPath)
#         
#         copyfile(sTestPath, sNewPath)
#         
#         self.oImageQuizzer = ImageQuizzer()
#         self.oImageQuizzer.setup()

#         bTestResult = self.oSession.readPresentationInstructions()
        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 

##########################################################################################
#                      Launching from main (Reload and Test button)
##########################################################################################

def main(self):
    try:
        logic = TestImageQuizzerLogic()
        logic.runTest()
        
    except Exception as e:
        print(e)
    sys.exit(0)


if __name__ == "__main__":
    main()
