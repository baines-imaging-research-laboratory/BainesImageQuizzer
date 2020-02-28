import PythonQt
import os
import vtk, qt, ctk, slicer
import sys
import unittest

from Utilities import *

from DICOMLib import DICOMUtils

import xml
from xml.dom import minidom
import ssl
from DICOMLib.DICOMUtils import loadPatientByUID

#-----------------------------------------------

class ImageView:
    
    def __init__(self,  parent=None):
        self.sClassName = type(self).__name__
        self.parent = parent
        self.sPageName = ''
        self.sPageDescriptor = ''
        
        self.lValidVolumeFormats = ['nrrd','nii','mhd']
        self.ltupViewNodes = []
        

    #-----------------------------------------------

    def RunSetup(self, xPageNode, quizLayout):

        self.quizLayout = quizLayout
        self.oIOXml = UtilsIOXml()
        self.oUtils = Utilities()


        # get name and descriptor
        self.sPageName = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'name')
        self.sPageDescriptor = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'descriptor')

        # display Images
        self.xImages = self.oIOXml.GetChildren(xPageNode, 'Image')
        self.iNumImages = self.oIOXml.GetNumChildren(xPageNode, 'Image')
        
        self.ltupViewNodes = self.BuildViewNodes(self.xImages)
        
        
        if len(self.ltupViewNodes) > 0:
            # clear images
            self.AssignViewToNone('Red')
            self.AssignViewToNone('Yellow')
            self.AssignViewToNone('Green')

            for i in range(len(self.ltupViewNodes)):
                
                # get node details
                slNode, sImageDestination, sOrientation, sViewLayer, sImageType, sSeriesInstanceUID, sRoiVisibilityCode, lsRoiList = self.ltupViewNodes[i]
                self.AssignNodesToView(slNode.GetName(), sImageDestination, sViewLayer, sOrientation)
                if not (sRoiVisibilityCode == 'Empty'):
                    self.SetRoiVisibility( sSeriesInstanceUID, sRoiVisibilityCode, lsRoiList)


    #-----------------------------------------------
    #         Manage Data Loading
    #-----------------------------------------------

    def BuildViewNodes(self, xImages):
        
        # for each image
        for indImage in range(len(xImages)):


            # Extract image attributes
            sVolumeFormat = self.oIOXml.GetValueOfNodeAttribute(xImages[indImage], 'format')
            sNodeDescriptor = self.oIOXml.GetValueOfNodeAttribute(xImages[indImage], 'descriptor')
            sImageType = self.oIOXml.GetValueOfNodeAttribute(xImages[indImage], 'type')
            sImageDestination = self.oIOXml.GetValueOfNodeAttribute(xImages[indImage], 'destination')
            sOrientation = self.oIOXml.GetValueOfNodeAttribute(xImages[indImage], 'orientation')
            sNodeName = self.sPageName + '_' + self.sPageDescriptor + '_' + sNodeDescriptor

            
            # Extract path element
            xPathNodes = self.oIOXml.GetChildren(xImages[indImage], 'Path')

            if len(xPathNodes) > 1:
                sWarningMsg = 'There can only be one path per image.  The first defined path will be used.'
                sWarningMsg = sWarningMsg + '    Page name: ' + self.sPageName + '   Page description: ' + self.sPageDescriptor
                self.oUtils.DisplayWarning( sWarningMsg )

            sImagePath = self.oIOXml.GetDataInNode(xPathNodes[0])
            

            # Extract destination layer (foreground, background, label)
            xLayerNodes = self.oIOXml.GetChildren(xImages[indImage], 'Layer')
            if len(xLayerNodes) > 1:
                sWarningMsg = 'There can only be one destination layer (foreground, background or label) per image. \nThe first defined destination in the XML will be used.'
                sWarningMsg = sWarningMsg + '    Page name: ' + self.sPageName + '   Page description: ' + self.sPageDescriptor
                self.oUtils.DisplayWarning(sWarningMsg)

            sViewLayer = self.oIOXml.GetDataInNode(xLayerNodes[0])


            ##########################
            #
            # handle image load Dicom / Other Valid Formats
            #
            ##########################
            
            # set defaults    
            sSeriesInstanceUID = ''
            sRoiVisibilityCode = 'Empty'
            lsRoiList = []
            bLoadSuccess = True
            
            if (sVolumeFormat == 'dicom'):
                
                # extract Series UID nodes
                xSeriesUIDNodes = self.oIOXml.GetChildren(xImages[indImage], 'SeriesInstanceUID')
                 
                if len(xSeriesUIDNodes) > 1:
                    sWarningMsg = 'There can only be one SeriesInstanceUID element per image. \nThe first defined Series UID in the XML will be used.'
                    sWarningMsg = sWarningMsg + '    Page name: ' + self.sPageName + '   Page description: ' + self.sPageDescriptor
                    self.oUtils.DisplayWarning(sWarningMsg)
                elif len(xSeriesUIDNodes) == 0:
                    sErrorMsg = ('There was no Series UID .. THIS SHOULD NOT HAPPEN : %s' % sVolumeFormat)
                    sErrorMsg = sErrorMsg + '    Page name: ' + self.sPageName + '   Page description: ' + self.sPageDescriptor
                    self.oUtils.DisplayError(sErrorMsg)
                else:
                    sSeriesInstanceUID = self.oIOXml.GetDataInNode(xSeriesUIDNodes[0])
                
                # if dicom is a volume series - store reference UID
                if (sImageType == 'Volume'):
                    sReferenceSeriesUID = sSeriesInstanceUID

                # for RTStruct, store segmentation Series UID and get list of ROIs
                elif (sImageType == 'RTStruct'):
                    # extract Series UID nodes
                    xSeriesUIDNodes = self.oIOXml.GetChildren(xImages[indImage], 'SeriesInstanceUID')
                    sRoiVisibilityCode, lsRoiList = self.ReadROIElements(xImages[indImage])
                                        
                else:
                    bLoadSuccess = False
                    sErrorMsg = ('Undefined dicom series type : %s' % sVolumeFormat)
                    sErrorMsg = sErrorMsg + '    Page name: ' + self.sPageName + '   Page description: ' + self.sPageDescriptor
                    self.oUtils.DisplayError(sErrorMsg)
                    
                
                # load dicom
                bLoadSuccess, slNode = self.LoadDicomVolume(sImagePath, sImageType)   


            # handle other valid formats
            elif (sVolumeFormat in self.lValidVolumeFormats):
                bLoadSuccess, slNode = self.LoadDataVolume(sNodeName, sImageType, sImagePath)

                        
            # error - not a valid format                        
            else:
                bLoadSuccess = False
                sErrorMsg = ('Undefined volume format : %s' % sVolumeFormat)
                self.oUtils.DisplayError(sErrorMsg)


            # after load, return image properties in list of tuples
            if bLoadSuccess and (slNode is not None):
                tupViewNode =\
                 [slNode, sImageDestination, sOrientation, sViewLayer,\
                 sImageType, sSeriesInstanceUID, sRoiVisibilityCode, lsRoiList]
                self.ltupViewNodes.append(tupViewNode)
            
            
    
        return self.ltupViewNodes
                    
                    
         
    #-----------------------------------------------

    def ReadROIElements(self, xImage):
        # if the Image type is RTStuct, XML holds a visibility code and (if applicable)
        # a list of ROI names
        # The visibility code is as follows: 
        #    'All' : turn on visibility of all ROIs in RTStruct
        #    'None': turn off visibility of all ROIs in RTStruct
        #    'Ignore' : turn on all ROIs except the ones listed
        #    'Select' : turn on visibility of only ROIs listed
        
        # default - remains empty for All or None
        lsRoiList = []
        
        # get XML ROIs element
        xRoisNode = self.oIOXml.GetChildren(xImage, 'ROIs')
        
        # get visibility code from the attribute
        sRoiVisibilityCode = self.oIOXml.GetValueOfNodeAttribute(xRoisNode[0], 'roiVisibilityCode')

        if (sRoiVisibilityCode == 'Select' or sRoiVisibilityCode == 'Ignore'):
            
            # get list of ROI children
            xRoiChildren = self.oIOXml.GetChildren(xRoisNode[0], 'ROI')

            for indRoi in range(len(xRoiChildren)):
                sRoiName = self.oIOXml.GetDataInNode(xRoiChildren[indRoi])
                lsRoiList.append(sRoiName)
                
                print('**** ROI :%s' % sRoiName)
        
        return sRoiVisibilityCode, lsRoiList
        
    #-----------------------------------------------

    def SetRoiVisibility(self, sSeriesInstanceUID, sRoiVisibilityCode, lsUserSelectRoiList):
        
        # in order to set visibility, get Slicer's subject hierarchy node (SHNode)
        slSHNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        
        # get the item ID for the RTStruct through the Series Instance UID
        slRTStructItemId = slSHNode.GetItemByUID(slicer.vtkMRMLSubjectHierarchyConstants.GetDICOMUIDName(), sSeriesInstanceUID)

        # using slicers vtk Item Id for the RTStruct, get the ROI names (children)
        slRTStructChildren = vtk.vtkIdList()    # initialize to ItemId type
        slSHNode.GetItemChildren(slRTStructItemId, slRTStructChildren) # populate children variable
        
        # get ROI child Item ID and store the child (ROI) name
        lsSubjectHierarchyROINames = []
        for indROI in range(slRTStructChildren.GetNumberOfIds()):
            slROIItemId = slRTStructChildren.GetId(indROI)
            sROIName = slSHNode.GetItemName(slROIItemId)
            lsSubjectHierarchyROINames.append(sROIName)
        
        # get segmentation node name from data node
        slSegDataNode = slSHNode.GetItemDataNode(slRTStructItemId)
        slSegNodeId = slSegDataNode.GetDisplayNodeID()
        slSegNode = slicer.mrmlScene.GetNodeByID(slSegNodeId)
        
        
        # all ROIs visible
        if (sRoiVisibilityCode == 'All'):
            for indSHList in range(len(lsSubjectHierarchyROINames)):
                slSegNode.SetSegmentVisibility(lsSubjectHierarchyROINames[indSHList],True)

        # all ROIs hidden
        if (sRoiVisibilityCode == 'None'):
            for indSHList in range(len(lsSubjectHierarchyROINames)):
                slSegNode.SetSegmentVisibility(lsSubjectHierarchyROINames[indSHList],False)
            
        # turn ON all ROI's and then turn OFF user's list    
        if (sRoiVisibilityCode == 'Ignore'):
            for indSHList in range(len(lsSubjectHierarchyROINames)):
                slSegNode.SetSegmentVisibility(lsSubjectHierarchyROINames[indSHList],True)
            for indUserList in range(len(lsUserSelectRoiList)):
                slSegNode.SetSegmentVisibility(lsUserSelectRoiList[indUserList], False)

        # turn OFF all ROI's and then turn ON user's list    
        if (sRoiVisibilityCode == 'Select'):
            for indSHList in range(len(lsSubjectHierarchyROINames)):
                slSegNode.SetSegmentVisibility(lsSubjectHierarchyROINames[indSHList],False)
            for indUserList in range(len(lsUserSelectRoiList)):
                slSegNode.SetSegmentVisibility(lsUserSelectRoiList[indUserList], True)
        
    #-----------------------------------------------

    def LoadDataVolume(self, sNodeName, sImageType, sImagePath):
        
        # Load a 3D data volume file - check if already loaded (node exists)
        
        dictProperties = {}
        bNodeExists = False
        slNode = None


        try:
                    
            bLoadSuccess = True
            if (sImageType == 'Volume'):
                
                bNodeExists, slNode = self.CheckForNodeExists(sNodeName, 'vtkMRMLScalarVolumeNode')
                if not (bNodeExists):
                    slNode = slicer.util.loadVolume(sImagePath, {'show': False, 'name': sNodeName})
                else: # make sure a node exists
                    if bNodeExists and (slNode is None):
                        bLoadSuccess = False
            
            elif (sImageType == 'Labelmap'):
                
                bNodeExists, slNode = self.CheckForNodeExists(sNodeName, 'vtkMRMLLabelMapVolumeNode')
                dictProperties = {'labelmap' : True, 'show': False, 'name': sNodeName}
                if not (bNodeExists):
                    slNode = slicer.util.loadLabelVolume(sImagePath, dictProperties)
                else: # make sure a node exists
                    if bNodeExists and (slNode is None):
                        bLoadSuccess = False
                    
            else:
                
                sErrorMsg = ('Undefined image type: %s' % sImageType)
                self.oUtils.DisplayError(sErrorMsg)
                bLoadSuccess = False
                
        except:
            
            bLoadSuccess = False
        
        
        return bLoadSuccess, slNode
    
    #-----------------------------------------------

    def LoadDicomVolume(self, sDicomFilePath, sImageType):
        slNode = None
        bLoadSuccess = False

        # first check if patient/series was already imported into the database
        
        database = slicer.dicomDatabase
        if (database.isOpen):
            bSeriesFoundInDB = False   # initialize
            
            lAllSeriesUIDs = DICOMUtils.allSeriesUIDsInDatabase(database)
            tags = {}
            tags['patientName'] = "0010,0010"
            tags['patientID'] = "0010,0020"
            tags['seriesUID'] = "0020,000E"
            
            sSeriesUIDToLoad = database.fileValue(sDicomFilePath, tags['seriesUID'])
            sPatientName = database.fileValue(sDicomFilePath , tags['patientName'])
            sPatientID = database.fileValue(sDicomFilePath , tags['patientID'])
            sExpectedSubjectHierarchyName = sPatientName + ' (' + sPatientID + ')'
