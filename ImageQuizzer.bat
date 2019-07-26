set SLICER_LAUNCHER="C:\Users\Carol\AppData\Local\NA-MIC\Slicer 4.11.0-2019-07-19\Slicer.exe"

# launch ImageQuizzer module as a slicelet
#%SLICER_LAUNCHER%  --no-main-window  --show-python-interactor --python-code "slicer.modules.imagequizzer.widgetRepresentation().show()"

# OR launch a script defining which widgets to show (as slicelets)
#%SLICER_LAUNCHER%  --no-main-window  --show-python-interactor --python-script D:\BainesWork\Slicer\SlicerProjectWeek2019\ImageQuizzerProject\ImageQuizzerStartupScript.py

# OR launch Slicer with the module showing as startup
%SLICER_LAUNCHER%   --python-code "slicer.util.selectModule('ImageQuizzer')"