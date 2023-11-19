import os, sys
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from Utilities.UtilsFilesIO import *
from Utilities.UtilsIOXml import *
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
# TestUtilsIOXml_ModuleWidget
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
        self.oFilesIO = UtilsFilesIO()
        self.oIOXml = self.oFilesIO.oIOXml
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
         
        tupResults.append(self.test_GetLastChild())
        tupResults.append(self.test_GetLastChild_DoesNotExist())

        tupResults.append(self.test_GetIndexOfNextChildWithAttributeValue())
        tupResults.append(self.test_AppendElement())
        tupResults.append(self.test_InsertElementBeforeIndex())
        tupResults.append(self.test_CopyElement())
        tupResults.append(self.test_GetXmlPageAndChildFromAttributeHistory())
        tupResults.append(self.test_GetXmlPageAndChildFromAttributeHistory_Randomizing())
        tupResults.append(self.test_GetFirstXmlNodeWithMatchingAttributes())
        tupResults.append(self.test_RemoveAttributeInElement())
        tupResults.append(self.test_GetMatchingXmlPagesFromAttributeHistory())
        tupResults.append(self.test_GetMatchingXmlPagesFromAttributeHistory_Randomizing())
        
        
             
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
    def test_GetIndexOfNextChildWithAttributeValue(self):
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        
        xRoot = etree.Element("Session")
        etree.SubElement(xRoot,"Page", Rep="0")
        etree.SubElement(xRoot,"Page", Rep="0")
        etree.SubElement(xRoot,"Page", Rep="0")
        etree.SubElement(xRoot,"Page", Rep="0")
        etree.SubElement(xRoot,"Page", Rep="1")
        etree.SubElement(xRoot,"Page", Rep="2")
        etree.SubElement(xRoot,"Page", Rep="0")
        etree.SubElement(xRoot,"Page", Rep="0")

        # search from index 4 for the next child with Rep="0"
        iExpectedIndex = 6
        iNextInd = self.oIOXml.GetIndexOfNextChildWithAttributeValue(xRoot, 'Page', 4, 'Rep', '0')
        
        if iNextInd == iExpectedIndex:
            bTestResult = True
        
        tupResult = self.fnName, bTestResult
        return tupResult
        
    #-------------------------------------------
    def test_AppendElement(self):
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = False
        
        xRoot = etree.Element("Session")
        etree.SubElement(xRoot,"Page", Rep="0")
        etree.SubElement(xRoot,"Page", Rep="0")
        etree.SubElement(xRoot,"Page", Rep="0")
        etree.SubElement(xRoot,"Page", Rep="0")
        etree.SubElement(xRoot,"Page", Rep="1")

        xNewElem = etree.Element("Page")
        dNewAttrib = {"Rep":"2"}
        self.oIOXml.UpdateAttributesInElement(xNewElem, dNewAttrib)

        self.oIOXml.AppendElement(xRoot, xNewElem)

        xExpectedRoot = etree.Element("Session")
        etree.SubElement(xExpectedRoot,"Page", Rep="0")
        etree.SubElement(xExpectedRoot,"Page", Rep="0")
        etree.SubElement(xExpectedRoot,"Page", Rep="0")
        etree.SubElement(xExpectedRoot,"Page", Rep="0")
        etree.SubElement(xExpectedRoot,"Page", Rep="1")
        etree.SubElement(xExpectedRoot,"Page", Rep="2")

        
        sRoot = etree.tostring(xRoot)
        sExpectedRoot = etree.tostring(xExpectedRoot)
        
        if sRoot == sExpectedRoot:
            bTestResult = True
        
        tupResult = self.fnName, bTestResult
        return tupResult

    #-------------------------------------------
    def test_InsertElementBeforeIndex(self):
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = False
        
        xRoot = etree.Element("Session")
        etree.SubElement(xRoot,"Page", Rep="0")
        etree.SubElement(xRoot,"Page", Rep="0")
        etree.SubElement(xRoot,"Page", Rep="0")
        etree.SubElement(xRoot,"Page", Rep="0")
        etree.SubElement(xRoot,"Page", Rep="1")
        etree.SubElement(xRoot,"Page", Rep="0")
        etree.SubElement(xRoot,"Page", Rep="0")
        
        xNewElem = etree.Element("Page")
        dNewAttrib = {"Rep":"2"}
        self.oIOXml.UpdateAttributesInElement(xNewElem, dNewAttrib)
        
        self.oIOXml.InsertElementBeforeIndex(xRoot, xNewElem, 5)

        xExpectedRoot = etree.Element("Session")
        etree.SubElement(xExpectedRoot,"Page", Rep="0")
        etree.SubElement(xExpectedRoot,"Page", Rep="0")
        etree.SubElement(xExpectedRoot,"Page", Rep="0")
        etree.SubElement(xExpectedRoot,"Page", Rep="0")
        etree.SubElement(xExpectedRoot,"Page", Rep="1")
        etree.SubElement(xExpectedRoot,"Page", Rep="2")
        etree.SubElement(xExpectedRoot,"Page", Rep="0")
        etree.SubElement(xExpectedRoot,"Page", Rep="0")
        
        
        sRoot = etree.tostring(xRoot)
        sExpectedRoot = etree.tostring(xExpectedRoot)
        
        if sRoot == sExpectedRoot:
            bTestResult = True
        
        tupResult = self.fnName, bTestResult
        return tupResult
    #-------------------------------------------
    def test_CopyElement(self):
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = False

        xRoot = etree.Element("Session")
        
        newRoot = self.oIOXml.CopyElement(xRoot)
        if id(xRoot) != id(newRoot):
            bTestResult = True
        
        tupResult = self.fnName, bTestResult
        return tupResult

    #-------------------------------------------
    def test_GetXmlPageAndChildFromAttributeHistory_Randomizing(self):
                
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
#         bTest1 = False
#         bTest2 = False
#         bTest3 = False
        bCaseTestResult = False


        # Randomize Page groups: [3,1,2]
        xRoot = etree.Element("Session")
        xPage0 = etree.SubElement(xRoot,"Page", {"PageGroup":"1", "ID":"Pt1"})  # RoiX-contour
        xPage1 = etree.SubElement(xRoot,"Page", {"PageGroup":"0", "ID":"Pt2"})
        xPage2 = etree.SubElement(xRoot,"Page", {"PageGroup":"1", "ID":"Pt3"})  # Display RoiX-contour
        xPage3 = etree.SubElement(xRoot,"Page", {"PageGroup":"2", "ID":"Pt4"})
        xPage4 = etree.SubElement(xRoot,"Page", {"PageGroup":"0", "ID":"Pt5"})
        xPage5 = etree.SubElement(xRoot,"Page", {"PageGroup":"2", "ID":"Pt6"})  # RoiY-contour
        xPage6 = etree.SubElement(xRoot,"Page", {"PageGroup":"3", "ID":"Pt7"})  # Display RoiY-contour
        xPage7 = etree.SubElement(xRoot,"Page", {"PageGroup":"0", "ID":"Pt8"})

        
        
        Im00 = etree.SubElement(xPage0,'Image',  {"ID":"Im00"})
        Im01 = etree.SubElement(xPage0,'Image',  {"ID":"Im01", "LabelMapID":"RoiX-contour"})
        Im10 = etree.SubElement(xPage1,'Image',  {"ID":"Im10"})
        Im11 = etree.SubElement(xPage1,'Image',  {"ID":"Im11"})
        Im12 = etree.SubElement(xPage1,'Image',  {"ID":"Im12"})
        Im21 = etree.SubElement(xPage2,'Image',  {"ID":"Im21"})
        Im22 = etree.SubElement(xPage2,'Image',  {"ID":"Im22", "DisplayLabelMapID":"RoiX-contour"})
        Im31 = etree.SubElement(xPage3,'Image',  {"ID":"Im31", "LabelMapID":"RoiY-contour"})
        Im32 = etree.SubElement(xPage3,'Image',  {"ID":"Im32"})
        Im41 = etree.SubElement(xPage4,'Image',  {"ID":"Im41"})
        Im42 = etree.SubElement(xPage4,'Image',  {"ID":"Im42"})
        Im51 = etree.SubElement(xPage5,'Image',  {"ID":"Im51"})
        Im52 = etree.SubElement(xPage5,'Image',  {"ID":"Im52"})
        Im61 = etree.SubElement(xPage6,'Image',  {"ID":"Im61", "DisplayLabelMapID":"RoiY-contour"})
        Im62 = etree.SubElement(xPage6,'Image',  {"ID":"Im62"})

        self.oIOXml.SetRootNode(xRoot)




        #>>>>>>>>>>>>>>>>> Randomization <<<<<<<<<<<<<<<<
        # Randomize Page groups: [3,1,2]
        
        ''' navInd, pgInd, qs, grp, rep,  id,       [Image,LabelMapID]
              0      1     0    0   0     Pt2,      [Im10,-] [Im11,-] [Im12,-]             
              1      4     0    0   0     Pt5,      [Im41,-] [Im42,-]
              2      7     0    0   0     Pt8       -
              3      6     0    3   0     Pt7       [Im61,DisplayLabelMapID":"RoiY-contour] [Im62,-]
              4      0     0    1   0     Pt1,      [Im00,-] [Im01,LabelMapID:RoiX-Contour]
              5      2     0    1   0     Pt3,      [Im21,-] [Im22, DisplayLabelMapID:RoiX-Contour]
              6      3     0    2   0     Pt4,      [Im31, LabelMapID:RoiY-contour] [Im32,-]
              7      5     0    2   0     Pt6,      [Im51,-] [Im52,-]
        '''
        
        l4iNavigationIndices = [ 
                        [1, 0, 0, 0], \
                        [4, 0, 0, 0], \
                        [7, 0, 0, 0], \
                        [6, 0, 3, 0], \
                        [0, 0, 1, 0], \
                        [2, 0, 1, 0], \
                        [3, 0, 2, 0], \
                        [5, 0, 2, 0] \
                       ]

        
        # Test1 - check that matching attribute is not found
        iNavIndex = 7
        xImageElement, xPageElement = self.oIOXml.GetXmlPageAndChildFromAttributeHistory(iNavIndex, l4iNavigationIndices, "Image","DisplayLabelMapID", "XXX")
        if xImageElement == None and xPageElement == None:
            bCaseTestResult = True
        else:
            bCaseTestResult = False
        bTestResult = bTestResult * bCaseTestResult
        
        
        # Test2 - check that matching attribute belongs to Pt1 and Im01
        iNavIndex = 5
        xImageElement, xPageElement = self.oIOXml.GetXmlPageAndChildFromAttributeHistory(iNavIndex, l4iNavigationIndices, "Image","LabelMapID", "RoiX-contour")
        sImID =  self.oIOXml.GetValueOfNodeAttribute(xImageElement,"ID")
        sPtID =  self.oIOXml.GetValueOfNodeAttribute(xPageElement,"ID")
        if sImID == "Im01" and sPtID == "Pt1":
            bCaseTestResult = True
        else:
            bCaseTestResult = False
        bTestResult = bTestResult * bCaseTestResult
