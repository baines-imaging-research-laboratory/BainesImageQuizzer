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
        
        # valid viewing windows for all of Image Quizzer layouts
        self.lViewingWindows = ['Red','Green','Yellow','Slice4']
        
        # setup observers to watch for changes in the volume slice nodes
        self.AddObservers()
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #-------------------------------------------
    #        Getters / Setters
    #-------------------------------------------
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #----------
    def SetMainWindowPosition(self, qPt):
        self.slMainWindowPos = qPt
        
    #----------
    def GetMainWindowPosition(self):
        return self.slMainWindowPos

    #----------

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #-------------------------------------------
    #        Functions
    #-------------------------------------------
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
        for sName in self.lViewingWindows:
            slSliceWidget = slicer.app.layoutManager().sliceWidget(sName)
            if slSliceWidget != None:
                interactorStyle = slicer.app.layoutManager().sliceWidget(sName).sliceView().sliceViewInteractorStyle()
                interactorStyle.SetActionEnabled(interactorStyle.Zoom, False)
                interactorStyle.SetActionEnabled(interactorStyle.Translate, False)
                interactorStyle.SetActionEnabled(interactorStyle.SetCursorPosition, True)

        
        
        slMainWindow.showMaximized()
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddObservers(self):
        ''' This is a function to add observers to watch for changes in the slice nodes.
            This is watching for a change in the volume - when scrolling occurs or when the 
            interactive crosshair mode causes a change in the volume slice being displayed.
        '''
        
                # add observers for each viewing window  
        for sName in self.lViewingWindows:
            slSliceWidget = slicer.app.layoutManager().sliceWidget(sName)
            if slSliceWidget != None:
                slWidgetLogic = slSliceWidget.sliceLogic()
                slSliceNode = slWidgetLogic.GetSliceNode()
                slSliceNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.onModifiedSlice)

        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onModifiedSlice(self, caller, event):
        self.logic.run(self.fh, self.fhTemplate, self.lViewingWindows)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CreateUserInteractionLog(self, oSession):
        ''' Open the user interaction log
        '''
        sDirName = oSession.oFilesIO.GetFolderNameForPageResults(oSession)
        sPageUserInteractionDir = oSession.oFilesIO.CreatePageDir(sDirName)
        
        # sUserInteractionLogPath = os.path.join(oSession.oFilesIO.GetUserQuizResultsDir(), 'UserInteraction.log')
        sUserInteractionLogPath = os.path.join(sPageUserInteractionDir, 'UserInteraction.log')



        bCreatingNewFile = True
        if os.path.exists(sUserInteractionLogPath):
            bCreatingNewFile = False
            
        self.fh = open(sUserInteractionLogPath,"a")

        if bCreatingNewFile:
            # write header lines
            self.fh.write('Time,Layout,ViewName,Location,X,Y,Height,Width,I (A-P),J (S-I),K (L-R),\
m(0-0),m(0-1),m(0-2),m(0-3),\
m(1-0),m(1-1),m(1-2),m(1-3),\
m(2-0),m(2-1),m(2-2),m(2-3),\
m(3-0),m(3-1),m(3-2),m(3-3)\n')
            self.fh.flush()
        else:
            self.fh.write('>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            self.fh.flush()

        return self.fh
        
        