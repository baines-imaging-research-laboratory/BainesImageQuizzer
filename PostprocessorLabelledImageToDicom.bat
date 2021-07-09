REM ############ Adjust hardcoded paths to Slicer.exe and LabelledImageToDicomGenerator.py
set SLICER_LAUNCHER="C:\Users\Carol\AppData\Local\NA-MIC\Slicer 4.11.20200930\Slicer.exe"
set POSTPROCESSOR_SCRIPT=D:\BainesWork\Slicer\ImageQuizzerProject\ImageQuizzer\LabelledImageToDicomGenerator.py

REM ############ set up input / output directories for conversion
set INPUT_IMAGE="D:\BainesWork\Slicer\ImageQuizzerProject\ImageQuizzer\ImageQuizzerData\ImageVolumes\ProstateDCE\3D DCE AX FSPGR FS T1 POST 15FLIP - as a 60 frames MultiVolume by TriggerTime.nrrd"
set OUTPUT_DIR=D:\BainesWork\Temp\DICOM
set INPUT_LABELMAP="D:\BainesWork\Slicer\ImageQuizzerProject\ImageQuizzer\ImageQuizzerData\Users\Carol\Test_PreviousY_MultipleN\Pg1_IGPC2026_Multiparametric_MRI\IGPC2026_Multiparametric_MRI_DCE-bainesquizlabel.nrrd"

REM ############ launch conversion script
%SLICER_LAUNCHER%  --no-main-window --show-python-interactor --python-script %POSTPROCESSOR_SCRIPT% -i %INPUT_IMAGE% -o %OUTPUT_DIR% -l %INPUT_LABELMAP%



REM ############ for debug simple case ################
REM set PREPROCESSOR_SCRIPT=D:\BainesWork\Slicer\ImageQuizzerProject\ImageQuizzer\Testing\Python\mpReviewPreprocessor_modifiedForDebug.py
REM set INPUT_DICOM_DIR=D:\BainesWork\ShareableData\SlicerData\Phantom\TinyPatientDicom
REM set OUTPUT_DIR=D:\BainesWork\ShareableData\SlicerData\Phantom

REM %SLICER_LAUNCHER%  --no-main-window --show-python-interactor --python-script %PREPROCESSOR_SCRIPT% -i %INPUT_DICOM_DIR% -o %OUTPUT_DIR% 

REM Following lines will start the script from the Python Interactor command line (Note the "\\" before "U" and "3")
REM sys.argv=["LabelledImageToDicomGenerator.py","-i","D:\BainesWork\Slicer\ImageQuizzerProject\ImageQuizzer\ImageQuizzerData\ImageVolumes\ProstateDCE\\3D DCE AX FSPGR FS T1 POST 15FLIP - as a 60 frames MultiVolume by TriggerTime.nrrd","-l","D:\BainesWork\Slicer\ImageQuizzerProject\ImageQuizzer\ImageQuizzerData\\Users\Carol\Test_PreviousY_MultipleN\Pg1_IGPC2026_Multiparametric_MRI\IGPC2026_Multiparametric_MRI_DCE-bainesquizlabel.nrrd","-o","D:\BainesWork\Temp\DICOM"]
REM exec(open("D:\BainesWork\Slicer\ImageQuizzerProject\ImageQuizzer\LabelledImageToDicomGenerator.py").read())