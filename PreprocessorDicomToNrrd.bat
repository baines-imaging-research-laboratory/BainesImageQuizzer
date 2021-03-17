REM ############ Adjust hardcoded path to Slicer.exe and mpReviewPreprocessor.py
set SLICER_LAUNCHER="C:\Users\Carol\AppData\Local\NA-MIC\Slicer 4.11.20200930\Slicer.exe"
set PREPROCESSOR_SCRIPT=C:\Users\Carol\AppData\Roaming\NA-MIC\Extensions-29402\mpReview\lib\Slicer-4.11\qt-scripted-modules\mpReviewPreprocessor.py

REM ############ set up input / output directories for conversion
set INPUT_DICOM_DIR=K:\ImageQuizzerData\ImageVolumes\BigDataStudy
set OUTPUT_DIR=K:\ImageQuizzerData\ImageVolumes\Temp

REM ############ launch conversion script
%SLICER_LAUNCHER%  --no-main-window --show-python-interactor --python-script %PREPROCESSOR_SCRIPT% -i %INPUT_DICOM_DIR% -o %OUTPUT_DIR% 



REM ############ for debug simple case ################
REM set PREPROCESSOR_SCRIPT=D:\BainesWork\Slicer\ImageQuizzerProject\ImageQuizzer\Testing\Python\mpReviewPreprocessor_modifiedForDebug.py
REM set INPUT_DICOM_DIR=D:\BainesWork\ShareableData\SlicerData\Phantom\TinyPatientDicom
REM set OUTPUT_DIR=D:\BainesWork\ShareableData\SlicerData\Phantom

REM %SLICER_LAUNCHER%  --no-main-window --show-python-interactor --python-script %PREPROCESSOR_SCRIPT% -i %INPUT_DICOM_DIR% -o %OUTPUT_DIR% 
