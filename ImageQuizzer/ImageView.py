from abc import ABC, abstractmethod

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
from vtkmodules.vtkCommonKitPython import vtkPassInputTypeAlgorithm

##########################################################################
#
#   Class ImageView
#
##########################################################################

class ImageView:
    
    def __init__(self,  parent=None):
        self.sClassName = type(self).__name__
        self.parent = parent
        self.sPageName = ''
        self.sPageDescriptor = ''
        
        self.lValidVolumeFormats = ['nrrd','nii','mhd']
        self.ltupViewNodes = []
        self.lViewNodes = []
        
        

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
        
       
        self.lViewNodes = self.BuildViewNodes(self.xImages)
        
        
        if len(self.lViewNodes) > 0:
            # clear images
            self.AssignViewToNone('Red')
            self.AssignViewToNone('Yellow')
            self.AssignViewToNone('Green')

            for i in range(len(self.lViewNodes)):
                self.AssignNodesToView(self.lViewNodes[i])
#                 if not (self.lViewNodes[i].sRoiVisibilityCode == 'Empty'):
#                     self.SetRoiVisibility( sSeriesInstanceUID, sRoiVisibilityCode, lsRoiList)
                


    #-----------------------------------------------
    #         Manage Data Loading
    #-----------------------------------------------

    def BuildViewNodes(self, xImages):
        

        # for each image
        for indImage in range(len(xImages)):


#             # Extract image attributes
            sVolumeFormat = self.oIOXml.GetValueOfNodeAttribute(xImages[indImage], 'format')
            
            if (sVolumeFormat == 'dicom'):
                oImageViewItem = DicomVolumeDetail(xImages[indImage])
            else:
                oImageViewItem = DataVolumeDetail(xImages[indImage])
                
            oImageViewItem.sNodeName = self.sPageName + '_' + self.sPageDescriptor + '_' + oImageViewItem.sNodeDescriptor
            bLoadSuccess = oImageViewItem.LoadVolume()
                
                
                
                
                
                
# 
# 
#             # if image format/type is dicom/RTStruct, get the ROI elements
#             
#             # set defaults to no RTSTruct
#             sSeriesInstanceUID = ''
#             sRoiVisibilityCode = 'Empty'
#             lsRoiList = []
#             if (sVolumeFormat == 'dicom' and sImageType == 'RTStruct'):
#                 # extract Series UID nodes
#                 xSeriesUIDNodes = self.oIOXml.GetChildren(xImages[indImage], 'SeriesInstanceUID')
#                 if len(xSeriesUIDNodes) > 1:
#                     sWarningMsg = 'There can only be one SeriesInstanceUID element per image. \nThe first defined Series UID in the XML will be used.'
#                     sWarningMsg = sWarningMsg + '    Page name: ' + self.sPageName + '   Page description: ' + self.sPageDescriptor
#                     self.oUtils.DisplayWarning(sWarningMsg)
# 
#                 sSeriesInstanceUID = self.oIOXml.GetDataInNode(xSeriesUIDNodes[0])
#                 sRoiVisibilityCode, lsRoiList = self.ReadROIElements(xImages[indImage])
#             
#             # Load images 
#             bLoadSuccess = True
#             if (sVolumeFormat == 'dicom'):
#                 bLoadSuccess, slNode = self.LoadDicomVolume(sImagePath, sImageType)
# 
# 
#             elif (sVolumeFormat in self.lValidVolumeFormats):
#                 bLoadSuccess, slNode = self.LoadDataVolume(sNodeName, sImageType, sImagePath)
# 
#                         
#             else:
#                 sErrorMsg = ('Undefined volume format : %s' % sVolumeFormat)
#                 self.oUtils.DisplayError(sErrorMsg)
#                 bLoadSuccess = False
# 
#             if bLoadSuccess and (slNode is not None):
#                  
#                 tupViewNode =\
#                  [slNode, sImageDestination, sOrientation, sViewLayer,\
#                  sImageType, sSeriesInstanceUID, sRoiVisibilityCode, lsRoiList]
#                 self.ltupViewNodes.append(tupViewNode)
#                  
#                 if (sVolumeFormat == 'dicom') and (sImageType == 'RTStruct'):
#                     self.ConvertSegmentationToLabelmap(lsRoiList)


            if bLoadSuccess and (oImageViewItem.slNode is not None):
                 
                self.lViewNodes.append(oImageViewItem)
                 
