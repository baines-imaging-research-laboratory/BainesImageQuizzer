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

import pydicom
import time

##########################################################################
#
#   Class ImageView
#
##########################################################################

class ImageView:
    
    def __init__(self,  parent=None):
        self.sClassName = type(self).__name__
        self.parent = parent
        self.sPageID = ''
        self.sPageDescriptor = ''
        
#         self.lValidVolumeFormats = ['NRRD', 'NIFTI', 'MHD', 'DICOM']
#         self.lValidSliceWidgets = ['Red', 'Green', 'Yellow', 'Slice4'] # for two over two layout
        self._loImageViews = []
        self.bLinkViews = False
        
        self.sParentDataDir = ''
        
        
    #----------
    def GetImageViewList(self):
        return self._loImageViews


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def RunSetup(self, xPageNode, quizLayout, sParentDataDir):

        self.quizLayout = quizLayout
        self.oIOXml = UtilsIOXml()
        self.oUtilsMsgs = UtilsMsgs()
        self.sParentDataDir = sParentDataDir


        # get ID and descriptor
        self.sPageID = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'ID')
        self.sPageDescriptor = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'Descriptor')
        
        # assign link views
        if (self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'LinkViews') == 'Y'):
            self.bLinkViews = True
        else:
            self.bLinkViews = False

        # display Images
        self.xImageNodes = self.oIOXml.GetChildren(xPageNode, 'Image')
#         self.iNumImages = self.oIOXml.GetNumChildrenByName(xPageNode, 'Image')
       
        self.BuildViewNodes()
        
        # After segmenting creates a new label map volume, visibility is left on
        # Turn off the visibility in the Subject Hierarchy when starting a new ImageView object
        self.SetLabelMapVisibility(0)
        
                
        # reset field of view to maximize background
        slicer.util.resetSliceViews()
                
                
            

    #-----------------------------------------------
    #         Manage Data Loading
    #-----------------------------------------------

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def BuildViewNodes(self):
        
        bLoadSuccess = False
        
        # progress bar set up for long image loads 
        # initialize to 1% to get the bar to display, then reset to the proper maximum
        progressBar = slicer.util.createProgressDialog( windowTitle="Working", autoClose=True)
        progressBar.labelText = 'Loading images'
        progressBar.setMaximum(100)
        progressBar.setValue(1) 
        slicer.app.processEvents() # force display
        if len(self.xImageNodes) == 0:
            progressBar.close()
            
        else:
            progressBar.setMaximum(len(self.xImageNodes)) # reset for this build
        
        # for each image
        for indImage in range(len(self.xImageNodes)):

            
#             sPageID = self.sPageName + '_' + self.sPageDescriptor
            
            # Extract the type of volume to be displayed 
            #     if not a DICOM - assume it is a 'Data' volume
            sDICOMRead = self.oIOXml.GetValueOfNodeAttribute(self.xImageNodes[indImage], 'DicomRead')
            
