from abc import ABC, abstractmethod

import PythonQt
import os
import unittest
import vtk, qt, ctk, slicer
import sys
import warnings

#-----------------------------------------------

class Question(ABC):
    """ Inherits from ABC - Abstract Base Class
    """
    
    def __init__(self):
        self.sClassName = 'undefinedClassName'
        self.sFnName = 'undefinedFunctionName'

    
    @abstractmethod        
    def buildQuestion(self): pass
    
    def createGroupBox(self, sTitle):
        # create group box widget to which each subclass can add elements
        self.qGrpBox = qt.QGroupBox()
        self.qGrpBox.setTitle(sTitle)
        self.qGrpBoxLayout = qt.QVBoxLayout()
        self.qGrpBox.setLayout(self.qGrpBoxLayout)
        
        return self.qGrpBox

    def displayGroupBoxEmpty(self):
        # check if group box was already created
        
        sLabel = 'Warning : No options were given. Group Box is empty'
        sWarningMsg = self.sClassName + ':' + self.sFnName + ':' + 'NoOptionsAvailable'
        qlabel = qt.QLabel(sLabel)
        self.qGrpBoxLayout.addWidget(qlabel)
#             warnings.warn( 'For Testing:' + sWarningMsg )
        warnings.warn( sWarningMsg )

#-----------------------------------------------
# class LabelWarningBox(Question):
#     # Class to produce a box with a label
#     # Special use case: To display a warning
#     def __init__(self, sLabelText, sGrpBoxTitle):
#         self.sGrpBoxTitle = sGrpBoxTitle
#         self.sLabelText = sLabelText
#         self.sClassName = type(self).__name__
# 
#     
#     def buildQuestion(self):
#         # This is a special case where a warning msg will appear in a box
#         # with a label
#         self.sFnName = sys._getframe().f_code.co_name
#         self.createGroupBox(self.sGrpBoxTitle)
#         qlabel = qt.QLabel(self.sLabelText)
#         self.qGrpBoxLayout.addWidget(qlabel)
#         return True, self.qGrpBox

#-----------------------------------------------

class RadioQuestion(Question):
    # Create a group box and add radio buttons based on the options provided
    # Inputs : lOptions - list of labels for each radio button
    # Outputs: exitCode - boolean describing whether function exited successfully
    #          qGrpBox  - group box widget holding radio buttons
    
    def __init__(self, lOptions, sGrpBoxTitle):
        self.lOptions = lOptions
        self.sGrpBoxTitle = sGrpBoxTitle
        self.sClassName = type(self).__name__
       
    def buildQuestion(self):
        self.sFnName = sys._getframe().f_code.co_name
        self.createGroupBox(self.sGrpBoxTitle)
        
        length = len(self.lOptions)
        if length < 1 :
            self.displayGroupBoxEmpty()
            return False, self.qGrpBox
        
        i = 0
        while i < length:
            element1 = self.lOptions[i]
            qRadioBtn = qt.QRadioButton(element1)
            self.qGrpBoxLayout.addWidget(qRadioBtn)
            i = i + 1

        return True, self.qGrpBox
        
#-----------------------------------------------

class CheckBoxQuestion(Question):
    # Create a group box and add check boxes based on the options provided
    # Inputs : lOptions - list of options for each check box
    # Outputs: exitCode - boolean describing whether function exited successfully
    #          qGrpBox  - group box widget holding check boxes
    
    def __init__(self, lOptions, sGrpBoxTitle):
        self.lOptions = lOptions
        self.sGrpBoxTitle = sGrpBoxTitle
        self.sClassName = type(self).__name__
       
    def buildQuestion(self):
        self.sFnName = sys._getframe().f_code.co_name
        self.createGroupBox(self.sGrpBoxTitle)
        
        length = len(self.lOptions)
        if length < 1 :
            self.displayGroupBoxEmpty()
            return False, self.qGrpBox
        
        i = 0
        while i < length:
            element1 = self.lOptions[i]
            qChkBox = qt.QCheckBox(element1)
            self.qGrpBoxLayout.addWidget(qChkBox)
            i = i + 1

        return True, self.qGrpBox
        
#-----------------------------------------------

