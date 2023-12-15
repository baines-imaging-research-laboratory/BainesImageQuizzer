set SCRIPT_DIR=%CD%
set SLICER_EXTENSIONS_FILE="..\Slicer 4.11.20210226\NA-MIC\Slicer-29738.ini"
set SLICER_LAUNCHER="..\Slicer 4.11.20210226\Slicer.exe"

REM >>>
REM >>>
REM >>>>>>>>>> Start extension list update 
REM >>>                        ----------  Initial load can take up to one minute  ----------
REM >>>
%SLICER_LAUNCHER%   --no-main-window  --python-script USB01-RunScriptShell.py %SLICER_EXTENSIONS_FILE% --show-python-interactor
REM >>>
REM >>>
REM >>>
REM >>>
REM >>>>>>>>>> Start Image Quizzer 
REM >>>
REM >>>
%SLICER_LAUNCHER%   --python-code "slicer.util.selectModule('ImageQuizzer')"

cd /D %SCRIPT_DIR%
call ImageQuizzerShutdown.bat