'''
####################################################
VolumeToDicomGenerator
####################################################
Description:
        DICOMs exported for a sequence will have the primary volume (and RTStruct)
        in the directory requested by the user. If the user also requested that all series
        of the sequence be exported, they will be in a subfolder named VolumeSequence_xx where xx 
        is the ID number of the volume node in the slicer scene.

Created September 2021

Author: Carol Johnson 
        Baines Imaging Laboratory, 
        LRCP, London Health Sciences Centre
        London, Ontario
'''
import qt, ctk, slicer
import os, sys, argparse, logging
import DICOMLib
from DICOMLib import DICOMUtils
from PythonQt import QtCore, QtGui
from slicer.ScriptedLoadableModule import *


import DicomRtImportExportPlugin
import DICOMVolumeSequencePlugin
import DICOMScalarVolumePlugin
 
import pydicom
import distutils
from distutils import util

try:
    import pandas as pd
  
    print("running with pandas")
except ImportError:
    print("!"*50, 'pandas not installed - required for VolumeToDicomGenerator remap UIDs function')
  
try:
    import numpy as np
    print("running with numpy")
except ImportError:
    print("!"*50, 'numpy not installed - required for VolumeToDicomGenerator remap UIDs function')


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Decorators
#

def handleErrors(func):
    def inner(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.state = 'invalid'
            #self.updateState()
    return inner


#==================================================================================================================================
# class VolumeToDicomGenerator
#==================================================================================================================================
class VolumeToDicomGenerator(ScriptedLoadableModule):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        parent.title = "VolumeToDicom Generator"
        parent.categories = ["Baines Custom Modules"]
        parent.dependencies = []
        parent.contributors = ["Carol Johnson (Baines Imaging Laboratories)"]
        parent.helpText = """
        This is a module to generate a dicom series for a specified volume (from format: .nrrd, .nii, or .mhd).
        \nIf the user defines the volume to be a 4D sequence, there is an option to export all volumes in the time series.
        \nThe user has the option to also specify a label map file (mask for contours from format: .nrrd, .nii, or .mhd).
        The label map will be exported as an RTStruct with the dicoms of the associated primary image volume.
        \nThere is also an option to modify the RTStruct's UID's to match the volume UID's of the original DICOM series.
        """
        parent.acknowledgementText = """
            Baines Imaging Lab, LRCP, London Health Sciences Centre, London ON
        """
        self.parent = parent
        
        # Add this test to the SelfTest module's list for discovery when the module
        # is created.  Since this module may be discovered before SelfTests itself,
        # create the list if it doesn't already exist.
        try:
            slicer.selfTests
        except AttributeError:
            slicer.selfTests = {}
        slicer.selfTests['VolumeToDicomGenerator'] = self.runTest

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def runTest(self):
        return
    
#==================================================================================================================================
# class VolumeToDicomGeneratorWidget
#==================================================================================================================================
class VolumeToDicomGeneratorWidget(ScriptedLoadableModuleWidget):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        
        self.oIOParams = IOParams()

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # GUI Layout
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        parametersCollapsibleButton = ctk.ctkCollapsibleButton()
        parametersCollapsibleButton.text = "Parameters to generate DICOM"
        self.layout.addWidget(parametersCollapsibleButton)
    
        ######## Define Layouts
        parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)
        qInputsGroupBoxLayout = qt.QVBoxLayout()
        qVolumeTypeGrpBoxLayout = qt.QHBoxLayout()
        qLabelMapGrpBoxLayout = qt.QVBoxLayout()
        qOutputGrpBoxLayout = qt.QVBoxLayout()
        
    
        ########################################
        ######## Image volume details
        qInputsGroupBox = qt.QGroupBox("Image Volume Details")
        qInputsGroupBox.setLayout(qInputsGroupBoxLayout)

        self.inputImageVolumeFileButton = qt.QPushButton('Select image volume file:')
        self.inputImageVolumeFileButton.setStyleSheet("QPushButton{ background-color: rgb(255,202,128) }")
        self.inputImageVolumeFileButton.toolTip = "Select image volume file (.nrrd, .nii, .mhd)."
        self.inputImageVolumeFileButton.connect('clicked(bool)', self.onSelectImageVolumeFile)
        
        
        self.qVolumeTypeGrpBox = qt.QGroupBox("Image Type       (3D Volume or 4D Volume Sequence)")
        self.qVolumeTypeGrpBox.setLayout(qVolumeTypeGrpBoxLayout)

        self.qVolumeTypeButtons = {}
        self.lVolumeTypes = ["volume", "sequence"]
        for sVolType in self.lVolumeTypes:
            self.qVolumeTypeButtons[sVolType] = qt.QRadioButton()
            self.qVolumeTypeButtons[sVolType].text = sVolType
            self.qVolumeTypeButtons[sVolType].connect("clicked()",
                                    lambda t=sVolType: self.onToggleImageType(t))
            qVolumeTypeGrpBoxLayout.addWidget(self.qVolumeTypeButtons[sVolType])

        self.chkExportAllSeriesOfSequence = qt.QCheckBox("Export all series of the sequence")
        self.chkExportAllSeriesOfSequence.setChecked(0)
        self.chkExportAllSeriesOfSequence.enabled = False
        self.chkExportAllSeriesOfSequence.toggled.connect(self.onToggleSeriesExport)

        # add image volume widgets to layout
        qInputsGroupBoxLayout.addWidget(self.inputImageVolumeFileButton)
        qInputsGroupBoxLayout.addWidget(self.qVolumeTypeGrpBox)
        qInputsGroupBoxLayout.addWidget(self.chkExportAllSeriesOfSequence)
        self.onToggleImageType(self.lVolumeTypes[0]) # set default

 
        parametersFormLayout.addWidget(qInputsGroupBox)
        parametersFormLayout.addRow("  ",qt.QLabel("   "))  # add spacing


        ########################################
        ######## Label map / RTStruct details
        qLabelMapGroupBox = qt.QGroupBox("Label Map Details (Optional)")
        qLabelMapGroupBox.setLayout(qLabelMapGrpBoxLayout)

        self.inputLabelMapFileButton = qt.QPushButton('Select label map file:')
        self.inputLabelMapFileButton.setStyleSheet("QPushButton{ background-color: rgb(255,202,128) }")
        self.inputLabelMapFileButton.toolTip = "OPTIONAL: Select label map (contour mask) file (.nrrd, .nii, .mhd)."
        self.inputLabelMapFileButton.connect('clicked(bool)', self.onSelectLabelMapFile)


        self.chkRemapRTStructUIDs = qt.QCheckBox("Remap RTStuct to original volume UIDs")
        self.chkRemapRTStructUIDs.setChecked(0)
        self.chkRemapRTStructUIDs.toggled.connect(self.onToggleRemapBtn)
        self.chkRemapRTStructUIDs.toolTip = "RTStruct will be remapped to match UIDs of original image volume."

        self.qOrigImageDirLabel = qt.QLabel("Select directory of original DICOM volume:")
        self.qOrigImageDirLabel.enabled = False
        self.originalImageDirButton = ctk.ctkDirectoryButton()
        self.originalImageDirButton.enabled = False
        self.originalImageDirButton.directory = slicer.app.temporaryPath


        # add widgets to layout
        qLabelMapGrpBoxLayout.addWidget(self.inputLabelMapFileButton)
        qLabelMapGrpBoxLayout.addWidget(self.chkRemapRTStructUIDs)
        qLabelMapGrpBoxLayout.addWidget(self.qOrigImageDirLabel)
        qLabelMapGrpBoxLayout.addWidget(self.originalImageDirButton)

        parametersFormLayout.addWidget(qLabelMapGroupBox)
        parametersFormLayout.addRow("  ",qt.QLabel("   "))  # add spacing

        ########################################
        ######## Output directory
        qOutputDirGroupBox = qt.QGroupBox('Select output directory for DICOM series:')
        qOutputDirGroupBox.setLayout(qOutputGrpBoxLayout)
        self.outputDirButton = ctk.ctkDirectoryButton()
        self.outputDirButton.directory = slicer.app.temporaryPath
        self.outputDirButton.setStyleSheet("QPushButton{ background-color: rgb(255,202,128) }")
        qOutputGrpBoxLayout.addWidget(self.outputDirButton)

        parametersFormLayout.addWidget(qOutputDirGroupBox)
        parametersFormLayout.addRow("  ",qt.QLabel("   "))  # add spacing

        ########################################
        ######## Generate button
        createRTStructButton = qt.QPushButton('Create DICOMs')
        createRTStructButton.setStyleSheet("QPushButton{ background-color: rgb(0,153,76) }")
        parametersFormLayout.addRow(createRTStructButton)
    
        createRTStructButton.connect('clicked()', self.onApplyCreateDicom)

        ########################################
        ######## Reset button
        resetButton = qt.QPushButton('Reset')
        resetButton.setStyleSheet("QPushButton{ background-color: rgb(100,250,206) }")
        resetButton.connect('clicked()', self.onApplyReset)
        parametersFormLayout.addWidget(resetButton)
        parametersFormLayout.addRow("  ",qt.QLabel("   "))  # add spacing
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onSelectImageVolumeFile(self):
        self.imageVolumeFileDialog = ctk.ctkFileDialog(slicer.util.mainWindow())
        self.imageVolumeFileDialog.setWindowModality(1)
        self.imageVolumeFileDialog.setWindowTitle("Select file for image volume")
        self.imageVolumeFileDialog.defaultSuffix = "nrrd"
        self.imageVolumeFileDialog.setNameFilter("Image volume file (*.nrrd *.nii *.mhd)")
        self.imageVolumeFileDialog.connect("fileSelected(QString)", self.onImageVolumeFileSelected)
        self.imageVolumeFileDialog.open()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onImageVolumeFileSelected(self,inputFilePath):
        self.inputImageVolumeFileButton.setText(inputFilePath)
        self.oIOParams.sImageVolumePath = inputFilePath
        return inputFilePath
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onSelectLabelMapFile(self):
        self.labelMapFileDialog = ctk.ctkFileDialog(slicer.util.mainWindow())
        self.labelMapFileDialog.setWindowModality(1)
        self.labelMapFileDialog.setWindowTitle("Select file for label map")
        self.labelMapFileDialog.defaultSuffix = "nrrd"
        self.labelMapFileDialog.setNameFilter("Label map file (*.nrrd *.nii *.mhd)")
        self.labelMapFileDialog.connect("fileSelected(QString)", self.onLabelMapFileSelected)
        self.labelMapFileDialog.open()
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onLabelMapFileSelected(self,inputFilePath):
        self.inputLabelMapFileButton.setText(inputFilePath)
        self.oIOParams.sLabelMapPath = inputFilePath
        return inputFilePath
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onToggleImageType(self, sValue):
        
        self.qVolumeTypeButtons[sValue].setChecked(True)

        if sValue == 'volume':
            self.oIOParams.sImageType = 'volume'
            self.chkExportAllSeriesOfSequence.enabled = False
            self.chkExportAllSeriesOfSequence.setChecked(0)
            self.bExportAllSeriesOfSequence = False
            
        else:
            # volume sequence
            self.oIOParams.sImageType = 'sequence'
            self.chkExportAllSeriesOfSequence.enabled = True
            self.chkExportAllSeriesOfSequence.setChecked(1)
            self.bExportAllSeriesOfSequence = True
            

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onToggleSeriesExport(self, enabled):
        if enabled:
            self.oIOParams.bExportAllSeriesOfSequence = True
        else:
            self.oIOParams.bExportAllSeriesOfSequence = False
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onToggleRemapBtn(self, enabled):
        if enabled:
            self.originalImageDirButton.enabled = True
            self.qOrigImageDirLabel.enabled = True
            self.originalImageDirButton.setStyleSheet("QPushButton{ background-color: rgb(255,202,128) }")
        else:
            self.originalImageDirButton.enabled = False
            self.qOrigImageDirLabel.enabled = False
            self.originalImageDirButton.setStyleSheet('')
            self.originalImageDirButton.directory = slicer.app.temporaryPath

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onApplyReset(self):
        slicer.mrmlScene.Clear()

        self.oIOParams.Reset()
        self.inputImageVolumeFileButton.setText("Select file for image volume")
        self.onToggleImageType(self.lVolumeTypes[0]) # set default
        self.chkExportAllSeriesOfSequence.setChecked(0)

        self.inputLabelMapFileButton.setText("Select file for label map")
        self.chkRemapRTStructUIDs.setChecked(0)
        self.outputDirButton.directory = slicer.app.temporaryPath
        self.originalImageDirButton.directory = slicer.app.temporaryPath

        print('*'*40, '   Reset Complete   ', '*'*40)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @handleErrors
    def onApplyCreateDicom(self):
        
        self.msgBox = qt.QMessageBox()
        slicer.mrmlScene.Clear()
        bGUIEnabled = True     # generate was requested through this module GUI
        
        self.oIOParams.sOutputDir = self.outputDirButton.directory
        self.oIOParams.sOriginalDicomImageDir = self.originalImageDirButton.directory

        logic = VolumeToDicomGeneratorLogic(True)

        logic.StartGenerator(self.oIOParams)
        
