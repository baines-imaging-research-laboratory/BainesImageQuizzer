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

        self.oUtilsMsgs = UtilsMsgs()
        self.oUtilsIO = UtilsIO()
        self.oUtilsIO.SetupModulePaths(sModuleName)
        
        # test that Users folder exists - if not, create it
        if not os.path.exists(self.oUtilsIO.GetUsersBasePath()):
            os.makedirs(self.oUtilsIO.GetUsersBasePath())
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        
        # ------------------------------------------------------------------------------------
        #                                   Global Variables
        # ------------------------------------------------------------------------------------
        self.qtQuizProgressWidget = qt.QTextEdit()
        #self.logic = ImageQuizzerLogic(self)
        self.slicerLeftWidget= None     
        
        
        slicer.util.setMenuBarsVisible(True)
#         slicer.util.setToolbarsVisible(False) # for live runs
        slicer.util.setToolbarsVisible(True) # while developing
        

        # create the ImageQuizzer widget 
        self.oQuizWidgets = QuizWidgets()
        self.oQuizWidgets.CreateQuizzerLayout()


        # add to Slicer's main layout
        self.slicerLeftWidget = self.oQuizWidgets.GetSlicerLeftWidget()
        self.layout.addWidget(self.slicerLeftWidget)  
              

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
         
        self.qLineUserName = qt.QLineEdit()
        self.qLineUserName.setPlaceholderText('Enter user name')
        qUserLoginLayout.addWidget(self.qLineUserName)
         
        # Add vertical spacer
        qUserLoginLayout.addSpacing(20)
         
        # Get study button
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
         
        # Launch study button (not enabled until study is picked)
        self.btnLaunchStudy = qt.QPushButton("Launch Quiz")
        self.btnLaunchStudy.setEnabled(False)
        self.btnLaunchStudy.connect('clicked(bool)', self.onApplyLaunchQuiz)
        qUserLoginLayout.addWidget(self.btnLaunchStudy)
         
         
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     
    def onApplyOpenFile(self):
        # set to default
        self.btnLaunchStudy.setEnabled(False)
        self.qLblQuizFilename.text = ""
 
        # get quiz filename
        self.quizInputFileDialog = qt.QFileDialog()
        sSelectedQuiz = self.quizInputFileDialog.getOpenFileName(self.qUserLoginWidget, "Open File", self.oUtilsIO.GetXmlResourcesPath(), "XML files (*.xml)" )
 
        # check that file was selected
        if not sSelectedQuiz:
#             msgBox = qt.QMessageBox()
#             msgBox.critical(0,"Error","No quiz was selected")
            sErrorMsg = 'No quiz was selected'
            self.oUtilsMsgs.DisplayError(sErrorMsg)
        else:
            # enable the launch button
            self.qLblQuizFilename.setText(sSelectedQuiz)
            self.btnLaunchStudy.setEnabled(True)
            self.qUserLoginWidget.show()
            self.qUserLoginWidget.activateWindow()
            
            self.oUtilsIO.SetQuizFilename(sSelectedQuiz)
         
 
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
    def onApplyLaunchQuiz(self):
        # confirm username was entered
        if not self.qLineUserName.text:
            msgBox = qt.QMessageBox()
            msgBox.critical(0,"ERROR","No user name was entered")
        else:
            
            self.oUtilsIO.SetQuizUsername(self.qLineUserName.text)
            
            # copy file from Resource into user folder
            if self.oUtilsIO.SetupUserQuizFolder(): # success
                # start the session
                self.slicerLeftWidget.activateWindow()
                oSession = Session()
                oSession.RunSetup(self.oUtilsIO, self.oQuizWidgets)
                try:
                    #provide as much room as possible for the quiz
                    qDataProbeCollapsibleButton = slicer.util.mainWindow().findChild("QWidget","DataProbeCollapsibleWidget")
                    qDataProbeCollapsibleButton.collapsed = True
                    self.reloadCollapsibleButton.collapsed = True
                except:
                    pass
                
    
        
        
    
    
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

 
 
##########################################################################
#
# class QuizWidgets
#
##########################################################################

class QuizWidgets:
    
    def __init__(self,  parent=None):
        self.sClassName = type(self).__name__
        self.parent = parent
        print('Constructor for QuizWidgets')

        self._slicerLeftMainLayout = None
        self._slicerQuizLayout = None
        self._slicerLeftWidget = None
        
    def GetSlicerLeftMainLayout(self):
        return self._slicerLeftMainLayout

    def GetSlicerQuizLayout(self):
        return self._slicerQuizLayout
    
    def GetSlicerLeftWidget(self):
        return self._slicerLeftWidget

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def CreateQuizzerLayout(self):

        print ("-------ImageQuizzer Widget SetUp--------")

        #-------------------------------------------
        # set up quiz widget
        self._slicerLeftWidget = qt.QWidget()
        self._slicerLeftMainLayout = qt.QVBoxLayout()
        self._slicerLeftWidget.setLayout(self._slicerLeftMainLayout)
         
        
        
        # Status button
        self.btnShowQuizProgress = qt.QPushButton("Show Quiz Progress")
        self.btnShowQuizProgress.toolTip = "Display status of images."
        self.btnShowQuizProgress.enabled = True
        self._slicerLeftMainLayout.addWidget(self.btnShowQuizProgress)
        

        
        #-------------------------------------------
        # Collapsible button
        self.quizCollapsibleButton = ctk.ctkCollapsibleButton()
        self.quizCollapsibleButton.text = "Baines Image Quizzer"
        self._slicerLeftMainLayout.addWidget(self.quizCollapsibleButton)
        

        
        # Layout within the sample collapsible button - form needs a frame
        self._slicerQuizLayout = qt.QFormLayout(self.quizCollapsibleButton)
        self.quizFrame = qt.QFrame(self.quizCollapsibleButton)
        self.quizFrame.setLayout(qt.QVBoxLayout())
        self._slicerQuizLayout.addWidget(self.quizFrame)

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
    

