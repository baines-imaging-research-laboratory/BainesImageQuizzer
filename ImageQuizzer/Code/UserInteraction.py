import os
import vtk, qt, ctk, slicer
import sys
import traceback
try:
    import cv2
except:
    print("OpenCV not imported. CPU time will not be recorded in User Interaction logs.")

from Utilities.UtilsMsgs import *
from Utilities.UtilsFilesIO import *

from enum import Enum


##########################################################################
#
# class UserInteraction
#
##########################################################################

class UserInteraction():
    
    def __init__(self, parent=None):
        self.sClassName = type(self).__name__
        
        self.fh = None
        self.fhTemplate = None
        self.fhInteractionLog = None
        
        self.slMainWindowPos = qt.QPoint()
        
        # valid viewing windows for all of Image Quizzer layouts
        self.lViewingWindows = ['Red','Green','Yellow','Slice4']
        self.ldictObserverIDs = {}
        
        self.oUtilsMsgs = UtilsMsgs()

        self.slMaximizedWindowPos = None   
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
    def SetFileHandlerInteractionLog(self, fh):
        self.fhInteractionLog
        
    #----------
    def GetFileHandlerInteractionLog(self):
        return self.fhInteractionLog
    
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
    def Lock_Unlock_Layout(self, oMaximizedWindowSize, bLocked):
        ''' This function locks or unlocks the Slicer layout.
        
            In the locked state, the user cannot:
                zoom, pan, adjust slider for size of viewing windows vs quiz panel.
                By locking down the display, the coordinates of the viewing windows relative to the
                user's monitor, can be recorded.
                
                Other lockdown steps:
                - The setup function in the ImageQuizzerWidget class sets the mainWindow to maximized and
                    toggles off visibility of the various toolbars 
                - The customEventFilter class handles when a user tries to drag the window to a new position.
        
            The unlocked state allows for main window resizing, slicer widget resizing and zoom and pan functionality
                
                
            The widgets that are controlled include:
                Dock panel (for quiz)
                Central widget (for image viewing windows)
                Main widget (Slicer main window)
                Python console (turned off regardless of lock state)
                Menu bar (top of Slicer platform)
                Status bar (bottom of Slicer platform)
                
                
                
        '''
        
        # >>>>> initializing
        slMainWindow = slicer.util.mainWindow()
        slDockPanel = slMainWindow.findChildren('QDockWidget','PanelDockWidget')[0]
        slicer.util.setPythonConsoleVisible(False)