#         print("Im ID:", sImID,  "   Pt ID:", sPtID)
        
        # Test3 - look for historical that doesn't fall on the first page to make sure the function breaks after the find
        iNavIndex = 7
        xImageElement, xPageElement = self.oIOXml.GetXmlPageAndChildFromAttributeHistory(iNavIndex, l4iNavigationIndices, "Image","LabelMapID", "RoiY-contour")
        sImID =  self.oIOXml.GetValueOfNodeAttribute(xImageElement,"ID")
        sPtID =  self.oIOXml.GetValueOfNodeAttribute(xPageElement,"ID")
        if sImID == "Im31" and sPtID == "Pt4":
            bCaseTestResult = True
        else:
            bCaseTestResult = False
        bTestResult = bTestResult * bCaseTestResult
#         print("Im ID:", sImID,  "   Pt ID:", sPtID)

        # Test4 - look for historical that isn't historical anymore because of randomization
        iNavIndex = 3
        xImageElement, xPageElement = self.oIOXml.GetXmlPageAndChildFromAttributeHistory(iNavIndex, l4iNavigationIndices, "Image","LabelMapID", "RoiY-contour")
        sImID =  self.oIOXml.GetValueOfNodeAttribute(xImageElement,"ID")
        sPtID =  self.oIOXml.GetValueOfNodeAttribute(xPageElement,"ID")
        if sImID == "" and sPtID == "":
            bCaseTestResult = True
        else:
            bCaseTestResult = False
        bTestResult = bTestResult * bCaseTestResult
