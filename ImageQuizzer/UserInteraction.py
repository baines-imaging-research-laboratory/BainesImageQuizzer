import os
import vtk, qt, ctk, slicer
import sys
import traceback

from Utilities.UtilsMsgs import *
from Utilities.UtilsFilesIO import *

from enum import Enum


##########################################################################
#
# class UserInteraction
#
##########################################################################

class UserInteraction:
    
    def __init__(self):
        self.sClassName = type(self).__name__
        
        self.fh = None
        self.fhTemplate = None
        self.lViewingWindows = []
        
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
        
        # slicer.util.setPythonConsoleVisible(False)

        
        slMainWindow = slicer.util.mainWindow()
        self.SetMainWindowPosition(slMainWindow.pos)
        
        
        
        slicer.util.setMenuBarsVisible(False)
        slMainWindow.statusBar().setEnabled(False)


        # set fixed geometry maximized        
        slMainWindow.showMaximized()
        fDesktopWidth = slMainWindow.geometry.width()
        fDesktopHeight = slMainWindow.geometry.height()
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

                
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddObservers(self):
        ''' This is a function to add observers to watch for changes in the slice nodes.
            This is watching for a change in the volume - when scrolling occurs or when the 
            interactive crosshair mode causes a change in the volume slice being displayed.
        '''
        
        for sName in self.lViewingWindows:
            slSliceWidget = slicer.app.layoutManager().sliceWidget(sName)
            if slSliceWidget != None:
                slWidgetLogic = slSliceWidget.sliceLogic()
                slSliceNode = slWidgetLogic.GetSliceNode()
                slSliceNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.onModifiedSlice)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def RemoveObservers(self):
        ''' This is a function to remove observers on exit
        '''
        
        for sName in self.lViewingWindows:
            slSliceWidget = slicer.app.layoutManager().sliceWidget(sName)
            if slSliceWidget != None:
                slWidgetLogic = slSliceWidget.sliceLogic()
                slSliceNode = slWidgetLogic.GetSliceNode()
                slSliceNode.RemoveObserver(vtk.vtkCommand.ModifiedEvent)
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onModifiedSlice(self, caller, event):
        
        self.CaptureCoordinates(self.fh, self.fhTemplate,  self.lViewingWindows)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CreateUserInteractionLog(self, oSession):
        ''' Open the user interaction log
            Return the file handler for the current log.
        '''
        sDirName = oSession.oFilesIO.GetFolderNameForPageResults(oSession)
        sPageUserInteractionDir = oSession.oFilesIO.CreatePageDir(sDirName)
        
        # sUserInteractionLogPath = os.path.join(oSession.oFilesIO.GetUserQuizResultsDir(), 'UserInteraction.log')
        sUserInteractionLogPath = os.path.join(sPageUserInteractionDir, 'UserInteractionlog.csv')



        bCreatingNewFile = True
        if os.path.exists(sUserInteractionLogPath):
            bCreatingNewFile = False
            
        self.fh = open(sUserInteractionLogPath,"a")

        if bCreatingNewFile:
            # write header lines (no indents for proper csv formatting)
            self.fh.write('Time,Layout,ViewName,Location,X,Y,Height,Width,I (A-P),J (S-I),K (L-R),\
m(0-0),m(0-1),m(0-2),m(0-3),\
m(1-0),m(1-1),m(1-2),m(1-3),\
m(2-0),m(2-1),m(2-2),m(2-3),\
m(3-0),m(3-1),m(3-2),m(3-3)\n')
            self.fh.flush()
        else:
            now = datetime.now()
            sAppendBreak = str(now.strftime("%Y/%m/%d %H:%M:%S.%f")) + ',>>>>>>>>>>>>>>>>>>>>>>>>>>>\n'
            self.fh.write(sAppendBreak)
            self.fh.flush()

        # template for rows - excludes formating of matrices
        self.fhTemplate = '{}, {},\
{}, {},\
{:.4f}, {:.4f},\
{:.0f}, {:.0f},\
{:.5f}, {:.5f}, {:.5f}'

        return self.fh
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CaptureCoordinates(self, fh, fhTemplate, lViewingWindows):
        """
        Run the actual algorithm
        """
        if self.fh != None and self.fhTemplate != None:
            lsCornerLocations = ['TopLeft', 'TopRight', 'BottomLeft', 'BottomRight']
            self.lViewingWindows = lViewingWindows
            
            for sName in self.lViewingWindows:
                    slSliceWidget = slicer.app.layoutManager().sliceWidget(sName)
                    if slSliceWidget != None and slSliceWidget.visible:
                    
                        for sCorner in lsCornerLocations:
                            oLogDetails = LogDetails( sName, slSliceWidget, sCorner)
                            fh.write(fhTemplate.format(oLogDetails.sDateTime,oLogDetails.sLayoutName,  \
                                        oLogDetails.sWidgetName, oLogDetails.oCornerCoordinates.sCornerLocation,\
                                        oLogDetails.oCornerCoordinates.lScreenXY[0], oLogDetails.oCornerCoordinates.lScreenXY[1],\
                                        oLogDetails.oCornerCoordinates.iWidgetHeight, oLogDetails.oCornerCoordinates.iWidgetWidth,\
                                        oLogDetails.oCornerCoordinates.liIJK[0],oLogDetails.oCornerCoordinates.liIJK[1],oLogDetails.oCornerCoordinates.liIJK[2] ))
                            # append transformation matrix
                            for iRow in range(4):
                                for iCol in range(4):
                                    fh.write(',{:.5f}'.format(oLogDetails.oCornerCoordinates.mTransformMatrix.GetElement(iRow,iCol)))
                            # finish the line
                            fh.write('\n')
                            fh.flush()
                             
        return
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CloseInteractionLog(self, fh):
        ''' Given the currently open file handler, flush the buffer and close the log
        '''

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
        
        self.sDateTime = ''
        self.sLayoutName = ''
        self.slSliceWidget = slSliceWidget
        self.sWidgetName = sWidgetName
        self.oCornerCoordinates = CornerCoordinates(self.slSliceWidget, sCorner)
        

        now = datetime.now()
        self.sDateTime = str(now.strftime("%Y/%m/%d %H:%M:%S.%f"))
        self.sLayoutName = SlicerLayoutDescription(slicer.app.layoutManager().layout).name
        