#==================================================================================================================================
# class VolumeToDicomGeneratorLogic
#==================================================================================================================================
class VolumeToDicomGeneratorLogic(ScriptedLoadableModuleLogic):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, bGUIEnabled):
        ScriptedLoadableModuleLogic.__init__(self)

        self.shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        self.slLabelMapSegNodeID = None   # default
        self.msgBox = qt.QMessageBox()
        self.iExportFilesCount = 0
        self.bGUIEnabled = bGUIEnabled
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def StartGenerator(self,  oIOParams):
#         self.LoadVolumes(oIOParams)
        
        tupResultSuccess = self.LoadVolumes( oIOParams)


        if tupResultSuccess[0] == False:
            if self.bGUIEnabled == True:
                self.msgBox.warning(slicer.util.mainWindow(),"VolumeToDicomGenerator: WARNING",tupResultSuccess[1])
            else:
                print('VolumeToDicomGenerator: WARNING   Trouble loading input volumes')
        else:
            tupResultSuccess = self.ExportToDicom(oIOParams)
 
        if tupResultSuccess != None and tupResultSuccess[0]:
            print("Export of DICOMs complete")
        else:
            sMsg = 'INCOMPLETE ... DICOMs not exported.'
            if self.bGUIEnabled:
                self.msgBox.warning(slicer.util.mainWindow(),"VolumeToDicomGenerator: WARNING",sMsg)
            else:
                print(sMsg)

        if tupResultSuccess[0] and oIOParams.sOriginalDicomImageDir != slicer.app.temporaryPath:
            self.RemapRTSTructToOriginalVolume(oIOParams)
            print('Finished remap to original DICOM UIDs')


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @handleErrors
    def LoadVolumes(self, oIOParams):
        self.canceled = False
        sMsg = ''
        bSuccess = True        

        try:
        
            print('Loading image volume and label map files.')
            
            logging.debug('Input image volume: %s' % oIOParams.sImageVolumePath)
            logging.debug('Input label map: %s' % oIOParams.sLabelMapPath)
            
            if self.bGUIEnabled:
                progressDialog = slicer.util.createProgressDialog(labelText=\
                                        'Loading volumes ...', maximum=0)
    
            # load image and label map volumes
            
            if oIOParams.sLabelMapPath == '':
                self.slLabelMapNode = None
            else:
                dictProperties = {'labelmap' : True, 'show': False}
                self.slLabelMapNode = slicer.util.loadLabelVolume(oIOParams.sLabelMapPath, dictProperties)
    
            if oIOParams.sImageType == 'volume':
                self.slImageNode = slicer.util.loadVolume(oIOParams.sImageVolumePath)
            elif oIOParams.sImageType == 'sequence':
                # load the multi volume file as a sequence node
                # from the sequence node, slicer creates a ScalarVolumeNode in the subject hierarchy
                # access the data node through the subject hierarchy
                slSeqNode = slicer.util.loadNodeFromFile(oIOParams.sImageVolumePath,'SequenceFile')
        
                slSHItemID = self.shNode.GetItemChildWithName(self.shNode.GetSceneItemID(), slSeqNode.GetName())
                self.slImageNode = self.shNode.GetItemDataNode(slSHItemID)
            else:
                bSuccess = False
                sMsg = sMsg + '\nTrouble loading image - Invalid volume type.'
                               
            if self.bGUIEnabled:
                progressDialog.close()
            
        except:
            sMsg = 'Trouble loading volumes ... '
            + '\nCheck the input volume(s) selection (image and label map)'
            + '\nand that the correct volume type was selected.'
            bSuccess = False
            if self.bGUIEnabled:
                progressDialog.close()
            
        return bSuccess, sMsg

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @handleErrors
    def ExportToDicom(self, oIOParams):
        
        print("Exporting DICOMs ")
        print("          ...........  primary volume.")

        # work in subject hierarchy node (shNode)
        self.slPrimaryVolumeID = self.shNode.GetItemByDataNode(self.slImageNode)
        
        # get number of files in the primary node
        slPrimaryDataNode = self.shNode.GetItemDataNode(self.slPrimaryVolumeID)
        slPrimaryImageNode = slPrimaryDataNode.GetImageData()
        lPrimaryDimensions = list(range(3))
        slPrimaryImageNode.GetDimensions(lPrimaryDimensions)
        self.iExportFilesCount = self.iExportFilesCount + lPrimaryDimensions[2]
        
        # create subject hierarchy - new patient and study
        slNewPatientItemID = self.shNode.CreateSubjectItem(self.shNode.GetSceneItemID(), "Patient Baines1")
        slNewStudyItemID = self.shNode.CreateStudyItem(slNewPatientItemID, "Study Baines1")
        self.shNode.SetItemParent(self.slPrimaryVolumeID, slNewStudyItemID)

        if (self.slLabelMapNode != None):
            # convert label map to segmentation
            slLabelMapSegNode =  slicer.mrmlScene.AddNewNodeByClass('vtkMRMLSegmentationNode')
            slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(self.slLabelMapNode, slLabelMapSegNode)
            
            # Associate segmentation node with a reference volume node
            slStudyShItem = self.shNode.GetItemParent(self.slPrimaryVolumeID)
            self.slLabelMapSegNodeID = self.shNode.GetItemByDataNode(slLabelMapSegNode)
            self.shNode.SetItemParent(self.slLabelMapSegNodeID, slStudyShItem)

        # define exporter based on the class of volume loaded        
        exporter = None
        if self.slImageNode.GetClassName() == 'vtkMRMLMultiVolumeNode':
            exporter = DICOMScalarVolumePlugin.DICOMScalarVolumePluginClass()
            sMsg = "This multi-volume image was loaded as a 'volume' instead of a 'sequence'."\
                    + "\nOnly the primary volume (time series 0) will be exported."
            if not (self.slLabelMapNode == None):
                # a multivolume node imported as a 'volume' can only have the primary
                # image volume (time series = 0) exported as a dicom. To have the RTStruct
                # exported as well, you must load the multi volume image as a 'sequence'
                sMsg = sMsg + "\nLabel map cannot be exported as an RTStruct unless the multi-volume image is imported as a 'sequence'."

            if self.bGUIEnabled:
                self.msgBox.warning(slicer.util.mainWindow(),"VolumeToDicomGenerator: WARNING",sMsg)
            else:
                print(sMsg)
                
                
        elif self.slImageNode.GetClassName() == 'vtkMRMLScalarVolumeNode':
            # use the DicomRTImportExport plugin to export scalar volume nodes
            # This can handle a label map volume if specified
            exporter = DicomRtImportExportPlugin.DicomRtImportExportPluginClass()
        else:
            if self.bGUIEnabled:
                sMsg = "Unrecognized volume class: " + self.slImageNode.GetClassName() + \
                        "Export will not be done."
                self.msgBox.error(slicer.util.mainWindow(),"VolumeToDicomGenerator: ERROR",sMsg)
            else:
                print(sMsg)
            
        # export primary series for both volume and sequence image types (class = vtkMRMLScalarVolumeNode)
        # RTStruct is also exported here if selected by the user
        if exporter != None:
            if (self.slLabelMapNode != None):
                print("          ...........  RTStruct.")
                self.iExportFilesCount = self.iExportFilesCount + 1
            tupResultSuccess = self.PerformExport(exporter, oIOParams)  
        

        # if the user requested exporting all series of a sequence, use
        #    DICOMVolumeSequencePlugin to export
        if oIOParams.sImageType == 'sequence' and oIOParams.bExportAllSeriesOfSequence == True:
 
            print("          ...........  all time series for 4D sequence.")
            
            # get number of frames in the sequence to adjust the number of files being exported
            slSeqNodeList = slicer.mrmlScene.GetNodesByClass('vtkMRMLSequenceNode')
            if slSeqNodeList != None:
                slPrimarySequenceNode = slSeqNodeList.GetItemAsObject(0)
                iNumFrames = int(slPrimarySequenceNode.GetAttribute('MultiVolume.NumberOfFrames'))
                self.iExportFilesCount = self.iExportFilesCount + (iNumFrames * lPrimaryDimensions[2])
            else:
                sMsg = 'VolumeToDicomGenerator.ExportToDicom:  Could not access the sequence node'
                return False, sMsg
            
            # export the time series (rtstruct not exported here)
            self.slLabelMapSegNodeID = None
            exporter = DICOMVolumeSequencePlugin.DICOMVolumeSequencePluginClass()
            tupResultSuccess = self.PerformExport(exporter, oIOParams)  

        return tupResultSuccess
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @handleErrors
    def PerformExport(self, exporter, oIOParams):

        bSuccess = True
        sMsg = ''
        try:
            exportables = []
            # examine volumes for export and add to export list
            volExportable = exporter.examineForExport(self.slPrimaryVolumeID)
            exportables.extend(volExportable)
            if self.slLabelMapSegNodeID != None:
                segExportable = exporter.examineForExport(self.slLabelMapSegNodeID)
                exportables.extend(segExportable)
              
            # assign output path to each exportable
            for exp in exportables:
                exp.directory = oIOParams.sOutputDir
                
            # perform export
            if self.bGUIEnabled:
                progressDialog = slicer.util.createProgressDialog(labelText=\
                                        'Exporting ' + str(self.iExportFilesCount) +\
                                         ' DICOM files. Be patient ...', maximum=0)

            exporter.export(exportables)
            
            if self.bGUIEnabled:
                progressDialog.close()
            
        except:
            sMsg = 'Trouble exporting'
            bSuccess = False
            
        return bSuccess, sMsg
       
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @handleErrors
    def RemapRTSTructToOriginalVolume(self, oIOParams):
        
        # Code adapted from 'mapRTStructToVolume' found on GitHub; authored by davisr28 on Jan 30, 2020
        # https://github.com/ryanmdavis/mapRTStructToVolume/blob/master/map_rtstruct_to_volume.py
        
        sRemappedRTStructOutputDir = os.path.join(oIOParams.sOutputDir, 'MappedToOriginal')
        self.mapRTStructToVolume(oIOParams.sOriginalDicomImageDir, oIOParams.sOutputDir, sRemappedRTStructOutputDir)
    
        


    # mapToOriginalVolume takes a image volume & RTStruct output by slicer and maps that RTStruct back to 
    #     the original volume that slicer originally read in.
    #
    # Input:
    #     original_volume_loc: path to folder containing the original volume that we want the RTStruct to reference
    #     slicer_volume_loc: path to folder containing the image volume ant RTStruct that was output by slicer
    #     rtss_save_loc: path to folder where the RTStruct (which references the original volume) should be stored.
    #
    # Caveats:
    #    1) This function throws an error when there is not a 1-to-1 mapping of z positions between the original and Slicer
    #    output volumes. This situation (no 1-to-1 mapping) occurs when Slicer loads an irregular geometry, such as
    #    jumps in z position.
    #
    #    2) In the situation where there is irregular geometry but still a 1-to-1 mapping of z positions between volumes
    #    this code maps the volume SOPInstanceUIDs by sorting z positions of both volumes, then pairing by the sorted order.
    #    
    #    3) Take caution in general when changing referenced UIDs, and especially when using this function on volumes
    #    with irregular geometries.
    
    def mapRTStructToVolume(self, original_volume_loc, slicer_volume_loc, rtss_save_loc):
    
        # read the z position to SOPInstanceUID mapping into dataframes
        original_uids_df,original_vol_attr=self.getUIDAndZPos(original_volume_loc)
        original_uids_df=original_uids_df.rename(mapper={"SOPInstanceUID":"SOPInstanceUID_Original"},axis=1)
        new_uids_df=self.getUIDAndZPos(slicer_volume_loc)[0].rename(mapper={"SOPInstanceUID":"SOPInstanceUID_New"},axis=1)

        
        # double check that the mapping based on Z position will be 1-to-1 as expected
        original_z=set(original_uids_df["ImageZPosMm"])
        new_z=set(new_uids_df["ImageZPosMm"])
        union=new_z.union(original_z)
        
        # generate the mapping from slicer_output_volume SOPInstanceUIDs to original volume SOPInstanceUIDs
        if len(union) == len(original_z): # if this is false, then the new and original volumes are not matched
        
            # Find the SOPInstanceUID mapping and drop the Z position
            new_uids_df=new_uids_df.rename(axis=1,mapper={"ImageZPosMm":"ImageZPosMm_New"})
            original_uids_df=original_uids_df.rename(axis=1,mapper={"ImageZPosMm":"ImageZPosMm_Original"})
        
            new_to_original_UID_mapping_df=new_uids_df[["ImageZPosMm_New","SOPInstanceUID_New"]].merge(original_uids_df[["ImageZPosMm_Original","SOPInstanceUID_Original"]],left_on="ImageZPosMm_New",right_on="ImageZPosMm_Original",how="left")
        
        # often this happens when there is irregular slice geometry
        elif len(original_z) == len(new_z):
            new_to_original_UID_mapping_df = mapBySliceSorting(new_uids_df,original_uids_df)
            if len(new_to_original_UID_mapping_df)==0:
                return False
        else:
            return False
        
        # get the rtss location and make sure there is only one RTSS in that directory as expected:
        new_vol_files=os.listdir(slicer_volume_loc)
        rtss_files=[file for file in new_vol_files if (("rtss" in file) or ("rtstruct" in file))]
        assert len(rtss_files) == 1
        rtss_file=rtss_files[0]
        
        # read the rtss
        rtss=pydicom.dcmread(os.path.join(slicer_volume_loc,rtss_file))
        
        # Set top level attributes of the RTStruct to output
        rtss[0x0020,0x000d].value=original_vol_attr["StudyInstanceUID"]
        
        # Set attributes within ReferencedFrameOfReferenceSequence
        for i_RefFrameOfRef in range(len(list(rtss[0x3006,0x0010]))):
            for i_RTRefStudy in range(len(list(rtss[0x3006,0x0010][i_RefFrameOfRef][0x3006,0x0012]))): # (3006, 0012)  RT Referenced Study Sequence
                
                # make sure for this simple code that RTStruct only references one series
                if len(list(rtss[0x3006,0x0010][i_RefFrameOfRef][0x3006,0x0012][i_RTRefStudy][0x3006,0x0014])) != 1:
                    raise RuntimeError("This function does not handle RTStructs referencing more than one series.")
                
                for i_RTRefSeries in range(len(list(rtss[0x3006,0x0010][i_RefFrameOfRef][0x3006,0x0012][i_RTRefStudy][0x3006,0x0014]))):
                    for i_ContourImage in range(len(list(rtss[0x3006,0x0010][i_RefFrameOfRef][0x3006,0x0012][i_RTRefStudy][0x3006,0x0014][i_RTRefSeries][0x3006,0x0016]))):
        #             for RTReferencedSeries in RTReferencedStudy[0x3006,0x0014]:
                        new_vol_SOPInstanceUID=rtss[0x3006,0x0010][i_RefFrameOfRef][0x3006,0x0012][i_RTRefStudy][0x3006,0x0014][i_RTRefSeries][0x3006,0x0016][i_ContourImage][0x0008,0x1155].value
                        original_vol_SOPInstanceUID=new_to_original_UID_mapping_df[new_to_original_UID_mapping_df["SOPInstanceUID_New"]==new_vol_SOPInstanceUID]["SOPInstanceUID_Original"].iloc[0]
                        rtss[0x3006,0x0010][i_RefFrameOfRef][0x3006,0x0012][i_RTRefStudy][0x3006,0x0014][i_RTRefSeries][0x3006,0x0016][i_ContourImage][0x0008,0x1155].value=original_vol_SOPInstanceUID
                        
                        # ReferenceSOPClassUID
                        if (0x0008,0x1150) in rtss[0x3006,0x0010][i_RefFrameOfRef][0x3006,0x0012][i_RTRefStudy][0x3006,0x0014][i_RTRefSeries][0x3006,0x0016][i_ContourImage]:               
                            rtss[0x3006,0x0010][i_RefFrameOfRef][0x3006,0x0012][i_RTRefStudy][0x3006,0x0014][i_RTRefSeries][0x3006,0x0016][i_ContourImage][0x0008,0x1150].value=original_vol_attr["SOPClassUID"]
                        
                    # Referenced SeriesInstanceUID
                    original_series=original_uids_df[original_uids_df["SOPInstanceUID_Original"] == original_vol_SOPInstanceUID]["SeriesInstanceUID"].iloc[0]
                    if (0x0020,0x000e) in rtss[0x3006,0x0010][i_RefFrameOfRef][0x3006,0x0012][i_RTRefStudy][0x3006,0x0014][i_RTRefSeries]:
                        rtss[0x3006,0x0010][i_RefFrameOfRef][0x3006,0x0012][i_RTRefStudy][0x3006,0x0014][i_RTRefSeries][0x0020,0x000e].value=original_series
                    else: # some RTStructs don't contain this element, so add it
                        rtss[0x3006,0x0010][i_RefFrameOfRef][0x3006,0x0012][i_RTRefStudy][0x3006,0x0014][0].add_new((0x0020,0x000e), "UI", original_series)
        # Set Attributes within ROIContourSequence
        for i_ROIContourSequence in range(len(list(rtss[0x3006,0x0039]))):
            for i_ContourSequence in range(len(list(rtss[0x3006,0x0039][i_ROIContourSequence][0x3006,0x0040]))):
                
                # check if slicer altered the z values for this contour (as happens when there is an irregular geometry
                contour_seq_z_val=round(float(rtss[0x3006,0x0039][i_ROIContourSequence][0x3006,0x0040][i_ContourSequence][0x3006,0x0050].value[2]),1)
                df_row=new_to_original_UID_mapping_df[new_to_original_UID_mapping_df["ImageZPosMm_New"]==contour_seq_z_val]
    
                # if slicer has altered the z values, then change the z values in the RTStruct to match those of the original image volume
                if not (df_row["ImageZPosMm_Original"].iloc[0] == df_row["ImageZPosMm_New"].iloc[0]):
                    original_z_pos=df_row["ImageZPosMm_Original"].iloc[0]
                    old_contour=[float(el) for el in rtss[0x3006,0x0039][i_ROIContourSequence][0x3006,0x0040][i_ContourSequence][0x3006,0x0050].value]
                    new_contour_float=[old_contour[ii] if (ii-2) % 3 != 0 else original_z_pos for ii in range(len(old_contour))]
                    new_contour_str=[str(el) for el in new_contour_float]
                    rtss[0x3006,0x0039][i_ROIContourSequence][0x3006,0x0040][i_ContourSequence][0x3006,0x0050].value = new_contour_str
                    raise UserWarning("Have not verified that sorting-based SOPInstanceUID mapping works. Compare the contour locations on the slicer and original volumes to make sure.")
                if (0x3006,0x0016) in rtss[0x3006,0x0039][i_ROIContourSequence][0x3006,0x0040][i_ContourSequence]:
                    for i_ContourImageSequence in range(len(list(rtss[0x3006,0x0039][i_ROIContourSequence][0x3006,0x0040][i_ContourSequence][0x3006,0x0016]))):
        
                        # Referenced SOPInstanceUID
                        new_vol_ReferencedSOPInstanceUID=rtss[0x3006,0x0039][i_ROIContourSequence][0x3006,0x0040][i_ContourSequence][0x3006,0x0016][i_ContourImageSequence][0x0008,0x1155].value
                        original_vol_ReferencedSOPInstanceUID=new_to_original_UID_mapping_df[new_to_original_UID_mapping_df["SOPInstanceUID_New"]==new_vol_ReferencedSOPInstanceUID]["SOPInstanceUID_Original"].iloc[0]
                        rtss[0x3006,0x0039][i_ROIContourSequence][0x3006,0x0040][i_ContourSequence][0x3006,0x0016][i_ContourImageSequence][0x0008,0x1155].value=original_vol_ReferencedSOPInstanceUID
                        
                        # ReferenceSOPClassUID
                        rtss[0x3006,0x0039][i_ROIContourSequence][0x3006,0x0040][i_ContourSequence][0x3006,0x0016][i_ContourImageSequence][0x0008,0x1150].value=original_vol_attr["SOPClassUID"]
    
        pydicom.filewriter.dcmwrite(os.path.join(rtss_save_loc,"mod_"+rtss_file),rtss)
                
        return True
    
    def mapBySliceSorting(new_uids_df,original_uids_df):
        
        # order the z position of the slices in both volumes
        slicer_vol_z_list=list(new_uids_df["ImageZPosMm"])
        slicer_vol_z_list_sort=slicer_vol_z_list.copy()
        slicer_vol_z_list_sort.sort(reverse=slicer_vol_z_list[0]>slicer_vol_z_list[-1])
        
        orig_vol_z_list=list(original_uids_df["ImageZPosMm"])
        orig_vol_z_list_sort=orig_vol_z_list.copy()
        orig_vol_z_list_sort.sort(reverse=orig_vol_z_list[0]>orig_vol_z_list[-1])
        
        # check if the slices are in order based on z position:
        if all(np.array(orig_vol_z_list) == np.array(orig_vol_z_list_sort)) and all(np.array(slicer_vol_z_list) == np.array(slicer_vol_z_list_sort)):
            
            original_uids_df=original_uids_df.rename(axis=1,mapper={"ImageZPosMm":"ImageZPosMm_Original"})
            new_uids_df=new_uids_df.rename(axis=1,mapper={"ImageZPosMm":"ImageZPosMm_New"})
            
            # if the slice orders are reversed, reverse the new volume order
            if np.sign(original_uids_df["ImageZPosMm_Original"].iloc[0] - original_uids_df["ImageZPosMm_Original"].iloc[len(original_uids_df)-1]) != np.sign(new_uids_df["ImageZPosMm_New"].iloc[0] - new_uids_df["ImageZPosMm_New"].iloc[len(new_uids_df)-1]):
                new_uids_df=new_uids_df.sort_index(axis=0, ascending=False)
                new_uids_df.index=range(len(new_uids_df))
                
            mapping_df=new_uids_df[["SOPInstanceUID_New","ImageZPosMm_New"]].join(original_uids_df[["SOPInstanceUID_Original","ImageZPosMm_Original"]])
            return mapping_df
        else:
            return pd.DataFrame([])
        print("t")
    

    
    def getUIDAndZPos(self, directory):
        
        # get mapping of SOPInstanceUIDs to z position
        uids_df=pd.DataFrame()
        image_files=os.listdir(directory)
        image_files=[im_f for im_f in image_files if (".dcm" in im_f and (("rtss" not in im_f) or ("rtstruct" not in im_f)))]
    #     count=0
        for image_file in image_files:
            try:
                dcm=pydicom.dcmread(directory+"\\"+image_file)
                to_append=pd.DataFrame({"SOPInstanceUID":[dcm[0x0008,0x0018].value],"ImageZPosMm":round(float(dcm[0x0020,0x0032].value[2]),1),"SOPClassUID":[dcm[0x0008,0x0016].value],"SeriesInstanceUID":[dcm[0x0020,0x000e].value],"StudyInstanceUID":[dcm[0x0020,0x000d].value],"FileName":[image_file]})
            except:
                print("t")
            
            uids_df=uids_df.append(to_append,ignore_index=True,sort=False)
        
        attr={}
        
        # get SOPClassUID_
        SOPClassUID_set=set(uids_df["SOPClassUID"])
        assert len(SOPClassUID_set) == 1
        attr["SOPClassUID"]=SOPClassUID_set.pop()
        
        #get SeriesInstanceUID
        SeriesInstanceUID_set=set(uids_df["SeriesInstanceUID"])
        if len(SeriesInstanceUID_set) > 1:
            raise RuntimeError("!"*100 + "\nWARNING!!!!!! More than one series in dir: " + directory + "\n" + "!"*100)
        attr["SeriesInstanceUID"]=SeriesInstanceUID_set.pop()    
    
        #get StudyInstanceUID
        StudyInstanceUID_set=set(uids_df["StudyInstanceUID"])
        if len(StudyInstanceUID_set) > 1:
            raise RuntimeError("!"*100 + "\nWARNING!!!!!! More than one study in dir: " + directory + "\n" + "!"*100)
        attr["StudyInstanceUID"]=StudyInstanceUID_set.pop()    
        
        return uids_df,attr
    

        
