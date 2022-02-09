import os, sys
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from UtilsIO import *
from Utilities import *
from TestingStatus import *

import xml
from xml.dom import minidom

try:
    from lxml import etree

    print("running with lxml.etree")
except ImportError:
    try:
        # Python 2.5
        import xml.etree.cElementTree as etree

        print("running with cElementTree on Python 2.5+")
    except ImportError:
        try:
            # Python 2.5
            import xml.etree.ElementTree as etree

            print("running with ElementTree on Python 2.5+")
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as etree

                print("running with cElementTree")
            except ImportError:
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree

                    print("running with ElementTree")
                except ImportError:
                    print("Failed to import ElementTree from any known place")

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
        self.parent.categories = ["Baines Custom Modules.Testing_ImageQuizzer"]
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
        self.sUsername = 'Tests'
        self.oFilesIO = UtilsIO()
        self.oIOXml = UtilsIOXml()
        self.sTestXmlFilePath = ''

        # create/set environment variable to be checked in UtilsIOXml class
        #    to prevent displaying error messages during testing
        os.environ["testing"] = "1"
        self.oFilesIO.setupTestEnvironment()
        self.oIOXml.setupTestEnvironment()


       
    #------------------------------------------- 
    def runTest(self):
        # Tests are initiated in Slicer by pressing the Reload and Test button

        self.setUp()
        logic = TestUtilsIOXmlLogic()

        tupResults = []
        tupResults.append(self.prepForTests())
        # tupResults.append(self.test_WriteXML())
        tupResults.append(self.test_NoErrors_OpenXml())
        tupResults.append(self.test_NoXmlFileFound())
        tupResults.append(self.test_InvalidRootNode())
        tupResults.append(self.test_ParsingError())
        tupResults.append(self.test_GetNumChildrenByName())
        tupResults.append(self.test_GetListOfNodeAttributes())
        tupResults.append(self.test_GetAttributes())
        tupResults.append(self.test_GetElementNodeName())
        tupResults.append(self.test_GetElementNodeNameError())
        tupResults.append(self.test_AccessChildren())
        tupResults.append(self.test_GetDataInNode())
        tupResults.append(self.test_GetDataInNodeEmpty())
#         
        tupResults.append(self.test_GetLastChild())
        tupResults.append(self.test_GetLastChild_DoesNotExist())

        
        logic.sessionTestStatus.DisplayTestResults(tupResults)

        # reset to allow for non-testing logic
        #    ie. display error messages when not testing
        os.environ["testing"] = "0"
 

    #-------------------------------------------
    def prepForTests(self):
        # create an xml file for testing
        # store in TEMP directory
        # run this as the first test
        #    - if this fails, all subsequent tests dependant on the test file will fail
        
        self.fnName = sys._getframe().f_code.co_name
        sMsg = ''
        bTestResult = True

        try:
            sXmlOutputFilename = 'ImageQuizzerTestXML.xml'
            sTempPath = os.environ['TEMP']
            self.sTestXmlFilePath = os.path.join(sTempPath, sXmlOutputFilename)
            
            # build test xml
            xRoot = self.buildXMLfile()
            self.oIOXml.SetRootNode(xRoot)
    
            self.oIOXml.SaveXml(self.sTestXmlFilePath)
            
        except:
            bTestResult = False

        tupResult = self.fnName, bTestResult
        return tupResult
        

    #------------------------------------------- 
    def test_NoErrors_OpenXml(self):
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name
                
        sRootName = 'RootNode'
        [bTestResult,xRootNode ] = self.oIOXml.OpenXml(self.sTestXmlFilePath, 'RootNode')
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
        sTempPath = os.environ['TEMP']
        sXmlPath = os.path.join(sTempPath, sXmlFile)
   
        try:
            bTestResult = False

            with self.assertRaises(Exception) as context:
                self.oIOXml.OpenXml(sXmlPath,'RootNode')

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
      
        bTestResult = False

        try:

            with self.assertRaises(NameError) as context:
                self.oIOXml.OpenXml(self.sTestXmlFilePath,'InvalidRootNodeName')

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
       
        sTestString = '<RootNode><Data></Data></RootNode>'
        sXmlOutputFilename = 'ImageQuizzerTestXMLParsingError.xml'
        sTempPath = os.environ['TEMP']
        sTestBadXmlFilePath = os.path.join(sTempPath, sXmlOutputFilename)
        sTestString = '<RootNode><Data></Data><RootNode>'
    
        file1 = open(sTestBadXmlFilePath,'w')
        file1.write(sTestString)
        file1.close()
    
        try:
            bTestResult = False

            with self.assertRaises(Exception) as context:
                self.oIOXml.OpenXml(sTestBadXmlFilePath,'RootNode')

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
        bTestResult = False
        
        bSuccess, xRootNode = self.oIOXml.OpenXml(self.sTestXmlFilePath,'RootNode')

        # get child of data node and check for expected tag name
        xElementNode = self.oIOXml.GetNthChild(xRootNode,'Data',0)
        sExpectedTag = 'Data'
        
        sActualTag = self.oIOXml.GetElementNodeName(xElementNode)
        if (sExpectedTag == sActualTag):
            bTestResult = True
        
        tupResult = self.fnName, bTestResult
        return tupResult
        
        
    #-------------------------------------------
    def test_GetElementNodeNameError(self):
        
        # this test sends in an 'Attribute' type of node to see if the
        # function raises the exception that it is not an 'Element' type of node
        
        self.fnName = sys._getframe().f_code.co_name
        
        bSuccess, xRootNode = self.oIOXml.OpenXml(self.sTestXmlFilePath,'RootNode')

        # get an attribute node to test the 'invalid element node'
        xElementNode = self.oIOXml.GetNthChild(xRootNode,'Data',0)
