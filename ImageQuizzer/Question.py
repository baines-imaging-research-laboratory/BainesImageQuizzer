from abc import ABC, abstractmethod

import PythonQt
import os
import unittest
import vtk, qt, ctk, slicer
import sys
import warnings

#-----------------------------------------------

class Question(ABC):
    
    @abstractmethod        
    def buildQuestion(self): pass
    
    def createGroupBox(self, sTitle):
        # create group box widget to which each subclass can add elements
        self.qGrpBox = qt.QGroupBox()
        self.qGrpBox.setTitle(sTitle)
        self.qGrpBoxLayout = qt.QVBoxLayout()
        self.qGrpBox.setLayout(self.qGrpBoxLayout)
        return self.qGrpBox

    
#-----------------------------------------------

class RadioQuestion(Question):
    
    def __init__(self, lOptions, sGrpBoxTitle):
        self.lOptions = lOptions
        self.sGrpBoxTitle = sGrpBoxTitle
        self.sClassName = type(self).__name__
        
    def buildQuestion(self):
        self.sFnName = sys._getframe().f_code.co_name
        qGrpBox = self.createGroupBox(self.sGrpBoxTitle)
        
        print(self.lOptions)
        length = len(self.lOptions)
        if length < 1 :
            sLabel = 'Warning : No options were given. Group Box is empty'
            qlabel = qt.QLabel(sLabel)
            self.qGrpBoxLayout.addWidget(qlabel)
            sWarningMsg = self.sClassName + ':' + self.sFnName + ':' + 'NoOptionsAvailable'
#             warnings.warn( 'For Testing:' + sWarningMsg )
            warnings.warn( sWarningMsg )
            return False, qGrpBox
        i = 0
        while i < length:
            element1 = self.lOptions[i]
            qRadioBtn = qt.QRadioButton(element1)
            self.qGrpBoxLayout.addWidget(qRadioBtn)
            i = i + 1

        return True, qGrpBox
        
#-----------------------------------------------

# class RadioQuestionTest():
#     """
#     This is the test case for building a radio button question box
#     """
#     
#     def setUp(self):
# #         slicer.mrmlScene.Clear(0)
#         print('Perform setup - clear scene')
#         
#     def runTest(self):
#         self.setUp()
#         self.test_buildRadioQuestion()
#         
#     def test_1(self):
#         """
#         Test valid entry
#         """
#         optList = ['Injury','Recurrence']
#         desc = 'Assessment'
#         rq = RadioQuestion(optList, desc)
#         rq.buildQuestion()

               
#-----------------------------------------------
        
# optList = ['Injury','Recurrence']
# desc = 'Assessment'
# rq = RadioQuestion(optList, desc)
# rq.buildQuestion()

print('Finished')