class TextQuestion(Question):
    # Create a group box and add radio buttons based on the options provided
    # Inputs : lOptions - list of labels for each 
    # Outputs: exitCode - boolean describing whether function exited successfully
    #          qGrpBox  - group box widget holding text edit boxes
    
    def __init__(self, lOptions, sGrpBoxTitle):
        self.lOptions = lOptions
        self.sGrpBoxTitle = sGrpBoxTitle
        self.sClassName = type(self).__name__
        
    def buildQuestion(self):
        self.sFnName = sys._getframe().f_code.co_name

        # add grid layout to group box
        self.createGroupBox(self.sGrpBoxTitle)
        newLayout = qt.QGridLayout()
        self.qGrpBoxLayout.addLayout(newLayout)
       
        length = len(self.lOptions)
        if length < 1 :
            self.displayGroupBoxEmpty()
            return False, self.qGrpBox

        i = 0
        while i < length:
            element1 = self.lOptions[i]
            qLineEdit = qt.QLineEdit()
            qLabel = qt.QLabel(element1)
            newLayout.addWidget(qLabel, i, 0)
            newLayout.addWidget(qLineEdit, i, 1)
            i = i + 1

        return True, self.qGrpBox
        
#-----------------------------------------------

class QuestionSet():
    """ Class to hold array of all questions that were built into group boxes on the form
    """
    
    def __init__(self, id, descriptor):
        self.sClassName = type(self).__name__
        self.id = id
        self.descriptor = descriptor
        self.overwritableResponsesYN = False
        
    def createForm(self):
        # create group box widget to which each subclass can add elements
        self.qQuizWidget = qt.QWidget()
        self.qQuizWidgetLayout = qt.QVBoxLayout()
        self.qQuizWidget.setLayout(self.qQuizWidgetLayout)
        self.qQuizTitle = qt.QLabel(self.descriptor)
        self.qQuizWidgetLayout.addWidget(self.qQuizTitle)
        
    def buildQuestionSetForm(self, ltupQuestionSet):
        # for each item in the list of Questions
        #    - parse the tuple into question items:
        #        0: question type (string)
        #        1: question descriptor (string)
        #        2: list of question options (list of strings)
        #    - create the appropriate group box
        #    - add to layout
        self.sFnName = sys._getframe().f_code.co_name
        bBuildSuccess = True
        self.createForm()
        self.ltupQuestionSet = ltupQuestionSet
        
        for i in range(len(self.ltupQuestionSet)):
            tupQuestionItemInfo = self.ltupQuestionSet[i]
            sQuestionType = str(tupQuestionItemInfo[0])
            sQuestionDescriptor = str(tupQuestionItemInfo[1])
            lsQuestionOptions = tupQuestionItemInfo[2]

            bQuestionTypeGood = True
            if (sQuestionType == 'Radio'):
                self.question = RadioQuestion(lsQuestionOptions, sQuestionDescriptor)
            elif (sQuestionType == 'Checkbox'):
                self.question = CheckBoxQuestion(lsQuestionOptions, sQuestionDescriptor)
            elif (sQuestionType == 'Text'):
                self.question = TextQuestion(lsQuestionOptions, sQuestionDescriptor)
            else:
                sLabel = 'Warning : Contact Administrator - Invalid question    '
                sWarningMsg = self.sClassName + ':' + self.sFnName + ':' + 'UnrecogizedQuestionType'
                qlabel = qt.QLabel(sLabel + sWarningMsg)
                qGrpBox = qt.QGroupBox()
                qGrpBoxLayout = qt.QVBoxLayout()
                qGrpBox.setLayout(qGrpBoxLayout)
                qGrpBoxLayout.addWidget(qlabel)
                warnings.warn( sWarningMsg )
                self.qQuizWidgetLayout.addWidget(qGrpBox)
                bQuestionTypeGood = False
                bBuildSuccess = False

            if bQuestionTypeGood:
                bItemSuccess, qWidget = self.question.buildQuestion()
                if bItemSuccess :
                    self.qQuizWidgetLayout.addWidget(qWidget)

            if i > 0:
                bBuildSuccess = bBuildSuccess & bItemSuccess
                
        return bBuildSuccess, self.qQuizWidget