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
        self.oIOXml = UtilsIOXml()
        self.oUtilsValidate = UtilsValidate(self._oFilesIO)
        
        # create/set environment variable to be checked in UtilsIOXml class
        #    to prevent displaying error messages during testing
        os.environ["testing"] = "1"
        self._oFilesIO.setupTestEnvironment()
        self.oUtilsValidate.setupTestEnvironment()

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
                self.oUtilsValidate.ValidatePageGroupNumbers(xRoot)
                
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
                self.oUtilsValidate.ValidatePageGroupNumbers(xRoot)

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
                self.oUtilsValidate.ValidatePageGroupNumbers(xRoot)
            
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

        sMsg = self.oUtilsValidate.ValidateOpacity(xImage, iPageNum)
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
                self.oUtilsValidate.ValidateOpacity(xImage, iPageNum)
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
                self.oUtilsValidate.ValidateOpacity(xImage, iPageNum)
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
                self.oUtilsValidate.ValidateOpacity(xImage, iPageNum)
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
        
        
        sMsg = self.oUtilsValidate.ValidateOpacity(xImage, iPageNum)
        if sMsg == '':
            bCaseTestResult = True
        else:
            bCaseTestResult = False
            
        bTestResult = bTestResult * bCaseTestResult
        
        tupResult = self.fnName, bTestResult
        return tupResult
        



            
    #-------------------------------------------
    #-------------------------------------------
    #
    #        Helper Functions
    #
    #-------------------------------------------
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
            