#                 if (sVolumeFormat == 'dicom') and (sImageType == 'RTStruct'):
#                     self.ConvertSegmentationToLabelmap(lsRoiList)

    
        return self.lViewNodes
                    
                    
         
    #-----------------------------------------------
    #         Manage Views
    #-----------------------------------------------
 
#    def AssignNodesToView(self, sSlicerNodeName, sImageDestination, sNodeLayer, sOrientation):
#  
#         slWidget = slicer.app.layoutManager().sliceWidget(sImageDestination)
#         slWindowLogic = slWidget.sliceLogic()
#         slWindowCompositeNode = slWindowLogic.GetSliceCompositeNode()
#         if sNodeLayer == 'Background':
#             slWindowCompositeNode.SetBackgroundVolumeID(slicer.util.getNode(sSlicerNodeName).GetID())
#             slWidget.setSliceOrientation(sOrientation)
#         elif sNodeLayer == 'Foreground':
#             slWindowCompositeNode.SetForegroundVolumeID(slicer.util.getNode(sSlicerNodeName).GetID())
#             slWidget.setSliceOrientation(sOrientation)
#         elif sNodeLayer == 'Label':
#             slWindowCompositeNode.SetLabelVolumeID(slicer.util.getNode(sSlicerNodeName).GetID())
#         
         
    def AssignNodesToView(self, oViewNode):
 
        slWidget = slicer.app.layoutManager().sliceWidget(oViewNode.sDestination)
        slWindowLogic = slWidget.sliceLogic()
        slWindowCompositeNode = slWindowLogic.GetSliceCompositeNode()
        if oViewNode.sViewLayer == 'Background':
            slWindowCompositeNode.SetBackgroundVolumeID(slicer.util.getNode(oViewNode.sNodeName).GetID())
            slWidget.setSliceOrientation(oViewNode.sOrientation)
        elif oViewNode.sViewLayer == 'Foreground':
            slWindowCompositeNode.SetForegroundVolumeID(slicer.util.getNode(oViewNode.sNodeName).GetID())
            slWidget.setSliceOrientation(oViewNode.sOrientation)
        elif oViewNode.sViewLayer == 'Label':
            slWindowCompositeNode.SetLabelVolumeID(slicer.util.getNode(oViewNode.sNodeName).GetID())
        
         

    #-----------------------------------------------
    
    def AssignViewToNone(self, sScreenColor):
        
        slWidget = slicer.app.layoutManager().sliceWidget(sScreenColor)
        slLogic = slWidget.sliceLogic()
        slCompNode = slLogic.GetSliceCompositeNode()
        slCompNode.SetBackgroundVolumeID('None')
        slCompNode.SetForegroundVolumeID('None')
        slCompNode.SetLabelVolumeID('None')
        
    #-----------------------------------------------

    def SetRoiVisibility(self, sSeriesInstanceUID, sRoiVisibilityCode, lsUserSelectRoiList):
        # in order to set visibility, you have to traverse Slicer's subject hierarchy
        # accessing the segmentation node, its children (to get ROI names) and its data node
        
        
        # get Slicer's subject hierarchy node (SHNode)
        
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
        
        
        # adjust visibility of each ROI as per user's request
        
        if (sRoiVisibilityCode == 'All'):
            for indSHList in range(len(lsSubjectHierarchyROINames)):
                slSegNode.SetSegmentVisibility(lsSubjectHierarchyROINames[indSHList],True)
                
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

    def ConvertSegmentationToLabelmap(self, lsRoiList):
        
        # To gain control of segment visibility in different view windows,
        # the ROI's in the Segmentation layer are converted to label maps
        
        # add a label map node to the subject hierarchy
        slLabelMapNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLabelMapVolumeNode')
        
        # get the segmentation node containing the ROI's to be converted
        
        
        
        
    
    
    
