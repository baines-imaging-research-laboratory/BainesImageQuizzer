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
#         self.oFilesIO.SetUserDir()

#         # capture Slicer's default database location
#         self.oFilesIO.SetDefaultDatabaseDir(slicer.dicomDatabase.databaseDirectory)
        
        
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
        
##########################################################
# --------TESTING A LAYOUT CHANGE ----------
#         # create button layout
#         self.CreateModuleButtons()
##########################################################


        self.BuildUserLoginWidget()
        self.qUserLoginWidget.show()



        #-------------------------------------------
        # Connections (Not yet implemented)
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
        # Get Database location
        ################################
        
        
        qUserLoginLayout.addSpacing(20)

        qDBGrpBox = qt.QGroupBox()
        qDBGrpBox.setTitle('1. Select data location')
        qDBGrpBoxLayout = qt.QVBoxLayout()
        qDBGrpBox.setLayout(qDBGrpBoxLayout)

        qUserLoginLayout.addWidget(qDBGrpBox)

#         btnUseDefaultDB = qt.QPushButton("Use default database location")
#         btnUseDefaultDB.setEnabled(True)
#         btnUseDefaultDB.toolTip = "Slicer's default database location will be used."
#         btnUseDefaultDB.connect('clicked(bool)', self.onApplyUseDefaultDB)
#         qDBGrpBoxLayout.addWidget(btnUseDefaultDB)
# 
#         
#         qDBGrpBoxLayout.addSpacing(10)

        
        btnGetDBLocation = qt.QPushButton("Define location for Image Quizzer data")
        btnGetDBLocation.setEnabled(True)
        btnGetDBLocation.toolTip = "Select folder for Image Quizzer data."
        btnGetDBLocation.connect('clicked(bool)', self.onApplyQuizzerDataLocation)
        qDBGrpBoxLayout.addWidget(btnGetDBLocation)
 
        self.qLblDBLocation = qt.QLabel('Selected data location')
        qUserLoginLayout.addWidget(self.qLblDBLocation)

        
        # Add vertical spacer
        qUserLoginLayout.addSpacing(20)
        
        
        
        ################################
        # Get/Create User folder
        ################################

        qUserLoginLayout.addSpacing(10) # Add vertical spacer

        self.qUserGrpBox = qt.QGroupBox()
        self.qUserGrpBox.setTitle('2. Enter / select user name')
        self.qUserGrpBoxLayout = qt.QVBoxLayout()
        self.qUserGrpBox.setLayout(self.qUserGrpBoxLayout)
        self.qUserGrpBox.setEnabled(False)

        qUserLoginLayout.addWidget(self.qUserGrpBox)

        
        qUserComboLabel = qt.QLabel('Use drop down. If not shown, replace ? with your name.')
        self.qUserGrpBoxLayout.addWidget(qUserComboLabel)
        

        self.comboGetUserName = qt.QComboBox()
        self.comboGetUserName.setEditable(True)
        self.comboGetUserName.addItem('?') # default to special character to force user entry
        
#         sUserSubfolders = [ f.name for f in os.scandir(self.oFilesIO.GetUserDir()) if f.is_dir() ]
#         for sUserName in list(sUserSubfolders):
#             self.comboGetUserName.addItem(sUserName)
        
        self.comboGetUserName.currentTextChanged.connect(self.onUserComboboxChanged)
        self.qUserGrpBoxLayout.addWidget(self.comboGetUserName)

        
        # Add vertical spacer
        self.qUserGrpBoxLayout.addSpacing(10)
         
        ################################
        # Get study button
        ################################
        # File Picker
        self.btnGetUserStudy = qt.QPushButton("Select quiz:")
        self.btnGetUserStudy.setEnabled(True)
        self.btnGetUserStudy.toolTip = "Select Quiz xml file for launch "
        self.btnGetUserStudy.connect('clicked(bool)', self.onApplyOpenFile)
        self.qUserGrpBoxLayout.addWidget(self.btnGetUserStudy)
 
        self.qLblQuizFilename = qt.QLabel('Selected quiz filename')
        self.qUserGrpBoxLayout.addWidget(self.qLblQuizFilename)
         
        # Add vertical spacer
        qUserLoginLayout.addSpacing(20)
         
        ################################
        # Launch study button (not enabled until study is picked)
        ################################
        
        self.qLaunchGrpBox = qt.QGroupBox()
        self.qLaunchGrpBox.setTitle('3. Launch Quiz')
        self.qLaunchGrpBoxLayout = qt.QHBoxLayout()
        self.qLaunchGrpBox.setLayout(self.qLaunchGrpBoxLayout)
        self.qLaunchGrpBox.setEnabled(False)

        qUserLoginLayout.addWidget(self.qLaunchGrpBox)
 
 
        self.btnLaunchStudy = qt.QPushButton("Begin")
