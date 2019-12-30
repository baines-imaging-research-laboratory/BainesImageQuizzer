import os
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
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
    
    def __init__(self, parent):
        ScriptedLoadableModuleWidget.__init__(self,parent)

        # create the widget for user login
        self.qUserLoginLayout = qt.QVBoxLayout()
        self.qUserLoginWidget = qt.QWidget()
        self.qUserLoginWidget.setLayout(self.qUserLoginLayout)
        qUserStudyWidgetTitle = qt.QLabel('Baines Image Quizzer - User Login')
        self.qUserLoginLayout.addWidget(qUserStudyWidgetTitle)
        
        self.filenameLabel = qt.QLabel('Quiz Filename')
        self.qUserLoginLayout.addWidget(self.filenameLabel)
        
        # Get study button
        # File Picker
        self.btnGetUserStudy = qt.QPushButton("Select Quiz")
        self.btnGetUserStudy.setEnabled(True)
        self.btnGetUserStudy.toolTip = "Select Quiz xml file for launch "
        self.btnGetUserStudy.connect('clicked(bool)', self.onApplyOpenFile)
        self.qUserLoginLayout.addWidget(self.btnGetUserStudy)
        
        # Launch study button (not enabled until study is picked)
        self.btnLaunchStudy = qt.QPushButton("Launch Quiz")
        self.btnLaunchStudy.setEnabled(False)
        self.btnLaunchStudy.connect('clicked(bool)', self.onApplyLaunchQuiz)
        self.qUserLoginLayout.addWidget(self.btnLaunchStudy)
        
        

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
#         slicer.util.setToolbarsVisible(False)
        slicer.util.setToolbarsVisible(True)
        
        
        #-------------------------------------------
        moduleName = 'ImageQuizzer'

        scriptedModulesPath = eval('slicer.modules.%s.path' % moduleName.lower())
        scriptedModulesPath = os.path.dirname(scriptedModulesPath)
        path = os.path.join(scriptedModulesPath, 'Resources', 'MD', '%s.md' %moduleName)
        print ("path", path)

        #-------------------------------------------
        # set up quiz widget
        self.leftWidget = qt.QWidget()
        leftLayout = qt.QVBoxLayout()
        self.leftWidget.setLayout(leftLayout)
         
        
        
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

#         #-------------------------------------------
#         # setup the tab widget
#         leftTabWidget = qt.QTabWidget()
#         tabQuiz = qt.QWidget()
#         tabStudyBrowser = qt.QWidget()
#         leftTabWidget.addTab(tabQuiz,"Quiz")
#         leftTabWidget.addTab(slicer.modules.segmenteditor.widgetRepresentation(),"Segment Editor")
#         leftTabWidget.addTab(tabStudyBrowser,"Study List")
#         
#         tabQuizLayout = qt.QVBoxLayout()
#         tabQuiz.setLayout(tabQuizLayout)
#         tabQuizLayout.addWidget(mdQuizWidget)
#         
#         tabStudyBrowserLayout = qt.QVBoxLayout()
#         tabStudyBrowser.setLayout(tabStudyBrowserLayout)
#         tabStudyBrowserLayout.addWidget(mdBrowserWidget)
#         
#         
#         #add quiz
#         self.quizFrame.layout().addWidget(leftTabWidget)
        
        
        
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
        
        self.layout.addWidget(self.leftWidget)
        
        self.qUserLoginWidget.show()



        #-------------------------------------------
        # Connections
        #-------------------------------------------
        self.btnShowQuizProgress.connect('clicked(bool)', self.onShowQuizProgressClicked)
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def onApplyOpenFile(self):
        self.btnLaunchStudy.setEnabled(False)
        self.bulkInputFileDialog = ctk.ctkFileDialog(slicer.util.mainWindow())
        self.bulkInputFileDialog.setWindowModality(1)
        self.bulkInputFileDialog.setWindowTitle("Select File For Bulk Processing")
        self.bulkInputFileDialog.defaultSuffix = "xml"
        self.bulkInputFileDialog.setNameFilter(" (*.xml)")
        self.bulkInputFileDialog.connect("fileSelected(QString)", self.onFileSelected)
        self.bulkInputFileDialog.open()

    def onFileSelected(self,inputFile):
        self.filenameLabel.setText(inputFile)
        self.btnLaunchStudy.setEnabled(True)
        self.qUserLoginWidget.show()
        self.qUserLoginWidget.activateWindow()
        return inputFile

    def onApplyLaunchQuiz(self):
        self.leftWidget.activateWindow()
        self.oSession = Session(self.filenameLabel.text)

    def onShowQuizProgressClicked(self):
        print('show progress')
#         self.qtQuizProgressWidget.setText(self.docHtmlStudies)
#         self.qtQuizProgressWidget.show()

    
    def onNextButtonClicked(self):
        print("Next volume ...")
##    #Confirm that the user has selected a node
##    inputVolume = self.inputSelector.currentNode()
##    self.inputValidation(inputVolume)
 
#         scene = slicer.mrmlScene
#         nNodes = scene.GetNumberOfNodes()
#         #   qt.QMessageBox.information(slicer.util.mainWindow(),'NextVolume ...',nNodes)
#         
#         nNodes = scene.GetNumberOfNodesByClass('vtkMRMLScalarVolumeNode')
#         n = scene.GetNthNodeByClass(0,'vtkMRMLScalarVolumeNode')
#         # qt.QMessageBox.information(slicer.util.mainWindow(),'NextVolume ...',nNodes)
#         for idx in range(nNodes):
#             node = scene.GetNthNodeByClass(idx,'vtkMRMLScalarVolumeNode')
#         name = node.GetName()
#         #  qt.QMessageBox.information(slicer.util.mainWindow(),'NextVolume ...',name)
#         self.changeView(node)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def changeView(self,volToDisplay):
        print ('changeView: ',volToDisplay.GetName())
#         # Change the views to the selected volume
#         ijkToRAS = vtk.vtkMatrix4x4()
#         volToDisplay.GetIJKToRASMatrix(ijkToRAS)
#         selectionNode = slicer.app.applicationLogic().GetSelectionNode()
#         selectionNode.SetReferenceActiveVolumeID(volToDisplay.GetID())
#         slicer.app.applicationLogic().PropagateVolumeSelection(0)
#         slicer.util.delayDisplay(volToDisplay.GetName())
    



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

 
 