##########################################################################
#
#   Class ViewNodeBase
#
##########################################################################

class ViewNodeBase(ABC):
    """ Inherits from ABC - Abstract Base Class
    """

    def __init__(self,  parent=None):
        self.sClassName = type(self).__name__
        self.parent = parent
    
        self._slNode = None
        self._sVolumeFormat = ''
        self._sDestination = ''
        self._sOrientation = ''
        self._sViewLayer = ''
        self._sImageType = ''
        self._sImagePath = ''
        self._sNodeName = ''
        
        #--------------------
        # define getters and setters
        #     use indirection - the setter calls an abstract method
        #--------------------
        
        @property
        def sImageType(self):
            return self._sImageType
        
        @sImageType.setter
        def sImageType(self, sInput):
            self._sImageType_setter(sInput)
            
        @abstractmethod
        def _sImageType_setter(self, sInput): pass
 
        #--------------------
         
        @property
        def sNodeName(self):
            return self._sNodeName
        
        @sNodeName.setter
        def sNodeName(self, sInput):
            self._sNodeName_setter(sInput)
            
        @abstractmethod
        def _sNodeName_setter(self, sInput): pass
        
        #--------------------

        @property
        def sImagePath(self):
            return self._sImagePath
        
        @sImagePath.setter
        def sImagePath(self, sInput):
            self._sImagePath_setter(sInput)
            
        @abstractmethod
        def _sImpagePath_setter(self, sInput): pass

        #--------------------

        @property
        def sViewLayer(self):
            return self._sViewLayer
        
        @sViewLayer.setter
        def sViewLayer(self, sInput):
            self._sViewLayer_setter(sInput)
            
        @abstractmethod
        def _sViewLayer_setter(self, sInput): pass
        
        #--------------------

        @property
        def sOrientation(self):
            return self._sOrientation
        
        @sOrientation.setter
        def sOrientation(self, sInput):
            self._sOrientation_setter(sInput)
            
        @abstractmethod
        def _sOrientation_setter(self, sInput): pass

        #--------------------

        @property
        def sDestination(self):
            return self._sDestination
        
        @sDestination.setter
        def sDestination(self, sInput):
            self._sDestination_setter(sInput)
            
        @abstractmethod
        def _sDestination_setter(self, sInput): pass

        #--------------------

        @property
        def sVolumeFormat(self):
            return self._sVolumeFormat
        
        @sVolumeFormat.setter
        def sVolumeFormat(self, sInput):
            self._sVolumeFormat_setter(sInput)
            
        @abstractmethod
        def _sVolumeFormat_setter(self, sInput): pass
        
        #--------------------

        @property
        def slNode(self):
            return self._slNode
        
        @slNode.setter
        def slNode(self, sInput):
            self._slNode_setter(sInput)
            
        @abstractmethod
        def _slNode_setter(self, sInput): pass

        #--------------------



        
    #-----------------------------------------------

    def ExtractImageAttributes(self):

        self.sNodeDescriptor = self.oIOXml.GetValueOfNodeAttribute(self.xImage, 'descriptor')
        self.sImageType = self.oIOXml.GetValueOfNodeAttribute(self.xImage, 'type')
        self.sDestination = self.oIOXml.GetValueOfNodeAttribute(self.xImage, 'destination')
        self.sOrientation = self.oIOXml.GetValueOfNodeAttribute(self.xImage, 'orientation')
        self.sVolumeFormat = self.oIOXml.GetValueOfNodeAttribute(self.xImage, 'format')
    
    #-----------------------------------------------

    def ExtractXMLNodeElements(self):
        
        # Extract path element
        xPathNodes = self.oIOXml.GetChildren(self.xImage, 'Path')

        if len(xPathNodes) > 1:
            sWarningMsg = 'There can only be one path per image.  The first defined path will be used.'
            sWarningMsg = sWarningMsg + '    Page name: ' + self.sPageName + '   Page description: ' + self.sPageDescriptor
            self.oUtils.DisplayWarning( sWarningMsg )

        self.sImagePath = self.oIOXml.GetDataInNode(xPathNodes[0])
        
        # Extract destination layer (foreground, background, label)
        xLayerNodes = self.oIOXml.GetChildren(self.xImage, 'Layer')
        if len(xLayerNodes) > 1:
            sWarningMsg = 'There can only be one destination layer (foreground, background or label) per image. \nThe first defined destination in the XML will be used.'
            sWarningMsg = sWarningMsg + '    Page name: ' + self.sPageName + '   Page description: ' + self.sPageDescriptor
            self.oUtils.DisplayWarning(sWarningMsg)

        self.sViewLayer = self.oIOXml.GetDataInNode(xLayerNodes[0])
    
    

    #-----------------------------------------------

    def CheckForNodeExists(self, sNodeClass):
        # a node does not have to be loaded if it already exists
        
        
        # initialize
        bNodeExists = False
        self.slNode = None
        
        # check for nodes by name and check it's the proper class
        try:
            self.slNode = slicer.mrmlScene.GetFirstNodeByName(self.sNodeName)
            if (self.slNode.GetClassName() == sNodeClass) :
                bNodeExists = True
        except:
            bNodeExists = False
        
        return bNodeExists
    
    
