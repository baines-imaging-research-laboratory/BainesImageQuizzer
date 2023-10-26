import os, sys
import warnings
import vtk, qt, ctk, slicer

from Utilities.UtilsIOXml import *
from Utilities.UtilsMsgs import *

from shutil import copyfile
import shutil
import re    # for regex re.sub
import SimpleITK as sitk
import numpy as np

from datetime import datetime
import DICOMLib
from DICOMLib import DICOMUtils

import logging
import time
import traceback



##########################################################################
#
#   class UtilsFilesIO
#
##########################################################################

class UtilsFilesIO:
    """ Class UtilsFilesIO
        - to set up path and filenames for the Image Quizzer module
        - to handle disk input/output
    """
    
    def __init__(self, parent=None):
        self.parent = parent
        
        self._sScriptedModulesPath = ''     # location of quizzer module project

        self._sXmlQuizDir = ''         # folder - holds XML quiz files to copy to user
        self._sXmlQuizPath = ''       # full path (dir/file) of quiz to copy to user
        self._sXmlQuizFilename = ''            # quiz filename only (no dir)

        self._sDataParentDir = ''           # parent folder to images
        
        self._sUsersParentDir = ''          # folder - parent dir to all user folders
        self._sUsername = ''                # name of user taking the quiz
        self._sUserDir = ''                 # folder - holds quiz subfolders for specific user

        self._sUserQuizResultsDir = ''      # folder for quiz results
        self._sUserQuizResultsPath = ''     # full path (dir/file) for user's quiz results

        self._sDICOMDatabaseDir = ''
#         self._sImageVolumeDataDir = ''

        self._sResourcesROIColorFilesDir = ''  # folder to the Quizzer specific roi color files
        self._sDefaultROIColorTableName = 'GenericColors'
        self._sQuizzerROIColorTableNameWithExt = 'QuizzerROIColorTable.txt'
        self._sQuizzerROIColorTablePath = ''

        self._liPageGroups = []
        self._liUniquePageGroups = []

        self.oUtilsMsgs = UtilsMsgs()
        self.oIOXml = UtilsIOXml()

        self.setupTestEnvironment()



    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #-------------------------------------------
    #        Unit testing Utility
    #-------------------------------------------

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        
    def setupTestEnvironment(self):
        # check if function is being called from unit testing
        if "testing" in os.environ:
            self.sTestMode = os.environ.get("testing")
        else:
            self.sTestMode = "0"

 
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
    #-------------------------------------------
    #        Getters / Setters
    #-------------------------------------------

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    #----------
    def SetDataParentDir(self, sDataDirInput):
        self._sDataParentDir = sDataDirInput
        
    #----------
    def SetUsersParentDir(self, sDirInput):
        self._sUsersParentDir = sDirInput
        
    #----------
    def SetQuizUsername(self, sInput):
        self._sUsername = sInput
        
    #----------
    def SetXmlQuizPathAndFilename(self, sSelectedQuizPath):

        self._sXmlQuizPath = os.path.join(self._sXmlQuizDir, sSelectedQuizPath)
        self._sXmlQuizDir, self._sXmlQuizFilename = os.path.split(self._sXmlQuizPath)
        
    #----------
    def SetUsernameAndDir(self, sSelectedUser):
        self._sUsername = sSelectedUser
        self._sUserDir = os.path.join(self.GetUsersParentDir(), self._sUsername)
        
    #----------
    def SetDICOMDatabaseDir(self, sInputDir):
        self._sDICOMDatabaseDir = sInputDir
    
    #----------
    #----------
    def GetDataParentDir(self):
        return self._sDataParentDir

    #----------
    def GetDICOMDatabaseDir(self):
        return self._sDICOMDatabaseDir
    
    #----------
    def GetScriptsDir(self):
        return os.path.join(self.GetScriptedModulesPath(),'..','Inputs','Scripts')
    
    #----------
    def GetDirFromPath(self, sFullPath):
        head, tail = os.path.split(sFullPath)
        return head
    
    #----------
    def GetScriptedModulesPath(self):
        return self._sScriptedModulesPath
    
    #----------
    def GetXmlQuizPath(self):
        return self._sXmlQuizPath
    
    #----------
    def GetUsername(self):
        return self._sUsername
     
    #----------
    def GetUserDir(self):
        return self._sUserDir

    def GetUsersParentDir(self):
        return self._sUsersParentDir    

    #----------
    def GetUserQuizResultsDir(self):
        return self._sUserQuizResultsDir

    #----------
    def GetUserQuizResultsPath(self):
        return self._sUserQuizResultsPath
    
    #----------
    def GetXmlQuizDir(self):
        return self._sXmlQuizDir
    
    #----------
    def GetRelativeUserPath(self, sInputPath):
        # remove absolute path to user folders
        return sInputPath.replace(self.GetUserDir()+'\\','')

    #----------
    def GetRelativeDataPath(self, sInputPath):
        # remove absolute path to user folders
        return sInputPath.replace(self.GetDataParentDir()+'\\','')

    #----------
    def GetAbsoluteDataPath(self, sInputPath):
        return os.path.join(self._sDataParentDir, sInputPath)
    
    #----------
    def GetAbsoluteUserPath(self, sInputPath):
        return os.path.join(self.GetUserDir(), sInputPath)
    
    #----------
    def GetQuizFilename(self):
        return self._sXmlQuizFilename
    
    #----------
    def GetQuizFilenameNoExt(self):
        sFilenameNoExt = os.path.splitext(self.GetQuizFilename())[0]
        
        return sFilenameNoExt
    
    #----------
    def GetFilenameWithExtFromPath(self, sFilePath):
        sDir,sFilenameWithExt = os.path.split(sFilePath)

        return sFilenameWithExt
    
    #----------
    def GetFilenameNoExtFromPath(self, sFilePath):
        sDir, sFilenameExt = os.path.split(sFilePath)
        sFilenameNoExt = os.path.splitext(sFilenameExt)[0]

        return sFilenameNoExt
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetFolderNameForPageResults(self, oSession):
        """ Quiz results (eg. LabelMaps, MarkupLines) are stored in a directory where the name is derived from the 
            current page of the Session.
        """
        
        # get page info from the session's current page to create directory
        xPageNode = oSession.GetCurrentPageNode()
        sPageIndex = str(oSession.GetCurrentPageIndex() + 1)
        sPageID = oSession.oIOXml.GetValueOfNodeAttribute(xPageNode, 'ID')
        sPageDescriptor = oSession.oIOXml.GetValueOfNodeAttribute(xPageNode, 'Descriptor')
        sPageGroup = oSession.oIOXml.GetValueOfNodeAttribute(xPageNode, 'PageGroup')
        # sDirName = os.path.join(self.GetUserQuizResultsDir(), 'Pg'+ sPageIndex + '_' + sPageID )
        sDirName = os.path.join(self.GetUserQuizResultsDir(), 'PgGroup' + sPageGroup + '_' + sPageID + '_' + sPageDescriptor )

        return sDirName
        


    #----------
    #----------ROI Color Files
    #----------
    def SetResourcesROIColorFilesDir(self):
        self._sResourcesROIColorFilesDir = os.path.join(self.GetScriptedModulesPath(),\
                                                        'Resources','ColorFiles')
        
    #----------
    def GetResourcesROIColorFilesDir(self):
        return self._sResourcesROIColorFilesDir
    
    #----------
    def GetQuizzerROIColorTableNameWithExt(self):
        return self._sQuizzerROIColorTableNameWithExt
    
    #----------
    def SetQuizzerROIColorTablePath(self, sInputPath):
        self._sQuizzerROIColorTablePath = sInputPath

    #----------
    def GetQuizzerROIColorTablePath(self):
        return self._sQuizzerROIColorTablePath
    
    #----------
    def GetCustomROIColorTablePath(self, sROIColorFile):
        return os.path.join(self.GetXmlQuizDir(), sROIColorFile + '.txt')

    #----------
    def GetDefaultROIColorTableName(self):
        return self._sDefaultROIColorTableName

    #----------
    def GetDefaultROIColorFilePath(self):
        return os.path.join(self.GetResourcesROIColorFilesDir(), self.GetDefaultROIColorTableName() + '.txt')

    #----------
    def GetConfigDir(self):
        return os.path.join(self.GetScriptedModulesPath(),'..','Inputs','Config')


    #----------
    #----------Page Groups
    #----------
    def SetListPageGroupNumbers(self, liNumbers):
        self._liPageGroups = liNumbers
        
    #----------
    def GetListPageGroupNumbers(self):
        return self._liPageGroups
    
    #----------
    def SetListUniquePageGroups(self, liNumbers):
        self._liUniquePageGroups = liNumbers
        
    #----------
    def GetListUniquePageGroups(self):
        return self._liUniquePageGroups
    
    #----------
    def ClearPageGroupLists(self):
        self._liPageGroups = []
        self._liUniquePageGroups = []
    
    
    #----------
    #----------General functions
    #----------
    def CleanFilename(self, sInputFilename):
#         sInvalid = '<>:"/\|?* '
        sInvalid = '<>:"/\|?*'
        sCleanName = sInputFilename
        
        for char in sInvalid:
            sCleanName = sCleanName.replace(char,'')
            
        return sCleanName

    #----------
    def getNodes(self):
        
        ##### For Debug #####
        # return nodes in the mrmlScene
        #    Can be used to flag differences in nodes before and after code
        #    being investigated (example: for memory leaks)

        nodes = slicer.mrmlScene.GetNodes()
        return [nodes.GetItemAsObject(i).GetID() for i in range(0,nodes.GetNumberOfItems())]

        ######################
        # set the following line before code being investigated
        #
        #        nodes1 = self.oFilesIO.getNodes()
        #
        # set these lines after code being investigated
        #
        #        nodes2 = self.oFilesIO.getNodes()
        #        filteredX = ' '.join((filter(lambda x: x not in nodes1, nodes2)))
        #        print(':',filteredX)
        ######################

    #----------
    def PrintDirLocations(self):
        
        ##### For Debug #####
        print('Data parent dir:      ', self.GetDataParentDir())
        print('DICOM DB dir:         ', self.GetDICOMDatabaseDir())
        print('User parent dir:      ', self.GetUsersParentDir())
        print('User dir:             ', self.GetUserDir())
        print('User Quiz Results dir:', self.GetUserQuizResultsDir())
        print('User Quiz Results XML path:', self.GetUserQuizResultsPath())
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #-------------------------------------------
    #        Setup Functions
    #-------------------------------------------

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetModuleDirs(self, sModuleName):
        self.SetScriptedModulesPath(sModuleName)
        self._sXmlQuizDir = os.path.join(self.GetScriptedModulesPath(),'..', 'Inputs','MasterQuiz')
        self.SetResourcesROIColorFilesDir()
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetScriptedModulesPath(self,sModuleName):
        # from Slicer's Application settings> modules
        self._sScriptedModulesPath = eval('slicer.modules.%s.path' % sModuleName.lower())
        self._sScriptedModulesPath = os.path.dirname(self._sScriptedModulesPath)