#         self.btnLaunchStudy.setEnabled(False)
        self.btnLaunchStudy.connect('clicked(bool)', self.onApplyLaunchQuiz)
        self.qLaunchGrpBoxLayout.addWidget(self.btnLaunchStudy)
         
         
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def onUserComboboxChanged(self):
        
        # capture selected user name
        self.oFilesIO.SetUsername(self.comboGetUserName.currentText)
        
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#      
#     def onApplyUseDefaultDB(self):
#         
#         # assign default DB location (captured on initialization)
#         self.oFilesIO.SetDatabaseDir(self.oFilesIO.GetDefaultDatabaseDir())
# 
#         # complete the setup for the user's name and quiz selection
#         self.CompleteDBAndUserSetup()
#        
#         ##### for debug... #####
#         self.oFilesIO.PrintDirLocations()
#         ########################
# 
#         self.qUserLoginWidget.raise_()
      
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def onApplyQuizzerDataLocation(self):
        
        # File Picker
        self.qDBLocationFileDialog = qt.QFileDialog()
        sDefaultWorkingDir = os.path.expanduser('~\Documents')
        sDataLocation = self.qDBLocationFileDialog.getExistingDirectory(None, "Select Directory", sDefaultWorkingDir, qt.QFileDialog.ShowDirsOnly )
        
        
        self.oFilesIO.SetupUserAndDataDirs(sDataLocation)
        
        
        sUserSubfolders = [ f.name for f in os.scandir(self.oFilesIO.GetUsersParentDir()) if f.is_dir() ]
        for sUserName in list(sUserSubfolders):
            self.comboGetUserName.addItem(sUserName)

        self.qUserGrpBox.setEnabled(True)

        
        ##### for debug... #####
        print('Setup data folders')
        self.oFilesIO.PrintDirLocations()
        ########################
        
        # confirm db is populated
        
        
        # if not populated, display warning message to have admin do this
        sMsg = 'Database does not have pre-stored images. Continue?'
        qtAns = self.oUtilsMsgs.DisplayYesNo(sMsg)
        if qtAns == qt.QMessageBox.Yes:
            self.oUtilsMsgs.DisplayWarning('Quiz will import images (progress may be slower).')
        else:
            self.oUtilsMsgs.DisplayError('Contact administrator to preload images into database.')
            slicer.util.exit(status=EXIT_SUCCESS)

        
        self.qUserLoginWidget.raise_()
        
        
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#         
#     def CompleteDBAndUserSetup(self):
# 
#         self.qLblDataLocation.setText(self.oFilesIO.GetDataParentDir())
#         
#         self.oFilesIO.SetDICOMDatabaseDir(self.oFilesIO.GetDataParentDir() + '\SlicerDICOMDatabase')
#         
#         self.oFilesIO.SetUserDir(self.oFilesIO.GetDataParentDir() + 'Users')
# 
#         
#         self.oFilesIO.SetUserDir(self.oFilesIO.GetDatabaseParentDir())
#         sUserSubfolders = [ f.name for f in os.scandir(self.oFilesIO.GetUserDir()) if f.is_dir() ]
#         for sUserName in list(sUserSubfolders):
#             self.comboGetUserName.addItem(sUserName)
# 
#         self.qUserGrpBox.setEnabled(True)
#         
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
    def onApplyOpenFile(self):
        
        # set to default
