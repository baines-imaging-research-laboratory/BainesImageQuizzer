import os, sys
import warnings
import vtk, qt, ctk, slicer

from Utilities import *

from shutil import copyfile
import shutil

from datetime import datetime
import DICOMLib
from DICOMLib import DICOMUtils

# import pydicom
# try:
#     import pandas as pd
# 
#     print("running with pandas")
# except ImportError:
#     print("!"*100, 'pandas not installed')
# 
# try:
#     import numpy as np
#     print("running with numpy")
# except ImportError:
#     print("!"*100, 'numpy not installed')


import logging
# import threading
import time

import DicomRtImportExportPlugin
import DICOMVolumeSequencePlugin


##########################################################################
#
#   class UtilsIO
#
##########################################################################

class UtilsIO:
    """ Class UtilsIO
        - to set up path and filenames for the Image Quizzer module
        - to handle disk input/output
    """
    
    def __init__(self, parent=None):
        self.parent = parent
        
        self._sScriptedModulesPath = ''     # location of quizzer module project

        self._sXmlResourcesDir = ''         # folder - holds XML quiz files to copy to user
        self._sResourcesQuizPath = ''       # full path (dir/file) of quiz to copy to user
        self._sQuizFilename = ''            # quiz filename only (no dir)

        self._sDataParentDir = ''           # parent folder to images, DICOM database and users folders
        
        self._sUsersParentDir = ''          # folder - parent dir to all user folders
        self._sUsername = ''                # name of user taking the quiz
        self._sUserDir = ''                 # folder - holds quiz subfolders for specific user

        self._sUserQuizResultsDir = ''      # folder for quiz results
        self._sUserQuizResultsPath = ''     # full path (dir/file) for user's quiz results

        self._sDICOMDatabaseDir = ''
#         self._sImageVolumeDataDir = ''

        self._sResourcesROIColorFilesDir = ''  # folder to the Quizzer specific roi color files
        self._sQuizzerROIColorTableNameWithExt = 'QuizzerROIColorTable.txt'
        self._sDefaultROIColorTableName = 'GenericColors'

        self._liPageGroups = []
        self._liUniquePageGroups = []

        self.oUtilsMsgs = UtilsMsgs()
        self.oIOXml = UtilsIOXml()

        self.setupTestEnvironment()



        
        
    def setupTestEnvironment(self):
         # check if function is being called from unittesting
        if "testing" in os.environ:
            self.sTestMode = os.environ.get("testing")
        else:
            self.sTestMode = "0"

 
        
    #-------------------------------------------
    #        Getters / Setters
    #-------------------------------------------
    
    #----------
    def SetDataParentDir(self, sDataDirInput):
        self._sDataParentDir = sDataDirInput
        
    #----------
    def SetResourcesQuizPathAndFilename(self, sSelectedQuizPath):

        self._sResourcesQuizPath = os.path.join(self._sXmlResourcesDir, sSelectedQuizPath)
        self._sDir, self._sQuizFilename = os.path.split(self._sResourcesQuizPath)
        
    #----------
    def SetUsernameAndDir(self, sSelectedUser):
        self._sUsername = sSelectedUser
        self._sUserDir = os.path.join(self.GetUsersParentDir(), self._sUsername)
        
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
    def GetDefaultROIColorTableName(self):
        return self._sDefaultROIColorTableName
    
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
    
    
#     ###################
#     #----------
#     def SetUserQuizResultsDir(self, sFilename):
#         self._sUserQuizResultsDir = os.path.join(self.GetUserDir(), sFilename)
#         
#     #----------
#     def SetUserQuizResultsPath(self, sFilename):
#         
#         self._sUserQuizResultsPath = os.path.join(self.GetUserQuizResultsDir(), sFilename)
#     #####################
    
    
    
    #----------
    def SetupForUserQuizResults(self):
        

        sQuizFileRoot, sExt = os.path.splitext(self.GetQuizFilename())
        
        self._sUserQuizResultsDir = os.path.join(self.GetUserDir(), sQuizFileRoot)
        self._sUserQuizResultsPath = os.path.join(self.GetUserQuizResultsDir(), self.GetQuizFilename())

        # check that the user folder exists - if not, create it
        if not os.path.exists(self._sUserQuizResultsDir):
            os.makedirs(self._sUserQuizResultsDir)
        
    
    #----------
    def CreatePageDir(self, sPageName):
        # page dir stores label maps for the specified page
        # store these in the user directory
        sPageDir = os.path.join(self.GetUserDir(), sPageName)
        
        # check that the Page directory exists - if not create it
        if not os.path.exists(sPageDir):
            os.makedirs(sPageDir)
    
        return sPageDir

    
    #----------

    #----------
    def GetDataParentDir(self):
        return self._sDataParentDir

    #----------
    def GetDICOMDatabaseDir(self):
        return self._sDICOMDatabaseDir
    
    #----------
    def GetDirFromPath(self, sFullPath):
        head, tail = os.path.split(sFullPath)
        return head
    
