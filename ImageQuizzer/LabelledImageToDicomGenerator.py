import qt, ctk, slicer
import os, sys, argparse, logging
import DICOMLib
from DICOMLib import DICOMUtils
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

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # GUI Layout
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        parametersCollapsibleButton = ctk.ctkCollapsibleButton()
        parametersCollapsibleButton.text = "Parameters to generate DICOM RTStruct"
        self.layout.addWidget(parametersCollapsibleButton)
    
        parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)
    
#         self.inputDirButton = ctk.ctkDirectoryButton()
#         parametersFormLayout.addRow("Input directory:", self.inputDirButton)

        self.inputImageVolumeFileButton = qt.QPushButton('Select image volume file:')
        self.inputImageVolumeFileButton.toolTip = "Select file that holds image volume."
#         self.inputLabelMapFileButton.setStyleSheet("QPushButton{ background-color: rgb(255,149,0) }")
        self.inputImageVolumeFileButton.connect('clicked(bool)', self.onSelectImageVolumeFile)
        inputLabelForImageVolume = qt.QLabel("Input image volume file:")
        parametersFormLayout.addRow(inputLabelForImageVolume, self.inputImageVolumeFileButton)

        self.inputLabelMapFileButton = qt.QPushButton('Select label map file:')
        self.inputLabelMapFileButton.toolTip = "Select file that holds the label map (contours)."
#         self.inputLabelMapFileButton.setStyleSheet("QPushButton{ background-color: rgb(255,149,0) }")
        self.inputLabelMapFileButton.connect('clicked(bool)', self.onSelectLabelMapFile)
        inputLabelForLabelMap = qt.QLabel("Input label map file:")
        parametersFormLayout.addRow(inputLabelForLabelMap, self.inputLabelMapFileButton)
        
    
        self.outputDirButton = ctk.ctkDirectoryButton()
        parametersFormLayout.addRow("Output directory:", self.outputDirButton)
    
#         self.copyDICOMButton = qt.QCheckBox()
#         self.copyDICOMButton.setChecked(0)
#         parametersFormLayout.addRow("Organize DICOMs:", self.copyDICOMButton)
    
        createRTStructButton = qt.QPushButton('Create RTStruct with dicom series')
        createRTStructButton.setStyleSheet("QPushButton{ background-color: rgb(0,179,246) }")
        parametersFormLayout.addRow(createRTStructButton)
    
        createRTStructButton.connect('clicked()', self.onCreateDicom)

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
    @handleErrors
    def onCreateDicom(self):
        logic = LabelledImageToDicomGeneratorLogic()
        self.progress = self.createProgressDialog()
        self.progress.canceled.connect(lambda: logic.cancelProcess())
        logic.LoadVolumesAndExport(self.sImageVolumePath,
                                self.outputDirButton.directory,
                                self.sLabelMapPath,
                                progressCallback=self.updateProgressBar)
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
    def LoadVolumesAndExport(self, sImageVolumePath, sOutputDir, sLabelMapPath, progressCallback=None):
        self.canceled = False
        
        print('Creating dicom series with RTStruct')
        
        
        self.progressCallback = progressCallback
        logging.debug('Input image volume: %s' % sImageVolumePath)
        logging.debug('Input label map: %s' % sLabelMapPath)
        self.indexer = getattr(self, "indexer", None)
        if not self.indexer:
            self.indexer = ctk.ctkDICOMIndexer()
        
        # load image and label map volumes
        self.slImageNode = slicer.util.loadVolume(sImageVolumePath)
        
        dictProperties = {'labelmap' : True, 'show': False}
        self.slLabelMapNode = slicer.util.loadLabelVolume(sLabelMapPath, dictProperties)
        
        bSuccess = self.ExportToDicom(sOutputDir)
        
        
        
        print('Process complete')


    @handleErrors
    def ExportToDicom(self, sOutputDir):
        
        # work in subject hierarchy node (shNode)
        shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        slPrimaryVolumeID = shNode.GetItemByDataNode(self.slImageNode)
        
        # convert label map to segmentation
        slLabelMapSegNode =  slicer.mrmlScene.AddNewNodeByClass('vtkMRMLSegmentationNode')
        slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(self.slLabelMapNode, slLabelMapSegNode)
        
        # create subject hierarchy - new patient and study
        slNewPatientItemID = shNode.CreateSubjectItem(shNode.GetSceneItemID(), "Patient Baines1")
        slNewStudyItemID = shNode.CreateStudyItem(slNewPatientItemID, "Study Baines1")
        shNode.SetItemParent(slPrimaryVolumeID, slNewStudyItemID)

        # Associate segmentation node with a reference volume node
        slStudyShItem = shNode.GetItemParent(slPrimaryVolumeID)
        slLabelMapSegNodeID = shNode.GetItemByDataNode(slLabelMapSegNode)
        shNode.SetItemParent(slLabelMapSegNodeID, slStudyShItem)
        
#         # create the dicom exporter
#         if oPrimaryImageNode.sImageType == 'VolumeSequence' :
#             exporter = DICOMVolumeSequencePlugin.DICOMVolumeSequencePluginClass()
#         else:
#             exporter = DicomRtImportExportPlugin.DicomRtImportExportPluginClass()

        exporter = DICOMVolumeSequencePlugin.DICOMVolumeSequencePluginClass()
         
         
        exportables = []
          
        # examine volumes for export and add to export list
        volExportable = exporter.examineForExport(slPrimaryVolumeID)
        segExportable = exporter.examineForExport(slLabelMapSegNodeID)
        exportables.extend(volExportable)
        exportables.extend(segExportable)
          
        # assign output path to each exportable
        for exp in exportables:
            exp.directory = sOutputDir
              
          
        # perform export
#         exporter.export(exportables)
        
        return True

#==================================================================================================================================
# Run from cmd window
#==================================================================================================================================

def main(argv):
    print('Running LabelledImageToDicomGenerator')
    try:
        parser = argparse.ArgumentParser(description="LabelledImageToDicom postprocessor")
        parser.add_argument("-i", "--image-file", dest="input_image_file", metavar="PATH",
                            default="-", required=True, help="Path to file of input image volume")
        parser.add_argument("-o", "--output-folder", dest="output_folder", metavar="PATH",
                            default=".", help="Folder to save DICOM series")
        parser.add_argument("-l", "--labelmap-file", dest="input_labelmap_file", metavar="PATH",
                            default="-", required=True, help="Path to file of input label map")
       
        
        args = parser.parse_args(argv)
        
        if args.input_image_file == "-":
            print('Please specify input image volume file!')
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
    print('Here we go ....')
    main(sys.argv[1:])