#         slicer.util.setPythonConsoleVisible(True)    # for debug

        fDesktopWidth = oMaximizedWindowSize.slMainWindowWidth
        fDesktopHeight = oMaximizedWindowSize.slMainWindowHeight
        fStatusBarHeight = slMainWindow.statusBar().geometry.height()
        fNonClientAreaHeight = slMainWindow.geometry.y()       # top bar window controls for minimize, full screen and exit
        fMenuBarHeight = slMainWindow.moduleSelector().geometry.height()  # module selector is one tool  on the tool bar; use this for height

        if bLocked :
            bOpenSetting = False
        else:
            bOpenSetting = True
            
        
        # >>>>> enable / disable
        
        slicer.util.setMenuBarsVisible(bOpenSetting)
        slMainWindow.statusBar().setEnabled(bOpenSetting)
        
        # zoom and pan controls from mouse right and center buttons 
        for sName in self.lViewingWindows:
            slSliceWidget = slicer.app.layoutManager().sliceWidget(sName)
            if slSliceWidget != None:
                interactorStyle = slicer.app.layoutManager().sliceWidget(sName).sliceView().sliceViewInteractorStyle()
                interactorStyle.SetActionEnabled(interactorStyle.Zoom, bOpenSetting)
                interactorStyle.SetActionEnabled(interactorStyle.Translate, bOpenSetting)
                interactorStyle.SetActionEnabled(interactorStyle.SetCursorPosition, True)
                # reset window/level to enabled (side effect of previous actions)
                interactorStyle.GetScalarBarDisplayableManager().SetAdjustBackgroundWindowLevelEnabled(True)
                interactorStyle.GetScalarBarDisplayableManager().SetAdjustForegroundWindowLevelEnabled(True)
        
        #  window resizing (unlocked) or fix window size (locked)
        if bOpenSetting:
            slMainWindow.setMaximumSize(fDesktopWidth, fDesktopHeight)
            slMainWindow.setMinimumSize(0,0)
            
            slDockPanel.setMaximumWidth(fDesktopWidth)
            slDockPanel.setMinimumWidth(0)

            slMainWindow.centralWidget().setMaximumHeight(fDesktopHeight)
            slMainWindow.centralWidget().setMinimumHeight(0)
            
        else:
            slMainWindow.showMaximized()
            self.SetMainWindowPosition(oMaximizedWindowSize.slMainWindowPos)
            slMainWindow.setFixedSize(fDesktopWidth, fDesktopHeight)
        
            # use 1/3 quiz to 2/3 central widget ratio
            slDockPanel.setFixedWidth(fDesktopWidth/3)

            # set height = desktop height - statusbar height - menubar height - nonclient area height
            #         initial y of main window is just below 'non-client' area
            slMainWindow.centralWidget().setFixedHeight(fDesktopHeight - fStatusBarHeight - fNonClientAreaHeight - fMenuBarHeight)



                
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddObservers(self):
        ''' This is a function to add observers to watch for changes in the slice nodes.
            This is watching for a change in the volume - when scrolling occurs or when the 
            interactive crosshair mode causes a change in the volume slice being displayed.
        '''
        self.ldictObserverIDs = {}
        
        for sName in self.lViewingWindows:
            slSliceWidget = slicer.app.layoutManager().sliceWidget(sName)
            if slSliceWidget != None:
                slWidgetLogic = slSliceWidget.sliceLogic()
                slSliceNode = slWidgetLogic.GetSliceNode()
                slObserverID = slSliceNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.onModifiedSlice)
                self.ldictObserverIDs.update({sName:slObserverID})

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def RemoveObservers(self):
        ''' This is a function to remove observers on exit
        '''
        
        for sName in self.lViewingWindows:
            slSliceWidget = slicer.app.layoutManager().sliceWidget(sName)
            if slSliceWidget != None:
                slWidgetLogic = slSliceWidget.sliceLogic()
                slSliceNode = slWidgetLogic.GetSliceNode()
                if len(self.ldictObserverIDs) > 0:
                    try:
                        slSliceNode.RemoveObserver(self.ldictObserverIDs[sName])
                    except:
                        pass # there may not be an observer for the viewing window if changing layouts

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onModifiedSlice(self, caller, event):
        
        self.CaptureCoordinates(self.fh, self.fhTemplate,  self.lViewingWindows)
