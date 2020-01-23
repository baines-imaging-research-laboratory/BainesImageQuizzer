import PythonQt
import os
import vtk, qt, ctk, slicer
import sys
import unittest

from Utilities import *
from Question import *

from DICOMLib import DICOMUtils

import xml
from xml.dom import minidom
import ssl

#-----------------------------------------------

class Page:
    
    def __init__(self,  parent=None):
        self.sClassName = type(self).__name__
        self.parent = parent
        self.sPageName = ''
        self.sPageDescriptor = ''
        self.iQuestionSetIndex = 0
        self.iNumQuestionSets = 0
        
        self.lValidVolumeFormats = ['nrrd','nii','mhd']
        self.ltupViewNodes = []
        
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
        self.oQuizzerUtils = Utilities()


        # get name and descriptor
        self.sPageName = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'name')
        self.sPageDescriptor = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'descriptor')

        self.quizLayout.addWidget(self.btnNextQuestionSet)
        self.quizLayout.addWidget(self.btnPreviousQuestionSet)
        self.quizLayout.addWidget(self.btnSaveQuestionSet)

        # for each 'outstanding' page (questions not yet answered)

        # display Images
        self.xImages = self.oIOXml.GetChildren(xPageNode, 'Image')
        self.iNumImages = self.oIOXml.GetNumChildren(xPageNode, 'Image')
        
        self.ltupViewNodes = self.BuildViewNodes(self.xImages)
        
        
        if len(self.ltupViewNodes) > 0:
            # clear images
            self.AssignViewToNone('Red')
            self.AssignViewToNone('Yellow')
            self.AssignViewToNone('Green')

            for i in range(len(self.ltupViewNodes)):
                
                # get node details
                slNode, sImageDestination, sOrientation, sViewLayer = self.ltupViewNodes[i]
                self.AssignNodesToView(slNode.GetName(), sImageDestination, sViewLayer, sOrientation)


        # get Question Set nodes and number of sets
        self.xQuestionSets = self.oIOXml.GetChildren(xPageNode, 'QuestionSet')
        self.iNumQuestionSets = self.oIOXml.GetNumChildren(xPageNode, 'QuestionSet')

        
        self.DisplayQuestionSet(self.xQuestionSets[self.iQuestionSetIndex])

        # enable buttons
        self.EnableQuestionSetButtons()
        
            
        
    #-----------------------------------------------
    #         Manage Data Input
    #-----------------------------------------------

    def BuildViewNodes(self, xImages):
        
        # for each image
        for i in range(len(xImages)):


            # Extract image attributes
            sVolumeFormat = self.oIOXml.GetValueOfNodeAttribute(xImages[i], 'format')
            sNodeDescriptor = self.oIOXml.GetValueOfNodeAttribute(xImages[i], 'descriptor')
            sImageDestination = self.oIOXml.GetValueOfNodeAttribute(xImages[i], 'destination')
            sOrientation = self.oIOXml.GetValueOfNodeAttribute(xImages[i], 'orientation')
            self.sNodeName = self.sPageName + '_' + self.sPageDescriptor + '_' + sNodeDescriptor

            
            # Extract type of image being loaded

            xImageTypeNodes = self.oIOXml.GetChildren(xImages[i], 'Type')
            
            if len(xImageTypeNodes) > 1:
                sWarningMsg = 'There can only be one type of image - using first definition'
                self.oQuizzerUtils.DisplayWarning(sWarningMsg) 
                
            self.sImageType = self.oIOXml.GetDataInNode(xImageTypeNodes[0])
            

            # Extract path element
            
            xPathNodes = self.oIOXml.GetChildren(xImages[i], 'Path')

            if len(xPathNodes) > 1:
                sWarningMsg = 'There can only be one path per image - using first defined path'
                self.oQuizzerUtils.DisplayWarning( sWarningMsg )

            self.sImagePath = self.oIOXml.GetDataInNode(xPathNodes[0])
            

            # Extract destination layer (foreground, background, label)

            xLayerNodes = self.oIOXml.GetChildren(xImages[i], 'Layer')
            if len(xLayerNodes) > 1:
                sWarningMsg = 'There can only be one layer per image - using first defined layer'
                self.oQuizzerUtils.DisplayWarning(sWarningMsg)

            sViewLayer = self.oIOXml.GetDataInNode(xLayerNodes[0])
            
            
            # Load images 
            
            bLoadSuccess = True
            if (sVolumeFormat == 'dicom'):
                bLoadSuccess, slNode = self.LoadDicomVolume(self.sImagePath)
                
            elif (sVolumeFormat in self.lValidVolumeFormats):
                bLoadSuccess, slNode = self.LoadDataVolume(self.sNodeName, self.sImageType, self.sImagePath)

                        
            else:
                sErrorMsg = ('Undefined volume format : %s' % sVolumeFormat)
                self.oQuizzerUtils.DisplayError(sErrorMsg)
                bLoadSuccess = False

            if bLoadSuccess and (slNode is not None):
                tupViewNode = [slNode, sImageDestination, sOrientation, sViewLayer]
                self.ltupViewNodes.append(tupViewNode)
    
        return self.ltupViewNodes
                    
                    
         
    #-----------------------------------------------

    def LoadDataVolume(self, sNodeName, sImageType, sImagePath):
        
        # Load a 3D data volume file - check if already loaded (node exists)
        
        dictProperties = {}
        bNodeExists = False
        slNode = None


        try:
                    
            bLoadSuccess = True
            if (sImageType == 'Volume'):
                
                bNodeExists, slNode = self.CheckForNodeExists(sNodeName, 'vtkMRMLScalarVolumeNode')
                if not (bNodeExists):
                    slNode = slicer.util.loadVolume(sImagePath, {'show': False, 'name': sNodeName})
                else: # make sure a node exists
                    if bNodeExists and (slNode is None):
                        bLoadSuccess = False
            
            elif (sImageType == 'Labelmap'):
                
                bNodeExists, slNode = self.CheckForNodeExists(sNodeName, 'vtkMRMLLabelMapVolumeNode')
                dictProperties = {'labelmap' : True, 'show': False, 'name': sNodeName}
                if not (bNodeExists):
                    slNode = slicer.util.loadLabelVolume(sImagePath, dictProperties)
                else: # make sure a node exists
                    if bNodeExists and (slNode is None):
                        bLoadSuccess = False
                    
            else:
                
                sErrorMsg = ('Undefined image type: %s' % sImageType)
                self.oQuizzerUtils.DisplayError(sErrorMsg)
                bLoadSuccess = False
                
        except:
            
            bLoadSuccess = False
        
        
        return bLoadSuccess, slNode
    
    #-----------------------------------------------

    def LoadDicomVolume(self, sDicomSeriesDir):
        slNode = None
        bLoadSuccess = False

        # db for storing imported dicom files
