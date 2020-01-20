import os, sys
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
# from UtilsIOXml import *
from Utilities import *
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
        tupResults.append(self.test_GetNumChildren())
        tupResults.append(self.test_GetListOfNodeAttributes())
        tupResults.append(self.test_GetAttributes())
        
        logic.sessionTestStatus.DisplayTestResults(tupResults)
 

    #------------------------------------------- 

    def test_NoErrors_OpenXml(self):
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name
         
  
        # test simple items xml file - confirm root name
        sRootName = 'rootNode'
        sXmlFile = 'items.xml'
        sXmlPath = os.path.join(self.testDataPath, sXmlFile)
  
          
        [bTestResult, xRootNode] = self.oIOXml.OpenXml(sXmlPath,'rootNode')
        if (self.oIOXml.GetNodeName(xRootNode) == sRootName):
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
                self.oIOXml.OpenXml(sXmlPath,'rootNode')
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
                self.oIOXml.OpenXml(sXmlPath,'Session')
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
                self.oIOXml.OpenXml(sXmlPath,'rootNode')
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
                self.oIOXml.OpenXml(sXmlPath,'rootNode')
        except:
            bTestResult = False # there should have been an exception
    
        tupResult = self.fnName, bTestResult
        return tupResult
         
    #-------------------------------------------
    
    def test_GetNumChildren(self):
        self.fnName = sys._getframe().f_code.co_name
        sXmlFile = 'items.xml'
        sXmlPath = os.path.join(self.testDataPath, sXmlFile)
        
        [bOpenResult, xRootNode] = self.oIOXml.OpenXml(sXmlPath,'rootNode')
            
        bTestResult = True
        
        xDataNode = xRootNode.getElementsByTagName('data')[0]
        
        dExpectedNumChildren = 3
        dNumChildren = self.oIOXml.GetNumChildren(xDataNode,'infoGroup')
        if (dNumChildren == dExpectedNumChildren):
            bTestResult = bTestResult * True
        else:
            bTestResult = bTestResult * False
        
        dExpectedNumChildren = 1
        dNumChildren = self.oIOXml.GetNumChildren(xDataNode,'soloTag')
        if (dNumChildren == dExpectedNumChildren):
            bTestResult = bTestResult * True
        else:
            bTestResult = bTestResult * False


        tupResult = self.fnName, bTestResult
        return tupResult

    #-------------------------------------------
    
    def test_GetListOfNodeAttributes(self):
        self.fnName = sys._getframe().f_code.co_name
        
        sXmlFile = 'items.xml'
        sXmlPath = os.path.join(self.testDataPath, sXmlFile)
        
        [bOpenResult, xRootNode] = self.oIOXml.OpenXml(sXmlPath,'rootNode')
            
        
        import operator
        bTestResult = True

        xNode = xRootNode.getElementsByTagName('data')[1]
        listOfAttributes = self.oIOXml.GetListOfNodeAttributes(xNode)
        sExpectedNames = ['id', 'descriptor']
        sExpectedValues = ['002', 'TestData Page2' ]
        for i in range(0,len(listOfAttributes)):
            sName = list(map(operator.itemgetter(0), listOfAttributes))[i]
            sValue = list(map(operator.itemgetter(1), listOfAttributes))[i]
#             print('Node Attributes ... name: {x} .... value: {y}'.format(x=sName, y=sValue) )
            if (sName == sExpectedNames[i]):
                bTestResult = True * bTestResult
            else:
                bTestResult = False * bTestResult
            if (sValue == sExpectedValues[i]):
                bTestResult = True * bTestResult
            else:
                bTestResult = False * bTestResult
                
        
        tupResult = self.fnName, bTestResult
        return tupResult

    #-------------------------------------------
    
    def test_GetAttributes(self):
        self.fnName = sys._getframe().f_code.co_name

        sXmlFile = 'items.xml'
        sXmlPath = os.path.join(self.testDataPath, sXmlFile)
        
        [bOpenResult, xRootNode] = self.oIOXml.OpenXml(sXmlPath,'rootNode')
            
        bTestResult = True

        xNode1 = xRootNode.getElementsByTagName('data')[1]
        sValue = self.oIOXml.GetValueOfNodeAttribute(xNode1, 'descriptor')
#         print('returned sValue {x}'.format(x=sValue))
        if (sValue == 'TestData Page2'):
            bTestResult = bTestResult * True
        else:
            bTestResult = bTestResult * False
            
        xNode0 = xRootNode.getElementsByTagName('data')[0]
        xSoloNode = xNode0.getElementsByTagName('soloTag')[0]
        sValue = self.oIOXml.GetValueOfNodeAttribute(xSoloNode, 'path')
#         print('returned sValue {x}'.format(x=sValue))
        if (sValue == 'C:\Documents'):
            bTestResult = bTestResult * True
        else:
            bTestResult = bTestResult * False
            
        
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
    


#######################################################
#                TESTING
#######################################################
    
        # See Parsing with minidom Mouse vs Python
        # http://www.blog.pythonlibrary.org/2010/11/12/python-parsing-xml-with-minidom/
        
#         listChildren = []
#         dataChildren = xRootNode.getElementsByTagName('data')
#         numObjs = dataChildren.length
#         numAttributes = xRootNode.getElementsByTagName('data')[0].attributes.length
#         print('Num of children %d' % numObjs)
#         for i in range(0,numAttributes):
#             (name, value) = xRootNode.getElementsByTagName('data')[0].attributes.items()[i]
#             print('name: %s ..... value: %s' % (name, value))
# 
#         for index in range(0,numObjs):
#             dataNode = xRootNode.getElementsByTagName('data')[index]
#             infoObj = dataNode.getElementsByTagName("soloTag")
#             print(infoObj.length)
#             for childIndex in range(0, infoObj.length):
#                 (name, value) = dataNode.getElementsByTagName("infoGroup")[childIndex].attributes.items()[0]
#                 print('name: %s ..... value: %s' % (name, value))
#          
# 
# 
#         print('***************************')
#         xParentNode = xRootNode.getElementsByTagName('data')[0]
#         sChildTagName = 'soloTag'
#         self.oIOXml.GetListOfAttributes(xParentNode, sChildTagName)
# 

