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
        
        # Start test button
        startTestButton = qt.QPushButton("Start Tests Question Class")
        startTestButton.toolTip = "start unit tests for Question class."
#         self.testFormLayout.addWidget(startTestButton)
        self.layout.addWidget(startTestButton)
        startTestButton.connect('clicked(bool)', self.onStartTestButtonClicked)

        # Collapsible button
        testQuestionCollapsibleButton = ctk.ctkCollapsibleButton()
        testQuestionCollapsibleButton.text = "Testing Question Layout"
        self.layout.addWidget(testQuestionCollapsibleButton)
        
        
        
        # Collapsible button
        testQuestionSetCollapsibleButton = ctk.ctkCollapsibleButton()
        testQuestionSetCollapsibleButton.text = "Testing Question Set Layout"
        self.layout.addWidget(testQuestionSetCollapsibleButton)
        
        # Layout within the collapsible buttons
        self.groupsLayout = qt.QFormLayout(testQuestionCollapsibleButton)
        self.questionSetLayout = qt.QFormLayout(testQuestionSetCollapsibleButton)

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
        oTestQuestion.runTest(self.groupsLayout, self.questionSetLayout)
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
        self.lClassNames = ['RadioQuestion', 'CheckBoxQuestion','TextQuestion', 'InvalidType']
        

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
            
    def AddWidgetToTestFormLayout(self, grpBoxWidget, testFormLayout):
        # display the resulting widget on the Test layout for visual test
        self.testFormLayout = testFormLayout
        self.gbWidget = grpBoxWidget
        self.testFormLayout.addWidget(self.gbWidget)
        
    def runTest(self, groupsLayout, questionSetLayout):
        """TODO: for this function to be automatically started with the '
            Reload and Test button in Slicer, there cannot be an extra argument here.
            I have the argument 'layout' to be able to display widgets as part of my testing. 
        """
        self.setUp()
        tupResults = []
#         self.testFormLayout = layout
        self.groupsLayout = groupsLayout
        self.questionSetLayout = questionSetLayout
        tupResults.append(self.test_NoErrors_BuildQuestionWidget())
#         tupResults.append(self.test_NoErrors_RadioButtons())
#         tupResults.append(self.test_NoErrors_CheckBoxes())
#         tupResults.append(self.test_NoErrors_TextQuestion())
        tupResults.append(self.test_NoOptionsWarning())
        tupResults.append(self.test_NoErrors_QuestionSetTest())
        tupResults.append(self.test_Error_QuestionSetTest())
        self.DisplayTestResults(tupResults)
        

    def test_NoErrors_BuildQuestionWidget(self):
        """ Test for each question type with no errors encountered
        """
        self.lOptions = ['Opt1','Opt2']
        self.sGroupTitle = 'Group Title'
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name
        
        
        self.questionType = None
        bTestResultTF = False
        i = 0
        while i < len(self.lClassNames):
            if self.lClassNames[i] == 'RadioQuestion':
                self.questionType = RadioQuestion(self.lOptions, self.sGroupTitle + '...' + self.lClassNames[i])
            elif self.lClassNames[i] == 'CheckBoxQuestion':
                self.questionType = CheckBoxQuestion(self.lOptions, self.sGroupTitle + '...' + self.lClassNames[i])
            elif self.lClassNames[i] == 'TextQuestion':
                self.questionType = TextQuestion(self.lOptions, self.sGroupTitle + '...' + self.lClassNames[i])
            else:
                print('TESTING CASE ERROR : Unknown Class ... Update list of class names for testing')
