from abc import ABC, abstractmethod

import PythonQt
import os
import vtk, qt, ctk, slicer
import sys
import unittest

from Utilities import *

from DICOMLib import DICOMUtils

import ssl
from DICOMLib.DICOMUtils import loadPatientByUID


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
        
        self.lValidVolumeFormats = ['nrrd', 'nii', 'mhd', 'dicom']
        self._loImageViews = []
        self.bLinkViews = False
        
        
    #----------
    def GetImageViewList(self):
        return self._loImageViews


    #-----------------------------------------------

    def RunSetup(self, xPageNode, quizLayout):

        self.quizLayout = quizLayout
        self.oIOXml = UtilsIOXml()
        self.oUtilsMsgs = UtilsMsgs()


        # get name and descriptor
        self.sPageName = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'name')
        self.sPageDescriptor = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'descriptor')
        
        # assign link views
        if (self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'linkviews') == 'y'):
            self.bLinkViews = True
        else:
            self.bLinkViews = False

        # display Images
        self.xImageNodes = self.oIOXml.GetChildren(xPageNode, 'Image')
        self.iNumImages = self.oIOXml.GetNumChildrenByName(xPageNode, 'Image')
        
        # clear views from previous page
        self.ClearImagesAndSegmentations()
       
        self.BuildViewNodes()
        
        

        # Assign images to view with proper orientation
        if len(self._loImageViews) > 0:
            
            # assign nodes for current page to views
            for i in range(len(self._loImageViews)):
                
                self.AssignNodesToView(self._loImageViews[i])
                
        # reset field of view to maximize background
        slicer.util.resetSliceViews()
                
                
            

    #-----------------------------------------------
    #         Manage Data Loading
    #-----------------------------------------------

    def BuildViewNodes(self):
        
        bLoadSuccess = False
        # for each image
        for indImage in range(len(self.xImageNodes)):


            sPageID = self.sPageName + '_' + self.sPageDescriptor
            
            # Extract volume attribute
            sVolumeFormat = self.oIOXml.GetValueOfNodeAttribute(self.xImageNodes[indImage], 'format')
            if not (sVolumeFormat in self.lValidVolumeFormats):
                sErrorMsg = 'Invalid data format defined for patient in XML : '
                sErrorMsg = sErrorMsg + sPageID
                self.oUtilsMsgs.DisplayError(sErrorMsg)
            
            if (sVolumeFormat == 'dicom'):
                oImageViewItem = DicomVolumeDetail(self.xImageNodes[indImage], sPageID)
            else:
                oImageViewItem = DataVolumeDetail(self.xImageNodes[indImage], sPageID)
                
            bLoadSuccess = oImageViewItem.LoadVolume()
            
                
            if bLoadSuccess and (oImageViewItem.slNode is not None):
                 
                self._loImageViews.append(oImageViewItem)
                 

         
    #-----------------------------------------------
    #         Manage Views
    #-----------------------------------------------
 
         
    def AssignNodesToView(self, oViewNode):
 
        slWidget = slicer.app.layoutManager().sliceWidget(oViewNode.sDestination)
        slWindowLogic = slWidget.sliceLogic()
        slWindowCompositeNode = slWindowLogic.GetSliceCompositeNode()
        slWidgetController = slWidget.sliceController()
        
        if self.bLinkViews == True:
            slWindowCompositeNode.LinkedControlOn()
        else:
            slWindowCompositeNode.LinkedControlOff()
        
        
        if oViewNode.sViewLayer == 'Background':
            slWindowCompositeNode.SetBackgroundVolumeID(slicer.util.getNode(oViewNode.sNodeName).GetID())
            slWidget.setSliceOrientation(oViewNode.sOrientation)

        elif oViewNode.sViewLayer == 'Foreground':
            slWindowCompositeNode.SetForegroundVolumeID(slicer.util.getNode(oViewNode.sNodeName).GetID())
            slWidget.setSliceOrientation(oViewNode.sOrientation)
            slWidgetController.setForegroundOpacity(0.5)

        elif oViewNode.sViewLayer == 'Label':
            slWindowCompositeNode.SetLabelVolumeID(slicer.util.getNode(oViewNode.sNodeName).GetID())

        elif oViewNode.sViewLayer == 'Segmentation':
            if not (oViewNode.sRoiVisibilityCode == 'Empty'):
                self.SetSegmentRoiVisibility(oViewNode)
        

    #-----------------------------------------------
    
    def AssignViewToNone(self, sScreenColor):
        
        slWidget = slicer.app.layoutManager().sliceWidget(sScreenColor)
        slLogic = slWidget.sliceLogic()
        slCompNode = slLogic.GetSliceCompositeNode()
        slCompNode.SetBackgroundVolumeID('None')
        slCompNode.SetForegroundVolumeID('None')
        slCompNode.SetLabelVolumeID('None')
        

    #-----------------------------------------------
    
    def ClearImagesAndSegmentations(self):

        # clear the images displayed
        
        self.AssignViewToNone('Red')
        self.AssignViewToNone('Yellow')
        self.AssignViewToNone('Green')
        
        
        # get list of all segmentation nodes and turn off the visibility
       
        lSegNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLSegmentationNode')
         
        for indSeg in range(lSegNodes.GetNumberOfItems()):

            slSegNode = lSegNodes.GetItemAsObject(indSeg)
            slSegDisplayNode = slSegNode.GetDisplayNode()
            
            slSegDisplayNode.SetVisibility(False)
            
        # unregister the nodes created by 'GetNodeByClass'otherwise you get a memory leak
        lSegNodes.UnRegister(slicer.mrmlScene) 
    
    #-----------------------------------------------

    def SetSegmentRoiVisibility(self,oViewNode):
        # in order to set visibility, you have to traverse Slicer's subject hierarchy
        # accessing the segmentation node, its children (to get ROI names) and its data node
        
        
        # get Slicer's subject hierarchy node (SHNode)
        
        slSHNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        
        
        # get the item ID for the RTStruct through the RTStruct Series Instance UID
        
        slRTStructItemId = slSHNode.GetItemByUID(slicer.vtkMRMLSubjectHierarchyConstants.GetDICOMUIDName(), oViewNode.sSeriesInstanceUID)


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
        slSegDisplayNodeId = slSegDataNode.GetDisplayNodeID()
        slSegDisplayNode = slicer.mrmlScene.GetNodeByID(slSegDisplayNodeId)

        # assign segmentation display node to the requested viewing window destination
        lsViewIDs = []
        
        # get viewing window node ID (1st object of node)
        slViewingNode = slicer.mrmlScene.GetNodesByName(oViewNode.sDestination)
        oSlicerViewNodeItem = slViewingNode.GetItemAsObject(0)
        sViewID = oSlicerViewNodeItem.GetID()

        lsViewIDs.append(sViewID)
        
        # if this segmentation display node was already assigned to a viewing window,
        #    capture the previous assignment and append the new request
        tupPreviousViewAssignments = slSegDisplayNode.GetViewNodeIDs()
        lsRemainingPreviousAssignments = []
        if len(tupPreviousViewAssignments) > 0:

            # extract first element of tuple and a list with the rest of the elements 
            #    (following python syntax rules for tuples) 
            sFirstPreviousAssignment, *lsRemainingPreviousAssignments = tupPreviousViewAssignments

            # the current requested view ID (sViewID) may already be in the list of
            #    previous assignments. Don't bother appending.
            #    (This may occur when this display is coming after a 'previous' button selection)
            if not (sFirstPreviousAssignment == sViewID):
                lsViewIDs.append(sFirstPreviousAssignment)
                if len(lsRemainingPreviousAssignments) >0:
                    for indTupList in range(len(lsRemainingPreviousAssignments)):
                        if not (lsRemainingPreviousAssignments[indTupList] == sViewID):
                            lsViewIDs.append(lsRemainingPreviousAssignments[indTupList])
                
        # assign all requested view destinations to the display node
        slSegDisplayNode.SetViewNodeIDs(lsViewIDs)
        
        
        # turn on segmentation node visibility 
        #    (necessary when this display is coming after a 'previous' button selection)
        slSegDataNode.SetDisplayVisibility(True)
        
        # adjust visibility of each ROI as per user's request
        
        if (oViewNode.sRoiVisibilityCode == 'All'):
            for indSHList in range(len(lsSubjectHierarchyROINames)):
                slSegDisplayNode.SetSegmentVisibility(lsSubjectHierarchyROINames[indSHList],True)
                
        if (oViewNode.sRoiVisibilityCode == 'None'):
            for indSHList in range(len(lsSubjectHierarchyROINames)):
                slSegDisplayNode.SetSegmentVisibility(lsSubjectHierarchyROINames[indSHList],False)
            
        # turn ON all ROI's and then turn OFF user's list    
        if (oViewNode.sRoiVisibilityCode == 'Ignore'):
            for indSHList in range(len(lsSubjectHierarchyROINames)):
                slSegDisplayNode.SetSegmentVisibility(lsSubjectHierarchyROINames[indSHList],True)
            for indUserList in range(len(oViewNode.lsRoiList)):
                slSegDisplayNode.SetSegmentVisibility(oViewNode.lsRoiList[indUserList], False)

        # turn OFF all ROI's and then turn ON user's list    
        if (oViewNode.sRoiVisibilityCode == 'Select'):
            for indSHList in range(len(lsSubjectHierarchyROINames)):
                slSegDisplayNode.SetSegmentVisibility(lsSubjectHierarchyROINames[indSHList],False)
            for indUserList in range(len(oViewNode.lsRoiList)):
                slSegDisplayNode.SetSegmentVisibility(oViewNode.lsRoiList[indUserList], True)
                
        # clean up memory leaks
        #    getting a node by ID (slSegDisplayNode) doesn't seem to cause a memory leak
        #    getting nodes by class does create a memory leak so you have to unregister it!
        slViewingNode.UnRegister(slicer.mrmlScene)
    
        
    #-----------------------------------------------

