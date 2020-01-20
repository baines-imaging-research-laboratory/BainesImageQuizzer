import PythonQt
import os
import vtk, qt, ctk, slicer
import sys
import unittest
from UtilsIOXml import *
from Question import *
from Image import *

import xml
from xml.dom import minidom
import ssl

#-----------------------------------------------

class Page:
    
    def __init__(self,  parent=None):
        self.sClassName = type(self).__name__
        self.parent = parent
        print('Constructor for Page')
        self.name = ''
        self.descriptor = ''
        self.iQuestionSetIndex = 0
        self.iNumQuestionSets = 0
        
        # Next button
        self.btnNextQuestionSet = qt.QPushButton("Next Question Set - same images")
        self.btnNextQuestionSet.toolTip = "Display next question set."
        self.btnNextQuestionSet.enabled = False
        self.btnNextQuestionSet.connect('clicked(bool)', self.onNextQuestionSetClicked)

        # Back button
        self.btnPreviousQuestionSet = qt.QPushButton("Back")
        self.btnPreviousQuestionSet.toolTip = "Display previous question set."
        self.btnPreviousQuestionSet.enabled = False
        self.btnPreviousQuestionSet.connect('clicked(bool)', self.onPreviousQuestionSetClicked)

        # Save button
        self.btnSaveQuestionSet = qt.QPushButton("Save")
        self.btnSaveQuestionSet.toolTip = "Save Question Set responses."
        self.btnSaveQuestionSet.enabled = False
        self.btnSaveQuestionSet.connect('clicked(bool)', self.onSaveQuestionSetClicked)
        

    #-----------------------------------------------

    def RunSetup(self, xPageNode, quizLayout):

        self.quizLayout = quizLayout
        self.oIOXml = UtilsIOXml()


        # get name and descriptor
        sName = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'name')
        sDescriptor = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'descriptor')
        print(sName, '    ' , sDescriptor)

        self.quizLayout.addWidget(self.btnNextQuestionSet)
        self.quizLayout.addWidget(self.btnPreviousQuestionSet)
        self.quizLayout.addWidget(self.btnSaveQuestionSet)

        # for each 'outstanding' page (questions not yet answered)

        # display Images
        self.xImages = self.oIOXml.GetChildren(xPageNode, 'Image')
        self.iNumImages = self.oIOXml.GetNumChildren(xPageNode, 'Image')
        print('**** NUMBER OF IMAGES %s' % self.iNumImages) 
        
        self.BuildViewNodes(self.xImages)
#         if len(self.xImages) > 1:
#             # clear images
#             self.AssignViewToNone('Red')
#             self.AssignViewToNone('Yellow')
#             self.AssignViewToNone('Green')
#             self.AssignImageToViewWindow('Case00', 'Red','Volume','Axial') 
#             self.AssignImageToViewWindow('Case00_segmentation', 'Red','Labelmap','Axial')
#             self.AssignImageToViewWindow('ManualRegistrationExample_moving_1', 'Yellow','Volume','Sagittal') 
#             self.AssignImageToViewWindow('ManualRegistrationExample_fixed_1', 'Green','Volume','Sagittal')


        # get Question Set nodes and number of sets
        self.xQuestionSets = self.oIOXml.GetChildren(xPageNode, 'QuestionSet')
        self.iNumQuestionSets = self.oIOXml.GetNumChildren(xPageNode, 'QuestionSet')

        
        self.DisplayQuestionSet(self.xQuestionSets[self.iQuestionSetIndex])

        # enable buttons
        self.EnableQuestionSetButtons()
        
            
        
    #-----------------------------------------------

    def BuildViewNodes(self, xImages):
        
        oIOXml = UtilsIOXml()
        oQuizzerMsg = QuizzerMessages()
        
        ltupViewNodes = []

        # for each image
        for i in range(len(xImages)):

            dictProperties = {}

            # Extract image attributes
            sImageType = oIOXml.GetValueOfNodeAttribute(xImages[i], 'type')
            sImageDestination = oIOXml.GetValueOfNodeAttribute(xImages[i], 'destination')
            sOrientation = oIOXml.GetValueOfNodeAttribute(xImages[i], 'orientation')
            
            # Extract path element
            xPathNodes = oIOXml.GetChildren(xImages[i], 'Path')

            if len(xPathNodes) > 1:
                sWarningMsg = 'There can only be one path per image - using first defined path'
                oQuizzerMsg.DisplayWarning( sWarningMsg )

            sImagePath = oIOXml.GetDataInNode(xPathNodes[0])
            
            xLayerNodes = oIOXml.GetChildren(xImages[i], 'Layer')
            if len(xLayerNodes) > 1:
                sWarningMsg = 'There can only be one layer per image - using first defined layer'
                oQuizzerMsg.DisplayWarning(sWarningMsg)

            sViewLayer = oIOXml.GetDataInNode(xLayerNodes[0])
            
            
