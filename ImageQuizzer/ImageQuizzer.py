import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

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
        #                        UI setup
        #  -----------------------------------------------------------------------------------
        loader = qt.QUiLoader()
        moduleName = 'ImageQuizzer'
        scriptedModulesPath = eval('slicer.modules.%s.path' % moduleName.lower())
        scriptedModulesPath = os.path.dirname(scriptedModulesPath)
        path = os.path.join(scriptedModulesPath, 'Resources', 'UI', '%s.ui' %moduleName)
        print ("path", path)
         
        qfile = qt.QFile(path)
        qfile.open(qt.QFile.ReadOnly)
        uiWidget = loader.load(qfile, self.parent)
        self.layout = self.parent.layout()
        # self.layout.addWidget(uiWidget)
         
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
         
        # Data buttons setup
        self.buttons = qt.QFrame()
        self.buttons.setLayout( qt.QHBoxLayout() )
        leftLayout.addWidget(self.buttons)
        self.addDataButton = qt.QPushButton("Add Data")
        self.buttons.layout().addWidget(self.addDataButton)
        self.addDataButton.connect("clicked()",slicer.app.ioManager().openAddDataDialog)
        self.loadDCMButton = qt.QPushButton("Load DCM")
        self.buttons.layout().addWidget(self.loadDCMButton)
        #  self.loadDCMButton.connect("clicked()",slicer.app.ioManager().openLoadDicomVolumeDialog)
        
        
        # Collapsible button
        self.sampleCollapsibleButton = ctk.ctkCollapsibleButton()
        self.sampleCollapsibleButton.text = "Patient Studies"
        leftLayout.addWidget(self.sampleCollapsibleButton)
        
        
        # Layout within the sample collapsible button
        self.sampleFormLayout = qt.QFormLayout(self.sampleCollapsibleButton)
        
        
        # the volume selectors
        self.inputFrame = qt.QFrame(self.sampleCollapsibleButton)
        self.inputFrame.setLayout(qt.QHBoxLayout())
        self.sampleFormLayout.addWidget(self.inputFrame)
        self.inputSelector = qt.QLabel("Studies: ", self.inputFrame)
        self.inputFrame.layout().addWidget(self.inputSelector)
        self.inputSelector = slicer.qMRMLNodeComboBox(self.inputFrame)
        self.inputSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
        self.inputSelector.addEnabled = False
        self.inputSelector.removeEnabled = False
        self.inputSelector.setMRMLScene( slicer.mrmlScene )
        self.inputFrame.layout().addWidget(self.inputSelector)
        
        #add quizz
        leftLayout.addWidget(uiWidget)
        
        
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
        self.layout.addWidget(splitter)
     
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
        print 'changeView: ',volToDisplay.GetName()
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
 