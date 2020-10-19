import os
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from Session import *
from pip._vendor.distlib._backport.shutil import copyfile
from slicer.util import findChild

from Utilities import *


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

#         # capture Slicer's default database location
#         self.oFilesIO.SetDefaultDatabaseDir(slicer.dicomDatabase.databaseDirectory)


        # comes after confirmation
#         slicer.app.aboutToQuit.connect(self.myCloseEvent)  # comes after confirmation

        # comes after confirmation  - endless loop unless you do a specific exit in the close module
#         slicer.app.moduleManager().connect('moduleAboutToBeUnloaded(QString)', self.myCloseEvent)

#         oMainWindow = SlicerMainWindowForClose()

        self.customEventFilter = customEventFilter()
#         slicer.app.installEventFilter(self.customEventFilter)
        slicer.util.mainWindow().installEventFilter(self.customEventFilter)        
        
        
        self.slicerMainLayout = self.layout
        
#     def myCloseEvent(self):
#         self.oUtilsMsgs.DisplayInfo('***** Closing *****')

    def __del__(self):
        slicer.util.mainWindow().removeEventFilter(self.customEventFilter)
 

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


        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
    def BuildUserLoginWidget(self):
         
        # create the widget for user login
        # This is run in the constructor so that the widget remains in scope
        qUserLoginLayout = qt.QVBoxLayout()
        self.qUserLoginWidget = qt.QWidget()
        self.qUserLoginWidget.setLayout(qUserLoginLayout)
         

        qTitleGroupBox = qt.QGroupBox()
        qTitleGroupBoxLayout = qt.QHBoxLayout()
        qTitleGroupBox.setLayout(qTitleGroupBoxLayout)
                                
        qLogoImg = qt.QLabel(self)
#         sLogoName = 'BainesChevrons.png'
        sLogoName = 'BainesLogoSmall.png'
        sLogoPath = os.path.join(self.oFilesIO.GetScriptedModulesPath(),'Resources','Icons',sLogoName)
        pixmap = qt.QPixmap(sLogoPath)
        qLogoImg.setPixmap(pixmap)
