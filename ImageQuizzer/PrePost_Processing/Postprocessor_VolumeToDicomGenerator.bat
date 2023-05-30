REM ############ Adjust hardcoded paths to Slicer.exe and VolumeToDicomGenerator.py
set SLICER_LAUNCHER="C:\Users\Carol\AppData\Local\NA-MIC\Slicer 4.11.20200930\Slicer.exe"
set POSTPROCESSOR_SCRIPT=D:\BainesWork\Slicer\ImageQuizzerProject\ImageQuizzer\VolumeToDicomGenerator.py

REM ############ set up input / output directories for dicom generation
REM set INPUT_IMAGE="D:\BainesWork\Slicer\ImageQuizzerProject\ImageQuizzer\ImageQuizzerData\ImageVolumes\ProstateDCE\3D DCE AX FSPGR FS T1 POST 15FLIP - as a 60 frames MultiVolume by TriggerTime.nrrd"
REM set OUTPUT_DIR=D:\BainesWork\Temp\DICOM
REM set INPUT_LABELMAP="D:\BainesWork\Slicer\ImageQuizzerProject\ImageQuizzer\ImageQuizzerData\Users\Carol\Test_PreviousY_MultipleN\Pg1_IGPC2026_Multiparametric_MRI\IGPC2026_Multiparametric_MRI_DCE-bainesquizlabel.nrrd"

set IMAGE_TYPE="sequence"
set EXPORT_ALL_SERIES="FALSE"

set INPUT_IMAGE="K:\ImageQuizzerData\ImageVolumes\IGPC1010\In-Vivo Image Volumes\Raw\NiFTi\DCE.nrrd"
set OUTPUT_DIR=K:\Temp\DicomExport
set INPUT_LABELMAP="K:\ImageQuizzerData\Users\Carol\TestSequence\Pg1_IGPCxxx_DCE Contouring\IGPCxxx_DCE Contouring_DCE-bainesquizlabel.nrrd"

REM ############ launch dicom generation script
%SLICER_LAUNCHER%  --no-main-window --show-python-interactor --python-script %POSTPROCESSOR_SCRIPT% -i %INPUT_IMAGE% -t %IMAGE_TYPE% -o %OUTPUT_DIR% -l %INPUT_LABELMAP% -e %EXPORT_ALL_SERIES%



REM ############ Test 2 launches in one batch file
REM %SLICER_LAUNCHER%  --no-main-window --show-python-interactor --python-script %POSTPROCESSOR_SCRIPT% -i %INPUT_IMAGE% -t %IMAGE_TYPE% -o %OUTPUT_DIR% -e %EXPORT_ALL_SERIES%
REM set OUTPUT_DIR2=K:\Temp\DicomExport2
REM %SLICER_LAUNCHER%  --no-main-window --show-python-interactor --python-script %POSTPROCESSOR_SCRIPT% -i %INPUT_IMAGE% -t %IMAGE_TYPE% -o %OUTPUT_DIR2% -e "TRUE"


REM ############ for debug simple case ################
REM set PREPROCESSOR_SCRIPT=D:\BainesWork\Slicer\ImageQuizzerProject\ImageQuizzer\Testing\Python\mpReviewPreprocessor_modifiedForDebug.py
REM set INPUT_DICOM_DIR=D:\BainesWork\ShareableData\SlicerData\Phantom\TinyPatientDicom
REM set OUTPUT_DIR=D:\BainesWork\ShareableData\SlicerData\Phantom

REM %SLICER_LAUNCHER%  --no-main-window --show-python-interactor --python-script %PREPROCESSOR_SCRIPT% -i %INPUT_DICOM_DIR% -o %OUTPUT_DIR% -t %IMAGE_TYPE% 

REM ########### Run in Slicer Python Interactor ##############
REM Following lines will start the script from the Python Interactor command line (Note the "\\" before "U" and "3")
REM import sys
REM sys.argv=["VolumeToDicomGenerator.py","-i","D:\BainesWork\Slicer\ImageQuizzerProject\ImageQuizzer\ImageQuizzerData\ImageVolumes\ProstateDCE\\3D DCE AX FSPGR FS T1 POST 15FLIP - as a 60 frames MultiVolume by TriggerTime.nrrd","-t","sequence","-l","D:\BainesWork\Slicer\ImageQuizzerProject\ImageQuizzer\ImageQuizzerData\\Users\Carol\Test_PreviousY_MultipleN\Pg1_IGPC2026_Multiparametric_MRI\IGPC2026_Multiparametric_MRI_DCE-bainesquizlabel.nrrd","-o","D:\BainesWork\Temp\DICOM"]
REM exec(open("D:\BainesWork\Slicer\ImageQuizzerProject\ImageQuizzer\VolumeToDicomGenerator.py").read())