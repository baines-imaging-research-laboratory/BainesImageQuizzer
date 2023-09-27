import os
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from Session import *
from pip._vendor.distlib._backport.shutil import copyfile
from slicer.util import findChild

from Utilities.UtilsMsgs import *
from Utilities.UtilsFilesIO import *

import importlib.util

from slicer import qSlicerMainWindow #for custom eventFilter
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

        self.oUtilsMsgs = UtilsMsgs()
        self.oFilesIO = UtilsFilesIO()
        self.oFilesIO.SetModuleDirs(sModuleName)
        
        # previous and current release dates
        # Note: Version 1.0 should be used with Slicer v4.11.20200930
        # self.sVersion = "Image Quizzer   v1.0 "  #  Release Date: May 10, 2022
        # Note: Version 2.0 should be used with Slicer v4.11.2021022
        self.sVersion = "Image Quizzer v2.3.1" 

        sSlicerVersion = slicer.app.applicationVersion
        if sSlicerVersion != '4.11.20210226':
            sMsg = 'This version of Image Quizzer requires 3D Slicer v4.11.20210226' +\
                    '\n You are running 3D Slicer v' + sSlicerVersion
            self.oUtilsMsgs.DisplayError(sMsg)


#         # capture Slicer's default database location
#         self.oFilesIO.SetDefaultDatabaseDir(slicer.dicomDatabase.databaseDirectory)


#         self.oCustomEventFilter = customEventFilter()
#         slicer.util.mainWindow().installEventFilter(self.oCustomEventFilter)        
         
        
        self.slicerMainLayout = self.layout
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __del__(self):
        
        # unhide Slicer's default toolbars
        for qtToolBar in slicer.util.mainWindow().findChildren('QToolBar'):
            if qtToolBar.name in self.lsModulesToToggleVisibilty:
                qtToolBar.setVisible(True)

        slicer.util.mainWindow().removeEventFilter(self.customEventFilter)
  

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        

        settings = qt.QSettings()
        settings.setValue('MainWindow/RestoreGeometry', 'true')

        
        
        self.qtQuizProgressWidget = qt.QTextEdit()
        #self.logic = ImageQuizzerLogic(self)
        self.slicerLeftWidget= None     
        
        
        
# ##########  For Development mode    ###########    
#         slicer.util.setPythonConsoleVisible(True)
#         slicer.util.setToolbarsVisible(True)
#         slicer.util.setMenuBarsVisible(True)
# ##########


###########  For Release mode   ###########
        # hide toolbars to prevent users accessing modules outside of the ImageQuizzer
        #    Equivalent to toggling through View>Toolbars
        #    'ModuleToolBar' includes the Editor module for segmenting
        #    'DialogToolBar' for Extensions
        #    'MainToolBar' for loading files by Data, Dcm buttons
        #    'ModuleSelectorToolBar' to see all the available modules
        #    'ViewersToolBar' to see crosshair options
        #    'ViewsToolBar' for different view layouts
        #    'MouseModeToolBar' for default, window/level, markups tools
          
        self.lsModulesToToggleVisibilty = ['ModuleToolBar', 'DialogToolBar', 'CaptureToolBar', 'MainToolBar',\
                                            'ModuleSelectorToolBar', 'MouseModeToolBar', 'ViewToolBar', 'ViewersToolBar']
  
        for qtToolBar in slicer.util.mainWindow().findChildren('QToolBar'):
            if qtToolBar.name in self.lsModulesToToggleVisibilty:
                qtToolBar.setVisible(False)
  
  
        slicer.util.setModuleHelpSectionVisible(False)
        slicer.modules.welcome.widgetRepresentation().setVisible(False)
        
        slicer.util.mainWindow().showMaximized()
