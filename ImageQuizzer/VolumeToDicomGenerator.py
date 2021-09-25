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
# class VolumeToDicomGeneratorWidget(ScriptedLoadableModuleWidget, ModuleWidgetMixin):
class VolumeToDicomGeneratorWidget(ScriptedLoadableModuleWidget):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        
        # initialize
        self.sInputImageType = 'volume'
        self.bExportAllSeriesOfSequence = False
        self.sLabelMapPath = ''
        self.bRemapRTStructToVolume = False

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

#         self.qVolumeBtn = qt.QRadioButton("volume")
#         self.qVolumeBtn.setChecked(True)
# #         self.qVolumeBtn.toggled.connect( self.onToggleImageTypeVolume)
#         self.qVolumeBtn.connect("clicked()", self.onToggleImageType('volume'))
#         self.qVolumeSequenceBtn = qt.QRadioButton("volume sequence (time series)")
# #         self.qVolumeSequenceBtn.toggled.connect(self.onToggleImageTypeVolumeSequence)
#         self.qVolumeSequenceBtn.connect("clicked()",self.onToggleImageType('sequence'))
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

        self.qOrigImageDirLabel = qt.QLabel("Select directory of original volume:")
        self.qOrigImageDirLabel.enabled = False
        self.originalImageDirButton = ctk.ctkDirectoryButton()
        self.originalImageDirButton.enabled = False


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
#         createRTStructButton.setStyleSheet("QPushButton{ background-color: rgb(202,150,202) }")
        createRTStructButton.setStyleSheet("QPushButton{ background-color: rgb(0,153,76) }")
#         createRTStructButton.setStyleSheet("QPushButton{ background-color: rgb(0,179,246) }")
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
        self.sImageVolumePath = inputFilePath
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
#         self.inputLabelMapFileButton.setStyleSheet("QPushButton{ background-color: rgb(0,179,246) }")
        self.sLabelMapPath = inputFilePath
        return inputFilePath
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onToggleImageType(self, sValue):
        
        self.qVolumeTypeButtons[sValue].setChecked(True)

        if sValue == 'volume':
            self.sInputImageType = 'volume'
            self.chkExportAllSeriesOfSequence.enabled = False
            self.chkExportAllSeriesOfSequence.setChecked(0)
            self.bExportAllSeriesOfSequence = False
            
        else:
            # volume sequence
            self.sInputImageType = 'sequence'
            self.chkExportAllSeriesOfSequence.enabled = True
            self.chkExportAllSeriesOfSequence.setChecked(1)
            self.bExportAllSeriesOfSequence = True
            

    
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def onToggleImageTypeVolume(self, enabled):
#         if enabled:
#             self.sInputImageType = 'volume'
#             self.chkExportAllSeriesOfSequence.enabled = False
#             self.chkExportAllSeriesOfSequence.setChecked(0)
#             self.bExportAllSeriesOfSequence = False
#             
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def onToggleImageTypeVolumeSequence(self, enabled):
#         if enabled:
#             self.sInputImageType = 'volumesequence'
#             self.chkExportAllSeriesOfSequence.enabled = True
#             self.chkExportAllSeriesOfSequence.setChecked(1)
#             self.bExportAllSeriesOfSequence = True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onToggleSeriesExport(self, enabled):
        if enabled:
            self.bExportAllSeriesOfSequence = True
        else:
            self.bExportAllSeriesOfSequence = False
            
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

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onApplyReset(self):
        slicer.mrmlScene.Clear()

        self.sImageVolumePath = ''
        self.inputImageVolumeFileButton.setText("Select file for image volume")
        self.sInputImageType = 'volume'
        self.onToggleImageType(self.lVolumeTypes[0]) # set default
        self.chkExportAllSeriesOfSequence.setChecked(0)
        self.bExportAllSeriesOfSequence = False

        self.sLabelMapPath = ''
        self.inputLabelMapFileButton.setText("Select file for label map")
        self.chkRemapRTStructUIDs.setChecked(0)
        self.bRemapRTStructToVolume = False
        
        self.outputDirButton.directory = slicer.app.temporaryPath

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @handleErrors
    def onApplyCreateDicom(self):
        
        self.msgBox = qt.QMessageBox()
        slicer.mrmlScene.Clear()

        logic = VolumeToDicomGeneratorLogic()
#         self.progress = self.createProgressDialog()
#         self.progress.canceled.connect(lambda: logic.cancelProcess())

        tupResultSuccess = logic.LoadVolumes(self.sImageVolumePath,
                                self.sInputImageType,
                                self.sLabelMapPath)


        if tupResultSuccess[0] == False:
            self.msgBox.warning(slicer.util.mainWindow(),"VolumeToDicomGenerator: WARNING",tupResultSuccess[1])
        else:
#             tupSuccessResult = logic.ExportToDicom(self.outputDirButton.directory, self.sInputImageType, self.chkExportAllSeriesOfSequence.isChecked(), progressCallback=self.updateProgressBar)
            tupResultSuccess = logic.ExportToDicom(self.outputDirButton.directory, self.sInputImageType, self.bExportAllSeriesOfSequence)
 
        if tupResultSuccess != None and tupResultSuccess[0]:
            print("Process complete")
        else:
            sMsg = 'INCOMPLETE ... DICOMs not exported.'
            self.msgBox.warning(slicer.util.mainWindow(),"VolumeToDicomGenerator: WARNING",sMsg)

#         self.progress.canceled.disconnect(lambda : logic.cancelProcess())
#         self.progress.close()

             
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def updateProgressBar(self, **kwargs):
#         ModuleWidgetMixin.updateProgressBar(self, progress=self.progress, **kwargs)



