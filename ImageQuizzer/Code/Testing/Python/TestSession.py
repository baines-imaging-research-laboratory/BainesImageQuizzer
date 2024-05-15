import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from Session import *
from CustomWidgets import *
from TestingStatus import *
from Utilities.UtilsIOXml import *

import xml.dom.minidom

import os
import sys
import tempfile



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
# TestSession_ModuleWidget
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

        self._oFilesIO = UtilsFilesIO()
        self.oIOXml = UtilsIOXml()
        self.oSession = Session()
        self.oSession.SetFilesIO(self._oFilesIO)
        self.oSession.SetIOXml(self.oIOXml)
        # reset when overriding Session > CustomWidget's constructor of oIOXml
        #     since this is customized for unit tests
        self.oSession.oCustomWidgets.SetIOXml(self.oIOXml)     
        
        # create/set environment variable to be checked in UtilsIOXml class
        #    to prevent displaying error messages during testing
        os.environ["testing"] = "1"
        self._oFilesIO.setupTestEnvironment()

        self.sTempDir = os.path.join(tempfile.gettempdir(),'ImageQuizzer')
        if not os.path.exists(self.sTempDir):
            os.makedirs(self.sTempDir)

    #------------------------------------------- 
    def runTest(self ):
        # Tests are initiated in Slicer by pressing the Reload and Test button

        self.setUp()
        # self.sTempDir = os.path.join(tempfile.gettempdir(),'ImageQuizzer')

        logic = TestSessionLogic()

        tupResults = []
        tupResults.append(self.test_BuildNavigationList())
        tupResults.append(self.test_BuildNavigationList_RepNumbers())
        tupResults.append(self.test_ShuffleNavigationList())
        tupResults.append(self.test_ShuffleNavigationList_WithZero())

        tupResults.append(self.test_RandomizePageGroups_WithZero())
        tupResults.append(self.test_RandomizePageGroups_WithoutZero())
        tupResults.append(self.test_RandomizePageGroups_NoSeed())

        tupResults.append(self.test_GetStoredRandomizedIndices())
        tupResults.append(self.test_AddRandomizedIndicesToQuizResultsFile())
        
        tupResults.append(self.test_AdjustXMLForRepeatedPage())
        tupResults.append(self.test_TestMultipleRepeats())
        tupResults.append(self.test_LoopingWithRandomizedPages())
        
        logic.sessionTestStatus.DisplayTestResults(tupResults)
        
        #>>>>>>>>>>> cleanup <<<<<<<<<<<<
 
        # reset to allow for non-testing logic
        #    ie. display error messages when not testing
        os.environ["testing"] = "0"
        
        
        # REMOVE TEMP FILES >>>>>>>> comment out for debugging for visualization
        if os.path.exists(self.sTempDir) and os.path.isdir(self.sTempDir):
            shutil.rmtree(self.sTempDir)

    #------------------------------------------- 
    def test_BuildNavigationList(self):
        bTestResult = True
        self.fnName = sys._getframe().f_code.co_name
        
        # lists: [page, question set, page group, repetition]
        
        # build XML
        xRoot = etree.Element("Session")
        xPage1 = etree.SubElement(xRoot,"Page")
        xPage2 = etree.SubElement(xRoot,"Page")
        xPage3 = etree.SubElement(xRoot,"Page")
        xQS1 = etree.SubElement(xPage1, "QuestionSet")
        xQS2 = etree.SubElement(xPage1, "QuestionSet")
        xQS1 = etree.SubElement(xPage2, "QuestionSet")
        xQS1 = etree.SubElement(xPage3, "QuestionSet")
        
        self.oIOXml.SetRootNode(xRoot)
        
        lExpectedCompositeIndices = []
        lExpectedCompositeIndices.append([0,0,1,0])
        lExpectedCompositeIndices.append([0,1,1,0])
        lExpectedCompositeIndices.append([1,0,2,0])
        lExpectedCompositeIndices.append([2,0,3,0])
        
        
        self.oSession.BuildNavigationList()
        lCompositeIndicesResult = self.oSession.GetNavigationList()
        
        if lCompositeIndicesResult == lExpectedCompositeIndices :
            bTestResult = True
        else:
            bTestResult = False
            
        # set quiz as complete for test purposes - so as not to trigger error message
        self.oSession.oCustomWidgets.SetQuizComplete(True)

        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 
    def test_BuildNavigationList_RepNumbers(self):
        bTestResult = True
        self.fnName = sys._getframe().f_code.co_name

        # composite indices syntax: [page, question set, page group, repetition]
        
        # build XML
        xRoot = etree.Element("Session")
        xPage1 = etree.SubElement(xRoot,"Page")
        xPage2 = etree.SubElement(xRoot,"Page")
        xPage3 = etree.SubElement(xRoot,"Page")
        xPage4 = etree.SubElement(xRoot,"Page")
        xPage5 = etree.SubElement(xRoot,"Page")
        xQS1 = etree.SubElement(xPage1, "QuestionSet")
        xQS2 = etree.SubElement(xPage1, "QuestionSet")
        xQS1 = etree.SubElement(xPage2, "QuestionSet")
        xQS1 = etree.SubElement(xPage3, "QuestionSet")
        xQS1 = etree.SubElement(xPage4, "QuestionSet")
        xQS1 = etree.SubElement(xPage5, "QuestionSet")
        
        dAttrib = {"PageGroup":"1"}
        self.oIOXml.UpdateAttributesInElement(xPage1, dAttrib)
        self.oIOXml.UpdateAttributesInElement(xPage2, dAttrib)
        self.oIOXml.UpdateAttributesInElement(xPage3, dAttrib)
        self.oIOXml.UpdateAttributesInElement(xPage4, dAttrib)
        self.oIOXml.UpdateAttributesInElement(xPage5, dAttrib)
        dAttrib = {"Rep":"1"}
        self.oIOXml.UpdateAttributesInElement(xPage4, dAttrib)
        
        self.oIOXml.SetRootNode(xRoot)
        
        lExpectedCompositeIndices = []
        lExpectedCompositeIndices.append([0,0,1,0])
        lExpectedCompositeIndices.append([0,1,1,0])
        lExpectedCompositeIndices.append([1,0,1,0])
        lExpectedCompositeIndices.append([2,0,1,0])
        lExpectedCompositeIndices.append([3,0,1,1])
        lExpectedCompositeIndices.append([4,0,1,0])
        
        
        self.oSession.BuildNavigationList()
        lCompositeIndicesResult = self.oSession.GetNavigationList()
        
        if lCompositeIndicesResult == lExpectedCompositeIndices :
            bTestResult = True
        else:
            bTestResult = False
            
        # set quiz as complete for test purposes - so as not to trigger error message
        self.oSession.oCustomWidgets.SetQuizComplete(True)

        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 
    def test_ShuffleNavigationList(self):
        bTestResult = True
        self.fnName = sys._getframe().f_code.co_name

        # composite indices syntax: [page, question set, page group, repetition]
        
        # build page/question set/page group composite indices list for testing
        '''
            e.g. Randomized Page Group order : 2,3,1
            
                    Original XML List             Randomized Page Indices         Shuffled Composite List
                       Page   QS   Grp   Rep             Indices                   Page   QS   Grp   Rep
                       0      0     1     0                 2                       2     0     2     0
                       0      1     1     0                 3                       2     1     2     0
                       1      0     1     0                 4                       3     0     2     0
                       2      0     2     0                 0                       4     0     3     0
                       2      1     2     0                 1                       4     1     3     0
                       3      0     2     0                                         0     0     1     0
                       4      0     3     0                                         0     1     1     0
                       4      1     3     0                                         1     0     1     0
        
        '''
        
        lCompositeTestIndices = []
        lCompositeTestIndices.append([0,0,1,0])
        lCompositeTestIndices.append([0,1,1,0])
        lCompositeTestIndices.append([1,0,1,0])
        lCompositeTestIndices.append([2,0,2,0])
        lCompositeTestIndices.append([2,1,2,0])
        lCompositeTestIndices.append([3,0,2,0])
        lCompositeTestIndices.append([4,0,3,0])
        lCompositeTestIndices.append([4,1,3,0])
        
        self.oSession.SetNavigationList(lCompositeTestIndices)
        
        
        lExpectedShuffledOrder = []
        lExpectedShuffledOrder.append([2,0,2,0])
        lExpectedShuffledOrder.append([2,1,2,0])
        lExpectedShuffledOrder.append([3,0,2,0])
        lExpectedShuffledOrder.append([4,0,3,0])
        lExpectedShuffledOrder.append([4,1,3,0])
        lExpectedShuffledOrder.append([0,0,1,0])
        lExpectedShuffledOrder.append([0,1,1,0])
        lExpectedShuffledOrder.append([1,0,1,0])
        
        # assign a set of randomized unique page groups
        lRandIndices = [2,3,1]
        
        # call function to rebuild the composite indices list
        lCompositeIndicesResult = self.oSession.ShuffleNavigationList(lRandIndices)
        
        # validate result with expected
        if lCompositeIndicesResult == lExpectedShuffledOrder :
            bTestResult = True
        else:
            bTestResult = False
        
        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 
    def test_ShuffleNavigationList_WithZero(self):
        bTestResult = True
        self.fnName = sys._getframe().f_code.co_name

        # composite indices syntax: [page, question set, page group, repetition]
        
        # build page/question set/page group composite indices list for testing
        
        lCompositeTestIndices = []
        lCompositeTestIndices.append([0,0,1,0])
        lCompositeTestIndices.append([0,1,1,0])
        lCompositeTestIndices.append([1,0,0,0])
        lCompositeTestIndices.append([2,0,1,0])
        lCompositeTestIndices.append([3,0,2,0])
        lCompositeTestIndices.append([3,1,2,0])
        lCompositeTestIndices.append([4,0,0,0])
        lCompositeTestIndices.append([5,0,2,0])
        lCompositeTestIndices.append([6,0,3,0])
        lCompositeTestIndices.append([6,1,3,0])
        lCompositeTestIndices.append([7,0,0,0])
      
        self.oSession.SetNavigationList(lCompositeTestIndices)
        
        
        lExpectedShuffledOrder = []
        lExpectedShuffledOrder.append([1,0,0,0])
        lExpectedShuffledOrder.append([4,0,0,0])
        lExpectedShuffledOrder.append([7,0,0,0])
        lExpectedShuffledOrder.append([3,0,2,0])
        lExpectedShuffledOrder.append([3,1,2,0])
        lExpectedShuffledOrder.append([5,0,2,0])
        lExpectedShuffledOrder.append([6,0,3,0])
        lExpectedShuffledOrder.append([6,1,3,0])
        lExpectedShuffledOrder.append([0,0,1,0])
        lExpectedShuffledOrder.append([0,1,1,0])
        lExpectedShuffledOrder.append([2,0,1,0])
        
        # assign a set of randomized unique page groups
        #    (code for creating the unique randomized numbers always puts zero first)
        lRandIndices = [0,2,3,1]
        
        # call function to rebuild the composite indices list
        lCompositeIndicesResult = self.oSession.ShuffleNavigationList(lRandIndices)
        
        # validate result with expected
        if lCompositeIndicesResult == lExpectedShuffledOrder :
            bTestResult = True
        else:
            bTestResult = False
        
        tupResult = self.fnName, bTestResult
        return tupResult

    #-------------------------------------------
    def test_RandomizePageGroups_WithZero(self):

        
        self.fnName = sys._getframe().f_code.co_name
        sMsg = ''
        bTestResult = True

        iSeed = 100
        liExpectedResult = [0,5,1,6,9,7,2,4,8,3]

        # supply a set of unique page group numbers to randomize
        # test moving the position of the zero 
        liNumbersToRandomize = [0,1,2,3,4,5,6,7,8,9]
        liRandomizedNumbers = self.oSession.RandomizePageGroups(liNumbersToRandomize, iSeed)
        # validate result with expected
        if liRandomizedNumbers == liExpectedResult :
            bTest1 = True
        else:
            bTest1 = False

        liNumbersToRandomize = [1,2,3,4,5,6,7,8,9,0]
        liRandomizedNumbers = self.oSession.RandomizePageGroups(liNumbersToRandomize, iSeed)
        # validate result with expected
        if liRandomizedNumbers == liExpectedResult :
            bTest2 = True
        else:
            bTest2 = False

        liNumbersToRandomize = [1,2,3,0,4,5,6,7,8,9]
        liRandomizedNumbers = self.oSession.RandomizePageGroups(liNumbersToRandomize, iSeed)
        # validate result with expected
        if liRandomizedNumbers == liExpectedResult :
            bTest3 = True
        else:
            bTest3 = False

        if bTest1 & bTest2 & bTest3:
            bTestResult = True
        else:
            bTestResult = False
            
        tupResult = self.fnName, bTestResult
        return tupResult

    #-------------------------------------------
    def test_RandomizePageGroups_WithoutZero(self):

        
        self.fnName = sys._getframe().f_code.co_name
        sMsg = ''
        bTestResult = True

        liNumbersToRandomize = [1,2,3,4,5,6,7,8,9]
        iSeed = 100
        liExpectedResult = [5,1,6,9,7,2,4,8,3]
        
        liRandomizedNumbers = self.oSession.RandomizePageGroups(liNumbersToRandomize, iSeed)

        # validate result with expected
        if liRandomizedNumbers == liExpectedResult :
            bTestResult = True
        else:
            bTestResult = False

        tupResult = self.fnName, bTestResult
        return tupResult

    #-------------------------------------------
    def test_RandomizePageGroups_NoSeed(self):
        ''' Function to make sure an empty parameter does not throw an error.
            Because there is no seed, we cannot test for an expected result.
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        sMsg = ''
        bTestResult = True

        liNumbersToRandomize = [1,2,3,4,5,6,7,8,9]
        try:
            liRandomizedNumbers = self.oSession.RandomizePageGroups(liNumbersToRandomize)
            bTestResult = True
            
        except:
            bTestResult = False

        tupResult = self.fnName, bTestResult
        return tupResult
        
    #-------------------------------------------
    def test_GetStoredRandomizedIndices(self):
        ''' Test getting the randomized list of indices from an XML file
            and converting it to a list of integers.
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        sMsg = ''
        bTestResult = True
        
        xRoot = etree.Element("Session", RandomizePageGroups="Y")
        etree.SubElement(xRoot,"Page", PageGroup="0")
        etree.SubElement(xRoot,"Page", PageGroup="1")
        child = etree.SubElement(xRoot,"RandomizedPageGroupIndices")
        child.text = '0,5,3,1,4,2' 
        self.oIOXml.SetRootNode(xRoot)
        
        liExpectedIndices = [0,5,3,1,4,2]
        liStoredIndices = self.oSession.oCustomWidgets.GetStoredRandomizedIndices()
        
        if liStoredIndices == liExpectedIndices:
            bTestResult = True
        else:
            bTestResult = False
        
        
        tupResult = self.fnName, bTestResult
        return tupResult
        
    #------------------------------------------- 
    def test_AddRandomizedIndicesToQuizResultsFile(self):
        
        self.fnName = sys._getframe().f_code.co_name
        sMsg = ''
        bTestResult = True
        
        xRoot = etree.Element("Session", RandomizePageGroups="Y")
        etree.SubElement(xRoot,"Page", PageGroup="0")
        self.oIOXml.SetRootNode(xRoot)