#     #----------
#     def GetImageVolumeDataDir(self):
#         return self._sImageVolumeDataDir

    #----------
    def GetScriptedModulesPath(self):
        return self._sScriptedModulesPath
    
    #----------
    def GetResourcesQuizPath(self):
        return self._sResourcesQuizPath
    
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
    def GetXmlResourcesDir(self):
        return self._sXmlResourcesDir
    
    #----------
    def GetRelativeUserPath(self, sInputPath):
        # remove absolute path to user folders
        return sInputPath.replace(self.GetUserDir()+'\\','')

    #----------
    def GetAbsoluteDataPath(self, sInputPath):
        return os.path.join(self._sDataParentDir, sInputPath)
    
    #----------
    def GetAbsoluteUserPath(self, sInputPath):
        return os.path.join(self.GetUserDir(), sInputPath)
    
    #----------
    def GetQuizFilename(self):
        return self._sQuizFilename

    #----------
    def GetFilenameWithExtFromPath(self, sFilePath):
        sDir,sFilenameWithExt = os.path.split(sFilePath)

        return sFilenameWithExt
    
    #----------
    def GetFilenameNoExtFromPath(self, sFilePath):
        sDir, sFilenameExt = os.path.split(sFilePath)
        sFilenameNoExt = os.path.splitext(sFilenameExt)[0]

        return sFilenameNoExt
    
    
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
        print('User Quiz Results Dir:', self.GetUserQuizResultsDir())
        print('User Quiz Reults path:', self.GetUserQuizResultsPath())
        
    #-------------------------------------------
    #        Functions
    #-------------------------------------------

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetModuleDirs(self, sModuleName, sSourceDirForQuiz):
        self.SetScriptedModulesPath(sModuleName)
        self._sXmlResourcesDir = os.path.join(self._sScriptedModulesPath, sSourceDirForQuiz)
        self.SetResourcesROIColorFilesDir()
        
    #----------
    def SetScriptedModulesPath(self,sModuleName):
        self._sScriptedModulesPath = eval('slicer.modules.%s.path' % sModuleName.lower())
        self._sScriptedModulesPath = os.path.dirname(self._sScriptedModulesPath)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetupUserAndDataDirs(self, sParentDirInput):
        
        # user selected data directory - the parent
        #    ImageVolumes subfolder will contain image volumes ready for import 
        #    Quiz results in XML format are stored in the Users subfolders
        #        as well as any saved label volumes
        #    Slicer updates the dicom database in the SlicerDICOMDatabase subfolder
        #        to coordinate import/load of images
        
        
        self._sDataParentDir = sParentDirInput
        
        # all paths for images in the XML quiz files are relative to the data parent directory
        
