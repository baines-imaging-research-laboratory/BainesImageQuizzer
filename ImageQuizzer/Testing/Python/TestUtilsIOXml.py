import os, sys
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from UtilsIOXml import *
from TestingStatus import *

import xml
from xml.dom import minidom


##########################################################################
#
# TestUtilsIOXml
#
##########################################################################

class TestUtilsIOXml(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    #------------------------------------------- 

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Test IO Utilities for XML handling" 
        self.parent.categories = ["Testing.ImageQuizzer"]
        self.parent.dependencies = []
        self.parent.contributors = ["Carol Johnson (Baines Imaging Research Laboratories)"] 
        self.parent.helpText = """
        This tests IO handling of xml files.
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

class TestUtilsIOXmlWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    #------------------------------------------- 
    def setup(self):
        self.developerMode = True
        ScriptedLoadableModuleWidget.setup(self)


##########################################################################
#
# TestUtilsIOXml_ModuleLogic
#
##########################################################################

class TestUtilsIOXmlLogic(ScriptedLoadableModuleLogic):
    """
    """

    def __init__(self):
        ScriptedLoadableModuleLogic.__init__(self)
        self.sClassName = type(self).__name__
        print("\n************ Unittesting for class UtilsIOXml ************\n")
        self.sessionTestStatus = TestingStatus()


##########################################################################
#
# TestUtilsIOXml_ModuleTest
#
##########################################################################

class TestUtilsIOXmlTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    #------------------------------------------- 

    def setUp(self):
        """ 
        """
        slicer.mrmlScene.Clear(0)
        self.sClassName = type(self).__name__

        # define path for test data
        moduleName = 'ImageQuizzer'
        scriptedModulesPath = eval('slicer.modules.%s.path' % moduleName.lower())
        scriptedModulesPath = os.path.dirname(scriptedModulesPath)
        self.testDataPath = os.path.join(scriptedModulesPath, 'Testing', 'TestData', 'InputXmlFiles')
        self.oIOXml = UtilsIOXml()

       
    #------------------------------------------- 

    def runTest(self):

        self.setUp()
        logic = TestUtilsIOXmlLogic()

        tupResults = []
        tupResults.append(self.test_NoErrors_OpenXml())
        tupResults.append(self.test_NoXmlFileFound())
        tupResults.append(self.test_InvalidRootNode())
        tupResults.append(self.test_ParsingError())
        # TODO: tupResults.append(self.test_InvalidNodeType())
        tupResults.append(self.test_GetPageAttributes())
        
        logic.sessionTestStatus.DisplayTestResults(tupResults)
 

    #------------------------------------------- 

    def test_NoErrors_OpenXml(self):
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name
         
  
        # test simple items xml file - confirm root name
        sRootName = 'data'
        sXmlFile = 'items.xml'
        sXmlPath = os.path.join(self.testDataPath, sXmlFile)
  
          
        [bTestResult, xRootNode] = self.oIOXml.openXml(sXmlPath,'data')
        if (self.oIOXml.getNodeName(xRootNode) == sRootName):
            bTestResult = bTestResult * True
        else:
            bTestResult = False
            
        
        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 

    def test_NoXmlFileFound(self):
        self.fnName = sys._getframe().f_code.co_name
      
        sXmlFile = 'ThisFileDoesNotExist.xml'
        sXmlPath = os.path.join(self.testDataPath, sXmlFile)
   
        try:
            bTestResult = True
            with self.assertRaises(Exception):
                self.oIOXml.openXml(sXmlPath,'data')
        except:
            bTestResult = False # there should have been an exception
    
        tupResult = self.fnName, bTestResult
        return tupResult
         
    #------------------------------------------- 

    def test_InvalidRootNode(self):
        self.fnName = sys._getframe().f_code.co_name
      
        sXmlFile = 'items.xml'
        sXmlPath = os.path.join(self.testDataPath, sXmlFile)
   
        try:
            bTestResult = True
            with self.assertRaises(Exception):
                self.oIOXml.openXml(sXmlPath,'Session')
        except:
            bTestResult = False # there should have been an exception
    
        tupResult = self.fnName, bTestResult
        return tupResult
         
    #------------------------------------------- 

    def test_ParsingError(self):
        self.fnName = sys._getframe().f_code.co_name
      
        sXmlFile = 'invalidParsingError.xml'
        sXmlPath = os.path.join(self.testDataPath, sXmlFile)
   
        try:
            bTestResult = True
            with self.assertRaises(Exception):
                self.oIOXml.openXml(sXmlPath,'data')
        except:
            bTestResult = False # there should have been an exception
    
        tupResult = self.fnName, bTestResult
        return tupResult
         
    #------------------------------------------- 

    def test_InvalidNodeType(self):
        self.fnName = sys._getframe().f_code.co_name
      
        sXmlFile = 'invalidParsingError.xml'
        sXmlPath = os.path.join(self.testDataPath, sXmlFile)
   
        try:
            bTestResult = True
            with self.assertRaises(Exception):
                self.oIOXml.openXml(sXmlPath,'data')
        except:
            bTestResult = False # there should have been an exception
    
        tupResult = self.fnName, bTestResult
        return tupResult
         
    #------------------------------------------- 
    
    def test_GetPageAttributes(self):
        self.fnName = sys._getframe().f_code.co_name

        sXmlFile = 'TestSimple_PC.xml'
        sXmlPath = os.path.join(self.testDataPath, sXmlFile)
        
        # See Parsing with minidom Mouse vs Python
        # http://www.blog.pythonlibrary.org/2010/11/12/python-parsing-xml-with-minidom/
        
        [bOpenResult, xRootNode] = self.oIOXml.openXml(sXmlPath,'Session')
#         xPages =  xRootNode.getElementsByTagName('Page')[0]
#         for(name, value) in xPages.attributes.items():
#             print('name: %s ..... alue: %s' % (name, value))
            
        listImages = []
        pages = xRootNode.getElementsByTagName('Page')
        for page in pages:
            imageObj = page.getElementsByTagName("Image")[0]
            listImages.append(imageObj)
            
        for image in listImages:
            (name, value) = image.attributes.items()[0]
            print('name: %s ..... value: %s' % (name, value))
            
#             nodes = image.childNodes
#             for node in nodes:
#                 for (name, value) in node.attribute.items():
#                     print('name: %s ..... value: %s' % (name, value))

        
        
        bTestResult = True        
        tupResult = self.fnName, bTestResult
        return tupResult
        
    
##########################################################################################
#                      Launching from main (Reload and Test button)
##########################################################################################

def main(self):
    try:
        logic = TestUtilsIOXmlLogic()
        logic.runTest()
        
    except Exception as e:
        print(e)
    sys.exit(0)


if __name__ == "__main__":
    main()