#             if not (sVolumeFormat in self.lValidVolumeFormats):
#                 sErrorMsg = 'Invalid data format defined for patient in XML : '
#                 sErrorMsg = sErrorMsg + sPageID
#                 self.oUtilsMsgs.DisplayError(sErrorMsg)
            
            if (sDICOMRead == 'Y'):
                oImageViewItem = DicomVolumeDetail(self.xImageNodes[indImage], self.sPageID, self.sParentDataDir)
            
            else:
                oImageViewItem = DataVolumeDetail(self.xImageNodes[indImage], self.sPageID, self.sParentDataDir)
                    
                
            bLoadSuccess = oImageViewItem.LoadVolume()
            
                
            if bLoadSuccess and (oImageViewItem.slNode is not None):
                
                if oImageViewItem.sImageType != 'Segmentation': 
                    oImageViewItem.slNode.SetName(oImageViewItem.sNodeName)
                    self._loImageViews.append(oImageViewItem)
                
            else:
                sMsg = 'Image load Failed : ' + self.sPageID + ':' + oImageViewItem.sImagePath
                self.oUtilsMsgs.DisplayWarning(sMsg)
                 
            progressBar.setValue(indImage + 1)
            slicer.app.processEvents()
        
        # all images loaded
        progressBar.close()

         
    #-----------------------------------------------
    #         Manage Views
    #-----------------------------------------------
 

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AssignNodesToView(self):
        ''' For each image node in the list, assign it to the destination widget (from list of valid widgets)
            If the background image has a corresponding label map created by the user in the quiz,
                assign the widget's label map setting otherwise set it to None.
            Foreground and Background images will have the color table applied (default Grey)
            If the image node in the quiz xml has the viewing layer set to  'Label'  (ie it was loaded in directly from the XML),
                it will only get assigned if there were no quiz label maps created and assigned to that widget.
                (User created label maps segmented as part of the quiz take priority). 
        '''
 
        # initialize all layers to None
        # make sure the widget exists in case the default layout changes
        for sWidgetName in self.oIOXml.lValidSliceWidgets:
            slWidget = slicer.app.layoutManager().sliceWidget(sWidgetName)
            if slWidget != None:
                slWindowLogic = slWidget.sliceLogic()
                slWindowCompositeNode = slWindowLogic.GetSliceCompositeNode()
                slWindowCompositeNode.SetBackgroundVolumeID('None')
                slWindowCompositeNode.SetForegroundVolumeID('None')
                slWindowCompositeNode.SetLabelVolumeID('None')


        for oViewNode in self._loImageViews:

            # if image type is an RTStruct, ensure that the referenced volume 
            #    SeriesInstanceUID exists in the list of images to be loaded
            if oViewNode.sImageType == 'RTStruct':
                bFoundReferencedVolume = False
                for oImage in self._loImageViews:
                    if oViewNode.sVolumeReferenceSeriesUID == oImage.sSeriesInstanceUID:
                        bFoundReferencedVolume = True
                        break
                if bFoundReferencedVolume == False:
                    sErrorMsg = 'Invalid RTStruct - Referenced Volume SeriesInstanceUID ' \
                                'does not match any of the image volumes being loaded \n' \
                                + oViewNode.sImagePath
                    
                    self.oUtilsMsgs.DisplayError(sErrorMsg)         
            
            
            # get slicer control objects for the widget
            slWidget = slicer.app.layoutManager().sliceWidget(oViewNode.sDestination)
            slWindowLogic = slWidget.sliceLogic()
            slWindowCompositeNode = slWindowLogic.GetSliceCompositeNode()
            slWidgetController = slWidget.sliceController()
            
            # turn off link control until all images have been assigned to their destinations
            slWindowCompositeNode.LinkedControlOff()

            #setup for color tables if defined in the xml attributes for foreground and background images
            if oViewNode.sColorTableName == '':
                oViewNode.sColorTableName = 'Grey' # default
            
            
            if oViewNode.sViewLayer == 'Background':
                slWindowCompositeNode.SetBackgroundVolumeID(slicer.util.getNode(oViewNode.sNodeName).GetID())

                # after defining the inital desired orientation, 
                #    if the rotatetoacquisition attribute was set,
                #    rotate the image to the volume plane
                slWidget.setSliceOrientation(oViewNode.sOrientation)
                if oViewNode.bRotateToAcquisition == True:
                    slVolumeNode = slWindowLogic.GetBackgroundLayer().GetVolumeNode()
                    slWidget.mrmlSliceNode().RotateToVolumePlane(slVolumeNode)
                    self.RotateSliceToImage(oViewNode.sDestination)

                slWidget.fitSliceToBackground()
                oViewNode.AssignColorTable()

                # turn on label map volume if a label map was loaded for the background image                
                if oViewNode.slQuizLabelMapNode != None:
                    slWindowCompositeNode.SetLabelVolumeID(oViewNode.slQuizLabelMapNode.GetID())
                else:
                    # there is no quiz label map node associated with the background,
                    #    but there may have been one in the foreground;
                    #    if so, leave it turned on
                    if slWindowCompositeNode.GetLabelVolumeID ()== None:
                        slWindowCompositeNode.SetLabelVolumeID('None')

    
            elif oViewNode.sViewLayer == 'Foreground':
                slWindowCompositeNode.SetForegroundVolumeID(slicer.util.getNode(oViewNode.sNodeName).GetID())
                slWidget.setSliceOrientation(oViewNode.sOrientation)
                slWidgetController.setForegroundOpacity(0.5)
                if oViewNode.bRotateToAcquisition == True:
                    self.RotateSliceToImage(oViewNode.sDestination)

                oViewNode.AssignColorTable()

                # turn on label map volume if a label map was loaded for the background image                
                if oViewNode.slQuizLabelMapNode != None:
                    slWindowCompositeNode.SetLabelVolumeID(oViewNode.slQuizLabelMapNode.GetID())
                else:
                    # there is no quiz label map node associated with the foreground,
                    #    but there may have been one in the background;
                    #    if so, leave it turned on
                    if slWindowCompositeNode.GetLabelVolumeID ()== None:
                        slWindowCompositeNode.SetLabelVolumeID('None')

    
            elif oViewNode.sViewLayer == 'Label':
                if slWindowCompositeNode.GetLabelVolumeID() == 'None':
                    slWindowCompositeNode.SetLabelVolumeID(slicer.util.getNode(oViewNode.sNodeName).GetID())
