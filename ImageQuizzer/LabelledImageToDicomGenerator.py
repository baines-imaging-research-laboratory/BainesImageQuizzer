import qt, ctk, slicer
import os, sys, argparse, logging
import DICOMLib
from DICOMLib import DICOMUtils
from PythonQt import QtCore, QtGui
from slicer.ScriptedLoadableModule import *
from SlicerDevelopmentToolboxUtils.mixins import ModuleWidgetMixin, ModuleLogicMixin


import DicomRtImportExportPlugin
import DICOMVolumeSequencePlugin
 
import pydicom

try:
    import pandas as pd
  
    print("running with pandas")
except ImportError:
    print("!"*100, 'pandas not installed')
  
try:
    import numpy as np
    print("running with numpy")
except ImportError:
    print("!"*100, 'numpy not installed')


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
# class LabelledImageToDicomGenerator
#==================================================================================================================================
class LabelledImageToDicomGenerator(ScriptedLoadableModule):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        parent.title = "LabelledImageToDicom Generator"
        parent.categories = ["Baines Custom Modules"]
        parent.dependencies = ["SlicerDevelopmentToolbox"]
        parent.contributors = ["Carol Johnson (Baines Imaging Laboratories)"]
        parent.helpText = """
        This is a module to convert an image and its label map (contours) (.nrrd, .nii, .mhd) into a DICOM series with an RTStruct.
        It includes the option to modify an RTStruct UID's to match the volume UID's of the original DICOM series.
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
        slicer.selfTests['LabelledImageToDicomGenerator'] = self.runTest

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def runTest(self):
        return
    
#==================================================================================================================================
# class LabelledImageToDicomGeneratorWidget
#==================================================================================================================================
class LabelledImageToDicomGeneratorWidget(ScriptedLoadableModuleWidget, ModuleWidgetMixin):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        
        # initialize
        self.sInputImageType = 'volume'

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # GUI Layout
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        parametersCollapsibleButton = ctk.ctkCollapsibleButton()
        parametersCollapsibleButton.text = "Parameters to generate DICOM RTStruct"
        self.layout.addWidget(parametersCollapsibleButton)
    
        parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)
    
        self.inputImageVolumeFileButton = qt.QPushButton('Select image volume file:')
        self.inputImageVolumeFileButton.toolTip = "Select file that holds image volume."
        self.inputImageVolumeFileButton.connect('clicked(bool)', self.onSelectImageVolumeFile)
        inputLabelForImageVolume = qt.QLabel("Input image volume file:")
        parametersFormLayout.addRow(inputLabelForImageVolume, self.inputImageVolumeFileButton)

        self.inputLabelMapFileButton = qt.QPushButton('Select label map file:')
        self.inputLabelMapFileButton.toolTip = "Select file that holds the label map (contours)."
        self.inputLabelMapFileButton.connect('clicked(bool)', self.onSelectLabelMapFile)
        inputLabelForLabelMap = qt.QLabel("Input label map file (contours):")
        parametersFormLayout.addRow(inputLabelForLabelMap, self.inputLabelMapFileButton)
        
        self.qGrpBox = qt.QGroupBox()
        qGrpBoxLayout = qt.QHBoxLayout()
        self.qGrpBox.setLayout(qGrpBoxLayout)
        self.qGrpBox.setStyleSheet("QGroupBox {background-color: \
            rgb(255, 255, 255); border: 1px solid gray;\
            border-top-style:solid; border-bottom-style:solid;\
            border-left-style:solid; border-right-style:solid; }")
        self.qVolumeBtn = qt.QRadioButton("volume")
        self.qVolumeBtn.setChecked(True)
        self.qVolumeBtn.toggled.connect( self.onToggleImageTypeVolume)
        qGrpBoxLayout.addWidget(self.qVolumeBtn)
        self.qVolumeSequenceBtn = qt.QRadioButton("volume sequence (time series)")
        self.qVolumeSequenceBtn.toggled.connect(self.onToggleImageTypeVolumeSequence)
        qGrpBoxLayout.addWidget(self.qVolumeSequenceBtn)
        inputVolumeTypeLabel = qt.QLabel("Input image type:")
        parametersFormLayout.addRow(inputVolumeTypeLabel, self.qGrpBox)
         
        self.chkExportAllSeriesOfSequence = qt.QCheckBox()
        self.chkExportAllSeriesOfSequence.setChecked(0)
        self.chkExportAllSeriesOfSequence.enabled = False
        parametersFormLayout.addRow("Export all series of volume sequence:", self.chkExportAllSeriesOfSequence)
        self.chkExportAllSeriesOfSequence.toolTip = "If unchecked, only the primary series for the sequence will be exported"
    
        parametersFormLayout.addRow("  ",qt.QLabel("   "))  # adds spacing


        self.chkRemapRTStructUIDs = qt.QCheckBox()
        self.chkRemapRTStructUIDs.setChecked(0)
        self.chkRemapRTStructUIDs.toggled.connect(self.onToggleRemapBtn)
        parametersFormLayout.addRow("Remap RTStuct to original volume UIDs:", self.chkRemapRTStructUIDs)
        self.chkRemapRTStructUIDs.toolTip = "RTStruct will be remapped to match UIDs of original image volume."

        self.originalImageDirButton = ctk.ctkDirectoryButton()
        self.originalImageDirButton.enabled = False
        parametersFormLayout.addRow("Select directory of original image volume:", self.originalImageDirButton)
        
        parametersFormLayout.addRow("  ",qt.QLabel("   "))  # adds spacing

        self.outputDirButton = ctk.ctkDirectoryButton()
        parametersFormLayout.addRow("Output directory:", self.outputDirButton)
    
        parametersFormLayout.addRow("  ",qt.QLabel("   "))  # adds spacing

        createRTStructButton = qt.QPushButton('Create DICOM')
        createRTStructButton.setStyleSheet("QPushButton{ background-color: rgb(0,153,76) }")
        parametersFormLayout.addRow(createRTStructButton)
    
        createRTStructButton.connect('clicked()', self.onApplyCreateDicom)

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
        head, tail = os.path.split(inputFilePath)
        self.inputImageVolumeFileButton.setText(tail)
        self.inputImageVolumeFileButton.setStyleSheet("QPushButton{ background-color: rgb(0,179,246) }")
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
        head, tail = os.path.split(inputFilePath)
        self.inputLabelMapFileButton.setText(tail)
        self.inputLabelMapFileButton.setStyleSheet("QPushButton{ background-color: rgb(0,179,246) }")
        self.sLabelMapPath = inputFilePath
        return inputFilePath
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onToggleImageTypeVolume(self, enabled):
        if enabled:
            self.chkExportAllSeriesOfSequence.enabled = False
            self.chkExportAllSeriesOfSequence.setChecked(0)
            self.sInputImageType = 'volume'
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onToggleImageTypeVolumeSequence(self, enabled):
        if enabled:
            self.chkExportAllSeriesOfSequence.enabled = True
            self.chkExportAllSeriesOfSequence.setChecked(1)
            self.sInputImageType = 'volumesequence'
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onToggleRemapBtn(self, enabled):
        if enabled:
            self.originalImageDirButton.enabled = True
        else:
            self.originalImageDirButton.enabled = False
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @handleErrors
    def onApplyCreateDicom(self):
        
        self.msgBox = qt.QMessageBox()
        slicer.mrmlScene.Clear()

        logic = LabelledImageToDicomGeneratorLogic()
        self.progress = self.createProgressDialog()
        self.progress.canceled.connect(lambda: logic.cancelProcess())

        [bLoadSuccess, sMsg] = logic.LoadVolumesAndExport(self.sImageVolumePath,
                                self.sInputImageType,
                                self.sLabelMapPath)


        if bLoadSuccess == False:
            self.msgBox.warning(slicer.util.mainWindow(),"LabelledImageToDicomGenerator: WARNING",sMsg)
        else:
            tupSuccessResult = logic.ExportToDicom(self.outputDirButton.directory, self.sInputImageType, self.chkExportAllSeriesOfSequence.isChecked(), progressCallback=self.updateProgressBar)
 
        if tupSuccessResult[0]:
            print("Process complete")
        else:
            sMsg = 'Trouble exporting image volume and RTStruct as DICOM'
            self.msgBox.warning(slicer.util.mainWindow(),"LabelledImageToDicomGenerator: WARNING",sMsg)

        self.progress.canceled.disconnect(lambda : logic.cancelProcess())
        self.progress.close()

             
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateProgressBar(self, **kwargs):
        ModuleWidgetMixin.updateProgressBar(self, progress=self.progress, **kwargs)



#==================================================================================================================================
# class LabelledImageToDicomGeneratorLogic
#==================================================================================================================================
class LabelledImageToDicomGeneratorLogic(ScriptedLoadableModuleLogic, ModuleLogicMixin):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self):
        ScriptedLoadableModuleLogic.__init__(self)
        self.shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateProgressBar(self, **kwargs):
        if self.progressCallback:
            self.progressCallback(**kwargs)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def cancelProcess(self):
        self.indexer.cancel()
        self.canceled = True
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @handleErrors
    def LoadVolumesAndExport(self, sImageVolumePath, sImageType, sLabelMapPath):
        self.canceled = False
        sMsg = ''
        bSuccess = True
        
        print('Loading image volume and label map files.')
        
        logging.debug('Input image volume: %s' % sImageVolumePath)
        logging.debug('Input label map: %s' % sLabelMapPath)
        

        # load image and label map volumes
        
        dictProperties = {'labelmap' : True, 'show': False}
        self.slLabelMapNode = slicer.util.loadLabelVolume(sLabelMapPath, dictProperties)

        if sImageType == 'volume':
            self.slImageNode = slicer.util.loadVolume(sImageVolumePath)
        elif sImageType == 'volumesequence':
            # slicer loads the multi volume file as a sequence node
            # from the sequence node, slicer creates a ScalarVolumeNode in the subject hierarchy
            # access the data node through the subject hierarchy
            slSeqNode = slicer.util.loadNodeFromFile(sImageVolumePath,'SequenceFile')
    
            slSHItemID = self.shNode.GetItemChildWithName(self.shNode.GetSceneItemID(), slSeqNode.GetName())
            self.slImageNode = self.shNode.GetItemDataNode(slSHItemID)
        else:
            bSuccess = False
            sMsg = sMsg + '\nTrouble loading image - Invalid volume type.'
                                      
            
        return bSuccess, sMsg

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @handleErrors
    def ExportToDicom(self, sOutputDir, sImageType, bExportAllSeries, progressCallback=None):
        
        self.progressCallback = progressCallback
        self.indexer = getattr(self, "indexer", None)
        if not self.indexer:
            self.indexer = ctk.ctkDICOMIndexer()


        # for both volume and volumesequence image types, export the rtstruct with
        #    the primary image volume using DicomRtImportExportPlugin
        
        print("Exporting RTStruct and primary image volume.")
        # work in subject hierarchy node (shNode)
#         shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        self.slPrimaryVolumeID = self.shNode.GetItemByDataNode(self.slImageNode)
        
        # create subject hierarchy - new patient and study
        slNewPatientItemID = self.shNode.CreateSubjectItem(self.shNode.GetSceneItemID(), "Patient Baines1")
        slNewStudyItemID = self.shNode.CreateStudyItem(slNewPatientItemID, "Study Baines1")
        self.shNode.SetItemParent(self.slPrimaryVolumeID, slNewStudyItemID)

        # convert label map to segmentation
        slLabelMapSegNode =  slicer.mrmlScene.AddNewNodeByClass('vtkMRMLSegmentationNode')
        slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(self.slLabelMapNode, slLabelMapSegNode)
        
        # Associate segmentation node with a reference volume node
        slStudyShItem = self.shNode.GetItemParent(self.slPrimaryVolumeID)
        self.slLabelMapSegNodeID = self.shNode.GetItemByDataNode(slLabelMapSegNode)
        self.shNode.SetItemParent(self.slLabelMapSegNodeID, slStudyShItem)
        
#         # create the dicom exporter
# 
#         # DicomRtImportExportPluginClass used for volume image types
#         # if a volume sequence , use the DicomRtImportExportPluginClass to export 
#         #    the master image series with the rtstruct
#         exporter = DicomRtImportExportPlugin.DicomRtImportExportPluginClass()
#         
#         exportables = []
#         # examine volumes for export and add to export list
#         volExportable = exporter.examineForExport(slPrimaryVolumeID)
#         segExportable = exporter.examineForExport(slLabelMapSegNodeID)
#         exportables.extend(volExportable)
#         exportables.extend(segExportable)
#           
#         # assign output path to each exportable
#         for exp in exportables:
#             exp.directory = sOutputDir
#               
#           
#         # perform export for the volume sequence - all series
#         #    using DICOMVolumeSequencePlugin
#         exporter.export(exportables)
#         
#         if sImageType == 'volumesequence' and bExportAllSeries == True:
# 
#             print("Exporting time series for volume sequence image.")
#             exportables = []
#             # export the time series (rtstruct not exported here)
#             exporter = DICOMVolumeSequencePlugin.DICOMVolumeSequencePluginClass()
#             volExportable = exporter.examineForExport(slPrimaryVolumeID)
#             exportables.extend(volExportable)
#               
#             # assign output path to each exportable
#             for exp in exportables:
#                 exp.directory = sOutputDir
#             # perform export
#             exporter.export(exportables)

        # for both 'volume' and 'volumesequence' image types, use 
        #    DicomRtImportExportPlugin to export the primary image volume
        #    and the RTStruct
        exporter = DicomRtImportExportPlugin.DicomRtImportExportPluginClass()
        tupSuccessResult = self.PerformExport(exporter, sOutputDir)  

        # if the user requested exporting all series of the volume sequence, use
        #    DICOMVolumeSequencePlugin to export
        if sImageType == 'volumesequence' and bExportAllSeries == True:
 
            print("Exporting time series for volume sequence image.")
            # export the time series (rtstruct not exported here)
            self.slLabelMapSegNodeID = None
            exporter = DICOMVolumeSequencePlugin.DICOMVolumeSequencePluginClass()
            tupResult = self.PerformExport(exporter, sOutputDir)  
        bSuccess = tupSuccessResult[0]
        sMsg = tupSuccessResult[1]
        return bSuccess, sMsg
    
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
            exporter.export(exportables)
                
        except:
            sMsg = 'Trouble exporting'
            bSuccess = False
            
        return bSuccess, sMsg
       

#==================================================================================================================================
# Run from cmd window
#==================================================================================================================================

def main(argv):
    print('Running LabelledImageToDicomGenerator')
    try:
        parser = argparse.ArgumentParser(description="LabelledImageToDicom postprocessor")
        parser.add_argument("-i", "--image-file", dest="input_image_file", metavar="PATH",
                            default="-", required=True, help="Path to file of input image volume")
        parser.add_argument("-t", "--image-type", dest="input_image_file_type",
                            default="volume", required=True, help="Input type of image volume: 'volume' or 'volumesequence'")
        parser.add_argument("-o", "--output-folder", dest="output_folder", metavar="PATH",
                            default=".", help="Folder to save DICOM series")
        parser.add_argument("-l", "--labelmap-file", dest="input_labelmap_file", metavar="PATH",
                            default="-", required=True, help="Path to file of input label map")
       
        
        args = parser.parse_args(argv)
        
        if args.input_image_file == "-":
            print('Please specify input image volume file!')
        if args.input_image_file_type == "volume":
            print("Input image type currently set to 'volume' (default). Please specify 'volumesequence' if input image is a time series")
        if args.output_folder == ".":
            print('Current directory is selected as output folder (default). To change it, please specify --output-folder')
        if args.input_labelmap_file == "-":
            print('Please specify input label map file!')
        
        logic = LabelledImageToDicomGeneratorLogic()
        logic.LoadVolumesAndExport(args.input_image_file, args.output_folder, args.input_labelmap_file)
    except Exception as e:
        print(e)
        
#     sys.exit()



if __name__ == "__main__":
    print('Exporting image and label map to DICOM ....')
    main(sys.argv[1:])