#         xAttributeNode = xElementNode.getAttributeNode('id')
        dictAttribs = xElementNode.attrib
        xAttributeNode = dictAttribs['ID']
        
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
    def test_GetNumChildrenByName(self):

        # this test checks how many children belong to different element nodes in the test file
        
        self.fnName = sys._getframe().f_code.co_name
        
        bSuccess, xRootNode = self.oIOXml.OpenXml(self.sTestXmlFilePath,'RootNode')
            
        bTestResult = True
        
#         xDataNode = xRootNode.getElementsByTagName('data')[0]

        lDataNodes = xRootNode.findall('Data')
        xDataNode = lDataNodes[0]
        
        dExpectedNumChildren = 3
        dNumChildren = self.oIOXml.GetNumChildrenByName(xDataNode,'InfoGroup')
        if (dNumChildren == dExpectedNumChildren):
            bTestResult = bTestResult * True
        else:
            bTestResult = bTestResult * False
        
        dExpectedNumChildren = 1
        dNumChildren = self.oIOXml.GetNumChildrenByName(xDataNode,'SoloTag')
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
        #     GetNumChildrenByName
        #     GetValueOfNodeAttribute
        
        self.fnName = sys._getframe().f_code.co_name
        
        bSuccess, xRootNode = self.oIOXml.OpenXml(self.sTestXmlFilePath,'RootNode')
            
        bTestResult = True
        
        lDataNodes = xRootNode.findall('Data')
        xDataNode = lDataNodes[0]

        
        sExpectedDescriptors = ['First Child Page1', 'Second Child Page1', 'Third Child Page1']
        dExpectedNumChildren = 3
        
        dNumChildren = self.oIOXml.GetNumChildrenByName(xDataNode,'InfoGroup')

        # ensure we have a node with the expected number of children
        if (dNumChildren == dExpectedNumChildren):
            
            # Test 1: Get All children and then loop through children to see
            #    if the 2nd child has the proper descriptor

            xAllInfoGroupNodes = self.oIOXml.GetChildren(xDataNode, 'InfoGroup')
            for iNode in range( 0,dNumChildren-1 ):