##########################################################################
#
# class CornerCoordinates
#
##########################################################################

class CornerCoordinates():
    
    def __init__(self, slWidget, sCorner):
        
        self.sCornerLocation = sCorner
        self.oScreenXY = qt.QPoint()
        self.liIJK = [0.0,0.0,0.0]
        self.lScreenXY = [0.0,0.0]
        self.oGeometry = qt.QRect()
        self.slWidget = slWidget
        self.sWidgetCornerXYZ = [0.0,0.0,0.0]
        self.mTransformMatrix = None
        self.iWidgetHeight = 0
        self.iWidgetWidth = 0
        
        self.oUtilsMsgs = UtilsMsgs()

        
        self.GetCornerCoordinates()
        self.ConvertWidgetCornerXYZToIJK()
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetCornerCoordinates(self):
        
#         lCornerLogicCalls = (('TopLeft', self.slWidget.geometry.topLeft()),
#                              ('TopRight', self.slWidget.geometry.topRight()),
#                              ('BottomLeft', self.slWidget.geometry.bottomLeft()),
#                              ('BottomRight',self.slWidget.geometry.bottomRight()))
#         self.sCornerLocation = self.sCornerLocation

            
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
    def ConvertWidgetCornerXYZToIJK(self):
        """ Convert the XY screen coordinates into IJK values
        """
#         slCrosshairNode = slicer.util.getNode("Crosshair")
        slAppLogic = slicer.app.applicationLogic()
        
        
        try:
            # from DataProbe
#             slCrosshairNode.SetCursorPositionXYZ(lXYZ)
#             slSliceNode = slCrosshairNode.GetCursorPositionXYZ(lXYZ)


            slWidgetLogic = self.slWidget.sliceLogic()
            slSliceNode = slWidgetLogic.GetSliceNode()
            slSliceLogic = slAppLogic.GetSliceLogic(slSliceNode)
            slLayerLogic = slSliceLogic.GetBackgroundLayer()
            xyToIJK = slLayerLogic.GetXYToIJKTransform()
            self.mTransformMatrix = xyToIJK.GetConcatenatedTransform(0).GetMatrix()
            self.liIJK = xyToIJK.TransformDoublePoint(self.sWidgetCornerXYZ)

            
        except:
            #TODO:  work out displaying appropriate error message - and exit?
            sMsg = "Cannot convert widget corner XYZ to IJK"
            self.oUtilsMsgs.DisplayWarning(sMsg)
            

        
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
     