#==================================================================================================================================
# class VolumeToDicomGeneratorLogic
#==================================================================================================================================
# class VolumeToDicomGeneratorLogic(ScriptedLoadableModuleLogic, ModuleLogicMixin):
class VolumeToDicomGeneratorLogic(ScriptedLoadableModuleLogic):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self):
        ScriptedLoadableModuleLogic.__init__(self)
        self.shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        self.slLabelMapSegNodeID = None   # default
        self.msgBox = qt.QMessageBox()
        self.iExportFilesCount = 0

#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def updateProgressBar(self, **kwargs):
#         if self.progressCallback:
#             self.progressCallback(**kwargs)

#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def cancelProcess(self):
#         self.indexer.cancel()
#         self.canceled = True
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @handleErrors
    def LoadVolumes(self, sImageVolumePath, sImageType, sLabelMapPath):
        self.canceled = False
        sMsg = ''
        bSuccess = True

        try:
        
            print('Loading image volume and label map files.')
            
            logging.debug('Input image volume: %s' % sImageVolumePath)
            logging.debug('Input label map: %s' % sLabelMapPath)
            
            progressDialog = slicer.util.createProgressDialog(labelText=\
                                    'Loading volumes ...', maximum=0)
    
            # load image and label map volumes
            
            if sLabelMapPath == '':
                self.slLabelMapNode = None
            else:
                dictProperties = {'labelmap' : True, 'show': False}
                self.slLabelMapNode = slicer.util.loadLabelVolume(sLabelMapPath, dictProperties)
    
            if sImageType == 'volume':
                self.slImageNode = slicer.util.loadVolume(sImageVolumePath)
            elif sImageType == 'sequence':
                # load the multi volume file as a sequence node
                # from the sequence node, slicer creates a ScalarVolumeNode in the subject hierarchy
                # access the data node through the subject hierarchy
                slSeqNode = slicer.util.loadNodeFromFile(sImageVolumePath,'SequenceFile')
        
                slSHItemID = self.shNode.GetItemChildWithName(self.shNode.GetSceneItemID(), slSeqNode.GetName())
                self.slImageNode = self.shNode.GetItemDataNode(slSHItemID)
            else:
                bSuccess = False
                sMsg = sMsg + '\nTrouble loading image - Invalid volume type.'
                               
            progressDialog.close()
            
        except:
            sMsg = 'Trouble loading volumes ... \nThe wrong image type may have been selected.'
            bSuccess = False
            progressDialog.close()
            
        return bSuccess, sMsg

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @handleErrors
#     def ExportToDicom(self, sOutputDir, sImageType, bExport4DSeries, progressCallback=None):
    def ExportToDicom(self, sOutputDir, sImageType, bExportAllSeriesOfSequence):
        
#         self.progressCallback = progressCallback
#         self.indexer = getattr(self, "indexer", None)
#         if not self.indexer:
#             self.indexer = ctk.ctkDICOMIndexer()
        
        print("Exporting DICOMs ")
        print("          ...........  primary volume.")
        # work in subject hierarchy node (shNode)
#         shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
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

            self.msgBox.warning(slicer.util.mainWindow(),"VolumeToDicomGenerator: WARNING",sMsg)
                
        elif self.slImageNode.GetClassName() == 'vtkMRMLScalarVolumeNode':
            # use the DicomRTImportExport plugin to export scalar volume nodes
            # This can handle a label map volume if specified
            exporter = DicomRtImportExportPlugin.DicomRtImportExportPluginClass()
        else:
            sMsg = "Unrecognized volume class: " + self.slImageNode.GetClassName() + \
                    "Export will not be done."
            self.msgBox.error(slicer.util.mainWindow(),"VolumeToDicomGenerator: ERROR",sMsg)
            
        # export primary series for both volume and sequence image types (class = vtkMRMLScalarVolumeNode)
        # RTStruct is also exported here if selected by the user
        if exporter != None:
            if (self.slLabelMapNode != None):
                print("          ...........  RTStruct.")
                self.iExportFilesCount = self.iExportFilesCount + 1
            tupResultSuccess = self.PerformExport(exporter, sOutputDir)  
        

        # if the user requested exporting all series of a sequence, use
        #    DICOMVolumeSequencePlugin to export
        if sImageType == 'sequence' and bExportAllSeriesOfSequence == True:
 
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
            tupResultSuccess = self.PerformExport(exporter, sOutputDir)  

        return tupResultSuccess
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @handleErrors
    def PerformExport(self, exporter, sOutputDir):

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
                exp.directory = sOutputDir
                
            # perform export
            progressDialog = slicer.util.createProgressDialog(labelText=\
                                    'Exporting ' + str(self.iExportFilesCount) +\
                                     ' DICOM files. Be patient ...', maximum=0)

            exporter.export(exportables)
            
            progressDialog.close()
            
        except:
            sMsg = 'Trouble exporting'
            bSuccess = False
            
        return bSuccess, sMsg
       

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
                            default="-", required=False, help="Path to file of input label map")
       
        
        args = parser.parse_args(argv)
        
        if args.input_image_file == "-":
            print('Please specify input image volume file!')
        if args.input_image_file_type == "volume":
            print("Input image type currently set to 'volume' (default). Please specify 'sequence' if input image is a 4D volume")
        if args.output_folder == ".":
            print('Current directory is selected as output folder (default). To change it, please specify --output-folder')
        if args.input_labelmap_file == "-":
            print('Please specify input label map file!')
        
        logic = VolumeToDicomGeneratorLogic()
        logic.LoadVolumesAndExport(args.input_image_file, args.output_folder, args.input_labelmap_file)
    except Exception as e:
        print(e)
        
#     sys.exit()



if __name__ == "__main__":
    print('Exporting image and label map to DICOM ....')
    main(sys.argv[1:])