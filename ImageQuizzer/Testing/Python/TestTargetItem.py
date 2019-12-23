import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from TargetItem import *
from TestingStatus import *

import os
import sys


##########################################################################
#
# TestTargetItem
#
##########################################################################

class TestTargetItem(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    #------------------------------------------- 

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Test Target Item" 
        self.parent.categories = ["Testing.ImageQuizzer"]
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

class TestTargetItemWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    #------------------------------------------- 
    def setup(self):
        self.developerMode = True
        ScriptedLoadableModuleWidget.setup(self)


##########################################################################
#
# TestTargetItem_ModuleLogic
#
##########################################################################

class TestTargetItemLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget
    """

    def __init__(self):
        ScriptedLoadableModuleLogic.__init__(self)
        self.sClassName = type(self).__name__
        print("\n************ Unittesting for class Target Item ************\n")
        self.sessionTestStatus = TestingStatus()


##########################################################################
#
# TestTargetItem_ModuleTest
#
##########################################################################

class TestTargetItemTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    #------------------------------------------- 

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear(0)
        self.sClassName = type(self).__name__

        # define path for test data
        moduleName = 'ImageQuizzer'
        scriptedModulesPath = eval('slicer.modules.%s.path' % moduleName.lower())
        scriptedModulesPath = os.path.dirname(scriptedModulesPath)
        self.testDataPath = os.path.join(scriptedModulesPath, 'Testing', 'TestData')

       
    #------------------------------------------- 

    def runTest(self ):
        """TODO: for this function to be automatically started with the 
            'Reload and Test' button in Slicer, there cannot be an extra argument here.
            I have the argument 'layout' to be able to display widgets as part of my testing. 
        """
        self.setUp()
        logic = TestTargetItemLogic()

        tupResults = []
        tupResults.append(self.test_NoErrors_LoadNrrd())
        tupResults.append(self.test_NoErrors_LoadNii())
        tupResults.append(self.test_NoErrors_LoadMhd())
        tupResults.append(self.test_NoErrors_LoadSegmentation())
        tupResults.append(self.test_Errors_NonExistentFile())
        
        
        logic.sessionTestStatus.DisplayTestResults(tupResults)
 

    #------------------------------------------- 

    def test_NoErrors_LoadNrrd(self):
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name

#     ?? IS THIS FOR URL's ? I don't need it when I send in a string
#         impath = 'D:\\Users\\cjohnson\\Work\\Resources\\ShareableData\\RegistrationDemos\\FromSlicer\\NRR-CTgLiverAblation\\CTp.nrrd'
#         strpath = urllib.request.unquote(impath)

        sTestDataSubfolder = 'Brain' 
        sInputFileName = 'ManualRegistrationExample_fixed'
        strpath = os.path.join(self.testDataPath, sTestDataSubfolder, '%s.nrrd' % sInputFileName)
        dictProperties = {}
        
        self.oTarget = DataVolume()
#        bTestResult = self.oTarget.loadTarget(strpath, dictProperties)
        oNodeVolume = self.oTarget.loadTarget(strpath, dictProperties)
        if (oNodeVolume.GetClassName() == 'vtkMRMLScalarVolumeNode') \
            & (oNodeVolume.GetName() == sInputFileName):
            bTestResult = True
        else:
            bTestResult = False
        
        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 

    def test_NoErrors_LoadNii(self):
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name

#     ?? IS THIS FOR URL's ? I don't need it when I send in a string
#         impath = 'D:\\Users\\cjohnson\\Work\\Resources\\ShareableData\\RegistrationDemos\\FromSlicer\\NRR-CTgLiverAblation\\CTp.nrrd'
#         strpath = urllib.request.unquote(impath)

        
        sTestDataSubfolder = 'Brain' 
        sInputFileName = 'ManualRegistrationExample_moving'
        strpath = os.path.join(self.testDataPath, sTestDataSubfolder, '%s.nii' %sInputFileName)
        dictProperties = {}

        self.oTarget = DataVolume()
        oNodeVolume = self.oTarget.loadTarget(strpath, dictProperties)
        if (oNodeVolume.GetClassName() == 'vtkMRMLScalarVolumeNode') \
            & (oNodeVolume.GetName() == sInputFileName):
            bTestResult = True
        else:
            bTestResult = False
       
        
        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 
    
    def test_NoErrors_LoadMhd(self):
        
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name

        sTestDataSubfolder = 'Prostate' 
        sInputFileName = 'Case00'
        strpath = os.path.join(self.testDataPath, sTestDataSubfolder, '%s.mhd' %sInputFileName)
        dictProperties = {}
        
        self.oTarget = DataVolume()
        oNodeVolume = self.oTarget.loadTarget(strpath, dictProperties)
        if (oNodeVolume.GetClassName() == 'vtkMRMLScalarVolumeNode') \
            & (oNodeVolume.GetName() == sInputFileName):
            bTestResult = True
        else:
            bTestResult = False
        
        
        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 
    
    def test_NoErrors_LoadSegmentation(self):
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name

        sTestDataSubfolder = 'Prostate' 
        sInputFileName = 'Case00_segmentation'
        strpath = os.path.join(self.testDataPath, sTestDataSubfolder, '%s.mhd' %sInputFileName)
        dictProperties = {"labelmap" : True}
        
        self.oTarget = DataVolume()
        oNodeVolume = self.oTarget.loadTarget(strpath, dictProperties)
        if (oNodeVolume.GetClassName() == 'vtkMRMLLabelMapVolumeNode') \
            & (oNodeVolume.GetName() == sInputFileName):
            bTestResult = True
        else:
            bTestResult = False
        
        
        tupResult = self.fnName, bTestResult
        return tupResult

    #------------------------------------------- 
    
    def test_Errors_NonExistentFile(self):
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name

        strpath = os.path.join(self.testDataPath, 'NonExistent.mhd')
        dictProperties = {}
        
        self.oTarget = DataVolume()
        oNodeVolume = self.oTarget.loadTarget(strpath, dictProperties)
        if ~oNodeVolume:
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
        logic = TestTargetItemLogic()
        logic.runTest()
        
    except Exception as e:
        print(e)
    sys.exit(0)


if __name__ == "__main__":
    main()
