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

        sModuleName = 'ImageQuizzer'
        oUtilsIO = UtilsIO()
        oUtilsIO.SetupModuleDirs(sModuleName)
#         # define path for test data
        self.testDataDir = os.path.join(oUtilsIO.GetTestDataBaseDir(), 'Test_UtilsIOXml')
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
        tupResults.append(self.test_GetNumChildren())
        tupResults.append(self.test_GetListOfNodeAttributes())
        tupResults.append(self.test_GetAttributes())
        tupResults.append(self.test_GetElementNodeName())
        tupResults.append(self.test_AccessChildren())
        tupResults.append(self.test_GetDataInNode())
        
        logic.sessionTestStatus.DisplayTestResults(tupResults)
 

    #------------------------------------------- 

    def test_NoErrors_OpenXml(self):
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name
         
  
        # test simple items xml file - confirm root name
        sRootName = 'rootNode'
        sXmlFile = 'UtilsIOXml_Test-items.xml'
        sXmlPath = os.path.join(self.testDataDir, sXmlFile)
  
          
        [bTestResult, xRootNode] = self.oIOXml.OpenXml(sXmlPath,'rootNode')
        if (self.oIOXml.GetElementNodeName(xRootNode) == sRootName):
            bTestResult = bTestResult * True
        else:
            bTestResult = False
            
        
        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 

    def test_NoXmlFileFound(self):
        self.fnName = sys._getframe().f_code.co_name
      
        sXmlFile = 'ThisFileDoesNotExist.xml'
        sXmlPath = os.path.join(self.testDataDir, sXmlFile)
   
        try:
            bTestResult = False

            with self.assertRaises(Exception) as context:
                self.oIOXml.OpenXml(sXmlPath,'rootNode')

            sMsg = context.exception.args[0]
            if sMsg.find('XML file does not exist')>=0:
                bTestResult = True

        except:
            bTestResult = False # there should have been an exception
    
        tupResult = self.fnName, bTestResult
        return tupResult
         
    #------------------------------------------- 

    def test_InvalidRootNode(self):
        self.fnName = sys._getframe().f_code.co_name
      
        sXmlFile = 'UtilsIOXml_Test-items.xml'
        sXmlPath = os.path.join(self.testDataDir, sXmlFile)
   
        try:
            bTestResult = False

            with self.assertRaises(NameError) as context:
                self.oIOXml.OpenXml(sXmlPath,'Session')

            sMsg = context.exception.args[0]
            if sMsg.find('Invalid XML root node')>=0:
                bTestResult = True

        except:
            bTestResult = False # there should have been an exception
    
        tupResult = self.fnName, bTestResult
        return tupResult
         
    #------------------------------------------- 
 
    def test_ParsingError(self):
        
        # this test sends in an xml file with a misnamed ending element tagname
        
        self.fnName = sys._getframe().f_code.co_name
       
        sXmlFile = 'UtilsIOXml_Test-invalidParsingError.xml'
        sXmlPath = os.path.join(self.testDataDir, sXmlFile)
    
        try:
            bTestResult = False

            with self.assertRaises(Exception) as context:
                self.oIOXml.OpenXml(sXmlPath,'rootNode')

            sMsg = context.exception.args[0]
            if sMsg.find('Parsing XML file error')>=0:
                bTestResult = True
        
        except:
            bTestResult = False # there should have been a parsing exception
     
        tupResult = self.fnName, bTestResult
        return tupResult
          
    #-------------------------------------------
    
    def test_GetElementNodeName(self):
        
        # this test sends in an 'Attribute' type of node to see if the
        # function raises the exception that it is not an 'Element' type of node
        
        self.fnName = sys._getframe().f_code.co_name
        
        sXmlFile = 'UtilsIOXml_Test-items.xml'
        sXmlPath = os.path.join(self.testDataDir, sXmlFile)
        
        bSuccess, xRootNode = self.oIOXml.OpenXml(sXmlPath,'rootNode')

        # get an attribute node to test the 'invalid element node'
        xElementNode = self.oIOXml.GetNthChild(xRootNode,'data',0)
        xAttributeNode = xElementNode.getAttributeNode('id')
 
        
        try:
            bTestResult = False

            with self.assertRaises(TypeError) as context:
                self.oIOXml.GetElementNodeName(xAttributeNode)

            sMsg = context.exception.args[0]
            if sMsg.find('Invalid XML node type: should be Element type of node')>=0:
                bTestResult = True

        except:
            bTestResult = False # there should have been an exception
    
        tupResult = self.fnName, bTestResult
        return tupResult
         
        
    #-------------------------------------------
    
    def test_GetNumChildren(self):

        # this test checks how many children belong to different element nodes in the test file
        
        self.fnName = sys._getframe().f_code.co_name
        sXmlFile = 'UtilsIOXml_Test-items.xml'
        sXmlPath = os.path.join(self.testDataDir, sXmlFile)
        
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
    
    def test_AccessChildren(self):

        # this test accessing the children of the first 'data' node
        # This tests the functions:
        #     GetChildren
        #     GetNthChild
        #     GetNumChildren
        #     GetValueOfNodeAttribute
        
        self.fnName = sys._getframe().f_code.co_name
        sXmlFile = 'UtilsIOXml_Test-items.xml'
        sXmlPath = os.path.join(self.testDataDir, sXmlFile)
        
        [bOpenResult, xRootNode] = self.oIOXml.OpenXml(sXmlPath,'rootNode')
            
        bTestResult = True
        
        xDataNode = xRootNode.getElementsByTagName('data')[0]
        
        sExpectedDescriptors = ['First Child Page1', 'Second Child Page1', 'Third Child Page1']
        dExpectedNumChildren = 3
        
        dNumChildren = self.oIOXml.GetNumChildren(xDataNode,'infoGroup')

        # ensure we have a node with the expected number of children
        if (dNumChildren == dExpectedNumChildren):
            
            # Test 1: Get All children and then loop through children to see
            #    if the 2nd child has the proper descriptor

            xAllInfoGroupNodes = self.oIOXml.GetChildren(xDataNode, 'infoGroup')
            for iNode in range( 0,dNumChildren-1 ):

                xInfoGroupChildNode = xAllInfoGroupNodes.item(iNode)
                sDescriptor = self.oIOXml.GetValueOfNodeAttribute(xInfoGroupChildNode,'descriptor')

                if sDescriptor == sExpectedDescriptors[iNode]:
                    bTestResult = bTestResult * True
                else:
                    bTestResult = bTestResult * False
            
            
            # Test 2: Access the second child directly

            # access the 2nd child (0 indexed) and check that it has the expected descriptor
            xSecondChildNode = self.oIOXml.GetNthChild(xDataNode, 'infoGroup', 1)
            
            sSecondChildDescriptor = self.oIOXml.GetValueOfNodeAttribute(xSecondChildNode,'descriptor')
            if (sSecondChildDescriptor == sExpectedDescriptors[1]) :
            
                bTestResult = bTestResult * True
            else:
                bTestResult = bTestResult * False

        else:
            # number of children accessed was not as expected
            bTestResult = bTestResult * False

        tupResult = self.fnName, bTestResult
        return tupResult

    #-------------------------------------------
    
    def test_GetListOfNodeAttributes(self):
        
        # this test gathers the attributes of an element node to confirm 
        # the attribute names (not the value of the attribute) match the expected values 
        
        self.fnName = sys._getframe().f_code.co_name
        
        sXmlFile = 'UtilsIOXml_Test-items.xml'
        sXmlPath = os.path.join(self.testDataDir, sXmlFile)
        
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

        # this test gathers the attributes of an element node to confirm 
        # the attribute values match the expected values 

        self.fnName = sys._getframe().f_code.co_name

        sXmlFile = 'UtilsIOXml_Test-items.xml'
        sXmlPath = os.path.join(self.testDataDir, sXmlFile)
        
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
        
    #-------------------------------------------
    
    def test_GetDataInNode(self):

        # this test checks the function to extract the data value from an element node

        self.fnName = sys._getframe().f_code.co_name

        sXmlFile = 'UtilsIOXml_Test-items.xml'
        sXmlPath = os.path.join(self.testDataDir, sXmlFile)
        
        [bOpenResult, xRootNode] = self.oIOXml.OpenXml(sXmlPath,'rootNode')
            
        bTestResult = True

        # from the test file, access the data in the following node ( 0 indexing)
        #    data node # 2
        #        infoGroup node # 1
        #            infoPiece node #2
        #                data = 'item2uvw'

        sExpectedData = 'item2uvw'
        
        xDataNode2 = self.oIOXml.GetNthChild(xRootNode,'data', 1)
        xInfoGroup1 = self.oIOXml.GetNthChild(xDataNode2, 'infoGroup', 0)
        xInfoPiece2 = self.oIOXml.GetNthChild(xInfoGroup1, 'infoPiece', 1)
        
        xStoredData = self.oIOXml.GetDataInNode(xInfoPiece2)
        
        if xStoredData == sExpectedData :
            bTestResult = True
        else:
            bTestResult = False



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

