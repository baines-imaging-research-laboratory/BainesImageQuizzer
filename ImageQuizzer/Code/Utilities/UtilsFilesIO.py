import os, sys
import warnings
import vtk, qt, ctk, slicer

import Utilities.UtilsMsgs as UtilsMsgs
import Utilities.UtilsIOXml as UtilsIOXml
import Utilities.UtilsCustomXml as UtilsCustomXml

from Utilities.UtilsCustomXml import *
from Utilities.UtilsIOXml import *
from Utilities.UtilsMsgs import *

from shutil import copyfile
import shutil
import re    # for regex re.sub
import SimpleITK as sitk
import numpy as np
import pathlib

from datetime import datetime
import DICOMLib
from DICOMLib import DICOMUtils
from pathlib import Path

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
    
    _sScriptedModulesPath = ''     # location of quizzer module project
    
    _sQuizDir = ''                 # folder - holds quiz files to copy to user
    _sQuizPath = ''                # full path (dir/file) of quiz to copy to user
    _sQuizFilename = ''            # quiz filename only (no dir)
    _sXmlSchemaFilePath = ''       # path to schema file for validation
    
    _sDataParentDir = ''           # parent folder to images
    
    _sUsersParentDir = ''          # folder - parent dir to all user folders
    _sUsername = ''                # name of user taking the quiz
    _sUserDir = ''                 # folder - holds quiz subfolders for specific user

    _sUserQuizResultsDir = ''      # folder for quiz results
    _sUserQuizResultsPath = ''     # full path (dir/file) for user's quiz results

    _sDICOMDatabaseDir = ''