#         self.btnLaunchStudy.setEnabled(False)
        self.qLaunchGrpBox.setEnabled(True)
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
#             self.btnLaunchStudy.setEnabled(True)
            self.qLaunchGrpBox.setEnabled(True)
            self.qUserLoginWidget.show()
            self.qUserLoginWidget.activateWindow()
            
            self.oFilesIO.SetResourcesQuizPath(sSelectedQuiz)
         
 
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
    def onApplyLaunchQuiz(self):
        
        # confirm username was entered

        if (self.comboGetUserName.currentText == '' or self.comboGetUserName.currentText == '?' or "?" in self.comboGetUserName.currentText):
            sMsg = 'No user or invalid name was entered'
            self.oUtilsMsgs.DisplayWarning(sMsg)
            self.qUserLoginWidget.raise_()

            # open the database - if not successful, allow user to reselect
            bDBSetupSuccess, sMsg = self.oFilesIO.OpenSelectedDatabase()

            if not bDBSetupSuccess:
                self.oUtilsMsgs.DisplayWarning(sMsg)
                self.qUserLoginWidget.raise_()
                
                 
            
        else:

            ##### for debug... #####
            self.oFilesIO.PrintDirLocations()
            ########################

            # create user folder if it doesn't exist
            self.oFilesIO.SetUserDir()

            # copy file from Resource into user folder
            if self.oFilesIO.PopulateUserQuizFolder(): # success

                # start the session
                oSession = Session()
                oSession.RunSetup(self.oFilesIO, self.slicerMainLayout)

                
                try:
                    #provide as much room as possible for the quiz
                    qDataProbeCollapsibleButton = slicer.util.mainWindow().findChild("QWidget","DataProbeCollapsibleWidget")
                    qDataProbeCollapsibleButton.collapsed = True
                    self.reloadCollapsibleButton.collapsed = True
                except:
                    pass
                
#########################################################
#    NOTE: This would be good if I could load these buttons onto the 
#        Slicer's main layout so they would exist if the user drifted
#        off the quiz module
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def CreateModuleButtons(self):
# 
#         self.qModuleBtnGrpBox = qt.QGroupBox()
#         self.qModuleBtnGrpBoxLayout = qt.QHBoxLayout()
#         self.qModuleBtnGrpBox.setLayout(self.qModuleBtnGrpBoxLayout)
# 
#         # Login button
#         self.btnLogin = qt.QPushButton("Login")
#         self.btnLogin.toolTip = "Login and select quiz"
#         self.btnLogin.enabled = True
#         self.btnLogin.connect('clicked(bool)', self.onLoginButtonClicked)
#          
#         # Quiz Button
#         self.btnQuizzer = qt.QPushButton("Baines Image Quizzer")
#         self.btnQuizzer.enabled = True
#         self.btnQuizzer.connect('clicked(bool)', self.onQuizButtonClicked)
#          
#         # Segment Editor Button
#         self.btnSegEditor = qt.QPushButton("Segment Editor")
#         self.btnSegEditor.enabled = True
#         self.btnSegEditor.connect('clicked(bool)', self.onSegEditorButtonClicked)
#  
#         self.qModuleBtnGrpBoxLayout.addWidget(self.btnLogin)
#         self.qModuleBtnGrpBoxLayout.addSpacing(20)
#         self.qModuleBtnGrpBoxLayout.addWidget(self.btnQuizzer)
#         self.qModuleBtnGrpBoxLayout.addSpacing(20)
#         self.qModuleBtnGrpBoxLayout.addWidget(self.btnSegEditor)
#  
#         self.layout.addWidget(self.qModuleBtnGrpBox)  
# 
# 
# ############################################################
       
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

 
 


