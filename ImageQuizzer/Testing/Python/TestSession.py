import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from Session import *
from TestingStatus import *
from Utilities import *

import xml.dom.minidom

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

    def __init__(self):
        
        self.sModuleName = 'ImageQuizzer'
        self.sUsername = 'Tests'
        self.sSourceDirForQuizTests = 'Testing/TestData/Test_Session'

        
        self._oFilesIO = None
        
        
    #------------------------------------------- 

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear(0)
        self.sClassName = type(self).__name__

        self._oFilesIO = UtilsIO()
        self._oFilesIO.SetModuleDirs(self.sModuleName, self.sSourceDirForQuizTests)
        self._oFilesIO.SetQuizUsername(self.sUsername)
        self._oFilesIO.SetUserDir()

        self._oIOXml = UtilsIOXml()

    #------------------------------------------- 

    def runTest(self ):
        """TODO: for this function to be automatically started with the 
            'Reload and Test' button in Slicer, there cannot be an extra argument here.
            I have the argument 'layout' to be able to display widgets as part of my testing. 
        """
        self.setUp()
        logic = TestSessionLogic()

        tupResults = []
        tupResults.append(self.test_BuildPageQuestionCompositeIndexList())

#         bTestResult = self.oSession.readPresentationInstructions()

        
        logic.sessionTestStatus.DisplayTestResults(tupResults)
 

    #------------------------------------------- 

    def test_BuildPageQuestionCompositeIndexList(self):
        bTestResult = True
        self.fnName = sys._getframe().f_code.co_name
        
        # copy test file to user area
        sTestFilename = 'Test_PageQuestions_GenericPath.xml'
        sTestPath = os.path.join(self._oFilesIO.GetXmlResourcesDir(), sTestFilename)
        
        
        [bOpenResult, self.xRootNode] = self._oIOXml.OpenXml(sTestPath, 'Session')
        self._oIOXml.SetRootNode(self.xRootNode)
        
        lExpectedCompositeIndices = []
        lExpectedCompositeIndices.append([0,0])
        lExpectedCompositeIndices.append([0,1])
        lExpectedCompositeIndices.append([1,0])
        lExpectedCompositeIndices.append([2,0])
        
        
        self.oSession = Session()
        self.oSession.SetFilesIO(self._oFilesIO)
        self.oSession.SetIOXml(self._oIOXml)
        self.oSession.BuildPageQuestionCompositeIndexList()
        lCompositeIndicesResult = self.oSession.CompositeIndicesList()
        
        if lCompositeIndicesResult == lExpectedCompositeIndices :
            bTestResult = True
        else:
            bTestResult = False
            
        # set quiz as complete for test purposes - so as not to trigger error message
        self.oSession.SetQuizComplete(True)

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