#     #-----------------------------------------------

    
##########################################################################
#
#   Class ViewNodeBase
#
##########################################################################

class ViewNodeBase:

    def __init__(self,  parent=None):
        self.sClassName = type(self).__name__
        self.parent = parent
    
        self.sPageID = ''
        self.slNode = None
        self.sDestination = ''
        self.sOrientation = ''
        self.sViewLayer = ''
        self.sImageType = ''
        self.sImagePath = ''
        self.sNodeName = ''
        self._xImage = None
        self._sPageID = ''
        

    #----------
    def SetXmlImageElement(self, xInput):
        self._xImage = xInput
        
    #----------
    def GetXmlImageElement(self):
        return self._xImage
    
    #----------
    def SetPageID(self, sInput):
        self._sPageID = sInput
        
    #----------
    def GetPageID(self):
        return self._sPageID

    #-----------------------------------------------
    def GetSlicerViewNode(self):
        return self.slNode

    #-----------------------------------------------

    def ExtractImageAttributes(self):

        self.sNodeDescriptor = self.oIOXml.GetValueOfNodeAttribute(self.GetXmlImageElement(), 'descriptor')
        self.sImageType = self.oIOXml.GetValueOfNodeAttribute(self.GetXmlImageElement(), 'type')
        self.sDestination = self.oIOXml.GetValueOfNodeAttribute(self.GetXmlImageElement(), 'destination')
    
        self.sNodeName =  self.GetPageID() + '_' + self.sNodeDescriptor

    #-----------------------------------------------

    def ExtractXMLNodeElements(self):
        
        # Extract path element
        xPathNodes = self.oIOXml.GetChildren(self.GetXmlImageElement(), 'Path')
        if len(xPathNodes) > 1:
            sWarningMsg = 'There can only be one path per image.  The first defined path will be used.   '
            sWarningMsg = sWarningMsg + self.sNodeName
            self.oUtilsMsgs.DisplayWarning( sWarningMsg )

        self.sImagePath = self.oIOXml.GetDataInNode(xPathNodes[0])
        
        # Extract destination layer (foreground, background, label)
        xLayerNodes = self.oIOXml.GetChildren(self.GetXmlImageElement(), 'Layer')
        if len(xLayerNodes) > 1:
            sWarningMsg = 'There can only be one destination layer (foreground, background or label) per image. \nThe first defined destination in the XML will be used.   '
            sWarningMsg = sWarningMsg + self.sNodeName
            self.oUtilsMsgs.DisplayWarning(sWarningMsg)

        self.sViewLayer = self.oIOXml.GetDataInNode(xLayerNodes[0])
    
        if (self.sImageType == 'Volume'):
            # Only image volumes have an orientation, 
            # segmentation layer (RTStruct) follows the orientation of the display node
             
            # Extract orientation (axial, sagittal, coronal)
            xOrientationNodes = self.oIOXml.GetChildren(self.GetXmlImageElement(), 'Orientation')
            if len(xOrientationNodes) > 1:
                sWarningMsg = 'There can only be one orientation (axial, sagittal, coronal) per image. \nThe first defined orientation in the XML will be used.   '
                sWarningMsg = sWarningMsg + self.sNodeName
                self.oUtilsMsgs.DisplayWarning(sWarningMsg)
    
            self.sOrientation = self.oIOXml.GetDataInNode(xOrientationNodes[0])
            
            

    #-----------------------------------------------

    def CheckForNodeExists(self, sNodeClass):
        # If a node already exists in the mrmlScene, it should not be loaded again
        # This function checks to see if it has already been loaded
        
        # initialize
        bNodeExists = False
        self.slNode = None
        
        # check for nodes by name and check if it's the proper class
        try:
            self.slNode = slicer.mrmlScene.GetFirstNodeByName(self.sNodeName)
            if (self.slNode.GetClassName() == sNodeClass) :
                bNodeExists = True
        except:
            bNodeExists = False
        
        return bNodeExists


    #-----------------------------------------------

    def GetViewState(self):
        
        # given the view node, window and level
        slDisplayNode = self.slNode.GetDisplayNode()
        fLevel = slDisplayNode.GetLevel()
        fWindow = slDisplayNode.GetWindow()

        # get the slice offset position for the current widget in the layout manager
        slWidget = slicer.app.layoutManager().sliceWidget(self.sDestination)
        slWindowLogic = slWidget.sliceLogic()
        
        fSliceOffset = slWindowLogic.GetSliceOffset()
        
        dictAttrib = { 'window': str(fWindow), 'level':  str(fLevel),\
                      'sliceoffset': str(fSliceOffset)}
        
        return dictAttrib

    #-----------------------------------------------

    def SetImageState(self, dictImageState):
        
        
        slViewNode = self.GetSlicerViewNode()
        slDisplayNode = slViewNode.GetDisplayNode()
        slDisplayNode.AutoWindowLevelOn() # default - if no saved state
            
        if len(dictImageState) > 0:

            if 'level' in dictImageState.keys() and 'window' in dictImageState.keys():
                fLevel = float(dictImageState['level'])
                fWindow = float(dictImageState['window'])
            
                # get display node for slicer image element
                slDisplayNode.AutoWindowLevelOff()
                slDisplayNode.SetLevel(fLevel)
                slDisplayNode.SetWindow(fWindow)

            if 'sliceoffset' in dictImageState.keys():
                # set the slice offset position for the current widget
                slWidget = slicer.app.layoutManager().sliceWidget(self.sDestination)
                slWindowLogic = slWidget.sliceLogic()
                
                fSliceOffset = float(dictImageState['sliceoffset'])
                
                slWindowLogic.SetSliceOffset(fSliceOffset)
        
    #-----------------------------------------------
    