#         print('...Captured')
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CreateUserInteractionLog(self, oSession, sCaller=''):
        ''' Open the user interaction log
            Return the file handler for the current log.
        '''
        sDirName = oSession.oFilesIO.GetFolderNameForPageResults(oSession)
        sPageUserInteractionDir = oSession.oFilesIO.CreatePageDir(sDirName)
        
        # sUserInteractionLogPath = os.path.join(oSession.oFilesIO.GetUserQuizResultsDir(), 'UserInteraction.log')
        sUserInteractionLogPath = os.path.join(sPageUserInteractionDir, 'UserInteractionLog.csv')



        bCreatingNewFile = True
        if os.path.exists(sUserInteractionLogPath):
            bCreatingNewFile = False
        while True:
            try:    
                self.fh = open(sUserInteractionLogPath,"a")
                break
            except IOError:
                self.oUtilsMsgs.DisplayWarning("UserInteractionLog.csv file is open. Please close Excel to continue.")

        if bCreatingNewFile:
            # write header lines (no indents for proper csv formatting)
            self.fh.write('CPU Uptime,Time,Layout,ViewName,Location,\
X,Y,Height,Width,\
Image_bg,I_bg,J_bg,K_bg,\
Image_fg,I_fg,J_fg,K_fg,\
m_bg(0-0),m_bg(0-1),m_bg(0-2),m_bg(0-3),\
m_bg(1-0),m_bg(1-1),m_bg(1-2),m_bg(1-3),\
m_bg(2-0),m_bg(2-1),m_bg(2-2),m_bg(2-3),\
m_bg(3-0),m_bg(3-1),m_bg(3-2),m_bg(3-3),\
m_fg(0-0),m_fg(0-1),m_fg(0-2),m_fg(0-3),\
m_fg(1-0),m_fg(1-1),m_fg(1-2),m_fg(1-3),\
m_fg(2-0),m_fg(2-1),m_fg(2-2),m_fg(2-3),\
m_fg(3-0),m_fg(3-1),m_fg(3-2),m_fg(3-3)\n')
            self.fh.flush()
        else:
            
            self.InsertTransitionRow(self.fh, 'Re-entering Page-- ' + sCaller)

        # template for rows - excludes formating of matrices
        self.fhTemplate = '{:.0f}, {}, {}, {}, {},\
{:.4f}, {:.4f}, {:.0f}, {:.0f},\
{}, {:.5f}, {:.5f}, {:.5f},\
{}, {:.5f}, {:.5f}, {:.5f}'

        return self.fh
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CaptureCoordinates(self, fh, fhTemplate, lViewingWindows):
        """
        Create log details - which will run the algorithm to create the corner coordinates
        Write log details to log.
        """
        
        if self.fh != None and self.fhTemplate != None:
            lsCornerLocations = ['TopLeft', 'TopRight', 'BottomLeft', 'BottomRight']
            self.lViewingWindows = lViewingWindows
            
            for sName in self.lViewingWindows:
                    slSliceWidget = slicer.app.layoutManager().sliceWidget(sName)
                    if slSliceWidget != None and slSliceWidget.visible:
                    
                        for sCorner in lsCornerLocations:
                            
                            oLogDetails = LogDetails( sName, slSliceWidget, sCorner)
                            
                            fh.write(fhTemplate.format(oLogDetails.iCPUUptime, oLogDetails.sDateTime,oLogDetails.sLayoutName,  \
                                        oLogDetails.sWidgetName, oLogDetails.oCornerCoordinates.sCornerLocation, \
                                        oLogDetails.oCornerCoordinates.lScreenXY[0], oLogDetails.oCornerCoordinates.lScreenXY[1],\
                                        oLogDetails.oCornerCoordinates.iWidgetHeight, oLogDetails.oCornerCoordinates.iWidgetWidth,\
                                        oLogDetails.sImageNodeName_bg, oLogDetails.oCornerCoordinates.liIJK_bg[0],oLogDetails.oCornerCoordinates.liIJK_bg[1],oLogDetails.oCornerCoordinates.liIJK_bg[2] ,\
                                        oLogDetails.sImageNodeName_fg, oLogDetails.oCornerCoordinates.liIJK_fg[0],oLogDetails.oCornerCoordinates.liIJK_fg[1],oLogDetails.oCornerCoordinates.liIJK_fg[2] ))
                            # append transformation matrix
                            for iRow in range(4):
                                for iCol in range(4):
                                    fh.write(',{:.5f}'.format(oLogDetails.oCornerCoordinates.mTransformMatrix_bg.GetElement(iRow,iCol)))
                            for iRow in range(4):
                                for iCol in range(4):
                                    fh.write(',{:.5f}'.format(oLogDetails.oCornerCoordinates.mTransformMatrix_fg.GetElement(iRow,iCol)))
                            # finish the line
                            fh.write('\n')
                            fh.flush()
                             
        return
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def InsertTransitionRow(self, fh, sDescription=None):
        
        if sDescription == None:
            sDescription = ''
        
        try:
            self.iCPUUptime = cv2.getTickCount()
        except:
            self.iCPUUptime = 0

        
        now = datetime.now()
        sAppendBreak = str(self.iCPUUptime) + ',' \
            + str(now.strftime("%Y/%m/%d %H:%M:%S.%f")) \
            + ',>>>>>>>>>>>>>>>>>>>>>>>>>>>' \
            + sDescription + '\n'
            
        self.fh.write(sAppendBreak)
        self.fh.flush()
       
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CloseInteractionLog(self, fh, sCaller=''):
        ''' Given the currently open file handler, flush the buffer and close the log
        '''
        
        self.InsertTransitionRow(fh, 'Leaving Page --' + sCaller)

        if fh != None:
            fh.flush()
            fh.close()

    
        
