import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import mistletoe
#import hashlib
import urllib
# 

#
# ImageQuizzer
#

class ImageQuizzer(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "ImageQuizzer" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Baines Custom Modules"]
    self.parent.dependencies = []
    self.parent.contributors = ["Carol Johnson (Baines Imaging Research Laboratory)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
AND it runs a quiz!!!
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# ImageQuizzerWidget
#

class ImageQuizzerWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        
        # ------------------------------------------------------------------------------------
        #                                   Global Variables
        # ------------------------------------------------------------------------------------
        #self.logic = ImageQuizzerLogic(self)
        # -------------------------------------------------------------------------------------
        # Interaction with 3D Scene
        #self.interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
        #  -----------------------------------------------------------------------------------
        #                        Surface Registration UI setup
        #  -----------------------------------------------------------------------------------
        
        
        
        
        print ("-------ImageQuizzer Widget SetUp--------")
        
        
        
        #  -----------------------------------------------------------------------------------
        #                        UI setup through .md file
        #  -----------------------------------------------------------------------------------
        
        #-------------------------------------------
        # load quiz
        moduleName = 'ImageQuizzer'
        scriptedModulesPath = eval('slicer.modules.%s.path' % moduleName.lower())
        scriptedModulesPath = os.path.dirname(scriptedModulesPath)
        path = os.path.join(scriptedModulesPath, 'Resources', 'UI', '%s.md' %moduleName)
        print ("path", path)

        with open(path, 'r') as fin:
            docHtml = mistletoe.markdown(fin)

        print(docHtml)

        displayWidget = qt.QTextEdit()
        displayWidget.setText(docHtml)
        displayWidget.show()


        #-------------------------------------------
        # load patient studies
        studyBrowserFileName = "ImageQuizzerStudyBrowser"
        scriptedModulesPath = eval('slicer.modules.%s.path' % moduleName.lower())
        scriptedModulesPath = os.path.dirname(scriptedModulesPath)
        path = os.path.join(scriptedModulesPath, 'Resources', 'UI', '%s.md' %studyBrowserFileName)
        print ("path", path)

        with open(path, 'r') as fin:
            docHtmlStudies = mistletoe.markdown(fin)

        print(docHtmlStudies)

        displayStudiesWidget = qt.QTextEdit()
        displayStudiesWidget.setText(docHtmlStudies)
        displayStudiesWidget.show()
        
        # build study browser Widget
        mdBrowserWidgetLayout = qt.QVBoxLayout()
        mdBrowserWidget = qt.QWidget()
        mdBrowserWidget.setLayout(mdBrowserWidgetLayout)
        browserTitle = qt.QLabel('Image Quizzer Patients')
        mdBrowserWidgetLayout.addWidget(browserTitle)

        # parse md study browser file
        doc = vtk.vtkXMLUtilities.ReadElementFromString("<root>"+docHtmlStudies+"</root>")
        patients = {}
        series = []
        for index0 in range(doc.GetNumberOfNestedElements()):
            element0 = doc.GetNestedElement(index0)
            if element0.GetName() == 'h1':
                # Found a new patient
                # Save old patient first
                if patients:
                    patients.append(series)
                series = {}
                series['Patient Name'] = element0.GetCharacterData()
                series['imagePath'] = []
                lbl = qt.QLabel(element0.GetCharacterData())
                mdBrowserWidgetLayout.addWidget(lbl)
            if element0.GetName() == 'ul':
                # Found a new answer list
                for index1 in range(element0.GetNumberOfNestedElements()):
                    element1 = element0.GetNestedElement(index1)
                    if element1.GetName() == 'li':
                        for index2 in range(element1.GetNumberOfNestedElements()):
                            element2 = element1.GetNestedElement(index2)
                            if element2.GetName() == 'a':
                                impath = element2.GetAttribute('href')
                                series['imagePath'].append(impath)
                                lbl = qt.QLabel(impath)
                                mdBrowserWidgetLayout.addWidget(lbl)
         
        print(patients)
        
        print(impath)
        strpath = urllib.request.unquote(impath)
        print(strpath)
        slicer.util.loadVolume(strpath)





        #-------------------------------------------
        # build quiz Widget
        mdQuizWidgetLayout = qt.QVBoxLayout()
        mdQuizWidget = qt.QWidget()
        mdQuizWidget.setLayout(mdQuizWidgetLayout)
        quizTitle = qt.QLabel('Baines Image Quizzer')
        mdQuizWidgetLayout.addWidget(quizTitle)
        

        
        # parse md quiz file
        doc = vtk.vtkXMLUtilities.ReadElementFromString("<root>"+docHtml+"</root>")
        question = {}
        questions = []
        for index0 in range(doc.GetNumberOfNestedElements()):
            element0 = doc.GetNestedElement(index0)
            if element0.GetName() == 'h1':
                # Found a new question
                # Save old question first
                if question:
                    questions.append(question)
                    mdQuizWidgetLayout.addWidget(grpBox)
                question = {}
                question['title'] = element0.GetCharacterData()
                question['answers'] = []
                grpBox = qt.QGroupBox()
                grpBox.setTitle(element0.GetCharacterData())
                grpBoxLayout = qt.QVBoxLayout()
                grpBox.setLayout(grpBoxLayout)
            if element0.GetName() == 'ul':
                # Found a new answer list
                for index1 in range(element0.GetNumberOfNestedElements()):
                    element1 = element0.GetNestedElement(index1)
                    question['answers'].append(element1.GetCharacterData())
                    rbtn = qt.QRadioButton(element1.GetCharacterData())
                    grpBoxLayout.addWidget(rbtn)
        
        print(questions)

        #-------------------------------------------
        #splitter
        splitter = qt.QSplitter()
        
        leftWidget = qt.QWidget()
        rightWidget = qt.QWidget()
        
        splitter.addWidget(leftWidget)
        splitter.addWidget(rightWidget)
         
             
        #-------------------------------------------
        #right layout for 2d/3d viewer
        sceneWidget = slicer.qMRMLLayoutWidget()
        sceneWidget.setMRMLScene(slicer.mrmlScene)
        sceneWidget.setLayout(0)
        
        rightLayout = qt.QVBoxLayout()
        rightWidget.setLayout(rightLayout)
        rightLayout.addWidget(sceneWidget)
        
        #-------------------------------------------
        #   #left layout for quizz
        leftLayout = qt.QVBoxLayout()
        leftWidget.setLayout(leftLayout)
         
        
        
        #-------------------------------------------
        # Collapsible button
        self.sampleCollapsibleButton = ctk.ctkCollapsibleButton()
        self.sampleCollapsibleButton.text = "Image Quizzer Components"
        leftLayout.addWidget(self.sampleCollapsibleButton)
        
        
        # Layout within the sample collapsible button
        self.sampleFormLayout = qt.QFormLayout(self.sampleCollapsibleButton)
        
        #-------------------------------------------
        # setup the tab widget
        leftTabWidget = qt.QTabWidget()
        tabQuiz = qt.QWidget()
        tabStudyBrowser = qt.QWidget()
        leftTabWidget.addTab(tabQuiz,"Quiz")
#        leftTabWidget.addTab(slicer.modules.segmenteditor.widgetRepresentation(),"Segment Editor")
        leftTabWidget.addTab(tabStudyBrowser,"Study List")
        
        tabQuizLayout = qt.QVBoxLayout()
        tabQuiz.setLayout(tabQuizLayout)
        tabQuizLayout.addWidget(mdQuizWidget)
        
        tabStudyBrowserLayout = qt.QVBoxLayout()
        tabStudyBrowser.setLayout(tabStudyBrowserLayout)
        tabStudyBrowserLayout.addWidget(mdBrowserWidget)
        
        
        #add quizz
#        leftLayout.addWidget(mdWidget)
        leftLayout.addWidget(leftTabWidget)
        
        
        #-------------------------------------------
        # Next button
        self.nextButton = qt.QPushButton("Next")
        self.nextButton.toolTip = "Display next in series."
        self.nextButton.enabled = True
        leftLayout.addWidget(self.nextButton)
        self.nextButton.connect('clicked(bool)',self.onNextButtonClicked)
        
        # Back button
        self.backButton = qt.QPushButton("Back")
        self.backButton.toolTip = "Display previous series."
        self.backButton.enabled = True
        leftLayout.addWidget(self.backButton)
        
        #-------------------------------------------
        # combine left and right layouts 
#        self.layout.addWidget(splitter)
        
        self.layout.addWidget(leftWidget)
     
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onNextButtonClicked(self):
##    print("Next volume ...")
##    #Confirm that the user has selected a node
##    inputVolume = self.inputSelector.currentNode()
##    self.inputValidation(inputVolume)
 
        scene = slicer.mrmlScene
        nNodes = scene.GetNumberOfNodes()
        #   qt.QMessageBox.information(slicer.util.mainWindow(),'NextVolume ...',nNodes)
        
        nNodes = scene.GetNumberOfNodesByClass('vtkMRMLScalarVolumeNode')
        n = scene.GetNthNodeByClass(0,'vtkMRMLScalarVolumeNode')
        # qt.QMessageBox.information(slicer.util.mainWindow(),'NextVolume ...',nNodes)
        for idx in range(nNodes):
            node = scene.GetNthNodeByClass(idx,'vtkMRMLScalarVolumeNode')
        name = node.GetName()
        #  qt.QMessageBox.information(slicer.util.mainWindow(),'NextVolume ...',name)
        self.changeView(node)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def changeView(self,volToDisplay):
        print ('changeView: ',volToDisplay.GetName())
        # Change the views to the selected volume
        ijkToRAS = vtk.vtkMatrix4x4()
        volToDisplay.GetIJKToRASMatrix(ijkToRAS)
        selectionNode = slicer.app.applicationLogic().GetSelectionNode()
        selectionNode.SetReferenceActiveVolumeID(volToDisplay.GetID())
        slicer.app.applicationLogic().PropagateVolumeSelection(0)
        slicer.util.delayDisplay(volToDisplay.GetName())
    



class ImageQuizzerLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """
    def __init__(self,interface):
        ScriptedLoadableModuleLogic.__init__(self)
        self.interface = interface

 
 
 
 
#class ImageQuizzerSlicelet(Slicelet):
#  """ Creates the interface when module is run as a stand alone gui app.
#  """
 
#  def __init__(self):
#    super(ImageQuizzerSlicelet,self).__init__(ImageQuizzerWidget)
 
 
# testing md5 hash
#         text = 'D:\BainesWork\ShareableData\SlicerData\Day2_CT.nrrd'
#         textUtf8 = text.encode("utf-8")
#         hash = hashlib.md5(textUtf8)
#         hexa = hash.hexdigest()
#         print(hexa)