##########################################################################
#
#   Class DataVolumeDetail
#
##########################################################################

class DataVolumeDetail(ViewNodeBase):
    
    
    def __init__(self, xImage, sPageID):
        self.sClassName = type(self).__name__
        self.oIOXml = UtilsIOXml()
        self.oUtilsMsgs = UtilsMsgs()


        #--------------------
        
        # functions from base class
        self.SetXmlImageElement(xImage)
        self.SetPageID(sPageID)
        self.ExtractImageAttributes()
        self.ExtractXMLNodeElements()
        

    #-----------------------------------------------

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
                self.oUtilsMsgs.DisplayError(sErrorMsg)
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
    
    
    def __init__(self, xImage, sPageID):
        self.sClassName = type(self).__name__
        self.oIOXml = UtilsIOXml()
        self.oUtilsMsgs = UtilsMsgs()
        
        self.sRoiVisibilityCode = 'Empty'
        self.sVolumeReferenceSeriesUID = ''
        self.sSeriesInstanceUID = ''
        self.sStudyInstanceUID = ''
        self.lsRoiList = []
        

        #--------------------
        
        # functions from base class
        self.SetXmlImageElement(xImage)
        self.SetPageID(sPageID)
        self.ExtractImageAttributes()
        self.ExtractXMLNodeElements()
        
        # specifics for Dicom volumes
        self.ExtractXMLDicomElements()
        
    #-----------------------------------------------
        
    def ExtractXMLDicomElements(self):

        # extract extra Dicom XML elements
        
        
        # extract Series Instance UID nodes
        xSeriesUIDNodes = self.oIOXml.GetChildren(self.GetXmlImageElement(), 'SeriesInstanceUID')
        if len(xSeriesUIDNodes) > 1:
            sWarningMsg = 'There can only be one SeriesInstanceUID element per Dicom element. \nThe first defined SeriesInstanceUID in the XML will be used.   '
            sWarningMsg = sWarningMsg + self.sNodeName
            self.oUtilsMsgs.DisplayWarning(sWarningMsg)
        self.sSeriesInstanceUID = self.oIOXml.GetDataInNode(xSeriesUIDNodes[0])
        
        
        if (self.sImageType == 'RTStruct'):


            # extract Reference Volume Series UID nodes
            xRefSeriesUIDNodes = self.oIOXml.GetChildren(self.GetXmlImageElement(), 'RefSeriesInstanceUID')
            if len(xRefSeriesUIDNodes) > 1:
                sWarningMsg = 'There can only be one Volume Reference SeriesInstanceUID element per image. \nThe first defined Series UID in the XML will be used.   '
                sWarningMsg = sWarningMsg + self.sNodeName
                self.oUtilsMsgs.DisplayWarning(sWarningMsg)
            self.sVolumeReferenceSeriesUID = self.oIOXml.GetDataInNode(xRefSeriesUIDNodes[0])

            
            self.ReadXMLRoiElements()
            
            
    #-----------------------------------------------
        
    def LoadVolume(self):
        bLoadSuccess = self.LoadDicomVolume()