#                 xInfoGroupChildNode = xAllInfoGroupNodes.item(iNode)
                xInfoGroupChildNode = xAllInfoGroupNodes[iNode]
                sDescriptor = self.oIOXml.GetValueOfNodeAttribute(xInfoGroupChildNode,'Descriptor')

                if sDescriptor == sExpectedDescriptors[iNode]:
                    bTestResult = bTestResult * True
                else:
                    bTestResult = bTestResult * False
            
            
            # Test 2: Access the second child directly

            # access the 2nd child (0 indexed) and check that it has the expected descriptor
            xSecondChildNode = self.oIOXml.GetNthChild(xDataNode, 'InfoGroup', 1)
            
            sSecondChildDescriptor = self.oIOXml.GetValueOfNodeAttribute(xSecondChildNode,'Descriptor')
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
        
        bSuccess, xRootNode = self.oIOXml.OpenXml(self.sTestXmlFilePath,'RootNode')
        
        import operator
        bTestResult = True

        lDataNodes = xRootNode.findall('Data')
        xNode = lDataNodes[1]


        listOfAttributes = self.oIOXml.GetListOfNodeAttributes(xNode)
        lsExpectedNames = ['ID', 'Descriptor']
        lsExpectedValues = ['002', 'TestData Page2' ]

        for i in range(0,len(listOfAttributes)):
            sName = list(map(operator.itemgetter(0), listOfAttributes))[i]
            sValue = list(map(operator.itemgetter(1), listOfAttributes))[i]
#             print('Node Attributes ... name: {x} .... value: {y}'.format(x=sName, y=sValue) )

            # get index of attribute in list to check for value (write to xml can change the order)
            if sName in lsExpectedNames:
                iAttribIndex = lsExpectedNames.index(sName)
                bTestResult = True * bTestResult
            else:
                bTestResult = False * bTestResult

            if sValue == lsExpectedValues[iAttribIndex]:
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

        bSuccess, xRootNode = self.oIOXml.OpenXml(self.sTestXmlFilePath,'RootNode')
            
        bTestResult = True

        lDataNodes = xRootNode.findall('Data')
        xNode1 = lDataNodes[1]
        sValue = self.oIOXml.GetValueOfNodeAttribute(xNode1, 'Descriptor')
