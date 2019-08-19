from abc import ABC, abstractmethod

import PythonQt
import os
import unittest
import vtk, qt, ctk, slicer


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
        
    def buildQuestion(self):
        print('add radio buttons')
        print(self.options)
        length = len(self.options)
        i = 0
        while i < length:
            element1 = self.options[i]
            i = i + 1


        
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