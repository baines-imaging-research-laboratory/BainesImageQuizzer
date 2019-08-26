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
        
        print(self.lOptions)
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
        
        print(self.lOptions)
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
       
        print(self.lOptions)
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
        
