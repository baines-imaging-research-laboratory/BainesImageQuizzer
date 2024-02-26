echo off

set SCRIPT_DIR=%CD%
set SLICER_EXTENSIONS_FILE="..\Slicer 4.11.20210226\NA-MIC\Slicer-29738.ini"
set SLICER_LAUNCHER="..\Slicer 4.11.20210226\Slicer.exe"

echo
echo.
echo "  >>>>>      Start Slicer module list update      <<<<<"
echo.
echo "  -----   Initial load can take up to one minute  -----  "
echo.
echo.
%SLICER_LAUNCHER%   --no-main-window  --python-script USB-Support/USB01-RunScriptShell.py %SLICER_EXTENSIONS_FILE% --show-python-interactor
echo.
echo.
echo.
echo.
echo "  >>>>>            Start Image Quizzer            <<<<<"
echo.
echo.
%SLICER_LAUNCHER%   --python-code "slicer.util.selectModule('ImageQuizzer')"

cd /D %SCRIPT_DIR%
call ImageQuizzerShutdown.bat