#         #  importing will use this directory as the root
#         self._sImageVolumeDataDir = os.path.join(sParentDirInput, 'ImageVolumes')

        # if users directory does not exist yet, it will be created
        self._sUsersParentDir = os.path.join(sParentDirInput, 'Users')
        if not os.path.exists(self._sUsersParentDir):
            os.makedirs(self._sUsersParentDir)
            
        # create the DICOM database if it is not there ready for importing
        self._sDICOMDatabaseDir = os.path.join(sParentDirInput, 'SlicerDICOMDatabase')
        if not os.path.exists(self._sDICOMDatabaseDir):
            os.makedirs(self._sDICOMDatabaseDir)
        
        # assign the database directory to the browser widget
        slDicomBrowser = slicer.modules.dicom.widgetRepresentation().self() 
        slDicomBrowserWidget = slDicomBrowser.browserWidget
        slDicomBrowserWidget.dicomBrowser.setDatabaseDirectory(self._sDICOMDatabaseDir)
        
        # update the database through the dicom browser 
        # this clears out path entries that can no longer be resolved
        #    (in the case of database location changes)
        slDicomBrowserWidget.dicomBrowser.updateDatabase()
        
        # test opening the database
        bSuccess, sMsg = self.OpenSelectedDatabase()
        if not bSuccess:
            self.oUtilsMsgs.DisplayWarning(sMsg)

        
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def OpenSelectedDatabase(self):
        
        sMsg = ''
        if DICOMUtils.openDatabase(self._sDICOMDatabaseDir):
            return True, sMsg
        else:
            sMsg = 'Trouble opening SlicerDICOMDatabase in : '\
                 + self._sDataParentDir\
                 + '\n Reselect Image Quizzer data directory or contact administrator.'
            return False, sMsg
            
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateQuiz(self, xRootNode):
        '''
            a function to check for specific validation requirements for the quiz
        '''
        sMsg = ''
        bSuccess = True
        
        
        try:
            lxPageElements = self.oIOXml.GetChildren(xRootNode, 'Page')
            
            iPageNum = 0
            for xPage in lxPageElements:
                lPathAndNodeNames= []
                iPageNum= iPageNum + 1

                sValidationMsg = self.ValidateRequiredAttribute(xPage, 'ID', str(iPageNum))
                sMsg = sMsg + sValidationMsg
                
                sPageID = self.oIOXml.GetValueOfNodeAttribute(xPage, 'ID')
                
                # Image element validations
                lxImageElements = self.oIOXml.GetChildren(xPage, 'Image')
                for xImage in lxImageElements:
                    sImageID = self.oIOXml.GetValueOfNodeAttribute(xImage, 'ID')
    
                    # Page ID + Image ID creates the node name for the image that is loaded (in ImageView>ViewNodeBase)
                    sNodeNameID = sPageID + '_' + sImageID
                    sPageReference = str(iPageNum) + ' ' + sNodeNameID

                    # Validate  frequency (one required element) and content
                    # >>>>>>>>>>>>>>> Elements
                    sValidationMsg = self.ValidateRequiredElement(xImage, 'Path', sPageReference)
                    sMsg = sMsg + sValidationMsg
                    
                    sValidationMsg = self.ValidateElementOptions(xImage, 'Layer', sPageReference, self.oIOXml.lValidLayers)
                    sMsg = sMsg + sValidationMsg
                    
                    sValidationMsg = self.ValidateElementOptions(xImage, 'Destination', sPageReference, self.oIOXml.lValidSliceWidgets)
                    sMsg = sMsg + sValidationMsg
                    
                    sValidationMsg = self.ValidateElementOptions(xImage, 'Orientation', sPageReference, self.oIOXml.lValidOrientations)
                    sMsg = sMsg + sValidationMsg
     
                    # >>>>>>>>>>>>>>> Attributes
                    sValidationMsg = self.ValidateRequiredAttribute(xImage, 'ID', sPageReference)
                    sMsg = sMsg + sValidationMsg
                    
                    sValidationMsg = self.ValidateRequiredAttribute(xImage, 'Type', sPageReference)
                    sMsg = sMsg + sValidationMsg
                    
                    sValidationMsg = self.ValidateAttributeOptions(xImage, 'Type', sPageReference, self.oIOXml.lValidImageTypes)
                    sMsg = sMsg + sValidationMsg
                    
                    sOpacity = self.oIOXml.GetValueOfNodeAttribute(xImage, 'Opacity')   # not required
                    if sOpacity != None:
                        try:
                            fOpacity = float(sOpacity)
                            if fOpacity < 0 or fOpacity > 1.0:
                                sMsg = sMsg + 'Opacity must be a number between 0.0 and 1.0' +  str(iPageNum)
                                if self.sTestMode == "1":
                                    raise
                        except ValueError:
                            sMsg = sMsg + 'Opacity must be a number between 0.0 and 1.0' +  str(iPageNum)
                            if self.sTestMode == "1":
                                raise ValueError('Invalid Opacity value: %s' % sMsg)

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
                            
                            
                    # If the image type is an RTStruct, validate the ROIs element
                    sImageType = self.oIOXml.GetValueOfNodeAttribute(xImage, 'Type')
                    if sImageType == 'RTStruct':
                        sValidationMsg = self.ValidateRequiredElement(xImage, 'ROIs', sPageReference)
                        sMsg = sMsg + sValidationMsg
                        
                        lxROIs = self.oIOXml.GetChildren(xImage, 'ROIs')
                        if len(lxROIs) >0:
                            sValidationMsg = self.ValidateRequiredAttribute(lxROIs[0], 'ROIVisibilityCode', sPageReference)
                            sMsg = sMsg + sValidationMsg
                            sValidationMsg = self.ValidateAttributeOptions(lxROIs[0], 'ROIVisibilityCode', sPageReference, self.oIOXml.lValidRoiVisibilityCodes)
                            sMsg = sMsg + sValidationMsg
                                
            # >>>>>>>>>>>>>>>
            # validate that each page has a PageGroup attribute if the session requires page group randomization
            sRandomizeRequested = self.oIOXml.GetValueOfNodeAttribute(xRootNode, 'RandomizePageGroups')
            if sRandomizeRequested == "Y":
                sValidationMsg = self.ValidatePageGroupNumbers(xRootNode)
                sMsg = sMsg + sValidationMsg

            
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
            self.oUtilsMsgs.DisplayWarning(sMsg)
            # after warning, reset the message for calling function to display error and exit
            sMsg = 'See Administrator: ERROR in XML validation.'
            
            
        return bSuccess, sMsg
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateRequiredElement(self, xParentElement, sElementName, sPageReference):
        '''
            This function checks that there is exactly one child element for the input parent element.
            If there is a valid list of options input as a parameter, the function checks that the
            data stored in the element exists in that list.
        '''
        sMsg = ''
        
        lxChildren = self.oIOXml.GetChildren(xParentElement, sElementName)
        if len(lxChildren) != 1:
            sMsg = sMsg + '\nError for ' + sElementName + ' Element.   See Page:' + sPageReference\
                     + '\n   .....There is either more than 1 of these elements or it is missing.'
        
        return sMsg
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateElementOptions(self, xParentElement, sElementName, sPageReference, lValidOptions):
        '''
            This function checks that the data stored in the xml element exists in the list of valid options.
        '''
        sMsg = ''
        
        lxChildren = self.oIOXml.GetChildren(xParentElement, sElementName)

        for xChild in lxChildren:
            sDataValue = self.oIOXml.GetDataInNode(xChild)
            if sDataValue not in lValidOptions:
                sValidOptions = ''
                for sOption in lValidOptions:
                    sValidOptions = sValidOptions + ', ' + sOption
                sMsg = sMsg + '\nNot a valid option for ' + sElementName + ' : ' + sDataValue + '   See Page:' + sPageReference\
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
    def ValidatePageGroupNumbers(self, xRootNode):
        ''' If the Session requires randomization of page groups, each page must have a PageGroup attribute
            If all page group numbers are equal, no randomization will be done.
            The page group values must be integer values.
            PageGroup = 0 is allowed. These will always appear at the beginning of the composite list of indices
        '''
        sMsg = ''
        sValidationMsg = ''
        # liPageGroups = []
        
        # check that each page has a page group number and that it is an integer
        lxPages = self.oIOXml.GetChildren(xRootNode,'Page')
        iPageNum = 0
        for xPage in lxPages:
            iPageNum = iPageNum + 1
            
            # required attribute for randomization
            sValidationMsg = self.ValidateRequiredAttribute(xPage, 'PageGroup', str(iPageNum))
            if sValidationMsg != '':
                raise Exception('Missing PageGroup attribute: %s' %sValidationMsg)
                sMsg = sMsg + sValidationMsg
            
            try:
                # test that the value is an integer
                iPageGroup = int(self.oIOXml.GetValueOfNodeAttribute(xPage, 'PageGroup'))
                # if iPageGroup == 0:
                #     sValidationMsg = 'Page Group must be an integer > 0. See Page: ' + str(iPageNum)
                #     sMsg = sMsg + sValidationMsg
                
            except ValueError:
                sValidationMsg = 'Page Group is not an integer. See Page: ' + str(iPageNum)
                sMsg = sMsg + sValidationMsg
                if self.sTestMode == "1":
                    raise ValueError('Invalid PageGroup value: %s' % sValidationMsg)
            
            self._liPageGroups.append(iPageGroup)

        # check that number of different page group numbers (that are >0) must be >1
        # you can't randomize if all the pages are assigned to the same group
        self._liUniquePageGroups = self.GetUniqueNumbers(self._liPageGroups)
        if 0 in self._liUniquePageGroups:
            self._liUniquePageGroups.remove(0) #ignore page groups set to 0
        if len(self._liUniquePageGroups) == 1:
            sValidationMsg = 'Not enough unique PageGroups for requested randomization. \nYou must have more than one page group (other than 0)'
            sMsg = sMsg + sValidationMsg
            if self.sTestMode == "1":
                raise Exception('Randomizing Error: %s' % sValidationMsg)
                
            
        return sMsg
    
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
    def PopulateUserQuizFolder(self):
            
        # check if quiz file already exists in the user folder - if not, copy from Resources

        # check if there is an existing file in the results directory (partially completed quiz)
        if not os.path.isfile(self.GetUserQuizResultsPath()):
            # file not found, copy file from Resources to User folder
            #     first make sure selected quiz file exists in the source directory
            if not os.path.isfile(self.GetResourcesQuizPath()):
                sErrorMsg = 'Selected Quiz file does not exist'
                self.oUtilsMsgs.DisplayWarning(sErrorMsg)
                return False  
            else:
                copyfile(self.GetResourcesQuizPath(), self.GetUserQuizResultsPath())
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
    def SetupROIColorFile(self, sInputROIColorFile):
        """ If quiz has a custom color table for segmenting ROI's, move this 
            into the color table file that is read in by the QuizzerHelperBox
        """
        # set up for default
        if sInputROIColorFile == '' or sInputROIColorFile == 'default':
            sInputROIColorFile = self.GetDefaultROIColorTableName()
        
        sInputROIColorFileWithExt = sInputROIColorFile + '.txt'   
        
        # get resources dir and join to requested color file
        sROIColorFileDir = self.GetResourcesROIColorFilesDir()
        sROIColorFilePath = os.path.join(sROIColorFileDir, sInputROIColorFileWithExt)
        sQuizzerROIColorTablePath = os.path.join(sROIColorFileDir, \
                                                 self.GetQuizzerROIColorTableNameWithExt())
        
        # check if requested table exists
        if not os.path.isfile(sROIColorFilePath):
            sMsg = 'ROI Color file "' + sInputROIColorFileWithExt + '" does not exist in :' + sROIColorFileDir
            self.oUtilsMsgs.DisplayError(sMsg)
        else:
            # if yes - overwrite QuizzerColorTable
            copyfile(sROIColorFilePath, sQuizzerROIColorTablePath)
                
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SaveLabelMaps(self, oSession, sCaller):

        """ label map volume nodes may exist in the mrmlScene if the user created a label map
            (in which case it is named with a '-bainesquizlabel' suffix), or if a label map 
            or segmentation was loaded in through the xml quiz file.
            
            This function looks for label maps created by the user (-bainesquizlabel suffix) 
            and if found, saves them as a data volume  (.nrrd file) in the specified directory.
            The path to this file is then stored in the xml file within the associated image element.
            
            Also store label maps as RTStructs if the attribute to do so was set in the xml root node.
            
            A warning is presented if the xml question set had the 'segmentrequired' flag set to 'y'
            but no label maps (with -bainesquizlabel suffix) were found. The user purposely may 
            not have created a label map if there were no lesions to segment. This is acceptable.
        """
            
        bLabelMapsSaved = True # initialize
        sMsg = ''
        
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


                        # only write to disk if it hasn't already been done for this image node                    
                        if not oImageNode.sNodeName in lsLabelMapsStoredForImages:

                            # store the path name in the xml file and the label map in the directory
                            sDirName = oSession.GetFolderNameForLabelMaps()
                            sPageLabelMapDir = self.CreatePageDir(sDirName)
    
                            sLabelMapFilenameWithExt = sLabelMapFilename + '.nrrd'
                             
                            # save the label map file to the user's page directory
                            sLabelMapPath = os.path.join(sPageLabelMapDir, sLabelMapFilenameWithExt)
    
                            bDataVolumeSaved, sMsg = self.SaveLabeMapAsDataVolume(sLabelMapPath, slNodeLabelMap) 
                         
                            # update list of names of images that have the label maps stored
                            lsLabelMapsStoredForImages.append(oImageNode.sNodeName)


                        # if label maps were saved as a data volume
                        #    add the label map path element to the image element in the xml
                        
