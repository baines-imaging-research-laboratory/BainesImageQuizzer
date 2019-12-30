import PythonQt
import os
import vtk, qt, ctk, slicer
import sys
import unittest

import xml

#-----------------------------------------------

class Session:
    
    def __init__(self, xmlFilename, parent=None):
        self.sClassName = type(self).__name__
        self.parent = parent
        print('Constructor for Session')
        print(xmlFilename)
#     def __init__(self, parent):
#         print('Constructor for Session - parent')

  
#     def __init__(self):
#         print('Constructor for Session - no parent')

    #------------------------------------------- 
    def readPresentationInstructions(self):
        #
        # This function reads in the set of instructions defining the flow of the quiz.
        # i.e. What target to display and what question set goes with it.
        #
        print("Read in quiz flow instructions for the session")

        #
        # open xml file and load into a document
        from xml.dom import minidom
        mydoc = minidom.parse('D:\\Users\\cjohnson\\Work\\Projects\\SlicerEclipseProjects\\ImageQuizzerProject\\ImageQuizzer\\Testing\\TestData\\InputXmlFiles\\items.xml')
#        mydoc = minidom.parse('D:\\BainesWork\\Slicer\\SlicerProjectWeek2019\\ImageQuizzerProject\\ImageQuizzer\\Testing\\TestData\\InputXmlFiles\\items.xml')
        
        items = mydoc.getElementsByTagName('item')
        
        print('Item 2 attribute:')
        print(items[1].attributes['name'].value)

        # all item attributes
        print('\nAll attributes:')
        for elem in items:
            print(elem.attributes['name'].value)
        
        # one specific item's data
        print('\nItem #2 data:')
        print(items[1].firstChild.data)
        print(items[1].childNodes[0].data)
        
        # all items data
        print('\nAll item data:')
        for elem in items:
            print(elem.firstChild.data)

        
        mydoc2 = minidom.parse('D:\\Users\\cjohnson\\Work\\Projects\\SlicerEclipseProjects\\ImageQuizzerProject\\ImageQuizzer\\Testing\\TestData\\InputXmlFiles\\Test1.xml')
#         mydoc2 = minidom.parse('D:\\BainesWork\\Slicer\\SlicerProjectWeek2019\\ImageQuizzerProject\\ImageQuizzer\\Testing\\TestData\\InputXmlFiles\\Test1.xml')
        targets = mydoc2.getElementsByTagName('Target')
        print ('\n*******\nTarget attributes:')
        print(targets[1].attributes['name'].value)
        print(targets[1].attributes['descriptor'].value)
        print(targets[0].attributes['name'].value)
        print(targets[0].attributes['descriptor'].value)
        
        return True