#         self._sImageVolumeDataDir = ''

    _sResourcesROIColorFilesDir = ''  # folder to the Quizzer specific roi color files
    _sDefaultROIColorTableName = 'GenericColors'
    _sQuizzerROIColorTableNameWithExt = 'QuizzerROIColorTable.txt'
    _sQuizzerROIColorTablePath = ''

    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #-------------------------------------------
    #        Unit testing Utility
    #-------------------------------------------

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        
    @staticmethod
    def setupTestEnvironment():
        # check if function is being called from unit testing
        if "testing" in os.environ:
            UtilsFilesIO.sTestMode = os.environ.get("testing")
        else:
            UtilsFilesIO.sTestMode = "0"
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
    #-------------------------------------------
    #        Getters / Setters
    #-------------------------------------------

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
        
    #----------
    @staticmethod
    def SetDataParentDir(sDataDirInput):
        UtilsFilesIO._sDataParentDir = sDataDirInput

    #----------
    @staticmethod
    def SetUsersParentDir(sDirInput):
        UtilsFilesIO._sUsersParentDir = sDirInput
        
    #----------
    @staticmethod
    def SetQuizUsername(sInput):
        UtilsFilesIO._sUsername = sInput
        
    #----------
    @staticmethod
    def SetQuizPathAndFilename(sSelectedQuizPath):

        UtilsFilesIO._sQuizPath = os.path.join(UtilsFilesIO._sQuizDir, sSelectedQuizPath)
        UtilsFilesIO._sQuizDir, UtilsFilesIO._sQuizFilename = os.path.split(UtilsFilesIO._sQuizPath)
        
    #----------
    @staticmethod
    def SetUsernameAndDir( sSelectedUser):
        UtilsFilesIO._sUsername = sSelectedUser
        UtilsFilesIO._sUserDir = os.path.join(UtilsFilesIO.GetUsersParentDir(), UtilsFilesIO._sUsername)
        
    #----------
    @staticmethod
    def SetDICOMDatabaseDir( sInputDir):
        UtilsFilesIO._sDICOMDatabaseDir = sInputDir
    
    #----------
    @staticmethod
    def SetSchemaFilePath(sInputFile):
        UtilsFilesIO._sXmlSchemaFilePath = os.path.join(UtilsFilesIO.GetXmlQuizDir(),sInputFile)
        
 
    #----------
    #----------
    #----------
    @staticmethod
    def GetDataParentDir():
        return UtilsFilesIO._sDataParentDir

    #----------
    @staticmethod
    def GetDICOMDatabaseDir():
        return UtilsFilesIO._sDICOMDatabaseDir
    
    #----------
    @staticmethod
    def GetScriptsDir():
        sImageQuizzerDir = str(Path(UtilsFilesIO.GetScriptedModulesPath()).parents[0])
        return os.path.join(sImageQuizzerDir,'Inputs','Scripts')
    
    #----------
    @staticmethod
    def GetDirFromPath( sFullPath):
        head, tail = os.path.split(sFullPath)
        return head
    
    #----------
    @staticmethod
    def GetScriptedModulesPath():
        return UtilsFilesIO._sScriptedModulesPath
    
    #----------
    @staticmethod
    def GetXmlQuizPath():
        return UtilsFilesIO._sQuizPath
    
    #----------
    @staticmethod
    def GetUsername():
        return UtilsFilesIO._sUsername
     
    #----------
    @staticmethod
    def GetUserDir():
        return UtilsFilesIO._sUserDir

    #----------
    @staticmethod
    def GetUsersParentDir():
        return UtilsFilesIO._sUsersParentDir    

    #----------
    @staticmethod
    def GetUserQuizResultsDir():
        return UtilsFilesIO._sUserQuizResultsDir

    #----------
    @staticmethod
    def GetUserQuizResultsPath():
        return UtilsFilesIO._sUserQuizResultsPath
    
    #----------
    @staticmethod
    def GetXmlQuizDir():
        return UtilsFilesIO._sQuizDir
    
    #----------
    @staticmethod
    def GetSchemaFilePath():
        return UtilsFilesIO._sXmlSchemaFilePath
    
    #----------
    @staticmethod
    def GetRelativeUserPath( sInputPath):
        # remove absolute path to user folders
        return sInputPath.replace(UtilsFilesIO.GetUserDir()+'\\','')

    #----------
    @staticmethod
    def GetRelativeDataPath( sInputPath):
        # remove absolute path to user folders
        return sInputPath.replace(UtilsFilesIO.GetDataParentDir()+'\\','')

    #----------
    @staticmethod
    def GetAbsoluteDataPath( sInputPath):
        return os.path.join(UtilsFilesIO._sDataParentDir, sInputPath)
    
    #----------
    @staticmethod
    def GetAbsoluteUserPath( sInputPath):
        return os.path.join(UtilsFilesIO.GetUserDir(), sInputPath)
    
    #----------
    @staticmethod
    def GetQuizFilename():
        return UtilsFilesIO._sQuizFilename
    
    #----------
    @staticmethod
    def GetQuizFilenameNoExt():
        sFilenameNoExt = os.path.splitext(UtilsFilesIO.GetQuizFilename())[0]
        
        return sFilenameNoExt
    
    #----------
    @staticmethod
    def GetFilenameWithExtFromPath( sFilePath):
        sDir,sFilenameWithExt = os.path.split(sFilePath)

        return sFilenameWithExt
    
    #----------
    @staticmethod
    def GetFilenameNoExtFromPath( sFilePath):
        sDir, sFilenameExt = os.path.split(sFilePath)
        sFilenameNoExt = os.path.splitext(sFilenameExt)[0]

        return sFilenameNoExt
    
    #----------
    @staticmethod
    def GetExtensionFromPath( sFilePath):
        
        sExt = pathlib.Path(sFilePath).suffix

        return sExt
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def GetFolderNameForPageResults( oSession):
        """ Quiz results (eg. LabelMaps, MarkupLines) are stored in a directory where the name is derived from the 
            current page of the Session.
        """
        
        # get page info from the session's current page to create directory
        xPageNode = oSession.oCustomWidgets.GetNthPageNode(oSession.GetCurrentPageIndex())
        sPageIndex = str(oSession.GetCurrentPageIndex() + 1)
        sPageID = UtilsIOXml.GetValueOfNodeAttribute(xPageNode, 'ID')
        sPageDescriptor = UtilsIOXml.GetValueOfNodeAttribute(xPageNode, 'Descriptor')
        sPageGroup = UtilsIOXml.GetValueOfNodeAttribute(xPageNode, 'PageGroup')
        # sDirName = os.path.join(self.GetUserQuizResultsDir(), 'Pg'+ sPageIndex + '_' + sPageID )
        sDirName = os.path.join(UtilsFilesIO.GetUserQuizResultsDir(), 'PgGroup' + sPageGroup + '_' + sPageID + '_' + sPageDescriptor )

        return sDirName
        


    #----------
    #----------ROI Color Files
    #----------
    @staticmethod
    def SetResourcesROIColorFilesDir():
        UtilsFilesIO._sResourcesROIColorFilesDir = os.path.join(UtilsFilesIO.GetScriptedModulesPath(),\
                                                        'Resources','ColorFiles')
        
    #----------
    @staticmethod
    def GetResourcesROIColorFilesDir():
        return UtilsFilesIO._sResourcesROIColorFilesDir
    
    #----------
    @staticmethod
    def GetQuizzerROIColorTableNameWithExt():
        return UtilsFilesIO._sQuizzerROIColorTableNameWithExt
    
    #----------
    @staticmethod
    def SetQuizzerROIColorTablePath( sInputPath):
        UtilsFilesIO._sQuizzerROIColorTablePath = sInputPath

    #----------
    @staticmethod
    def GetQuizzerROIColorTablePath():
        return UtilsFilesIO._sQuizzerROIColorTablePath
    
    #----------
    @staticmethod
    def GetCustomROIColorTablePath( sROIColorFile):
        return os.path.join(UtilsFilesIO.GetXmlQuizDir(), sROIColorFile + '.txt')

    #----------
    @staticmethod
    def GetDefaultROIColorTableName():
        return UtilsFilesIO._sDefaultROIColorTableName

    #----------
    @staticmethod
    def GetDefaultROIColorFilePath():
        return os.path.join(UtilsFilesIO.GetResourcesROIColorFilesDir(), UtilsFilesIO.GetDefaultROIColorTableName() + '.txt')

    #----------
    @staticmethod
    def GetConfigDir():
        sImageQuizzerDir = str(Path(UtilsFilesIO.GetScriptedModulesPath()).parents[0])
        return os.path.join(sImageQuizzerDir,'Inputs','Config')

    #----------
    @staticmethod
    def SetColorSpinBoxDefaultLabel(sLabel):
        slicer.modules.quizzereditor.widgetRepresentation().self().SetColorSpinBoxDefaultLabel(sLabel)

    #----------
    @staticmethod
    def SetColorSpinBoxValidLabels(lsLabels):
        slicer.modules.quizzereditor.widgetRepresentation().self().SetColorSpinBoxValidLabels(lsLabels)

   
    #----------
    #----------General functions
    #----------
    
    
    #----------
    @staticmethod
    def CleanFilename( sInputFilename):
