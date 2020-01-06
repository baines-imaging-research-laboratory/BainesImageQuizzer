import os
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from Session import *
from pip._vendor.distlib._backport.shutil import copyfile
#

##########################################################################################
#
#                                ImageQuizzer
#
##########################################################################################

class ImageQuizzer(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Image Quizzer" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Baines Custom Modules"]
    self.parent.dependencies = []
    self.parent.contributors = ["Carol Johnson (Software Developer - Baines Imaging Laboratory)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """ This scripted loadable module displays a quiz to be answered based on images shown."""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """ Baines Imaging Research Laboratory. 
    Principal Investigator: Dr. Aaron Ward.
    """
    

##########################################################################
#
# ImageQuizzerWidget
#
##########################################################################


class ImageQuizzerWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __init__(self, parent):
        ScriptedLoadableModuleWidget.__init__(self,parent)
        
        moduleName = 'ImageQuizzer'

        self.ScriptedModulesPath = eval('slicer.modules.%s.path' % moduleName.lower())
        self.ScriptedModulesPath = os.path.dirname(self.ScriptedModulesPath)
        self.sResourcesPath = os.path.join(self.ScriptedModulesPath, 'Resources', 'XML')
        self.sUsersBasePath = os.path.join(self.ScriptedModulesPath, 'Users')
        
        # test that Users folder exists - if not, create it
        if not os.path.exists(self.sUsersBasePath):
            os.makedirs(self.sUsersBasePath)
        
        self.BuildUserLoginWidget()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def BuildUserLoginWidget(self):
        
        # create the widget for user login
        # This is run in the constructor so that the widget remains in scope
        self.qUserLoginLayout = qt.QVBoxLayout()
        self.qUserLoginWidget = qt.QWidget()
        self.qUserLoginWidget.setLayout(self.qUserLoginLayout)
        qUserStudyWidgetTitle = qt.QLabel('Baines Image Quizzer - User Login')
        self.qUserLoginLayout.addWidget(qUserStudyWidgetTitle)
        
        self.qLineUserName = qt.QLineEdit()
        self.qLineUserName.setPlaceholderText('Enter user name')
        self.qUserLoginLayout.addWidget(self.qLineUserName)
        
        # Add vertical spacer
        self.qUserLoginLayout.addSpacing(20)
        
       # Get study button
        # File Picker
        self.btnGetUserStudy = qt.QPushButton("Select Quiz")
        self.btnGetUserStudy.setEnabled(True)
        self.btnGetUserStudy.toolTip = "Select Quiz xml file for launch "
        self.btnGetUserStudy.connect('clicked(bool)', self.onApplyOpenFile)
        self.qUserLoginLayout.addWidget(self.btnGetUserStudy)

        self.qLblQuizFilename = qt.QLabel('Selected quiz filename')
        self.qUserLoginLayout.addWidget(self.qLblQuizFilename)
        
        # Add vertical spacer
        self.qUserLoginLayout.addSpacing(20)
        
        # Launch study button (not enabled until study is picked)
        self.btnLaunchStudy = qt.QPushButton("Launch Quiz")
        self.btnLaunchStudy.setEnabled(False)
        self.btnLaunchStudy.connect('clicked(bool)', self.onApplyLaunchQuiz)
        self.qUserLoginLayout.addWidget(self.btnLaunchStudy)
        
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
#         slicer.util.setToolbarsVisible(False) # for live runs
        slicer.util.setToolbarsVisible(True) # while developing
        
        
        #-------------------------------------------
#         moduleName = 'ImageQuizzer'

#         scriptedModulesPath = eval('slicer.modules.%s.path' % moduleName.lower())
#         scriptedModulesPath = os.path.dirname(scriptedModulesPath)
#         path = os.path.join(scriptedModulesPath, 'Resources', 'XML', '%s.xml' %moduleName)
#         print ("path", path)

        #-------------------------------------------
        # set up quiz widget
        self.leftWidget = qt.QWidget()
        self.leftLayout = qt.QVBoxLayout()
        self.leftWidget.setLayout(self.leftLayout)
         
        
        
        #-------------------------------------------
        # Collapsible button
        self.sampleCollapsibleButton = ctk.ctkCollapsibleButton()
        self.sampleCollapsibleButton.text = "Baines Image Quizzer"
        self.leftLayout.addWidget(self.sampleCollapsibleButton)
        

        
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
        
        
        
#         #-------------------------------------------
#         # Next button
#         self.nextButton = qt.QPushButton("Next")
#         self.nextButton.toolTip = "Display next in series."
#         self.nextButton.enabled = True
#         self.leftLayout.addWidget(self.nextButton)
#         self.nextButton.connect('clicked(bool)',self.onNextButtonClicked)
#         
#         # Back button
#         self.backButton = qt.QPushButton("Back")
#         self.backButton.toolTip = "Display previous series."
#         self.backButton.enabled = True
#         self.leftLayout.addWidget(self.backButton)
        
        # Status button
        self.btnShowQuizProgress = qt.QPushButton("Show Quiz Progress")
        self.btnShowQuizProgress.toolTip = "Display status of images."
        self.btnShowQuizProgress.enabled = True
        self.leftLayout.addWidget(self.btnShowQuizProgress)
        
        self.layout.addWidget(self.leftWidget)
        
        self.qUserLoginWidget.show()



        #-------------------------------------------
        # Connections
        #-------------------------------------------
        self.btnShowQuizProgress.connect('clicked(bool)', self.onShowQuizProgressClicked)
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def onApplyOpenFile(self):
        # set to default
        self.btnLaunchStudy.setEnabled(False)
        self.qLblQuizFilename.text = ""

        # get quiz filename
        self.quizInputFileDialog = qt.QFileDialog()
        self.sSelectedQuiz = self.quizInputFileDialog.getOpenFileName(self.qUserLoginWidget, "Open File", self.sResourcesPath, "XML files (*.xml)" )

        # check that file was selected
        if not self.sSelectedQuiz:
            msgBox = qt.QMessageBox()
            msgBox.critical(0,"Error","No quiz was selected")
        else:
            # enable the launch button
            self.qLblQuizFilename.setText(self.sSelectedQuiz)
            self.btnLaunchStudy.setEnabled(True)
            self.qUserLoginWidget.show()
            self.qUserLoginWidget.activateWindow()
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def onApplyLaunchQuiz(self):
        # confirm username was entered
        if not self.qLineUserName.text:
            msgBox = qt.QMessageBox()
            msgBox.critical(0,"ERROR","No user name was entered")
        else:
            # copy file from Resource into user folder
            if self.SetupUserQuizFolder(): # success
                # start the session
                self.leftWidget.activateWindow()
                self.oSession = Session()
                self.oSession.RunSetup(self.qLblQuizFilename.text, self.qLineUserName.text,self.leftLayout, self.sampleFormLayout)
#                 self.oSession = Session(self.qLblQuizFilename.text, self.qLineUserName.text)

    def SetupUserQuizFolder(self):
        # create user folder if it doesn't exist
        self.sUserFolder = os.path.join(self.sUsersBasePath, self.qLineUserName.text)
        if not os.path.exists(self.sUserFolder):
            os.makedirs(self.sUserFolder)
            
        # check if quiz file already exists in the user folder - if not, copy from Resources

        # setup for new location
        sPath, sFilename = os.path.split(self.sSelectedQuiz)
        sUserQuizFile = os.path.join(self.sUserFolder, sFilename)
        if not os.path.isfile(sUserQuizFile):
            # file not found, copy file from Resources to User folder
            copyfile(self.qLblQuizFilename.text, sUserQuizFile)
            return True

        else:
            # file exists - make sure it is readable
            if not os.access(sUserQuizFile, os.R_OK):
                # existing file is unreadable            
                msgBox = qt.QMessageBox()
                msgBox.critical(0,"ERROR","Quiz file is not readable")
                return False
            else:
                msgBox = qt.QMessageBox()
                msgBox.setText('Quiz file exists in user folder - new results will be appended')
                msgBox.exec()
                return True
        
    
        
        
    
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
    



##########################################################################
#
# ImageQuizzerLogic
#
##########################################################################

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

 
 