#             print('    *** type: %s' % sImageType)
#             print('    *** format: %s' % sImageFormat)
#             print('    *** destination: %s' % sImageDestination)
#             print('    *** path: %s' % sImagePath)
#             sImagePath = oIOXml.GetValueOfNodeAttribute(xImages[i], 'path')
#             sImageFormat = oIOXml.GetValueOfNodeAttribute(xImages[i], 'format')
            
            

            if (sImageType == 'Volume'):
                
#                     slNode = slicer.util.loadVolume(sImagePath, {'show':False})
                    slNode = slicer.util.loadVolume(sImagePath)
#                     print(' NODE NAME %s:' %slNode.GetName())
            
            else:
                if (sImageType == 'Labelmap'):
#                     dictProperties = {'labelmap' : True, 'show':False}
                    dictProperties = {'labelmap' : True}
                    
                    slNode = slicer.util.loadLabelVolume(sImagePath, dictProperties)
                    
                    
                else:
                    msgBox = qt.QMessageBox()
                    msgBox.critical(0,"ERROR","Undefined image type")


            tupViewNode = [slNode, sImageDestination, sOrientation, sViewLayer]
            ltupViewNodes.append(tupViewNode)
    
        return ltupViewNodes
                    
                    
#             if not (sImageDestination == ''):
#                 # get name of last scalar volume node loaded
#                 iIndexLastNode = slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLScalarVolumeNode') - 1
#                  
#                 slNode = slicer.mrmlScene.GetNthNodeByClass(iIndexLastNode, 'vtkMRMLScalarVolumeNode')
#                 sSlicerNodeName = slNode.GetName()
#                  
#                 self.AssignImageToViewWindow(sSlicerNodeName, sImageDestination)    
            

