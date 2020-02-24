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
                slNode, sImageDestination, sOrientation, sViewLayer = self.ltupViewNodes[i]
                self.AssignNodesToView(slNode.GetName(), sImageDestination, sViewLayer, sOrientation)


    #-----------------------------------------------
    #         Manage Data Loading
    #-----------------------------------------------

    def BuildViewNodes(self, xImages):
        
        # for each image
        for i in range(len(xImages)):


            # Extract image attributes
            sVolumeFormat = self.oIOXml.GetValueOfNodeAttribute(xImages[i], 'format')
            sNodeDescriptor = self.oIOXml.GetValueOfNodeAttribute(xImages[i], 'descriptor')
            sImageType = self.oIOXml.GetValueOfNodeAttribute(xImages[i], 'type')
            sImageDestination = self.oIOXml.GetValueOfNodeAttribute(xImages[i], 'destination')
            sOrientation = self.oIOXml.GetValueOfNodeAttribute(xImages[i], 'orientation')
            sNodeName = self.sPageName + '_' + self.sPageDescriptor + '_' + sNodeDescriptor

            
            # Extract type of image being loaded

            xImageTypeNodes = self.oIOXml.GetChildren(xImages[i], 'Type')
            
            if len(xImageTypeNodes) > 1:
                sWarningMsg = 'There can only be one type of image - using first definition'
                self.oUtils.DisplayWarning(sWarningMsg) 
                
#            self.sImageType = self.oIOXml.GetDataInNode(xImageTypeNodes[0])
            

            # Extract path element
            
            xPathNodes = self.oIOXml.GetChildren(xImages[i], 'Path')

            if len(xPathNodes) > 1:
                sWarningMsg = 'There can only be one path per image - using first defined path'
                self.oUtils.DisplayWarning( sWarningMsg )

            sImagePath = self.oIOXml.GetDataInNode(xPathNodes[0])
            

            # Extract destination layer (foreground, background, label)

            xLayerNodes = self.oIOXml.GetChildren(xImages[i], 'Layer')
            if len(xLayerNodes) > 1:
                sWarningMsg = 'There can only be one layer per image - using first defined layer'
                self.oUtils.DisplayWarning(sWarningMsg)

            sViewLayer = self.oIOXml.GetDataInNode(xLayerNodes[0])
            
            
            # Load images 
            
            bLoadSuccess = True
            if (sVolumeFormat == 'dicom'):
                bLoadSuccess, slNode = self.LoadDicomVolume(sImagePath, sImageType)                

            elif (sVolumeFormat in self.lValidVolumeFormats):
                bLoadSuccess, slNode = self.LoadDataVolume(sNodeName, sImageType, sImagePath)

                        
            else:
                sErrorMsg = ('Undefined volume format : %s' % sVolumeFormat)
                self.oUtils.DisplayError(sErrorMsg)
                bLoadSuccess = False

            if bLoadSuccess and (slNode is not None):
                tupViewNode = [slNode, sImageDestination, sOrientation, sViewLayer]
                self.ltupViewNodes.append(tupViewNode)
    
        return self.ltupViewNodes
                    
                    
         
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
            
            sHead_Tail = os.path.split(sDicomFilePath)
            sDicomSeriesDir = sHead_Tail[0]
            
            
            for sImportedSeries in lAllSeriesUIDs:
                if sImportedSeries == sSeriesUIDToLoad:
                    bSeriesFoundInDB = True
                
            if not bSeriesFoundInDB:  # import all series in user specified directory
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
    
    