##########################################################################
#
# class LogDetails
#
##########################################################################


class LogDetails():
    
    def __init__(self, sWidgetName, slSliceWidget, sCorner):
        
        self.iCPUUptime = 0
        self.sDateTime = ''
        self.sLayoutName = ''
        self.slSliceWidget = slSliceWidget
        self.sWidgetName = sWidgetName
        self.sImageNodeName_bg = ''
        self.sImageNodeName_fg = ''
        
        self.oUtilsMsgs = UtilsMsgs()
        
        try:
            self.iCPUUptime = cv2.getTickCount()
        except:
            self.iCPUUptime = 0
        
        now = datetime.now()
        self.sDateTime = str(now.strftime("%Y/%m/%d %H:%M:%S.%f"))
        self.sLayoutName = SlicerLayoutDescription(slicer.app.layoutManager().layout).name
        self.GetImageNodeName()
        self.oCornerCoordinates = CornerCoordinates(self.slSliceWidget, sCorner, self.sImageNodeName_bg, self.sImageNodeName_fg)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetImageNodeName(self):
        ''' Get image node names from the viewing window.
        '''
        try:
            slLayoutManager = slicer.app.layoutManager() 
            slSliceView = slLayoutManager.sliceWidget(self.sWidgetName).sliceView() 
    
            slSliceNode = slSliceView.mrmlSliceNode()
            slSliceLogic = slicer.app.applicationLogic().GetSliceLogic(slSliceNode) 
            slCompositeNode = slSliceLogic.GetSliceCompositeNode() 
    
            sID_bg = slCompositeNode.GetBackgroundVolumeID()
            if sID_bg != None:
                slImageNode_bg = slicer.mrmlScene.GetNodeByID(sID_bg)
                if slImageNode_bg != None:       
                    self.sImageNodeName_bg = slImageNode_bg.GetName()
    
            sID_fg = slCompositeNode.GetForegroundVolumeID() 
            if sID_fg != None:
                slImageNode_fg = slicer.mrmlScene.GetNodeByID(sID_fg)
                if slImageNode_fg != None:
                    self.sImageNodeName_fg = slImageNode_fg.GetName()

        except Exception:
            tb = traceback.format_exc()
            sMsg = 'GetImageNodeName: Failed to get image node from viewing window. \n\n' + tb
            self.oUtilsMsgs.DisplayError(sMsg)
            
                    

##########################################################################
#
# class CornerCoordinates
#
##########################################################################