#                 print('after set Label Volume ID',slWidget.sliceOrientation)
    

            elif oViewNode.sViewLayer == 'Segmentation':
                if not (oViewNode.sRoiVisibilityCode == 'Empty'):
                    self.SetSegmentRoiVisibility(oViewNode)
#                 print('after set Segmentation Volume ID',slWidget.sliceOrientation)

            # after all images and their label maps have been assigned, adjust the link control
            if self.bLinkViews == True:
                slWindowCompositeNode.LinkedControlOn()
            else:
                slWindowCompositeNode.LinkedControlOff()

          
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def RotateSliceToImage(self, sViewDestination):
        # for each viewing window,        
        #    adjust slice node to align with the native space of the image data
        #     from EditorLib/LabelEffect.py
              
        slWidget = slicer.app.layoutManager().sliceWidget(sViewDestination)
        slWindowLogic = slWidget.sliceLogic()
          
        slSliceNode = slWidget.mrmlSliceNode()
        slVolumeNode = slWindowLogic.GetBackgroundLayer().GetVolumeNode()
        slSliceNode.RotateToVolumePlane(slVolumeNode)
        # make sure the slice plane does not lie on an index boundary
        # - (to avoid rounding issues)
        slWindowLogic.SnapSliceOffsetToIJK()
        slSliceNode.UpdateMatrices()

    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
    
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetLabelMapVisibility(self, iOnOff):
        
        # Set the label map volume visibility: on = 1; off = 0

        # get list of all label map nodes
        
        lLabelMapNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLLabelMapVolumeNode')
        
        for indLabelMap in range(lLabelMapNodes.GetNumberOfItems()):
            
            slLabelMapNode = lLabelMapNodes.GetItemAsObject(indLabelMap)
            slLabelMapNodeName = slLabelMapNode.GetName()
            
            # we need the subject hierarchy node id 
            slSHNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
            slSceneItemID = slSHNode.GetSceneItemID()
            iLabelMapSubjectHierarchyId = slSHNode.GetItemChildWithName(slSceneItemID, slLabelMapNodeName)
            
            # using the slicer plugin, set the visibility
            slLabelMapPlugin = slicer.qSlicerSubjectHierarchyLabelMapsPlugin()
            slLabelMapPlugin.setDisplayVisibility(iLabelMapSubjectHierarchyId, iOnOff)

        # clean up memory leaks
        #    getting a node by ID (slSegDisplayNode) doesn't seem to cause a memory leak
        #    getting nodes by class does create a memory leak so you have to unregister it!
        lLabelMapNodes.UnRegister(slicer.mrmlScene)
    
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
#         self.sFormat=''
        self._xImageElement = None
#         self._sPageID = ''
        self.sColorTableName = ''
        self.bRotateToAcquisition = False
        
        self.slQuizLabelMapNode = None
        

    #----------
    def SetXmlImageElement(self, xInput):
        self._xImageElement = xInput
        
    #----------
    def GetXmlImageElement(self):
        return self._xImageElement
    
    #----------
    def SetPageID(self, sInput):
        self.sPageID = sInput
         
    #----------
    def GetPageID(self):
        return self.sPageID

    #----------
    def GetSlicerViewNode(self):
        return self.slNode

    #----------
    def SetQuizLabelMapNode(self, slNodeInput):
        self.slQuizLabelMapNode = slNodeInput

    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ExtractImageAttributes(self):

        sImageID = self.oIOXml.GetValueOfNodeAttribute(self.GetXmlImageElement(), 'ID')
        self.sImageType = self.oIOXml.GetValueOfNodeAttribute(self.GetXmlImageElement(), 'Type')