#                 self.questionType = LabelWarningBox('Invalid question type', 'WARNING- See administrator')
                self.questionType = None
                bTestResultTF = True
                
            if self.questionType != None:
                bTestResult, qWidgetBox = self.questionType.buildQuestion()
                self.AddWidgetToTestFormLayout(qWidgetBox, self.groupsLayout)
                bTestResultTF = True

            i = i + 1
            
        tupResult = self.fnName, bTestResultTF
        return tupResult
        
        
        

    def test_NoErrors_RadioButtons(self):
        """ Class is called with no errors encountered
        """
        self.lOptions = ['Injury','Recurrence']
        self.sGroupTitle = 'Assessment'
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name
        
        self.rq = RadioQuestion(self.lOptions, self.sGroupTitle + ' ...Test No Errors for Radio Buttons')
        bTestResult, qGrpBox = self.rq.buildQuestion()
        self.AddWidgetToTestFormLayout(qGrpBox, self.groupsLayout)
        
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
        self.AddWidgetToTestFormLayout(qGrpBox, self.groupsLayout)
        
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
        self.AddWidgetToTestFormLayout(qGrpBox, self.groupsLayout)
        
        tupResult = self.fnName, bTestResult
        return tupResult
    
    def test_NoOptionsWarning(self):
        """ Test warning when no options are given.
            Test for each class in the list of classes defined in constructor.
        """
        self.lOptions = []
        self.sGroupTitle = 'Test No Options'
        self.fnName = sys._getframe().f_code.co_name
        
        bTestResultTF = False
        i = 0
        while i < len(self.lClassNames):
            if self.lClassNames[i] == 'RadioQuestion':
                self.questionType = RadioQuestion(self.lOptions, self.sGroupTitle + '...' + self.lClassNames[i])
            elif self.lClassNames[i] == 'CheckBoxQuestion':
                self.questionType = CheckBoxQuestion(self.lOptions, self.sGroupTitle + '...' + self.lClassNames[i])
            elif self.lClassNames[i] == 'TextQuestion':
                self.questionType = TextQuestion(self.lOptions, self.sGroupTitle + '...' + self.lClassNames[i])
            else:
                print('TESTING ERROR : Unknown Class ... Update list of class names for testing')
                self.questionType = None 
                bTestResultTF = True

            if self.questionType != None:
                sExpWarning = self.lClassNames[i] + ':buildQuestion:NoOptionsAvailable'
                with warnings.catch_warnings (record=True) as w:
                    warnings.simplefilter("always")
                    bFnResultSuccess, qGrpBox = self.questionType.buildQuestion() 
                    if bFnResultSuccess == False:   # error was encountered - check the warning msg
                        if len(w) > 0:
                            print(str(w[0].message))
                            if sExpWarning == str(w[0].message):
                                if i > 0:   # consider previous result - test fails if any loop fails
                                    bTestResultTF = True & bTestResultTF 
                                else:
                                    bTestResultTF = True
                                self.AddWidgetToTestFormLayout(qGrpBox, self.groupsLayout)
                            else:
                                bTestResultTF = False
            i = i + 1
            
        tupResult = self.fnName, bTestResultTF
        return tupResult
            
    def test_NoErrors_QuestionSetTest(self):
        """ Test building a form given a list of questions.
        """
        self.fnName = sys._getframe().f_code.co_name
        
        bTestResultTF = True
        
        # initialize
        ltupQuestionSet = []
        sID = 'QS 1.0'
        sQuestionSetTitle = 'Test Baines Image Quizzer Title'
        self.oQuestionSet = QuestionSet(sID, sQuestionSetTitle )
        
        lsQuestionOptions = ['rbtn1', 'rbtn2', 'rbtn3']
        sQuestionType = 'Radio'
        sQuestionDescriptor = 'Title for radio button group'
        tupQuestionGroup = [sQuestionType, sQuestionDescriptor, lsQuestionOptions]
        ltupQuestionSet.append(tupQuestionGroup)
        
        lsQuestionOptions = ['box1', 'box2', 'box3']
        sQuestionType = 'Checkbox'
        sQuestionDescriptor = 'Title for checkbox group'
        tupQuestionGroup = [sQuestionType, sQuestionDescriptor, lsQuestionOptions]
        ltupQuestionSet.append(tupQuestionGroup)

        lsQuestionOptions = ['text label1', 'text label2']
        sQuestionType = 'Text'
        sQuestionDescriptor = 'Title for line edit text group'
        tupQuestionGroup = [sQuestionType, sQuestionDescriptor, lsQuestionOptions]
        ltupQuestionSet.append(tupQuestionGroup)
        

        bTestResultTF, qQuizWidget = self.oQuestionSet.buildQuestionSetForm(ltupQuestionSet)
 
        self.AddWidgetToTestFormLayout(qQuizWidget, self.questionSetLayout)
        
        tupResult = self.fnName, bTestResultTF
        return tupResult
    
    def test_Error_QuestionSetTest(self):
        """ Test building a form given a list of questions.
        """
        self.fnName = sys._getframe().f_code.co_name
        
        bBuildSetSuccess = True
        
        # initialize
        ltupQuestionSet = []
        sID = 'QS 1.0'
        sQuestionSetTitle = 'Test Baines Image Quizzer Title'
        self.oQuestionSet = QuestionSet(sID, sQuestionSetTitle )
        
        lsQuestionOptions = ['option1']
        sQuestionType = 'Invalid'
        sQuestionDescriptor = 'Title invalid group'
        tupQuestionGroup = [sQuestionType, sQuestionDescriptor, lsQuestionOptions]
        ltupQuestionSet.append(tupQuestionGroup)

        lsQuestionOptions = ['rbtn1', 'rbtn2', 'rbtn3']
        sQuestionType = 'Radio'
        sQuestionDescriptor = 'Title for radio button group'
        tupQuestionGroup = [sQuestionType, sQuestionDescriptor, lsQuestionOptions]
        ltupQuestionSet.append(tupQuestionGroup)

        bBuildSetSuccess, qQuizWidget = self.oQuestionSet.buildQuestionSetForm(ltupQuestionSet)

        if bBuildSetSuccess == False:
            bTestResultTF = True # we expected an error
        
        
        tupResult = self.fnName, bTestResultTF
        return tupResult

        