import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
from TargetItem import *
import urllib.request # import submodule directly

import sys
import warnings
import numpy as np
from pathlib import Path
import imp



#
# TestQuestion
#

class TestTargetItem(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Test TargetItem" # TODO make this more human readable by adding spaces
        self.parent.categories = ["Testing.ImageQuizzer"]
        self.parent.dependencies = []
        self.parent.contributors = ["Carol Johnson (Baines Imaging Research Laboratory)"] 
        self.parent.helpText = """
        This is an example of scripted loadable module bundled in an extension.
        It performs a simple thresholding on the input volume and optionally captures a screenshot.
        """
        self.parent.helpText += self.getDefaultModuleDocumentationLink()
        self.parent.acknowledgementText = """
        This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
        and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
        """ # replace with organization, grant and thanks.

#
# TestTargetItemWidget
#

class TestTargetItemWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        # Instantiate and connect widgets ...
        
        
        # Start test button
        startTestButton = qt.QPushButton("Start Tests TargetItem Class")
        startTestButton.toolTip = "start unit tests for TargetItem class."
#         self.testFormLayout.addWidget(startTestButton)
        self.layout.addWidget(startTestButton)
        startTestButton.connect('clicked(bool)', self.onStartTestButtonClicked)

        # Collapsible button
        testTargetItemCollapsibleButton = ctk.ctkCollapsibleButton()
        testTargetItemCollapsibleButton.text = "Testing TargetItem Display"
        self.layout.addWidget(testTargetItemCollapsibleButton)
        
            
        # Layout within the collapsible buttons
        self.groupsLayout = qt.QFormLayout(testTargetItemCollapsibleButton)

        # Add vertical spacer
        self.layout.addStretch(1)
        
        # Set local var as instance attribute
        self.startTestButton = startTestButton

        # reload class being tested
        #    This reloads the scripts for testing which are not handled by the 'Reload' button
        self.reloadClassForTest()
        
    def reloadClassForTest(self):
        # TODO: Fix so that you don't have to 'Reload' twice for this to take effect

        # function to force reload of scripts that are not 'loadable' in Slicer
        sModule = "TargetItem"
        sScriptName = sModule + '.py'
        # Test files are located in .\Testing\Python\TestModule\xxx.py - i.e. up 4 levels to root
        sProjectPath = Path(__file__).parent.parent.parent.parent
        print ('**** : ' + str(sProjectPath))
        sSourceFile = str(sProjectPath) + '\\' + sScriptName
        fp = open(sSourceFile, "r")
        globals()[sModule] = imp.load_module(sModule, fp, sSourceFile, ('.py', 'r', imp.PY_SOURCE))
        fp.close()

    def onStartTestButtonClicked(self):
        oTestTargetItem = TestTargetItemTest()
        oTestTargetItem.runTest(self.groupsLayout)
        print("Test Complete !")


class TestTargetItemTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

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

        

    def DisplayTestResults(self, tupResults):
        # print the boolean results for each test
        self.tupResults = tupResults
        print('--- Test Results ' + ' --------- ' + self.sClassName + ' functions -----')
        for i in range(len(tupResults)):
            success = False   # assume fail
            sFname, success = tupResults[i]
            if success == True:
                sDisplay = "Ahh....... test passed.    : "
            else:
                sDisplay = "!$!*^&#!@$%! Test Failed!! : "
            print(sDisplay, i+1, sFname)
            
    def AddWidgetToTestFormLayout(self, grpBoxWidget, testFormLayout):
        # display the resulting widget on the Test layout for visual test
        self.testFormLayout = testFormLayout
        self.gbWidget = grpBoxWidget
        self.testFormLayout.addWidget(self.gbWidget)
        

    
    ##########################################################################################
    #                                TEST FLOW
    ##########################################################################################
    
    def runTest(self, groupsLayout ):
        """TODO: for this function to be automatically started with the 
            'Reload and Test' button in Slicer, there cannot be an extra argument here.
            I have the argument 'layout' to be able to display widgets as part of my testing. 
        """
        self.setUp()
        tupResults = []
#         self.testFormLayout = layout
#        slicer.mrmlScene.Clear(0)
        tupResults.append(self.test_NoErrors_LoadNrrd())
        tupResults.append(self.test_NoErrors_LoadNii())
        tupResults.append(self.test_NoErrors_LoadMhd())
        tupResults.append(self.test_NoErrors_LoadSegmentation())
        tupResults.append(self.test_Errors_NonExistentFile())

        
        self.groupsLayout = groupsLayout
        self.DisplayTestResults(tupResults)
 
    ##########################################################################################
    #                                    TESTS
    ##########################################################################################

    def test_NoErrors_LoadNrrd(self):
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name

#     ?? IS THIS FOR URL's ? I don't need it when I send in a string
#         impath = 'D:\\Users\\cjohnson\\Work\\Resources\\ShareableData\\RegistrationDemos\\FromSlicer\\NRR-CTgLiverAblation\\CTp.nrrd'
#         strpath = urllib.request.unquote(impath)

        sInputFileName = 'ManualRegistrationExample_fixed'
        strpath = os.path.join(self.testDataPath, '%s.nrrd' %sInputFileName)
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

    #-----------------------

    def test_NoErrors_LoadNii(self):
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name

#     ?? IS THIS FOR URL's ? I don't need it when I send in a string
#         impath = 'D:\\Users\\cjohnson\\Work\\Resources\\ShareableData\\RegistrationDemos\\FromSlicer\\NRR-CTgLiverAblation\\CTp.nrrd'
#         strpath = urllib.request.unquote(impath)

        
        sInputFileName = 'ManualRegistrationExample_moving'
        strpath = os.path.join(self.testDataPath, '%s.nii' %sInputFileName)
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

    #-----------------------
    
    def test_NoErrors_LoadMhd(self):
        
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name

        sInputFileName = 'Case00'
        strpath = os.path.join(self.testDataPath, '%s.mhd' %sInputFileName)
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

    #-----------------------
    
    def test_NoErrors_LoadSegmentation(self):
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name

        sInputFileName = 'Case00_segmentation'
        strpath = os.path.join(self.testDataPath, '%s.mhd' %sInputFileName)
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

    #-----------------------
    
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