#==================================================================================================================================
# class IOParams
#==================================================================================================================================
class IOParams():

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self):
        
        self.sImageVolumePath = ''
        self.sImageType = 'volume'
        self.bExportAllSeriesOfSequence = False
        self.sLabelMapPath = ''
        self.bRemapRTStructToVolume = False
        self.sOutputDir = ''
        self.sOriginalDicomImageDir = ''
        
    def Reset(self):
        self.sImageVolumePath = ''
        self.sImageType = 'volume'
        self.bExportAllSeriesOfSequence = False
        self.sLabelMapPath = ''
        self.bRemapRTStructToVolume = False
        self.sOutputDir = ''
        self.sOriginalDicomImageDir = ''
        
        
#==================================================================================================================================
# Run from cmd window
#==================================================================================================================================

def main(argv):
    print('Running VolumeToDicomGenerator')
    try:
        
        parser = argparse.ArgumentParser(description="VolumeToDicom postprocessor")
        parser.add_argument("-i", "--image-file", dest="input_image_file", metavar="PATH",
                            default="-", required=True, help="Path to file of input image volume")
        parser.add_argument("-t", "--image-type", dest="input_image_file_type",
                            default="volume", required=True, help="Input type of image volume: 'volume' or 'sequence' (for a 4D volume)")
        parser.add_argument("-o", "--output-folder", dest="output_folder", metavar="PATH",
                            default=".", help="Folder to save DICOM series")
        parser.add_argument("-l", "--labelmap-file", dest="input_labelmap_file", metavar="PATH",
                            default="", required=False, help="Path to file of input label map")
        parser.add_argument("-e", "--export-all-series", dest="export_all_series",
                            default=False, required=False, help="Indicate whether all series of the sequence is to be exported.")
       
        
        args = parser.parse_args(argv)
        
        if args.input_image_file == "-":
            print('Please specify input image volume file!')
        if args.input_image_file_type == "volume":
            print("Input image type currently set to 'volume' (default). Please specify 'sequence' if input image is a 4D volume")
        if args.output_folder == ".":
            print('Current directory is selected as output folder (default). To change it, please specify --output-folder')
        if args.input_labelmap_file == "-":
            print('Please specify input label map file!')

        oIOParams = IOParams()
        oIOParams.sImageVolumePath = args.input_image_file
        oIOParams.sLabelMapPath = args.input_labelmap_file
        oIOParams.sImageType = args.input_image_file_type
        oIOParams.sOutputDir = args.output_folder
        if oIOParams.sImageType == "volume":
            oIOParams.bExportAllSeriesOfSequence = False
        else:
            oIOParams.bExportAllSeriesOfSequence = bool(distutils.util.strtobool(args.export_all_series))
        

        bGUIEnabled = False     # export issued from CLI
        
        logic = VolumeToDicomGeneratorLogic(bGUIEnabled)
        logic.StartGenerator(oIOParams)
        
    except Exception as e:
        print(e)
        
    # Uncomment this for bulk runs
    # sys.exit()



if __name__ == "__main__":
    print('Exporting image and label map to DICOM ....')
    main(sys.argv[1:])