##########################################################################
#
#   Class DataVolumeDetail
#
##########################################################################

class DataVolumeDetail(ViewNodeBase):
    
    
    def __init__(self, xImage):
        self.sClassName = type(self).__name__
        self.lValidVolumeFormats = ['nrrd','nii','mhd']
        self.oIOXml = UtilsIOXml()
        self.oUtils = Utilities()
        self.xImage = xImage


        self.ExtractImageAttributes()
        self.ExtractXMLNodeElements()

    def LoadVolume(self):
        bLoadSuccess = self.LoadDataVolume()
        return bLoadSuccess
            


    #-----------------------------------------------

    def LoadDataVolume(self):
        
        # Load a 3D data volume file - check if already loaded (node exists)
        
        dictProperties = {}
        bNodeExists = False
        self.slNode = None


        try:
                    
            bLoadSuccess = True
            if (self.sImageType == 'Volume'):
                
                bNodeExists = self.CheckForNodeExists('vtkMRMLScalarVolumeNode')
                if not (bNodeExists):
                    self.slNode = slicer.util.loadVolume(self.sImagePath, {'show': False, 'name': self.sNodeName})
                else: # make sure a node exists
                    if bNodeExists and (self.slNode is None):
                        bLoadSuccess = False
            
            elif (self.sImageType == 'Labelmap'):
                
                bNodeExists = self.CheckForNodeExists( 'vtkMRMLLabelMapVolumeNode')
                dictProperties = {'labelmap' : True, 'show': False, 'name': self.sNodeName}
                if not (bNodeExists):
                    self.slNode = slicer.util.loadLabelVolume(self.sImagePath, dictProperties)
                else: # make sure a node exists
                    if bNodeExists and (self.slNode is None):
                        bLoadSuccess = False
                    
            else:
                
                sErrorMsg = ('Undefined image type: %s' % self.sImageType)
                self.oUtils.DisplayError(sErrorMsg)
                bLoadSuccess = False
                
        except:
            
            bLoadSuccess = False
        
        
        return bLoadSuccess
    




##########################################################################
#
#   Class DicomVolumeDetail
#
##########################################################################