#         print('Path:',self._sScriptedModulesPath)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetupROIColorFile(self, sCustomInputROIColorFile):
        """ If quiz has a custom color table for segmenting ROI's, move this 
            into the color table file that is read in by the QuizzerEditor HelperBox
        """
        if sCustomInputROIColorFile == '':
            sROIColorFilePath = self.GetDefaultROIColorFilePath()
        else:
            sROIColorFilePath = os.path.join(self.GetXmlQuizDir(), sCustomInputROIColorFile + '.txt')
        
        self.SetQuizzerROIColorTablePath( os.path.join(self.GetResourcesROIColorFilesDir(), \
                                             self.GetQuizzerROIColorTableNameWithExt()) )
        copyfile(sROIColorFilePath, self.GetQuizzerROIColorTablePath() )
                
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetupForUserQuizResults(self):
        
        sQuizFileRoot, sExt = os.path.splitext(self.GetQuizFilename())
         
        self._sUserQuizResultsDir = os.path.join(self.GetUserDir(), sQuizFileRoot)
        self._sUserQuizResultsPath = os.path.join(self.GetUserQuizResultsDir(), self.GetQuizFilename())
 
        # check that the user folder exists - if not, create it
        if not os.path.exists(self._sUserQuizResultsDir):
            os.makedirs(self._sUserQuizResultsDir)
         
     
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetupOutputDirs(self):
        
        # the parent of the Outputs directory is  path/to/ImageQuizzermodule/Outputs
        #    Quiz results in XML format are stored in the UsersResults subfolders
        #        as well as any saved label volumes (contours, annotations)
        #    Slicer updates the DICOM database in the SlicerDICOMDatabase subfolder
        #        to coordinate import/load of images
        
        
        sParentOutputsDir = os.path.join(self.GetScriptedModulesPath(),'..', 'Outputs')
        
        # if users directory does not exist yet, it will be created
        self.SetUsersParentDir(os.path.join(sParentOutputsDir, 'UsersResults'))
        if not os.path.exists(self._sUsersParentDir):
            os.makedirs(self._sUsersParentDir)
                    
        
        # create the DICOM database if it is not there ready for importing
        self.SetDICOMDatabaseDir( os.path.join(sParentOutputsDir, 'SlicerDICOMDatabase') )
        if not os.path.exists(self.GetDICOMDatabaseDir()):
            os.makedirs(self.GetDICOMDatabaseDir())
        
        # assign the database directory to the browser widget
        slDicomBrowser = slicer.modules.dicom.widgetRepresentation().self() 
        slDicomBrowserWidget = slDicomBrowser.browserWidget
        slDicomBrowserWidget.dicomBrowser.setDatabaseDirectory(self.GetDICOMDatabaseDir())
        
        # update the database through the dicom browser 
        # this clears out path entries that can no longer be resolved
        #    (in the case of database location changes)
        slDicomBrowserWidget.dicomBrowser.updateDatabase()
        
        # test opening the database
        if DICOMUtils.openDatabase(self.GetDICOMDatabaseDir()):
            pass
        else:
            sMsg = 'Trouble opening SlicerDICOMDatabase in : '\
                 + self.GetDICOMDatabaseDir()
            self.oUtilsMsgs.DisplayError(sMsg)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def PopulateUserQuizFolder(self):
            
        # check if there is an existing file in the output users results directory (partially completed quiz)
        #    if not - copy from the master quiz file in inputs to outputs directory
        if not os.path.isfile(self.GetUserQuizResultsPath()):

            if not os.path.isfile(self.GetXmlQuizPath()):
                sErrorMsg = 'Selected Quiz file does not exist'
                self.oUtilsMsgs.DisplayWarning(sErrorMsg)
                return False  
            else:
                copyfile(self.GetXmlQuizPath(), self.GetUserQuizResultsPath())
                return True

        else:

            # create backup of existing file
            self.BackupUserQuizResults()
                
            # file exists - make sure it is readable
            if not os.access(self.GetUserQuizResultsPath(), os.R_OK):
                # existing file is unreadable
                sErrorMsg = 'Quiz file is not readable'
                self.oUtilsMsgs.DisplayWarning(sErrorMsg)     
                return False
            else:
                return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #-------------------------------------------
    #        Utility Functions
    #-------------------------------------------

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CreatePageDir(self, sPageName):
        # page dir stores label maps for the specified page
        # store these in the user directory
        sPageDir = os.path.join(self.GetUserDir(), sPageName)
        
        # check that the Page directory exists - if not create it
        if not os.path.exists(sPageDir):
            os.makedirs(sPageDir)
    
        return sPageDir

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetUniqueNumbers(self, liNumbers):
        ''' Utility to return the unique numbers from a given list of numbers.
        '''

        liUniqueNumbers = []
        for ind in range(len(liNumbers)):
            iNum = liNumbers[ind]
            if iNum not in liUniqueNumbers:
                liUniqueNumbers.append(iNum)
        
        return liUniqueNumbers
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CreateShutdownBatchFile(self):
        """ If Image Quizzer was started using the batch file, 
            the shutdown batch file will be called on close.
            This function sets up the shutdown batch file instructing it to
            remove the SlicerDicomDatabase directory.
            This speeds up the relaunch of the Image Quizzer. 
            
            This batch file resides in the parent directory of the ImageQuizzer module .
        """
        
        # get parent directory of the Image Quizzer module
        sShutdownDir = os.path.abspath(os.path.join(self.GetScriptedModulesPath(),'..', os.pardir))
        sShutdownPath = os.path.join(sShutdownDir,'ImageQuizzerShutdown.bat')

        sCommand = 'RMDIR /S /Q ' + '"' + self.GetDICOMDatabaseDir() +'"'
        
        fh = open(sShutdownPath,"w")
        fh.write(sCommand)
        fh.close()

        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def BackupUserQuizResults(self):
        
        # get current date/time
        from datetime import datetime
        now = datetime.now()
        sSuffix = now.strftime("%b-%d-%Y-%H-%M-%S")
        
        sFileRoot, sExt = os.path.splitext(self.GetQuizFilename())
        
        sNewFileRoot = '_'.join([sFileRoot, sSuffix])
        sNewFilename = ''.join([sNewFileRoot, sExt])
        
        sBackupQuizResultsPath = os.path.join(self.GetUserQuizResultsDir(), sNewFilename)
        
        # create copy with data/time stamp as suffix
        copyfile(self.GetUserQuizResultsPath(), sBackupQuizResultsPath)
        
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #-------------------------------------------
    #        Validation Functions
    #-------------------------------------------

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateQuiz(self):
        '''
            a function to check for specific validation requirements for the quiz
        '''
        sMsg = ''
        bSuccess = True
        
        
        try:
            # open requested quiz xml 
            bSuccess, xRootNode = self.oIOXml.OpenXml(self.GetXmlQuizPath(),'Session')

            # >>>>>>>>>>>>>>>
            # check options for ContourVisibility at the Session level
            sContourVisibility = self.oIOXml.GetValueOfNodeAttribute(xRootNode, 'ContourVisibility')
            if not (sContourVisibility == 'Fill' or sContourVisibility == 'Outline' or sContourVisibility == ''):
                sValidationMsg = "\nContourVisibility value must be 'Fill' or 'Outline'. See attribute in Session"
                sMsg = sMsg + sValidationMsg
                
            sEmailResultsTo = self.oIOXml.GetValueOfNodeAttribute(xRootNode, 'EmailResultsTo')
            if sEmailResultsTo != '':
                # ensure that the smtp config file exists
                sSmtpConfigFile = os.path.join(self.GetConfigDir(), 'smtp_config.txt')
                if not (os.path.exists(sSmtpConfigFile)) :
                    sMsg = sMsg + '\nMissing smtp configuration file for request to email quiz results : ' + sSmtpConfigFile
            
            sROIColorFile = self.oIOXml.GetValueOfNodeAttribute(xRootNode, 'ROIColorFile')
            if sROIColorFile != '':
                sROIColorFilePath = os.path.join(self.GetXmlQuizDir(), sROIColorFile + '.txt')
                sValidationMsg = self.ValidateROIColorFile(sROIColorFilePath)
                sMsg = sMsg + sValidationMsg
            
            
            # check matches of LabelMapID with DisplayLabelMapID
            sValidationMsg = self.ValidateDisplayLabelMapID()
            sMsg = sMsg + sValidationMsg
            
            # check matches of BookmarkID with request 'GoToBookmark' attribute
            sValidationMsg = self.ValidateGoToBookmarkRequest()
            sMsg = sMsg + sValidationMsg
            
            # >>>>>>>>>>>>>>>
            lxPageElements = self.oIOXml.GetChildren(xRootNode, 'Page')
            
            iPageNum = 0
            for xPage in lxPageElements:
                lPathAndNodeNames= []
                iPageNum= iPageNum + 1

                sValidationMsg = self.ValidateRequiredAttribute(xPage, 'ID', str(iPageNum))
                sMsg = sMsg + sValidationMsg
                
                sPageID = self.oIOXml.GetValueOfNodeAttribute(xPage, 'ID')
                sPageReference = str(iPageNum) # initialize
                
                # for any page, make sure there is matching Images Volume to Segmentation or Volume to LabelMap for each destination
                sValidationMsg = self.ValidateImageToSegmentationMatch(xPage, sPageReference)
                sMsg = sMsg + sValidationMsg

                
                # Image element validations
                lxImageElements = self.oIOXml.GetChildren(xPage, 'Image')
                for xImage in lxImageElements:
                    sImageID = self.oIOXml.GetValueOfNodeAttribute(xImage, 'ID')
    
                    # Page ID + Image ID creates the node name for the image that is loaded (in ImageView>ViewNodeBase)
                    sNodeNameID = sPageID + '_' + sImageID
                    sPageReference = str(iPageNum) + ' ' + sNodeNameID

                    # >>>>>>>>>>>>>>> Attributes
                    sValidationMsg = self.ValidateRequiredAttribute(xImage, 'ID', sPageReference)
                    sMsg = sMsg + sValidationMsg
                    
                    sValidationMsg = self.ValidateRequiredAttribute(xImage, 'Type', sPageReference)
                    sMsg = sMsg + sValidationMsg
                    
                    sValidationMsg = self.ValidateAttributeOptions(xImage, 'Type', sPageReference, self.oIOXml.lValidImageTypes)
                    sMsg = sMsg + sValidationMsg
                    
                    sValidationMsg = self.ValidateOpacity(xImage, iPageNum)
                    sMsg = sMsg + sValidationMsg

                    # check merging of label maps have a matching LabelMapID Image and Loop in Page
                    sValidationMsg = self.ValidateMergeLabelMaps(xImage, xPage, iPageNum)
                    sMsg = sMsg + sValidationMsg

                    # >>>>>>>>>>>>>>> Elements
                    sValidationMsg = self.ValidateRequiredElement(xImage, 'Path', sPageReference)
                    sMsg = sMsg + sValidationMsg
                    
                    sValidationMsg = self.ValidateElementOptions(xImage, 'Layer', sPageReference, self.oIOXml.lValidLayers)
                    sMsg = sMsg + sValidationMsg
                    
                    sValidationMsg = self.ValidateElementOptions(xImage, 'DefaultDestination', sPageReference, self.oIOXml.lValidSliceWidgets)
                    sMsg = sMsg + sValidationMsg
                    
                    sImageType = self.oIOXml.GetValueOfNodeAttribute(xImage, 'Type')
                    if not (sImageType == 'Segmentation' or sImageType == 'RTStruct' or sImageType == 'LabelMap'):
                        sValidationMsg = self.ValidateElementOptions(xImage, 'DefaultOrientation', sPageReference, self.oIOXml.lValidOrientations)
                        sMsg = sMsg + sValidationMsg
                        
                    sPanOrigin = self.oIOXml.GetValueOfNodeAttribute(xImage, 'PanOrigin')
                    if sPanOrigin != '':
                        sValidationMsg = self.ValidateListOfNumbers(sPanOrigin, 'Float', 3, 'PanOrigin', sPageReference)
                        sMsg = sMsg + sValidationMsg
                    
                    # >>>>>>>>>>>>>>>
     

                    # For any page, test that a path always has only one associated PageID_ImageID (aka node name)
                    #    (Otherwise, the quizzer will reload the same image with a different node name)
                    lxImagePath = self.oIOXml.GetChildren(xImage, 'Path')
                    if len(lxImagePath) == 1:
                        sImagePath = self.oIOXml.GetDataInNode(lxImagePath[0])
                         
                        # create tuple of path, sNodeName
                        tupPathAndID = (sImagePath, sNodeNameID)
                         
                        # search list of path/nodeNames for existing match
                        bFoundMatchingPath = False
                        ind = 0
                        for lElement in lPathAndNodeNames:
                            ind = ind + 1
                            msg = (str(ind) + ':' )
                            if bFoundMatchingPath == False:
                                # check if path exists in the list elements
                                if sImagePath in lElement:
                                    bFoundMatchingPath = True
                                    # check that sNodeName exists in that list element
                                    if sNodeNameID not in lElement:
                                        sMsg = sMsg + "\nIn any Page Element, there should be only one match of the combined 'PageID_ImageID' attributes with the Image Path" +\
                                                "\nThere are multiple paths that have the same 'PageID_ImageID' on this Page" +\
                                                "\n   .....Check all paths for Page: " + str(iPageNum) + ' '+ sNodeNameID
                                     
                        if not bFoundMatchingPath:
                            # new path found; add to list
                            lPathAndNodeNames.append(tupPathAndID)
                            
                            
                    # If the image type is an RTStruct or Segmentation, validate the ROIs element
                    sImageType = self.oIOXml.GetValueOfNodeAttribute(xImage, 'Type')
                    if sImageType == 'RTStruct' or sImageType == 'Segmentation':
                        sValidationMsg = self.ValidateRequiredElement(xImage, 'ROIs', sPageReference)
                        sMsg = sMsg + sValidationMsg
                        
                        lxROIs = self.oIOXml.GetChildren(xImage, 'ROIs')
                        if len(lxROIs) >0:
                            sValidationMsg = self.ValidateRequiredAttribute(lxROIs[0], 'ROIVisibilityCode', sPageReference)
                            sMsg = sMsg + sValidationMsg
                            sValidationMsg = self.ValidateAttributeOptions(lxROIs[0], 'ROIVisibilityCode', sPageReference, self.oIOXml.lValidRoiVisibilityCodes)
                            sMsg = sMsg + sValidationMsg
                            
                            # if the visibility code is Select or Ignore, there must be an ROI element(s) with the name(s) present
                            sVisibilityCode = self.oIOXml.GetValueOfNodeAttribute(lxROIs[0], 'ROIVisibilityCode')
                            if sVisibilityCode == 'Select' or sVisibilityCode == 'Ignore':
                                sValidationMsg = self.ValidateRequiredElement(lxROIs[0], 'ROI', sPageReference, True)  # True for multiple elements allowed
                                sMsg = sMsg + sValidationMsg

                    

                # >>>>>>>>>>>>>>>
                # validate attributes 'SegmentRequired' and 'SegmentRequiredOnAnyImage'
                sValidationMsg = self.ValidateSegmentRequiredSettings(xPage, iPageNum)
                sMsg = sMsg + sValidationMsg
                            
                # >>>>>>>>>>>>>>>
                # validate attributes 'SegmentRequired' and 'MinMarkupLinesRequiredOnAnyImage'
                sValidationMsg = self.ValidateMarkupLinesRequiredSettings(xPage, sPageReference)
                sMsg = sMsg + sValidationMsg
                            
                # Slice4 assignments and TwoOverTwo layout
                sValidationMsg = self.ValidateSlice4Layout(xPage, sPageReference)
                sMsg = sMsg + sValidationMsg
                  
            # >>>>>>>>>>>>>>>
            # validate that each page has a PageGroup attribute if the session requires page group randomization
            #    a quiz that has no PageGroup attributes will be assigned the default numbers during the session setup
            sRandomizeRequested = self.oIOXml.GetValueOfNodeAttribute(xRootNode, 'RandomizePageGroups')
            if sRandomizeRequested == "Y":
                sValidationMsg = self.ValidatePageGroupNumbers(xRootNode)
                sMsg = sMsg + sValidationMsg

            # check that the ROI Color file exists if requested
            sROIColorFile = self.oIOXml.GetValueOfNodeAttribute(xRootNode,'ROIColorFile')
            if sROIColorFile.endswith('.txt'):
                sMsg = sMsg + '\nRemove .txt extenstion from ROIColorFile name.'
            if sROIColorFile == '':
                sROIColorFilePath = self.GetDefaultROIColorFilePath()
            else:
                sROIColorFilePath = self.GetCustomROIColorTablePath(sROIColorFile)
            if not os.path.isfile(sROIColorFilePath):
                sMsg = sMsg + '\nCustom ROIColorFile does not exist in the directory with the quiz.' + sROIColorFilePath
                
                
            
            # >>>>>>>>>>>>>>>

            # validation errors found
            if sMsg != '':
                raise
        
        except ValueError:
            if self.sTestMode == "0":
                raise   # rethrow for live run
            else:
                raise ('Value Error: %s' % sMsg)
            
        except:
            bSuccess = False
            self.oUtilsMsgs.DisplayWarning('Quiz Validation Errors \n' + sMsg)
            # after warning, reset the message for calling function to display error and exit
            tb = traceback.format_exc()
            self.oUtilsMsgs.DisplayWarning('Quiz Validation Errors \n' + sMsg)
            # after warning, reset the message for calling function to display error and exit
            sMsg = 'See Administrator: ERROR in quiz XML validation. --Exiting--'\
                   + "\n\n" + tb 
            
            
        return bSuccess, sMsg
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateRequiredElement(self, xParentElement, sElementName, sPageReference, bMultipleAllowed=False):
        '''
            This function checks that there is exactly one child element for the input parent element if the flag for
            multiples has not been set to true.
        '''
        sMsg = ''
        sMsgPrefix = '\nError for ' + sElementName + ' Element. '
        sMsgMissing = 'Required element is missing.'
        sMsgMultipleNotAllowed = 'More than one of this element was found. Only one is allowed.'
        sMsgEnding = '  See Page:' + sPageReference
        
        lxChildren = self.oIOXml.GetChildren(xParentElement, sElementName)
        if len(lxChildren) == 0:
            sMsg = sMsgPrefix +  sMsgMissing + sMsgEnding
        elif len(lxChildren) >1 and bMultipleAllowed == False:
            sMsg = sMsgPrefix + sMsgMultipleNotAllowed + sMsgEnding
                     
        return sMsg
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateElementOptions(self, xParentElement, sElementName, sPageReference, lValidOptions):
        '''
            This function checks that the data stored in the xml element exists in the list of valid options.
        '''
        sMsg = ''
        sValidOptions = ''
        for sOption in lValidOptions:
            sValidOptions = sValidOptions + ', ' + sOption
        
        lxChildren = self.oIOXml.GetChildren(xParentElement, sElementName)

        for xChild in lxChildren:
            sDataValue = self.oIOXml.GetDataInNode(xChild)
            if sDataValue not in lValidOptions:
                sMsg = sMsg + '\nNot a valid option for ' + sElementName + ' : ' + sDataValue + '   See Page:' + sPageReference\
                        + '\n   .....Valid options are:' + sValidOptions

        if len(lxChildren) == 0:
            sMsg = sMsg + '\nMissing Element: ' + sElementName + '   See Page:' + sPageReference\
                        + '\n   .....Valid options are:' + sValidOptions
            

        return sMsg
                        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateRequiredAttribute(self, xParentElement, sAttributeName, sPageReference):
        sMsg = ''
        sDataValue = ''
        sDataValue = self.oIOXml.GetValueOfNodeAttribute(xParentElement, sAttributeName)
        if sDataValue == '':
            sMsg = sMsg + '\nError for ' + sAttributeName + ' Attribute.   See Page:' + sPageReference\
                     + '\n   .....The required attribute is missing.'
        
        return sMsg

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateAttributeOptions(self, xParentElement, sAttributeName, sPageReference, lValidOptions):
        ''' Given the list of valid options, the function checks that the
            data stored in the element exists in that list.
        '''
        
        sMsg = ''
        
        sDataValue = self.oIOXml.GetValueOfNodeAttribute(xParentElement, sAttributeName)

        # check for valid option if it exists
        if sDataValue != '':
            if sDataValue not in lValidOptions:
                sValidOptions = ''
                for sOption in lValidOptions:
                    sValidOptions = sValidOptions + ', ' + sOption
                sMsg = sMsg + '\nNot a valid option for ' + sAttributeName + ' : ' + sDataValue + '   See Page:' + sPageReference\
                        + '\n   .....Valid options are:' + sValidOptions
            
        return sMsg

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateDatabaseLocation(self):
        ''' collect all file paths and ensure the file exists in the given database location
        '''
        
        # open requested quiz xml 
        bSuccess, xRootNode = self.oIOXml.OpenXml(self.GetXmlQuizPath(),'Session')
        
        if bSuccess:
            
            lsUniqueImagePaths = []
            sMissingFiles = ''
            sMissingFilesPrefix = 'Do you indicate the wrong Database directory? Check file path. \n\n'
            
            lxPageNodes = self.oIOXml.GetChildren(xRootNode,'Page')
            iPageNum = 0
            for xPageNode in lxPageNodes:
                iPageNum = iPageNum + 1
                
                lxImageNodes = self.oIOXml.GetChildren(xPageNode, 'Image')
                for xImageNode in lxImageNodes:
                    
                    lxPathNodes = self.oIOXml.GetChildren(xImageNode, 'Path')
                    for xPathNode in lxPathNodes:
                        sPath = self.oIOXml.GetDataInNode(xPathNode)
                        
                        if sPath in lsUniqueImagePaths:
                            pass
                        else:
                            lsUniqueImagePaths.append(sPath)
                            sFullPath = os.path.join(self.GetDataParentDir(), sPath)
                            if not os.path.exists(sFullPath):
                                if sMissingFiles == '':
                                    sMissingFiles = sMissingFiles + sMissingFilesPrefix
                                sMissingFiles = sMissingFiles + 'Missing File... Page: ' + str(iPageNum) + '  File: ' + sFullPath + '\n'
                    

        return sMissingFiles
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidatePageGroupNumbers(self, xRootNode):
        ''' If the Session requires randomization of page groups, each page must have a PageGroup attribute
            If all page group numbers are equal, no randomization will be done.
            The page group values must be integer values.
            PageGroup = 0 is allowed. These will always appear at the beginning of the composite list of indices
        '''
        sMsg = ''
        sValidationMsg = ''
        self.ClearPageGroupLists()
        
        # check that each page has a page group number and that it is an integer
        lxPages = self.oIOXml.GetChildren(xRootNode,'Page')
        iPageNum = 0
        for xPage in lxPages:
            iPageNum = iPageNum + 1
            
            # required attribute for randomization
            sValidationMsg = self.ValidateRequiredAttribute(xPage, 'PageGroup', str(iPageNum))
            if sValidationMsg != '':
                sMsg = sMsg + sValidationMsg
                if self.sTestMode == "1":
                    raise Exception('Missing PageGroup attribute: %s' %sValidationMsg)
            
            try:
                # test that the value is an integer
                iPageGroup = int(self.oIOXml.GetValueOfNodeAttribute(xPage, 'PageGroup'))
                # if iPageGroup == 0:
                #     sValidationMsg = 'Page Group must be an integer > 0. See Page: ' + str(iPageNum)
                #     sMsg = sMsg + sValidationMsg
                
            except ValueError:
                sValidationMsg = '\nPage Group is not an integer. See Page: ' + str(iPageNum)
                sMsg = sMsg + sValidationMsg
                if self.sTestMode == "1":
                    raise ValueError('Invalid PageGroup value: %s' % sValidationMsg)
            
            if sMsg == '':
                self._liPageGroups.append(iPageGroup)

        # check that number of different page group numbers (that are >0) must be >1
        # you can't randomize if all the pages are assigned to the same group
        self.SetListUniquePageGroups(self.GetUniqueNumbers(self._liPageGroups))
        
        liValidationPageGroups=[]
        liValidationPageGroups = self._liUniquePageGroups[:]   # use a working copy of the list of unique page groups
        if 0 in liValidationPageGroups:
            liValidationPageGroups.remove(0) # ignore page groups set to 0
        if len(liValidationPageGroups) <= 1: # <= in case of an empty list
            sValidationMsg = '\nNot enough unique PageGroups for requested randomization. \nYou must have more than one page group (other than 0)'
            sMsg = sMsg + sValidationMsg
            if self.sTestMode == "1":
                raise Exception('Validating PageGroups Error: %s' % sValidationMsg)
            
        return sMsg

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateOpacity(self,xImage, iPageNum):
        sMsg = ''
        sErrorMsg = '\nOpacity must be a number between 0.0 and 1.0.   See Page: '
        
        sOpacity = self.oIOXml.GetValueOfNodeAttribute(xImage, 'Opacity')   # not required
        if sOpacity != '':
            try:
                fOpacity = float(sOpacity)
                if fOpacity < 0 or fOpacity > 1.0:
                    sMsg = sErrorMsg + str(iPageNum)
                    if self.sTestMode == "1":
                        raise
            except ValueError:  # to catch : not a number
                sMsg = sErrorMsg + str(iPageNum)
                if self.sTestMode == "1":
                    raise ValueError('Invalid Opacity value: %s' % sMsg)
            except:
                sMsg = sErrorMsg + str(iPageNum)
                if self.sTestMode == "1":
                    raise Exception('Invalid Opacity value: %s' % sMsg)
        
        return sMsg
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateSegmentRequiredSettings(self, xPageNode, iPageReference):
        
       
        sMsg = ''
        sErrorMsgEnableEditor = "\nPage must have 'EnableSegmentEditor' attribute set to 'Y' when a segment required attribute is set. See Page: "
        sErrorMsgSegmentOnAnyImage = "\nContradicting attributes. You cannot have both 'SegmentRequired' on an image and 'SegmentRequiredOnAnyImage' on a page. See Page: "
        sErrorMsgMismatchSegmentRequired = "\nAll image elements with the same path (but different destinations) must have the same attribute 'SegmentRequired' setting. See Page: "
        sErrorMsgSegmentRequiredOnWrongLayer = "\n'SegmentRequired' attribute cannot be on an image assigned to Layer='Segmentation' or 'Label' See Page: "
        
        sEnableSegmentEditorSetting = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'EnableSegmentEditor')
        sSegmentOnAnyImageSetting = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'SegmentRequiredOnAnyImage')
        
        lxImageNodes = self.oIOXml.GetChildren(xPageNode, 'Image')
        
        bFoundSegmentRequiredForImage = False
        l2tupImageSettings = []
        
        for idx in range(len(lxImageNodes)):
            xImageNode = lxImageNodes[idx]

            # collect settings for image
            sSegmentRequiredSetting = self.oIOXml.GetValueOfNodeAttribute(xImageNode, 'SegmentRequired')
            if sSegmentRequiredSetting == '':
                sSegmentRequiredSetting = 'N'
            sImageLayerNode = self.oIOXml.GetLastChild(xImageNode, 'Layer')
            sImageLayer = self.oIOXml.GetDataInNode(sImageLayerNode)
            sImagePathNode = self.oIOXml.GetLastChild(xImageNode,'Path')
            sImagePath = self.oIOXml.GetDataInNode(sImagePathNode)
            tupImageSettings = [sImagePath, sSegmentRequiredSetting]
            l2tupImageSettings.append(tupImageSettings)
            
            if sSegmentRequiredSetting == 'Y':
                bFoundSegmentRequiredForImage = True
                if (sImageLayer=="Segmentation" or sImageLayer=="Label"):
                    sMsg = sMsg + sErrorMsgSegmentRequiredOnWrongLayer + str(iPageReference)

                
        if sSegmentOnAnyImageSetting == "Y" or bFoundSegmentRequiredForImage == True :
            if sEnableSegmentEditorSetting != "Y":
                sMsg = sMsg + sErrorMsgEnableEditor + str(iPageReference)
                
        # if a segment required attribute was found for an image, ensure:
        #    - that it is not on an image set to Layer="Segmentation" or "Label"
        #    - that all images with that same path have the same attribute setting
        
        if sSegmentOnAnyImageSetting == "Y" and bFoundSegmentRequiredForImage == True:
            sMsg = sMsg + sErrorMsgSegmentOnAnyImage + str(iPageReference)
                

        if bFoundSegmentRequiredForImage:
            bMismatch = False
            for idxOuterLoop in range(len(l2tupImageSettings)):
                if bMismatch == True:
                    break
                sPathToCompare = l2tupImageSettings[idxOuterLoop][0]
                sSettingToCompare = l2tupImageSettings[idxOuterLoop][1]
                
                for idxInnerLoop in range(len(l2tupImageSettings)):
                    sPath = l2tupImageSettings[idxInnerLoop][0]
                    sSetting = l2tupImageSettings[idxInnerLoop][1]
                    if sPathToCompare == sPath:
                        if sSettingToCompare != sSetting:
                            sMsg = sMsg + sErrorMsgMismatchSegmentRequired + str(iPageReference)
                            bMismatch = True
                            break
        
        return sMsg
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateMarkupLinesRequiredSettings(self, xPageNode, iPageReference):
        
        sMsg = ''
        sErrorMsgMarkupLinesOnAnyImage = "\nContradicting attributes. You cannot have both 'MinMarkupLinesRequired' on an image and 'MinMarkupLinesRequiredOnAnyImage' on a page. See Page: "
        sErrorMsgMismatchMarkupLinesRequired = "\nAll image elements with the same path (but different destinations) must have the same attribute 'MinMarkupLinesRequired' setting. See Page: "
        sErrorMsgMarkupLinesRequiredOnWrongLayer = "\n'MinMarkupLinesRequired' attribute cannot be on an image assigned to Layer='Segmentation' or 'Label' See Page: "
        
        bFoundMarkupLinesRequiredForImage = False
        l2tupImageSettings = []

        sMarkupLinesOnAnyImageSetting = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'MinMarkupLinesRequiredOnAnyImage')
        lxImageNodes = self.oIOXml.GetChildren(xPageNode, 'Image')
        

        for idx in range(len(lxImageNodes)):
            xImageNode = lxImageNodes[idx]

            # collect settings for image
            sMarkupLinesRequiredSetting = self.oIOXml.GetValueOfNodeAttribute(xImageNode, 'MinMarkupLinesRequired')
            if sMarkupLinesRequiredSetting == '':
                iNumRequiredLines = 0
            else:
                iNumRequiredLines = int(sMarkupLinesRequiredSetting)
                
                
            sImageLayerNode = self.oIOXml.GetLastChild(xImageNode, 'Layer')
            sImageLayer = self.oIOXml.GetDataInNode(sImageLayerNode)
            sImagePathNode = self.oIOXml.GetLastChild(xImageNode,'Path')
            sImagePath = self.oIOXml.GetDataInNode(sImagePathNode)
            tupImageSettings = [sImagePath, sMarkupLinesRequiredSetting]
            l2tupImageSettings.append(tupImageSettings)


            if iNumRequiredLines > 0:
                bFoundMarkupLinesRequiredForImage = True
                if (sImageLayer=="Segmentation" or sImageLayer=="Label"):
                    sMsg = sMsg + sErrorMsgMarkupLinesRequiredOnWrongLayer + str(iPageReference)

        # if a markup line required attribute was found for an image, ensure:
        #    - that it is not on an image set to Layer="Segmentation" or "Label"
        #    - that all images with that same path have the same attribute setting
        
        if sMarkupLinesOnAnyImageSetting != '' and bFoundMarkupLinesRequiredForImage:
                sMsg = sMsg + sErrorMsgMarkupLinesOnAnyImage + str(iPageReference)
            
        if bFoundMarkupLinesRequiredForImage:
            bMismatch = False
            for idxOuterLoop in range(len(l2tupImageSettings)):
                if bMismatch == True:
                    break
                sPathToCompare = l2tupImageSettings[idxOuterLoop][0]
                sSettingToCompare = l2tupImageSettings[idxOuterLoop][1]
                
                for idxInnerLoop in range(len(l2tupImageSettings)):
                    sPath = l2tupImageSettings[idxInnerLoop][0]
                    sSetting = l2tupImageSettings[idxInnerLoop][1]
                    if sPathToCompare == sPath:
                        if sSettingToCompare != sSetting:
                            sMsg = sMsg + sErrorMsgMismatchMarkupLinesRequired + str(iPageReference)
                            bMismatch = True
                            break
        
        return sMsg
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateSlice4Layout(self, xPageNode, iPageReference):
        ''' For all image elements, check if it is assigned to Slice4, 
            that the Page has the attribute 'Layout="TwoOverTwo" '
        '''
        sMsg = ''
        sLayoutSetting = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'Layout')
        
        lxImageNodes = self.oIOXml.GetChildren(xPageNode, 'Image')

        for idx in range(len(lxImageNodes)):
            xImageNode = lxImageNodes[idx]
            xDestination = self.oIOXml.GetNthChild(xImageNode, 'DefaultDestination',0)
            sDestination = self.oIOXml.GetDataInNode(xDestination)
            
            if sDestination == 'Slice4' and sLayoutSetting != 'TwoOverTwo':
                sMsg = sMsg + "\nAssigning an image to Slice4 requires the Page Layout attribute to be set to 'TwoOverTwo'."\
                        + "\nSee Page:" + str(iPageReference)
        
        return sMsg
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateGoToBookmarkRequest(self):
        ''' For all instances of 'GoToBookmark', ensure that there is a corresponding
            BookmarkID. This can help trap spelling mistakes. 
            (This is not checked
            for a 'previous instance' of BookmarkID if RandomizePageGroups attribute
            is set to 'Y'.)
        '''
        sMsg = ''
        l3tupGoToBookmarkIDs = []
        l3tupBookmarkIDs = []
        sRandomizeSetting = self.oIOXml.GetValueOfNodeAttribute(self.oIOXml.GetRootNode(), 'RandomizePageGroups')
        if sRandomizeSetting == 'Y':
            bTestForPrevious = False
        else:
            bTestForPrevious = True
        
        lxPageNodes = self.oIOXml.GetChildren(self.oIOXml.GetRootNode(), 'Page')
        
        # collect all instances of BookmarkID and GoToBookmarkID and which page they are set
        for idxPage in range(len(lxPageNodes)):
            xPageNode = lxPageNodes[idxPage]
        
            sBookmarkID = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'BookmarkID')
            sGoToBookmarkID = ''
            sGoToBookmarkRequest = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'GoToBookmark')
            if sGoToBookmarkRequest != '':
                sGoToBookmarkID = sGoToBookmarkRequest.split()[0]

            if sBookmarkID != '':
                l3tupBookmarkIDs.append([sBookmarkID, idxPage])
            if sGoToBookmarkID != '':
                l3tupGoToBookmarkIDs.append([sGoToBookmarkID, idxPage])
                
            
        # for every instance of GoToBookmarkID, confirm there is a BookmarkID
         
        for idxGoToBookmarkID in range(len(l3tupGoToBookmarkIDs)):
            tupGoToBookmarkIDItem = l3tupGoToBookmarkIDs[idxGoToBookmarkID]
            sGoToBookmarkIDToSearch = tupGoToBookmarkIDItem[0]
            iGoToBookmarkIDPage = tupGoToBookmarkIDItem[1]

            bFoundMatch = False
        
            for idxBookmarkID in range(len(l3tupBookmarkIDs)):
                
                if not bFoundMatch:
                    tupBookmarkIDItem = l3tupBookmarkIDs[idxBookmarkID]
                    sBookmarkIDToCompare = tupBookmarkIDItem[0]
                    iBookmarkIDPage = tupBookmarkIDItem[1]
        
                    if sBookmarkIDToCompare == sGoToBookmarkIDToSearch:
                        if bTestForPrevious:
                            if (iBookmarkIDPage < iGoToBookmarkIDPage):
                                bFoundMatch = True
                                break
                        else:   # randomize is set , ignore page test
                            bFoundMatch = True
       
        
            if not bFoundMatch:
                sMsg = sMsg + "\nMissing historical 'BookmarkID' setting to match 'GoToBookmark': " + sGoToBookmarkIDToSearch \
                            + '\nSee Page #: '\
                            + str(iGoToBookmarkIDPage + 1)
        
        return sMsg
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateDisplayLabelMapID(self):
        ''' For all instances of DisplayLabelMapID, ensure that there is a corresponding
            LabelMapID. This can help trap spelling mistakes. 
            (This is not checked
            for a 'previous instance' of LabelMapID if RandomizePageGroups attribute
            is set to 'Y'.)
        '''
        sMsg = ''
        l3tupDisplayLabelMapIDs = []
        l3tupLabelMapIDs = []
        sRandomizeSetting = self.oIOXml.GetValueOfNodeAttribute(self.oIOXml.GetRootNode(), 'RandomizePageGroups')
        if sRandomizeSetting == 'Y':
            bTestForPrevious = False
        else:
            bTestForPrevious = True
        
        lxPageNodes = self.oIOXml.GetChildren(self.oIOXml.GetRootNode(), 'Page')
        
        # collect all instances of LabelMapID and DisplayLabelMapID and which page they are set
        for idxPage in range(len(lxPageNodes)):
            xPageNode = lxPageNodes[idxPage]
            lxImageNodes = self.oIOXml.GetChildren(xPageNode, 'Image')
    
            for idxImage in range(len(lxImageNodes)):
                xImageNode = lxImageNodes[idxImage]
                sLabelMapID = self.oIOXml.GetValueOfNodeAttribute(xImageNode, 'LabelMapID')
                sDisplayLabelMapID = self.oIOXml.GetValueOfNodeAttribute(xImageNode, 'DisplayLabelMapID')
                xImagePath = self.oIOXml.GetNthChild(xImageNode, 'Path', 0)
                sImagePath = self.oIOXml.GetDataInNode(xImagePath)

                if sLabelMapID != '':
                    l3tupLabelMapIDs.append([sLabelMapID, idxPage, sImagePath])
                if sDisplayLabelMapID != '':
                    l3tupDisplayLabelMapIDs.append([sDisplayLabelMapID, idxPage, sImagePath])
        
        # for every DisplayLabelMapID confirm there is a LabelMapID
        
        for idxDisplayLabelMapID in range(len(l3tupDisplayLabelMapIDs)):
            tupDisplayLabelMapIDItem = l3tupDisplayLabelMapIDs[idxDisplayLabelMapID]
            sDisplayLabelMapIDToSearch = tupDisplayLabelMapIDItem[0]
            iDisplayLabelMapIDPage = tupDisplayLabelMapIDItem[1]
            sDisplayLabelMapIDPath = tupDisplayLabelMapIDItem[2]

            bFoundMatch = False
            for idxLabelMapID in range(len(l3tupLabelMapIDs)):
                
                if not bFoundMatch:
                    tupLabelMapIDItem = l3tupLabelMapIDs[idxLabelMapID]
                    sLabelMapIDToCompare = tupLabelMapIDItem[0]
                    iLabelMapIDPage = tupLabelMapIDItem[1]
                    sLabelMapIDPath = tupLabelMapIDItem[2]
                    
                    if sLabelMapIDToCompare == sDisplayLabelMapIDToSearch:
                        if bTestForPrevious:
                            if (iLabelMapIDPage < iDisplayLabelMapIDPage) and (sLabelMapIDPath == sDisplayLabelMapIDPath):
                                bFoundMatch = True
                                break
                        else:   # randomize is set , ignore page test
                            bFoundMatch = True
            
            if not bFoundMatch:
                sMsg = sMsg + "\nMissing historical 'LabelMapID' setting to match 'DisplayLabelMapID': " + sDisplayLabelMapIDToSearch \
                            + " ...OR... the historical image Path for LabelMapID does not match the image Path where DisplayLabelMapID is requested."\
                            + '\nSee Page #: '\
                            + str(iDisplayLabelMapIDPage + 1)
        
        return sMsg
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateMergeLabelMaps(self, xImage, xPage, iPageNum):
        ''' For the attribute MergeLabeMaps , this function makes sure of the following conditions:
            - EnableSegmentEditor attribute must be turned off (no contouring on a merge display page)
            - there is also a DisplayLabelMapID attribute on that image
            - an historical xml image exists on a page with Loop=Y and with a matching LabelMapID value
            - the PageGroup number must match
            - (Also, the image path of the historical element must match that of the current image -
               This validation is already done in ValidateDisplayLabelMapID)
        '''
        
        sAttributeName = 'MergeLabelMaps'

        sMsg = ''
        sErrorMsgSegmentingNotAllowed = "\n There can be no segmenting on a Page with the 'MergeLabelMaps' attribute"\
                        +"\nThis includes EnableSegmentEditor, SegmentRequired and SegmentRequiredOnAnyImage."
        sErrorMsgInvalidOption = "\nInvalid option - must be 'Y' or 'N'"
        sErrorMsgMissingDisplayLabelMapIDAttribute = "\nImage with 'MergeLabelMaps' attribute must also have the 'DisplayLabelMapID' attribute."
        sErrorMsgNoMatchingHistoricalLabelMapID = "\nThere was no previous Image with a LabelMapID attribute to match the ID in 'DisplayLabelMapID'."
        sErrorMsgNoLoopOnHistoricalPage = "\nYou requested a label map merge but the previous Image with matching LabelMapID was not on a Page with attribute Loop='Y'. No merge can be done."
        sErrorMsgNoMatchingPageGroups = "\nYou requested a label map merge but the PageGroup numbers of this page do not match with the previous page that has the matching LabelMapID."
        sErrorMsgEmptyPageGroups = "\nYou requested a label map merge but the PageGroup numbers of this page are either empty or don't exist. Page Group numbers must match with the previous page that has the matching LabelMapID to be merged."
        sErrorMsgLoopingNotAllowed = "\nThere can not be Looping on a Page with the 'MergeLabelMaps' attribute"
        
        sMergeLabelMaps = self.oIOXml.GetValueOfNodeAttribute(xImage, sAttributeName)

        if sMergeLabelMaps == "Y":                       
            try:
                
                # capture the DisplayLabelMapID attribute for this image
                sLabelMapIDLink = self.oIOXml.GetValueOfNodeAttribute(xImage, 'DisplayLabelMapID')

                if sLabelMapIDLink == '':
                    # missing attribute
                    raise Exception(sErrorMsgMissingDisplayLabelMapIDAttribute)
                
                
                
                if self.oIOXml.GetValueOfNodeAttribute(xPage, 'EnableSegmentEditor') == 'Y' or\
                    self.oIOXml.GetValueOfNodeAttribute(xPage, 'SegmentRequiredOnAnyImage') == 'Y' or\
                    self.oIOXml.GetValueOfNodeAttribute(xImage, 'SegmentRequired') == 'Y' :
                    raise Exception(sErrorMsgSegmentingNotAllowed)

                # look for historical LabelMapID match
                iPageIndex = iPageNum - 1  # zero indexing for current page
                xHistoricalImageElement, xHistoricalPageElement = self.oIOXml.GetXmlPageAndChildFromAttributeHistory(iPageIndex, 'Image','LabelMapID',sLabelMapIDLink)
                if xHistoricalImageElement == None:
                    raise Exception(sErrorMsgNoMatchingHistoricalLabelMapID)
                
                # look for Loop=Y on historical page
                if self.oIOXml.GetValueOfNodeAttribute(xHistoricalPageElement, 'Loop') != "Y":
                    raise Exception(sErrorMsgNoLoopOnHistoricalPage)

                if self.oIOXml.GetValueOfNodeAttribute(xPage, 'Loop') == 'Y':
                    raise Exception(sErrorMsgLoopingNotAllowed)


                # look for matching PageGroup number (these might be empty strings)
                sPageGroupNumToMatch = self.oIOXml.GetValueOfNodeAttribute(xPage, 'PageGroup')
                sHistoricalPageGroupNum = self.oIOXml.GetValueOfNodeAttribute(xHistoricalPageElement, 'PageGroup')
                
                if sPageGroupNumToMatch == sHistoricalPageGroupNum and sPageGroupNumToMatch ==  '':
                    raise Exception(sErrorMsgEmptyPageGroups)
                if sPageGroupNumToMatch != sHistoricalPageGroupNum:
                    raise Exception(sErrorMsgNoMatchingPageGroups)
                
                
            except Exception as error:
                sMsg = str(error) + '\nSee Page #: ' + str(iPageNum) + ' for attribute: ' + sAttributeName + '\n'
         
        else:       
            if (sMergeLabelMaps == '' or sMergeLabelMaps == 'N') == False:
                # not a valid option
                sMsg = sErrorMsgInvalidOption + '\nSee Page #: ' + str(iPageNum) + ' for attribute: ' + sAttributeName + '\n'
                
        
        return sMsg
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateListOfNumbers(self, sString, sType, iLength, sAttributeName, sPageReference):
        # function to validate a string holds a list of values of given type and length
        
        sMsg = ''
        
        lSplitString = sString.split()
        
        # check for required length
        if len(lSplitString) != iLength:
            sMsg = '\nList of numbers does not match required length of ' + str(iLength)\
                     + ' for attribute ' + sAttributeName
        else:
            # check that each entry can be converted to the required type
            try:
                for ind in range(len(lSplitString)):
                    if sType == 'Float':
                        float(lSplitString[ind])
                    elif sType == 'Int':
                        int(lSplitString[ind])
                    else:
                        sMsg = '\nCannot validate this variable type :' + sType
            except:
                sMsg = '\nAttribute ' + sAttributeName + ' does not have valid entries.'\
                        + '\n The required variable type is a list of ' + str(iLength) \
                        +  ' entries of type ' + sType + ' delimited by spaces.'
             
        if sMsg != '':
            sMsg = sMsg + '\n----------See Page: ' + sPageReference

        return sMsg
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateImageToSegmentationMatch(self, xPageNode, sPageReference):
        '''
        '''
        sMsg = ''
        lxAllImages = []
        llDestImageVolume = []
        llDestSegmentation = []
        llDestLabelMap = []
        llDestRTStruct = []
        llDestSegImageType = []
        
        # collect images and their destinations
        lxAllImages = self.oIOXml.GetChildren(xPageNode, 'Image')
        
        for xImage in lxAllImages:
            
            sImageType = self.oIOXml.GetValueOfNodeAttribute(xImage, 'Type')
            xDestination = self.oIOXml.GetNthChild(xImage, 'DefaultDestination', 0)
            sDestination = self.oIOXml.GetDataInNode(xDestination)
            xImagePath = self.oIOXml.GetNthChild(xImage, 'Path', 0)
            sImagePath = self.oIOXml.GetDataInNode(xImagePath)
            
            if sImageType == 'Volume' or sImageType == 'VolumeSequence':
                llDestImageVolume.append([sDestination, sImagePath])
            elif sImageType == 'Segmentation':
                llDestSegmentation.append([sDestination, sImagePath])
            elif sImageType == 'LabelMap':
                llDestLabelMap.append([sDestination, sImagePath])
            elif sImageType == 'RTStruct':
                llDestRTStruct.append([sDestination, sImagePath])
                

            
           
        sSegmentationMsg = self.SyncSegsAndVolumes(llDestImageVolume, 'Segmentation', llDestSegmentation)
        
        sLabelMapMsg = self.SyncSegsAndVolumes(llDestImageVolume, 'LabelMap', llDestLabelMap)
        
        sRTStructMsg = self.SyncSegsAndVolumes(llDestImageVolume, 'RTStruct', llDestRTStruct)

        sMsg = sMsg + sSegmentationMsg + sLabelMapMsg + sRTStructMsg
        if sMsg != '':
            sMsg = sMsg + '\n----------See Page: ' + sPageReference

        return sMsg
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateROIColorFile(self, sFilePath):
        
        # color files cannot use an ID = 0 
        # using ID=0 will cause images to disappear when segment editor is started
        # syntax: id descriptor r g b a
        # lines beginning with '#' are comments
        sMsg = ''
        
        fh = open(sFilePath, "r")
        lLines = fh.readlines()
        
        for sLine in lLines:
            if sLine[:1] == "#":
                pass
            elif sLine[:1] == "0":
                sMsg = "ROI Color File cannot have an entry with ID = '0'" \
                        + "\n See file " + sFilePath
                break
            else:
                pass
            
        return sMsg
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SyncSegsAndVolumes(self, llDestImageVolume, sSegImageType, llDestSegImageType):
        
        sMsg = ''
        bMismatchFound = False
        
        for indSegTypeToMatch in range(len(llDestSegImageType)):
            if not bMismatchFound:
                # there must be an image volume to sync with the  destination of this segmentation type of image
                sSegTypeDestToMatch = llDestSegImageType[indSegTypeToMatch][0]
                sSegTypePathToMatch = llDestSegImageType[indSegTypeToMatch][1]
                lDestMatchedVolImagePaths = []
                
                for indVol in range(len(llDestImageVolume)):
                    if llDestImageVolume[indVol][0] == sSegTypeDestToMatch:
                        lDestMatchedVolImagePaths.append(llDestImageVolume[indVol][1])
                        
                        
                if len(lDestMatchedVolImagePaths) > 0:        
                    # image volumes found at that destination
                    # there may have been more than one image found (FG and BG)
                    # check if they are repeated in another destination
                    lAllDests = []
                    for indMatchedPath in range(len(lDestMatchedVolImagePaths)):
                        sMatchedVolPathToSearch = lDestMatchedVolImagePaths[indMatchedPath]
                        for indMatchedPath in range(len(llDestImageVolume)):
                            if sMatchedVolPathToSearch == llDestImageVolume[indMatchedPath][1]:
                                if llDestImageVolume[indMatchedPath][0] not in lAllDests: # only keep FG or BG
                                    lAllDests.append(llDestImageVolume[indMatchedPath][0])
                    
                        if len(lAllDests) > 0:
                            # the same image volume is repeated in other destinations
                            # there needs to be the same seg type image in those destinations
                            iNumMatches = 0
                            for indDest in range(len(lAllDests)):
                                sDest = lAllDests[indDest]
                                for indSeg in range(len(llDestSegImageType)):
                                    if (sSegTypePathToMatch == llDestSegImageType[indSeg][1]):
                                        if llDestSegImageType[indSeg][0] == sDest:
                                            iNumMatches = iNumMatches + 1
                            
                        if iNumMatches == len(lAllDests):
                            pass
                        else:
                            sMsg = sMsg + '\n\nYou do not have a ' + sSegImageType + ' xml entry for each ' +\
                                    'of the associated image volume entries.' +\
                                    '\n(eg. If Vol1 is on Red and Green; there must be the same ' + sSegImageType + ' entry for each of these destinations' +\
                                    '\n.....Images defined as ' + sSegImageType + ' and Volumes are not in sync.'
                            bMismatchFound = True
                            break
        
                            
                        
                        
                        
                else:
                    sMsg = sMsg + '\n\nYou have a ' + sSegImageType + ' type of image defined in the xml ' +\
                            '\nwith no matching volume in the same default destination.' +\
                            '\n.....Images defined as ' + sSegImageType + ' and Volumes are not in sync.'
                            
                

       
        
        return sMsg
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ExportResultsItemToFile(self, sItemName, sPath, slNode):
        """ Use Slicer's storage node to export node to a file
        """
        
        sMsg = ''
        bSuccess = True
        
        try:
            slStorageNode = slNode.CreateDefaultStorageNode()
            slStorageNode.SetFileName(sPath)
            slStorageNode.WriteData(slNode)
            slStorageNode.UnRegister(slicer.mrmlScene) # for memory leaks
            
        except Exception as error:
            tb = traceback.format_exc()
            sMsg = '\nExportResultsItemToFile: Failed to store ' + sItemName + ' as file: \n' + sPath \
                    + str(error) \
                    + "\n\n" + tb 
            self.oUtilsMsgs.DisplayError(sMsg)
    
        return bSuccess, sMsg
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CheckForLoadedNodeInScene(self, sFilenameNoExt):
        """ A label map or markup line is stored on disk with the same name as the node in the mrmlScene.
            Using the filename for the entity (with no extension) check if it is already
            loaded into the scene.
        """
        bFound = False
        slNode = None
        
        slNodesCollection = slicer.mrmlScene.GetNodesByName(sFilenameNoExt)

        if slNodesCollection.GetNumberOfItems() == 1:
            bFound = True
            slNode = slNodesCollection.GetItemAsObject(0)

        # for memory leak
        slNodesCollection.UnRegister(slicer.mrmlScene)
              
        return bFound, slNode

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
    #-------------------------------------------
    #        LabelMap Functions
    #-------------------------------------------

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SaveLabelMaps(self, oSession, sCaller):

        """ label map volume nodes may exist in the mrmlScene if the user created a label map
            (in which case it is named with a '-bainesquizlabel' suffix), or if a label map 
            or segmentation was loaded in through the xml quiz file.
            
            This function looks for label maps created by the user (-bainesquizlabel suffix) 
            and if found, saves them as a data volume  (.nrrd file) in the specified directory.
            The path to this file is then stored in the xml file within the associated image element.
            
            Also store label maps as RTStructs if the attribute to do so was set in the xml root node.
            
            A warning is presented if the xml question set had the 'EnableSegmentEditor' flag set to 'y'
            but no label maps (with -bainesquizlabel suffix) were found. The user purposely may 
            not have created a label map if there were no lesions to segment. This is acceptable.
        """
            
        bLabelMapsSaved = True # initialize
        
        bLabelMapFound = False  # to detect if label map was created by user
 
        # capture the names of the images that have had the label maps stored
        #    the list of image nodes may repeat the same image if being viewed in 
        #    multiple windows
        lsLabelMapsStoredForImages = [] # initialize for each label map

        # get list of label maps to save
        lSlicerLabelMapNodes = slicer.util.getNodesByClass('vtkMRMLLabelMapVolumeNode')
         
        # if list length > 0, create folder to hold labels
        if len(lSlicerLabelMapNodes) > 0:
            
            for oImageNode in oSession.oImageView.GetImageViewList():
                  
                for slNodeLabelMap in lSlicerLabelMapNodes:

                    # match label map file with xml image
                    sLabelMapFilename = slNodeLabelMap.GetName()
                    if oImageNode.sNodeName + '-bainesquizlabel' == sLabelMapFilename:
                        
                        bLabelMapFound = True  # -bainesquizlabel suffix is associated with an image on the page
                        
                        sDirName = self.GetFolderNameForPageResults(oSession)
                        sPageLabelMapDir = self.CreatePageDir(sDirName)
                        sLabelMapFilenameWithExt = sLabelMapFilename + '.nrrd'
                        sLabelMapPath = os.path.join(sPageLabelMapDir, sLabelMapFilenameWithExt)
                        
                        if not oImageNode.sNodeName in lsLabelMapsStoredForImages:
                            # save the label map file to the user's page directory
                            self.ExportResultsItemToFile('LabelMap', sLabelMapPath, slNodeLabelMap) 
                         
                            # update list of names of images that have the label maps stored
                            lsLabelMapsStoredForImages.append(oImageNode.sNodeName)


                        #    add the label map path element to the image element in the xml
                        #    only one label map path element is to be recorded
                        xLabelMapPathElement = self.oIOXml.GetLastChild(oImageNode.GetXmlImageElement(), 'LabelMapPath')
                        
                        if xLabelMapPathElement == None:
                            # update xml storing the path to the label map file with the image element
                            oSession.AddPathElement('LabelMapPath', oImageNode.GetXmlImageElement(),\
                                                 self.GetRelativeUserPath(sLabelMapPath))
                            
                            

        if sCaller != 'ResetView':   # warning not required on a reset
    
            #####
            # Display warning if segmentation was required but no user created label map was found.
            #####
            #    If there were no label map volume nodes 
            #    OR if there were label map volume nodes, but there wasn't a -bainesquizlabel suffix 
            #        to match an image on the page, ie. the labelMaps found flag was left as false
            #    Check if the segmentation was required and if enabled present the warning
            if len(lSlicerLabelMapNodes) == 0 or (len(lSlicerLabelMapNodes) > 0 and bLabelMapFound == False):    
                
                # user doesn't get the option to cancel if the call was initiated 
                # from the Close event filter
                if sCaller != 'EventFilter':
                    if oSession._bSegmentationModule == True:   # if there is a segmentation module
                        if oSession.GetSegmentationTabEnabled() == True:    # if the tab is enabled
                            qtAns = oSession.oUtilsMsgs.DisplayOkCancel(\
                                                'No contours were created. Do you want to continue?')
                            if qtAns == qt.QMessageBox.Ok:
                                # user did not create a label map but there may be no lesions to segment
                                # continue with the save
                                bLabelMapsSaved = True
                            else:
                                # user wants to resume work on this page
                                bLabelMapsSaved = False
                    
                    
        if bLabelMapsSaved == True:
            oSession.oIOXml.SaveXml(oSession.oFilesIO.GetUserQuizResultsPath())

        return bLabelMapsSaved
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def LoadSavedLabelMaps(self, oSession):
        # when loading label maps created in the quiz, associate it with the correct 
        #    image node in the subject hierarchy
        # add it to the slquizlabelmap property of the image node 



        lLoadedLabelMaps = []

        for oImageNode in oSession.oImageView.GetImageViewList():
            
            # for each image view, get list of labelmap files stored (may be more than one)
            if (oImageNode.sImageType == 'Volume' or oImageNode.sImageType == 'VolumeSequence'):

                # read attribute from xml file whether to use label maps previously created
                #    by the user in the quiz for this image
                sLabelMapIDLink = '' # initialize
                sLabelMapIDLink = oSession.oIOXml.GetValueOfNodeAttribute(oImageNode.GetXmlImageElement(), 'DisplayLabelMapID')
                if sLabelMapIDLink != '':
                    bUsePreviousLabelMap = True
                else:
                    bUsePreviousLabelMap = False

        
                # look at latest instance of the label map elements stored in the xml
                xLabelMapPathElement = oSession.oIOXml.GetLatestChildElement(oImageNode.GetXmlImageElement(), 'LabelMapPath')
                slLabelMapNode = None # initialize

                # if there were no label map paths stored with the image, and xml attribute has DisplayLabelMapID 
                #    to use a previous label map, check previous pages for the first matching image
                if (xLabelMapPathElement == None and bUsePreviousLabelMap == True)\
                    or (bUsePreviousLabelMap == True and oImageNode.bMergeLabelMaps):

                    # get image element from history that holds the same label map id; 
                    xHistoricalImageElement = None  # initialize
                    xHistoricalLabelMapMatch = None
                    # xHistoricalImageElement = oSession.GetXmlElementFromAttributeHistory('Image','LabelMapID',sLabelMapIDLink)
                    xHistoricalImageElement, xHistoricalPageElement = oSession.oIOXml.GetXmlPageAndChildFromAttributeHistory(oSession.GetCurrentPageIndex(),'Image','LabelMapID',sLabelMapIDLink)

                    if oImageNode.bMergeLabelMaps:
                        # combine label maps and store on disk
                        xLabelMapPathElement = self.MergeLabelMapsAndSave(oSession, oImageNode, xHistoricalImageElement, xHistoricalPageElement)
                        
                        
                    else:
                        # load single label map
                        if xHistoricalImageElement != None:
                            xHistoricalLabelMapMatch = oSession.oIOXml.GetLatestChildElement(xHistoricalImageElement, 'LabelMapPath')
                        
                        if xHistoricalLabelMapMatch != None:
                            # found a label map for this image in history
                            # copy to disk and store it in xml for the current image
                            self.CopyAndStoreLabelMapFromHistory(oSession, xHistoricalLabelMapMatch, oImageNode)
    
                            #    assign newly stored xml element to xLabelMapPathElement
                            xLabelMapPathElement = oSession.oIOXml.GetLatestChildElement( oImageNode.GetXmlImageElement(), 'LabelMapPath')
                    
                
                # load labelmap file from stored path in XML                
                if xLabelMapPathElement != None:
                    sStoredRelativePath = oSession.oIOXml.GetDataInNode(xLabelMapPathElement)
                    
                    # check if label map was already loaded (if between question sets, label map will persisit)
                    sLabelMapNodeName = self.GetFilenameNoExtFromPath(sStoredRelativePath)
                    bFoundLabelMap, slLabelMapNode = self.CheckForLoadedNodeInScene(sLabelMapNodeName)

                    # only load the label map once
                    if not sStoredRelativePath in lLoadedLabelMaps:
                        sAbsolutePath = self.GetAbsoluteUserPath(sStoredRelativePath)
                        dictProperties = {'LabelMap' : True}
                        
                        try:

                            if not bFoundLabelMap:
                                if os.path.exists(sAbsolutePath):
                                    # load label map into the scene
                                    slLabelMapNode = slicer.util.loadLabelVolume(sAbsolutePath, dictProperties)
                                else:
                                    sMsg = 'Stored path to label map file does not exist. Label map will not be loaded.\n' \
                                        + sAbsolutePath
                                    oSession.oUtilsMsgs.DisplayWarning(sMsg)
                                    break # continue in for loop for next label map path element
                            
                            
                            lLoadedLabelMaps.append(sStoredRelativePath)
    
                            # set associated volume to connect label map to master
                            sLabelMapNodeName = slLabelMapNode.GetName()