###########
        


        self.oSession = Session()                    
        self.oCustomEventFilter = customEventFilter(self.oSession, self.oFilesIO)
        slicer.util.mainWindow().installEventFilter(self.oCustomEventFilter)        


        self.BuildUserLoginWidget()
        self.qUserLoginWidget.show()
        


        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def BuildUserLoginWidget(self):
         
        # create the widget for user login
        # This is run in the constructor so that the widget remains in scope
        qUserLoginLayout = qt.QVBoxLayout()
        self.qUserLoginWidget = qt.QWidget()
        self.qUserLoginWidget.setLayout(qUserLoginLayout)
        self.qUserLoginWidget.setWindowModality(2)
        self.qUserLoginWidget.setWindowTitle(self.sVersion)
         

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
        
        
        qUserLoginLayout.addSpacing(10)

        qDBGrpBox = qt.QGroupBox()
        qDBGrpBox.setTitle('1. Select data location')
        qDBGrpBoxLayout = qt.QVBoxLayout()
        qDBGrpBox.setLayout(qDBGrpBoxLayout)

        qUserLoginLayout.addWidget(qDBGrpBox)

        
        btnGetDBLocation = qt.QPushButton("Define location for Image Quizzer data")
        btnGetDBLocation.setStyleSheet("QPushButton{ background-color: rgb(0,179,246); color: black }")
        btnGetDBLocation.setEnabled(True)
        btnGetDBLocation.toolTip = "Select folder for Image Quizzer data."
        btnGetDBLocation.connect('clicked(bool)', self.onApplyQuizzerDataLocation)
        qDBGrpBoxLayout.addWidget(btnGetDBLocation)
 
        self.qLblDataLocation = qt.QLabel('Selected data location:')
        qDBGrpBoxLayout.addWidget(self.qLblDataLocation)


        # Add vertical spacer
        qUserLoginLayout.addSpacing(10)
        
        ################################
        # Define User name 
        ################################
 
        # NOTE: User name must be after database location selection for dropdown list to be populated
        
        self.qUserGrpBox = qt.QGroupBox()
        self.qUserGrpBox.setTitle('User name')
        self.qUserGrpBoxLayout = qt.QVBoxLayout()
        self.qUserGrpBox.setLayout(self.qUserGrpBoxLayout)

        self.comboGetUserName = qt.QComboBox()
        self.comboGetUserName.addItem(os.getlogin())
        self.comboGetUserName.currentTextChanged.connect(self.onUserComboboxChanged)
        self.comboGetUserName.setEditable(True)

        self.qUserGrpBoxLayout.addWidget(self.comboGetUserName)
        self.qUserGrpBox.setEnabled(False)

        qUserLoginLayout.addWidget(self.qUserGrpBox)
        
        # Add vertical spacer
        qUserLoginLayout.addSpacing(10)
        
        ################################
        # Get study button
        ################################
        
        self.qQuizSelectionGrpBox = qt.QGroupBox()
        self.qQuizSelectionGrpBox.setTitle('2. Select Quiz')
        self.qQuizSelectionGrpBoxLayout = qt.QVBoxLayout()
        self.qQuizSelectionGrpBox.setLayout(self.qQuizSelectionGrpBoxLayout)
        self.qQuizSelectionGrpBox.setEnabled(False)
        
        # File Picker
        self.btnGetUserStudy = qt.QPushButton("Choose quiz to launch")
        self.btnGetUserStudy.setStyleSheet("QPushButton{ background-color: rgb(0,179,246); color: black }")
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
        self.qLaunchGrpBox.setTitle('3. Launch Quiz')
        self.qLaunchGrpBoxLayout = qt.QHBoxLayout()
        self.qLaunchGrpBox.setLayout(self.qLaunchGrpBoxLayout)
        self.qLaunchGrpBox.setEnabled(False)

        qUserLoginLayout.addWidget(self.qLaunchGrpBox)
 
 
        self.btnLaunchStudy = qt.QPushButton("Begin")
        self.btnLaunchStudy.setStyleSheet("QPushButton{ background-color: rgb(0,179,246); color: black }")
        self.btnLaunchStudy.connect('clicked(bool)', self.onApplyLaunchQuiz)
        self.qLaunchGrpBoxLayout.addWidget(self.btnLaunchStudy)
         
         
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onUserComboboxChanged(self):
        
        # capture selected user name
        self.oFilesIO.SetQuizUsername(self.comboGetUserName.currentText)
     
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def onApplyQuizzerDataLocation(self):
        
        # File Picker
        self.qDBLocationFileDialog = qt.QFileDialog()
        sDefaultDataDir = os.path.join(self.oFilesIO.GetScriptedModulesPath(), 'Inputs','Images')
        sDataLocation = self.qDBLocationFileDialog.getExistingDirectory(None, "SELECT DIRECTORY FOR IMAGE DATABASE", sDefaultDataDir,  qt.QFileDialog.ShowDirsOnly )
        
        if sDataLocation != '':
            self.oFilesIO.SetDataParentDir(sDataLocation)
       
            self.qLblDataLocation.setText(self.oFilesIO.GetDataParentDir())
            self.qQuizSelectionGrpBox.setEnabled(True)
            self.qUserGrpBox.setEnabled(True)
            
            self.oFilesIO.SetupOutputDirs()  # dirs in UserResults folder will populate User names
            
            # populate user name list in combo box
            sUsersParentDir = self.oFilesIO.GetUsersParentDir()
            lSubFolders = [f.name for f in os.scandir(sUsersParentDir) if f.is_dir()]
            
            if os.getlogin() in lSubFolders:
                lSubFolders.remove(os.getlogin())
                
            lCurrentItems = []
            for i in range(self.comboGetUserName.count):
                lCurrentItems.append(self.comboGetUserName.itemText(i))
            for sSubFolder in lSubFolders:
                if sSubFolder not in lCurrentItems:
                    self.comboGetUserName.addItem(sSubFolder)
            
        else:
            sMsg = 'No location was selected for image database'
            self.oUtilsMsgs.DisplayWarning(sMsg)
            self.qUserLoginWidget.raise_()
            
                
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onApplyQuizSelection(self):
        
        # set to default
        self.qLaunchGrpBox.setEnabled(True)
        self.qLblQuizFilename.text = ""
 
        # get quiz filename
        self.quizInputFileDialog = qt.QFileDialog()
        sSelectedQuizPath = self.quizInputFileDialog.getOpenFileName(self.qUserLoginWidget, "SELECT QUIZ FILE", self.oFilesIO.GetXmlQuizDir(), "XML files (*.xml)" )
 
        # check that file was selected
        if not sSelectedQuizPath:
            sMsg = 'No quiz was selected'
            self.oUtilsMsgs.DisplayWarning(sMsg)
            self.qUserLoginWidget.raise_()

        else:
            # enable the launch button
            self.qLblQuizFilename.setText(sSelectedQuizPath)
            self.qLaunchGrpBox.setEnabled(True)
            self.qUserLoginWidget.show()
            self.qUserLoginWidget.activateWindow()
            
            self.oFilesIO.SetXmlQuizPathAndFilename(sSelectedQuizPath)
         
 
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onApplyLaunchQuiz(self):
        
        sMsg = ''
        bSuccess = True

            
        self.oFilesIO.SetUsernameAndDir(self.comboGetUserName.currentText)


            
        # check for errors in quiz xml layout before populating the user response folder
        bQuizValidated, sMsg = self.oFilesIO.ValidateQuiz()
    

        if bQuizValidated:
            # create user and results folders if it doesn't exist
            self.oFilesIO.SetupForUserQuizResults()

            ##### for debug... #####
            #self.oFilesIO.PrintDirLocations()
            ########################
            
            
            sMissingFiles = self.oFilesIO.ValidateDatabaseLocation()
            if sMissingFiles != '':
                sMsgMissigFiles = 'Database images are missing. ' + sMissingFiles \
                                + '\nReselect the proper database location or contact your administrator.'
                self.oUtilsMsgs.DisplayWarning(sMsgMissigFiles)
                self.qUserLoginWidget.raise_()
    
            else:
    
    
                # copy file from Resource into user folder
                if self.oFilesIO.PopulateUserQuizFolder(): # success
    
                    # turn off login widget modality (hide first)
                    self.qUserLoginWidget.hide()
                    self.qUserLoginWidget.setWindowModality(0)
                    self.qUserLoginWidget.show()
                    
                    # start the session
                    self.oSession.RunSetup(self.oFilesIO, self.slicerMainLayout)
    
        else:
            self.oUtilsMsgs.DisplayError(sMsg)

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


