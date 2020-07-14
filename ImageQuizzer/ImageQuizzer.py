import os
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from Session import *
from pip._vendor.distlib._backport.shutil import copyfile
from slicer.util import findChild

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
        
        sModuleName = 'ImageQuizzer'
        sSourceDirForQuiz = 'Resources/XML'

        self.oUtilsMsgs = UtilsMsgs()
        self.oFilesIO = UtilsIO()
        self.oFilesIO.SetModuleDirs(sModuleName, sSourceDirForQuiz)
        self.oFilesIO.SetUserDir()
        
        self.slicerMainLayout = self.layout
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        

        settings = qt.QSettings()
        settings.setValue('MainWindow/RestoreGeometry', 'true')

        
        
        self.qtQuizProgressWidget = qt.QTextEdit()
        #self.logic = ImageQuizzerLogic(self)
        self.slicerLeftWidget= None     
        
        
        slicer.util.setMenuBarsVisible(True)
#         slicer.util.setToolbarsVisible(False) # for live runs
        slicer.util.setToolbarsVisible(True) # while developing
        
#         # create button layout
#         self.CreateModuleButtons()

#         # create the ImageQuizzer widget 
#         self.oQuizWidgets = QuizWidgets()
# #         self.oQuizWidgets.CreateQuizzerLayout()
#         self.oQuizWidgets.CreateQuizzerLayoutWithTabs()
# 
# 
#         # add to Slicer's main layout
#         self.slicerLeftWidget = self.oQuizWidgets.GetSlicerLeftWidget()
#         self.layout.addWidget(self.slicerLeftWidget)  
              

        self.BuildUserLoginWidget()
        self.qUserLoginWidget.show()



        #-------------------------------------------
        # Connections
        #-------------------------------------------
#         self.btnShowQuizProgress.connect('clicked(bool)', self.onShowQuizProgressClicked)
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
    def BuildUserLoginWidget(self):
         
        # create the widget for user login
        # This is run in the constructor so that the widget remains in scope
        qUserLoginLayout = qt.QVBoxLayout()
        self.qUserLoginWidget = qt.QWidget()
        self.qUserLoginWidget.setLayout(qUserLoginLayout)
        qUserStudyWidgetTitle = qt.QLabel('Baines Image Quizzer - User Login')
        qUserLoginLayout.addWidget(qUserStudyWidgetTitle)
         
        
        ################################
        # Get/Create User folder
        ################################

        qUserLoginLayout.addSpacing(10) # Add vertical spacer
        qUserComboLabel = qt.QLabel('Select user name. If not shown, enter new name.')
        qUserLoginLayout.addWidget(qUserComboLabel)
        

        self.comboGetUserName = qt.QComboBox()
        self.comboGetUserName.setEditable(True)
        self.comboGetUserName.addItem('?') # default to special character to force user entry
        
        sUserSubfolders = [ f.name for f in os.scandir(self.oFilesIO.GetUserDir()) if f.is_dir() ]
        for sUserName in list(sUserSubfolders):
            self.comboGetUserName.addItem(sUserName)
        
        self.comboGetUserName.currentTextChanged.connect(self.onUserComboboxChanged)
        qUserLoginLayout.addWidget(self.comboGetUserName)

        
        # Add vertical spacer
        qUserLoginLayout.addSpacing(20)
         
        ################################
        # Get study button
        ################################
        # File Picker
        self.btnGetUserStudy = qt.QPushButton("Select Quiz")
        self.btnGetUserStudy.setEnabled(True)
        self.btnGetUserStudy.toolTip = "Select Quiz xml file for launch "
        self.btnGetUserStudy.connect('clicked(bool)', self.onApplyOpenFile)
        qUserLoginLayout.addWidget(self.btnGetUserStudy)
 
        self.qLblQuizFilename = qt.QLabel('Selected quiz filename')
        qUserLoginLayout.addWidget(self.qLblQuizFilename)
         
        # Add vertical spacer
        qUserLoginLayout.addSpacing(20)
         
        ################################
        # Launch study button (not enabled until study is picked)
        ################################

        self.btnLaunchStudy = qt.QPushButton("Launch Quiz")
        self.btnLaunchStudy.setEnabled(False)
        self.btnLaunchStudy.connect('clicked(bool)', self.onApplyLaunchQuiz)
        qUserLoginLayout.addWidget(self.btnLaunchStudy)
         
         
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def onUserComboboxChanged(self):
        
        # capture selected user name
        self.oFilesIO.SetQuizUsername(self.comboGetUserName.currentText)
     
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     
    def onApplyOpenFile(self):
        
        # set to default
        self.btnLaunchStudy.setEnabled(False)
        self.qLblQuizFilename.text = ""
 
        # get quiz filename
        self.quizInputFileDialog = qt.QFileDialog()
        sSelectedQuiz = self.quizInputFileDialog.getOpenFileName(self.qUserLoginWidget, "Open File", self.oFilesIO.GetXmlResourcesDir(), "XML files (*.xml)" )
 
        # check that file was selected
        if not sSelectedQuiz:
            sMsg = 'No quiz was selected'
            self.oUtilsMsgs.DisplayWarning(sMsg)
            self.qUserLoginWidget.raise_()

        else:
            # enable the launch button
            self.qLblQuizFilename.setText(sSelectedQuiz)
            self.btnLaunchStudy.setEnabled(True)
            self.qUserLoginWidget.show()
            self.qUserLoginWidget.activateWindow()
            
            self.oFilesIO.SetResourcesQuizPath(sSelectedQuiz)
         
 
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
    def onApplyLaunchQuiz(self):
        
        # confirm username was entered
        
        if (self.comboGetUserName.currentText == '' or self.comboGetUserName.currentText == '?'):
            sMsg = 'No user name was entered'
            self.oUtilsMsgs.DisplayWarning(sMsg)
            self.qUserLoginWidget.raise_()
            
        else:
            print(self.oFilesIO.GetQuizUsername())
            
            # copy file from Resource into user folder
            if self.oFilesIO.PopulateUserQuizFolder(): # success
                # start the session
