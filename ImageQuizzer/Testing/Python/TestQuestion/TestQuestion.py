import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
from Question import *
import sys
import warnings
import numpy as np
from pathlib import Path
import imp

#
# TestQuestion
#

class TestQuestion(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Test Question" # TODO make this more human readable by adding spaces
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
# TestQuestionWidget
#

class TestQuestionWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        # Instantiate and connect widgets ...
        
        # Collapsible button
        testingCollapsibleButton = ctk.ctkCollapsibleButton()
        testingCollapsibleButton.text = "Testing Layout"
        self.layout.addWidget(testingCollapsibleButton)
        
        # Layout within the collapsible button
        self.testFormLayout = qt.QFormLayout(testingCollapsibleButton)
        
        # Start test button
        startTestButton = qt.QPushButton("Start Tests Question Class")
        startTestButton.toolTip = "start unit tests for Question class."
        self.testFormLayout.addWidget(startTestButton)
        startTestButton.connect('clicked(bool)', self.onStartTestButtonClicked)
        
        # Add vertical spacer
        self.layout.addStretch(1)
        
        # Set local var as instance attribute
        self.startTestButton = startTestButton

        # reload class being tested
        #    This reloads the scripts for testing which are not handled by the 'Reload' button
        self.reloadClassForTest()
        
    def reloadClassForTest(self):
        # TODO: Fix so that you don't have to 'Reload' twice for this to take affect

        # function to force reload of scripts that are not 'loadable' in Slicer
        sModule = "Question"
        sScriptName = sModule + '.py'
        # Test files are located in .\Testing\Python\TestModule\xxx.py - i.e. up 4 levels to root
        sProjectPath = Path(__file__).parent.parent.parent.parent
        print ('**** : ' + str(sProjectPath))
        sSourceFile = str(sProjectPath) + '\\' + sScriptName
        fp = open(sSourceFile, "r")
        globals()[sModule] = imp.load_module(sModule, fp, sSourceFile, ('.py', 'r', imp.PY_SOURCE))
        fp.close()

    def onStartTestButtonClicked(self):
        oTestQuestion = TestQuestionTest()
        oTestQuestion.runTest(self.testFormLayout)
        print("Test Complete !")


class TestQuestionTest(ScriptedLoadableModuleTest):
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
        

    def DisplayTestResults(self, results):
        # print the boolean results for each test
        self.results = results
        print('--- Test Results ' + ' --------- ' + self.sClassName + ' functions -----')
        for i in range(len(results)):
            sFname, success = results[i]
            if success:
                sDisplay = "Ahh....... test passed.    : "
            else:
                sDisplay = "!$!#!@#!@$%! Test Failed!! : "
            print(sDisplay, i+1, sFname)
            
    def AddWidgetToTestFormLayout(self, grpBoxWidget):
        # display the resulting widget on the Test layout for visual test
        self.gbWidget = grpBoxWidget
        self.testFormLayout.addWidget(self.gbWidget)
        
    def runTest(self, layout):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        tupResults = []
        self.testFormLayout = layout
        tupResults.append(self.test_NoErrors_RadioButtons())
        tupResults.append(self.test_NoErrors_CheckBoxes())
        tupResults.append(self.test_NoErrors_TextQuestion())
        tupResults.append(self.test_NoOptionsWarning())
        self.DisplayTestResults(tupResults)
        

    def test_NoErrors_RadioButtons(self):
        """ Class is called with no errors encountered
        """
        self.lOptions = ['Injury','Recurrence']
        self.sGroupTitle = 'Assessment'
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name
        
        self.rq = RadioQuestion(self.lOptions, self.sGroupTitle + ' ...Test No Errors for Radio Buttons')
        bTestResult, qGrpBox = self.rq.buildQuestion()
        self.AddWidgetToTestFormLayout(qGrpBox)
        
        tupResult = self.fnName, bTestResult
        return tupResult

    def test_NoErrors_CheckBoxes(self):
        """ Class is called with no errors encountered
        """
        self.sGroupTitle = 'High Risk Factors'
        self.lOptions = ['Enlarging Opacity','Bulging Margin', 'Sequential Enlargement']
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name
        
        self.cb = CheckBoxQuestion(self.lOptions, self.sGroupTitle + ' ...Test No Errors for Check Boxes')
        bTestResult, qGrpBox = self.cb.buildQuestion()
        self.AddWidgetToTestFormLayout(qGrpBox)
        
        tupResult = self.fnName, bTestResult
        return tupResult
    
    def test_NoErrors_TextQuestion(self):
        """ Class is called with no errors encountered
        """
        self.sGroupTitle = 'Physician Notes'
        self.sNotes = ['Enter patient observations:','Describe next steps:']
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name
        
        self.textQuestion = TextQuestion(self.sNotes, self.sGroupTitle + ' ...Test No Errors for Line Edits')
        bTestResult, qGrpBox = self.textQuestion.buildQuestion()
        self.AddWidgetToTestFormLayout(qGrpBox)
        
        tupResult = self.fnName, bTestResult
        return tupResult
    
    def test_NoOptionsWarning(self):
        """ Test warning when no options are given """
        self.lOptions = []
        self.sGroupTitle = 'Assessment'
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name
        
        self.rq = RadioQuestion(self.lOptions, self.sGroupTitle + ' ...Test No Options')
        sExpWarning = 'RadioQuestion:buildQuestion:NoOptionsAvailable'
#         self.assertWarns(sExpWarning, self.rq.buildQuestion())
        with warnings.catch_warnings (record=True) as w:
            warnings.simplefilter("always")
            bFnResult, qGrpBox = self.rq.buildQuestion() 
            if bFnResult == False:
                if len(w) > 0:
                    print(str(w[0].message))
                    if sExpWarning == str(w[0].message):
                        bTestResult = True
                        self.AddWidgetToTestFormLayout(qGrpBox)
        
        tupResult = self.fnName, bTestResult
        return tupResult
