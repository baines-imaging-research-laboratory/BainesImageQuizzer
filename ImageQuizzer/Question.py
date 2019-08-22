from abc import ABC, abstractmethod

import PythonQt
import os
import unittest
import vtk, qt, ctk, slicer
import sys
import warnings

#-----------------------------------------------

class Question(ABC):
    
#     def __init__(self, color='black'):
#         self.color = color

    @abstractmethod        
    def buildQuestion(self): pass
    
#-----------------------------------------------

class RadioQuestion(Question):
    def __init__(self, options, description):
        self.options = options
        self.description = description
        self.className = type(self).__name__
        
    def buildQuestion(self):
        self.fnName = sys._getframe().f_code.co_name
        print('add radio buttons to group box')
        print(self.options)
        length = len(self.options)
        if length < 1 :
#             print('Warning : No options were given. No Group Box will be created')
            sWarningMsg = self.className + ':' + self.fnName + ':' + 'NoOptionsAvailable'
#             warnings.warn( 'For Testing:' + sWarningMsg )
            warnings.warn( sWarningMsg )
            return False
        i = 0
        while i < length:
            element1 = self.options[i]
            i = i + 1

        return True
        
#-----------------------------------------------

class RadioQuestionTest():
    """
    This is the test case for building a radio button question box
    """
    
    def setUp(self):
#         slicer.mrmlScene.Clear(0)
        print('Perform setup - clear scene')
        
    def runTest(self):
        self.setUp()
        self.test_buildRadioQuestion()
        
    def test_1(self):
        """
        Test valid entry
        """
        optList = ['Injury','Recurrence']
        desc = 'Assessment'
        rq = RadioQuestion(optList, desc)
        rq.buildQuestion()

               
#-----------------------------------------------
        
# optList = ['Injury','Recurrence']
# desc = 'Assessment'
# rq = RadioQuestion(optList, desc)
# rq.buildQuestion()

print('Finished')