#         qLogoImg.setAlignment(QtCore.Qt.AlignRight)
        qLogoImg.setAlignment(QtCore.Qt.AlignLeft)

        qTitle = qt.QLabel('Image Quizzer - User Login')
        qTitle.setFont(qt.QFont('Arial',12, qt.QFont.Bold))
        qTitle.setAlignment(QtCore.Qt.AlignVCenter)

        qTitleGroupBoxLayout.addWidget(qLogoImg)
        qTitleGroupBoxLayout.addWidget(qTitle)
        
        qUserLoginLayout.addWidget(qTitleGroupBox)
        
        
        ################################
        # Get Database location
        ################################
        
        
        qUserLoginLayout.addSpacing(20)

        qDBGrpBox = qt.QGroupBox()
        qDBGrpBox.setTitle('1. Select data location')
        qDBGrpBoxLayout = qt.QVBoxLayout()
        qDBGrpBox.setLayout(qDBGrpBoxLayout)

        qUserLoginLayout.addWidget(qDBGrpBox)

        
        btnGetDBLocation = qt.QPushButton("Define location for Image Quizzer data")
        btnGetDBLocation.setStyleSheet("QPushButton{ background-color: rgb(0,179,246) }")
        btnGetDBLocation.setEnabled(True)
        btnGetDBLocation.toolTip = "Select folder for Image Quizzer data."
        btnGetDBLocation.connect('clicked(bool)', self.onApplyQuizzerDataLocation)
        qDBGrpBoxLayout.addWidget(btnGetDBLocation)
 
        self.qLblDataLocation = qt.QLabel('Selected data location:')
        qUserLoginLayout.addWidget(self.qLblDataLocation)

        
        # Add vertical spacer
        qUserLoginLayout.addSpacing(10)
        
        
        
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
        self.comboGetUserName.setStyleSheet("QComboBox{ background-color: rgba(0,179,246,.9) }")
        
        self.comboGetUserName.setEditable(True)
        self.comboGetUserName.addItem('?') # default to special character to force user entry
        
        self.comboGetUserName.currentTextChanged.connect(self.onUserComboboxChanged)
        self.qUserGrpBoxLayout.addWidget(self.comboGetUserName)

        
        # Add vertical spacer
        self.qUserGrpBoxLayout.addSpacing(20)
         
        ################################
        # Get study button
        ################################
        
        self.qQuizSelectionGrpBox = qt.QGroupBox()
        self.qQuizSelectionGrpBox.setTitle('3. Select Quiz')
        self.qQuizSelectionGrpBoxLayout = qt.QVBoxLayout()
        self.qQuizSelectionGrpBox.setLayout(self.qQuizSelectionGrpBoxLayout)
        self.qQuizSelectionGrpBox.setEnabled(False)
        
        # File Picker
        self.btnGetUserStudy = qt.QPushButton("Choose quiz to launch")
        self.btnGetUserStudy.setStyleSheet("QPushButton{ background-color: rgb(0,179,246) }")
        self.btnGetUserStudy.setEnabled(True)
        self.btnGetUserStudy.toolTip = "Select Quiz xml file for launch "
        self.btnGetUserStudy.connect('clicked(bool)', self.onApplyQuizSelection)
        self.qQuizSelectionGrpBoxLayout.addWidget(self.btnGetUserStudy)
 
        self.qLblQuizFilename = qt.QLabel('Selected quiz filename')
        self.qQuizSelectionGrpBoxLayout.addWidget(self.qLblQuizFilename)
        
        qUserLoginLayout.addWidget(self.qQuizSelectionGrpBox)
        
        
        # Add vertical spacer
        qUserLoginLayout.addSpacing(20)
         
        ################################
        # Launch study button (not enabled until study is picked)
        ################################
        
        self.qLaunchGrpBox = qt.QGroupBox()
        self.qLaunchGrpBox.setTitle('4. Launch Quiz')
        self.qLaunchGrpBoxLayout = qt.QHBoxLayout()
        self.qLaunchGrpBox.setLayout(self.qLaunchGrpBoxLayout)
        self.qLaunchGrpBox.setEnabled(False)

        qUserLoginLayout.addWidget(self.qLaunchGrpBox)
 
 
        self.btnLaunchStudy = qt.QPushButton("Begin")
        self.btnLaunchStudy.setStyleSheet("QPushButton{ background-color: rgb(0,179,246) }")
        self.btnLaunchStudy.connect('clicked(bool)', self.onApplyLaunchQuiz)
        self.qLaunchGrpBoxLayout.addWidget(self.btnLaunchStudy)
         
         
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def onUserComboboxChanged(self):
        
        # capture selected user name
        self.oFilesIO.SetUsernameAndDir(self.comboGetUserName.currentText)
        self.qQuizSelectionGrpBox.setEnabled(True)
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def onApplyQuizzerDataLocation(self):
        
        # File Picker
        self.qDBLocationFileDialog = qt.QFileDialog()
        sDefaultWorkingDir = os.path.expanduser('~\Documents')
        sDataLocation = self.qDBLocationFileDialog.getExistingDirectory(None, "Select Directory", sDefaultWorkingDir, qt.QFileDialog.ShowDirsOnly )
        
        
        self.oFilesIO.SetupUserAndDataDirs(sDataLocation)
        
        self.qLblDataLocation.setText(self.oFilesIO.GetDataParentDir())
        
        sUserSubfolders = [ f.name for f in os.scandir(self.oFilesIO.GetUsersParentDir()) if f.is_dir() ]
        for sUserName in list(sUserSubfolders):
            self.comboGetUserName.addItem(sUserName)

        self.qUserGrpBox.setEnabled(True)

        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
    def onApplyQuizSelection(self):
        
        # set to default
#         self.btnLaunchStudy.setEnabled(False)
        self.qLaunchGrpBox.setEnabled(True)
        self.qLblQuizFilename.text = ""
 
        # get quiz filename
        self.quizInputFileDialog = qt.QFileDialog()
        sSelectedQuizPath = self.quizInputFileDialog.getOpenFileName(self.qUserLoginWidget, "Open File", self.oFilesIO.GetXmlResourcesDir(), "XML files (*.xml)" )
 
        # check that file was selected
        if not sSelectedQuizPath:
            sMsg = 'No quiz was selected'
            self.oUtilsMsgs.DisplayWarning(sMsg)
            self.qUserLoginWidget.raise_()

        else:
            # enable the launch button
            self.qLblQuizFilename.setText(sSelectedQuizPath)
