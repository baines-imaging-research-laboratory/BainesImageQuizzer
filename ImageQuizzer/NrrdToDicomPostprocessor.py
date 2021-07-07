import qt, ctk, slicer
import os, sys, argparse
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


class NrrdToDicomPostprocessor(ScriptedLoadableModule):
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        parent.title = "NrrdToDicom Postprocessor"
        parent.categories = ["Baines Custom Modules"]
        parent.dependencies = ["SlicerDevelopmentToolbox"]
        parent.contributors = ["Carol Johnson (Baines Imaging Laboratories)"]
        parent.helpText = """
        This is a module to convert a Nrrd volume into a DICOM series.
        It includes the option to modify the RTStruct UID's to match the volume UID's of the original DICOM series.
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
        slicer.selfTests['NrrdToDicomPostprocessor'] = self.runTest

    def runTest(self):
        return
    

#
# mpReviewPreprocessorWidget
#

class NrrdToDicomPostprocessorWidget(ScriptedLoadableModuleWidget, ModuleWidgetMixin):

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)

        parametersCollapsibleButton = ctk.ctkCollapsibleButton()
        parametersCollapsibleButton.text = "Parameters"
        self.layout.addWidget(parametersCollapsibleButton)
    
        parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)
    
        self.inputDirButton = ctk.ctkDirectoryButton()
        parametersFormLayout.addRow("Input directory:", self.inputDirButton)
    
        self.outputDirButton = ctk.ctkDirectoryButton()
        parametersFormLayout.addRow("Output directory:", self.outputDirButton)
    
        self.copyDICOMButton = qt.QCheckBox()
        self.copyDICOMButton.setChecked(0)
        parametersFormLayout.addRow("Organize DICOMs:", self.copyDICOMButton)
    
        applyButton = qt.QPushButton('Run')
        parametersFormLayout.addRow(applyButton)
    
        applyButton.connect('clicked()', self.onRunClicked)

    def onRunClicked(self):
        logic = NrrdToDicomPostprocessorLogic()
        self.progress = self.createProgressDialog()
        self.progress.canceled.connect(lambda: logic.cancelProcess())
        logic.importAndProcessData(self.inputDirButton.directory, self.outputDirButton.directory,
                                   copyDICOM=self.copyDICOMButton.checked,
                                   progressCallback=self.updateProgressBar)
        self.progress.canceled.disconnect(lambda : logic.cancelProcess())
        self.progress.close()

    def updateProgressBar(self, **kwargs):
        ModuleWidgetMixin.updateProgressBar(self, progress=self.progress, **kwargs)



class NrrdToDicomPostprocessorLogic(ScriptedLoadableModuleLogic, ModuleLogicMixin):
    def __init__(self):
        ScriptedLoadableModuleLogic.__init__(self)

    def importAndProcessData(self, inputDir, outputDir):
        pass


def main(argv):
    print('Running NrrdToDicomPostprocessor')
    try:
        parser = argparse.ArgumentParser(description="nrrdToDicom postprocessor")
        parser.add_argument("-i", "--input-folder", dest="input_folder", metavar="PATH",
                            default="-", required=True, help="Folder of input NRRD files")
        parser.add_argument("-o", "--output-folder", dest="output_folder", metavar="PATH",
                            default=".", help="Folder to save DICOM series")
        
        
        args = parser.parse_args(argv)
        
        if args.input_folder == "-":
            print('Please specify input DICOM study folder!')
        if args.output_folder == ".":
            print('Current directory is selected as output folder (default). To change it, please specify --output-folder')
        
        logic = NrrdToDicomPostprocessorLogic()
        logic.importAndProcessData(args.input_folder, args.output_folder)
    except Exception as e:
        print(e)
        
    print('Input folder', args.input_folder)
#     sys.exit()



if __name__ == "__main__":
    print('Here we go ....')
    main(sys.argv[1:])