#         self.dicomDatabaseDir = 'D:\\Users\\cjohnson\\Work\\Projects\\SlicerEclipseProjects\\ImageQuizzerExtras\\CtkDicomDatabase'
        self.dicomURL = 'file:\\\\\\D:\\Users\\cjohnson\\Work\\Projects\\SlicerEclipseProjects\\ImageQuizzerExtras\\TinyRT.zip'
       
        sPatientName = 'TinyPatient'
        
        if (slicer.dicomDatabase.isOpen):
            bPatientFoundInDB = False
            patients = slicer.dicomDatabase.patients()
            for patientUID in patients:
                    currentName = slicer.dicomDatabase.nameForPatient(patientUID)
                    if currentName == sPatientName:
                        bPatientFoundInDB = True

            if not bPatientFoundInDB:
                DICOMUtils.importDicom(sDicomSeriesDir)

            
            # get loaded scalar volume nodes to see if patient already exists
            bPatientAlreadyLoaded = False
            
            lNodeCollection = slicer.mrmlScene.GetNodesByClass('vtkMRMLScalarVolumNode')
            lNodeCollection.UnRegister(None)
            
            iNumNodes = slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLScalarVolumeNode')
            for idx in range(iNumNodes):
                slTempNode = slicer.mrmlScene.GetNthNodeByClass(idx,'vtkMRMLScalarVolumeNode')
                sTempNodeName = slTempNode.GetName()
                print(sTempNodeName)
                if sTempNodeName == sPatientName:
                    bPatientAlreadyLoaded = True
            
#             for node in lNodeCollection:
#                 name = node.GetNodeName(node)
#                 if name == sPatientName:
#                     bPatientAlreadyLoaded = True

            if not bPatientAlreadyLoaded:
                DICOMUtils.loadPatient(None, sPatientName, None)
        
        else:
            sErrorMsg = ('Slicer Database is not open')
            self.oQuizzerUtils.DisplayError(sErrorMsg)
        

        return bLoadSuccess, slNode
    
    #-----------------------------------------------
    #         Manage Views
    #-----------------------------------------------
 
    def AssignNodesToView(self, sSlicerNodeName, sImageDestination, sNodeLayer, sOrientation):
 
        slWidget = slicer.app.layoutManager().sliceWidget(sImageDestination)
        slWindowLogic = slWidget.sliceLogic()
        slWindowCompositeNode = slWindowLogic.GetSliceCompositeNode()
        if sNodeLayer == 'Background':
            slWindowCompositeNode.SetBackgroundVolumeID(slicer.util.getNode(sSlicerNodeName).GetID())
            slWidget.setSliceOrientation(sOrientation)
        elif sNodeLayer == 'Foreground':
            slWindowCompositeNode.SetForegroundVolumeID(slicer.util.getNode(sSlicerNodeName).GetID())
            slWidget.setSliceOrientation(sOrientation)
        elif sNodeLayer == 'Label':
            slWindowCompositeNode.SetLabelVolumeID(slicer.util.getNode(sSlicerNodeName).GetID())
#             slWidget.setSliceOrientation(sOrientation)
        
         

    #-----------------------------------------------
    
    def AssignViewToNone(self, sScreenColor):
        
        slWidget = slicer.app.layoutManager().sliceWidget(sScreenColor)
        slLogic = slWidget.sliceLogic()
        slCompNode = slLogic.GetSliceCompositeNode()
        slCompNode.SetBackgroundVolumeID('None')
        slCompNode.SetForegroundVolumeID('None')
        slCompNode.SetLabelVolumeID('None')
        

    #-----------------------------------------------

    def CheckForNodeExists(self, sNodeName, sNodeClass):
        # a node does not have to be loaded if it already exists
        
        
        # initialize
        bNodeExists = False
        slNode = None
        
        # check for nodes by name and check it's the proper class
        try:
            slNode = slicer.mrmlScene.GetFirstNodeByName(sNodeName)
            if (slNode.GetClassName() == sNodeClass) :
                bNodeExists = True
        except:
            bNodeExists = False
        
        return bNodeExists, slNode
    
    
    
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


