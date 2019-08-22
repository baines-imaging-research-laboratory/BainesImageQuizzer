import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
from Question import *
import sys
import warnings
import numpy as np
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
        dummyCollapsibleButton = ctk.ctkCollapsibleButton()
        dummyCollapsibleButton.text = "A collapsible button"
        self.layout.addWidget(dummyCollapsibleButton)
        
        # Layout within the dummy collapsible button
        dummyFormLayout = qt.QFormLayout(dummyCollapsibleButton)
        
        # HelloWorld button
        startTestButton = qt.QPushButton("Start Tests Question Class")
        startTestButton.toolTip = "start unit tests for Question class."
        dummyFormLayout.addWidget(startTestButton)
        startTestButton.connect('clicked(bool)', self.onStartTestButtonClicked)
        
        # Add vertical spacer
        self.layout.addStretch(1)
        
        # Set local var as instance attribute
        self.startTestButton = startTestButton

        # reload class being tested
        self.reloadClassForTest()
        
    def reloadClassForTest(self):
        # TODO: Fix so that you don't have to 'Reload' twice for this to take affect
        #       Get project name and path from system
        #

        # function to force reload of scripts that are not 'loadable' in Slicer

        self.projectName = "ImageQuizzer"
        mod = "Question"
        self.projectPath = 'D:\\Users\\cjohnson\\Work\\Projects\\SlicerEclipseProjects\\ImageQuizzerProject\\ImageQuizzer'
        self.sourceFile = self.projectPath + '\\Question.py'
        fp = open(self.sourceFile, "r")
        globals()[mod] = imp.load_module("Question", fp, self.sourceFile, ('.py', 'r', imp.PY_SOURCE))
        fp.close()

    def onStartTestButtonClicked(self):
        tqt = TestQuestionTest()
        tqt.runTest()
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
        self.optList = ['Injury','Recurrence']
        self.desc = 'Assessment'
        self.className = type(self).__name__
        

    def DisplayResults(self, results):
        self.results = results
        print('--- Test Results ' + ' --------- ' + self.className + ' functions -----')
        for i in range(len(results)):
            sFname, success = results[i]
            if success:
                sDisplay = "Ahh....... test passed.    : "
            else:
                sDisplay = "!$!#!@#!@$%! Test Failed!! : "
            print(sDisplay, i+1, sFname)
            

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        results = []
        results.append(self.test_NoErrors())
        results.append(self.test_NoOptions())
        self.DisplayResults(results)

    def test_NoErrors(self):
        """ Class is called with no errors encountered
        """
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name
        
        self.rq = RadioQuestion(self.optList, self.desc)
        bTestResult = self.rq.buildQuestion()
#         if not(self.assertTrue(1, 2)) :
#             success = False
#         if self.returnCode:
#             success = True
        
        result = self.fnName, bTestResult
        return result
    
    def test_NoOptions(self):
        """ Test warning when no options are given """
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name
        
        self.optList = []
        self.rq = RadioQuestion(self.optList, self.desc)
        sExpWarning = 'RadioQuestion:buildQuestion:NoOptionsAvailable'
#         self.assertWarns(sExpWarning, self.rq.buildQuestion())
        with warnings.catch_warnings (record=True) as w:
            warnings.simplefilter("always")
            bFnResult = self.rq.buildQuestion() 
            if bFnResult == False:
                if len(w) > 0:
                    print(str(w[0].message))
                    if sExpWarning == str(w[0].message):
                        bTestResult = True
#             self.assertGreater( len(w), 0)
#             self.assertEqual( sExpWarning, str(w[0].message))
#             success = True
        
        result = self.fnName, bTestResult
        return result