#                         if (bDataVolumeSaved * bRTStructSaved):
                        if bDataVolumeSaved:
                            # update xml storing the path to the label map file with the image element
                            oSession.AddLabelMapPathElement(oImageNode.GetXmlImageElement(),\
                                                 self.GetRelativeUserPath(sLabelMapPath))
                        
                            bLabelMapsSaved = True  # at least one label map was saved
                        else:
                            bLabelMapsSaved = False
#                             sMsg = sNRRDMsg + sRTStructMsg
                            oSession.oUtilsMsgs.DisplayError(sMsg)


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
                                            'No label maps were created. Do you want to continue?')
                        if qtAns == qt.QMessageBox.Ok:
                            # user did not create a label map but there may be no lesions to segment
                            # continue with the save
                            bLabelMapsSaved = True
                        else:
                            # user wants to resume work on this page
                            bLabelMapsSaved = False
                
                    
    
    
        return bLabelMapsSaved, sMsg


        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SaveLabeMapAsDataVolume(self, sLabelMapPath, slNodeLabelMap):
        """ Use Slicer's storage node to export label map node as a data volume.
        """
        
        sMsg = ''
        bSuccess = True
        
        try:
            slStorageNode = slNodeLabelMap.CreateDefaultStorageNode()
            slStorageNode.SetFileName(sLabelMapPath)
            slStorageNode.WriteData(slNodeLabelMap)
            slStorageNode.UnRegister(slicer.mrmlScene) # for memory leaks
            
        except:
            bSuccess = False
            sMsg = 'Failed to store label map as data volume file: \n'\
                    + sLabelMapPath +\
                    'See administrator: ' + sys._getframe(  ).f_code.co_name
    
    
        return bSuccess, sMsg
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def SaveLabelMapAsRTStruct(self, oPrimaryImageNode, sLabelMapName, sOutputLabelDir):
#     
#         bRTStructSaved = True
#         sMsg = ''
#     
#         sSubDirForDicom = 'DICOM-' + oPrimaryImageNode.sNodeName
#         sOutputDir = os.path.join(sOutputLabelDir ,sSubDirForDicom)
#         
#         try:
#             
#             if not os.path.exists(sOutputDir):
#                 os.makedirs(sOutputDir)
#                 
#             # convert label map to segmentation
#             slLabelMapVolumeNode = slicer.util.getNode(sLabelMapName)
#             slLabelMapSegNode =  slicer.mrmlScene.AddNewNodeByClass('vtkMRMLSegmentationNode')
#             slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(slLabelMapVolumeNode, slLabelMapSegNode)
# 
# 
#             # work in subject hierarchy node (shNode)
#             shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
#             slPrimaryVolumeID = shNode.GetItemByDataNode(oPrimaryImageNode.slNode)
# 
#             # If image was originally loaded as a data volume, move it to 
#             #    a new patient & study in the subject hierarchy
#             if ( oPrimaryImageNode.sVolumeFormat != "DICOM"):
#                 slNewPatientItemID = shNode.CreateSubjectItem(shNode.GetSceneItemID(), "Patient Baines1")
#                 slNewStudyItemID = shNode.CreateStudyItem(slNewPatientItemID, "Study Baines1")
#                 shNode.SetItemParent(slPrimaryVolumeID, slNewStudyItemID)
# 
#              
# 
#             # Associate segmentation node with a reference volume node
#             slStudyShItem = shNode.GetItemParent(slPrimaryVolumeID)
#             slLabelMapSegNodeID = shNode.GetItemByDataNode(slLabelMapSegNode)
#             shNode.SetItemParent(slLabelMapSegNodeID, slStudyShItem)
# 
#                  
#             # create the dicom exporter
#             if oPrimaryImageNode.sImageType == 'VolumeSequence' :
#                 exporter = DICOMVolumeSequencePlugin.DICOMVolumeSequencePluginClass()
#             else:
#                 exporter = DicomRtImportExportPlugin.DicomRtImportExportPluginClass()
#             
#             
#             exportables = []
#              
#             # examine volumes for export and add to export list
#             volExportable = exporter.examineForExport(slPrimaryVolumeID)
#             segExportable = exporter.examineForExport(slLabelMapSegNodeID)
#             exportables.extend(volExportable)
#             exportables.extend(segExportable)
#              
#             # assign output path to each exportable
#             for exp in exportables:
#                 exp.directory = sOutputDir
#                  
#              
#             # perform export
#             exporter.export(exportables)
# 
# 
#         except:
#             bRTStructSaved = False
#             sMsg = 'Failed to store Dicom RTStruct ' + sOutputDir \
#                    + '\n See administrator: ' + sys._getframe(  ).f_code.co_name
# 
#         
#         return bRTStructSaved, sMsg, sOutputDir

    
    
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
#                 if (oSession.oIOXml.GetValueOfNodeAttribute(oImageNode.GetXmlImageElement(), 'UsePreviousLabelMap') == 'Y'):
#                     bUsePreviousLabelMap = True
#                 else:
#                     bUsePreviousLabelMap = False

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

                # if there were no label map paths stored with the image, and xml attribute has flag 
                #    to use a previous label map, check previous pages for the first matching image
                if xLabelMapPathElement == None and bUsePreviousLabelMap == True:
