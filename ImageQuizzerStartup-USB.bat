set SCRIPT_DIR=%CD%

set SLICER_LAUNCHER="..\Slicer\Slicer 4.11.20210226\Slicer.exe"

%SLICER_LAUNCHER%   --python-code "slicer.util.selectModule('ImageQuizzer')"

cd /D %SCRIPT_DIR%
call ImageQuizzerShutdown.bat