#         self.oSession.SetIOXml(self.oIOXml)

        
        liIndices = [0,5,3,1,4,2]
        self.oSession.oCustomWidgets.AddRandomizedIndicesToQuizResultsFile(liIndices)

        # read the updated xml to get what was stored 
        liStoredIndices = self.oSession.oCustomWidgets.GetStoredRandomizedIndices()
        
        if liStoredIndices == liIndices:
            bTestResult = True
        else:
            bTestResult = False

        
        tupResult = self.fnName, bTestResult
        return tupResult
        
    #------------------------------------------- 
    def test_CreatingRandomIndices(self):
        ''' This test is to ensure the randomizer is truly creating 
            random lists of indices.
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        sMsg = ''
        bTestResult = True
        
        liNumbersToRandomize = [1,2,3,4,5,6,7,8,9]
        iSeed = 100
        liExpectedResult = [5,1,6,9,7,2,4,8,3]
        liRandomizedNumbers = self.oSession.RandomizePageGroups(liNumbersToRandomize)

        # second set should be different
        liRandomizedNumbers2 = self.oSession.RandomizePageGroups(liNumbersToRandomize)
        
        if liRandomizedNumbers != liRandomizedNumbers2:
            bTestResult = True
        else:
            bTestResult = False
        
        tupResult = self.fnName, bTestResult
        return tupResult
        

    #-------------------------------------------
    def test_AdjustXMLForRepeatedPage(self):

        self.fnName = sys._getframe().f_code.co_name
        sMsg = ''
        bTestResult = False

        # build XMLs
        #>>>>>>>>>>>>>>>>>>>>>>> Expected

        xExpectedRoot = etree.Element("Session")
        xExpPage0 = etree.SubElement(xExpectedRoot,"Page")
        xExpPage1 = etree.SubElement(xExpectedRoot,"Page")
        xExpPage2 = etree.SubElement(xExpectedRoot,"Page", {"Rep":"0"})
        xExpPage3NewRepeat = etree.SubElement(xExpectedRoot,"Page", {"ID":"-Rep1", "Rep":"1", "PageComplete":"N"})
        xExpPage4 = etree.SubElement(xExpectedRoot,"Page")
 
        xExpIm1 = etree.SubElement(xExpPage3NewRepeat, "Image")
        xExpIm2 = etree.SubElement(xExpPage3NewRepeat, "Image")
        xExpIm3 = etree.SubElement(xExpPage3NewRepeat, "Image")
          
        xState = etree.SubElement(xExpIm1, "State")
        xState = etree.SubElement(xExpIm2, "State")
        xState = etree.SubElement(xExpIm3, "State")

        # QuestionSet elements are automatically added in the BuildNavigationList function
        QS0 = etree.SubElement(xExpPage0,'QuestionSet')
        QS1 = etree.SubElement(xExpPage1,'QuestionSet')
        QS2 = etree.SubElement(xExpPage2,'QuestionSet')
        Q2 = etree.SubElement(QS2,'Question')
        O2 = etree.SubElement(Q2, 'Option')
        R2 = etree.SubElement(O2, 'Response')
        QS3 = etree.SubElement(xExpPage3NewRepeat,'QuestionSet')
        Q3 = etree.SubElement(QS3,'Question')
        O3 = etree.SubElement(Q3, 'Option')
        QS4 = etree.SubElement(xExpPage4,'QuestionSet')

        self.oIOXml.SetRootNode(xExpectedRoot)
        
        sFullFile = self.sTempDir + '\\ExpectedLoop.xml'
        self.oIOXml.SaveXml(sFullFile)

        
        #>>>>>>>>>>>>>>>>>>>>>>> Input
        
        xRoot = etree.Element("Session")
        xPage0 = etree.SubElement(xRoot,"Page")
        xPage1 = etree.SubElement(xRoot,"Page")
        xPage2 = etree.SubElement(xRoot,"Page", {"Rep":"0"})    # previous page
        xPage3 = etree.SubElement(xRoot,"Page")
        xPage4 = etree.SubElement(xRoot,"Page")

        
        xIm1 = etree.SubElement(xPage3, "Image")
        xIm2 = etree.SubElement(xPage3, "Image")
        xIm3 = etree.SubElement(xPage3, "Image")
         
        xLMPath = etree.SubElement(xIm1, "LabelMapPath")
        xState = etree.SubElement(xIm1, "State")
        xMULinePath = etree.SubElement(xIm2, "MarkupLinePath")
        xState = etree.SubElement(xIm2, "State")
        xState = etree.SubElement(xIm3, "State")
        
        QS0 = etree.SubElement(xPage0,'QuestionSet')
        QS1 = etree.SubElement(xPage1,'QuestionSet')
        QS2 = etree.SubElement(xPage2,'QuestionSet')
        Q2 = etree.SubElement(QS2,'Question')
        O2 = etree.SubElement(Q2, 'Option')
        R2 = etree.SubElement(O2, 'Response')
        QS3 = etree.SubElement(xPage3,'QuestionSet')
        Q3 = etree.SubElement(QS3,'Question')
        O3 = etree.SubElement(Q3, 'Option')
        R3 = etree.SubElement(O3, 'Response')
        QS4 = etree.SubElement(xPage4,'QuestionSet')
        
        
        
        
        self.oIOXml.SetRootNode(xRoot)
#         self.oSession.SetIOXml(self.oIOXml)

        
        # for debug
        sFullFile = self.sTempDir + '\\PreLoop.xml' 
        self.oIOXml.SaveXml(sFullFile)
        
#         self.oSession.oCustomWidgets.SetRootNode(xRoot)
         
        #>>>>>>>>>>>>>>>>>>>>>>>
        
        self.oSession.BuildNavigationList()
        # set current index to the repeated xml element
        self.oSession.SetCurrentNavigationIndex(3)
        self.oSession.oCustomWidgets.AdjustXMLForRepeatedPage(\
                    self.oSession.oCustomWidgets.GetNthPageNode(self.oSession.GetCurrentNavigationIndex()),\
                    self.oSession.GetNavigationPage( self.oSession.GetCurrentNavigationIndex() - 1))
        
#         xAdjustedRoot = self.oIOXml.GetRootNode()
        xAdjustedRoot = self.oSession.oCustomWidgets.GetRootNode()
        sAdjustedXML = etree.tostring(xAdjustedRoot)
        sExpectedXML = etree.tostring(xExpectedRoot)
        
        # # for debug
#         print(sAdjustedXML)
#         print(sExpectedXML)
#         print(self.oSession.GetNavigationList())
        
        if sAdjustedXML == sExpectedXML:
            bTestResult = True
    
        tupResult = self.fnName, bTestResult
        return tupResult
        
    #-------------------------------------------
    def test_TestMultipleRepeats(self):
        ''' Function to test looping - repeat a Page
            There are multiple consecutive tests to pass. For each test the composite navigation  
            list changes and the next test results are based on the previous test resulting navigation list.
        '''
        self.fnName = sys._getframe().f_code.co_name
        sMsg = ''
        bTestResult = True
        liTestResults = []
        
        # Set up an xml file with the basic elements and question sets for testing.
        xRoot = self.CreateTestXmlForLooping()


        self.oIOXml.SetRootNode(xRoot)
        
        #############
        # for debug visualization - save inputs and outputs to temp files
        # comment out the deletion of these files at the end of 'runTest' if you need to visualize the xml structure
        sResultsPath = self.sTempDir + '\\Results.xml'
        sFullFile = self.sTempDir + '\\PreLoop.xml'
        self.oIOXml.SaveXml(sFullFile)
        #############

#         self.oSession.oCustomWidgets.SetRootNode(xRoot)
        self.oSession.SetIOXml(self.oIOXml)
        self.oSession.BuildNavigationList()
            # print(self.oSession.GetNavigationList())
        '''
        # composite indices syntax: [page, question set, page group, repetition]
        # Pre-loop composite navigation list = [[0, 0, 1, 0],        # xPage0   Pt1/QS0
                                                [0, 1, 1, 0],        # xPage0   Pt1/QS1
                                                [1, 0, 0, 0],        # xPage1   Pt2/QS0
                                                [2, 0, 1, 0],        # xPage2   Pt3/QS0
                                                [3, 0, 2, 0],        # xPage3   Pt4/QS0
                                                [3, 1, 2, 0],        # xPage3   Pt4/QS1
                                                [4, 0, 0, 0],        # xPage4   Pt5/QS0
                                                [5, 0, 2, 0],        # xPage5   Pt6/QS0
                                                [6, 0, 3, 0],        # xPage6   Pt7/QS0
                                                [6, 1, 3, 0],        # xPage6   Pt7/QS1
                                                [7, 0, 0, 0]]        # xPage7   Pt8/QS0
        '''
        
        # nav index------------->      0             1             2             3             4             5             6             7             8             9            10            11            12            13              14             15           16           
        # Pre-Loop                [[0, 0, 1, 0], [0, 1, 1, 0], [1, 0, 0, 0], [2, 0, 1, 0], [3, 0, 2, 0], [3, 1, 2, 0], [4, 0, 0, 0], [5, 0, 2, 0], [6, 0, 3, 0], [6, 1, 3, 0], [7, 0, 0, 0]] 
        # Repeat nav 3 (Pt3)
        liExpectedResults_Test1 = [[0, 0, 1, 0], [0, 1, 1, 0], [1, 0, 0, 0], [2, 0, 1, 0], [3, 0, 1, 1], [4, 0, 2, 0], [4, 1, 2, 0], [5, 0, 0, 0], [6, 0, 2, 0], [7, 0, 3, 0], [7, 1, 3, 0], [8, 0, 0, 0]]
        # Repeat nav 5 (Pt4) (page with 2 question sets)
        liExpectedResults_Test2 = [[0, 0, 1, 0], [0, 1, 1, 0], [1, 0, 0, 0], [2, 0, 1, 0], [3, 0, 1, 1], [4, 0, 2, 0], [4, 1, 2, 0], [5, 0, 2, 1], [5, 1, 2, 1], [6, 0, 0, 0], [7, 0, 2, 0], [8, 0, 3, 0], [8, 1, 3, 0], [9, 0, 0, 0]]
        # Repeat nav 3 (Pt3 again) from Rep0 position
        liExpectedResults_Test3 = [[0, 0, 1, 0], [0, 1, 1, 0], [1, 0, 0, 0], [2, 0, 1, 0], [3, 0, 1, 1], [4, 0, 1, 2], [5, 0, 2, 0], [5, 1, 2, 0], [6, 0, 2, 1], [6, 1, 2, 1], [7, 0, 0, 0], [8, 0, 2, 0], [9, 0, 3, 0], [9, 1, 3, 0], [10, 0, 0, 0]]
        # Repeat nav 5 (Pt3 again) from Rep2 position
        liExpectedResults_Test4 = [[0, 0, 1, 0], [0, 1, 1, 0], [1, 0, 0, 0], [2, 0, 1, 0], [3, 0, 1, 1], [4, 0, 1, 2], [5, 0, 1, 3], [6, 0, 2, 0], [6, 1, 2, 0], [7, 0, 2, 1], [7, 1, 2, 1], [8, 0, 0, 0], [9, 0, 2, 0], [10, 0, 3, 0], [10, 1, 3, 0], [11, 0, 0, 0]]
        # Repeat nav 15 (Pt8) append 
        liExpectedResults_Test5 = [[0, 0, 1, 0], [0, 1, 1, 0], [1, 0, 0, 0], [2, 0, 1, 0], [3, 0, 1, 1], [4, 0, 1, 2], [5, 0, 1, 3], [6, 0, 2, 0], [6, 1, 2, 0], [7, 0, 2, 1], [7, 1, 2, 1], [8, 0, 0, 0], [9, 0, 2, 0], [10, 0, 3, 0], [10, 1, 3, 0], [11, 0, 0, 0], [12, 0, 0, 1]]

        liResults_test1 = []
        

        ########### Test 1
        #     Repeat nav index 3 - loop on Page with only one question set
        self.oSession.SetCurrentNavigationIndex(3) # repeat xPage2 (3 in composite list - 0-based)
        self.oSession.CreateRepeatedPageNode(sResultsPath)
        liResults_test1 = self.oSession.GetNavigationList()
            # print(liResults_test1)
        # resulting list has a new composite index at nav 4 with the rep index = 1  (increased page index)
        # all remaining composite indices are from Pre-Loop nav 4 to end  but page index is increased by 1 
        bResult = [lambda:0, lambda:1][liResults_test1 == liExpectedResults_Test1]()
        liTestResults.append(bResult)


        
        ########### Test 2
        #     Repeat nav 5 (Pt4) (page with 2 question sets)
        self.oSession.SetCurrentNavigationIndex(5) # repeat xPage4 (5 in updated composite list - 0-based)
        self.oSession.CreateRepeatedPageNode(sResultsPath)
        liResults_test2 = self.oSession.GetNavigationList()
            # print(liResults_test2)
        # resulting list has two new composite indices at positions 7 and 8 (increased page index)
        # all remaining composite indices are from TestResult1 nav 7 to end but page index is increased by 1
        bResult = [lambda:0, lambda:1][liResults_test2 == liExpectedResults_Test2]()
        liTestResults.append(bResult)


        ########### Test 3
        #     Repeat nav 3 (Pt3 again) from Rep0 position
        self.oSession.SetCurrentNavigationIndex(3) # repeat xPage2 again
        self.oSession.CreateRepeatedPageNode(sResultsPath)
        liResults_test3 = self.oSession.GetNavigationList()
            # print(liResults_test3)
        # resulting list has a new composite index at nav 5 with the rep index = 2  (increased page index)
        # all remaining composite indices are from TestResult2 nav 5 to end  but page index is increased by 1 
        bResult = [lambda:0, lambda:1][liResults_test3 == liExpectedResults_Test3]()
        liTestResults.append(bResult)



        ########### Test 4
        #     Repeat nav 5 (Pt3 again) from Rep2 position
        self.oSession.SetCurrentNavigationIndex(5) # repeat xPage2 again - but from Rep2 position
        self.oSession.CreateRepeatedPageNode(sResultsPath)
        liResults_test4 = self.oSession.GetNavigationList()
            # print(liResults_test4)
        # resulting list has a new composite index at nav 6 with the rep index = 3  (increased page index)
        # all remaining composite indices are from TestResult3 nav 6 to end  but page index is increased by 1 
        bResult = [lambda:0, lambda:1][liResults_test4 == liExpectedResults_Test4]()
        liTestResults.append(bResult)


        ########### Test 5
        #     Repeat nav 15 (Pt8) last Page - new Page is appended
        self.oSession.SetCurrentNavigationIndex(15) # repeat last page - append
        self.oSession.CreateRepeatedPageNode(sResultsPath)
        liResults_test5 = self.oSession.GetNavigationList()
            # print(liResults_test5)
        # resulting list has a new composite index appended at nav 16 with the rep index = 1  (increased page index)
        bResult = [lambda:0, lambda:1][liResults_test5 == liExpectedResults_Test5]()
        liTestResults.append(bResult)

        ############ End testing ###########

        ########## Check for any failed tests    
        if any(i == 0 for i in liTestResults):
            bTestResult = False
    
        tupResult = self.fnName, bTestResult
        return tupResult
        
    #-------------------------------------------
    def test_LoopingWithRandomizedPages(self):
        ''' Test that randomized pages are handled properly when looping is introduced.
            Each test builds on the previous test results.
            The shuffled composite list continues to expand with each test.
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        sMsg = ''
        bTestResult = True
        liTestResults = []

        #############
        # for debug visualization - save inputs and outputs to temp files
        # comment out the deletion of these files at the end of 'runTest' if you need to visualize the xml structure
        sResultsPath = self.sTempDir + '\\Results.xml'
        sFullFile = self.sTempDir + '\\PreLoop.xml'
        self.oIOXml.SaveXml(sFullFile)
        #############

        # build xml
        xRoot = self.CreateTestXmlForLooping()

        
        self.oIOXml.SetRootNode(xRoot)
        self.oIOXml.SaveXml(sFullFile)
        
        self.oSession.BuildNavigationList()
            #print(self.oSession.GetNavigationList())
        
        # set up for randomizing given a randomized list of PageGroup indices
        self.oSession.oCustomWidgets.SetRandomizeRequired('Y')
        liRandIndices = [0,2,3,1]
        self.oSession.oCustomWidgets.AddRandomizedIndicesToQuizResultsFile(liRandIndices)
        # liRandIndices = [2,3,1] # PageGroup numbers
        # self.oSession.SetNavigationList( self.oSession.ShuffleNavigationList(liRandIndices) )
        self.oSession.BuildNavigationList()
        liResults_test0 = self.oSession.GetNavigationList()
            #print(liResults_test0)
        
        '''
        # composite indices syntax: [page, question set, page group, repetition]
        # Pre-loop composite navigation list = [[0, 0, 1, 0],        # xPage0   Pt1/QS0
                                                [0, 1, 1, 0],        # xPage0   Pt1/QS1
                                                [1, 0, 0, 0],        # xPage1   Pt2/QS0
                                                [2, 0, 1, 0],        # xPage2   Pt3/QS0
                                                [3, 0, 2, 0],        # xPage3   Pt4/QS0
                                                [3, 1, 2, 0],        # xPage3   Pt4/QS1
                                                [4, 0, 0, 0],        # xPage4   Pt5/QS0
                                                [5, 0, 2, 0],        # xPage5   Pt6/QS0
                                                [6, 0, 3, 0],        # xPage6   Pt7/QS0
                                                [6, 1, 3, 0],        # xPage6   Pt7/QS1
                                                [7, 0, 0, 0]]        # xPage7   Pt8/QS0
        '''
        
        # check that the composite navigation list matches the requested page order
        # nav index------------->      0             1             2             3             4             5             6             7             8             9            10            11            12            13              14             15           16           
        # Pre-Loop                [[0, 0, 1, 0], [0, 1, 1, 0], [1, 0, 0, 0], [2, 0, 1, 0], [3, 0, 2, 0], [3, 1, 2, 0], [4, 0, 0, 0], [5, 0, 2, 0], [6, 0, 3, 0], [6, 1, 3, 0], [7, 0, 0, 0]] 
        # Test 0 - shuffled based on page groups - no looping 
        liExpectedResults_Test0 = [[1, 0, 0, 0], [4, 0, 0, 0], [7, 0, 0, 0], [3, 0, 2, 0], [3, 1, 2, 0], [5, 0, 2, 0], [6, 0, 3, 0], [6, 1, 3, 0], [0, 0, 1, 0], [0, 1, 1, 0], [2, 0, 1, 0]]
        # Test 1 - repeat at nav 1 (Pt 5 - only one question set)
        liExpectedResults_Test1 = [[1, 0, 0, 0], [4, 0, 0, 0], [5, 0, 0, 1], [8, 0, 0, 0], [3, 0, 2, 0], [3, 1, 2, 0], [6, 0, 2, 0], [7, 0, 3, 0], [7, 1, 3, 0], [0, 0, 1, 0], [0, 1, 1, 0], [2, 0, 1, 0]]
        # Test 2 - repeat at nav 4 (Pt 4 - two question sets)
        liExpectedResults_Test2 = [[1, 0, 0, 0], [5, 0, 0, 0], [6, 0, 0, 1], [9, 0, 0, 0], [3, 0, 2, 0], [3, 1, 2, 0], [4, 0, 2, 1], [4, 1, 2, 1],[7, 0, 2, 0], [8, 0, 3, 0], [8, 1, 3, 0], [0, 0, 1, 0], [0, 1, 1, 0], [2, 0, 1, 0]]
        # Test 3 - repeat at nav 13 (last entry - Pt 3 - one question set)
        liExpectedResults_Test3 = [[1, 0, 0, 0], [6, 0, 0, 0], [7, 0, 0, 1], [10, 0, 0, 0], [4, 0, 2, 0], [4, 1, 2, 0], [5, 0, 2, 1], [5, 1, 2, 1],[8, 0, 2, 0], [9, 0, 3, 0], [9, 1, 3, 0], [0, 0, 1, 0], [0, 1, 1, 0], [2, 0, 1, 0], [3, 0, 1, 1]]
        # Test 4 - repeat at nav 0 (first entry - Pt 2 - one question set)
        liExpectedResults_Test4 = [[1, 0, 0, 0], [2, 0, 0, 1], [7, 0, 0, 0], [8, 0, 0, 1], [11, 0, 0, 0], [5, 0, 2, 0], [5, 1, 2, 0], [6, 0, 2, 1], [6, 1, 2, 1],[9, 0, 2, 0], [10, 0, 3, 0], [10, 1, 3, 0], [0, 0, 1, 0], [0, 1, 1, 0], [3, 0, 1, 0], [4, 0, 1, 1]]

        
        
        
        bResult = [lambda:0, lambda:1][liResults_test0 == liExpectedResults_Test0]()
        liTestResults.append(bResult)
        
        # repeat a page
        # use nav index 3 (Pt2 with 1 question set)
        
        
        ########### Test 1
        #     Repeat nav index 1 - (Pt 5 - page index 4) loop on Page with only one question set
        self.oSession.SetCurrentNavigationIndex(1) 
        self.oSession.CreateRepeatedPageNode(sResultsPath)
        liResults_test1 = self.oSession.GetNavigationList()
            #print(liResults_test1)
        # resulting list has a new composite index at nav 2 with the rep index = 1  (increased page index)
        # all other composite indices are from Shuffled_Test0 - 
        # page indices for other list items are increased by 1 except for page indices < 4
        # (in this example, list items with page indices 0,1,2 and 3 remain the same)
        bResult = [lambda:0, lambda:1][liResults_test1 == liExpectedResults_Test1]()
        liTestResults.append(bResult)
        
        
        ########### Test 2
        #     Repeat nav index 4 - (Pt 4 - page index 3) loop on Page with two question sets
        self.oSession.SetCurrentNavigationIndex(4) 
        self.oSession.CreateRepeatedPageNode(sResultsPath)
        liResults_test2 = self.oSession.GetNavigationList()
            #print(liResults_test2)
        # resulting list has two new composite indices at nav 6 and nav 7 with the rep index = 1  (increased page index)
        # any pages prior to page index 4 remain the same
        # all other composite indices are from liResults_test1 - 
        # page indices for other list items are increased by 1 except for page indices < 3
        # (in this example, list items with page indices 0,1 and 2 remain the same)
        bResult = [lambda:0, lambda:1][liResults_test2 == liExpectedResults_Test2]()
        liTestResults.append(bResult)
        
        
        ########### Test 3
        #     Repeat nav index 13 - (Pt 3 - page index 2) loop on last Page with one question set
        self.oSession.SetCurrentNavigationIndex(13) 
        self.oSession.CreateRepeatedPageNode(sResultsPath)
        liResults_test3 = self.oSession.GetNavigationList()
            #print(liResults_test3)
        # resulting list has one new composite index at nav 14 with the rep index = 1  (increased page index)
        # all other composite indices are from liResults_test2 - 
        # page indices for other list items are increased by 1 except for page indices < 3
        # (in this example, list items with page indices 0,1 and 2 remain the same)
        bResult = [lambda:0, lambda:1][liResults_test3 == liExpectedResults_Test3]()
        liTestResults.append(bResult)
        
        
        ########### Test 4
        #     Repeat nav index 0 - (Pt 2 - page index 1) loop on first Page with one question set
        self.oSession.SetCurrentNavigationIndex(0) 
        self.oSession.CreateRepeatedPageNode(sResultsPath)
        liResults_test4 = self.oSession.GetNavigationList()
            #print(liResults_test4)
        # resulting list has one new composite index at nav 1 with the rep index = 1  (increased page index)
        # all other composite indices are from liResults_test3 - 
        # page indices for other list items are increased by 1 except for page indices < 1
        # (in this example, list items with page indices 0 and 1 remain the same)
        bResult = [lambda:0, lambda:1][liResults_test4 == liExpectedResults_Test4]()
        liTestResults.append(bResult)
        
        
        
        
        ############ End testing ###########

        ########## Check for any failed tests    
        if any(i == 0 for i in liTestResults):
            bTestResult = False

    
        tupResult = self.fnName, bTestResult
        return tupResult
        
    #-------------------------------------------
    #-------------------------------------------

    
    #-------------------------------------------
    #-------------------------------------------
    #
    #        Helper Functions
    #
    #-------------------------------------------
    #-------------------------------------------
    def CreateTestXmlForLooping(self):
        ''' A helper function to create an xml file for testing the Loop functionality.
        '''

        # lCompositeTestIndices = []
        # lCompositeTestIndices.append([0,0,1,0])
        # lCompositeTestIndices.append([0,1,1,0])
        # lCompositeTestIndices.append([1,0,0,0])
        # lCompositeTestIndices.append([2,0,1,0])
        # lCompositeTestIndices.append([3,0,2,0])
        # lCompositeTestIndices.append([3,1,2,0])
        # lCompositeTestIndices.append([4,0,0,0])
        # lCompositeTestIndices.append([5,0,2,0])
        # lCompositeTestIndices.append([6,0,3,0])
        # lCompositeTestIndices.append([6,1,3,0])
        # lCompositeTestIndices.append([7,0,0,0])

        
        xRoot = etree.Element("Session")
        xPage0 = etree.SubElement(xRoot,"Page", {"PageGroup":"1", "Rep":"0","ID":"Pt1"})
        xPage1 = etree.SubElement(xRoot,"Page", {"PageGroup":"0", "Rep":"0","ID":"Pt2"})
        xPage2 = etree.SubElement(xRoot,"Page", {"PageGroup":"1", "Rep":"0","ID":"Pt3"})
        xPage3 = etree.SubElement(xRoot,"Page", {"PageGroup":"2", "Rep":"0","ID":"Pt4"})
        xPage4 = etree.SubElement(xRoot,"Page", {"PageGroup":"0", "Rep":"0","ID":"Pt5"})
        xPage5 = etree.SubElement(xRoot,"Page", {"PageGroup":"2", "Rep":"0","ID":"Pt6"})
        xPage6 = etree.SubElement(xRoot,"Page", {"PageGroup":"3", "Rep":"0","ID":"Pt7"})
        xPage7 = etree.SubElement(xRoot,"Page", {"PageGroup":"0", "Rep":"0","ID":"Pt8"})

        
        
        QS0 = etree.SubElement(xPage0,'QuestionSet',  {"ID":"QS0"})
        QS01 = etree.SubElement(xPage0,'QuestionSet', {"ID":"QS1"})
        QS1 = etree.SubElement(xPage1,'QuestionSet',  {"ID":"QS0"})
        QS2 = etree.SubElement(xPage2,'QuestionSet',  {"ID":"QS0"})
        QS3 = etree.SubElement(xPage3,'QuestionSet',  {"ID":"QS0"})
        QS31 = etree.SubElement(xPage3,'QuestionSet', {"ID":"QS1"})
        QS4 = etree.SubElement(xPage4,'QuestionSet',  {"ID":"QS0"})
        QS5 = etree.SubElement(xPage5,'QuestionSet',  {"ID":"QS0"})
        QS6 = etree.SubElement(xPage6,'QuestionSet',  {"ID":"QS0"})
        QS61 = etree.SubElement(xPage6,'QuestionSet', {"ID":"QS1"})
        QS7 = etree.SubElement(xPage7,'QuestionSet',  {"ID":"QS0"})
        
        
        return xRoot
        
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