#                 self.slicerLeftWidget.activateWindow()
#                 oSession = Session()
#                 oSession.RunSetup(self.oFilesIO, self.oQuizWidgets)


                oSession = Session()
                oSession.RunSetup(self.oFilesIO, self.slicerMainLayout)

                
                try:
                    #provide as much room as possible for the quiz
                    qDataProbeCollapsibleButton = slicer.util.mainWindow().findChild("QWidget","DataProbeCollapsibleWidget")
                    qDataProbeCollapsibleButton.collapsed = True
                    self.reloadCollapsibleButton.collapsed = True
                except:
                    pass
                
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CreateModuleButtons(self):

        self.qModuleBtnGrpBox = qt.QGroupBox()
        self.qModuleBtnGrpBoxLayout = qt.QHBoxLayout()
        self.qModuleBtnGrpBox.setLayout(self.qModuleBtnGrpBoxLayout)

        # Login button
        self.btnLogin = qt.QPushButton("Login")
        self.btnLogin.toolTip = "Login and select quiz"
        self.btnLogin.enabled = True
        self.btnLogin.connect('clicked(bool)', self.onLoginButtonClicked)
        
        # Quiz Button
        self.btnQuizzer = qt.QPushButton("Baines Image Quizzer")
        self.btnQuizzer.enabled = True
        self.btnQuizzer.connect('clicked(bool)', self.onQuizButtonClicked)
        
        # Segment Editor Button
        self.btnSegEditor = qt.QPushButton("Segment Editor")
        self.btnSegEditor.enabled = True
        self.btnSegEditor.connect('clicked(bool)', self.onSegEditorButtonClicked)

        self.qModuleBtnGrpBoxLayout.addWidget(self.btnLogin)
        self.qModuleBtnGrpBoxLayout.addSpacing(20)
        self.qModuleBtnGrpBoxLayout.addWidget(self.btnQuizzer)
        self.qModuleBtnGrpBoxLayout.addSpacing(20)
        self.qModuleBtnGrpBoxLayout.addWidget(self.btnSegEditor)

        self.layout.addWidget(self.qModuleBtnGrpBox)  

        
        
    def onLoginButtonClicked(self):
        self.qUserLoginWidget.show()
        self.qUserLoginWidget.raise_()

        
    def onQuizButtonClicked(self):
        self.oUtilsMsgs.DisplayInfo('Return to Quiz')
        slicer.util.selectModule('ImageQuizzer')
    
    def onSegEditorButtonClicked(self):
