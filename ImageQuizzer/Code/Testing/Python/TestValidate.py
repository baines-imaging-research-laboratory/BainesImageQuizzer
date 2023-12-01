import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from Session import *
from TestingStatus import *
from Utilities.UtilsIOXml import *
from Utilities.UtilsValidate import *

import xml.dom.minidom

import os
import sys
import tempfile



##########################################################################
#
# TestValidate
#
##########################################################################

class TestValidate(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    #------------------------------------------- 

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Test Validate" 
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
# TestValidate_ModuleWidget
#
##########################################################################

class TestValidateWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """


    #------------------------------------------- 
    def setup(self):
        self.developerMode = True
        ScriptedLoadableModuleWidget.setup(self)


##########################################################################
#
# TestValidate_ModuleLogic
#
##########################################################################

class TestValidateLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget
    """

    def __init__(self):
        ScriptedLoadableModuleLogic.__init__(self)
        self.sClassName = type(self).__name__
        print("\n************ Unittesting for class Validate ************\n")
        self.sessionTestStatus = TestingStatus()


##########################################################################
#
# TestSession_ModuleTest
#
##########################################################################

class TestValidateTest(ScriptedLoadableModuleTest):
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
        self.oValidation = UtilsValidate(self._oFilesIO)
        self.oIOXml = self.oValidation.oIOXml
        
        # create/set environment variable to be checked in UtilsIOXml class
        #    to prevent displaying error messages during testing
        os.environ["testing"] = "1"
        self._oFilesIO.setupTestEnvironment()
        self.oValidation.setupTestEnvironment()

        self.sTempDir = os.path.join(tempfile.gettempdir(),'ImageQuizzer')
        if not os.path.exists(self.sTempDir):
            os.makedirs(self.sTempDir)

    #------------------------------------------- 
    def runTest(self ):
        # Tests are initiated in Slicer by pressing the Reload and Test button

        self.setUp()
        # self.sTempDir = os.path.join(tempfile.gettempdir(),'ImageQuizzer')

        logic = TestValidateLogic()

        tupResults = []
        tupResults.append(self.test_ValidatePageGroupNumbers_MissingPageGroup())
        tupResults.append(self.test_ValidatePageGroupNumbers_InvalidNumber())
        tupResults.append(self.test_ValidatePageGroupNumbers_NotEnoughPageGroups())
        tupResults.append(self.test_ValidateImageOpacity())

        tupResults.append(self.test_ValidateGoToBookmarkRequest_Valid_NoRandomize())
        tupResults.append(self.test_ValidateGoToBookmarkRequest_Valid_Randomize())
        tupResults.append(self.test_ValidateGoToBookmarkRequest_Valid_BothPageGroups0s())
        tupResults.append(self.test_ValidateGoToBookmarkRequest_Valid_PageGroup0_OnSetID())
        tupResults.append(self.test_ValidateGoToBookmarkRequest_Valid_PageGroup0_Reversed())
        tupResults.append(self.test_ValidateGoToBookmarkRequest_Invalid_OrderWithPageGroup0OnDisplayID())
        tupResults.append(self.test_ValidateGoToBookmarkRequest_Invalid_PageGroup())
        tupResults.append(self.test_ValidateGoToBookmarkRequest_Invalid_NoRandomize())
        tupResults.append(self.test_ValidateGoToBookmarkRequest_Invalid_Order_SamePageGroups())
        tupResults.append(self.test_ValidateGoToBookmarkRequest_Invalid_PageGroup_Reversed())
        tupResults.append(self.test_ValidateGoToBookmarkRequest_Invalid_OrderWithBothPageGroup0s())
        tupResults.append(self.test_ValidateGoToBookmarkRequest_Invalid_OrderWithPageGroup0_OnDisplayID_Reversed())
        
        tupResults.append(self.test_ValidateDisplayLabelMapID_InvalidPath())
        tupResults.append(self.test_ValidateDisplayLabelMapID_Valid_NoRandomize())
        tupResults.append(self.test_ValidateDisplayLabelMapID_Valid_Randomize())
        tupResults.append(self.test_ValidateDisplayLabelMapID_Valid_BothPageGroup0s())
        tupResults.append(self.test_ValidateDisplayLabelMapID_Valid_PageGroup0_OnSetID())
        tupResults.append(self.test_ValidateDisplayLabelMapID_Valid_PageGroup0_Reversed())
        tupResults.append(self.test_ValidateDisplayLabelMapID_Invalid_Order_PageGroup0OnDisplayID())
        tupResults.append(self.test_ValidateDisplayLabelMapID_Invalid_PageGroup())
        tupResults.append(self.test_ValidateDisplayLabelMapID_Invalid_NoRandomize())
        tupResults.append(self.test_ValidateDisplayLabelMapID_Invalid_Order_SamePageGroups())
        tupResults.append(self.test_ValidateDisplayLabelMapID_Invalid_PageGroup_Reversed())
        tupResults.append(self.test_ValidateDisplayLabelMapID_Invalid_Order_BothPageGroups0s())
        tupResults.append(self.test_ValidateDisplayLabelMapID_Invalid_Order_PageGroup0_OnDisplayID_Reversed())



        logic.sessionTestStatus.DisplayTestResults(tupResults)
        
        #>>>>>>>>>>> cleanup <<<<<<<<<<<<
 
        # reset to allow for non-testing logic
        #    ie. display error messages when not testing
        os.environ["testing"] = "0"
        
        
        # REMOVE TEMP FILES >>>>>>>> comment out for debugging for visualization
        if os.path.exists(self.sTempDir) and os.path.isdir(self.sTempDir):
            shutil.rmtree(self.sTempDir)
            
            
            
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
                self.oValidation.ValidatePageGroupNumbers(xRoot)
                
            sMsg = context.exception.args[0]
            if sMsg.find('Missing PageGroup attribute')>=0:
                bTestResult = True
            else:
                raise   # another error
               
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
                self.oValidation.ValidatePageGroupNumbers(xRoot)

            sMsg = context.exception.args[0]
            if sMsg.find('Invalid PageGroup value')>=0:
                bTestResult = True
            else:
                raise   # another error

            
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
                self.oValidation.ValidatePageGroupNumbers(xRoot)
            
            # the validation was supposed to catch an error 
            # check that the correct error was raised
            sMsg = context.exception.args[0]
            if sMsg.find('Validating PageGroups Error')>=0:
                bTestResult = True
            else:
                raise   # another error
            
        except:
            # validation did not catch the error
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

        sMsg = self.oValidation.ValidateOpacity(xImage, iPageNum)
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
                self.oValidation.ValidateOpacity(xImage, iPageNum)
            sMsg = context.exception.args[0]
            if sMsg.find('Invalid Opacity value') >= 0:
                bCaseTestResult = True
            else:
                raise   # another error

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
                self.oValidation.ValidateOpacity(xImage, iPageNum)
            sMsg = context.exception.args[0]
            if sMsg.find('Invalid Opacity value') >= 0:
                bCaseTestResult = True
            else:
                raise   # another error

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
                self.oValidation.ValidateOpacity(xImage, iPageNum)
            sMsg = context.exception.args[0]
            if sMsg.find('Invalid Opacity value') >= 0:
                bCaseTestResult = True
            else:
                raise   # another error

        except:
            bCaseTestResult = False
            
        bTestResult = bTestResult * bCaseTestResult

        # >>>>>>>>>>>>>>>>>>>>>>     Missing attribute
        xImage = etree.SubElement(xPage,"Image", ID="TestImage", Type="Volume")
        xImageChild = etree.SubElement(xImage,"Path")
        xImageChild.text = "C:\TestFolder"
        self.oIOXml.SetRootNode(xRoot)
        
        
        sMsg = self.oValidation.ValidateOpacity(xImage, iPageNum)
        if sMsg == '':
            bCaseTestResult = True
        else:
            bCaseTestResult = False
            
        bTestResult = bTestResult * bCaseTestResult
        
        tupResult = self.fnName, bTestResult
        return tupResult
        

    #------------------------------------------- 
    #------------------------------------------- 
    #------------------------------------------- 
    #------------BookmarkID tests--------------- 
    #------------------------------------------- 
    #------------------------------------------- 

    #------------------------------------------- 
    def test_ValidateGoToBookmarkRequest_Valid_NoRandomize(self):
        ''' BookmarkID must appear before GoToBookmark attribute
            Test with the same PageGroup number.
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        sMsg = ''
        
        xRoot = self.CreateXMLBaseForTests()

        # add attributes to specific pages
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("BookmarkID","ReturnHere")
        xPageNode.set("PageGroup","2")

        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 5)
        xPageNode.set("GoToBookmark","ReturnHere ABORT")
        xPageNode.set("PageGroup","3")

        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self.oValidation.ValidateGoToBookmarkRequest()
            sMsg = context.exception.args[0]
            if sMsg.find('Missing historical BookmarkID') >= 0:
                bTestResult = False
            else:
                raise   # another error

        except:
            bTestResult = True
        
        
        tupResult = self.fnName, bTestResult
        return tupResult
    
    
    
    #------------------------------------------- 
    def test_ValidateGoToBookmarkRequest_Valid_Randomize(self):
        ''' BookmarkID must appear before GoToBookmark attribute
            Test with the same PageGroup number.
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        sMsg = ''
        
        xRoot = self.CreateXMLBaseForTests()
        
        xRoot.set("RandomizePageGroups","Y")

        # add attributes to specific pages
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("BookmarkID","ReturnHere")
        xPageNode.set("PageGroup","2")

        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 5)
        xPageNode.set("GoToBookmark","ReturnHere ABORT")
        xPageNode.set("PageGroup","2")

        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self.oValidation.ValidateGoToBookmarkRequest()
            sMsg = context.exception.args[0]
            if sMsg.find('Missing historical BookmarkID') >= 0:
                bTestResult = False
            else:
                raise   # another error

        except:
            bTestResult = True
        
        
        tupResult = self.fnName, bTestResult
        return tupResult
    
    #------------------------------------------- 
    def test_ValidateGoToBookmarkRequest_Valid_BothPageGroups0s(self):
        ''' BookmarkID must appear before GoToBookmark attribute
            Even if randomizing is turned on, a BookmarkID can be on a page with PageGroup=0
            since those pages don't get randomized.
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        sMsg = ''
        
        xRoot = self.CreateXMLBaseForTests()
        xRoot.set("RandomizePageGroups","Y")

        # add attributes to specific pages
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("BookmarkID","ReturnHere")
        xPageNode.set("PageGroup","0")

        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 5)
        xPageNode.set("GoToBookmark","ReturnHere ABORT")
        xPageNode.set("PageGroup","0")

        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self.oValidation.ValidateGoToBookmarkRequest()
            sMsg = context.exception.args[0]
            if sMsg.find('Missing historical BookmarkID') >= 0:
                bTestResult = False
            else:
                raise   # another error

        except:
            bTestResult = True
        
        
        tupResult = self.fnName, bTestResult
        return tupResult
    
    #------------------------------------------- 
    def test_ValidateGoToBookmarkRequest_Valid_PageGroup0_OnSetID(self):
        ''' BookmarkID must appear before GoToBookmark attribute
            Even if randomizing is turned on, a BookmarkID can be on a page with PageGroup=0
            since those pages don't get randomized.
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        sMsg = ''
        
        xRoot = self.CreateXMLBaseForTests()
        xRoot.set("RandomizePageGroups","Y")

        # add attributes to specific pages
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("BookmarkID","ReturnHere")
        xPageNode.set("PageGroup","0")

        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 5)
        xPageNode.set("GoToBookmark","ReturnHere ABORT")
        xPageNode.set("PageGroup","2")

        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self.oValidation.ValidateGoToBookmarkRequest()
            sMsg = context.exception.args[0]
            if sMsg.find('Missing historical BookmarkID') >= 0:
                bTestResult = False
            else:
                raise   # another error

        except:
            bTestResult = True
        
        
        tupResult = self.fnName, bTestResult
        return tupResult
    
    #------------------------------------------- 
    def test_ValidateGoToBookmarkRequest_Valid_PageGroup0_Reversed(self):
        ''' BookmarkID must appear before GoToBookmark attribute
            Even if randomizing is turned on, a BookmarkID can be on a page with PageGroup=0
            since those pages don't get randomized.
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        sMsg = ''
        
        xRoot = self.CreateXMLBaseForTests()
        xRoot.set("RandomizePageGroups","Y")

        # add attributes to specific pages
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 5)
        xPageNode.set("BookmarkID","ReturnHere")
        xPageNode.set("PageGroup","0")

        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("GoToBookmark","ReturnHere ABORT")
        xPageNode.set("PageGroup","2")

        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self.oValidation.ValidateGoToBookmarkRequest()
            sMsg = context.exception.args[0]
            if sMsg.find('Missing historical BookmarkID') >= 0:
                bTestResult = False
            else:
                raise   # another error

        except:
            bTestResult = True
        
        
        tupResult = self.fnName, bTestResult
        return tupResult
    
    #------------------------------------------- 
    def test_ValidateGoToBookmarkRequest_Invalid_OrderWithPageGroup0OnDisplayID(self):
        ''' Test when BookmarkID is on a Page that follows the GoToBookmark attribute.
            Randomizing is on and page groups match at 0
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        
        xRoot = self.CreateXMLBaseForTests()

        xRoot.set("RandomizePageGroups","Y")


        # add attributes to specific pages
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("BookmarkID","ReturnHere")
        xPageNode.set("PageGroup","2")

        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 5)
        xPageNode.set("GoToBookmark","ReturnHere ABORT")
        xPageNode.set("PageGroup","0")

        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self.oValidation.ValidateGoToBookmarkRequest()
            sMsg = context.exception.args[0]
            if sMsg.find('Missing historical BookmarkID') >= 0:
                bTestResult = True
            else:
                raise   # another error

        except:
            bTestResult = False

        
        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 
    def test_ValidateGoToBookmarkRequest_Invalid_PageGroup(self):
        ''' BookmarkID must appear before GoToBookmark attribute
            Test with invalid PageGroup numbers
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        sMsg = ''
        
        xRoot = self.CreateXMLBaseForTests()

        xRoot.set("RandomizePageGroups","Y")
        
        # add attributes to specific pages
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("BookmarkID","ReturnHere")
        xPageNode.set("PageGroup","2")

        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 5)
        xPageNode.set("GoToBookmark","ReturnHere ABORT")
        xPageNode.set("PageGroup","3")

        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self.oValidation.ValidateGoToBookmarkRequest()
            sMsg = context.exception.args[0]
            if sMsg.find('do not match') >= 0:
                bTestResult = True
            else:
                raise   # another error

        except:
            bTestResult = False
        
        
        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 
    def test_ValidateGoToBookmarkRequest_Invalid_NoRandomize(self):
        ''' Test when BookmarkID is on a Page that follows the GoToBookmark attribute.
            
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        
        xRoot = self.CreateXMLBaseForTests()
        self.oIOXml.SetRootNode(xRoot)

        # add attributes to specific pages
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 5)
        xPageNode.set("BookmarkID","ReturnHere")
        xPageNode.set("PageGroup","2")

        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("GoToBookmark","ReturnHere ABORT")
        xPageNode.set("PageGroup","3")

        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self.oValidation.ValidateGoToBookmarkRequest()
            sMsg = context.exception.args[0]
            if sMsg.find('Missing historical BookmarkID') >= 0:
                bTestResult = True
            else:
                raise   # another error

        except:
            bTestResult = False

        
        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 
    def test_ValidateGoToBookmarkRequest_Invalid_Order_SamePageGroups(self):
        ''' Test when BookmarkID is on a Page that follows the GoToBookmark attribute.
            
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        
        xRoot = self.CreateXMLBaseForTests()
        
        xRoot.set("RandomizePageGroups","Y")
        self.oIOXml.SetRootNode(xRoot)

        # add attributes to specific pages
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 5)
        xPageNode.set("BookmarkID","ReturnHere")
        xPageNode.set("PageGroup","2")

        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("GoToBookmark","ReturnHere ABORT")
        xPageNode.set("PageGroup","2")

        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self.oValidation.ValidateGoToBookmarkRequest()
            sMsg = context.exception.args[0]
            if sMsg.find('Missing historical BookmarkID') >= 0:
                bTestResult = True
            else:
                raise   # another error

        except:
            bTestResult = False

        
        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 
    def test_ValidateGoToBookmarkRequest_Invalid_PageGroup_Reversed(self):
        ''' BookmarkID must appear before GoToBookmark attribute
            Test with invalid PageGroup numbers
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        sMsg = ''
        
        xRoot = self.CreateXMLBaseForTests()

        xRoot.set("RandomizePageGroups","Y")
        
        # add attributes to specific pages
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 5)
        xPageNode.set("BookmarkID","ReturnHere")
        xPageNode.set("PageGroup","3")

        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("GoToBookmark","ReturnHere ABORT")
        xPageNode.set("PageGroup","2")

        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self.oValidation.ValidateGoToBookmarkRequest()
            sMsg = context.exception.args[0]
            if sMsg.find('do not match') >= 0:
                bTestResult = True
            else:
                raise   # another error

        except:
            bTestResult = False
        
        
        tupResult = self.fnName, bTestResult
        return tupResult


    #------------------------------------------- 
    def test_ValidateGoToBookmarkRequest_Invalid_OrderWithBothPageGroup0s(self):
        ''' Test when BookmarkID is on a Page that follows the GoToBookmark attribute.
            Randomizing is on and page groups match at 0
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        
        xRoot = self.CreateXMLBaseForTests()

        xRoot.set("RandomizePageGroups","Y")


        # add attributes to specific pages
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 5)
        xPageNode.set("BookmarkID","ReturnHere")
        xPageNode.set("PageGroup","0")

        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("GoToBookmark","ReturnHere ABORT")
        xPageNode.set("PageGroup","0")

        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self.oValidation.ValidateGoToBookmarkRequest()
            sMsg = context.exception.args[0]
            if sMsg.find('Missing historical BookmarkID') >= 0:
                bTestResult = True
            else:
                raise   # another error

        except:
            bTestResult = False

        
        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 
    def test_ValidateGoToBookmarkRequest_Invalid_OrderWithPageGroup0_OnDisplayID_Reversed(self):
        ''' Test when BookmarkID is on a Page that follows the GoToBookmark attribute.
            Randomizing is on and page groups match at 0
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        
        xRoot = self.CreateXMLBaseForTests()

        xRoot.set("RandomizePageGroups","Y")


        # add attributes to specific pages
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 5)
        xPageNode.set("BookmarkID","ReturnHere")
        xPageNode.set("PageGroup","2")

        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("GoToBookmark","ReturnHere ABORT")
        xPageNode.set("PageGroup","0")

        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self.oValidation.ValidateGoToBookmarkRequest()
            sMsg = context.exception.args[0]
            if sMsg.find('Missing historical BookmarkID') >= 0:
                bTestResult = True
            else:
                raise   # another error

        except:
            bTestResult = False

        
        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 
    #------------------------------------------- 
    #------------------------------------------- 
    #------------LabelMapID tests--------------- 
    #------------------------------------------- 
    #------------------------------------------- 

    
    #------------------------------------------- 
    def test_ValidateDisplayLabelMapID_InvalidPath(self):
        ''' BookmarkID must appear before GoToBookmark attribute
            Test with invalid labelmap path
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        sMsg = ''
        
        xRoot = self.CreateXMLBaseForTests()

        xRoot.set("RandomizePageGroups","Y")
        
        # add attributes to specific pages
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("PageGroup","3")
        xImage0 = etree.SubElement(xPageNode,"Image", {"LabelMapID":"DCE-Contour"})
        xPath0 = etree.SubElement(xImage0,"Path")
        xPath0.text = "C:\\Documents"

        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 5)
        xPageNode.set("PageGroup","3")
        xImage1 = etree.SubElement(xPageNode,"Image", {"DisplayLabelMapID":"DCE-Contour"})
        xPath1 = etree.SubElement(xImage1,"Path")
        xPath1.text = "C:\\Documents\\NewFolder"

        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self.oValidation.ValidateDisplayLabelMapID()
            sMsg = context.exception.args[0]
            if sMsg.find('do not match') >= 0:
                bTestResult = True
            else:
                raise   # another error

        except:
            bTestResult = False
        
        
        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 
    def test_ValidateDisplayLabelMapID_Valid_NoRandomize(self):
        ''' LabelMapID must appear before DisplayLabelMapID attribute
            Test with the same PageGroup number.
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        sMsg = ''
        
        xRoot = self.CreateXMLBaseForTests()

        # add attributes to specific pages
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("PageGroup","2")
        xImage0 = etree.SubElement(xPageNode,"Image", {"LabelMapID":"DCE-Contour"})
        

        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 5)
        xPageNode.set("PageGroup","3")
        xImage1 = etree.SubElement(xPageNode,"Image", {"DisplayLabelMapID":"DCE-Contour"})

        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self.oValidation.ValidateDisplayLabelMapID()
            sMsg = context.exception.args[0]
            if sMsg.find('Missing historical LabelMapID') >= 0:
                bTestResult = False
            else:
                raise   # another error

        except:
            bTestResult = True
        
        
        tupResult = self.fnName, bTestResult
        return tupResult
    
    #------------------------------------------- 
    def test_ValidateDisplayLabelMapID_Valid_Randomize(self):
        ''' LabelMapID must appear before DisplayLabelMapID attribute
            Test with the same PageGroup number.
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        sMsg = ''
        
        xRoot = self.CreateXMLBaseForTests()
        xRoot.set("RandomizePageGroups","Y")

        # add attributes to specific pages
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("PageGroup","2")
        xImage0 = etree.SubElement(xPageNode,"Image", {"LabelMapID":"DCE-Contour"})
        

        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 5)
        xPageNode.set("PageGroup","2")
        xImage1 = etree.SubElement(xPageNode,"Image", {"DisplayLabelMapID":"DCE-Contour"})

        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self.oValidation.ValidateDisplayLabelMapID()
            sMsg = context.exception.args[0]
            if sMsg.find('Missing historical LabelMapID') >= 0:
                bTestResult = False
            else:
                raise   # another error

        except:
            bTestResult = True
        
        
        tupResult = self.fnName, bTestResult
        return tupResult
    
    #------------------------------------------- 
    def test_ValidateDisplayLabelMapID_Valid_BothPageGroup0s(self):
        ''' LabelMapID must appear before DisplayLabelMapID attribute
            Test with the same PageGroup number.
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        sMsg = ''
        
        xRoot = self.CreateXMLBaseForTests()
        xRoot.set("RandomizePageGroups","Y")

        # add attributes to specific pages
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("PageGroup","0")
        xImage0 = etree.SubElement(xPageNode,"Image", {"LabelMapID":"DCE-Contour"})
        

        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 5)
        xPageNode.set("PageGroup","0")
        xImage1 = etree.SubElement(xPageNode,"Image", {"DisplayLabelMapID":"DCE-Contour"})

        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self.oValidation.ValidateDisplayLabelMapID()
            sMsg = context.exception.args[0]
            if sMsg.find('Missing historical LabelMapID') >= 0:
                bTestResult = False
            else:
                raise   # another error

        except:
            bTestResult = True
        
        
        tupResult = self.fnName, bTestResult
        return tupResult
    
    #------------------------------------------- 
    def test_ValidateDisplayLabelMapID_Valid_PageGroup0_OnSetID(self):
        ''' LabelMapID must appear before DisplayLabelMapID attribute
            Test with Randomizing and finding the historical on PageGroup = 0.
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        sMsg = ''
        
        xRoot = self.CreateXMLBaseForTests()
        
        xRoot.set("RandomizePageGroups","Y")

        # add attributes to specific pages
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("PageGroup","0")
        xImage0 = etree.SubElement(xPageNode,"Image", {"LabelMapID":"DCE-Contour"})
        

        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 5)
        xPageNode.set("PageGroup","2")
        xImage1 = etree.SubElement(xPageNode,"Image", {"DisplayLabelMapID":"DCE-Contour"})

        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self.oValidation.ValidateDisplayLabelMapID()
            sMsg = context.exception.args[0]
            if sMsg.find('Missing historical LabelMapID') >= 0:
                bTestResult = False
            else:
                raise   # another error

        except:
            bTestResult = True
        
        
        tupResult = self.fnName, bTestResult
        return tupResult
    
    #------------------------------------------- 
    def test_ValidateDisplayLabelMapID_Valid_PageGroup0_Reversed(self):
        ''' LabelMapID must appear before DisplayLabelMapID attribute
            Test with PageGroup=0 when display is on a Page before label map id with randomizing on.
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        sMsg = ''
        
        xRoot = self.CreateXMLBaseForTests()
        
        xRoot.set("RandomizePageGroups","Y")

        # add attributes to specific pages
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 5)
        xPageNode.set("PageGroup","0")
        xImage0 = etree.SubElement(xPageNode,"Image", {"LabelMapID":"DCE-Contour"})
        

        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("PageGroup","2")
        xImage1 = etree.SubElement(xPageNode,"Image", {"DisplayLabelMapID":"DCE-Contour"})

        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self.oValidation.ValidateDisplayLabelMapID()
            sMsg = context.exception.args[0]
            if sMsg.find('Missing historical LabelMapID') >= 0:
                bTestResult = False
            else:
                raise   # another error

        except:
            bTestResult = True
        
        
        tupResult = self.fnName, bTestResult
        return tupResult
    
    #------------------------------------------- 
    def test_ValidateDisplayLabelMapID_Invalid_Order_PageGroup0OnDisplayID(self):
        ''' LabelMapID must appear before DisplayLabelMapID attribute
            Test with invalid order
        '''
         
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        sMsg = ''
         
        xRoot = self.CreateXMLBaseForTests()
         
        xRoot.set("RandomizePageGroups","Y")
 
        # add attributes to specific pages
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("PageGroup","2")
        xImage0 = etree.SubElement(xPageNode,"Image", {"LabelMapID":"DCE-Contour"})
 
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 5)
        xPageNode.set("PageGroup","0")
        xImage1 = etree.SubElement(xPageNode,"Image", {"DisplayLabelMapID":"DCE-Contour"})
 
        self.oIOXml.SetRootNode(xRoot)
         
        try:
            with self.assertRaises(Exception) as context:
                self.oValidation.ValidateDisplayLabelMapID()
            sMsg = context.exception.args[0]
            if sMsg.find('do not match') >= 0:
                bTestResult = True
            else:
                raise   # another error
 
        except:
            bTestResult = False
         
         
        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 
    def test_ValidateDisplayLabelMapID_Invalid_PageGroup(self):
        ''' BookmarkID must appear before GoToBookmark attribute
            Test with invalid PageGroup numbers
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        sMsg = ''
        
        xRoot = self.CreateXMLBaseForTests()

        xRoot.set("RandomizePageGroups","Y")
        
        # add attributes to specific pages
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("PageGroup","2")
        xImage0 = etree.SubElement(xPageNode,"Image", {"LabelMapID":"DCE-Contour"})

        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 5)
        xPageNode.set("PageGroup","3")
        xImage1 = etree.SubElement(xPageNode,"Image", {"DisplayLabelMapID":"DCE-Contour"})

        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self.oValidation.ValidateDisplayLabelMapID()
            sMsg = context.exception.args[0]
            if sMsg.find('do not match') >= 0:
                bTestResult = True
            else:
                raise   # another error

        except:
            bTestResult = False
        
        
        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 
    def test_ValidateDisplayLabelMapID_Invalid_NoRandomize(self):
        ''' LabelMapID must appear before DisplayLabelMapID attribute
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        sMsg = ''
        
        xRoot = self.CreateXMLBaseForTests()
        
        # add attributes to specific pages
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 5)
        xPageNode.set("PageGroup","2")
        xImage0 = etree.SubElement(xPageNode,"Image", {"LabelMapID":"DCE-Contour"})

        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("PageGroup","3")
        xImage1 = etree.SubElement(xPageNode,"Image", {"DisplayLabelMapID":"DCE-Contour"})

        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self.oValidation.ValidateDisplayLabelMapID()
            sMsg = context.exception.args[0]
            if sMsg.find('do not match') >= 0:
                bTestResult = True
            else:
                raise   # another error

        except:
            bTestResult = False
        
        
        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 
    def test_ValidateDisplayLabelMapID_Invalid_Order_SamePageGroups(self):
        ''' LabelMapID must appear before DisplayLabelMapID attribute
            Test with invalid order
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        sMsg = ''
        
        xRoot = self.CreateXMLBaseForTests()
        
        xRoot.set("RandomizePageGroups","Y")

        # add attributes to specific pages
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 5)
        xPageNode.set("PageGroup","2")
        xImage0 = etree.SubElement(xPageNode,"Image", {"LabelMapID":"DCE-Contour"})

        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("PageGroup","2")
        xImage1 = etree.SubElement(xPageNode,"Image", {"DisplayLabelMapID":"DCE-Contour"})

        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self.oValidation.ValidateDisplayLabelMapID()
            sMsg = context.exception.args[0]
            if sMsg.find('do not match') >= 0:
                bTestResult = True
            else:
                raise   # another error

        except:
            bTestResult = False
        
        
        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 
    def test_ValidateDisplayLabelMapID_Invalid_PageGroup_Reversed(self):
        ''' LabelMapID must appear before DisplayLabelMapID attribute
            Test with invalid order
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        sMsg = ''
        
        xRoot = self.CreateXMLBaseForTests()
        
        xRoot.set("RandomizePageGroups","Y")

        # add attributes to specific pages
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 5)
        xPageNode.set("PageGroup","3")
        xImage0 = etree.SubElement(xPageNode,"Image", {"LabelMapID":"DCE-Contour"})

        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("PageGroup","2")
        xImage1 = etree.SubElement(xPageNode,"Image", {"DisplayLabelMapID":"DCE-Contour"})

        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self.oValidation.ValidateDisplayLabelMapID()
            sMsg = context.exception.args[0]
            if sMsg.find('do not match') >= 0:
                bTestResult = True
            else:
                raise   # another error

        except:
            bTestResult = False
        
        
        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 
    def test_ValidateDisplayLabelMapID_Invalid_Order_BothPageGroups0s(self):
        ''' LabelMapID must appear before DisplayLabelMapID attribute
            Test with invalid order
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        sMsg = ''
        
        xRoot = self.CreateXMLBaseForTests()
        
        xRoot.set("RandomizePageGroups","Y")

        # add attributes to specific pages
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 5)
        xPageNode.set("PageGroup","0")
        xImage0 = etree.SubElement(xPageNode,"Image", {"LabelMapID":"DCE-Contour"})

        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("PageGroup","0")
        xImage1 = etree.SubElement(xPageNode,"Image", {"DisplayLabelMapID":"DCE-Contour"})

        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self.oValidation.ValidateDisplayLabelMapID()
            sMsg = context.exception.args[0]
            if sMsg.find('do not match') >= 0:
                bTestResult = True
            else:
                raise   # another error

        except:
            bTestResult = False
        
        
        tupResult = self.fnName, bTestResult
        return tupResult


    #------------------------------------------- 
    def test_ValidateDisplayLabelMapID_Invalid_Order_PageGroup0_OnDisplayID_Reversed(self):
        ''' LabelMapID must appear before DisplayLabelMapID attribute
            Test with invalid order
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        sMsg = ''
        
        xRoot = self.CreateXMLBaseForTests()
        
        xRoot.set("RandomizePageGroups","Y")

        # add attributes to specific pages
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 5)
        xPageNode.set("PageGroup","2")
        xImage0 = etree.SubElement(xPageNode,"Image", {"LabelMapID":"DCE-Contour"})

        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("PageGroup","0")
        xImage1 = etree.SubElement(xPageNode,"Image", {"DisplayLabelMapID":"DCE-Contour"})

        self.oIOXml.SetRootNode(xRoot)
        
        try:
            with self.assertRaises(Exception) as context:
                self.oValidation.ValidateDisplayLabelMapID()
            sMsg = context.exception.args[0]
            if sMsg.find('do not match') >= 0:
                bTestResult = True
            else:
                raise   # another error

        except:
            bTestResult = False
        
        
        tupResult = self.fnName, bTestResult
        return tupResult

            
    #-------------------------------------------
    #-------------------------------------------
    #
    #        Helper Functions
    #
    #-------------------------------------------
    #-------------------------------------------
    def CreateXMLBaseForTests(self):
    
        xRoot = etree.Element("Session")
        xPage0 = etree.SubElement(xRoot,"Page", {"ID":"Pt1"})
        xPage1 = etree.SubElement(xRoot,"Page", {"ID":"Pt2"})
        xPage2 = etree.SubElement(xRoot,"Page", {"ID":"Pt3"})
        xPage3 = etree.SubElement(xRoot,"Page", {"ID":"Pt4"})
        xPage4 = etree.SubElement(xRoot,"Page", {"ID":"Pt5"})
        xPage5 = etree.SubElement(xRoot,"Page", {"ID":"Pt6"})

    
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
            
