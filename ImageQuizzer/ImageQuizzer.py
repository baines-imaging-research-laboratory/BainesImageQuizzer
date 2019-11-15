import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

import mistletoe
import urllib.request # import submodule directly
from pkg_resources import _set_parent_ns
from pathlib import _PathParents
from Question import *
from TargetItem import *
from Session import *
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
    self.parent.contributors = ["Carol Johnson (Software Developer - Baines Imaging Laboratory)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """ This scripted loadable module displays a quiz to be answered based on images shown."""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """ Baines Imaging Research Laboratory. 
    Principal Investigator: Dr. Aaron Ward.
    """
    

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
        self.qtQuizProgressWidget = qt.QTextEdit()
        # -------------------------------------------------------------------------------------
        # Interaction with 3D Scene
        #self.interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
        #  -----------------------------------------------------------------------------------
        #                        Surface Registration UI setup
        #  -----------------------------------------------------------------------------------
        
        
        
        
        print ("-------ImageQuizzer Widget SetUp--------")
        
        slicer.util.setMenuBarsVisible(True)
        slicer.util.setToolbarsVisible(False)
        
        #  -----------------------------------------------------------------------------------
        #                        UI setup through .md files
        #  -----------------------------------------------------------------------------------
        
        #-------------------------------------------
        # load quiz
        moduleName = 'ImageQuizzer'
        scriptedModulesPath = eval('slicer.modules.%s.path' % moduleName.lower())
        scriptedModulesPath = os.path.dirname(scriptedModulesPath)
        path = os.path.join(scriptedModulesPath, 'Resources', 'MD', '%s.md' %moduleName)
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
        path = os.path.join(scriptedModulesPath, 'Resources', 'MD', '%s.md' %studyBrowserFileName)
        print ("path", path)

        with open(path, 'r') as fin:
            self.docHtmlStudies = mistletoe.markdown(fin)

        print(self.docHtmlStudies)

        displayStudiesWidget = qt.QTextEdit()
        displayStudiesWidget.setText(self.docHtmlStudies)
        displayStudiesWidget.show()
        
        # build study browser Widget
        mdBrowserWidgetLayout = qt.QVBoxLayout()
        mdBrowserWidget = qt.QWidget()
        mdBrowserWidget.setLayout(mdBrowserWidgetLayout)
        browserTitle = qt.QLabel('Image Quizzer Patients')
        mdBrowserWidgetLayout.addWidget(browserTitle)

        # parse md study browser file
        doc = vtk.vtkXMLUtilities.ReadElementFromString("<root>"+self.docHtmlStudies+"</root>")
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
                                lblText = "  - " + element2.GetCharacterData()
                                lbl = qt.QLabel(lblText)
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
        
        # -----------
        # test creating a radio button object through the abstract Question Class
        # display the group box in the layout.
        # ready for further development
        optList = ['Injury','Recurrence']
        desc = 'Assessment'
        rq = RadioQuestion(optList, desc)
        (rqSuccess, rqGrpBox) = rq.buildQuestion()
 
        mdQuizWidgetLayout.addWidget(rqGrpBox)

        
        # -----------
        
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
        # set up quiz widget
        leftWidget = qt.QWidget()
        leftLayout = qt.QVBoxLayout()
        leftWidget.setLayout(leftLayout)
         
        
        
        #-------------------------------------------
        # Collapsible button
        self.sampleCollapsibleButton = ctk.ctkCollapsibleButton()
        self.sampleCollapsibleButton.text = "Image Quizzer Components"
        leftLayout.addWidget(self.sampleCollapsibleButton)
        
        
        # Layout within the sample collapsible button - form needs a frame
        self.sampleFormLayout = qt.QFormLayout(self.sampleCollapsibleButton)
        self.quizFrame = qt.QFrame(self.sampleCollapsibleButton)
        self.quizFrame.setLayout(qt.QVBoxLayout())
        self.sampleFormLayout.addWidget(self.quizFrame)
        
        #-------------------------------------------
        # setup the tab widget
        leftTabWidget = qt.QTabWidget()
        tabQuiz = qt.QWidget()
        tabStudyBrowser = qt.QWidget()
        leftTabWidget.addTab(tabQuiz,"Quiz")
        leftTabWidget.addTab(slicer.modules.segmenteditor.widgetRepresentation(),"Segment Editor")
        leftTabWidget.addTab(tabStudyBrowser,"Study List")
        
        tabQuizLayout = qt.QVBoxLayout()
        tabQuiz.setLayout(tabQuizLayout)
        tabQuizLayout.addWidget(mdQuizWidget)
        
        tabStudyBrowserLayout = qt.QVBoxLayout()
        tabStudyBrowser.setLayout(tabStudyBrowserLayout)
        tabStudyBrowserLayout.addWidget(mdBrowserWidget)
        
        
        #add quiz
        self.quizFrame.layout().addWidget(leftTabWidget)
        
        
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
        
        # Status button
        self.btnShowQuizProgress = qt.QPushButton("Show Quiz Progress")
        self.btnShowQuizProgress.toolTip = "Display status of images."
        self.btnShowQuizProgress.enabled = True
        leftLayout.addWidget(self.btnShowQuizProgress)
        
        self.layout.addWidget(leftWidget)

        #-------------------------------------------
        # Connections
        #-------------------------------------------
        self.btnShowQuizProgress.connect('clicked(bool)', self.onShowQuizProgressClicked)
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def onShowQuizProgressClicked(self):
        self.qtQuizProgressWidget.setText(self.docHtmlStudies)
        self.qtQuizProgressWidget.show()

    
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

 
 
#-----------------------------------------------------------------------------------------------
#
# I can't get this working yet ... I want to load and run all tests in the Testing subdirectory
#
# from TestQuestion import *
# from ImageQuizzer.Testing.Python.TestQuestion.TestQuestion import *
#
class ImageQuizzerTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """
     
    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear(0)
#         self.tqt = TestQuestionTest()
         
    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_ImageQuizzer1()
#         self.tqt.runTest()
#         
# 
    def test_ImageQuizzer1(self):
        """ Ideally you should have several levels of tests.  At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).  At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.  For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """
         
        self.delayDisplay('WARNING: THIS UNITTEST IS UNDER DEVELOPMENT - SEE TESTCASES')
 
 
# testing md5 hash
#         text = 'D:\BainesWork\ShareableData\SlicerData\Day2_CT.nrrd'
#         textUtf8 = text.encode("utf-8")
#         hash = hashlib.md5(textUtf8)
#         hexa = hash.hexdigest()
#         print(hexa)