#         sInvalid = '<>:"/\|?* '
        sInvalid = '<>:"/\|?*'
        sCleanName = sInputFilename
        
        for char in sInvalid:
            sCleanName = sCleanName.replace(char,'')
            
        return sCleanName

    #----------
    @staticmethod
    def getNodes():
        
        ##### For Debug #####
        # return nodes in the mrmlScene
        #    Can be used to flag differences in nodes before and after code
        #    being investigated (example: for memory leaks)

        nodes = slicer.mrmlScene.GetNodes()
        return [nodes.GetItemAsObject(i).GetID() for i in range(0,nodes.GetNumberOfItems())]

        ######################
        # set the following line before code being investigated
        #
        #        nodes1 = UtilsFilesIO.getNodes()
        #
        # set these lines after code being investigated
        #
        #        nodes2 = UtilsFilesIO.getNodes()
        #        filteredX = ' '.join((filter(lambda x: x not in nodes1, nodes2)))
        #        print(':',filteredX)
        ######################

    #----------
    @staticmethod
    def PrintDirLocations():
        
        ##### For Debug #####
        print('Data parent dir:      ', UtilsFilesIO.GetDataParentDir())
        print('DICOM DB dir:         ', UtilsFilesIO.GetDICOMDatabaseDir())
        print('User parent dir:      ', UtilsFilesIO.GetUsersParentDir())
        print('User dir:             ', UtilsFilesIO.GetUserDir())
        print('User Quiz Results dir:', UtilsFilesIO.GetUserQuizResultsDir())
        print('User Quiz Results XML path:', UtilsFilesIO.GetUserQuizResultsPath())


    #-------------------------------------------
    #        Setup Functions
    #-------------------------------------------

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def SetModuleDirs( sModuleName):

        UtilsFilesIO.SetScriptedModulesPath(sModuleName)
        UtilsFilesIO._sQuizDir = os.path.join(UtilsFilesIO.GetScriptedModulesPath(),'..', 'Inputs','MasterQuiz')
        UtilsFilesIO.SetResourcesROIColorFilesDir()
        UtilsFilesIO.SetSchemaFilePath('ImageQuizzer.xsd')
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def SetScriptedModulesPath(sModuleName):
        # from Slicer's Application settings> modules
        sScriptedModulesPath = eval('slicer.modules.%s.path' % sModuleName.lower())
        UtilsFilesIO._sScriptedModulesPath = os.path.dirname(sScriptedModulesPath)
