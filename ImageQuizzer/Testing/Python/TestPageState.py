import os, sys
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from UtilsIO import *
from Utilities import *
from Session import *
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

class TestPageState(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    #------------------------------------------- 

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Test PageState class" 
        self.parent.categories = ["Baines Custom Modules.Testing_ImageQuizzer"]
        self.parent.dependencies = []
        self.parent.contributors = ["Carol Johnson (Baines Imaging Research Laboratories)"] 
        self.parent.helpText = """
        This tests the functions of the PageState class.
        """
        self.parent.helpText += self.getDefaultModuleDocumentationLink()
        self.parent.acknowledgementText = """
        This file was originally developed by Carol Johnson of the Baines Imaging Research Laboratories, 
        under the supervision of Dr. Aaron Ward
        """ 

##########################################################################
#
# TestPageState_ModuleWidget
#
##########################################################################

class TestPageStateWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    #------------------------------------------- 
    def setup(self):
        self.developerMode = True
        ScriptedLoadableModuleWidget.setup(self)


##########################################################################
#
# TestPageState_ModuleLogic
#
##########################################################################

class TestPageStateLogic(ScriptedLoadableModuleLogic):
    """
    """

    def __init__(self):
        ScriptedLoadableModuleLogic.__init__(self)
        self.sClassName = type(self).__name__
        print("\n************ Unittesting for class PageState ************\n")
        self.sessionTestStatus = TestingStatus()

##########################################################################
#
# TestUtilsIOXml_ModuleTest
#
##########################################################################

class TestPageStateTest(ScriptedLoadableModuleTest):
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
        logic = TestPageStateLogic()

        tupResults = []
        tupResults.append(self.prepForTests())
        tupResults.append(self.test_InitializeStates_NoMarkupLinesRequired())
        tupResults.append(self.test_InitializeStates_MarkupLinesRequiredOnAnyImage_Y())
        tupResults.append(self.test_InitializeStates_MarkupLinesRequiredOnAnyImage_3())

        
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
            xRoot = self.buildXML_MarkupLinesfile1()
            self.oIOXml.SetRootNode(xRoot)
    
            self.oIOXml.SaveXml(self.sTestXmlFilePath)
            
        except:
            bTestResult = False

        tupResult = self.fnName, bTestResult
        return tupResult
        

    #------------------------------------------- 
    def test_InitializeStates_NoMarkupLinesRequired(self):
        ''' No attributes for markup lines exist in the page node
        '''
        self.fnName = sys._getframe().f_code.co_name

        xRoot = etree.Element("Session")
        xPage = etree.SubElement(xRoot,"Page", ID="001", Descriptor="TestData Page1")
        xImage = etree.SubElement(xPage, "Image", Descriptor="Image1_Axial")
        xLayer = etree.SubElement(xImage, "Layer")
        xLayer.text = "Background"
        xImage = etree.SubElement(xPage, "Image", Descriptor="Image1_Sagittal")
        xLayer = etree.SubElement(xImage, "Layer")
        xLayer.text = "Background"
        xImage = etree.SubElement(xPage, "Image", Descriptor="Image1_Coronal")
        xLayer = etree.SubElement(xImage, "Layer")
        xLayer.text = "Background"
        xImage = etree.SubElement(xPage, "Image", Descriptor="Segmentation overlay")
        xLayer = etree.SubElement(xImage, "Layer")
        xLayer.text = "Segmentation"
        
        self.oSession = Session()
        self.oPageState = PageState(self.oSession)
        self.oPageState.InitializeStates(xPage)
        
        lExpectedl2iCompletedMarkupLines = [[0,0],[0,0],[0,0],[-1,0]]
        if self.oPageState.l2iCompletedMarkupLines == lExpectedl2iCompletedMarkupLines:
            bTestResult = True
        else:
            bTestResult = False
        
        tupResult = self.fnName, bTestResult
        return tupResult
        
    #------------------------------------------- 
    #------------------------------------------- 
    def test_InitializeStates_MarkupLinesRequiredOnAnyImage_Y(self):
        ''' No attributes for markup lines exist in the page node
        '''
        self.fnName = sys._getframe().f_code.co_name

        xRoot = etree.Element("Session")
        xPage = etree.SubElement(xRoot,"Page", ID="001", Descriptor="TestData Page1", MarkupLinesRequiredOnAnyImage="Y")
        xImage = etree.SubElement(xPage, "Image", Descriptor="Image1_Axial")
        xLayer = etree.SubElement(xImage, "Layer")
        xLayer.text = "Background"
        xImage = etree.SubElement(xPage, "Image", Descriptor="Image1_Sagittal")
        xLayer = etree.SubElement(xImage, "Layer")
        xLayer.text = "Background"
        xImage = etree.SubElement(xPage, "Image", Descriptor="Image1_Coronal")
        xLayer = etree.SubElement(xImage, "Layer")
        xLayer.text = "Background"
        xImage = etree.SubElement(xPage, "Image", Descriptor="Segmentation overlay")
        xLayer = etree.SubElement(xImage, "Layer")
        xLayer.text = "Segmentation"
        
        self.oSession = Session()
        self.oPageState = PageState(self.oSession)
        self.oPageState.InitializeStates(xPage)
        
        
        iExpectedMinimumNumberOfLines = 1
        sExpectedMarkupLinesRequiredState = 'AnyLinesReq'
        lExpectedl2iCompletedMarkupLines = [[0,0],[0,0],[0,0],[-1,0]]
        if self.oPageState.l2iCompletedMarkupLines == lExpectedl2iCompletedMarkupLines \
                and self.oPageState.sMarkupLinesRequiredState == sExpectedMarkupLinesRequiredState \
                and self.oPageState.iMarkupLinesOnAnyImageMinimum == iExpectedMinimumNumberOfLines:
            bTestResult = True
        else:
            bTestResult = False
        
        tupResult = self.fnName, bTestResult
        return tupResult
        
    #------------------------------------------- 
    def test_InitializeStates_MarkupLinesRequiredOnAnyImage_3(self):
        ''' No attributes for markup lines exist in the page node
        '''
        self.fnName = sys._getframe().f_code.co_name

        xRoot = etree.Element("Session")
        xPage = etree.SubElement(xRoot,"Page", ID="001", Descriptor="TestData Page1", MarkupLinesRequiredOnAnyImage="3")
        xImage = etree.SubElement(xPage, "Image", Descriptor="Image1_Axial")
        xLayer = etree.SubElement(xImage, "Layer")
        xLayer.text = "Background"
        xImage = etree.SubElement(xPage, "Image", Descriptor="Image1_Sagittal")
        xLayer = etree.SubElement(xImage, "Layer")
        xLayer.text = "Background"
        xImage = etree.SubElement(xPage, "Image", Descriptor="Image1_Coronal")
        xLayer = etree.SubElement(xImage, "Layer")
        xLayer.text = "Background"
        xImage = etree.SubElement(xPage, "Image", Descriptor="Segmentation overlay")
        xLayer = etree.SubElement(xImage, "Layer")
        xLayer.text = "Segmentation"
        
        self.oSession = Session()
        self.oPageState = PageState(self.oSession)
        self.oPageState.InitializeStates(xPage)
        
        
        iExpectedMinimumNumberOfLines = 3
        sExpectedMarkupLinesRequiredState = 'AnyLinesReq'
        lExpectedl2iCompletedMarkupLines = [[0,0],[0,0],[0,0],[-1,0]]
        if self.oPageState.l2iCompletedMarkupLines == lExpectedl2iCompletedMarkupLines \
                and self.oPageState.sMarkupLinesRequiredState == sExpectedMarkupLinesRequiredState \
                and self.oPageState.iMarkupLinesOnAnyImageMinimum == iExpectedMinimumNumberOfLines:
            bTestResult = True
        else:
            bTestResult = False
        
        tupResult = self.fnName, bTestResult
        return tupResult
        
    #------------------------------------------- 
    #------------------------------------------- 
    #------------------------------------------- 
    #------------------------------------------- 

    
    #-------------------------------------------
    #-------------------------------------------
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Helper functions
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def buildXML_MarkupLinesfile1(self):
        # create an xml file for testing
        xRoot = etree.Element("Session")
        xPage = etree.SubElement(xRoot,"Page", ID="001", Descriptor="TestData Page1")

        xImage = etree.SubElement(xPage, "Image", Descriptor="Image1_Axial")

        xImage = etree.SubElement(xPage, "Image", Descriptor="Image1_Sagittal")

        xImage = etree.SubElement(xPage, "Image", Descriptor="Image1_Coronal")

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