#                     xHistoricalLabelMapMatch = oSession.GetXmlElementFromImagePathHistory( oImageNode.GetXmlImageElement(), 'LabelMapPath')

                    # get image element from history that holds the same label map id; 
                    xHistoricalImageElement = None  # initialize
                    xHistoricalLabelMapMatch = None
                    xHistoricalImageElement = oSession.GetXmlElementFromAttributeHistory('Image','LabelMapID',sLabelMapIDLink)
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
                    bFoundLabelMap, slLabelMapNode = self.CheckForLoadedLabelMapInScene(sLabelMapNodeName)

                    # only load the label map once
                    #    same label map may have been stored multiple times in XML for the page
                    #    (same image but different orientations)
                    if not sStoredRelativePath in lLoadedLabelMaps:
                        sAbsolutePath = self.GetAbsoluteUserPath(sStoredRelativePath)
#                         dictProperties = {'LabelMap' : True, 'show': False}
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
        sCurrentLabelMapFolderName = oSession.GetFolderNameForLabelMaps()
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
        oSession.AddLabelMapPathElement(oImageNode.GetXmlImageElement(), self.GetRelativeUserPath(sLabelMapPathForDest))


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CheckForLoadedLabelMapInScene(self, sFilenameNoExt):
        """ A label map is stored on disk with the same name as the node in the mrmlScene.
            Using the filename for the label map (with no extension) check if it is already
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
    def CreateShutdownBatchFile(self):
        """ If Image Quizzer was started using the batch file, 
            the shutdown batch file will be called on close.
            This function sets up the shutdown batch file instructing it to
            remove the SlicerDicomDatabase directory.
            This speeds up the relaunch of the Image Quizzer. 
            
            This batch file resides in the parent directory of the ImageQuizzer module .
        """
        
        # get parent directory of the Image Quizzer module
        sShutdownDir = os.path.abspath(os.path.join(self.GetScriptedModulesPath(), os.pardir))
        sShutdownPath = os.path.join(sShutdownDir,'ImageQuizzerShutdown.bat')

        sCommand = 'RMDIR /S /Q ' + '"' + self.GetDICOMDatabaseDir() +'"'
        
        fh = open(sShutdownPath,"w")
        fh.write(sCommand)
        fh.close()