#         print('Path:',_sScriptedModulesPath)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def SetupROIColorFile( sCustomInputROIColorFile):
        """ If quiz has a custom color table for segmenting ROI's, move this 
            into the color table file that is read in by the QuizzerEditor HelperBox
        """
        if sCustomInputROIColorFile == '':
            sROIColorFilePath = UtilsFilesIO.GetDefaultROIColorFilePath()
        else:
            sROIColorFilePath = os.path.join(UtilsFilesIO.GetXmlQuizDir(), sCustomInputROIColorFile + '.txt')
        
        UtilsFilesIO.SetQuizzerROIColorTablePath( os.path.join(UtilsFilesIO.GetResourcesROIColorFilesDir(), \
                                             UtilsFilesIO.GetQuizzerROIColorTableNameWithExt()) )
        copyfile(sROIColorFilePath, UtilsFilesIO.GetQuizzerROIColorTablePath() )
        
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def SetupForUserQuizResults():
        
        try:
        
            sQuizFileRoot, sExt = os.path.splitext(UtilsFilesIO.GetQuizFilename())
             
            UtilsFilesIO._sUserQuizResultsDir = os.path.join(UtilsFilesIO.GetUserDir(), sQuizFileRoot)
            UtilsFilesIO._sUserQuizResultsPath = os.path.join(UtilsFilesIO.GetUserQuizResultsDir(), UtilsFilesIO.GetQuizFilename())
     
            # check that the user folder exists - if not, create it
            if not os.path.exists(UtilsFilesIO._sUserQuizResultsDir):
                os.makedirs(UtilsFilesIO._sUserQuizResultsDir)
                
        except Exception as error:
            tb = traceback.format_exc()
            sMsg = '\SetupForUserQuizResults: Failed to set up directories for results '\
                    + '   Possible cause: directory path too long. Admin must move Image Quizzer closer to root.'\
                    + "\n\n" + str(error) \
                    + "\n\n" + tb 
            UtilsMsgs.DisplayError(sMsg)
         
     
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def SetupOutputDirs():
        
        # the parent of the Outputs directory is  path/to/ImageQuizzermodule/Outputs
        #    Quiz results in XML format are stored in the UsersResults subfolders
        #        as well as any saved label volumes (contours, annotations)
        #    Slicer updates the DICOM database in the SlicerDICOMDatabase subfolder
        #        to coordinate import/load of images
        
        
        sParentOutputsDir = os.path.join(UtilsFilesIO.GetScriptedModulesPath(),'..', 'Outputs')
        
        # if users directory does not exist yet, it will be created
        UtilsFilesIO.SetUsersParentDir(os.path.join(sParentOutputsDir, 'UsersResults'))
        if not os.path.exists(UtilsFilesIO._sUsersParentDir):
            os.makedirs(UtilsFilesIO._sUsersParentDir)
                    
        
        # create the DICOM database if it is not there ready for importing
        UtilsFilesIO.SetDICOMDatabaseDir( os.path.join(sParentOutputsDir, 'SlicerDICOMDatabase') )
        if not os.path.exists(UtilsFilesIO.GetDICOMDatabaseDir()):
            os.makedirs(UtilsFilesIO.GetDICOMDatabaseDir())
        
        # assign the database directory to the browser widget
        slDicomBrowser = slicer.modules.dicom.widgetRepresentation().self() 
        slDicomBrowserWidget = slDicomBrowser.browserWidget
        slDicomBrowserWidget.dicomBrowser.setDatabaseDirectory(UtilsFilesIO.GetDICOMDatabaseDir())
        
        # update the database through the dicom browser 
        # this clears out path entries that can no longer be resolved
        #    (in the case of database location changes)
        slDicomBrowserWidget.dicomBrowser.updateDatabase()
        
        # test opening the database
        if DICOMUtils.openDatabase(UtilsFilesIO.GetDICOMDatabaseDir()):
            pass
        else:
            sMsg = 'Trouble opening SlicerDICOMDatabase in : '\
                 + UtilsFilesIO.GetDICOMDatabaseDir()
            UtilsMsgs.DisplayError(sMsg)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def PopulateUserQuizFolder():
            
        # check if there is an existing file in the output users results directory (partially completed quiz)
        #    if not - copy from the master quiz file in inputs to outputs directory
        if not os.path.isfile(UtilsFilesIO.GetUserQuizResultsPath()):

            if not os.path.isfile(UtilsFilesIO.GetXmlQuizPath()):
                sErrorMsg = 'Selected Quiz file does not exist'
                UtilsMsgs.DisplayWarning(sErrorMsg)
                return False  
            else:
                copyfile(UtilsFilesIO.GetXmlQuizPath(), UtilsFilesIO.GetUserQuizResultsPath())
                return True

        else:

            # create backup of existing file
            UtilsFilesIO.BackupUserQuizResults()
                
            # file exists - make sure it is readable
            if not os.access(UtilsFilesIO.GetUserQuizResultsPath(), os.R_OK):
                # existing file is unreadable
                sErrorMsg = 'Quiz file is not readable'
                UtilsMsgs.DisplayWarning(sErrorMsg)     
                return False
            else:
                return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #-------------------------------------------
    #        Utility Functions
    #-------------------------------------------

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def CreatePageDir( sPageName):
        # page dir stores label maps for the specified page
        # store these in the user directory
        sPageDir = os.path.join(UtilsFilesIO.GetUserDir(), sPageName)
        
        # check that the Page directory exists - if not create it
        if not os.path.exists(sPageDir):
            os.makedirs(sPageDir)
    
        return sPageDir

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def CreateShutdownBatchFile():
        """ If Image Quizzer was started using the batch file, 
            the shutdown batch file will be called on close.
            This function sets up the shutdown batch file instructing it to
            remove the SlicerDicomDatabase directory.
            This speeds up the relaunch of the Image Quizzer. 
            
            This batch file resides in the parent directory of the ImageQuizzer module .
        """
        
        # get parent directory of the Image Quizzer module
        sShutdownDir = os.path.abspath(os.path.join(UtilsFilesIO.GetScriptedModulesPath(),'..', os.pardir))
        sShutdownPath = os.path.join(sShutdownDir,'ImageQuizzerShutdown.bat')

        sCommand = 'RMDIR /S /Q ' + '"' + UtilsFilesIO.GetDICOMDatabaseDir() +'"'
        
        fh = open(sShutdownPath,"w")
        fh.write(sCommand)
        fh.close()

        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def BackupUserQuizResults():
        
        # get current date/time
        from datetime import datetime
        now = datetime.now()
        sSuffix = now.strftime("%b-%d-%Y-%H-%M-%S")
        
        sFileRoot, sExt = os.path.splitext(UtilsFilesIO.GetQuizFilename())
        
        sNewFileRoot = '_'.join([sFileRoot, sSuffix])
        sNewFilename = ''.join([sNewFileRoot, sExt])
        
        sBackupQuizResultsPath = os.path.join(UtilsFilesIO.GetUserQuizResultsDir(), sNewFilename)
        
        # create copy with data/time stamp as suffix
        copyfile(UtilsFilesIO.GetUserQuizResultsPath(), sBackupQuizResultsPath)
        
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def ExportResultsItemToFile( sItemName, sPath, slNode):
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
            UtilsMsgs.DisplayError(sMsg)
    
        return bSuccess, sMsg
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def CheckForLoadedNodeInScene( sFilenameNoExt):
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
    @staticmethod
    def SaveLabelMaps( oSession, sCaller):

        """ label map volume nodes may exist in the mrmlScene if the user created a label map
            (in which case it is named with a '-quizlabel' suffix), or if a label map 
            or segmentation was loaded in through the xml quiz file.
            
            This function looks for label maps created by the user (-quizlabel suffix) 
            and if found, saves them as a data volume  (.nrrd file) in the specified directory.
            The path to this file is then stored in the xml file within the associated image element.
            
            Also store label maps as RTStructs if the attribute to do so was set in the xml root node.
            
            A warning is presented if the xml question set had the 'EnableSegmentEditor' flag set to 'y'
            but no label maps (with -quizlabel suffix) were found. The user purposely may 
            not have created a label map if there were no lesions to segment. This is acceptable.
        """
            
        sMsg = ''
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
                    if oImageNode.sNodeName + '-quizlabel' == sLabelMapFilename:
                        
                        bLabelMapFound = True  # -quizlabel suffix is associated with an image on the page
                        
                        sDirName = UtilsFilesIO.GetFolderNameForPageResults(oSession)
                        sPageLabelMapDir = UtilsFilesIO.CreatePageDir(sDirName)
                        sLabelMapFilenameWithExt = sLabelMapFilename + '.nrrd'
                        sLabelMapPath = os.path.join(sPageLabelMapDir, sLabelMapFilenameWithExt)
                        
                        if not oImageNode.sNodeName in lsLabelMapsStoredForImages:
                            # save the label map file to the user's page directory
                            UtilsFilesIO.ExportResultsItemToFile('LabelMap', sLabelMapPath, slNodeLabelMap) 
                         
                            # update list of names of images that have the label maps stored
                            lsLabelMapsStoredForImages.append(oImageNode.sNodeName)


                        # there is a quiz validation for this error - estimation during validation may have been off
                        sErrorMsg = 'ERROR - LabelMap file not saved. Filename too long : ' + str(len(sLabelMapPath))\
                                    + '\n' + sLabelMapPath\
                                    + '\n\nContact Administrator'
                        if len(sLabelMapPath) > 256:  # Windows limitation
                            UtilsMsgs.DisplayError(sErrorMsg)

                        
                        #    add the label map path element to the image element in the xml
                        #    only one label map path element is to be recorded
                        xLabelMapPathElement = UtilsIOXml.GetLastChild(oImageNode.GetXmlImageElement(), 'LabelMapPath')
                        
                        if xLabelMapPathElement == None:
                            # update xml storing the path to the label map file with the image element
                            oSession.oCustomWidgets.AddPathElement('LabelMapPath', oImageNode.GetXmlImageElement(),\
                                                 UtilsFilesIO.GetRelativeUserPath(sLabelMapPath))
                            
                            

        if sCaller != 'ResetView':   # warning not required on a reset
    
            #####
            # Display warning if segmentation was required but no user created label map was found.
            #####
            #    If there were no label map volume nodes 
            #    OR if there were label map volume nodes, but there wasn't a -quizlabel suffix 
            #        to match an image on the page, ie. the labelMaps found flag was left as false
            #    Check if the segmentation was required and if enabled present the warning
            if len(lSlicerLabelMapNodes) == 0 or (len(lSlicerLabelMapNodes) > 0 and bLabelMapFound == False):    
                
                # user doesn't get the option to cancel if the call was initiated 
                # from the Close event filter
                if sCaller != 'EventFilter':
                    if oSession.oCustomWidgets.GetSegmentationModuleRequired():   # if there is a segmentation module
                        if oSession.oCoreWidgets.GetSegmentationTabEnabled() == True:    # if the tab is enabled
                            qtAns = UtilsMsgs.DisplayOkCancel(\
                                                'No contours were created. Do you want to continue?')
                            if qtAns == qt.QMessageBox.Ok:
                                # user did not create a label map but there may be no lesions to segment
                                # continue with the save
                                bLabelMapsSaved = True
                            else:
                                # user wants to resume work on this page
                                bLabelMapsSaved = False
                                sMsg = ' ... cancelled to continue contouring'
                    
                    
        if bLabelMapsSaved == True:
            UtilsIOXml.SaveXml(UtilsFilesIO.GetUserQuizResultsPath())

        return bLabelMapsSaved, sMsg
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def LoadSavedLabelMaps( oSession):
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
                sLabelMapIDLink = UtilsIOXml.GetValueOfNodeAttribute(oImageNode.GetXmlImageElement(), 'DisplayLabelMapID')
                if sLabelMapIDLink != '':
                    bUsePreviousLabelMap = True
                else:
                    bUsePreviousLabelMap = False

        
                # look at latest instance of the label map elements stored in the xml
                xLabelMapPathElement = UtilsCustomXml.GetLatestChildElement(oImageNode.GetXmlImageElement(), 'LabelMapPath')
                slLabelMapNode = None # initialize

                # if the image has the xml attribute DisplayLabelMapID 
                #    to use a previous label map, check previous pages for the first matching image
                if (bUsePreviousLabelMap == True):

                    # get image element from history that holds the same label map id; 
                    xHistoricalImageElement = None  # initialize
                    xHistoricalLabelMapMatch = None
                    xHistoricalImageElement, xHistoricalPageElement = UtilsCustomXml.GetXmlPageAndChildFromAttributeHistory(\
                                                                                    oSession.GetCurrentNavigationIndex(), \
                                                                                    oSession.GetNavigationList(),\
                                                                                    'Image',\
                                                                                    'LabelMapID',\
                                                                                    sLabelMapIDLink)

                    if oImageNode.bMergeLabelMaps:
                        # combine label maps and store on disk
                        xLabelMapPathElement = UtilsFilesIO.MergeLabelMapsAndSave(oSession, oImageNode, xHistoricalImageElement, xHistoricalPageElement)
                        
                        
                    else:
                        # load single label map
                        if xHistoricalImageElement != None:
                            xHistoricalLabelMapMatch = UtilsCustomXml.GetLatestChildElement(xHistoricalImageElement, 'LabelMapPath')
                        
                        if xHistoricalLabelMapMatch != None:
                            # found a label map for this image in history
                            # copy to disk and store it in xml for the current image
                            UtilsFilesIO.CopyAndStoreLabelMapFromHistory(oSession, xHistoricalLabelMapMatch, oImageNode)
    
                            #    assign newly stored xml element to xLabelMapPathElement
                            xLabelMapPathElement = UtilsCustomXml.GetLatestChildElement( oImageNode.GetXmlImageElement(), 'LabelMapPath')
                    
                
                # load labelmap file from stored path in XML                
                if xLabelMapPathElement != None:
                    sStoredRelativePath = UtilsIOXml.GetDataInNode(xLabelMapPathElement)
                    
                    # check if label map was already loaded (if between question sets, label map will persisit)
                    sLabelMapNodeName = UtilsFilesIO.GetFilenameNoExtFromPath(sStoredRelativePath)
                    bFoundLabelMap, slLabelMapNode = UtilsFilesIO.CheckForLoadedNodeInScene(sLabelMapNodeName)

                    # only load the label map once
                    if not sStoredRelativePath in lLoadedLabelMaps:
                        sAbsolutePath = UtilsFilesIO.GetAbsoluteUserPath(sStoredRelativePath)
                        dictProperties = {'LabelMap' : True}
                        
                        try:

                            if not bFoundLabelMap:
                                if os.path.exists(sAbsolutePath):
                                    # load label map into the scene
                                    slLabelMapNode = slicer.util.loadLabelVolume(sAbsolutePath, dictProperties)
                                else:
                                    sMsg = 'Stored path to label map file does not exist. Label map will not be loaded.\n' \
                                        + sAbsolutePath
                                    UtilsMsgs.DisplayWarning(sMsg)
                                    break # continue in for loop for next label map path element
                            
                            
                            lLoadedLabelMaps.append(sStoredRelativePath)
    
                            # set associated volume to connect label map to master
                            sLabelMapNodeName = slLabelMapNode.GetName()