#         print('returned sValue {x}'.format(x=sValue))

        if (sValue == 'TestData Page2'):
            bTestResult = bTestResult * True
        else:
            bTestResult = bTestResult * False
            
        xNode0 = lDataNodes[0]
        xSoloNode = xNode0.find('SoloTag')
        sValue = self.oIOXml.GetValueOfNodeAttribute(xSoloNode, 'Path')
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

        bSuccess, xRootNode = self.oIOXml.OpenXml(self.sTestXmlFilePath,'RootNode')
            
        bTestResult = True

        # from the test file, access the data in the following node ( 0 indexing)
        #    data node # 2
        #        infoGroup node # 1
        #            infoPiece node #2
        #                data = 'item2uvw'

        sExpectedData = 'item2uvw'
        
        xDataNode2 = self.oIOXml.GetNthChild(xRootNode,'Data', 1)
        xInfoGroup1 = self.oIOXml.GetNthChild(xDataNode2, 'InfoGroup', 0)
        xInfoPiece2 = self.oIOXml.GetNthChild(xInfoGroup1, 'InfoPiece', 1)
        
        xStoredData = self.oIOXml.GetDataInNode(xInfoPiece2)
        
        if xStoredData == sExpectedData :
            bTestResult = True
        else:
            bTestResult = False



        tupResult = self.fnName, bTestResult
        return tupResult
        

    #-------------------------------------------
    def test_GetDataInNodeEmpty(self):

        # this test checks the function to extract the data value 
        #    from an element node that has no data

        self.fnName = sys._getframe().f_code.co_name

        bSuccess, xRootNode = self.oIOXml.OpenXml(self.sTestXmlFilePath,'RootNode')
            
        bTestResult = True

        sExpectedData = ''
        
        xDataNode2 = self.oIOXml.GetNthChild(xRootNode,'Data', 1)

        xStoredData = self.oIOXml.GetDataInNode(xDataNode2)
        
        if xStoredData == sExpectedData :
            bTestResult = True
        else:
            bTestResult = False


        
        tupResult = self.fnName, bTestResult
        return tupResult



    #-------------------------------------------
    def test_GetLastChild(self):

        self.fnName = sys._getframe().f_code.co_name
        sMsg = ''
        bTestResult = True

        # build XML
        xRoot = etree.Element("Session")
        etree.SubElement(xRoot,"Login", LoginTime="10", LogoutTime="15")
        etree.SubElement(xRoot,"Login", LoginTime="20", LogoutTime="25")
        etree.SubElement(xRoot,"Login", LoginTime="30", LogoutTime="35")
        etree.SubElement(xRoot,"Login", LoginTime="40", LogoutTime="45")
        
        xLastChild = self.oIOXml.GetLastChild(xRoot, 'Login')
        
        if self.oIOXml.GetValueOfNodeAttribute(xLastChild, 'LogoutTime') != "45":
            bTestResult = False

        tupResult = self.fnName, bTestResult
        return tupResult

    #-------------------------------------------
    def test_GetLastChild_DoesNotExist(self):

        self.fnName = sys._getframe().f_code.co_name
        sMsg = ''
        bTestResult = True

        # build XML
        xRoot = etree.Element("Session")
        
        xLastChild = self.oIOXml.GetLastChild(xRoot, 'Login')
        
        if xLastChild != None:
            bTestResult = False

        tupResult = self.fnName, bTestResult
        return tupResult

    
    #-------------------------------------------
    #-------------------------------------------
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Helper functions
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def buildXMLfile(self):
        # create an xml file for testing
        xRoot = etree.Element("RootNode")
        xPage = etree.SubElement(xRoot,"Data", ID="001", Descriptor="TestData Page1")
        xChildNodata = etree.SubElement(xPage, "SoloTag", Path="C:\Documents")

        xChild = etree.SubElement(xPage, "InfoGroup", Descriptor="First Child Page1")
        xSubChild = etree.SubElement(xChild, "InfoPiece", Descriptor="Item1")
        xSubChild.text = 'item1abc'
        xSubChild = etree.SubElement(xChild, "InfoPiece", Descriptor="Item2")
        xSubChild.text = 'item2abc'

        xChild = etree.SubElement(xPage, "InfoGroup", Descriptor="Second Child Page1")
        xSubChild = etree.SubElement(xChild, "InfoPiece", Descriptor="Item1")
        xSubChild.text = 'item1def'
        xSubChild = etree.SubElement(xChild, "InfoPiece", Descriptor="Item2")
        xSubChild.text = 'item2def'

        xChild = etree.SubElement(xPage, "InfoGroup", Descriptor="Third Child Page1")
        xSubChild = etree.SubElement(xChild, "InfoPiece", Descriptor="Item1")
        xSubChild.text = 'item1ghi'
        xSubChild = etree.SubElement(xChild, "InfoPiece", Descriptor="Item2")
        xSubChild.text = 'item2ghi'
        
        # Page 2 data
        xPage = etree.SubElement(xRoot,"Data", ID="002", Descriptor="TestData Page2")
        
        xChild = etree.SubElement(xPage, "InfoGroup", Descriptor="First Child Page2")
        xSubChild = etree.SubElement(xChild, "InfoPiece", Descriptor="Item1")
        xSubChild.text = 'item1uvw'
        xSubChild = etree.SubElement(xChild, "InfoPiece", Descriptor="Item2")
        xSubChild.text = 'item2uvw'

        xChild = etree.SubElement(xPage, "InfoGroup", Descriptor="Second Child Page2")
        xSubChild = etree.SubElement(xChild, "InfoPiece", Descriptor="Item1")
        xSubChild.text = 'item1xyz'
        xSubChild = etree.SubElement(xChild, "InfoPiece", Descriptor="Item2")
        xSubChild.text = 'item2xyz'

        return xRoot
    #-------------------------------------------
    #-------------------------------------------
     
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

