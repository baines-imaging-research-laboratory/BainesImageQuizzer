import os, sys
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from Utilities.UtilsFilesIO import *
from Utilities.UtilsIOXml import *
from Utilities.UtilsMsgs import *
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
# TestPageState
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
# TestUtilsPageState_ModuleTest
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
        self.sTestXmlFilePath = ''
        self.oSession = Session()
        self.oPageState = PageState(self.oSession)

    #------------------------------------------- 
    def runTest(self):
        # Tests are initiated in Slicer by pressing the Reload and Test button

        self.setUp()
        logic = TestPageStateLogic()

        tupResults = []
        # tupResults.append(self.prepForTests())
        tupResults.append(self.test_InitializeStates_NoMarkupLineRequired())
        tupResults.append(self.test_InitializeStates_MinMarkupLinesRequiredOnAnyImage_3())
        tupResults.append(self.test_InitializeStates_MinMarkupLinesRequired_num())
        tupResults.append(self.test_UpdateMarkupLinesCompletionList_SpecificLinesReq_num())
        tupResults.append(self.test_UpdatePageCompletionLevelForMarkupLines_NoLinesReq())
        tupResults.append(self.test_UpdatePageCompletionLevelForMarkupLines_AnyLinesReq())
        tupResults.append(self.test_UpdatePageCompletionLevelForMarkupLines_SpecificLinesReq())
        #
        # tupResults.append(self.test_UpdateSegmentation())

        
        logic.sessionTestStatus.DisplayTestResults(tupResults)