class DicomVolumeDetail(ViewNodeBase):
    
    
    def __init__(self, xImage):
        self.sClassName = type(self).__name__
        self.lValidVolumeFormats = ['dicom']
        self.oIOXml = UtilsIOXml()
        self.oUtils = Utilities()
        self.xImage = xImage
        
        self._sRoiVisibilityCode = ''

        #--------------------
        # define getters and setters
        #     use indirection - the setter calls an abstract method
        #--------------------
        
        @property
        def sRoiVisibilityCode(self):
            return self._sRoiVisibilityCode
        
        @sRoiVisibilityCode.setter
        def sRoiVisibilityCode(self, sInput):
            self._sRoiVisibilityCode_setter(sInput)
            
        @abstractmethod
        def _sRoiVisibilityCode_setter(self, sInput): pass





        self.ExtractImageAttributes()
        self.ExtractXMLNodeElements()
        self.ExtractROIElements()
        
        
    def ExtractROIElements(self):
        print('Getting ROI Stuff')
        #             # set defaults to no RTSTruct
        sSeriesInstanceUID = ''
        self.sRoiVisibilityCode = 'Empty'
        lsRoiList = []
        if (self.sImageType == 'RTStruct'):
            # extract Series UID nodes
            xSeriesUIDNodes = self.oIOXml.GetChildren(self.xImage, 'SeriesInstanceUID')
            if len(xSeriesUIDNodes) > 1:
                sWarningMsg = 'There can only be one SeriesInstanceUID element per image. \nThe first defined Series UID in the XML will be used.'
                sWarningMsg = sWarningMsg + '    Page name: ' + self.sPageName + '   Page description: ' + self.sPageDescriptor
                self.oUtils.DisplayWarning(sWarningMsg)

            sSeriesInstanceUID = self.oIOXml.GetDataInNode(xSeriesUIDNodes[0])
            lsRoiList = self.ReadROIElements()
        
#         # Load images 
#         bLoadSuccess = True
#         if (sVolumeFormat == 'dicom'):
#             bLoadSuccess, slNode = self.LoadDicomVolume(sImagePath, sImageType)

        
    def LoadVolume(self):
            bLoadSuccess = self.LoadDicomVolume()
            return bLoadSuccess
        

    #-----------------------------------------------

    def LoadDicomVolume(self):
        self.slNode = None
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
            
            sSeriesUIDToLoad = database.fileValue(self.sImagePath, tags['seriesUID'])
            sPatientName = database.fileValue(self.sImagePath , tags['patientName'])
            sPatientID = database.fileValue(self.sImagePath , tags['patientID'])
            sExpectedSubjectHierarchyName = sPatientName + ' (' + sPatientID + ')'
            print(' ~~~ Subject Hierarchy expected name : %s' % sExpectedSubjectHierarchyName)
            
            # get directory that stores the dicom series
            sHead_Tail = os.path.split(self.sImagePath)
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
            
            self.slNode = slSubjectHierarchyNode.GetItemDataNode(slNodeId)
            bLoadSuccess = True
        
        else:
            sErrorMsg = ('Slicer Database is not open')
            self.oUtils.DisplayError(sErrorMsg)
        

        return bLoadSuccess

    #-----------------------------------------------

    def ReadROIElements(self):
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
        xRoisNode = self.oIOXml.GetChildren(self.xImage, 'ROIs')
        
        # get visibility code from the attribute
        self.sRoiVisibilityCode = self.oIOXml.GetValueOfNodeAttribute(xRoisNode[0], 'roiVisibilityCode')

        if (self.sRoiVisibilityCode == 'Select' or self.sRoiVisibilityCode == 'Ignore'):
            
            # get list of ROI children
            xRoiChildren = self.oIOXml.GetChildren(xRoisNode[0], 'ROI')

            for indRoi in range(len(xRoiChildren)):
                sRoiName = self.oIOXml.GetDataInNode(xRoiChildren[indRoi])
                lsRoiList.append(sRoiName)
                
                print('**** ROI :%s' % sRoiName)
        
        return lsRoiList
        

        