#         if not (self.sRoiVisibilityCode == 'Empty'):
#             self.SetSegmentRoiVisibility()
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
            tags['studyUID'] = "0020,000D"
            
            # using the path defined by the user to one of the files in the series,
            # access dicom information stored in that series
            
            sSeriesUIDToLoad = database.fileValue(self.sImagePath, tags['seriesUID'])
            sPatientName = database.fileValue(self.sImagePath , tags['patientName'])
            sPatientID = database.fileValue(self.sImagePath , tags['patientID'])

            self.sStudyInstanceUID = database.fileValue(self.sImagePath, tags['studyUID'])
            sExpectedSubjectHierarchyName = sPatientName + ' (' + sPatientID + ')'
#             print(' ~~~ Subject Hierarchy expected name : %s' % sExpectedSubjectHierarchyName)

            
            # extract directory that stores the dicom series from defined image path
            sHead_Tail = os.path.split(self.sImagePath)
            sDicomSeriesDir = sHead_Tail[0]
            
            # check if already loaded into the database
            for sImportedSeries in lAllSeriesUIDs:
                if sImportedSeries == sSeriesUIDToLoad:
                    bSeriesFoundInDB = True
                
            # if not already loaded, import from series directory 
            #  NOTE: if more than one series is located in this directory, 
            #        all series will be imported
            if not bSeriesFoundInDB:
                DICOMUtils.importDicom(sDicomSeriesDir)


            # check subject hierarchy to see if volume already exists (loaded)
            bVolumeAlreadyLoaded = False
            
            
            slSubjectHierarchyNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
            slNodeId = slSubjectHierarchyNode.GetItemByUID(slicer.vtkMRMLSubjectHierarchyConstants.GetDICOMUIDName(),sSeriesUIDToLoad)
            if slNodeId > 0:
                bVolumeAlreadyLoaded = True
            else:
                DICOMUtils.loadSeriesByUID([sSeriesUIDToLoad])
                slNodeId = slSubjectHierarchyNode.GetItemByUID(slicer.vtkMRMLSubjectHierarchyConstants.GetDICOMUIDName(),sSeriesUIDToLoad)
            

            # update the class properties with the slicer node and node name 
            self.slNode = slSubjectHierarchyNode.GetItemDataNode(slNodeId)
            self.sNodeName = self.slNode.GetName()
            
                        
            bLoadSuccess = True
        
        else:
            sErrorMsg = ('Slicer Database is not open')
            self.oUtilsMsgs.DisplayError(sErrorMsg)

        

        return bLoadSuccess

        
    #-----------------------------------------------

    def ReadXMLRoiElements(self):
        # if the Image type is RTStuct, XML holds a visibility code and (if applicable)
        # a list of ROI names
        # The visibility code is as follows: 
        #    'All' : turn on visibility of all ROIs in RTStruct
        #    'None': turn off visibility of all ROIs in RTStruct
        #    'Ignore' : turn on all ROIs except the ones listed
        #    'Select' : turn on visibility of only ROIs listed
        
        # get XML ROIs element
        xRoisNode = self.oIOXml.GetChildren(self.GetXmlImageElement(), 'ROIs')
        
        # get visibility code from the attribute
        self.sRoiVisibilityCode = self.oIOXml.GetValueOfNodeAttribute(xRoisNode[0], 'roiVisibilityCode')

        if (self.sRoiVisibilityCode == 'Select' or self.sRoiVisibilityCode == 'Ignore'):
            
            # get list of ROI children
            xRoiChildren = self.oIOXml.GetChildren(xRoisNode[0], 'ROI')

            for indRoi in range(len(xRoiChildren)):
                sRoiName = self.oIOXml.GetDataInNode(xRoiChildren[indRoi])
                self.lsRoiList.append(sRoiName)
                
        

    

    #-----------------------------------------------

    def CheckForLabelMapNodeExists(self, sROIName):
        
        bNodeExists = False
        
        # get Slicer's subject hierarchy node (SHNode)
        
        slSHNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        
        
        # get the item ID for the Patient through the Study Series Instance UID
        
        slStudyItemID = slSHNode.GetItemByUID(slicer.vtkMRMLSubjectHierarchyConstants.GetDICOMUIDName(), self.sStudyInstanceUID)


        # using slicers vtk Item Id for the Volume, get the ROI names (children)
        
        slStudyChildren = vtk.vtkIdList()    # initialize to ItemId type
        slSHNode.GetItemChildren(slStudyItemID, slStudyChildren) # populate children variable
        
        for indChild in range(slStudyChildren.GetNumberOfIds()):
            # get id
            slChildId = slStudyChildren.GetId(indChild)
            # get datanode
            slChildDataNode = slSHNode.GetItemDataNode(slChildId)
            
            #check if class name matches
            if (slChildDataNode.GetClassName() == 'vtkMRMLLabelMapVolumeNode'):
                # check if name matches
                if (slChildDataNode.GetName() == sROIName):
                    bNodeExists = True
                    
        
        return bNodeExists
        