#         self.sVolumeFormat = self.oIOXml.GetValueOfNodeAttribute(self.GetXmlImageElement(), 'Format')

        self.sColorTableName = self.oIOXml.GetValueOfNodeAttribute(self.GetXmlImageElement(), 'ColorTable')

        sRotateToAcquisition = self.oIOXml.GetValueOfNodeAttribute(self.GetXmlImageElement(), 'RotateToAcquisition')
        if sRotateToAcquisition == 'Y':
            self.bRotateToAcquisition = True
        else:
            self.bRotateToAcquisition = False
    
        self.sNodeName =  self.GetPageID() + '_' + sImageID

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ExtractXMLNodeElements(self, sParentDataDir):
        
        sWarningMsg = ''
        

        # Extract Destination (Red, Green, Yellow, Slice4)
        xDestinationNodes = self.oIOXml.GetChildren(self.GetXmlImageElement(), 'Destination')
        if len(xDestinationNodes) == 0:
            self.sDestination = 'Red'
            sWarningMsg = sWarningMsg + '\n' + 'Missing XML element: Destination . The default "Red" viewing window will be used.   '
        else:
            self.sDestination = self.oIOXml.GetDataInNode(xDestinationNodes[0])
            
            if len(xDestinationNodes) > 1:
                sWarningMsg = sWarningMsg + '\n' + 'There can only be one viewing destination (Red, Green, Yellow, or Slice4) per image. The first defined destination in the XML will be used.   '


        # Extract viewing layer (foreground, background, label)
        xLayerNodes = self.oIOXml.GetChildren(self.GetXmlImageElement(), 'Layer')
        if len(xLayerNodes) == 0: # default
            self.sViewLayer = 'Background'
            sWarningMsg = sWarningMsg + '\n' + 'Missing XML element: Layer. The default "Background" will be used.   '
        else:
            self.sViewLayer = self.oIOXml.GetDataInNode(xLayerNodes[0])

            if len(xLayerNodes) > 1:
                sWarningMsg = sWarningMsg + '\n' + 'There can only be one viewing layer (foreground, background or label) per image. The first defined layer in the XML will be used.   '
    

        # Extract orientation (axial, sagittal, coronal)
        if (self.sImageType == 'Volume' or self.sImageType == 'VolumeSequence'):
            # Only image volumes have an orientation, 
            # segmentation layer (RTStruct) follows the orientation of the display node
             
            xOrientationNodes = self.oIOXml.GetChildren(self.GetXmlImageElement(), 'Orientation')
            if len(xOrientationNodes) == 0:
                self.sOrientation = 'Axial'
                sWarningMsg = sWarningMsg + '\n' + 'Missing XML element: Orientation . The default "Axial" will be used.   '
                
            else:
                self.sOrientation = self.oIOXml.GetDataInNode(xOrientationNodes[0])

                if len(xOrientationNodes) > 1:
                    sWarningMsg = sWarningMsg + '\n' + 'There can only be one orientation (axial, sagittal, coronal) per image. \nThe first defined orientation in the XML will be used.   '
            
        # Extract path element
        xPathNodes = self.oIOXml.GetChildren(self.GetXmlImageElement(), 'Path')

        if len(xPathNodes) == 0:
            sWarningMsg = sWarningMsg + '\n' + 'Missing XML element: Path . No image will be displayed.'
            self.sImagePath = ''
        else:
            self.sImagePath = os.path.join(sParentDataDir, self.oIOXml.GetDataInNode(xPathNodes[0]))
            
            if len(xPathNodes) > 1:
                sWarningMsg = sWarningMsg + '\n' + 'There can only be one path per image.  The first defined path will be used.   '

