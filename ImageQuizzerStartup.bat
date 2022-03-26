set SCRIPT_DIR=%CD%

cd %LOCALAPPDATA%
set SLICER_LAUNCHER="NA-MIC\Slicer 4.11.20210226\Slicer.exe"


rem  OR launch a script defining which widgets to show (as slicelets)
rem %SLICER_LAUNCHER%  --no-main-window  --show-python-interactor --python-script D:\BainesWork\Slicer\SlicerProjectWeek2019\ImageQuizzerProject\ImageQuizzerStartupScript.py

rem OR launch Slicer with the module showing as startup
%SLICER_LAUNCHER%   --python-code "slicer.util.selectModule('ImageQuizzer')"

cd %SCRIPT_DIR%
call ImageQuizzerShutdown.bat
