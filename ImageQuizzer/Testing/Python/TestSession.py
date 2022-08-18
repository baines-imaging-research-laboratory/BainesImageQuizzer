import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from Session import *
from TestingStatus import *
from Utilities.UtilsIOXml import *

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

        self._oFilesIO = UtilsFilesIO()
        self.oIOXml = UtilsIOXml()
        
        # create/set environment variable to be checked in UtilsIOXml class
        #    to prevent displaying error messages during testing
        os.environ["testing"] = "1"
        self._oFilesIO.setupTestEnvironment()

    #------------------------------------------- 
    def runTest(self ):
        # Tests are initiated in Slicer by pressing the Reload and Test button

        self.setUp()
        logic = TestSessionLogic()

        tupResults = []
        tupResults.append(self.test_BuildNavigationList())
        tupResults.append(self.test_BuildNavigationList_RepNumbers())
        tupResults.append(self.test_ShuffleNavigationList())
        tupResults.append(self.test_ShuffleNavigationList_WithZero())

        tupResults.append(self.test_ValidatePageGroupNumbers_MissingPageGroup())
        tupResults.append(self.test_ValidatePageGroupNumbers_InvalidNumber())
        tupResults.append(self.test_ValidatePageGroupNumbers_NotEnoughPageGroups())

        tupResults.append(self.test_RandomizePageGroups_WithZero())
        tupResults.append(self.test_RandomizePageGroups_WithoutZero())
        tupResults.append(self.test_RandomizePageGroups_NoSeed())

        tupResults.append(self.test_GetStoredRandomizedIndices())
        tupResults.append(self.test_AddRandomizedIndicesToXML())
        
        tupResults.append(self.test_ValidateImageOpacity())
        tupResults.append(self.test_AdjustXMLForRepeatedPage())

        
        logic.sessionTestStatus.DisplayTestResults(tupResults)
 
        # reset to allow for non-testing logic
        #    ie. display error messages when not testing
        os.environ["testing"] = "0"
 

    #------------------------------------------- 
    def test_BuildNavigationList(self):
        bTestResult = True
        self.fnName = sys._getframe().f_code.co_name
        
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
        
        
        self.oSession = Session()
        self.oSession.SetFilesIO(self._oFilesIO)
        self.oSession.SetIOXml(self.oIOXml)
        self.oSession.BuildNavigationList()
        lCompositeIndicesResult = self.oSession.GetNavigationList()
        
        if lCompositeIndicesResult == lExpectedCompositeIndices :
            bTestResult = True
        else:
            bTestResult = False
            
        # set quiz as complete for test purposes - so as not to trigger error message
        self.oSession.SetQuizComplete(True)

        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 
    def test_BuildNavigationList_RepNumbers(self):
        bTestResult = True
        self.fnName = sys._getframe().f_code.co_name
        
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
        
        
        self.oSession = Session()
        self.oSession.SetFilesIO(self._oFilesIO)
        self.oSession.SetIOXml(self.oIOXml)
        self.oSession.BuildNavigationList()
        lCompositeIndicesResult = self.oSession.GetNavigationList()
        
        if lCompositeIndicesResult == lExpectedCompositeIndices :
            bTestResult = True
        else:
            bTestResult = False
            
        # set quiz as complete for test purposes - so as not to trigger error message
        self.oSession.SetQuizComplete(True)

        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 
    def test_ShuffleNavigationList(self):
        bTestResult = True
        self.fnName = sys._getframe().f_code.co_name
        
        # build page/question set/page group composite indices list for testing
        '''
            eg.     Original XML List         Randomized Page Group indices      Shuffled Composite List
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
        ''' Test that only one PageGroup number was assigned for entire XML.
            Zeros are ignored because they will always appear at the beginning of a list.
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        sMsg = ''
        bTestResult = True

        # build XML
        xRoot = etree.Element("Session", RandomizePageGroups="Y")
        etree.SubElement(xRoot,"Page", PageGroup="0")   # this will be ignored
        etree.SubElement(xRoot,"Page", PageGroup="1")
        etree.SubElement(xRoot,"Page", PageGroup="1")
        etree.SubElement(xRoot,"Page", PageGroup="1")
            
            
        try:
            with self.assertRaises(Exception) as context:
                self._oFilesIO.ValidatePageGroupNumbers(xRoot)
            
            # the validation was supposed to catch an error 
            # check that the correct error was raised
            sMsg = context.exception.args[0]
            if sMsg.find('Validating PageGroups Error')>=0:
                bTestResult = True

            
        except:
            # validation did not catch the error
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
        liStoredIndices = self.oSession.GetStoredRandomizedIndices()
        
        
        if liStoredIndices == liExpectedIndices:
            bTestResult = True
        else:
            bTestResult = False
        
        
        tupResult = self.fnName, bTestResult
        return tupResult
        
    #------------------------------------------- 
    def test_AddRandomizedIndicesToXML(self):
        
        self.fnName = sys._getframe().f_code.co_name
        sMsg = ''
        bTestResult = True
        
        xRoot = etree.Element("Session", RandomizePageGroups="Y")
        etree.SubElement(xRoot,"Page", PageGroup="0")
        self.oIOXml.SetRootNode(xRoot)
        
        liIndices = [0,5,3,1,4,2]
        self.oSession.AddRandomizedIndicesToXML(liIndices)

        # read the updated xml to get what was stored 
        liStoredIndices = self.oSession.GetStoredRandomizedIndices()
        
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
    def test_ValidateImageOpacity(self):
        ''' test that the opacity attribute is properly validated
            1: valid number
            2: if value is negative
            3: if value is > 1
            4: if value is not a number
            5: missing opacity attribute (allowed)
        '''
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        bCaseTestResult = True
        iPageNum = 1

        xRoot = etree.Element("Session", RandomizePageGroups="Y")
        xPage = etree.SubElement(xRoot,"Page", ID="Patient1", PageGroup="0")

        # >>>>>>>>>>>>>>>>>>>>>>     Value is valid
        sMsg = ''
        xImage = etree.SubElement(xPage,"Image", ID="TestImage", Type="Volume", Opacity="0.7")
        xImageChild = etree.SubElement(xImage,"Path")
        xImageChild.text = "C:\TestFolder"
        self.oIOXml.SetRootNode(xRoot)

        sMsg = self._oFilesIO.ValidateOpacity(xImage, iPageNum)
        if sMsg == '':
            bCaseTestResult = True
        else:
            bCaseTestResult = False
                                  
            
        bTestResult = bTestResult * bCaseTestResult

        # >>>>>>>>>>>>>>>>>>>>>>     Value is negative
        sMsg = ''
        xImage = etree.SubElement(xPage,"Image", ID="TestImage", Type="Volume", Opacity="-0.9")
        xImageChild = etree.SubElement(xImage,"Path")
        xImageChild.text = "C:\TestFolder"
        
        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self._oFilesIO.ValidateOpacity(xImage, iPageNum)
            sMsg = context.exception.args[0]
            if sMsg.find('Invalid Opacity value') >= 0:
                bCaseTestResult = True
        except:
            # validation did not catch the error
            bCaseTestResult = False
        
        bTestResult = bTestResult * bCaseTestResult
        

        
        
        # >>>>>>>>>>>>>>>>>>>>>>     Value >1
        xImage = etree.SubElement(xPage,"Image", ID="TestImage", Type="Volume", Opacity="15")
        xImageChild = etree.SubElement(xImage,"Path")
        xImageChild.text = "C:\TestFolder"
        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self._oFilesIO.ValidateOpacity(xImage, iPageNum)
            sMsg = context.exception.args[0]
            if sMsg.find('Invalid Opacity value') >= 0:
                bCaseTestResult = True
        except:
            bCaseTestResult = False
            
        bTestResult = bTestResult * bCaseTestResult


        # >>>>>>>>>>>>>>>>>>>>>>     Invalid Value
        xImage = etree.SubElement(xPage,"Image", ID="TestImage", Type="Volume", Opacity="a")
        xImageChild = etree.SubElement(xImage,"Path")
        xImageChild.text = "C:\TestFolder"
        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self._oFilesIO.ValidateOpacity(xImage, iPageNum)
            sMsg = context.exception.args[0]
            if sMsg.find('Invalid Opacity value') >= 0:
                bCaseTestResult = True
        except:
            bCaseTestResult = False
            
        bTestResult = bTestResult * bCaseTestResult

        # >>>>>>>>>>>>>>>>>>>>>>     Missing attribute
        xImage = etree.SubElement(xPage,"Image", ID="TestImage", Type="Volume")
        xImageChild = etree.SubElement(xImage,"Path")
        xImageChild.text = "C:\TestFolder"
        self.oIOXml.SetRootNode(xRoot)
        
        
        sMsg = self._oFilesIO.ValidateOpacity(xImage, iPageNum)
        if sMsg == '':
            bCaseTestResult = True
        else:
            bCaseTestResult = False
            
        bTestResult = bTestResult * bCaseTestResult
        
        tupResult = self.fnName, bTestResult
        return tupResult
        
    #-------------------------------------------
    def test_AdjustXMLForRepeatedPage(self):

        self.fnName = sys._getframe().f_code.co_name
        sMsg = ''
        bTestResult = False

        # build XML
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
        
        
        #>>>>>>>>>>>>>>>>>>>>>>>

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

         
        
        #>>>>>>>>>>>>>>>>>>>>>>>
        
        self.oSession.BuildNavigationList()
        # set current index to the repeated xml element
        self.oSession.SetCurrentNavigationIndex(3)
        self.oSession.AdjustXMLForRepeatedPage()
        
        xAdjustedRoot = self.oIOXml.GetRootNode()
        sAdjustedXML = etree.tostring(xAdjustedRoot)
        sExpectedXML = etree.tostring(xExpectedRoot)
        
        # # for debug
        # print(sAdjustedXML)
        # print(sExpectedXML)
        
        if sAdjustedXML == sExpectedXML:
            bTestResult = True
    
        tupResult = self.fnName, bTestResult
        return tupResult
        
    #-------------------------------------------
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