##########################################################################
#
#   Class SubjectHierarchyDetail
#
##########################################################################

class SubjectHierarchyDetail:
    
    def __init__(self,  parent=None):
        
        self.slSHNode = None
        self.slSegDisplayNode = None
        self.slSegDataNode = None
        
        self.slStudyItemId = ''
        self.slRTStructItemId = ''
        self.slSegDisplayNodeId = ''

        
        self.slRTStructChildren = None
        self.slStudyChildren = None
        
        self.lsSubjectHierarchyROINames = []
        
    
    #-----------------------------------------------

    def TraverseSubjectHierarchy(self, sStudyInstanceUID, sSeriesInstanceUID):
        
        # get Slicer's subject hierarchy node (SHNode)
        
        self.slSHNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        
        
        # get the item ID for the Patient study through the Study Series Instance UID
        
        self.slStudyItemID = self.slSHNode.GetItemByUID(slicer.vtkMRMLSubjectHierarchyConstants.GetDICOMUIDName(), sStudyInstanceUID)


        # using slicers vtk Item Id for the Volume, get the ROI names (children)
        
        self.slStudyChildren = vtk.vtkIdList()    # initialize to ItemId type
        self.slSHNode.GetItemChildren(self.slStudyItemID, self.slStudyChildren) # populate children variable

        # get the item ID for the RTStruct through the RTStruct Series Instance UID
        
        self.slRTStructItemId = self.slSHNode.GetItemByUID(slicer.vtkMRMLSubjectHierarchyConstants.GetDICOMUIDName(), sSeriesInstanceUID)


        # using slicers vtk Item Id for the RTStruct, get the ROI names (children)
        
        self.slRTStructChildren = vtk.vtkIdList()    # initialize to ItemId type
        self.slSHNode.GetItemChildren(self.slRTStructItemId, self.slRTStructChildren) # populate children variable
        
        
        # get ROI child Item ID and store the child (ROI) name
        
        self.lsSubjectHierarchyROINames = []
        for indROI in range(self.slRTStructChildren.GetNumberOfIds()):
            slROIItemId = self.slRTStructChildren.GetId(indROI)
            sROIName = self.slSHNode.GetItemName(slROIItemId)
            self.lsSubjectHierarchyROINames.append(sROIName)
        
        
        # get segmentation node name from data node
        
        self.slSegDataNode = self.slSHNode.GetItemDataNode(self.slRTStructItemId)
        self.slSegDisplayNodeId = self.slSegDataNode.GetDisplayNodeID()
        self.slSegDisplayNode = slicer.mrmlScene.GetNodeByID(self.slSegDisplayNodeId)