#             print(' ~~~ Subject Hierarchy expected name : %s' % sExpectedSubjectHierarchyName)
            
            # get directory that stores the dicom series
            sHead_Tail = os.path.split(sDicomFilePath)
            sDicomSeriesDir = sHead_Tail[0]
            
            # check if already loaded into the database
            for sImportedSeries in lAllSeriesUIDs:
                if sImportedSeries == sSeriesUIDToLoad:
                    bSeriesFoundInDB = True
                
            # if not already loaded, import from series directory    
            if not bSeriesFoundInDB:
                DICOMUtils.importDicom(sDicomSeriesDir)


            # check subject hierarchy to see if volume already exists
            bVolumeAlreadyLoaded = False
            
            
            slSubjectHierarchyNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
            slNodeId = slSubjectHierarchyNode.GetItemByUID(slicer.vtkMRMLSubjectHierarchyConstants.GetDICOMUIDName(),sSeriesUIDToLoad)
            if slNodeId > 0:
                bVolumeAlreadyLoaded = True
            else:
                DICOMUtils.loadSeriesByUID([sSeriesUIDToLoad])
                slNodeId = slSubjectHierarchyNode.GetItemByUID(slicer.vtkMRMLSubjectHierarchyConstants.GetDICOMUIDName(),sSeriesUIDToLoad)
            
            slNode = slSubjectHierarchyNode.GetItemDataNode(slNodeId)
            bLoadSuccess = True
        
        else:
            sErrorMsg = ('Slicer Database is not open')
            self.oUtils.DisplayError(sErrorMsg)
        

        return bLoadSuccess, slNode
    
    #-----------------------------------------------
    #         Manage Views
    #-----------------------------------------------
 
    def AssignNodesToView(self, sSlicerNodeName, sImageDestination, sNodeLayer, sOrientation):
 
        slWidget = slicer.app.layoutManager().sliceWidget(sImageDestination)
        slWindowLogic = slWidget.sliceLogic()
        slWindowCompositeNode = slWindowLogic.GetSliceCompositeNode()
        if sNodeLayer == 'Background':
            slWindowCompositeNode.SetBackgroundVolumeID(slicer.util.getNode(sSlicerNodeName).GetID())
            slWidget.setSliceOrientation(sOrientation)
        elif sNodeLayer == 'Foreground':
            slWindowCompositeNode.SetForegroundVolumeID(slicer.util.getNode(sSlicerNodeName).GetID())
            slWidget.setSliceOrientation(sOrientation)
        elif sNodeLayer == 'Label':
            slWindowCompositeNode.SetLabelVolumeID(slicer.util.getNode(sSlicerNodeName).GetID())
        
         

    #-----------------------------------------------
    
    def AssignViewToNone(self, sScreenColor):
        
        slWidget = slicer.app.layoutManager().sliceWidget(sScreenColor)
        slLogic = slWidget.sliceLogic()
        slCompNode = slLogic.GetSliceCompositeNode()
        slCompNode.SetBackgroundVolumeID('None')
        slCompNode.SetForegroundVolumeID('None')
        slCompNode.SetLabelVolumeID('None')
        

    #-----------------------------------------------

    def CheckForNodeExists(self, sNodeName, sNodeClass):
        # a node does not have to be loaded if it already exists
        
        
        # initialize
        bNodeExists = False
        slNode = None
        
        # check for nodes by name and check it's the proper class
        try:
            slNode = slicer.mrmlScene.GetFirstNodeByName(sNodeName)
            if (slNode.GetClassName() == sNodeClass) :
                bNodeExists = True
        except:
            bNodeExists = False
        
        return bNodeExists, slNode
    
    