#         print("Im ID:", sImID,  "   Pt ID:", sPtID)
        
               
        # print(etree.tostring(xRoot, encoding='utf8').decode('utf8'))
#         if bTest1 & bTest2 & bTest3:
#             bTestResult = True
        
        tupResult = self.fnName, bTestResult
        return tupResult

    #-------------------------------------------

    def test_GetXmlPageAndChildFromAttributeHistory(self):
                
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = False
        bTest1 = False
        bTest2 = False
        bTest3 = False

        xRoot = etree.Element("Session")
        xPage0 = etree.SubElement(xRoot,"Page", {"PageGroup":"1", "ID":"Pt1"})
        xPage1 = etree.SubElement(xRoot,"Page", {"PageGroup":"0", "ID":"Pt2"})
        xPage2 = etree.SubElement(xRoot,"Page", {"PageGroup":"1", "ID":"Pt3"})
        xPage3 = etree.SubElement(xRoot,"Page", {"PageGroup":"2", "ID":"Pt4"})
        xPage4 = etree.SubElement(xRoot,"Page", {"PageGroup":"0", "ID":"Pt5"})
        xPage5 = etree.SubElement(xRoot,"Page", {"PageGroup":"2", "ID":"Pt6"})
        xPage6 = etree.SubElement(xRoot,"Page", {"PageGroup":"3", "ID":"Pt7"})
        xPage7 = etree.SubElement(xRoot,"Page", {"PageGroup":"0", "ID":"Pt8"})

        
        
        Im00 = etree.SubElement(xPage0,'Image',  {"ID":"Im00"})
        Im01 = etree.SubElement(xPage0,'Image',  {"ID":"Im01", "LabelMapID":"RoiX-contour"})
        Im10 = etree.SubElement(xPage1,'Image',  {"ID":"Im10"})
        Im11 = etree.SubElement(xPage1,'Image',  {"ID":"Im11"})
        Im12 = etree.SubElement(xPage1,'Image',  {"ID":"Im12"})
        Im21 = etree.SubElement(xPage2,'Image',  {"ID":"Im21"})
        Im22 = etree.SubElement(xPage2,'Image',  {"ID":"Im22", "DisplayLabelMapID":"RoiX-contour"})
        Im31 = etree.SubElement(xPage3,'Image',  {"ID":"Im31", "LabelMapID":"RoiY-contour"})
        Im32 = etree.SubElement(xPage3,'Image',  {"ID":"Im32"})
        Im41 = etree.SubElement(xPage4,'Image',  {"ID":"Im41"})
        Im42 = etree.SubElement(xPage4,'Image',  {"ID":"Im42"})
        Im51 = etree.SubElement(xPage5,'Image',  {"ID":"Im51"})
        Im52 = etree.SubElement(xPage5,'Image',  {"ID":"Im52"})
        Im61 = etree.SubElement(xPage6,'Image',  {"ID":"Im61", "DisplayLabelMapID":"RoiY-contour"})
        Im62 = etree.SubElement(xPage6,'Image',  {"ID":"Im62"})

        self.oIOXml.SetRootNode(xRoot)




        #>>>>>>>>>>>>>>>>> No Randomization <<<<<<<<<<<<<<<<
        
        ''' navInd, pgInd, qs, grp, rep,  id,       [Image,LabelMapID]
              0      0     0    1   0     Pt1,      [Im00,-] [Im01,LabelMapID:RoiX-Contour]
              1      1     0    0   0     Pt2,      [Im10,-] [Im11,-] [Im12,-]             
              2      2     0    1   0     Pt3,      [Im21,-] [Im22, DisplayLabelMapID:RoiX-Contour]
              3      3     0    2   0     Pt4,      [Im31, LabelMapID:RoiY-contour] [Im32,-]
              4      4     0    0   0     Pt5,      [Im41,-] [Im42,-]
              5      5     0    2   0     Pt6,      [Im51,-] [Im52,-]
              6      6     0    3   0     Pt7       [Im61,DisplayLabelMapID":"RoiY-contour] [Im62,-]
              7      7     0    0   0     Pt8       -
        '''
        
        l4iNavigationIndices = [ 
                        [0, 0, 1, 0], \
                        [1, 0, 0, 0], \
                        [2, 0, 1, 0], \
                        [3, 0, 2, 0], \
                        [4, 0, 0, 0], \
                        [5, 0, 2, 0], \
                        [6, 0, 3, 0], \
                        [7, 0, 0, 0] \
                       ]

        
        # Test1 - check that matching attribute is not found
        iNavIndex = 7
        xImageElement, xPageElement = self.oIOXml.GetXmlPageAndChildFromAttributeHistory(iNavIndex, l4iNavigationIndices, "Image","DisplayLabelMapID", "XXX")
        if xImageElement == None and xPageElement == None:
            bTest1 = True
        
        
        # Test2 - check that matching attribute belongs to Pt1 and Im01
        iNavIndex = 7
        xImageElement, xPageElement = self.oIOXml.GetXmlPageAndChildFromAttributeHistory(iNavIndex, l4iNavigationIndices, "Image","LabelMapID", "RoiX-contour")
        sImID =  self.oIOXml.GetValueOfNodeAttribute(xImageElement,"ID")
        sPtID =  self.oIOXml.GetValueOfNodeAttribute(xPageElement,"ID")
        if sImID == "Im01" and sPtID == "Pt1":
            bTest2 = True
        # print("Im ID:", sImID,  "   Pt ID:", sPtID)
        
        # Test3 - look for historical that doesn't fall on the first page to make sure the function breaks after the find
        iNavIndex = 7
        xImageElement, xPageElement = self.oIOXml.GetXmlPageAndChildFromAttributeHistory(iNavIndex, l4iNavigationIndices, "Image","LabelMapID", "RoiY-contour")
        sImID =  self.oIOXml.GetValueOfNodeAttribute(xImageElement,"ID")
        sPtID =  self.oIOXml.GetValueOfNodeAttribute(xPageElement,"ID")
        if sImID == "Im31" and sPtID == "Pt4":
            bTest3 = True
        # print("Im ID:", sImID,  "   Pt ID:", sPtID)
        
               
        # print(etree.tostring(xRoot, encoding='utf8').decode('utf8'))
        if bTest1 & bTest2 & bTest3:
            bTestResult = True
        
        tupResult = self.fnName, bTestResult
        return tupResult

    #-------------------------------------------
    def test_GetFirstXmlNodeWithMatchingAttributes(self):
        ''' given a list of attributes, find the first page in the given list of nodes
            that match all the attributes
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        
        dictAttrib  = {"Descriptor":"MarkedPage", "ID":"Pt3"}
        
        xRoot = self.CreateXMLBaseForTests1()
        
        # add attributes to specific pages
        xPageNode0 = self.oIOXml.GetNthChild(xRoot, 'Page', 0)
        xPageNode1 = self.oIOXml.GetNthChild(xRoot, 'Page', 1)
        xPageNode2 = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode2.set("Descriptor","MarkedPage")
        xPageNode3 = self.oIOXml.GetNthChild(xRoot, 'Page', 3)
        xPageNode3.set("Descriptor","MarkedPage")
        xPageNode4 = self.oIOXml.GetNthChild(xRoot, 'Page', 4)
        xPageNode5 = self.oIOXml.GetNthChild(xRoot, 'Page', 5)

        self.oIOXml.SetRootNode(xRoot)
        
        #>>>>>>>>>>>>>>>
        # navigate without randomizing
        lxPageNodes = []
        lNavIndices = [0,1,2,3,4,5]
        for iNavInd in lNavIndices:
            lxPageNodes.append(self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', iNavInd))
            
        
        iNavidx, xPageNode = self.oIOXml.GetFirstXmlNodeWithMatchingAttributes(lxPageNodes, dictAttrib)
        
        if iNavidx == 2 and xPageNode == xPageNode2:
            bCaseTestResult = True
        else:
            bCaseTestResult = False

        bTestResult = bTestResult * bCaseTestResult

        #>>>>>>>>>>>>>>>
        # navigate with randomized data
        lxPageNodes = []
        lNavIndices = [3, 0, 1, 2, 5, 4]
        for iNavInd in lNavIndices:
            lxPageNodes.append(self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', iNavInd))
            
        iNavidx, xPageNode = self.oIOXml.GetFirstXmlNodeWithMatchingAttributes(lxPageNodes, dictAttrib)
        
        if iNavidx == 3 and xPageNode == xPageNode2:
            bCaseTestResult = True
        else:
            bCaseTestResult = False

        bTestResult = bTestResult * bCaseTestResult

        
        tupResult = self.fnName, bTestResult
        return tupResult
        
    #-------------------------------------------
    def test_RemoveAttributeInElement(self):

        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        
        
        
        # test removing an item that doesn't exist - there should be no error
        
        xRoot = self.CreateXMLBaseForTests1()
        
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("Descriptor","MarkedPage")
        xPageNode.set("BookmarkID","ReturnHere")

        self.oIOXml.SetRootNode(xRoot)
        
        
        xPageNode = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', 2)
        self.oIOXml.RemoveAttributeInElement(xPageNode,'NonExistentKey')
        dictExpectedValues = {"ID":"Pt3","Descriptor":"MarkedPage", "BookmarkID":"ReturnHere"}
        dictUpdatedValues = self.oIOXml.GetAttributes(xPageNode)
        
        if dictExpectedValues == dictUpdatedValues:
            bCaseTestResult = True
        else:
            bCaseTestResult = False

        bTestResult = bTestResult * bCaseTestResult
        
        
        # test removing an item that does exist - compare to expected
        
        xRoot = self.CreateXMLBaseForTests1()
        
        xPageNode = self.oIOXml.GetNthChild(xRoot, 'Page', 2)
        xPageNode.set("Descriptor","MarkedPage")
        xPageNode.set("BookmarkID","ReturnHere")

        self.oIOXml.SetRootNode(xRoot)

        xPageNode = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', 2)
        self.oIOXml.RemoveAttributeInElement(xPageNode,'BookmarkID')
        dictExpectedValues = {"ID":"Pt3","Descriptor":"MarkedPage"}
        dictUpdatedValues = self.oIOXml.GetAttributes(xPageNode)
        
        if dictExpectedValues == dictUpdatedValues:
            bCaseTestResult = True
        else:
            bCaseTestResult = False

        bTestResult = bTestResult * bCaseTestResult
        
    
        tupResult = self.fnName, bTestResult
        return tupResult
        
    #-------------------------------------------
    def test_GetMatchingXmlPagesFromAttributeHistory(self):
        ''' test getting the list of page nodes and their navigation indices 
            that are historical - ignoring pages beyond the current index
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        
        
        xRoot = etree.Element("Session")
        xPage0 = etree.SubElement(xRoot,"Page", {"ID":"Pt1", "PageGroup":"1", "Tag":"Label1"})
        xPage1 = etree.SubElement(xRoot,"Page", {"ID":"Pt1-Rep1", "PageGroup":"1",  "Tag":"Label1"})
        xPage2 = etree.SubElement(xRoot,"Page", {"ID":"Pt2",  "PageGroup":"2", "Tag":"Label2"})
        xPage3 = etree.SubElement(xRoot,"Page", {"ID":"Pt2-Rep2", "PageGroup":"2",  "Tag":"Label2"})
        xPage4 = etree.SubElement(xRoot,"Page", {"ID":"Pt3", "PageGroup":"3",  "Tag":"Label1"})
        xPage5 = etree.SubElement(xRoot,"Page", {"ID":"Pt4", "PageGroup":"4",  "Tag":"Label2"})
        xPage6 = etree.SubElement(xRoot,"Page", {"ID":"Pt5", "PageGroup":"5",  "Tag":"Label3"})
        xPage7 = etree.SubElement(xRoot,"Page", {"ID":"Pt6", "PageGroup":"6",  "Tag":"Label1"})
        self.oIOXml.SetRootNode(xRoot)

        # [pg, qs, pgGp, rep]
        # Pages 0,1 are part of group 1 (they have a 'Rep')
        # Pages 2,3 are part of group 2 (they have a 'Rep')
        # Pages 0, 1, 5 have 2 question sets
        
        l4iNavigationIndices = [ 
                                [0, 0, 1, 0], \
                                        [0, 1, 1, 0], \
                                [1, 0, 1, 1], \
                                        [1, 1, 1, 1], \
                                [2, 0, 2, 0], \
                                [3, 0, 2, 1], \
                                [4, 0, 3, 0], \
                                [5, 0, 4, 0], \
                                        [5, 1, 4, 0], \
                                [6, 0, 5, 0], \
                                [7, 0, 6, 0] \
                               ]
        ''' navInd, pgInd, qs, grp, rep,  id,       label
              0      0     0    1   0     Pt1,      Label1
              1      0     1    1   0     Pt1,      Label1
              2      1     0    1   1     Pt1-Rep1, Label1
              3      1     1    1   1     Pt1-Rep1, Label1
              4      2     0    2   0     Pt2,      Label2
              5      3     0    3   0     Pt2-Rep1, Label2
              6      4     0    3   0     Pt3       Label1
              7      5     0    4   0     Pt4       Label2
              8      5     1    4   0     Pt4       Label2
              9      6     0    5   0     Pt5       Label3
              10     7     0    6   0     Pt6       Label1
        '''
        xNode0 = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', 0)
        xNode1 = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', 1)
        xNode2 = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', 2)
        xNode3 = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', 3)
        xNode4 = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', 4)
        xNode5 = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', 5)
        xNode6 = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', 6)
        xNode7 = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', 7)

        #>>>>>>>>>>>>        
        # test nothing matches
        dictAttribsToMatch = {"ID":"Pt2","Tag":"Label1"}
        dictExpectedResult = {}
        dictPgNodeAndPgIndex = self.oIOXml.GetMatchingXmlPagesFromAttributeHistory(9, l4iNavigationIndices, dictAttribsToMatch)
        
        if dictExpectedResult == dictPgNodeAndPgIndex:
            bCaseTestResult = True
        else:
            bCaseTestResult = False
        bTestResult = bTestResult * bCaseTestResult


        #>>>>>>>>>>>>        
        # test match to one attribute
        dictAttribsToMatch = {"Tag":"Label1"}
        dictExpectedResult = {xNode4:4, xNode1:1, xNode0:0}
        dictPgNodeAndPgIndex = self.oIOXml.GetMatchingXmlPagesFromAttributeHistory(9, l4iNavigationIndices, dictAttribsToMatch)
        
        if dictExpectedResult == dictPgNodeAndPgIndex:
            bCaseTestResult = True
        else:
            bCaseTestResult = False
        bTestResult = bTestResult * bCaseTestResult
        

        #>>>>>>>>>>>>        
        # test match to two attributes
        dictAttribsToMatch = {"ID":"Pt2","Tag":"Label2"}
        dictExpectedResult = {xNode2:2}
        dictPgNodeAndPgIndex = self.oIOXml.GetMatchingXmlPagesFromAttributeHistory(9, l4iNavigationIndices, dictAttribsToMatch)
        
        if dictExpectedResult == dictPgNodeAndPgIndex:
            bCaseTestResult = True
        else:
            bCaseTestResult = False
        bTestResult = bTestResult * bCaseTestResult
        
        #>>>>>>>>>>>>        
        # test match to two attributes with an ignore string
        reIgnoreSubstring= '-Rep[0-9]+'  # remove -Rep with any number of digits following
        dictAttribsToMatch = {"ID":"Pt2","Tag":"Label2"}
        dictExpectedResult = {xNode3:3, xNode2:2}
        dictPgNodeAndPgIndex = self.oIOXml.GetMatchingXmlPagesFromAttributeHistory(9, l4iNavigationIndices, dictAttribsToMatch, reIgnoreSubstring)
        
        if dictExpectedResult == dictPgNodeAndPgIndex:
            bCaseTestResult = True
        else:
            bCaseTestResult = False
        bTestResult = bTestResult * bCaseTestResult
        
    
        tupResult = self.fnName, bTestResult
        return tupResult
    
    
    
    #-------------------------------------------
    def test_GetMatchingXmlPagesFromAttributeHistory_Randomizing(self):
        ''' test getting the list of page nodes and their navigation indices 
            that are historical - ignoring pages beyond the current index
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = True
        
        
        
        xRoot = etree.Element("Session")
        xPage0 = etree.SubElement(xRoot,"Page", {"ID":"Pt1", "PageGroup":"1", "Tag":"Label1"})
        xPage1 = etree.SubElement(xRoot,"Page", {"ID":"Pt1-Rep1", "PageGroup":"1",  "Tag":"Label1"})
        xPage2 = etree.SubElement(xRoot,"Page", {"ID":"Pt2",  "PageGroup":"2", "Tag":"Label2"})
        xPage3 = etree.SubElement(xRoot,"Page", {"ID":"Pt2-Rep2", "PageGroup":"2",  "Tag":"Label2"})
        xPage4 = etree.SubElement(xRoot,"Page", {"ID":"Pt3", "PageGroup":"3",  "Tag":"Label1"})
        xPage5 = etree.SubElement(xRoot,"Page", {"ID":"Pt4", "PageGroup":"4",  "Tag":"Label2"})
        xPage6 = etree.SubElement(xRoot,"Page", {"ID":"Pt5", "PageGroup":"5",  "Tag":"Label3"})
        xPage7 = etree.SubElement(xRoot,"Page", {"ID":"Pt6", "PageGroup":"6",  "Tag":"Label1"})


        self.oIOXml.SetRootNode(xRoot)


        # [pg, qs, pgGp, rep]
        # Pages 0,1 are part of group 1 (they have a 'Rep')
        # Pages 2,3 are part of group 2 (they have a 'Rep')
        # Pages 0, 1, 5 have 2 question sets
        
        # randomize Page Groups  2,4,1,6,5,3
        l4iNavigationIndices = [ 
                                [2, 0, 2, 0], \
                                [3, 0, 2, 1], \
                                [5, 0, 4, 0], \
                                        [5, 1, 4, 0], \
                                [0, 0, 1, 0], \
                                        [0, 1, 1, 0], \
                                [1, 0, 1, 1], \
                                        [1, 1, 1, 1], \
                                [7, 0, 6, 0], \
                                [6, 0, 5, 0], \
                                [4, 0, 3, 0] \
                               ]

        ''' navInd, pgInd, qs, grp, rep,  id,       label
              0      2     0    2   0     Pt2,      Label2
              1      3     0    2   0     Pt2-Rep1, Label2
              2      5     0    4   0     Pt4       Label2
              3      5     1    4   0     Pt4       Label2
              4      0     0    1   0     Pt1,      Label1
              5      0     1    1   0     Pt1,      Label1
              6      1     0    1   1     Pt1-Rep1, Label1
              7      1     1    1   1     Pt1-Rep1, Label1
              8      7     0    6   0     Pt6       Label1
              9      6     0    5   0     Pt5       Label3
             10      4     0    3   0     Pt3       Label1
        '''
        


        xNode0 = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', 0)
        xNode1 = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', 1)
        xNode2 = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', 2)
        xNode3 = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', 3)
        xNode4 = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', 4)
        xNode5 = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', 5)
        xNode6 = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', 6)
        xNode7 = self.oIOXml.GetNthChild(self.oIOXml.GetRootNode(), 'Page', 7)


        #>>>>>>>>>>>>        
        # test nothing matches
        dictAttribsToMatch = {"ID":"Pt2","Tag":"Label1"}
        dictExpectedResult = {}
        dictPgNodeAndPgIndex = self.oIOXml.GetMatchingXmlPagesFromAttributeHistory(8, l4iNavigationIndices, dictAttribsToMatch)
        
        if dictExpectedResult == dictPgNodeAndPgIndex:
            bCaseTestResult = True
        else:
            bCaseTestResult = False
        bTestResult = bTestResult * bCaseTestResult


        #>>>>>>>>>>>>        
        # test match to one attribute
        dictAttribsToMatch = {"Tag":"Label1"}
        dictExpectedResult = {xNode1:1, xNode0:0}
        dictPgNodeAndPgIndex = self.oIOXml.GetMatchingXmlPagesFromAttributeHistory(8, l4iNavigationIndices, dictAttribsToMatch)
        
        if dictExpectedResult == dictPgNodeAndPgIndex:
            bCaseTestResult = True
        else:
            bCaseTestResult = False
        bTestResult = bTestResult * bCaseTestResult

        # test match to one attribute
        dictAttribsToMatch = {"Tag":"Label2"}
        dictExpectedResult = {xNode5:5, xNode3:3, xNode2:2 }
        dictPgNodeAndPgIndex = self.oIOXml.GetMatchingXmlPagesFromAttributeHistory(8, l4iNavigationIndices, dictAttribsToMatch)
        
        if dictExpectedResult == dictPgNodeAndPgIndex:
            bCaseTestResult = True
        else:
            bCaseTestResult = False
        bTestResult = bTestResult * bCaseTestResult

    
        tupResult = self.fnName, bTestResult
        return tupResult
    
    #-------------------------------------------
    #-------------------------------------------
    #-------------------------------------------
    
    ### NOTE : FOR NEXT TEST - Watch for what root is being used.
    ###        test_GetXmlPageAndChildFromAttributeHistory did a 
    ###            self.oIOXml.SetRootNode(xRoot)
    ###        with a different tree structure from the helper function
    
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
    def CreateXMLBaseForTests1(self):
    
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