#             if not (sImageDestination == ''):
#                 if not (slNode.GetClassName() == 'vtkMRMLLabelMapVolumeNode'):
# 
#                     self.AssignImageToViewWindow(slNode.GetName(), sImageDestination)    

                
#         for i in range(len(xImages)):
# 
#             dictProperties = {}
# 
#             # Extract image attributes
#             sImageType = oIOXml.GetValueOfNodeAttribute(xImages[i], 'type')
#             sImageFormat = oIOXml.GetValueOfNodeAttribute(xImages[i], 'format')
#             sImageDestination = oIOXml.GetValueOfNodeAttribute(xImages[i], 'destination')
#             sImagePath = oIOXml.GetValueOfNodeAttribute(xImages[i], 'path')
#             if (sImageType == 'Volume'):
#                 if not (sImageDestination == ''):
#                     self.AssignImageToViewWindow(slNode.GetName(), sImageDestination)    
#          
         
         
    #-----------------------------------------------
    #         Manage Views
    #-----------------------------------------------
 
    def AssignImageToViewWindow(self, sSlicerNodeName, sImageDestination, sNodeType, sOrientation):
        print('         - Node name   : %s' % sSlicerNodeName)
        print('         - Destination : %s' % sImageDestination)
 
        slWidget = slicer.app.layoutManager().sliceWidget(sImageDestination)
        slWindowLogic = slWidget.sliceLogic()
        slWindowCompositeNode = slWindowLogic.GetSliceCompositeNode()
        if sNodeType == 'ScalarVolume':
            slWindowCompositeNode.SetBackgroundVolumeID(slicer.util.getNode(sSlicerNodeName).GetID())
            slWidget.setSliceOrientation(sOrientation)
        else:
            if sNodeType == 'Labelmap':
                slWindowCompositeNode.SetLabelVolumeID(slicer.util.getNode(sSlicerNodeName).GetID())
        
         

    #-----------------------------------------------
    
    def AssignViewToNone(self, sScreenColor):
        
        slWidget = slicer.app.layoutManager().sliceWidget(sScreenColor)
        slLogic = slWidget.sliceLogic()
        slCompNode = slLogic.GetSliceCompositeNode()
        slCompNode.SetBackgroundVolumeID('None')
        
    #-----------------------------------------------
    #         Manage Questions
    #-----------------------------------------------

    def DisplayQuestionSet(self, xNodeQuestionSet):    
        # given a question set node, extract the information from the xml document
        # and add the widget to the layout
        
        # first clear any previous widgets (except push buttons)
            for i in reversed(range(self.quizLayout.count())):
                x = self.quizLayout.itemAt(i).widget()
                if not(isinstance(x, qt.QPushButton)):
                    self.quizLayout.itemAt(i).widget().setParent(None)

            oQuestionSet = QuestionSet()
            ltupQuestionSet = oQuestionSet.ExtractQuestionsFromXML(xNodeQuestionSet)
            bTestResultTF, qQuizWidget = oQuestionSet.BuildQuestionSetForm(ltupQuestionSet)
            self.quizLayout.addWidget(qQuizWidget)
        
    #-----------------------------------------------
    #         Manage Buttons
    #-----------------------------------------------

    def EnableQuestionSetButtons(self):
        # using the question set index display/enable the relevant buttons
        
        print('---Question Set Number %s' % self.iQuestionSetIndex)
        # Case : only one Question set
        if (self.iQuestionSetIndex == 0 and self.iNumQuestionSets == 1):
            self.btnNextQuestionSet.enabled = False
            self.btnPreviousQuestionSet.enabled = False
            self.btnSaveQuestionSet.enabled = True
        else:
            # Case : first Question Set and more to follow
            if (self.iQuestionSetIndex == 0 and self.iNumQuestionSets > 1):
                self.btnNextQuestionSet.enabled = True
                self.btnPreviousQuestionSet.enabled = False
                self.btnSaveQuestionSet.enabled = False
            else:
                # Case : last Question Set with a number of previous sets
                if (self.iQuestionSetIndex == self.iNumQuestionSets - 1 and self.iNumQuestionSets > 1):
                    self.btnNextQuestionSet.enabled = False
                    self.btnPreviousQuestionSet.enabled = True
                    self.btnSaveQuestionSet.enabled = True
                else:
                    # Case : middle of number of question sets
                    if (self.iQuestionSetIndex > 0 and self.iQuestionSetIndex < self.iNumQuestionSets):
                        self.btnNextQuestionSet.enabled = True
                        self.btnPreviousQuestionSet.enabled = True
                        self.btnSaveQuestionSet.enabled = False
                        
        
        
         

    #-----------------------------------------------

    def onNextQuestionSetClicked(self):

        # enable buttons dependent on case

        # increase the question set index
        self.iQuestionSetIndex = self.iQuestionSetIndex + 1
        

#         # display next set of questions
#         if (self.iQuestionSetIndex < self.iNumQuestionSets):
#             self.btnPreviousQuestionSet.enabled = True
#             self.DisplayQuestionSet(self.xQuestionSets[self.iQuestionSetIndex])
#             self.EnableQuestionSetButtons()
#         else:
#             self.btnNextQuestionSet.enabled = False

        self.EnableQuestionSetButtons()
        if (self.iQuestionSetIndex < self.iNumQuestionSets):
            self.DisplayQuestionSet(self.xQuestionSets[self.iQuestionSetIndex])
        
    #-----------------------------------------------

    def onPreviousQuestionSetClicked(self):

        # enable buttons dependent on case

        # decrease the question set index
        self.iQuestionSetIndex = self.iQuestionSetIndex - 1

#         # display previous set of questions
#         if (self.iQuestionSetIndex >= 0):
#             self.btnNextQuestionSet.enabled = True
#             self.DisplayQuestionSet(self.xQuestionSets[self.iQuestionSetIndex])
#             self.EnableQuestionSetButtons()
#         else:
#             self.btnPreviousQuestionSetQuestionSet.enabled = False

        self.EnableQuestionSetButtons()
        if (self.iQuestionSetIndex >= 0):
            self.DisplayQuestionSet(self.xQuestionSets[self.iQuestionSetIndex])


    #-----------------------------------------------

    def onSaveQuestionSetClicked(self):

        print('---Saving Question Set responses')
        #TODO: perform save ???
        
        # clear widget for Next Page
        for i in reversed(range(self.quizLayout.count())):
            self.quizLayout.itemAt(i).widget().setParent(None)


