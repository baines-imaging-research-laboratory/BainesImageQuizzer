import os
import vtk, qt, ctk, slicer
import sys
import traceback

from Utilities.UtilsMsgs import *
from Utilities.UtilsFilesIO import *

##########################################################################
#
# class UserInteraction
#
##########################################################################

class UserInteraction:
    
    def __init__(self):
        self.sClassName = type(self).__name__
        
        self.slMainWindowPos = qt.QPoint()
        
    def SetMainWindowPosition(self, qPt):
        self.slMainWindowPos = qPt
        
    def GetMainWindowPosition(self):
        return self.slMainWindowPos


    def LockLayout(self):
        ''' This function locks the Slicer layout so that the user cannot perform any of the following:
            zoom, pan, adjust slider for size of viewing windows vs quiz panel.
            
            By locking down the display, the coordinates of the viewing windows relative to the
            user's monitor, can be recorded.
            
            Other lockdown steps:
            - The setup function in the ImageQuizzerWidget class sets the mainWindow to maximized and
                toggles off visibility of the various toolbars 
            - The customEventFilter class handles when a user tries to drag the window to a new position.
        '''
        
        slicer.util.setPythonConsoleVisible(False)

        
        slMainWindow = slicer.util.mainWindow()
        self.SetMainWindowPosition(slMainWindow.pos)
        
        
        
        slicer.util.setMenuBarsVisible(False)
        slMainWindow.statusBar().setEnabled(False)
        
        
        # get monitor desktop geometry
        fDesktopWidth = slicer.app.desktop().screenGeometry().width()
        fDesktopHeight = slicer.app.desktop().screenGeometry().height()
        slMainWindow.setFixedSize(fDesktopWidth, fDesktopHeight)
        
        # set sizes for slicer's dock panel (quiz) and central widget (viewing windows) 
        slDockPanel = slMainWindow.findChildren('QDockWidget','PanelDockWidget')[0]
        
        # use 1/3 quiz to 2/3 central widget ratio
        slDockPanel.setFixedWidth(fDesktopWidth/3)
        slDockPanel.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Expanding)
#         modulePanelScrollArea = slDockPanel.findChild('QWidget', 'dockWidgetContents')
#         modulePanelScrollArea.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Expanding)
#         modulePanelScrollArea.setFixedWidth(fDesktopWidth/4)

        # use 1/5 slicer border to 4/5 central widget ratio
        slMainWindow.centralWidget().setFixedHeight(fDesktopHeight/5*4)
        
        # disable zoom and pan controls from mouse right and center buttons 
        self.lViewingWindows = ['Red','Green','Yellow','Slice4']
        for sName in self.lViewingWindows:
            slSliceWidget = slicer.app.layoutManager().sliceWidget(sName)
            if slSliceWidget != None:
                interactorStyle = slicer.app.layoutManager().sliceWidget(sName).sliceView().sliceViewInteractorStyle()
                interactorStyle.SetActionEnabled(interactorStyle.Zoom, False)
                interactorStyle.SetActionEnabled(interactorStyle.Translate, False)
                interactorStyle.SetActionEnabled(interactorStyle.SetCursorPosition, True)

        
        
        slMainWindow.showMaximized()
        
        
        
        
        
        