#         sFilename_w_ext = os.path.basename(self.sImagePath)
#         sFilename, sFileExt = os.path.splitext(sFilename_w_ext)
        

        # display warnings
        if sWarningMsg != '':
            sWarningMsg = sWarningMsg + '\n' +  self.sNodeName
            self.oUtilsMsgs.DisplayWarning( sWarningMsg )
            

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetViewState(self):
        
        # given the view node, window and level
        
        # access the display node
        slDisplayNode = self.slNode.GetDisplayNode()
                
        dictAttrib = {}
        
        if not slDisplayNode == None:
            fLevel = slDisplayNode.GetLevel()
            fWindow = slDisplayNode.GetWindow()
    
            # get the slice offset position for the current widget in the layout manager
            slWidget = slicer.app.layoutManager().sliceWidget(self.sDestination)
            slWindowLogic = slWidget.sliceLogic()
            
            fSliceOffset = slWindowLogic.GetSliceOffset()
            
            dictAttrib = { 'Window': str(fWindow), 'Level':  str(fLevel),\
                          'SliceOffset': str(fSliceOffset)}
        
        return dictAttrib

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AssignColorTable(self):
        
        # assign defined color table map to the node
        
        # get the list of color table nodes for the requested map
        slColorTableNodeList = slicer.mrmlScene.GetNodesByName(self.sColorTableName)
        
        # get the ID of the first node in the list of color table nodes
        if slColorTableNodeList.GetNumberOfItems() >= 1:
            slColorTableNode = slColorTableNodeList.GetItemAsObject(0)
            slColorTableNodeID = slColorTableNode.GetID()
          
            # assign the color table node ID to the volume's display node
            slDisplayNode = self.slNode.GetDisplayNode()
            slDisplayNode.SetAndObserveColorNodeID(slColorTableNodeID)
            
        # for memory leaks
        slColorTableNodeList.UnRegister(slicer.mrmlScene)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetImageState(self, dictImageState):
        
        
        slViewNode = self.GetSlicerViewNode()
        slDisplayNode = slViewNode.GetDisplayNode()
        slDisplayNode.AutoWindowLevelOn() # default - if no saved state
            
        if len(dictImageState) > 0:

            if 'Level' in dictImageState.keys() and 'Window' in dictImageState.keys():
                fLevel = float(dictImageState['Level'])
                fWindow = float(dictImageState['Window'])
            
                # get display node for slicer image element
                slDisplayNode.AutoWindowLevelOff()
                slDisplayNode.SetLevel(fLevel)
                slDisplayNode.SetWindow(fWindow)

            if 'SliceOffset' in dictImageState.keys():
                # set the slice offset position for the current widget
                slWidget = slicer.app.layoutManager().sliceWidget(self.sDestination)
                slWindowLogic = slWidget.sliceLogic()
                
                fSliceOffset = float(dictImageState['SliceOffset'])
                
                slWindowLogic.SetSliceOffset(fSliceOffset)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
##########################################################################
#
#   Class DataVolumeDetail
#
##########################################################################

class DataVolumeDetail(ViewNodeBase):
    
    
    def __init__(self, xImage, sPageID, sParentDataDir, slLabelMapNode=None):
        self.sClassName = type(self).__name__
        self.oIOXml = UtilsIOXml()
        self.oUtilsMsgs = UtilsMsgs()


        #--------------------
        
        # functions from base class
        self.SetXmlImageElement(xImage)
        self.SetPageID(sPageID)
        self.ExtractImageAttributes()
        self.ExtractXMLNodeElements(sParentDataDir)
        self.SetQuizLabelMapNode(slLabelMapNode)
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def LoadVolume(self):
        bLoadSuccess = self.LoadDataVolume()
        return bLoadSuccess
            


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
                    self.slNode = slicer.util.loadVolume(self.sImagePath, {'show': False, 'name': self.sNodeName, 'singleFile': True} )
                else: # make sure a node exists after load
                    if bNodeExists and (self.slNode is None):
                        bLoadSuccess = False
            
            elif (self.sImageType == 'Segmentation'):
                
                bNodeExists = self.CheckForNodeExists('vtkMRMLSegmentationNode')
                if not (bNodeExists):
                    self.slNode = slicer.util.loadSegmentation(self.sImagePath, {'show': False, 'name': self.sNodeName})
                else: # make sure a node exists after load
                    if bNodeExists and (self.slNode is None):
                        bLoadSuccess = False
            
            elif (self.sImageType == 'LabelMap'):
                
                bNodeExists = self.CheckForNodeExists( 'vtkMRMLLabelMapVolumeNode')
                dictProperties = {'labelmap' : True, 'show': False, 'name': self.sNodeName}
                if not (bNodeExists):
                    self.slNode = slicer.util.loadLabelVolume(self.sImagePath, dictProperties)
                else: # make sure a node exists after load
                    if bNodeExists and (self.slNode is None):
                        bLoadSuccess = False

            elif (self.sImageType == 'VolumeSequence'):
                
                bNodeExists = self.CheckForNodeExists( 'vtkMRMLScalarVolumeNode')
                if not (bNodeExists):
                    # slicer loads the multi volume file as a sequence node
                    # from the sequence node, slicer creates a ScalarVolumeNode in the subject hierarchy
                    # access the data node through the subject hierarchy
                    slSeqNode = slicer.util.loadNodeFromFile(self.sImagePath,'SequenceFile')
