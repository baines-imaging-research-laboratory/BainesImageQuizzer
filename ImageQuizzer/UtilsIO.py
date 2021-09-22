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

        self.oUtilsMsgs = UtilsMsgs()

#     def setup(self):
#         self.oUtilsMsgs = UtilsMsgs()
        
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
        self._sScriptedModulesPath = eval('slicer.modules.%s.path' % sModuleName.lower())
        self._sScriptedModulesPath = os.path.dirname(self._sScriptedModulesPath)
        self._sXmlResourcesDir = os.path.join(self._sScriptedModulesPath, sSourceDirForQuiz)
        self.SetResourcesROIColorFilesDir()
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
    def PopulateUserQuizFolder(self):
            
        # check if quiz file already exists in the user folder - if not, copy from Resources

#         # setup for new location
#         self._sUserQuizResultsPath = os.path.join(self._sUserDir, self._sQuizFilename)

        if not os.path.isfile(self.GetUserQuizResultsPath()):
            # file not found, copy file from Resources to User folder
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
                         
#                             if (oSession.oIOXml.GetValueOfNodeAttribute(oSession.oIOXml.GetRootNode(), 'SaveLabelMapAsRTStruct')) == 'Y':
#                                 bRTStructSaved, sRTStructMsg, sDicomExportOutputDir = self.SaveLabelMapAsRTStruct(oImageNode, sLabelMapFilename, sPageLabelMapDir)
#   
#                                 if (oSession.oIOXml.GetValueOfNodeAttribute(oSession.oIOXml.GetRootNode(), 'MapRTStructToVolume')) == 'Y':
#                                     try:
#                                         if oImageNode.sVolumeFormat == 'DICOM':
#                                             sOriginalDicomPath = oImageNode.sImagePath
#                                             sOriginalDicomDir = self.GetDirFromPath(sOriginalDicomPath)
#                                         else:
#                                             xImage = oImageNode.GetXmlImageElement()
#                                             xOrigDicomDirElement = oSession.oIOXml.GetNthChild(xImage, 'OriginalDicomDir', 0 )
#                                             if xOrigDicomDirElement != None:
#                                                 sOrigDicomRelativeDir = oSession.oIOXml.GetDataInNode(xOrigDicomDirElement)
#                                                 sOriginalDicomDir = self.GetAbsoluteDataPath(sOrigDicomRelativeDir)
#                                             else:
#                                                 sMsg = 'Study set up to remap exported RTStruct to original dicom volume'\
#                                                         + '\n but XML element OriginalDicomDir is missing'\
#                                                         + '\nFor page:' + str(oSession.GetCurrentPageIndex()) \
#                                                         + '\nSee administrator: ' + sys._getframe(  ).f_code.co_name
#                                                 oSession.oUtilsMsgs.DisplayWarning(sMsg) 
#                                         # args=(original dicom series, Slicer's dicom output, SaveTo dir)
# #                                         self.mapRTStructToVolume(self.GetDirFromPath(oImageNode.sImagePath), sDicomExportOutputDir, sPageLabelMapDir )
# #                                         self.mapRTStructToVolume(self.GetDirFromPath(sOriginalDicomPath), sDicomExportOutputDir, sPageLabelMapDir )
#                                         self.mapRTStructToVolume(sOriginalDicomDir, sDicomExportOutputDir, sPageLabelMapDir )
#                                         shutil.rmtree(sDicomExportOutputDir, ignore_errors=True)
# 
#                                     except:
#                                         sMsg = 'Failed to map exported RTStruct to original volume.'\
#                                                 + '\nNotes: - It is possible that the original dicom had irregular geometry'\
#                                                 + '\n- or that the number of slices output by Slicer does not match that of the original volume'\
#                                                 + '\n- The following packages are required for mapping to the original volume UIDs: Pandas, pydicom and numpy'\
#                                                 + '\n' + sys._getframe(  ).f_code.co_name
#                                         oSession.oUtilsMsgs.DisplayWarning(sMsg) 
# 
# 
#                             
#                             else:
#                                 bRTStructSaved = True # allow label map path to be written to xml
                                 
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
                if (oSession.oIOXml.GetValueOfNodeAttribute(oImageNode.GetXmlImageElement(), 'UsePreviousLabelMap') == 'Y'):
                    bUsePreviousLabelMap = True
                else:
                    bUsePreviousLabelMap = False

        
                # look at latest instance of the label map elements stored in the xml
                xLabelMapPathElement = oSession.oIOXml.GetLatestChildElement(oImageNode.GetXmlImageElement(), 'LabelMapPath')
                slLabelMapNode = None # initialize

                # if there were no label map paths stored with the image, and xml attribute has flag 
                #    to use a previous label map, check previous pages for the first matching image
                if xLabelMapPathElement == None and bUsePreviousLabelMap == True:
                    xHistoricalLabelMapMatch = oSession.CheckXmlImageHistoryForMatch( oImageNode.GetXmlImageElement(), 'LabelMapPath')
                    
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
