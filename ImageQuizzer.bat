rem LAPTOP Launch setup
set SLICER_LAUNCHER="C:\Users\Carol\AppData\Local\NA-MIC\Slicer 4.11.0-2019-07-15\Slicer.exe"

rem Lab PC Launch setup
rem set SLICER_LAUNCHER="C:\Users\cjohnson\AppData\Local\NA-MIC\Slicer 4.11.0\Slicer.exe"


rem CURRENTLY NOT WORKING (June 12, 2020)
rem launch ImageQuizzer module as a slicelet
rem %SLICER_LAUNCHER%  --no-main-window  --show-python-interactor --python-code "slicer.modules.imagequizzer.widgetRepresentation().show()"


rem  OR launch a script defining which widgets to show (as slicelets)
rem %SLICER_LAUNCHER%  --no-main-window  --show-python-interactor --python-script D:\BainesWork\Slicer\SlicerProjectWeek2019\ImageQuizzerProject\ImageQuizzerStartupScript.py

rem OR launch Slicer with the module showing as startup
%SLICER_LAUNCHER%   --python-code "slicer.util.selectModule('ImageQuizzer')"