class CornerCoordinates():
    
    def __init__(self, slWidget, sCorner, sImageNodeName_bg, sImageNodeName_fg):
        
        self.sCornerLocation = sCorner
        self.oScreenXY = qt.QPoint()
        self.liIJK_bg = [0.0,0.0,0.0]
        self.liIJK_fg = [0.0,0.0,0.0]
        self.lScreenXY = [0.0,0.0]
        self.oGeometry = qt.QRect()
        self.slWidget = slWidget
        self.sWidgetCornerXYZ = [0.0,0.0,0.0]
        self.mTransformMatrix_bg = vtk.vtkMatrix4x4()
        self.mTransformMatrix_fg = vtk.vtkMatrix4x4()
        self.iWidgetHeight = 0
        self.iWidgetWidth = 0
        
        self.oUtilsMsgs = UtilsMsgs()

        
        self.GetCornerCoordinates()
        self.ConvertWidgetCornerXYZToIJK(sImageNodeName_bg, sImageNodeName_fg)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetCornerCoordinates(self):
        ''' Record the X,Y positions (screen coordinates) for each corner of the 
            viewing window widget as well as the widget's height and width.
        '''
        
            
        slMainWindow = slicer.util.mainWindow()
        slCentralWidget = slMainWindow.centralWidget()
            
       
        self.lScreenXY[0] = slMainWindow.geometry.topLeft().x()\
                            + slCentralWidget.pos.x()\
                            + self.slWidget.geometry.left()
       
        
        self.lScreenXY[1] = slMainWindow.geometry.topLeft().y()\
                            + slCentralWidget.pos.y()\
                            + self.slWidget.geometry.top()
        
            
        # adjust for width and height
        
        if self.sCornerLocation == 'TopRight' or self.sCornerLocation == 'BottomRight':
            self.lScreenXY[0] = self.lScreenXY[0] + self.slWidget.geometry.width()

        
        if self.sCornerLocation == 'BottomLeft' or self.sCornerLocation == 'BottomRight':
            self.lScreenXY[1] = self.lScreenXY[1] + self.slWidget.geometry.height()


        
        # assign XYZ values for each corner - as if getting cursor positions
        #       " sliceNode = crosshairNode.GetCursorPositionXYZ(xyz) "
        #    cursor positions in the widget start with (0,0) at the bottom left corner
        # adjust by the height of the slice slider within the widget
        slSliderWidget = self.slWidget.sliceController()
        fSliderHeight = slSliderWidget.geometry.height()
        
        self.iWidgetHeight = self.slWidget.geometry.height() - int(fSliderHeight)
        self.iWidgetWidth = self.slWidget.geometry.width()
        

        if self.sCornerLocation == 'TopRight':
            self.sWidgetCornerXYZ = [self.slWidget.geometry.width(), self.slWidget.geometry.height()-fSliderHeight, 0.0]
    
        if self.sCornerLocation == 'TopLeft':
            self.sWidgetCornerXYZ = [0.0, self.slWidget.geometry.height()-fSliderHeight, 0.0]

        if self.sCornerLocation == 'BottomLeft':
            self.sWidgetCornerXYZ = [0.0, 0.0, 0.0]

        if self.sCornerLocation == 'BottomRight':
            self.sWidgetCornerXYZ = [self.slWidget.geometry.width(), 0.0, 0.0]
       
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ConvertWidgetCornerXYZToIJK(self, sImageNodeName_bg, sImageNodeName_fg):
        """ Convert the XY screen coordinates into IJK values of the volumes loaded.
        """

        slAppLogic = slicer.app.applicationLogic()
        
        try:

            slWidgetLogic = self.slWidget.sliceLogic()
            slSliceNode = slWidgetLogic.GetSliceNode()
            slSliceLogic = slAppLogic.GetSliceLogic(slSliceNode)
            
            if sImageNodeName_bg != '':
                slLayerLogic_bg = slSliceLogic.GetBackgroundLayer()
                xyToIJK_bg = slLayerLogic_bg.GetXYToIJKTransform()
                self.mTransformMatrix_bg = xyToIJK_bg.GetConcatenatedTransform(0).GetMatrix()
                self.liIJK_bg = xyToIJK_bg.TransformDoublePoint(self.sWidgetCornerXYZ)


            if sImageNodeName_fg != '':
                slLayerLogic_fg = slSliceLogic.GetForegroundLayer()
                xyToIJK_fg = slLayerLogic_fg.GetXYToIJKTransform()
                self.mTransformMatrix_fg = xyToIJK_fg.GetConcatenatedTransform(0).GetMatrix()
                self.liIJK_fg = xyToIJK_fg.TransformDoublePoint(self.sWidgetCornerXYZ)
            
        except:
            sMsg = "Cannot convert widget corner XYZ to IJK"
            self.oUtilsMsgs.DisplayError(sMsg)
            

        
##########################################################################
#
# class SlicerLayoutDescription
#
##########################################################################

class SlicerLayoutDescription(Enum):
    """ This list of viewing layouts is based on the SlicerLayout enums defined in Slicer's vtkMRMLLayoutNode.h
        It is not a complete list - but connects the names used in the ImageQuizzer with the enums in Slicer.
    """
    
    FourUpView = 3
    OneUpRedSlice = 6
    TwoOverTwoView = 27
    SideBySideView = 29
     