#                     self.slNode = slSeqNode.GetDataNodeAtValue('0')
                    slSHNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
                    slSHItemID = slSHNode.GetItemChildWithName(slSHNode.GetSceneItemID(), slSeqNode.GetName())
                    self.slNode = slSHNode.GetItemDataNode(slSHItemID)                

                
                
                else: # make sure a node exists after load
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
    
    
    def __init__(self, xImage, sPageID, sParentDataDir, slLabelMapNode=None):
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
        self.ExtractXMLNodeElements(sParentDataDir)
        self.SetQuizLabelMapNode(slLabelMapNode)
        
        # specifics for Dicom volumes
#         self.ExtractXMLDicomElements()
        
        self.ExtractSeriesInstanceUIDs()

        # get list of ROIs to be displayed
        if self.sImageType == 'RTStruct':
            self.ReadXMLRoiElements()
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ExtractSeriesInstanceUIDs(self):
        ''' Using pydicom, extract the SeriesInstanceUID from the given dcm file
            If this is an RTStruct, extract the referenced volume SeriesInstanceUID 
            that the contours are associated.
        '''
        
        if os.path.isfile(self.sImagePath):
            try:
                dcmDataset = pydicom.dcmread(self.sImagePath)
                self.sSeriesInstanceUID = dcmDataset.SeriesInstanceUID
                
                # access the referenced volume series instance UID that the contours are associated with
                if self.sImageType == 'RTStruct':
                    dcmReferencedFrameOfRefenceSequence = dcmDataset.ReferencedFrameOfReferenceSequence[0]
                    dcmRTReferencedStudySequence = dcmReferencedFrameOfRefenceSequence.RTReferencedStudySequence[0]
                    dcmRTReferencedSeriesSequence = dcmRTReferencedStudySequence.RTReferencedSeriesSequence[0]
                    
                    self.sVolumeReferenceSeriesUID = dcmRTReferencedSeriesSequence.SeriesInstanceUID
            except:
                sMsg = 'Cannot read SeriesInstanceUID from DICOM using pydicom.' \
                        + '\n See administrator : ' + sys._getframe(  ).f_code.co_name
                self.oUtilsMsgs.DisplayError(sMsg)

        else:
            sMsg = 'Image file does not exist: ' + self.sImagePath \
                    + '\n See administrator : ' + sys._getframe(  ).f_code.co_name
            self.oUtilsMsgs.DisplayError(sMsg)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def LoadVolume(self):
        bLoadSuccess = self.LoadDicomVolume()
#         if not (self.sRoiVisibilityCode == 'Empty'):
#             self.SetSegmentRoiVisibility()
        return bLoadSuccess
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def LoadDicomVolume(self):
        self.slNode = None
        bLoadSuccess = False
        t = time.time()

        # first check if patient/series was already imported into the database
        
        database = slicer.dicomDatabase
        if (database.isOpen):

            bSeriesFoundInDB = False   # initialize
            
            lAllSeriesUIDs = DICOMUtils.allSeriesUIDsInDatabase(database)
#             print('NumSeries in DB: ', len(lAllSeriesUIDs))
            tags = {}
            tags['patientName'] = "0010,0010"
            tags['patientID'] = "0010,0020"
            tags['seriesUID'] = "0020,000E"
            tags['studyUID'] = "0020,000D"
            tags['seriesDescription'] = "0008,103E"
            tags['seriesNumber'] = "0020,0011"
            
            # using the path defined by the user to one of the files in the series,
            # access dicom information stored in that series
            
            sSeriesUIDToLoad = database.fileValue(self.sImagePath, tags['seriesUID'])
            sPatientName = database.fileValue(self.sImagePath , tags['patientName'])
            if sPatientName == '':
                sPatientName = 'No Name'
            sPatientID = database.fileValue(self.sImagePath , tags['patientID'])
            sSeriesDescription = database.fileValue(self.sImagePath, tags['seriesDescription'])
            if sSeriesDescription == '':
                sSeriesDescription = 'Unnamed Series'
            sSeriesNumber = database.fileValue(self.sImagePath, tags['seriesNumber'])

            self.sStudyInstanceUID = database.fileValue(self.sImagePath, tags['studyUID'])

            
            # extract directory that stores the dicom series from defined image path
            sHead_Tail = os.path.split(self.sImagePath)
            sDicomSeriesDir = sHead_Tail[0]
            
            elapsed = time.time() - t
#             print('Checking if already in db: %s' % elapsed)
            
            # check if already loaded into the database
            for sImportedSeries in lAllSeriesUIDs:
                if sImportedSeries == sSeriesUIDToLoad:
                    bSeriesFoundInDB = True
                    break

            # if not already in the database, import from series directory 
            #  NOTE: if more than one series is located in this directory, 
            #        all series will be imported
            if not bSeriesFoundInDB:
                elaspsed = time.time() - elapsed