#             self.btnLaunchStudy.setEnabled(True)
            self.qLaunchGrpBox.setEnabled(True)
            self.qUserLoginWidget.show()
            self.qUserLoginWidget.activateWindow()
            
            self.oFilesIO.SetResourcesQuizPathAndFilename(sSelectedQuizPath)
         
 
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
    def onApplyLaunchQuiz(self):
        
        # open the database - if not successful, allow user to reselect
        bDBSetupSuccess, sMsg = self.oFilesIO.OpenSelectedDatabase()

        if not bDBSetupSuccess:
            self.oUtilsMsgs.DisplayWarning(sMsg)
            self.qUserLoginWidget.raise_()

        else:
            
            # confirm username was entered
            if (self.comboGetUserName.currentText == '' or self.comboGetUserName.currentText == '?' or "?" in self.comboGetUserName.currentText):
                sMsg = 'No user or invalid name was entered'
                self.oUtilsMsgs.DisplayWarning(sMsg)
                self.qUserLoginWidget.raise_()
    
            else:
                self.oFilesIO.SetUsernameAndDir(self.comboGetUserName.currentText)

                # create user and results folders if it doesn't exist
                self.oFilesIO.SetupForUserQuizResults()

                ##### for debug... #####
                self.oFilesIO.PrintDirLocations()
                ########################
    
    
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
#        
#     def onLoginButtonClicked(self):
#         self.qUserLoginWidget.show()
#         self.qUserLoginWidget.raise_()
# 
#         
#     def onQuizButtonClicked(self):
#         self.oUtilsMsgs.DisplayInfo('Return to Quiz')
#         slicer.util.selectModule('ImageQuizzer')
#     
#     def onSegEditorButtonClicked(self):
# #         self.oUtilsMsgs.DisplayInfo('Start Segment Editor Module')
# #         slicer.modules.segmenteditor.widgetRepresentation().show()
#         slicer.util.selectModule('SegmentEditor')

    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



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
# # SlicerMainWindowForClose
# #
# ##########################################################################
# 
# class SlicerMainWindowForClose(qSlicerMainWindow):
# 
#     def __init__(self, parent=None):
#         qSlicerMainWindow.__init__(self,parent)
#         print('***** MyMainWindow *****')
#         
#     def closeEvent(self, event):
#         
#         self.oUtilsMsgs.DisplayInfo('**** Closing MyMainWindow ****')
#         event.accept()        
# 
# 
#     def on_FileExitAction_triggered(self):
#         
#         self.oUtilsMsgs.DisplayInfo('**** Closing MyMainWindow FileExitAction****')
# 
# 
#     def confirmCloseApplication(self, event):
#         
#         self.oUtilsMsgs.DisplayInfo('**** Closing MyMainWindow ****')
# #         event.accept()        


##########################################################################
#
# CustomEventFilter
#
##########################################################################
class customEventFilter(qt.QObject):
    """ Custom event filter set up to capture when the user presses the 'X'
        button on the main window to exit the application
        
        Note: you can't have a constructor here
    """
    
    def eventFilter(self, obj, event):
        
        self.oFilesIO = UtilsIO()
        self.oIOXml = UtilsIOXml()
        self.oUtilsMsgs = UtilsMsgs()
        
        if event.type() == qt.QEvent.Close:
            print('type: ', event.type())
            print('closeEvent: ', qt.QEvent.Close)

            qtAns = self.oUtilsMsgs.DisplayOkCancel('Image Quizzer Exiting \n Results will be saved. \n Restarting the quiz will resume where you left off.')
            if qtAns == qt.QMessageBox.Ok:
                sUserQuizResultsPath = self.oFilesIO.GetUserQuizResultsPath()
                if not sUserQuizResultsPath == '':
                    self.oIOXml.SaveXml(sUserQuizResultsPath)
                slicer.util.exit(status=EXIT_SUCCESS)
            else:
                if qtAns == qt.QMessageBox.Cancel:
                    self.oUtilsMsgs.DisplayWarning('The Sicer application confirmation will follow. \nSelect Slicer option: "Cancel exit" to return or "Exit (Discard modifications)" to exit')
     