#                             sAssociatedName = sLabelMapNodeName.replace('-quizlabel','')
                            sAssociatedName = oImageNode.sNodeName
                            slAssociatedNodeCollection = slicer.mrmlScene.GetNodesByName(sAssociatedName)
                            slAssociatedNode = slAssociatedNodeCollection.GetItemAsObject(0)
                            slLabelMapNode.SetNodeReferenceID('AssociatedNodeID',slAssociatedNode.GetID())

                            # apply ROIColor table to label map display node
                            slLabelMapDisplayNode = slLabelMapNode.GetDisplayNode()
                            slColorLogic = slicer.modules.colors.logic()
                            slColorNode = slColorLogic.LoadColorFile(UtilsFilesIO.GetQuizzerROIColorTablePath())
                            slLabelMapDisplayNode.SetAndObserveColorNodeID(slColorNode.GetID())
    
    
                        except:
                             
                            sMsg = 'Trouble loading label map file:' + sAbsolutePath
                            UtilsMsgs.DisplayWarning(sMsg)
                           

                # add the label map node to the image property so that it gets
                #    set when assigning nodes to the viewing widgets (red, green, yellow)
                # the node may be None (no label map path was stored)
                oImageNode.SetQuizLabelMapNode(slLabelMapNode)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def CopyAndStoreLabelMapFromHistory( oSession, xHistoricalLabelMapElement, oImageNode):
        ''' given an element holding the path for a label map, the file is copied into the
            results folder for the current page. If a label map file of that name already 
            exists in this folder, it will be overwritten
        '''

        # define source for copy
        sStoredRelativePathForSource = UtilsIOXml.GetDataInNode(xHistoricalLabelMapElement)
        sAbsolutePathForSource = UtilsFilesIO.GetAbsoluteUserPath(sStoredRelativePathForSource)

        # create new folder for destination based on current page information
        sCurrentLabelMapFolderName = UtilsFilesIO.GetFolderNameForPageResults(oSession)
        sLabelMapDirForDest = UtilsFilesIO.CreatePageDir(sCurrentLabelMapFolderName)
        
        # create new file name to which the historical label map is to be copied
        sLabelMapFilenameWithExtForDest = oImageNode.sNodeName + '-quizlabel' + '.nrrd'
        
        # define destination path
        sLabelMapPathForDest = os.path.join(sLabelMapDirForDest, sLabelMapFilenameWithExtForDest)

        # copy source to dest
        shutil.copy(sAbsolutePathForSource, sLabelMapPathForDest)

        # update xml storing the path to the label map file with the image element
        #    for display on the next page
        oSession.oCustomWidgets.AddPathElement('LabelMapPath', oImageNode.GetXmlImageElement(), UtilsFilesIO.GetRelativeUserPath(sLabelMapPathForDest))


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def MergeLabelMapsAndSave( oSession, oImageNode, xHistoricalImageElement, xHistoricalPageElement):
        ''' This function will search for all Pages with the same 'base' name as the historical page that
            was found to have the matching LabelMapID for the DisplayLabelMapID.
            The base name is the PageID_Descriptor without the '-Rep##' which is added when using the Repeat button.
            From these pages, collect the LabelMapPath values for the Images with the matching LabelMapID
            and merge these.
            The merged label map is then saved to disk and the current ImageElement is updated with a new LabelMapPath element. 


            Merging methodology:
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

        try:        
            xLabelMapPathElement = None
            lsLabelMapFullPaths = []
            
            # Search for all previous Pages that match PageID_Descriptor (without the -Rep## substring)
            sPageIDToSearch = UtilsIOXml.GetValueOfNodeAttribute(xHistoricalPageElement, 'ID')
                        # remove ignore string
            reIgnoreSubstring= '-Rep[0-9]+'  # remove -Rep with any number of digits following
            sPageIDToSearchStripped = re.sub(reIgnoreSubstring,'',sPageIDToSearch)
            sPageDescriptorToSearch = UtilsIOXml.GetValueOfNodeAttribute(xHistoricalPageElement, 'Descriptor')
    
            dictAttribToMatch = {}
            dictAttribToMatch['ID'] = sPageIDToSearchStripped
            dictAttribToMatch['Descriptor'] = sPageDescriptorToSearch
    
            sLabelMapIDToMatch = UtilsIOXml.GetValueOfNodeAttribute(xHistoricalImageElement, 'LabelMapID')
            
            
            # collect label map paths
            dictPgNodeAndPgIndex = UtilsCustomXml.GetMatchingXmlPagesFromAttributeHistory(\
                                                    oSession.GetCurrentNavigationIndex(),\
                                                    oSession.GetNavigationList() , \
                                                    dictAttribToMatch, \
                                                    reIgnoreSubstring)
            
            lMatchingPageNodes = list(dictPgNodeAndPgIndex.keys())
            for xPageNode in lMatchingPageNodes:
                
                lxImageElements = UtilsIOXml.GetChildren(xPageNode, 'Image')
    
                for xImage in lxImageElements:
                    sLabelMapID = UtilsIOXml.GetValueOfNodeAttribute(xImage,'LabelMapID')
    
                    if sLabelMapID == sLabelMapIDToMatch:
                        lxLabelMapPath = UtilsIOXml.GetChildren(xImage, 'LabelMapPath')
    
                        for xPath in lxLabelMapPath:
                            sLabelMapPath = UtilsIOXml.GetDataInNode(xPath)
                            sLabelMapFullPath = os.path.join(UtilsFilesIO.GetUserDir(), sLabelMapPath)
                            lsLabelMapFullPaths.append(sLabelMapFullPath)
            
            
            # use SimpleITK to collect all matching images
            litkAllLabelImages = []
            for sPath in lsLabelMapFullPaths:
                itkLabelImage = sitk.ReadImage(sPath)
                litkAllLabelImages.append(itkLabelImage)
                
    
            # merge label maps
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
                sDirName = UtilsFilesIO.GetFolderNameForPageResults(oSession)
                sPageLabelMapDir = UtilsFilesIO.CreatePageDir(sDirName)
        
                sLabelMapFilenameWithExt = oImageNode.sNodeName + '-quizlabel.nrrd'
                
                
                sLabelMapPath = os.path.join(sPageLabelMapDir, sLabelMapFilenameWithExt)
                
                
                # if merge was already done and a label map already exists, delete it and save the new merge
                #    this allows the user to make any corrections to contours using the previous button
                
                if os.path.exists(sLabelMapPath):
                    os.remove(sLabelMapPath)
        
                UtilsFilesIO.ExportResultsItemToFile('LabelMap', sLabelMapPath, slLabelMapVolumeCombined)
        
                # update xml storing the path to the label map file with the image element
                #    for display on the next page
                oSession.oCustomWidgets.AddPathElement('LabelMapPath', oImageNode.GetXmlImageElement(), UtilsFilesIO.GetRelativeUserPath(sLabelMapPath))
                UtilsIOXml.SaveXml(UtilsFilesIO.GetUserQuizResultsPath())
                xLabelMapPathElement = UtilsCustomXml.GetLatestChildElement(oImageNode.GetXmlImageElement(), 'LabelMapPath')
        
                # cleanup
                slicer.mrmlScene.RemoveNode(slLabelMapVolumeReference)
                slicer.mrmlScene.RemoveNode(slLabelMapVolumeCombined)
            
        except Exception as error:
            tb = traceback.format_exc()
            sMsg = "MergeLabelMapsAndSave: Error while merging label maps."  \
                    + str(error) \
                    + "\n\n" + tb 
            UtilsMsgs.DisplayError(sMsg)


        
        return xLabelMapPathElement
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
    #-------------------------------------------
    #        MarkupsLine Functions
    #-------------------------------------------

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def SaveMarkupLines( oSession):
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
                        sLineName = UtilsFilesIO.CreateUniqueLineName(lsMarkupLineNodes, slMarkupLine.GetName(), sAssociatedReferenceNodeName)
                        slMarkupLine.SetName(sLineName)
                
                    # save the markup line in the directory
                    sDirName = UtilsFilesIO.GetFolderNameForPageResults(oSession)
                    sPageMarkupsLineDir = UtilsFilesIO.CreatePageDir(sDirName)
        
                    sMarkupsLineFilenameWithExt = slMarkupLine.GetName() + '.mrk.json'
                                 
                    # save the markup line file to the user's page directory
                    sMarkupsLinePath = os.path.join(sPageMarkupsLineDir, sMarkupsLineFilenameWithExt)

                    # there is a quiz validation for this error - estimation during validation may have been off
                    sErrorMsg = 'ERROR - MarkupsLine not saved. Filename too long : ' + str(len(sMarkupsLinePath))\
                                + '\n' + sMarkupsLinePath\
                                + '\n\nContact Administrator'
                    if len(sMarkupsLinePath) > 256:  # Windows limitation
                        UtilsMsgs.DisplayError(sErrorMsg)

        
                    for oImageNode in oSession.oImageView.GetImageViewList():
                        
                        # match the markup line to the image to save the path to the correct xml Image node
                        if slicer.mrmlScene.GetNodeByID(sAssociatedReferenceNodeID).GetName() == oImageNode.sNodeName:
                            UtilsFilesIO.ExportResultsItemToFile('MarkupsLine', sMarkupsLinePath, slMarkupLine)

                            # store the path name in the xml file
                                
                            sRelativePathToStoreInXml = UtilsFilesIO.GetRelativeUserPath(sMarkupsLinePath)
                            lxLinePathElements = UtilsIOXml.GetChildren(oImageNode.GetXmlImageElement(), 'MarkupLinePath')
                            bPathAlreadyInXml = False
                            for xPathElement in lxLinePathElements:
                                sStoredRelativePath = UtilsIOXml.GetDataInNode(xPathElement)
                                if sStoredRelativePath == sRelativePathToStoreInXml:
                                    bPathAlreadyInXml = True
                                    break
                                
                            if bPathAlreadyInXml == False:   
                                # update xml storing the path to the markup line file with the image element
                                oSession.oCustomWidgets.AddPathElement('MarkupLinePath', oImageNode.GetXmlImageElement(),
                                                        sRelativePathToStoreInXml)

                
            
                UtilsIOXml.SaveXml(UtilsFilesIO.GetUserQuizResultsPath())

            
            
        except Exception as error:
            tb = traceback.format_exc()
            sMsg = "\nSaveMarkupLines: Error saving markup lines to disk. "  \
                    + str(error) \
                    + "\n\n" + tb 
            raise Exception(sMsg)
            
        return

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def CreateUniqueLineName( lAllNodeNamesInScene, sSystemGeneratedName, sAssociatedReferenceNodeName):
        ''' Input parameters:
                - list of all nodes in the scene
                - the system generated node name to be changed
                - name of the associated image node
            If there is already a node that has the proposed name, we need to add the 'next' integer suffix
        '''

        sProposedName =  sAssociatedReferenceNodeName  + '_' + sSystemGeneratedName + '_quizline'
        sUniqueName = sProposedName # default
         
        lExistingNamesWithProposedName = []
        for slNode in lAllNodeNamesInScene:
            if slNode.GetName().find(sProposedName) >= 0:
                lExistingNamesWithProposedName.append(slNode.GetName())
                
        if len(lExistingNamesWithProposedName) > 0:
            sSubstringToSearch = 'quizline_'
            iNewSuffix = UtilsFilesIO.GetSuffix(lExistingNamesWithProposedName, sSubstringToSearch)
            if iNewSuffix > 0:
                sUniqueName = sProposedName + '_' + str(iNewSuffix)

        return sUniqueName
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def GetSuffix( lExistingNamesWithProposedName, sSubstringToSearch ):
    
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
    @staticmethod
    def LoadSavedMarkupLines( oSession):
        ''' Scan the xml for markup line path elements and load the saved file.
        '''
        lxImageElements = []
        lxMarkupLinePaths = []
        
        lxImageElements = UtilsIOXml.GetChildren( oSession.oCustomWidgets.GetNthPageNode(oSession.GetCurrentPageIndex()), 'Image')
        
        for  xImageNode in lxImageElements:
            
            lxMarkupLinePaths = UtilsIOXml.GetChildren( xImageNode, 'MarkupLinePath')
            
            for xLinePathNode in lxMarkupLinePaths:
                
                sStoredRelativePath = UtilsIOXml.GetDataInNode( xLinePathNode )
                if sStoredRelativePath != '':
                    sAbsolutePath = UtilsFilesIO.GetAbsoluteUserPath(sStoredRelativePath)
                    
                    # check that the markup line does not already exist in the scene 
                    #    (if relative path has double extension .mrk.json - additional remove .mrk)
                    sMarkupLineNodeName = UtilsFilesIO.GetFilenameNoExtFromPath(sStoredRelativePath)
                    if sMarkupLineNodeName.endswith('.mrk') and sMarkupLineNodeName != '.mrk':
                        sMarkupLineNodeName = sMarkupLineNodeName[:-len('.mrk')]
                    bFoundMarkupLine, slMarkupLineNode = UtilsFilesIO.CheckForLoadedNodeInScene(sMarkupLineNodeName)
                    
                    if not bFoundMarkupLine:
                        if os.path.exists(sAbsolutePath):
                            # load label map into the scene
                            slMarkupLineNode = slicer.util.loadMarkups(sAbsolutePath)
                        else:
                            sMsg = 'Stored path to markup line file does not exist. Markup line will not be loaded.\n' \
                                + sAbsolutePath
                            UtilsMsgs.DisplayWarning(sMsg)
                            break # continue in for loop for next label map path element
                
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