#                 print('Starting import: %s' % elapsed )                
                DICOMUtils.importDicom(sDicomSeriesDir)


            # check subject hierarchy to see if volume already exists (loaded)
            bVolumeAlreadyLoaded = False
            
            
            slSubjectHierarchyNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
            
            slNodeId = slSubjectHierarchyNode.GetItemByUID(slicer.vtkMRMLSubjectHierarchyConstants.GetDICOMUIDName(),sSeriesUIDToLoad)
            if slNodeId > 0:
                bVolumeAlreadyLoaded = True
            else:
                elaspsed = time.time() - elapsed
#                 print('Starting load: %s' % elapsed )                

                DICOMUtils.loadSeriesByUID([sSeriesUIDToLoad])
                slNodeId = slSubjectHierarchyNode.GetItemByUID(slicer.vtkMRMLSubjectHierarchyConstants.GetDICOMUIDName(),sSeriesUIDToLoad)
                
#                 slPlugin = slicer.qSlicerSubjectHierarchyVolumesPlugin()
#                 iOnOrOff = slPlugin.getDisplayVisibility(slNodeId)
#                 print('SH eye: ',iOnOrOff, slNodeId)
                    
            
            if slNodeId == 0:
                
                # a multivolume type of node is not detected in the subject hierarchy using the GetItemByUID
                # (because there are multiple UID's ???)
                # if the the node ID is still 0 at this point,
                # search for a multivolume node containing SeriesDescription

                iNumNodes = slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLMultiVolumeNode')
                
                if iNumNodes > 0:
                    for idx in range(iNumNodes):
                        slMultiVolumeNode = slicer.mrmlScene.GetNthNodeByClass(idx, 'vtkMRMLMultiVolumeNode')
                        sNodeName = slMultiVolumeNode.GetName()
                        if sSeriesDescription in sNodeName:
                            self.slNode = slMultiVolumeNode
                            self.sNodeName = self.slNode.GetName()
                            bLoadSuccess = True
                            break
                else:
                    bLoadSuccess = False

            else:
                # load is complete with a valid node id
                # update the class properties with the slicer node and node name 
                self.slNode = slSubjectHierarchyNode.GetItemDataNode(slNodeId)
#                 self.sNodeName = self.slNode.GetName()
                bLoadSuccess = True
                        
            
        
        else:
            bLoadSuccess = False
            sErrorMsg = ('Slicer Database is not open')
            self.oUtilsMsgs.DisplayError(sErrorMsg)

        

        return bLoadSuccess

        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ReadXMLRoiElements(self):
        ''' For Image type is RTStuct, XML holds a visibility code and (if applicable)
            a list of ROI names
            
            The visibility code is as follows: 
           'All' : turn on visibility of all ROIs in RTStruct
           'None': turn off visibility of all ROIs in RTStruct
           'Ignore' : turn on all ROIs except the ones listed
           'Select' : turn on visibility of only ROIs listed
        '''
        
        # get XML ROIs element
        xRoisNode = self.oIOXml.GetChildren(self.GetXmlImageElement(), 'ROIs')
        
        # get visibility code from the attribute
        self.sRoiVisibilityCode = self.oIOXml.GetValueOfNodeAttribute(xRoisNode[0], 'ROIVisibilityCode')

        if (self.sRoiVisibilityCode == 'Select' or self.sRoiVisibilityCode == 'Ignore'):
            
            # get list of ROI children
            xRoiChildren = self.oIOXml.GetChildren(xRoisNode[0], 'ROI')

            for indRoi in range(len(xRoiChildren)):
                sRoiName = self.oIOXml.GetDataInNode(xRoiChildren[indRoi])
                self.lsRoiList.append(sRoiName)
                
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def GetAcquisitionVolumePlane(self, slInputNode):
#         
#         # extract the scan order from the volume's IJKToRASMatrix in order to determine 
#         # the original plane of acquisition for the volume
#         m4ijkToRAS = vtk.vtkMatrix4x4() # initialize
#         
#         slInputNode.GetIJKToRASMatrix(m4ijkToRAS)
#         
#         sScanOrder = slInputNode.ComputeScanOrderFromIJKToRAS(m4ijkToRAS)
#         
#         # order abbreviations:
#         #    I: inferior
#         #    S: superior
#         #    A: anterior
#         #    P: posterior
#         #    R: right
#         #    L: left
#         
#         if sScanOrder == 'IS' or sScanOrder == 'SI':
#             return 'Axial'
#         elif sScanOrder == 'PA' or sScanOrder == 'AP':
#             return 'Coronal'
#         elif sScanOrder == 'LR' or sScanOrder == 'RL':
#             return 'Sagittal'
#         
#          

