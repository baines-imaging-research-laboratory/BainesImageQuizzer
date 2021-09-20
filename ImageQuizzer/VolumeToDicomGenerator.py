'''
####################################################
VolumeToDicomGenerator
####################################################
Description:

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
from SlicerDevelopmentToolboxUtils.mixins import ModuleWidgetMixin, ModuleLogicMixin


import DicomRtImportExportPlugin
import DICOMVolumeSequencePlugin
 
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
        parent.dependencies = ["SlicerDevelopmentToolbox"]
        parent.contributors = ["Carol Johnson (Baines Imaging Laboratories)"]
        parent.helpText = """
        This is a module to generate a dicom series for a specified volume (from format: .nrrd, .nii, or .mhd).
        \nIf the user defines the volume to be a 4D volume sequence, you have the option to export the primary series only or
        all time series.
        \nThe user has the option to also specify a label map file (mask for contours from format: .nrrd, .nii, or .mhd).
        The label map will be exported as an RTStruct with the dicoms of the associated image volume.
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
class VolumeToDicomGeneratorWidget(ScriptedLoadableModuleWidget, ModuleWidgetMixin):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        
        # initialize
        self.sInputImageType = 'volume'
        self.bExportAllSeries = False
        self.sLabelMapPath = ''

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # GUI Layout
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        parametersCollapsibleButton = ctk.ctkCollapsibleButton()
        parametersCollapsibleButton.text = "Parameters to generate DICOM"
        self.layout.addWidget(parametersCollapsibleButton)
    
        ######## Define Layouts
        parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)
        ## image volume box
        qInputsGroupBoxLayout = qt.QVBoxLayout()
        qInputSpecificsGrpBoxLayout = qt.QHBoxLayout()
        qVolumeTypeGrpBoxLayout = qt.QVBoxLayout()
        qExportSeriesGrpBoxLayout = qt.QVBoxLayout()
        ## label map volume box
        qLabelMapGrpBoxLayout = qt.QVBoxLayout()
        ## output directory box
        qOutputGrpBoxLayout = qt.QVBoxLayout()
        
    
        ######## Image volume details
        qInputsGroupBox = qt.QGroupBox("Image Volume Details")
        qInputsGroupBox.setLayout(qInputsGroupBoxLayout)

        self.inputImageVolumeFileButton = qt.QPushButton('Select image volume file:')
        self.inputImageVolumeFileButton.toolTip = "Select image volume file (.nrrd, .nii, .mhd)."
        self.inputImageVolumeFileButton.connect('clicked(bool)', self.onSelectImageVolumeFile)
#        inputLabelForImageVolume = qt.QLabel("Input image volume file:")
#         parametersFormLayout.addRow(inputLabelForImageVolume, self.inputImageVolumeFileButton)
        
#         parametersFormLayout.addWidget(qInputsGroupBox)

        
        qInputSpecificsGrpBox = qt.QGroupBox()
        qInputSpecificsGrpBox.setLayout(qInputSpecificsGrpBoxLayout)
        
        
        self.qVolumeTypeGrpBox = qt.QGroupBox("Image Type")
        self.qVolumeTypeGrpBox.setLayout(qVolumeTypeGrpBoxLayout)
#         self.qVolumeTypeGrpBox.setStyleSheet("QGroupBox {background-color: \
#             rgb(255, 255, 255); border: 1px solid gray;\
#             border-top-style:solid; border-bottom-style:solid;\
#             border-left-style:solid; border-right-style:solid; }")
        self.qVolumeBtn = qt.QRadioButton("volume")
        self.qVolumeBtn.setChecked(True)
        self.qVolumeBtn.toggled.connect( self.onToggleImageTypeVolume)
        qVolumeTypeGrpBoxLayout.addWidget(self.qVolumeBtn)
        self.qVolumeSequenceBtn = qt.QRadioButton("volume sequence (time series)")
        self.qVolumeSequenceBtn.toggled.connect(self.onToggleImageTypeVolumeSequence)
        qVolumeTypeGrpBoxLayout.addWidget(self.qVolumeSequenceBtn)
#         inputVolumeTypeLabel = qt.QLabel("Input image type:")
#         parametersFormLayout.addRow(inputVolumeTypeLabel, self.qGrpBox)


        self.qExportSeriesGrpBox = qt.QGroupBox("Series Export")
        self.qExportSeriesGrpBox.setLayout( qExportSeriesGrpBoxLayout)
        self.qExportSeriesGrpBox.enabled = False
                 
        self.qExportPrimaryBtn = qt.QRadioButton("primary series only")
        self.qExportPrimaryBtn.setChecked(True)
        self.qExportPrimaryBtn.toggled.connect (self.onTogglePrimarySeriesExport)
        self.qExportAllSeriesBtn = qt.QRadioButton("all time series")
        self.qExportAllSeriesBtn.setChecked(False)
        self.qExportAllSeriesBtn.toggled.connect (self.onToggleAllSeriesExport)

        
    
        # add image volume widgets to layouts
        qInputsGroupBoxLayout.addWidget(self.inputImageVolumeFileButton)
        qInputSpecificsGrpBoxLayout.addWidget(self.qVolumeTypeGrpBox)
        qInputSpecificsGrpBoxLayout.addWidget(self.qExportSeriesGrpBox)
        qExportSeriesGrpBoxLayout.addWidget(self.qExportPrimaryBtn)
        qExportSeriesGrpBoxLayout.addWidget(self.qExportAllSeriesBtn)
        qInputsGroupBoxLayout.addWidget(qInputSpecificsGrpBox)
 
        parametersFormLayout.addWidget(qInputsGroupBox)
        parametersFormLayout.addRow("  ",qt.QLabel("   "))  # adds spacing


        ######## Label map / RTStruct details
        qLabelMapGroupBox = qt.QGroupBox("Label Map Details (Optional)")
        qLabelMapGroupBox.setLayout(qLabelMapGrpBoxLayout)

        self.inputLabelMapFileButton = qt.QPushButton('Select label map file:')
        self.inputLabelMapFileButton.toolTip = "OPTIONAL: Select label map (contour mask) file (.nrrd, .nii, .mhd)."
        self.inputLabelMapFileButton.connect('clicked(bool)', self.onSelectLabelMapFile)
#         inputLabelForLabelMap = qt.QLabel("Input label map file:")
#         parametersFormLayout.addRow(inputLabelForLabelMap, self.inputLabelMapFileButton)


        self.chkRemapRTStructUIDs = qt.QCheckBox("Remap RTStuct to original volume UIDs")
        self.chkRemapRTStructUIDs.setChecked(0)
        self.chkRemapRTStructUIDs.toggled.connect(self.onToggleRemapBtn)
#         parametersFormLayout.addRow("Remap RTStuct to original volume UIDs:", self.chkRemapRTStructUIDs)
        self.chkRemapRTStructUIDs.toolTip = "RTStruct will be remapped to match UIDs of original image volume."


        self.originalImageDirButton = ctk.ctkDirectoryButton()
        self.originalImageDirButton.enabled = False
#         parametersFormLayout.addRow("Select directory of original image volume:", self.originalImageDirButton)


        qLabelMapGrpBoxLayout.addWidget(self.inputLabelMapFileButton)
        qLabelMapGrpBoxLayout.addWidget(self.chkRemapRTStructUIDs)
        qLabelMapGrpBoxLayout.addWidget(self.originalImageDirButton)

        parametersFormLayout.addWidget(qLabelMapGroupBox)
        parametersFormLayout.addRow("  ",qt.QLabel("   "))  # adds spacing

        ######## Output directory
        qOutputDirGroupBox = qt.QGroupBox('Select output directory for DICOM series:')
        qOutputDirGroupBox.setLayout(qOutputGrpBoxLayout)
        self.outputDirButton = ctk.ctkDirectoryButton()
#         parametersFormLayout.addRow("Output directory:", self.outputDirButton)
        qOutputGrpBoxLayout.addWidget(self.outputDirButton)

        parametersFormLayout.addWidget(qOutputDirGroupBox)
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
#         head, tail = os.path.split(inputFilePath)
#         self.inputImageVolumeFileButton.setText(tail)
        self.inputImageVolumeFileButton.setText(inputFilePath)
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
#         head, tail = os.path.split(inputFilePath)
#         self.inputLabelMapFileButton.setText(tail)
        self.inputLabelMapFileButton.setText(inputFilePath)
        self.inputLabelMapFileButton.setStyleSheet("QPushButton{ background-color: rgb(0,179,246) }")
        self.sLabelMapPath = inputFilePath
        return inputFilePath
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onToggleImageTypeVolume(self, enabled):
        if enabled:
#             self.chkExportAllSeriesOfSequence.enabled = False
#             self.chkExportAllSeriesOfSequence.setChecked(0)

            self.qExportSeriesGrpBox.enabled = False
            self.sInputImageType = 'volume'
            self.qExportPrimaryBtn.setChecked(True)
            self.bExportSeriesSequence = False
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onToggleImageTypeVolumeSequence(self, enabled):
        if enabled:
#             self.chkExportAllSeriesOfSequence.enabled = True
#             self.chkExportAllSeriesOfSequence.setChecked(1)

            self.qExportSeriesGrpBox.enabled = True
            self.sInputImageType = 'volumesequence'
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onTogglePrimarySeriesExport(self, enabled):
        if enabled:
            self.bExportAllSeries = False
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onToggleAllSeriesExport(self, enabled):
        if enabled:
            self.bExportAllSeries = True
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

        logic = VolumeToDicomGeneratorLogic()
        self.progress = self.createProgressDialog()
        self.progress.canceled.connect(lambda: logic.cancelProcess())

        tupResultSuccess = logic.LoadVolumesAndExport(self.sImageVolumePath,
                                self.sInputImageType,
                                self.sLabelMapPath)


        if tupResultSuccess[0] == False:
            self.msgBox.warning(slicer.util.mainWindow(),"VolumeToDicomGenerator: WARNING",tupResultSuccess[1])
        else:
#             tupSuccessResult = logic.ExportToDicom(self.outputDirButton.directory, self.sInputImageType, self.chkExportAllSeriesOfSequence.isChecked(), progressCallback=self.updateProgressBar)
            tupSuccessResult = logic.ExportToDicom(self.outputDirButton.directory, self.sInputImageType, self.chkExportAllSeriesOfSequence.isChecked())
 
        if tupSuccessResult[0]:
            print("Process complete")
        else:
            sMsg = 'Trouble exporting image volume and RTStruct as DICOM'
            self.msgBox.warning(slicer.util.mainWindow(),"VolumeToDicomGenerator: WARNING",sMsg)

        self.progress.canceled.disconnect(lambda : logic.cancelProcess())
        self.progress.close()

             
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateProgressBar(self, **kwargs):
        ModuleWidgetMixin.updateProgressBar(self, progress=self.progress, **kwargs)



#==================================================================================================================================
# class VolumeToDicomGeneratorLogic
#==================================================================================================================================
class VolumeToDicomGeneratorLogic(ScriptedLoadableModuleLogic, ModuleLogicMixin):

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
        if sLabelMapPath == '':
            self.slLabelMapNode = None
        else:
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

        if not (self.slLabelMapNode == None):
            # convert label map to segmentation
            slLabelMapSegNode =  slicer.mrmlScene.AddNewNodeByClass('vtkMRMLSegmentationNode')
            slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(self.slLabelMapNode, slLabelMapSegNode)
            
            # Associate segmentation node with a reference volume node
            slStudyShItem = self.shNode.GetItemParent(self.slPrimaryVolumeID)
            self.slLabelMapSegNodeID = self.shNode.GetItemByDataNode(slLabelMapSegNode)
            self.shNode.SetItemParent(self.slLabelMapSegNodeID, slStudyShItem)
        

            # for both 'volume' and 'volumesequence' image types, use 
            #    DicomRtImportExportPlugin to export the primary image volume
            #    and the RTStruct
            exporter = DicomRtImportExportPlugin.DicomRtImportExportPluginClass()
            tupResultSuccess = self.PerformExport(exporter, sOutputDir)  

        # if the user requested exporting all series of the volume sequence, use
        #    DICOMVolumeSequencePlugin to export
        if sImageType == 'volumesequence' and bExportAllSeries == True:
 
            print("Exporting time series for volume sequence image.")
            # export the time series (rtstruct not exported here)
            self.slLabelMapSegNodeID = None
            exporter = DICOMVolumeSequencePlugin.DICOMVolumeSequencePluginClass()
            tupResultSuccess = self.PerformExport(exporter, sOutputDir)  

        return tupResultSuccess
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
    print('Running VolumeToDicomGenerator')
    try:
        parser = argparse.ArgumentParser(description="VolumeToDicom postprocessor")
        parser.add_argument("-i", "--image-file", dest="input_image_file", metavar="PATH",
                            default="-", required=True, help="Path to file of input image volume")
        parser.add_argument("-t", "--image-type", dest="input_image_file_type",
                            default="volume", required=True, help="Input type of image volume: 'volume' or 'volumesequence'")
        parser.add_argument("-o", "--output-folder", dest="output_folder", metavar="PATH",
                            default=".", help="Folder to save DICOM series")
        parser.add_argument("-l", "--labelmap-file", dest="input_labelmap_file", metavar="PATH",
                            default="-", required=False, help="Path to file of input label map")
       
        
        args = parser.parse_args(argv)
        
        if args.input_image_file == "-":
            print('Please specify input image volume file!')
        if args.input_image_file_type == "volume":
            print("Input image type currently set to 'volume' (default). Please specify 'volumesequence' if input image is a time series")
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