#         self.oUtilsMsgs.DisplayInfo('Start Segment Editor Module')
#         slicer.modules.segmenteditor.widgetRepresentation().show()
        slicer.util.selectModule('SegmentEditor')

    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onShowQuizProgressClicked(self):
        print('show progress')
#         self.qtQuizProgressWidget.setText(self.docHtmlStudies)
#         self.qtQuizProgressWidget.show()

    



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

 
 
# ##########################################################################
# #
# # class QuizWidgets
# #
# ##########################################################################
# 
# class QuizWidgets:
#     
#     def __init__(self,  parent=None):
#         self.sClassName = type(self).__name__
#         self.parent = parent
#         print('Constructor for QuizWidgets')
# 
#         self._slicerLeftMainLayout = None
#         self._slicerQuizLayout = None
#         self._slicerLeftWidget = None
#         self._slicerTabWidget = None
#         
#     def GetSlicerLeftMainLayout(self):
#         return self._slicerLeftMainLayout
# 
#     def GetSlicerQuizLayout(self):
#         return self._slicerQuizLayout
#     
#     def GetSlicerLeftWidget(self):
#         return self._slicerLeftWidget
#     
#     def GetSlicerTabWidget(self):
#         return self._slicerTabWidget
# 
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# #     def CreateQuizzerLayout(self):
# # 
# #         print ("-------ImageQuizzer Widget SetUp--------")
# # 
# #         #-------------------------------------------
# #         # set up quiz widget
# #         self._slicerLeftWidget = qt.QWidget()
# #         self._slicerLeftMainLayout = qt.QVBoxLayout()
# #         self._slicerLeftWidget.setLayout(self._slicerLeftMainLayout)
# #          
# #         
# #         
# #         # Status button
# #         self.btnShowQuizProgress = qt.QPushButton("Show Quiz Progress")
# #         self.btnShowQuizProgress.toolTip = "Display status of images."
# #         self.btnShowQuizProgress.enabled = True
# #         self._slicerLeftMainLayout.addWidget(self.btnShowQuizProgress)
# #         
# # 
# #         
# #         #-------------------------------------------
# #         # Collapsible button
# #         self.quizCollapsibleButton = ctk.ctkCollapsibleButton()
# #         self.quizCollapsibleButton.text = "Baines Image Quizzer"
# #         self._slicerLeftMainLayout.addWidget(self.quizCollapsibleButton)
# #         
# # 
# #         
# #         # Layout within the sample collapsible button - form needs a frame
# #         self._slicerQuizLayout = qt.QFormLayout(self.quizCollapsibleButton)
# #         self.quizFrame = qt.QFrame(self.quizCollapsibleButton)
# #         self.quizFrame.setLayout(qt.QVBoxLayout())
# #         self._slicerQuizLayout.addWidget(self.quizFrame)
# 
# 
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
#     def CreateQuizzerLayoutWithTabs(self):
# 
#         #-------------------------------------------
#         # set up quiz widget
# 
#         # create a layout for the quiz to go in Slicer's left widget
#         self._slicerLeftMainLayout = qt.QVBoxLayout()
#         
#         # add the quiz main layout to Slicer's left widget
#         self._slicerLeftWidget = qt.QWidget()
#         self._slicerLeftWidget.setLayout(self._slicerLeftMainLayout)
#         
#         qTitle = qt.QLabel('Baines Image Quizzer')
#         qTitle.setFont(qt.QFont('Arial',14, qt.QFont.Bold))
# 
#         self._slicerLeftMainLayout.addWidget(qTitle)
# 
#     
#         #-------------------------------------------
#         # setup the tab widget
#         self._slicerTabWidget = qt.QTabWidget()
#         qTabQuiz = qt.QWidget()
#         self._slicerTabWidget.addTab(qTabQuiz,"Quiz")
#         
#         # NOTE: Tab for segment editor is set up in Session - if a quiz question set requires it 
# 
#         self._slicerLeftMainLayout.addWidget(self._slicerTabWidget)
# 
#         
#         # Layout within the tab widget - form needs a frame
# 
#         self._slicerQuizLayout = qt.QFormLayout(qTabQuiz)
#         self.quizFrame = qt.QFrame(qTabQuiz)
#         self.quizFrame.setLayout(qt.QVBoxLayout())
#         self._slicerQuizLayout.addWidget(self.quizFrame)
# 