#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def CheckForLabelMapNodeExists(self, sROIName):
#         
#         bNodeExists = False
#         
#         # get Slicer's subject hierarchy node (SHNode)
#         
#         slSHNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
#         
#         
#         # get the item ID for the Patient through the Study Series Instance UID
#         
#         slStudyItemID = slSHNode.GetItemByUID(slicer.vtkMRMLSubjectHierarchyConstants.GetDICOMUIDName(), self.sStudyInstanceUID)
# 
# 
#         # using slicers vtk Item Id for the Volume, get the ROI names (children)
#         
#         slStudyChildren = vtk.vtkIdList()    # initialize to ItemId type
#         slSHNode.GetItemChildren(slStudyItemID, slStudyChildren) # populate children variable
#         
#         for indChild in range(slStudyChildren.GetNumberOfIds()):
#             # get id
#             slChildId = slStudyChildren.GetId(indChild)
#             # get datanode
#             slChildDataNode = slSHNode.GetItemDataNode(slChildId)
#             
#             #check if class name matches
#             if (slChildDataNode.GetClassName() == 'vtkMRMLLabelMapVolumeNode'):
#                 # check if name matches
#                 if (slChildDataNode.GetName() == sROIName):
#                     bNodeExists = True
#                     
#         
#         return bNodeExists
        

# ##########################################################################
# #
# #   Class SubjectHierarchyDetail
# #
# ##########################################################################
# 
# class SubjectHierarchyDetail:
#     
#     def __init__(self,  parent=None):
#         
#         self.slSHNode = None
#         self.slSegDisplayNode = None
#         self.slSegDataNode = None
#         
#         self.slStudyItemId = ''
#         self.slRTStructItemId = ''
#         self.slSegDisplayNodeId = ''
# 
#         
#         self.slRTStructChildren = None
#         self.slStudyChildren = None
#         
#         self.lsSubjectHierarchyROINames = []
#         
#     
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def TraverseSubjectHierarchy(self, sStudyInstanceUID, sSeriesInstanceUID):
#         
#         # get Slicer's subject hierarchy node (SHNode)
#         
#         self.slSHNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
#         
#         
#         # get the item ID for the Patient study through the Study Series Instance UID
#         
#         self.slStudyItemID = self.slSHNode.GetItemByUID(slicer.vtkMRMLSubjectHierarchyConstants.GetDICOMUIDName(), sStudyInstanceUID)
# 
# 
#         # using slicers vtk Item Id for the Volume, get the ROI names (children)
#         
#         self.slStudyChildren = vtk.vtkIdList()    # initialize to ItemId type
#         self.slSHNode.GetItemChildren(self.slStudyItemID, self.slStudyChildren) # populate children variable
# 
#         # get the item ID for the RTStruct through the RTStruct Series Instance UID
#         
#         self.slRTStructItemId = self.slSHNode.GetItemByUID(slicer.vtkMRMLSubjectHierarchyConstants.GetDICOMUIDName(), sSeriesInstanceUID)
# 
# 
#         # using slicers vtk Item Id for the RTStruct, get the ROI names (children)
#         
#         self.slRTStructChildren = vtk.vtkIdList()    # initialize to ItemId type
#         self.slSHNode.GetItemChildren(self.slRTStructItemId, self.slRTStructChildren) # populate children variable
#         
#         
#         # get ROI child Item ID and store the child (ROI) name
#         
#         self.lsSubjectHierarchyROINames = []
#         for indROI in range(self.slRTStructChildren.GetNumberOfIds()):
#             slROIItemId = self.slRTStructChildren.GetId(indROI)
#             sROIName = self.slSHNode.GetItemName(slROIItemId)
#             self.lsSubjectHierarchyROINames.append(sROIName)
#         
#         
#         # get segmentation node name from data node
#         
#         self.slSegDataNode = self.slSHNode.GetItemDataNode(self.slRTStructItemId)
#         self.slSegDisplayNodeId = self.slSegDataNode.GetDisplayNodeID()
#         self.slSegDisplayNode = slicer.mrmlScene.GetNodeByID(self.slSegDisplayNodeId)