#     #------------------------------------------- 
#     def test_ShellTemplate(self):
#         '''
#         '''
#         self.fnName = sys._getframe().f_code.co_name
#         bTestResult = False
#         
#         
#     
#         tupResult = self.fnName, bTestResult
#         return tupResult

    #------------------------------------------- 
    def test_InitializeStates_NoMarkupLineRequired(self):
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
        
        # self.oSession = Session()
        # self.oPageState = PageState(self.oSession)
        self.oPageState.InitializeStates(xPage)
        
        lExpectedl3iCompletedMarkupLines = [[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
        if self.oPageState.l3iCompletedMarkupLines == lExpectedl3iCompletedMarkupLines:
            bTestResult = True
        else:
            bTestResult = False
        
        tupResult = self.fnName, bTestResult
        return tupResult
        
    #------------------------------------------- 
    #------------------------------------------- 
        
    #------------------------------------------- 
    def test_InitializeStates_MinMarkupLinesRequiredOnAnyImage_3(self):
        ''' Test that page initialization is updated as expected.
            Case : MinMarkupLinesRequiredOnAnyImage on specific image with a number.
        '''
        self.fnName = sys._getframe().f_code.co_name

        xRoot = etree.Element("Session")
        xPage = etree.SubElement(xRoot,"Page", ID="001", Descriptor="TestData Page1", MinMarkupLinesRequiredOnAnyImage="3")
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
        
        # self.oSession = Session()
        # self.oPageState = PageState(self.oSession)
        self.oPageState.InitializeStates(xPage)
        
        
        iExpectedMinimumNumberOfLines = 3
        sExpectedMarkupLineRequiredState = 'AnyLinesReq'
        lExpectedl3iCompletedMarkupLines = [[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
        if self.oPageState.l3iCompletedMarkupLines == lExpectedl3iCompletedMarkupLines \
                and self.oPageState.sMarkupLineRequiredState == sExpectedMarkupLineRequiredState \
                and self.oPageState.iMarkupLinesOnAnyImageMinimum == iExpectedMinimumNumberOfLines:
            bTestResult = True
        else:
            bTestResult = False
        
        tupResult = self.fnName, bTestResult
        return tupResult
        
        
    #------------------------------------------- 
    def test_InitializeStates_MinMarkupLinesRequired_num(self):
        ''' Test that page initialization is updated as expected.
            Case : MinMarkupLinesRequired on specific image with a number
        '''
        self.fnName = sys._getframe().f_code.co_name

        xRoot = etree.Element("Session")
        xPage = etree.SubElement(xRoot,"Page", ID="001", Descriptor="TestData Page1")
        xImage = etree.SubElement(xPage, "Image", Descriptor="Image1_Axial", MinMarkupLinesRequired="2")
        xLayer = etree.SubElement(xImage, "Layer")
        xLayer.text = "Background"
        xImage = etree.SubElement(xPage, "Image", Descriptor="Image2_Axial", MinMarkupLinesRequired="5")
        xLayer = etree.SubElement(xImage, "Layer")
        xLayer.text = "Background"
        xImage = etree.SubElement(xPage, "Image", Descriptor="Image3_Axial")
        xLayer = etree.SubElement(xImage, "Layer")
        xLayer.text = "Background"
        xImage = etree.SubElement(xPage, "Image", Descriptor="Segmentation overlay", MinMarkupLinesRequired="5")
        xLayer = etree.SubElement(xImage, "Layer")
        xLayer.text = "Segmentation"
        
        # self.oSession = Session()
        # self.oPageState = PageState(self.oSession)
        self.oPageState.InitializeStates(xPage)
        
        
        iExpectedMinimumNumberOfLines = 0
        sExpectedMarkupLineRequiredState = 'SpecificLinesReq'
        lExpectedl3iCompletedMarkupLines = [[0,2,0],[0,5,0],[0,0,0],[0,5,0]]
        if self.oPageState.l3iCompletedMarkupLines == lExpectedl3iCompletedMarkupLines \
                and self.oPageState.sMarkupLineRequiredState == sExpectedMarkupLineRequiredState \
                and self.oPageState.iMarkupLinesOnAnyImageMinimum == iExpectedMinimumNumberOfLines:
            bTestResult = True
        else:
            bTestResult = False
        
        tupResult = self.fnName, bTestResult
        return tupResult
        
    #------------------------------------------- 
    def test_UpdateMarkupLinesCompletionList_SpecificLinesReq_num(self):
        ''' Test that the completion list is updated as expected when the
            path element is found.
            Case : MinMarkupLinesRequired on specific image with a number
        '''
        self.fnName = sys._getframe().f_code.co_name

        xRoot = etree.Element("Session")
        xPage = etree.SubElement(xRoot,"Page", ID="001", Descriptor="TestData Page1")
        xImage = etree.SubElement(xPage, "Image", Descriptor="Image1_Axial", ID="Im1", MinMarkupLinesRequired="2")
        xLayer = etree.SubElement(xImage, "Layer")
        xLayer.text = "Background"
        xPath = etree.SubElement(xImage, "MarkupLinePath")
        xPath.text = "C:/Documents/Line1-1"
        xPath = etree.SubElement(xImage, "MarkupLinePath")
        xPath.text = "C:/Documents/Line1-2"
        
        xImage = etree.SubElement(xPage, "Image", Descriptor="Image2_Axial", ID="Im2", MinMarkupLinesRequired="5")
        xLayer = etree.SubElement(xImage, "Layer")
        xLayer.text = "Background"
        xPath = etree.SubElement(xImage, "MarkupLinePath")
        xPath.text = "C:/Documents/Line2-1"

        xImage = etree.SubElement(xPage, "Image", Descriptor="Image3_Axial", ID="Im3")
        xLayer = etree.SubElement(xImage, "Layer")
        xLayer.text = "Background"
        xPath = etree.SubElement(xImage, "MarkupLinePath")
        xPath.text = "C:/Documents/Line3-1"

        xImage = etree.SubElement(xPage, "Image", Descriptor="Segmentation overlay", ID="Im3", MinMarkupLinesRequired="5")
        xLayer = etree.SubElement(xImage, "Layer")
        xLayer.text = "Segmentation"
        
        # self.oSession = Session()
        # self.oPageState = PageState(self.oSession)
        self.oPageState.InitializeStates(xPage)
        
        self.oPageState.UpdateMarkupLinesCompletionList(xPage)
        l3iExpectedList = [[0,2,2],[0,5,1],[0,0,1],[0,5,0]]
        
        if self.oPageState.l3iCompletedMarkupLines == l3iExpectedList:
            bTestResult = True
        else:
            bTestResult = False
        
        
        tupResult = self.fnName, bTestResult
        return tupResult
        
        
    #------------------------------------------- 
    def test_UpdatePageCompletionLevelForMarkupLines_NoLinesReq(self):
        ''' Test that the completion list is updated as expected when the
            path element is found.
            Case : No attribute for markup lines exist
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        
        bTestResult = False

        xRoot = self.buildXML_TestFile_Generic()
        xPage = UtilsIOXml.GetNthChild(xRoot, 'Page', 0)
        
        self.oPageState.InitializeStates(xPage)

        
        # test no markup lines required
        self.oPageState.sMarkupLineRequiredState = 'NoLinesReq'
        self.oPageState.l3iCompletedMarkupLines = [[1,2,2],[1,5,1],[1,0,1],[1,0,0]]
        self.oPageState.UpdatePageCompletionLevelForMarkupLines(xPage)
        
        bExpectedCompleted = True
        if bExpectedCompleted == self.oPageState.bMarkupLinesCompleted:
            bTestResult = True


        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 
    def test_UpdatePageCompletionLevelForMarkupLines_AnyLinesReq(self):
        ''' Test resulting page completion state for case when markup lines
            are set as required on any image.
            Cases: MinMarkupLinesRequiredOnAnyImage set a number
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        
        # test any markup lines required
        
        bTestResult = False
        bTestResult1 = False
        bTestResult2 = False
        bTestResult3 = False
        
        xRoot = self.buildXML_TestFile_Generic()
        xPage = UtilsIOXml.GetNthChild(xRoot, 'Page', 0)
        
        self.oPageState.InitializeStates(xPage)
        self.oPageState.sMarkupLineRequiredState = 'AnyLinesReq'
        self.oPageState.iMarkupLinesOnAnyImageMinimum = 2
        self.oPageState.l3iCompletedMarkupLines = [[0,0,2],[0,0,1],[0,0,1],[0,0,0]]
        self.oPageState.UpdatePageCompletionLevelForMarkupLines(xPage)
        
        bExpectedCompleted = True
        if bExpectedCompleted == self.oPageState.bMarkupLinesCompleted:
            bTestResult1 = True

        self.oPageState.InitializeStates(xPage)
        self.oPageState.sMarkupLineRequiredState = 'AnyLinesReq'
        self.oPageState.iMarkupLinesOnAnyImageMinimum = 5
        self.oPageState.l3iCompletedMarkupLines = [[0,0,2],[0,0,1],[0,0,1],[0,0,0]]
        self.oPageState.UpdatePageCompletionLevelForMarkupLines(xPage)
        
        bExpectedCompleted = False
        if bExpectedCompleted == self.oPageState.bMarkupLinesCompleted:
            bTestResult2 = True

        self.oPageState.InitializeStates(xPage)
        self.oPageState.sMarkupLineRequiredState = 'AnyLinesReq'
        self.oPageState.iMarkupLinesOnAnyImageMinimum = 1 
        self.oPageState.l3iCompletedMarkupLines = [[0,0,2],[0,0,1],[0,0,1],[0,0,0]]
        self.oPageState.UpdatePageCompletionLevelForMarkupLines(xPage)
        
        bExpectedCompleted = True
        if bExpectedCompleted == self.oPageState.bMarkupLinesCompleted:
            bTestResult3 = True

        bTestResult = bTestResult1 * bTestResult2 * bTestResult3

        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 
    def test_UpdatePageCompletionLevelForMarkupLines_SpecificLinesReq(self):
        ''' Test resulting page completion state for case when markup lines
            are set as required on specific images.
            Case: MinMarkupLinesRequired set to a number and number of MarkupLinePath elements
            either meet the required number for the image or not.
        '''
        
        self.fnName = sys._getframe().f_code.co_name
        
        # test markup lines on specific images required
        
        bTestResult = False
        bTestResult1 = False
        bTestResult2 = False
        
        xRoot = self.buildXML_TestFile_Generic()
        xPage = UtilsIOXml.GetNthChild(xRoot, 'Page', 0)
        
        self.oPageState.InitializeStates(xPage)
        self.oPageState.sMarkupLineRequiredState = 'SpecificLinesReq'
        self.oPageState.l3iCompletedMarkupLines = [[0,2,2],[0,0,1],[0,0,1],[0,0,0]]
        self.oPageState.UpdatePageCompletionLevelForMarkupLines(xPage)
        
        bExpectedCompleted = True
        if bExpectedCompleted == self.oPageState.bMarkupLinesCompleted:
            bTestResult1 = True

        self.oPageState.InitializeStates(xPage)
        self.oPageState.sMarkupLineRequiredState = 'SpecificLinesReq'
        self.oPageState.l3iCompletedMarkupLines = [[0,2,2],[0,0,1],[0,3,1],[0,0,0]]
        self.oPageState.UpdatePageCompletionLevelForMarkupLines(xPage)
        
        bExpectedCompleted = False
        if bExpectedCompleted == self.oPageState.bMarkupLinesCompleted:
            bTestResult2 = True

        bTestResult = bTestResult1 * bTestResult2

        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 
    def test_UpdateSegmentation(self):
        ''' Test updating the segmentation completion list when no
            segmentations are required
        '''
        self.fnName = sys._getframe().f_code.co_name
        bTestResult = False
        

        xRoot = etree.Element("Session")
        xPage = etree.SubElement(xRoot,"Page", ID="001", Descriptor="TestData Page1", SegmentationRequiredOnAnyImage="Y")
        
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

        
        
    
        tupResult = self.fnName, bTestResult
        return tupResult
    
    
    #------------------------------------------- 

    
    #-------------------------------------------
    #-------------------------------------------
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Helper functions
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def buildXML_TestFile_Generic(self):
        
        # create an xml file for testing
        # this is set up as a generic structure with no requirements for segementations or markup lines
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
    
        return xRoot
    #-------------------------------------------
    #-------------------------------------------
     
##########################################################################################
#                      Launching from main (Reload and Test button)
##########################################################################################

def main(self):
    try:
        logic = TestPageStateLogic()
        logic.runTest()
        
    except Exception as e:
        print(e)
    sys.exit(0)


if __name__ == "__main__":
    main()
    
