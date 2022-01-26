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
        self.parent.categories = ["Baines Custom Modules.Testing_ImageQuizzer"]
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
        
        
        self._oFilesIO = None
        
        
    #------------------------------------------- 

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear(0)
        self.sClassName = type(self).__name__

        sModuleName = 'ImageQuizzer'

        self._oFilesIO = UtilsIO()

        # define path for test data
        self._oFilesIO.SetScriptedModulesPath(sModuleName)
        self.sBaseDirForTestData = os.path.join(self._oFilesIO.GetScriptedModulesPath(),'Testing\TestData')

        self.sTestDataDir = os.path.join(self.sBaseDirForTestData, 'Test_Session')

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
        tupResults.append(self.test_ShufflePageQuestionCompositeIndexList())
        tupResults.append(self.test_ShufflePageQuestionGroupCompositeIndexList())


        tupResults.append(self.test_ValidatePageGroupNumbers_MissingPageGroup())
        tupResults.append(self.test_ValidatePageGroupNumbers_InvalidNumber())
        tupResults.append(self.test_ValidatePageGroupNumbers_NotEnoughPageGroups())

        
        logic.sessionTestStatus.DisplayTestResults(tupResults)
 

    #------------------------------------------- 
    def test_BuildPageQuestionCompositeIndexList(self):
        bTestResult = True
        self.fnName = sys._getframe().f_code.co_name
        
        # copy test file to user area
        sTestFilename = 'Test_PageQuestions_GenericPath.xml'
        sTestPath = os.path.join(self.sTestDataDir, sTestFilename)
        
        
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
        lCompositeIndicesResult = self.oSession.GetCompositeIndicesList()
        
        if lCompositeIndicesResult == lExpectedCompositeIndices :
            bTestResult = True
        else:
            bTestResult = False
            
        # set quiz as complete for test purposes - so as not to trigger error message
        self.oSession.SetQuizComplete(True)

        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 
    def test_ShufflePageQuestionCompositeIndexList(self):
        bTestResult = True
        self.fnName = sys._getframe().f_code.co_name
        
        # build page/question set composite indices list for testing
        '''
            eg.     Original XML List           Randomized Page indices          Shuffled Composite List
                       Page   QS                         Indices                      Page   QS
                       0      0                             3                         3      0
                       0      1                             0                         0      0
                       1      0                             2                         0      1
                       2      0                             4                         2      0
                       2      1                             1                         2      1
                       3      0                                                       4      0
                       4      0                                                       4      1
                       4      1                                                       1      0
        
        '''
        
        lCompositeTestIndices = []
        lCompositeTestIndices.append([0,0])
        lCompositeTestIndices.append([0,1])
        lCompositeTestIndices.append([1,0])
        lCompositeTestIndices.append([2,0])
        lCompositeTestIndices.append([2,1])
        lCompositeTestIndices.append([3,0])
        lCompositeTestIndices.append([4,0])
        lCompositeTestIndices.append([4,1])
    
        self.oSession.SetCompositeIndicesList(lCompositeTestIndices)
        
        
        lExpectedShuffledOrder = []
        lExpectedShuffledOrder.append([3,0])
        lExpectedShuffledOrder.append([0,0])
        lExpectedShuffledOrder.append([0,1])
        lExpectedShuffledOrder.append([2,0])
        lExpectedShuffledOrder.append([2,1])
        lExpectedShuffledOrder.append([4,0])
        lExpectedShuffledOrder.append([4,1])
        lExpectedShuffledOrder.append([1,0])
    
        lRandIndices = [3,0,2,4,1]
        
        # call function to rebuild the composite indices list
        lCompositeIndicesResult = self.oSession.ShufflePageQuestionCompositeIndexList(lRandIndices)
        
        # valid result with expected
        if lCompositeIndicesResult == lExpectedShuffledOrder :
            bTestResult = True
        else:
            bTestResult = False
        
        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 
    def test_ShufflePageQuestionGroupCompositeIndexList(self):
        bTestResult = True
        self.fnName = sys._getframe().f_code.co_name
        
        # build page/question set/page group composite indices list for testing
        '''
            eg.     Original XML List         Randomized Page Group indices      Shuffled Composite List
                       Page   QS  Grp                    Indices                      Page   QS    Grp
                       0      0     1                        2                         2      0     2
                       0      1     1                        3                         2      1     2
                       1      0     1                        1                         3      0     2
                       2      0     2                                                  4      0     3
                       2      1     2                                                  4      1     3
                       3      0     2                                                  0      0     1
                       4      0     3                                                  0      1     1
                       4      1     3                                                  1      0     1
        
        '''
        
        lCompositeTestIndices = []
        lCompositeTestIndices.append([0,0,1])
        lCompositeTestIndices.append([0,1,1])
        lCompositeTestIndices.append([1,0,1])
        lCompositeTestIndices.append([2,0,2])
        lCompositeTestIndices.append([2,1,2])
        lCompositeTestIndices.append([3,0,2])
        lCompositeTestIndices.append([4,0,3])
        lCompositeTestIndices.append([4,1,3])
        
        self.oSession.Set3DCompositeIndicesList(lCompositeTestIndices)
        
        
        lExpectedShuffledOrder = []
        lExpectedShuffledOrder.append([2,0,2])
        lExpectedShuffledOrder.append([2,1,2])
        lExpectedShuffledOrder.append([3,0,2])
        lExpectedShuffledOrder.append([4,0,3])
        lExpectedShuffledOrder.append([4,1,3])
        lExpectedShuffledOrder.append([0,0,1])
        lExpectedShuffledOrder.append([0,1,1])
        lExpectedShuffledOrder.append([1,0,1])
        
        lRandIndices = [2,3,1]
        
        # call function to rebuild the composite indices list
        lCompositeIndicesResult = self.oSession.ShufflePageQuestionGroupCompositeIndexList(lRandIndices)
        
        # valid result with expected
        if lCompositeIndicesResult == lExpectedShuffledOrder :
            bTestResult = True
        else:
            bTestResult = False
        
        tupResult = self.fnName, bTestResult
        return tupResult

    #-------------------------------------------
    def test_ValidatePageGroupNumbers_MissingPageGroup(self):
        '''Test if randomization is requested that the PageGroup attribute exists 
            for all pages.
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        sMsg = ''
        bTestResult = True

        # build XML
        xRoot = etree.Element("Session", RandomizePageGroups="Y")
        etree.SubElement(xRoot,"Page", PageGroup="1")
        etree.SubElement(xRoot,"Page")
        etree.SubElement(xRoot,"Page", PageGroup="1")
        
        
        # tree = etree.ElementTree(xRoot)
        # sPath = "C:\\Users\\alibi\\Documents\\Work-Baines\\Projects\\ImageQuizzer\\ImageQuizzerProject\\ImageQuizzer\\Testing\\TestData\\Test_UtilsIOXml\\filename.xml"
        # tree.write(sPath)
        try:
            with self.assertRaises(Exception) as context:
                self._oFilesIO.ValidatePageGroupNumbers(xRoot)
                
            sMsg = context.exception.args[0]
            if sMsg.find('Missing PageGroup attribute')>=0:
                bTestResult = True
               
        except:
            bTestResult = False
        
        
        

        tupResult = self.fnName, bTestResult
        return tupResult

    #-------------------------------------------
    def test_ValidatePageGroupNumbers_InvalidNumber(self):
        
        self.fnName = sys._getframe().f_code.co_name
        sMsg = ''
        bTestResult = True

        # build XML
        xRoot = etree.Element("Session", RandomizePageGroups="Y")
        etree.SubElement(xRoot,"Page", PageGroup="1")
        etree.SubElement(xRoot,"Page", PageGroup="a")
        etree.SubElement(xRoot,"Page", PageGroup="1")
            
            
        try:
            with self.assertRaises(ValueError) as context:
                self._oFilesIO.ValidatePageGroupNumbers(xRoot)

            sMsg = context.exception.args[0]
            if sMsg.find('Invalid PageGroup value')>=0:
                bTestResult = True

            
        except:
            bTestResult = False
        
        
        

        tupResult = self.fnName, bTestResult
        return tupResult

  
    #-------------------------------------------
    def test_ValidatePageGroupNumbers_NotEnoughPageGroups(self):
        
        self.fnName = sys._getframe().f_code.co_name
        sMsg = ''
        bTestResult = True

        # build XML
        xRoot = etree.Element("Session", RandomizePageGroups="Y")
        etree.SubElement(xRoot,"Page", PageGroup="0")
        etree.SubElement(xRoot,"Page", PageGroup="1")
        etree.SubElement(xRoot,"Page", PageGroup="1")
        etree.SubElement(xRoot,"Page", PageGroup="1")
            
            
        try:
            with self.assertRaises(Exception) as context:
                self._oFilesIO.ValidatePageGroupNumbers(xRoot)

            sMsg = context.exception.args[0]
            if sMsg.find('Randomizing Error')>=0:
                bTestResult = True

            
        except:
            bTestResult = False
        
        
        

        tupResult = self.fnName, bTestResult
        return tupResult

  
    
    #-------------------------------------------
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