#                             sAssociatedName = sLabelMapNodeName.replace('-bainesquizlabel','')
                            sAssociatedName = oImageNode.sNodeName
                            slAssociatedNodeCollection = slicer.mrmlScene.GetNodesByName(sAssociatedName)
                            slAssociatedNode = slAssociatedNodeCollection.GetItemAsObject(0)
                            slLabelMapNode.SetNodeReferenceID('AssociatedNodeID',slAssociatedNode.GetID())

                            # apply ROIColor table to label map display node
                            slLabelMapDisplayNode = slLabelMapNode.GetDisplayNode()
                            slColorLogic = slicer.modules.colors.logic()
                            slColorNode = slColorLogic.LoadColorFile(self.GetQuizzerROIColorTablePath())
                            slLabelMapDisplayNode.SetAndObserveColorNodeID(slColorNode.GetID())
    
    
                        except:
                             
                            sMsg = 'Trouble loading label map file:' + sAbsolutePath
                            oSession.oUtilsMsgs.DisplayWarning(sMsg)
                           

                # add the label map node to the image property so that it gets
                #    set when assigning nodes to the viewing widgets (red, green, yellow)
                # the node may be None (no label map path was stored)
                oImageNode.SetQuizLabelMapNode(slLabelMapNode)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CopyAndStoreLabelMapFromHistory(self, oSession, xHistoricalLabelMapElement, oImageNode):

        # define source for copy
        sStoredRelativePathForSource = oSession.oIOXml.GetDataInNode(xHistoricalLabelMapElement)
        sAbsolutePathForSource = oSession.oFilesIO.GetAbsoluteUserPath(sStoredRelativePathForSource)

        # create new folder for destination based on current page information
        sCurrentLabelMapFolderName = self.GetFolderNameForPageResults(oSession)
        sLabelMapDirForDest = self.CreatePageDir(sCurrentLabelMapFolderName)
        
        # create new file name to which the historical label map is to be copied
        sLabelMapFilenameWithExtForDest = oImageNode.sNodeName + '-bainesquizlabel' + '.nrrd'
        
        # define destination path
        sLabelMapPathForDest = os.path.join(sLabelMapDirForDest, sLabelMapFilenameWithExtForDest)

        # check if exists
        if not os.path.exists(sLabelMapPathForDest):
        
            # copy source to dest
            shutil.copy(sAbsolutePathForSource, sLabelMapPathForDest)

        # update xml storing the path to the label map file with the image element
        #    for display on the next page
        oSession.AddPathElement('LabelMapPath', oImageNode.GetXmlImageElement(), self.GetRelativeUserPath(sLabelMapPathForDest))


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def MergeLabelMapsAndSave(self, oSession, oImageNode, xHistoricalImageElement, xHistoricalPageElement):
        ''' This function will search for all Pages with the same 'base' name as the historical page that
            was found to have the matching LabelMapID for the DisplayLabelMapID.
            The base name is the PageID_Descriptor without the '-Rep##' which is added when using the Repeat button.
            From these pages, collect the LabelMapPath values for the Images with the matching LabelMapID
            and merge these.
            The merged label map is then saved to disk and the current ImageElement is updated with a new LabelMapPath element. 
        '''

        try:        
            xLabelMapPathElement = None
            lsLabelMapFullPaths = []
            
            # Search for all previous Pages that match PageID_Descriptor (without the -Rep## substring)
            sPageIDToSearch = oSession.oIOXml.GetValueOfNodeAttribute(xHistoricalPageElement, 'ID')
                        # remove ignore string
            reIgnoreSubstring= '-Rep[0-9]+'  # remove -Rep with any number of digits following
            sPageIDToSearchStripped = re.sub(reIgnoreSubstring,'',sPageIDToSearch)
            sPageDescriptorToSearch = oSession.oIOXml.GetValueOfNodeAttribute(xHistoricalPageElement, 'Descriptor')
    
            dictAttribToMatch = {}
            dictAttribToMatch['ID'] = sPageIDToSearchStripped
            dictAttribToMatch['Descriptor'] = sPageDescriptorToSearch
    
            sLabelMapIDToMatch = oSession.oIOXml.GetValueOfNodeAttribute(xHistoricalImageElement, 'LabelMapID')
            
            
            # collect label map paths
            lMatchingPageNodes = oSession.oIOXml.GetMatchingXmlPagesFromAttributeHistory(oSession.GetCurrentPageIndex(), dictAttribToMatch, reIgnoreSubstring)
            for xPageNode in lMatchingPageNodes:
                
                lxImageElements = oSession.oIOXml.GetChildren(xPageNode, 'Image')
    
                for xImage in lxImageElements:
                    sLabelMapID = oSession.oIOXml.GetValueOfNodeAttribute(xImage,'LabelMapID')
    
                    if sLabelMapID == sLabelMapIDToMatch:
                        lxLabelMapPath = self.oIOXml.GetChildren(xImage, 'LabelMapPath')
    
                        for xPath in lxLabelMapPath:
                            sLabelMapPath = oSession.oIOXml.GetDataInNode(xPath)
                            sLabelMapFullPath = os.path.join(oSession.oFilesIO.GetUserDir(), sLabelMapPath)
                            lsLabelMapFullPaths.append(sLabelMapFullPath)
            
            
            # use SimpleITK to collect all matching images
            litkAllLabelImages = []
            for sPath in lsLabelMapFullPaths:
                itkLabelImage = sitk.ReadImage(sPath)
                litkAllLabelImages.append(itkLabelImage)
                
    
            # merge label maps
    
            ''' Merging methodology:
                initialize combined map (C) with the first image (A)
                For each labelmap (B), take the difference (Diff = B - C)
                    -In Diff, Any existing LM pixels from C will be marked as the -ve value of its label
                    - Any new LM pixels from B will be marked with its LM value
                    - Any overlap, will now have an offset value 
                        - example label 5 (from B) overlapped label 3 (in C) - offset = 2
                        - Example, label 2 (from B) overlapped label 5  (in C) - offset=-3
    
                Create offset array --> Reset all -ve pixels to 0 (they won't be added into the combined LM array)
                    - (-ve values from overlap means that it was a smaller label map value and is to be 'ignored', allowing the higher value (already in C) to take priority)
                Update the combined array C)
    
            '''
    
            dictProperties = {'LabelMap' : True}
            if len(lsLabelMapFullPaths) > 0:

                slLabelMapVolumeReference = slicer.util.loadLabelVolume(lsLabelMapFullPaths[0], dictProperties)

                # create temporary label map nodes
                slLabelMapVolumeCombined = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLabelMapVolumeNode')
                slLabelMapVolumeCombined.CopyOrientation(slLabelMapVolumeReference)
                
                # use numpy to combine label maps
                np_combined = sitk.GetArrayFromImage(litkAllLabelImages[0])     # initialize
                for image in litkAllLabelImages:
                    np_img_arr = sitk.GetArrayFromImage(image)
                    np_diff_arr = np_img_arr - np_combined
                    np_diff_offset =  np.where(np_diff_arr <0, 0, np_diff_arr)
                    np_combined = np_combined + np_diff_offset
                    
                slicer.util.updateVolumeFromArray(slLabelMapVolumeCombined, np_combined)
            
                
                
                # save new labelmap to disk
                sDirName = self.GetFolderNameForPageResults(oSession)
                sPageLabelMapDir = self.CreatePageDir(sDirName)
        
                sLabelMapFilenameWithExt = oImageNode.sNodeName + '-bainesquizlabel.nrrd'
                
                
                sLabelMapPath = os.path.join(sPageLabelMapDir, sLabelMapFilenameWithExt)
                
                
                # if merge was already done and a label map already exists, delete it and save the new merge
                #    this allows the user to make any corrections to contours using the previous button
                
                if os.path.exists(sLabelMapPath):
                    os.remove(sLabelMapPath)
        
                self.ExportResultsItemToFile('LabelMap', sLabelMapPath, slLabelMapVolumeCombined)
        
                # update xml storing the path to the label map file with the image element
                #    for display on the next page
                oSession.AddPathElement('LabelMapPath', oImageNode.GetXmlImageElement(), self.GetRelativeUserPath(sLabelMapPath))
                oSession.oIOXml.SaveXml(oSession.oFilesIO.GetUserQuizResultsPath())
                xLabelMapPathElement = oSession.oIOXml.GetLatestChildElement(oImageNode.GetXmlImageElement(), 'LabelMapPath')
        
                # cleanup
                slicer.mrmlScene.RemoveNode(slLabelMapVolumeReference)
                slicer.mrmlScene.RemoveNode(slLabelMapVolumeCombined)
            
        except Exception as error:
            tb = traceback.format_exc()
            sMsg = "MergeLabelMapsAndSave: Error while merging label maps."  \
                    + str(error) \
                    + "\n\n" + tb 
            self.oUtilsMsgs.DisplayError(sMsg)


        
        return xLabelMapPathElement
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
    #-------------------------------------------
    #        MarkupsLine Functions
    #-------------------------------------------

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SaveMarkupLines(self, oSession):
        ''' This function will capture all markup lines, rename them to reflect the associated 
            reference node and save them in the json format.
        '''
        
        try:
            lsMarkupLineNodes = slicer.util.getNodesByClass('vtkMRMLMarkupsLineNode')
    
            for slMarkupLine in lsMarkupLineNodes:
                iNumPoints = slMarkupLine.GetNumberOfControlPoints()
                
                # only work with nodes that have 2 points
                #    -    just adding the line tool can create a null markup line node (0 control points)
                if iNumPoints == 2:
                    sAssociatedReferenceNodeID = slMarkupLine.GetNthControlPointAssociatedNodeID(0)
                    sAssociatedReferenceNodeName = slicer.mrmlScene.GetNodeByID(sAssociatedReferenceNodeID).GetName()
                    # update markup line name with associated node only if not already done
                    if slMarkupLine.GetName().find(sAssociatedReferenceNodeName) == -1: 
                        
                        # check the scene if the name already exists
                        #    - if not all lines are created yet and user moves between Next and Previous, a 
                        #    newly created markup line node may be created with the same base name ('MarkupsLine'),
                        #    so a suffix needs to be added to the new line name
                        sLineName = self.CreateUniqueLineName(lsMarkupLineNodes, slMarkupLine.GetName(), sAssociatedReferenceNodeName)
                        slMarkupLine.SetName(sLineName)
                
                    # save the markup line in the directory
                    sDirName = self.GetFolderNameForPageResults(oSession)
                    sPageMarkupsLineDir = self.CreatePageDir(sDirName)
        
                    sMarkupsLineFilenameWithExt = slMarkupLine.GetName() + '.mrk.json'
                                 
                    # save the markup line file to the user's page directory
                    sMarkupsLinePath = os.path.join(sPageMarkupsLineDir, sMarkupsLineFilenameWithExt)
        
                     
                
                    for oImageNode in oSession.oImageView.GetImageViewList():
                        
                        # match the markup line to the image to save the path to the correct xml Image node
                        if slicer.mrmlScene.GetNodeByID(sAssociatedReferenceNodeID).GetName() == oImageNode.sNodeName:
                            self.ExportResultsItemToFile('MarkupsLine', sMarkupsLinePath, slMarkupLine)

                            # store the path name in the xml file
                                
                            sRelativePathToStoreInXml = self.GetRelativeUserPath(sMarkupsLinePath)
                            lxLinePathElements = self.oIOXml.GetChildren(oImageNode.GetXmlImageElement(), 'MarkupLinePath')
                            bPathAlreadyInXml = False
                            for xPathElement in lxLinePathElements:
                                sStoredRelativePath = self.oIOXml.GetDataInNode(xPathElement)
                                if sStoredRelativePath == sRelativePathToStoreInXml:
                                    bPathAlreadyInXml = True
                                    break
                                
                            if bPathAlreadyInXml == False:   
                                # update xml storing the path to the markup line file with the image element
                                oSession.AddPathElement('MarkupLinePath', oImageNode.GetXmlImageElement(),
                                                        sRelativePathToStoreInXml)
            
                oSession.oIOXml.SaveXml(oSession.oFilesIO.GetUserQuizResultsPath())
            
            
        except Exception as error:
            tb = traceback.format_exc()
            sMsg = "\nSaveMarkupLines: Error saving markup lines to disk. "  \
                    + str(error) \
                    + "\n\n" + tb 
            raise Exception(sMsg)
            
        return

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CreateUniqueLineName(self, lAllNodeNamesInScene, sSystemGeneratedName, sAssociatedReferenceNodeName):
        ''' Input parameters:
                - list of all nodes in the scene
                - the system generated node name to be changed
                - name of the associated image node
            If there is already a node that has the proposed name, we need to add the 'next' integer suffix
        '''

        sProposedName =  sAssociatedReferenceNodeName  + '_' + sSystemGeneratedName + '_bainesquizline'
        sUniqueName = sProposedName # default
         
        lExistingNamesWithProposedName = []
        for slNode in lAllNodeNamesInScene:
            if slNode.GetName().find(sProposedName) >= 0:
                lExistingNamesWithProposedName.append(slNode.GetName())
                
        if len(lExistingNamesWithProposedName) > 0:
            sSubstringToSearch = 'bainesquizline_'
            iNewSuffix = self.GetSuffix(lExistingNamesWithProposedName, sSubstringToSearch)
            if iNewSuffix > 0:
                sUniqueName = sProposedName + '_' + str(iNewSuffix)

        return sUniqueName
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetSuffix(self, lExistingNamesWithProposedName, sSubstringToSearch ):
    
        iNextInteger = 0
        
        if len(lExistingNamesWithProposedName) > 0:
            lExistingSuffixes = []
            for sName in lExistingNamesWithProposedName:
                # extract existing numeric suffix if there is one
                iSubstringStart = sName.find(sSubstringToSearch)
                if iSubstringStart >= 0:
                    iSuffixStart = iSubstringStart + len(sSubstringToSearch)
                    sSuffix = sName[iSuffixStart :]
                    if sSuffix.isdigit():
                        lExistingSuffixes.append(int(sSuffix))
                
            if len(lExistingSuffixes) > 0:
                iNextInteger = max(lExistingSuffixes) + 1
            else:
                iNextInteger = 1
    
        return iNextInteger
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def LoadSavedMarkupLines(self, oSession):
        ''' Scan the xml for markup line path elements and load the saved file.
        '''
        lxImageElements = []
        lxMarkupLinePaths = []
        
        lxImageElements = self.oIOXml.GetChildren( oSession.GetCurrentPageNode(), 'Image')
        
        for  xImageNode in lxImageElements:
            
            lxMarkupLinePaths = self.oIOXml.GetChildren( xImageNode, 'MarkupLinePath')
            
            for xLinePathNode in lxMarkupLinePaths:
                
                sStoredRelativePath = self.oIOXml.GetDataInNode( xLinePathNode )
                if sStoredRelativePath != '':
                    sAbsolutePath = self.GetAbsoluteUserPath(sStoredRelativePath)
                    
                    # check that the markup line does not already exist in the scene 
                    #    (if relative path has double extension .mrk.json - additional remove .mrk)
                    sMarkupLineNodeName = self.GetFilenameNoExtFromPath(sStoredRelativePath)
                    if sMarkupLineNodeName.endswith('.mrk') and sMarkupLineNodeName != '.mrk':
                        sMarkupLineNodeName = sMarkupLineNodeName[:-len('.mrk')]
                    bFoundMarkupLine, slMarkupLineNode = self.CheckForLoadedNodeInScene(sMarkupLineNodeName)
                    
                    if not bFoundMarkupLine:
                        if os.path.exists(sAbsolutePath):
                            # load label map into the scene
                            slMarkupLineNode = slicer.util.loadMarkups(sAbsolutePath)
                        else:
                            sMsg = 'Stored path to markup line file does not exist. Markup line will not be loaded.\n' \
                                + sAbsolutePath
                            oSession.oUtilsMsgs.DisplayWarning(sMsg)
                            break # continue in for loop for next label map path element
                
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetupLoopingInitialization(self, xRootNode):
        
        # if Loop="Y" for any page in the quiz, add Rep="0" to each page if not defined
        
        bLoopingInQuiz = False
        lxPages = self.oIOXml.GetChildren(xRootNode,'Page')
        for xPageNode in lxPages:
            sLoopAllowed = self.oIOXml.GetValueOfNodeAttribute(xPageNode, "Loop")
            if sLoopAllowed == "Y":
                bLoopingInQuiz = True
                break
            
        if bLoopingInQuiz:
            for xPageNode in lxPages:
                sRepNum = self.oIOXml.GetValueOfNodeAttribute(xPageNode, "Rep")
                try:
                    int(sRepNum)
                except:
                    # not a valid integer - create/set the attribute to 0
                    self.oIOXml.UpdateAttributesInElement(xPageNode, {"Rep":"0"})
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetupPageGroupInitialization(self, xRootNode):
        ''' If no PageGroup attribute exists, update the XML to initialize each page
            to a unique number. Start PageGroup numbers at '1'. ('0' has specialized
            meaning when randomizing page groups.
        '''
        
        bPageGroupFound = False
         
        lxPages = self.oIOXml.GetChildren(xRootNode,'Page')
        for xPageNode in lxPages:
            sPageGroupNum = self.oIOXml.GetValueOfNodeAttribute(xPageNode, "PageGroup")
            if sPageGroupNum != '':
                bPageGroupFound = True
                break
       
        if not bPageGroupFound:
            for iPageNum in range(len(lxPages)):
                xPageNode = self.oIOXml.GetNthChild(xRootNode, "Page", iPageNum)
                self.oIOXml.UpdateAttributesInElement(xPageNode, {"PageGroup":str(iPageNum + 1)})
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