##########################################################################
#
# customEventFilter
#
##########################################################################
 
class customEventFilter(qt.QObject):
    """ Custom event filter set up to capture when the user presses the 'X'
        button on the main window to exit the application.
    """
     
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, oSession, oFilesIO):
        qSlicerMainWindow.__init__(self) # required for event filter
        
        self.oSession = oSession
        self.oFilesIO = oFilesIO
     
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def eventFilter(self, obj, event):
        ''' Function to save current data if the user presses Slicer's 'X' 
            to exit the quiz.
        '''
         
        self.oUtilsMsgs = UtilsMsgs()
        if event.type() == qt.QEvent.Close:
            
            sExitMsg = 'Image Quizzer Exiting'
            sUserQuizResultsPath = self.oFilesIO.GetUserQuizResultsPath()
            
            if sUserQuizResultsPath != '':
                sExitMsg = sExitMsg + '\n   Results will be saved.\
                    \n   Restarting the quiz will resume where you left off.'
                
                sCaller = 'EventFilter'
                bSuccess, sMsg = self.oSession.PerformSave(sCaller)
                if bSuccess == False:
                    if sMsg != '':
                        self.oUtilsMsgs.DisplayWarning(sMsg)
                    
            self.oUtilsMsgs.DisplayInfo(sExitMsg)
            slicer.util.exit(status=EXIT_SUCCESS)
            
        # disable minimize for UserInteraction
        elif self.oSession.GetUserInteractionLogRequest() == True and\
                ((event.type() == qt.QEvent.WindowStateChange) and slicer.util.mainWindow().isMinimized()):
            slicer.util.mainWindow().showMaximized()
            
#         # disable drag window for UserInteraction  (located in non-client area)
        elif self.oSession.GetUserInteractionLogRequest() == True and\
                (event.type() ==  qt.QEvent.NonClientAreaMouseButtonRelease):
            slicer.util.mainWindow().move(self.oSession.oUserInteraction.GetMainWindowPosition())
            

                    