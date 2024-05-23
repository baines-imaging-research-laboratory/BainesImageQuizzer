# import PythonQt
import os
import vtk, qt, ctk, slicer
import sys
import unittest
import random
import traceback
from copy import deepcopy

from Utilities.UtilsIOXml import *
from Utilities.UtilsMsgs import *
from Utilities.UtilsFilesIO import *
from Utilities.UtilsEmail import *
from Utilities.UtilsValidate import *

from Question import *
from ImageView import *
from PageState import *
from UserInteraction import *
from CustomWidgets import *
from CoreWidgets import *

# import QuizzerEditorLib
# from QuizzerEditorLib import EditUtil

# from PythonQt import QtCore, QtGui

from slicer.util import EXIT_SUCCESS
from datetime import datetime


##########################################################################
#
# class Session
#
##########################################################################

class Session:
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #-------------------------------------------
    #        Session
    #-------------------------------------------
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self,  parent=None):
        self.sClassName = type(self).__name__
        self.parent = parent
        
        self._iCurrentNavigationIndex = 0
        self._l4iNavigationIndices = []

        self._loQuestionSets = []
        self._lsPreviousResponses = []
        self._lsNewResponses = []
        
        
        self._bQuizResuming = False

#         self._sSessionContourVisibility = 'Outline'
#         self._sSessionContourOpacity = 1.0

#         self._dictTabIndices = {'Quiz':0, 'ExtraTools':-1, 'SegmentEditor':-1}  #defaults
#         self._iPreviousTabIndex = 0

       
        self.oFilesIO = None
        self.oValidation = None
        self.oIOXml = UtilsIOXml()
        self.oUtilsMsgs = UtilsMsgs()
        self.oUtilsEmail = UtilsEmail()
        self.oUserInteraction = None

        self.oImageView = None
        
        self.oCustomWidgets = CustomWidgets(self.oIOXml, self.oFilesIO)
        self.oCoreWidgets = CoreWidgets(self)
        
        
        self.bNPlanesViewingMode = False
        self.sViewingMode = "Default"
        self.loCurrentQuizImageViewNodes = []
        self.liImageDisplayOrder = []
        self.lsLayoutWidgets = []

        self.setupTestEnvironment()
        

    #----------
    def __del__(self):

        # clean up of editor observers and nodes that may cause memory leaks (color table?)
        if self.GetTabIndex('SegmentEditor') > 0:
            slicer.modules.quizzereditor.widgetRepresentation().self().exit()

    #----------
    def setupTestEnvironment(self):
        # check if function is being called from unit testing
        if "testing" in os.environ:
            self.sTestMode = os.environ.get("testing")
        else:
            self.sTestMode = "0"
        
    
    #-------------------------------------------
    #        Getters / Setters
    #-------------------------------------------

    #----------
    def SetFilesIO(self, oFilesIO):
        self.oFilesIO = oFilesIO
        self.oCustomWidgets.SetFilesIO(oFilesIO)

    #----------
    def SetValidation(self, oValidation):
        self.oValidation = oValidation
        
    #----------
    def SetIOXml(self, oIOXml):
        self.oIOXml = oIOXml

    #----------
    def SetupCoreWidgets(self):
        self.oCoreWidgets.SetFilesIO(self.oFilesIO)
        self.oCoreWidgets.SetIOXml(self.oIOXml)
        self.oCoreWidgets.SetCustomWidgets(self.oCustomWidgets)
        
    #----------
    def SetNewResponses(self, lInputResponses):
        self._lsNewResponses = lInputResponses
        
    #----------
    def GetNewResponses(self):
        return self._lsNewResponses
    
    #----------
    def SetPreviousResponses(self, lInputResponses):
        self._lsPreviousResponses = lInputResponses
        
    #----------
    def GetPreviousResponses(self):
        return self._lsPreviousResponses
    
    #----------
    def SetupForUserInteraction(self, iPageIndex):
        ''' Function to define whether a page is to be set for user interaction logging.
            If logging is on - the Slicer layout is locked down otherwise, 
                window and widget resizing is enabled.
        '''
        
        
#         xPageNode = self.oCustomWidgets.GetNthPageNode(iPageIndex)
        self.oCustomWidgets.SetUserInteractionLogRequest(iPageIndex)
        
        if self.oUserInteraction == None:
            self.oUserInteraction = UserInteraction()
        
        self.oUserInteraction.Lock_Unlock_Layout(self.oMaximizedWindowSize, self.oCustomWidgets.GetUserInteractionLogRequest())
            
    #----------
    def SetInteractionLogOnOff(self, sState, sCaller=''):
        ''' Turn interaction log on:
                create new log if one doesn't exist for the page or open for append
                start the observers to watch for slice changes
                trigger event to get the initial slice position recorded
            Turn interaction log off:
                close currently open file
                turn off observers to prevent logging of slice changes during transitions 
        '''

        if self.oCustomWidgets.GetQuizComplete() == False:   
            if sState=='On':
    #             print('Log On *********')
                if self.oCustomWidgets.GetUserInteractionLogRequest():
                    self.oUserInteraction.SetFileHandlerInteractionLog(self.oUserInteraction.CreateUserInteractionLog(self, sCaller))
                    self.oUserInteraction.AddObservers()
                    slicer.mrmlScene.InvokeEvent(vtk.vtkCommand.ModifiedEvent, self.oUserInteraction.onModifiedSlice('SessionSetup','CurrentSlice'))
                
            else: 
                if self.oCustomWidgets.GetUserInteractionLogRequest():
                    self.oUserInteraction.CloseInteractionLog(self.oUserInteraction.GetFileHandlerInteractionLog(),sCaller)
                    self.oUserInteraction.RemoveObservers()

    #----------
    def SetupPageState(self, iPageIndex):
        ''' Initialize a new page state object for the page.
            Quiz specifics for the input page index are used for initializing.
        '''
        xPageNode = self.oCustomWidgets.GetNthPageNode(iPageIndex)
        self.oPageState.InitializeStates( xPageNode)

    #----------
    def GetQuestionSet(self, iIndex):
        return self._loQuestionSets[iIndex]
    
    #----------
    def ClearQuestionSetList(self):
        self._loQuestionSets = []
        
    #----------
    def AddToQuestionSetList(self, oQS):
        self._loQuestionSets.append(oQS)

    #-------------------------------------------
    #        Functions
    #-------------------------------------------
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def RunSetup(self, oFilesIO, oValidation, slicerMainLayout):
        
        sMsg = ''
        try:
            self.SetFilesIO(oFilesIO)
            self.SetupCoreWidgets()

            self.SetValidation(oValidation)
            self.oPageState = PageState(self)

            # open xml and check for root node
            bSuccess = self.oCustomWidgets.OpenQuiz(self.oFilesIO)
            
    
            if bSuccess == False:
                sMsg = "ERROR   -    Not a valid quiz - Trouble with Quiz syntax."
                raise
    
            else:
                
                self.oMaximizedWindowSize = SlicerWindowSize()

#                 self.oCustomWidgets.SetEmailResultsRequest(self.oUtilsEmail, self.oFilesIO)
                
                # >>>>>>>>>>>>>>>>> Widgets <<<<<<<<<<<<<<<<<<<<

                self.oCoreWidgets.SetupWidgets(slicerMainLayout)
                self.oCoreWidgets.oSlicerInterface.qLeftWidget.activateWindow()
                
                self.oCoreWidgets.AddExtraToolsTab()
    
                
                # turn on functionality if any page contains the attribute
                self.oCoreWidgets.AddSegmentationModule( self.oCustomWidgets.GetSegmentationModuleRequired())
                
                # set up and initialize Session attributes
                self.oFilesIO.SetupROIColorFile(self.oCustomWidgets.GetROIColorFile())
                self.oCoreWidgets.SetContourVisibilityCheckBox(self.oCustomWidgets.GetSessionContourVisibilityDefault())
                self.oCustomWidgets.SetRandomizeRequired()
                
                self.oCustomWidgets.SetupLoopingInitialization()
                self.oCustomWidgets.SetupPageGroupInitialization()
                

                # >>>>>>>>>>>>>>>>>>>>>>> Navigation and Displays <<<<<<<<<<<<<<<<
                    
                # build the list of indices page/questionset as read in by the XML 
                #    list is shuffled if randomizing is requested
                self.BuildNavigationList()
                self.InitializeImageDisplayOrderIndices(self.GetCurrentPageIndex())
                
                # check for partial or completed quiz
                self.SetNavigationIndexIfResumeRequired()
                            

                self.oCoreWidgets.progress.setMaximum(len(self.GetNavigationList()))
                self.oCoreWidgets.progress.setValue(self.GetCurrentNavigationIndex())
        
                self.SetInteractionLogOnOff('Off','Login')
                self.DisplayQuizLayout()
                self.DisplayImageLayout()
    
                
                if self.GetQuizResuming():
                    # page has been displayed - reset Quiz Resuming to false
                    self.SetQuizResuming(False)
                else:
                    self.SetupPageState(self.GetCurrentPageIndex())     # create new state object
                    
                if not self.oCustomWidgets.GetQuizComplete():
                    self.oCustomWidgets.AddSessionLoginTimestamp(self.oFilesIO)
                    self.oCustomWidgets.AddUserNameAttribute(self.oFilesIO)
                    
                    
                self.oCoreWidgets.EnableButtons()

                self.SetInteractionLogOnOff('On','Login')



        except:
            if self.GetNavigationList() == []:
                iPage = 0
            else:
                iPage = self.GetCurrentPageIndex() + 1
                
            tb = traceback.format_exc()
            sMsg = sMsg + "RunSetup: Error trying to set up the quiz. Page: " + str(iPage) \
                   + "\n\n" + tb 
            self.oUtilsMsgs.DisplayError(sMsg)
            
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def DisplayQuizLayout(self):
        
        try:
            # extract page and question set indices from the current composite index
            xNodeQuestionSet = self.oCustomWidgets.GetCurrentQuestionSetNode(\
                                    self.GetCurrentPageIndex(), self.GetCurrentQuestionSetIndex())
            oQuestionSet = QuestionSet(self)
            
            oQuestionSet.ExtractQuestionsFromXML(xNodeQuestionSet)
            
    
            # first clear any previous widgets (except push buttons)
            self.oCoreWidgets.oSlicerInterface.ClearLayout(self.oCoreWidgets.oSlicerInterface.qQuizLayout)
    

            bBuildSuccess, qWidgetQuestionSetForm = oQuestionSet.BuildQuestionSetForm()
            
            if bBuildSuccess:
                self.oCoreWidgets.slMarkupsLineWidget.setPlaceModeEnabled(True)
                self.oCoreWidgets.oSlicerInterface.qQuizLayout.addWidget(qWidgetQuestionSetForm)
                self.AddToQuestionSetList(oQuestionSet)
                qWidgetQuestionSetForm.setEnabled(True) # initialize
    
    
                self.DisplaySavedResponse()
                self.SetPreviousResponses([]) # reset for new Question Set
                
            ################################################
            ''' Enable tabs and update the progress bar.
                This is done after displaying questions and prior to loading images to provide a smooth transition
                when widgets need to be disabled.
            '''
                
            self.oCustomWidgets.SetMultipleResponseAllowed(self.GetCurrentPageIndex())
            bPageComplete = self.oCustomWidgets.GetPageCompleteAttribute(self.GetCurrentPageIndex())
            
            self.SetupForUserInteraction(self.GetCurrentPageIndex())
            self.oCoreWidgets.SetGoToBookmarkRequestButton(self.GetCurrentPageIndex())
            self.oCoreWidgets.SetEditorContourToolRadius(self.oCustomWidgets.GetContourToolRadius(self.GetCurrentPageIndex()))

    
            if self.oCustomWidgets.GetQuizComplete():
                self.oCustomWidgets.SetMultipleResponse(False) #read only
                qWidgetQuestionSetForm.setEnabled(False)
                self.oCoreWidgets.SegmentationTabEnabler(False)
                self.oCoreWidgets.EnableMarkupLinesTF(False)
            else:
                
                #enable tabs
                if self.oCustomWidgets.GetMultipleResponseAllowed() or self.GetQuizResuming() or bPageComplete == False:
                    qWidgetQuestionSetForm.setEnabled(True)
                    self.oCoreWidgets.SegmentationTabEnabler(self.oCustomWidgets.GetRequestToEnableSegmentEditorTF(self.GetCurrentPageIndex()))
                    self.oCoreWidgets.EnableMarkupLinesTF(True)
                    
                    
                else:
                    # Multiple Responses are not allowed AND this is not a Quiz Resuming state
                    sSavedResponseCompletionLevel = self.oPageState.GetSavedResponseCompletionLevel(\
                                                            self.oCustomWidgets.GetCurrentQuestionSetNode(\
                                                                        self.GetCurrentPageIndex(),
                                                                        self.GetNavigationQuestionSet(self.GetCurrentNavigationIndex())))
                    if bPageComplete:
                        qWidgetQuestionSetForm.setEnabled(False)
                        self.oCoreWidgets.SegmentationTabEnabler(False)
                        self.oCoreWidgets.EnableMarkupLinesTF(False)
                        

            ################################################
                
            # add page ID/descriptor to the progress bar
            self.sPageID = self.oCustomWidgets.GetPageID(self.GetCurrentPageIndex())
            self.sPageDescriptor = self.oCustomWidgets.GetPageDescriptor(self.GetCurrentPageIndex())
            iProgressPercent = int(self.GetCurrentNavigationIndex() / len(self.GetNavigationList()) * 100)
            self.oCoreWidgets.progress.setFormat(self.sPageID + '  ' + self.sPageDescriptor + '    ' + str(iProgressPercent) + '%')
                
        except:
            iPage = self.GetCurrentPageIndex() + 1
            tb = traceback.format_exc()
            sMsg = "Session:DisplayQuizLayout: Error trying to display questions. Page: " + str(iPage) \
                   + "\n\n" + tb 
            self.oUtilsMsgs.DisplayError(sMsg)
            
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def DisplayImageLayout(self, sCaller=None):

        try:
            self.oCoreWidgets.EnableTabBar(False)
            
            self.lsLayoutWidgets = self.oCustomWidgets.SetViewingLayout(self.GetCurrentPageIndex())
    
            # set up the images on the page
            self.oImageView = ImageView()
            self.oCoreWidgets.SetImageView(self.oImageView)
            
            self.oImageView.RunSetup(self.oCustomWidgets.GetNthPageNode(self.GetCurrentPageIndex()),\
                                      self.oFilesIO.GetDataParentDir())
            
    
            # load label maps and markup lines if a path has been stored in the xml for the images on this page
            self.oFilesIO.LoadSavedLabelMaps(self)
            self.oFilesIO.LoadSavedMarkupLines(self)

            self.oCoreWidgets.ResetExtraToolsDefaults()
    
            # assign each image node and its label map (if applicable) to the viewing widget
            self.oImageView.AssignNodesToView()
            
            if sCaller == 'ResetView':
                self.oImageView.SetNewLabelMapsVisible()
            
            self.oCoreWidgets.SetNPlanesComboBoxImageNames()
    
            self.ApplySavedImageState()
        
            self.oCoreWidgets.EnableTabBar(True)
        except:
            iPage = self.GetCurrentPageIndex() + 1
            tb = traceback.format_exc()
            sMsg = "Session:DisplayImageLayout: Error trying to display images. Page: " + str(iPage) \
                   + "\n\n" + tb 
            self.oUtilsMsgs.DisplayError(sMsg)
    

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def PerformSave(self, sCaller):
        """ Actions performed here include:
            - save the label maps (done before saving the collected quiz responses)
            - write the collected responses to the quiz results file
            - capture and write the state of the images (window/level and slice offset) to quiz results file
        """
        
        sMsg = ''
        sMissingMsg = ''
        sReturnMsg = ''
        bSaveComplete = False
        
        try:
            
            if self.oCustomWidgets.GetQuizComplete():
                bSaveComplete = True   
            
            else:
                if sCaller != 'ResetView':
                    self.oCoreWidgets.oSlicerInterface.qTabWidget.setCurrentIndex(0) # move to Quiz tab
        
        
                bLabelMapsSaved, sLabelMapMsg = self.oFilesIO.SaveLabelMaps(self, sCaller)
                self.oFilesIO.SaveMarkupLines(self)
      
                sCaptureSuccessLevel, lsNewResponses, sMsg = self.CaptureNewResponses()
                self.SetNewResponses(lsNewResponses)
                   
                if sCaller == 'NextBtn' or sCaller == 'Finish':
                    # only write to xml if all responses were captured
                    if sCaptureSuccessLevel == 'AllResponses':
                        self.SaveResponses()
                        bResponsesSaved = True
                    else:
                        sMsg = sMsg + '\n\nAll questions must be answered to proceed'
                        self.oUtilsMsgs.DisplayWarning( sMsg )
                        bResponsesSaved = False
                        sMissingMsg = ' ... missing quiz questions'
                       
                           
                else:  
                    # Caller must have been the Previous ,GoToBookmark, Exit buttons or a close (X) was 
                    #     requested (which triggers the event filter)
                    #     Capture current responses
                    #     Since this isn't the Next button, missing responses are allowed
                    bResponsesSaved = True  
                    self.SaveResponses()
                    
                    # if caller was Exit or close (X) reset the page to incomplete if there were
                    # missing pieces in order to resume on this page
                    if sLabelMapMsg != '' or sMissingMsg != '':
                        self.oSession.SetPageIncomplete(self.oSession.GetCurrentPageIndex())
                        

                if bLabelMapsSaved and bResponsesSaved:
                    bSaveComplete = True
                
                sReturnMsg = sLabelMapMsg + sMissingMsg
        
        
        except Exception:
            tb = traceback.format_exc()
            sMsg = sMsg + '\nSession:PerformSave error. Caller: ' + sCaller + '\n\n' + tb
            raise Exception(sMsg)                
    
        return bSaveComplete, sReturnMsg
                        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CaptureAndSaveImageState(self):
        ''' Save the current image state (window/level, slice number) to the quiz results file.
            This state is reset if the user revisits this page.
            Special case: User has entered a viewing mode. The widgets no
            longer hold the default list of images and orientations.
        '''

        sMsg = ''
        bSuccess = True
        bAddedNewElement = False
        
        try:
            if not self.oCustomWidgets.GetQuizComplete():
                lsDestOrientNode = []
                llsNodeProperties = []
                
                if not self.bNPlanesViewingMode:
                    # quizzer is in the default view mode - get state from assigned widgets
                    for oImageNode in self.oImageView.GetImageViewList():
                        if (oImageNode.sImageType == 'Volume' or oImageNode.sImageType == 'VolumeSequence'):
                            lsDestOrientNode = [oImageNode.sDestination, oImageNode.sOrientation, oImageNode]
                            llsNodeProperties.append(lsDestOrientNode)
                else:
                    # quizzer was in alternate viewing mode - set up the list to hold current view's orientation, destination and image node
                    for oImageNode in self.loCurrentQuizImageViewNodes:
                        
                        for i in range(len(self.oCoreWidgets.llsNPlanesOrientDest)):
                                llsNodeProperties.append([self.oCoreWidgets.llsNPlanesOrientDest[i][1], self.oCoreWidgets.llsNPlanesOrientDest[i][0], oImageNode])
                
                
                # for each image, capture the slice, window and level settings of the current mode being displayed 
                #        before changing the selection or resetting to default
                #        (eg. what was the state for the images in 1-Plane Axial view before changing to default view)
                for idx in range(len(llsNodeProperties)):
                    sWidgetName = llsNodeProperties[idx][0]
                    sOrientation = llsNodeProperties[idx][1]
                    oImageNode = llsNodeProperties[idx][2]
    
                    if (oImageNode.sImageType == 'Volume' or oImageNode.sImageType == 'VolumeSequence'):
        
                        dictAttribState = self.oImageView.GetViewState(oImageNode.slNode, sWidgetName)
                        dictViewModeAttributes = {"Orientation": sOrientation, "Destination": sWidgetName, "ViewingMode": self.sViewingMode}
                        dictAttribState.update(dictViewModeAttributes)
                        
                        if oImageNode.sImageType == 'VolumeSequence':
                            slAssociatedSequenceBrowserNode = oImageNode.GetAssociatedSequenceBrowserNode()
                            if slAssociatedSequenceBrowserNode != None:
                                sFrameNumber = str(slAssociatedSequenceBrowserNode.GetSelectedItemNumber())
                                dictFrameAttribute = {'Frame':sFrameNumber}
                                dictAttribState.update(dictFrameAttribute)
        
                        # check if xml State element exists
                        xImage = oImageNode.GetXmlImageElement()
                        # add image state element (tagged with response time)
                        self.oCustomWidgets.AddImageStateElement(xImage, dictAttribState)
                        bAddedNewElement = True     # at least one element added
                            
                if bAddedNewElement:
                    self.oCustomWidgets.SaveQuiz(self.oFilesIO.GetUserQuizResultsPath())
    
        except:
            bSuccess = False
            iPage = self.GetCurrentPageIndex() + 1
            tb = traceback.format_exc()
            sMsg = "CaptureAndSaveImageState: Error saving the image state. Current page: " + str(iPage) \
                   + "\n\n" + tb 
            self.oUtilsMsgs.DisplayError(sMsg)
            
        return bSuccess
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ApplySavedImageState(self):
        """ From the xml file, get the image state elements. 
            Based on the viewing mode, define the state orientations that need to be searched for and set.
            Check the quiz results file for the current page for state elements. If the required orientations are
            not found, search for a previously stored state for this image in the required orientation.
            (eg. if clinician set the window/level for an image on one page, and that same image is 
            loaded on a subsequent page, the same window/level should be applied.)
            
        """
        
        loImageNodes = []
        lsRequiredOrientations = []
        dictNPlanesOrientDest = {}
        dictBackgroundWidgetsToResetWithOffsets = {}
        idxCurrentPage = self.GetCurrentPageIndex()
        
        if not self.bNPlanesViewingMode:
            loImageNodes = self.oImageView.GetImageViewList()
        else:
            oImageNodeOverride, iQuizImageIndex = self.oCoreWidgets.GetNPlanesImageComboBoxSelection()
            loImageNodes.append(oImageNodeOverride)
            for i in range(len(self.oCoreWidgets.llsNPlanesOrientDest)):
                lsRequiredOrientations.append(self.oCoreWidgets.llsNPlanesOrientDest[i][0])
                dictNPlanesOrientDest.update({self.oCoreWidgets.llsNPlanesOrientDest[i][0] : self.oCoreWidgets.llsNPlanesOrientDest[i][1]})
            
        for ind in range(len(loImageNodes)):
            if self.bNPlanesViewingMode:
                oImageNode = loImageNodes[ind]
            else:
                oImageNode = loImageNodes[self.GetImageDisplayOrderIndices()[ind]]
                
            dictImageState = {}
            
            if (oImageNode.sImageType == "Volume" or oImageNode.sImageType == "VolumeSequence"):

                if self.sViewingMode == "Default":
                    lsRequiredOrientations = [oImageNode.sOrientation]
                    
                bLatestWindowLevelFound = False
                ldictAllImageStateItems =\
                    self.oCustomWidgets.GetStateElementsForMatchingImagePath(self.oFilesIO.GetRelativeDataPath(oImageNode.sImagePath), self.GetCurrentPageIndex())
    
                for sRequiredOrientation in lsRequiredOrientations:
                    bFoundOrientation = False
                    
                    for idxImageStateElement in reversed(range(len(ldictAllImageStateItems))):
                        
                        dictImageStateItems = ldictAllImageStateItems[idxImageStateElement]
                        dictImageState = self.oCustomWidgets.GetImageStateAttributes(ldictAllImageStateItems[idxImageStateElement])

                        # get first instance in the reversed search for the window/level
                        # then continue search for matching orientation to get the slice offset
                        if not bLatestWindowLevelFound:
                            sLevel = dictImageState['Level']
                            sWindow = dictImageState['Window']
                            bLatestWindowLevelFound = True


                        if dictImageState["Orientation"] == sRequiredOrientation :
                            bFoundOrientation = True
                            break
                    
                    
                    
                    # capture the destination and offset if this was a background layer for later reset to center the field of view
                    #    - this is necessary because a foreground layer for a widget may be processed
                    #      after the background layer (depending on xml order) which may change the slice offset
                    #    (This is particularly important for Background layers that have an image with
                    #     only one slice (eg. histology) )

                    # work with destination depending on the viewing mode        
                    if not self.bNPlanesViewingMode:
                        sDestination = oImageNode.sDestination
                    else:
                        sDestination = dictNPlanesOrientDest[sRequiredOrientation]
                        
                    if dictImageState != {} :

                        if oImageNode.sViewLayer == 'Background' and idxCurrentPage != int(dictImageStateItems['Page']):
                            # image state element was from a previous page
                            #    update slice offset with current page initial offset if defined
                            if oImageNode.fInitialSliceOffset != None:
                                dictBackgroundWidgetsToResetWithOffsets[sDestination] = oImageNode.fInitialSliceOffset
                            else:
                                dictBackgroundWidgetsToResetWithOffsets[sDestination] = float(dictImageState['SliceOffset'])
                        else:
                            if oImageNode.sViewLayer == 'Background' and idxCurrentPage == int(dictImageStateItems['Page']):
                                # image state element was from current page
                                #    update slice offset with saved offset
                                dictBackgroundWidgetsToResetWithOffsets[sDestination] = float(dictImageState['SliceOffset'])

                            
                            
                    if bFoundOrientation:
                        # update with most recent window/level
                        if bLatestWindowLevelFound:
                            dictImageState["Window"] = sWindow
                            dictImageState["Level"] = sLevel
                            
                        if not self.bNPlanesViewingMode:
                            oImageNode.SetImageState(dictImageState)
                        else:
                            # for NPlanes viewing mode, adjust with the destination override
                            sDestinationOverride = dictNPlanesOrientDest[sRequiredOrientation]
                            oImageNode.SetImageState(dictImageState, sDestinationOverride)
                    
                    else:
                        # no state element was found - 
                        #    capture destination and assign the offset to the initial if defined 
                        #    (will be None if not defined)
                        if oImageNode.sViewLayer == 'Background':
                            dictBackgroundWidgetsToResetWithOffsets[sDestination] = oImageNode.fInitialSliceOffset
                                            
            # first reset identified widgets to the default - fit to the background
            for key in dictBackgroundWidgetsToResetWithOffsets:
                slWidget = slicer.app.layoutManager().sliceWidget(key)
                slWidget.fitSliceToBackground() # default

            # re-adjust with captured offset
            for key in dictBackgroundWidgetsToResetWithOffsets:
                slWidget = slicer.app.layoutManager().sliceWidget(key)
                slWindowLogic = slWidget.sliceLogic()
                if dictBackgroundWidgetsToResetWithOffsets[key] != None :
                    slWindowLogic.SetSliceOffset(dictBackgroundWidgetsToResetWithOffsets[key])

        # reset field of view and origin if zoom/pan was requested
        for ind in range(len(loImageNodes)):
            if not self.bNPlanesViewingMode:
                oImageNode = loImageNodes[self.GetImageDisplayOrderIndices()[ind]]
                oImageNode.SetFieldOfViewAndOrigin()
            else:
                oImageNode = loImageNodes[0]
                oImageNode.SetFieldOfViewAndOrigin('Red')

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def DisplayCurrentResponsesOnResetView(self, lsCurrentResponses):

        indQSet = self.GetCurrentQuestionSetIndex()
 
        oQuestionSet = self.GetQuestionSet(indQSet)
        loQuestions = oQuestionSet.GetQuestionList()
         
        for indQuestion in range(len(loQuestions)):
            oQuestion = loQuestions[indQuestion]
            oQuestion.PopulateQuestionWithResponses(lsCurrentResponses[indQuestion])

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def DisplaySavedResponse(self):
        
        oQuestionSet = self.GetQuestionSet(self.GetCurrentQuestionSetIndex())
        loQuestions = oQuestionSet.GetQuestionList()
          
        # for each question and each option, extract any existing responses from the XML
          
        lsAllResponsesForQuestions = []
        for indQuestion in range(len(loQuestions)):
            oQuestion = loQuestions[indQuestion]
            xQuestionNode = self.oCustomWidgets.GetCurrentQuestionNode(\
                                            self.GetCurrentPageIndex(),\
                                            self.GetCurrentQuestionSetIndex(), indQuestion)
                  
            lsResponseValues = self.oCustomWidgets.GetSavedResponses(xQuestionNode)
            
                 
            oQuestion.PopulateQuestionWithResponses(lsResponseValues)
 
            # only InfoBox type of question can have all responses equal to null string
            if self.oCustomWidgets.GetQuestionType(xQuestionNode) != "InfoBox" \
                    and (all(elem == '' for elem in lsResponseValues)):
                lsResponseValues = []   # reset if all are empty
 
            lsAllResponsesForQuestions.append(lsResponseValues)
             
     
            lsResponseValues = []  # clear for next set of options 
 
        self.SetPreviousResponses(lsAllResponsesForQuestions)
     
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CaptureNewResponses(self):
        ''' When moving to another display of Images and QuestionSet (from pressing Next or Previous)
            the new responses that were entered must be captured ready to do the save to XML.
            A check for any missing responses to the questions is done and passed back to the calling function.
        '''
        
        # sMsg may be set in Question class function to capture the response
        sMsg = ''
        sAllMsgs = ''
        
        # get list of questions from current question set
        indQSet = self.GetCurrentQuestionSetIndex()
        oQuestionSet = self.GetQuestionSet(indQSet)
        loQuestions = oQuestionSet.GetQuestionList()
            
        lsAllResponses = []
        lsResponsesForOptions = []
        iNumMissingResponses = 0
        
        for indQuestion in range(len(loQuestions)):
            oQuestion = loQuestions[indQuestion]
            bResponseCaptured = False
            
            bResponseCaptured, lsResponsesForOptions, sMsg = oQuestion.CaptureResponse()


            # append all captured lists - even if it was empty (partial responses)
            lsAllResponses.append(lsResponsesForOptions)
            
            # string together all missing response messages
            if sMsg != '':
                if sAllMsgs == '':
                    sAllMsgs = sMsg
                else:
                    sAllMsgs = sAllMsgs + '\n' + sMsg 
            
            # keep track if a question was missed
            if bResponseCaptured == False:
                iNumMissingResponses = iNumMissingResponses + 1
                
        # define success level
        sCaptureSuccessLevel = self.oPageState.CategorizeResponseCompletionLevel(len(loQuestions), len(loQuestions)-iNumMissingResponses)
                
        return sCaptureSuccessLevel, lsAllResponses, sAllMsgs
       
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SaveResponses(self):
        """ Write captured responses to results file. If this is the first write to the results file
            with responses, the login timestamp is also added.
            After responses are added, record the image state in the results file.
        """
         
        try:
            '''
                only allow for writing of responses under certain conditions
                    - allow if the question set is marked for multiple responses allowed
                    - OR allow if the number of questions with responses already 
                      recorded is 'NoResponses' or 'PartialResponses' (not 'AllResponses')
                    - OR allow if the current Page has not been marked as complete 
                      indicating that there are multiple question sets and Prev or Next was
                      used to move between them or user has pressed 'Exit'
            '''
             
            # get from xml, the category of saved recorded responses to 
            #    determine whether the newly captured responses are to be written
            sQuestionsWithRecordedResponses = self.oPageState.GetSavedResponseCompletionLevel(\
                                                    self.oCustomWidgets.GetCurrentQuestionSetNode(\
                                                        self.GetCurrentPageIndex(), self.GetCurrentQuestionSetIndex()))
             
 
            if ( self.oCustomWidgets.GetMultipleResponseAllowed() == True)  or \
                ((self.oCustomWidgets.GetMultipleResponseAllowed() == False) and (sQuestionsWithRecordedResponses != 'AllResponses') ) or \
                ((self.oCustomWidgets.GetMultipleResponseAllowed() == False) and (self.oCustomWidgets.GetPageCompleteAttribute(self.GetCurrentNavigationIndex()) == False) ):
 
                # check to see if the responses for the question set match 
                #    what was previously captured
                #    -only write responses if they have changed
                if not self.GetNewResponses() == self.GetPreviousResponses():
                         
                    self.oCustomWidgets.WriteResponses(self.GetCurrentPageIndex(), self.GetCurrentQuestionSetIndex(), self.GetNewResponses())
                     
                    # potential exit of quiz - update logout time with each write
                    self.oCustomWidgets.UpdateSessionLogoutTimestamp()
                     
                    self.oCustomWidgets.SaveQuiz(self.oFilesIO.GetUserQuizResultsPath())
                     
         
        except Exception:
            tb = traceback.format_exc()
            sMsg = 'Error writing responses to results file' + '\n Does this file exist? : \n' \
                + self.oFilesIO.GetUserQuizResultsPath()\
                + '\n\n' + tb
            # critical error - exit
            self.oUtilsMsgs.DisplayError( sMsg )
             
        return 
     
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def UpdateCompletions(self, sCaller):
        ''' Function that first updates the completion lists based on the requirements for the
            page. When moving to the next page (not a previous or a bookmarked page or an exit), 
            the function will then update the flags that determine whether it is okay to 
            progress with the quiz.
            
            The QuizComplete attribute is only set to "Y" if the user presses the 'Finish' button
            on the last page. (Pressing the 'Exit' button on this page does not set this flag.)
            
        '''
        ################################################
        ##########  Updating completion flags ##########        
        ################################################

        sReturnMsg = ''
        bPageStateComplete = True
        idxQuestionSet = self.GetCurrentQuestionSetIndex()
        iNumQSets = len(self.oCustomWidgets.GetAllQuestionSetNodesForCurrentPage(self.GetCurrentPageIndex()))

        
        # update current state in lists of requirements
        self.oPageState.UpdateCompletionLists(self.oCustomWidgets.GetNthPageNode(self.GetCurrentPageIndex()))
        
        
        if sCaller == 'NextBtn' or sCaller == 'Finish':
            
            # if this was the last question set for the page, check for completion
            if idxQuestionSet == iNumQSets - 1:
                
                sCompletionFlagMsg = self.oPageState.UpdateCompletedFlags(self.oCustomWidgets.GetNthPageNode(self.GetCurrentPageIndex()))
#                 sMsg = sMsg + sCompletionFlagMsg
                
                if self.oPageState.GetPageCompletedTF():
                    bPageStateComplete = True
                    self.oCustomWidgets.AddPageCompleteAttribute(self.GetCurrentPageIndex())
                    
                    if sCaller == 'Finish':
                        self.oCustomWidgets.AddQuizCompleteAttribute()
                        self.oCustomWidgets.SetQuizComplete(True)
    
                else:
                    bPageStateComplete = False
                    self.oUtilsMsgs.DisplayWarning( sCompletionFlagMsg )
                    sReturnMsg = ' ... missing requirement for Page (contours / markuplines / questions) '
                        

        else:      # for 'Previous' 'GoToBookmark' 'Exit'
            bPageStateComplete = True    # allow with unfinished requirements
            
                
                
                
                                    
        return bPageStateComplete, sReturnMsg
    

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ExitOnQuizComplete(self):
        """ the last index in the composite navigation indices list was reached
            the quiz was completed - exit
        """
        self.QueryThenSendEmailResults()
        self.oUtilsMsgs.DisplayInfo('Quiz Complete - Exiting')
        slicer.util.exit(status=EXIT_SUCCESS)
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def QueryThenSendEmailResults(self):
        
        if self.oCustomWidgets.GetEmailResultsRequest(self.oUtilsEmail, self.oFilesIO) and self.oCustomWidgets.GetQuizComplete():
            sMsg = 'Ready to email results?'
            qtEmailAns = self.oUtilsMsgs.DisplayYesNo(sMsg)
    
            if qtEmailAns == qt.QMessageBox.Yes:
    
                sArchiveFilenameWithPath = os.path.join(self.oFilesIO.GetUserDir(), self.oFilesIO.GetQuizFilenameNoExt())
                sPathToZipFile = self.oCustomWidgets.GetXmlUtils().ZipXml(sArchiveFilenameWithPath, self.oFilesIO.GetUserQuizResultsDir())
                
                if sPathToZipFile != '':
                    self.oUtilsEmail.SendEmail(sPathToZipFile)
                else:
                    sMsg = 'Trouble archiving quiz results: ' + sPathToZipFile
                    self.oUtilsMsgs.DisplayError(sMsg)
        
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #-------------------------------------------
    #        Quiz navigation
    #-------------------------------------------
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #-------------------------------------------
    #        Getters / Setters
    #-------------------------------------------
    
    #----------
    def SetQuizResuming(self, bInput):
        self._bQuizResuming = bInput
        
    #----------
    def GetQuizResuming(self):
        return self._bQuizResuming
            
    #----------
    def GetNavigationList(self):
        return self._l4iNavigationIndices

    #----------
    def SetNavigationList(self, lIndices):
        self._l4iNavigationIndices = lIndices
        
    #----------
    def ClearNavigationList(self):
        self._l4iNavigationIndices = []
        
    #----------
    def GetCurrentNavigationIndex(self):
        return self._iCurrentNavigationIndex
    
    #----------
    def SetCurrentNavigationIndex(self, iInd):
        self._iCurrentNavigationIndex = iInd
        
    #----------
    def GetCurrentPageIndex(self):
        return self.GetNavigationPage(self.GetCurrentNavigationIndex())
    
    #----------
    def GetCurrentQuestionSetIndex(self):
        return self.GetNavigationQuestionSet(self.GetCurrentNavigationIndex())
    
    #----------
    def GetNavigationPage(self, iNavInd):
        return self._l4iNavigationIndices[iNavInd][0]
    
    #----------
    def GetNavigationQuestionSet(self, iNavInd):
        return self._l4iNavigationIndices[iNavInd][1]
    
    #----------
    def GetNavigationPageGroup(self, iNavInd):
        return self._l4iNavigationIndices[iNavInd][2]
    
    #----------
    def GetNavigationRepNum(self, iNavInd):
        return self._l4iNavigationIndices[iNavInd][3]
    
    #----------
    def GetNavigationIndicesAtIndex(self, iNavInd):
        return self._l4iNavigationIndices[iNavInd]
        
    #----------
    def NavigationListAppend(self, lNavIndices):
        self._l4iNavigationIndices.append(lNavIndices)
    
    #----------
    def NavigationListInsertBeforeIndex(self, iNavInd, lNavIndices):
        self._l4iNavigationIndices.insert(iNavInd, lNavIndices)
    
    #----------
    def GetImageDisplayOrderIndices(self):
        return self.liImageDisplayOrder
    
    
    
    

    #-------------------------------------------
    #        Functions
    #-------------------------------------------

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def BuildNavigationList(self):
        ''' This function sets up the page and question set indices which
            are used to coordinate the next and previous buttons.
            The information is gathered by querying the XML quiz.
        '''
        # given the root of the xml document build composite navigation list 
        #     of indices for each page, question sets, page group and rep number
        
        
        self.SetNavigationList(self.oIOXml.GetQuizLayoutForNavigationList(self.oIOXml.GetRootNode()))
        
        # if randomization is requested - shuffle the page/questionset list
        if self.oCustomWidgets.GetRandomizeRequired():
            # check if xml already holds a set of randomized indices otherwise, call randomizing function
            liRandIndices = self.oCustomWidgets.GetStoredRandomizedIndices()
            if liRandIndices == []:
                # get the unique list  of all Page Group numbers to randomize
                #    this was set during xml validation during the initial read
                liIndicesToRandomize = self.oValidation.GetListUniquePageGroups()
                liRandIndices = self.RandomizePageGroups(liIndicesToRandomize)
                self.oCustomWidgets.AddRandomizedIndicesToQuizResultsFile(liRandIndices)
             
            self.SetNavigationList( self.ShuffleNavigationList(liRandIndices) )
    
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ShuffleNavigationList(self, lRandIndices):
        ''' This function will shuffle the original list as read in from the quiz xml,  that holds the
            "[page number,questionset number, page group number, rep number]" according to the randomized index list input.
            The question sets always remain in the same order as read in with the page, they are never randomized.
            The page groups are randomized. 
                 If more than one page has the same group number, they will remain in the order they were read in.
                 
            e.g. Randomized Page Group order : 2,3,1
            
                     Original XML List                Randomized Page           Shuffled Composite List
                       Page   QS   Grp   Rep             Groups                   Page   QS   Grp   Rep
                       0      0     1     0                 2                       2     0     2     0
                       0      1     1     0                 3                       2     1     2     0
                       1      0     1     0                 1                       3     0     2     0
                       2      0     2     0                                         4     0     3     0
                       2      1     2     0                                         4     1     3     0
                       3      0     2     0                                         0     0     1     0
                       4      0     3     0                                         0     1     1     0
                       4      1     3     0                                         1     0     1     0
        '''
    
        lShuffledCompositeIndices = []
        
        for indRand in range(len(lRandIndices)):
            for indOrig in range(len(self.GetNavigationList())):
                if self.GetNavigationPageGroup(indOrig) == lRandIndices[indRand] :
                    lShuffledCompositeIndices.append( self.GetNavigationIndicesAtIndex(indOrig))
        
        return lShuffledCompositeIndices
   
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def RandomizePageGroups(self, liIndicesToRandomize, iSeed=None):
        ''' Function to take a list of indices and randomize them.
            If there is a '0', it is removed prior to randomizing and inserted back to the
            beginning of the list.
        '''
        
        bPageGroup0 = False
        # remove PageGroup 0 before reandomizing since these represent pages  
        # that will always appear at the beginning of the quiz
        if 0 in liIndicesToRandomize:
            liIndicesToRandomize.remove(0)
            bPageGroup0 = True
        
        ###### iSeed = 100 # for debug
        if iSeed != None:     # used for testing
            random.seed(iSeed)
        else:
            random.seed()
            
        random.shuffle(liIndicesToRandomize)
        liRandIndices = liIndicesToRandomize

        # reset the first PageGroup number to 0 if it was in the quiz
        if bPageGroup0:
            liRandIndices.insert(0,0)
        
        return liRandIndices
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CheckForLastQuestionSetForPage(self):
        bLastQuestionSet = False
        
        # check if at the end of the quiz
        if (self.GetCurrentNavigationIndex() == len(self.GetNavigationList()) - 1):
            bLastQuestionSet = True

        else:
            # we are not at the end of the quiz
            # assume multiple question sets for the page
            # check if next page in the composite index is different than the current page
            #    if yes - we have reached the last question set
            if not( self.GetCurrentPageIndex()) == self.GetNavigationPage(self.GetCurrentNavigationIndex() + 1):
                bLastQuestionSet = True            
           
            
        return bLastQuestionSet
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AdjustToCurrentQuestionSet(self):
        '''
            if there are multiple question sets for a page, the list of question sets must
               include all previous question sets - up to the one being displayed
               (eg. if a page has 4 Qsets, and we are going back to Qset 3,
               we need to collect question set indices 0, and 1 first,
               then continue processing for index 2 which will be appended in DisplayQuestionSet function)
            
            This function is called 
               - when the previous button is pressed or
               - if the ResetView button in Extra Tools is pressed  
        '''
        
        self.ClearQuestionSetList() # initialize
        indQSet = self.GetCurrentQuestionSetIndex()

        if indQSet > 0:

            for idx in range(indQSet):
                xNodeQuestionSet = self.oCustomWidgets.GetNthQuestionSetForCurrentPage(idx, self.GetCurrentPageIndex())
                oQuestionSet = QuestionSet(self)
                oQuestionSet.ExtractQuestionsFromXML(xNodeQuestionSet)
                self.AddToQuestionSetList(oQuestionSet)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetNavigationIndexIfResumeRequired(self):
        ''' Scan the user's quiz file for existing responses in case the user
            exited the quiz prematurely (before it was complete) on the last login

            We assume the quiz pages and question sets are presented sequentially as stored in the
            composite navigation index (which takes into account randomization of the pages if requested)
        '''

            
        # initialize
        iResumeNavigationIndex = 0
        self.SetQuizResuming(False)
        iPageIndex = 0
        xPageNode = None
        # get last login - this will set if QuizComplete is true
        dtLastLogin = self.oCustomWidgets.GetLastLoginTimestamp() # value in datetime format

        
        if self.oCustomWidgets.GetQuizComplete():
            # quiz does not allow for changing responses - review is allowed
            sMsg = 'Quiz has already been completed and responses cannot be modified.'\
                    + ' \nWould you like to review the quiz? '
            if self.oCustomWidgets.GetEmailResultsRequest(self.oUtilsEmail, self.oFilesIO):
                sMsg = sMsg + '\n\nClick No to exit. You will have the option to email results.'
            else:
                sMsg = sMsg + '\n\nClick No to exit.'
                
            qtAns = self.oUtilsMsgs.DisplayYesNo(sMsg)

            if qtAns == qt.QMessageBox.Yes:
                iResumeNavigationIndex = 0
                iPageIndex = self.GetNavigationPage(iResumeNavigationIndex)
                self.SetupPageState(iPageIndex)
                
            else:
                self.ExitOnQuizComplete()
        else:        
    
            # loop through composite navigation index to search for the first page without a "PageComplete='Y'"
            for indNav in range(len(self.GetNavigationList())):
                if not self.GetQuizResuming():
                    iResumeNavigationIndex = indNav
                    iPageIndex = self.GetNavigationPage(indNav)

                    self.SetupPageState(iPageIndex)
                    
                    if self.oCustomWidgets.GetPageCompleteAttribute(iPageIndex) == False:
                        # found first page that was not complete
                        self.SetQuizResuming(True)

            
            # Display a message to user if resuming (special case if resuming on first page)
            # if not iResumeNavigationIndex == self.GetCurrentNavigationIndex():
            if (not iResumeNavigationIndex == self.GetCurrentNavigationIndex()) or\
                (iResumeNavigationIndex == 0 and dtLastLogin != ''):
                self.oUtilsMsgs.DisplayInfo('Resuming quiz from previous login session.')
                self.SetQuizResuming(True)
    
        self.SetCurrentNavigationIndex(iResumeNavigationIndex)

        # reset the default order of image indices based on the new page
        self.InitializeImageDisplayOrderIndices(self.GetCurrentPageIndex())
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def FindNewRepeatedPosition(self, iSearchPageNum, iSearchRepNum):
        ''' this function scans the navigation composite indices to match 
            the Page and Rep numbers of the new repeated page that was inserted
            into the xml file. If there is more than one question set, 
            the navigation index of the first question set is returned.
        '''

        indFound = -1
        
        for iNavInd in range(len(self.GetNavigationList())):
            iPgNum = self.GetNavigationPage(iNavInd)
            iRepNum = self.GetNavigationRepNum(iNavInd)
            
            if iPgNum == iSearchPageNum and iRepNum == iSearchRepNum :
                indFound = iNavInd
                break

                
        return indFound
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def InitializeImageDisplayOrderIndices(self, iPageIndex):
        ''' default to the original order for Images to be displayed based on image elements
            stored in the XML file
        '''
        self.liImageDisplayOrder = []
        lxImageElements = self.oCustomWidgets.GetImageElements(iPageIndex)
        for i in range(len(lxImageElements)):
            self.liImageDisplayOrder.append(i)
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ReorderImageIndexToEnd(self, iIndexToMove):
        ''' Move index to end of list to prioritize the image state of
            the last viewed image in the 1 or 3 Planes view mode.
            This is used in the apply image state function.
            (It prevents the state being overridden because of the order of images read in from the xml file.)
        '''

        liRearrangedOrder = []
        
        for i in range(len(self.liImageDisplayOrder)):
            if self.liImageDisplayOrder[i] != iIndexToMove:
                liRearrangedOrder.append(self.liImageDisplayOrder[i])
                
        liRearrangedOrder.append(iIndexToMove)
        
        return liRearrangedOrder
                
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CreateRepeatedPageNode(self, sXmlFilePath = None):
        ''' Function to copy the current page into the xml allowing the user to create new segments or  
            measurement lines for the same image. 
        '''
        # allow for testing environment to use a pre-set testing file path
        if sXmlFilePath == None:
            sXmlFilePath = self.oFilesIO.GetUserQuizResultsPath()   # for live run
         
        indXmlPageToRepeat = self.GetCurrentPageIndex()
         
        indNextXmlPageWithRep0, iCopiedRepNum = self.oCustomWidgets.RepeatNode(indXmlPageToRepeat, sXmlFilePath) 


###         self.oIOXml.SaveXml(sXmlFilePath)    # for debug
        self.oCustomWidgets.SaveQuiz(sXmlFilePath)
        self.BuildNavigationList() # update after adding xml page
         
        iNewNavInd = self.FindNewRepeatedPosition(indNextXmlPageWithRep0, iCopiedRepNum)
        self.SetCurrentNavigationIndex(iNewNavInd)
     
        # update the repeated page
        self.oCustomWidgets.AdjustQuizResultsFileForRepeatedPage(\
                 self.GetNavigationPage(iNewNavInd),\
                 self.GetNavigationPage( self.GetCurrentNavigationIndex() - 1) )



###         self.oIOXml.SaveXml(sXmlFilePath)    # for debug
        self.BuildNavigationList()  # repeated here to pick up attribute adjustments for Rep#
        self.oCustomWidgets.SaveQuiz(sXmlFilePath)
 
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CheckIfLastRepAndNextPageIncomplete(self):
        ''' Two parts : confirm if this page is at the end of a loop and see if the next page is incomplete.
                1) Look at PageID for this and next Page to see if it is part of the same loop.
             
                2)Identify if any subsequent pages have a PageComplete="Y".
 
            Note: All repeated looping pages follow each other in the XML with consecutive Rep numbers.
 
            This can happen if a 'Previous' or 'GoToBookmark' button was pressed putting the user
            possibly in a page with looping. In this case, the Repeat button needs to be disabled
            until the last rep has been reached - with no subsequent completed pages.
             
        '''
        bEndOfLoopAndNextPageIncomplete = False
         
        bLastLoopingRep = False
        sNextPageID = ''
          
        bLastPageComplete = True
        bNextPageComplete = False
         
        sCurrentPageID = self.oCustomWidgets.GetPageID(self.GetCurrentNavigationIndex())
  
          
        sRepNum = self.oCustomWidgets.GetPageRep(self.GetCurrentNavigationIndex())
        iRepNum = int(sRepNum)
        iNextRepNum = iRepNum + 1
          
        iSubIndex = sCurrentPageID.find('-Rep')
        if iSubIndex >=0:
            sStrippedPageID = sCurrentPageID[0:iSubIndex]
        else:
            sStrippedPageID = sCurrentPageID
          
        sIDForNextRep = sStrippedPageID + '-Rep' + str(iNextRepNum)
  
        # for next page            
        iNextNavigationIndex = self.GetCurrentNavigationIndex() + 1
        if iNextNavigationIndex < len(self.GetNavigationList()):
            sNextPageID = self.oCustomWidgets.GetPageID(self.GetNavigationPage(iNextNavigationIndex))
            bNextPageComplete = self.oCustomWidgets.GetPageCompleteAttribute(self.GetNavigationPage(iNextNavigationIndex))
          
           
        if sNextPageID == sIDForNextRep:
            bLastLoopingRep = False
        else:
            bLastLoopingRep = True
      
          
        if bNextPageComplete:
            bLastPageComplete = False
         
        if bLastLoopingRep and bLastPageComplete:
            bEndOfLoopAndNextPageIncomplete = True
         
        return bEndOfLoopAndNextPageIncomplete
     

   
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #-------------------------------------------
    #        Core Widgets
    #-------------------------------------------
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
#     
#     #-------------------------------------------
#     #        Getters / Setters
#     #-------------------------------------------
# 
#     #----------
#     def SetTabIndex(self, sTabName, iTabIndex):
#         self._dictTabIndices[sTabName] = iTabIndex
#         
#     #----------
#     def GetTabIndex(self, sTabName):
#         return self._dictTabIndices[sTabName]
#         
#     #----------
#     def SetPreviousTabIndex(self, iTabIndex):
#         self._iPreviousTabIndex = iTabIndex
#         
#     #----------
#     def GetPreviousTabIndex(self):
#         return self._iPreviousTabIndex
# 
#     #----------
#     def ResetExtraToolsDefaults(self):
#         self.ResetContourVisibilityToSessionDefault()
#         self.SetViewLinesOnAllDisplays(False)
#         self.SetMeasurementVisibility(True)
#         
         
#     #----------
#     def AddExtraToolsTab(self):
#  
#         # add extra tools tab to quiz widget
#         self.tabExtraTools = qt.QWidget()
#         self.oSlicerInterface.qTabWidget.addTab(self.tabExtraTools,"Extra Tools")
#         self.SetTabIndex('ExtraTools',self.oSlicerInterface.qTabWidget.count - 1)
#         self.oSlicerInterface.qTabWidget.setTabEnabled(self.GetTabIndex('ExtraTools'), True)
#          
#         widget = self.SetupExtraToolsButtons()
#         self.tabExtraTools.setLayout(widget)
# 
#     #----------
#     def InitializeTabSettings(self):
#         self.slEditorMasterVolume = None
#         self.slEditorCurrentTool = 'DefaultTool'
#         self.SetPreviousTabIndex(0)
#         
#         self.btnWindowLevel.setChecked(False)
#         self.onWindowLevelClicked()
#         self.btnCrosshairs.setChecked(False)
#         self.onCrosshairsClicked()
# 
#     #----------
#     def SetGoToBookmarkRequestButton(self, iPageIndex):
# 
#         lsBookmarkRequest = self.oCustomWidgets.GetGoToBookmarkRequest(iPageIndex)
# 
#         if lsBookmarkRequest !=[] :
#             
#             if len(lsBookmarkRequest) > 1:
#                     self._btnGoToBookmark.text = lsBookmarkRequest[1]
#             else:
#                 self._btnGoToBookmark.text = "Return"
# 
#             self._btnGoToBookmark.visible = True
#             self._btnGoToBookmark.enabled = True
#         else:
#             self._btnGoToBookmark.visible = False
#             self._btnGoToBookmark.enabled = False
#             
#     #----------
#     #----------   Segment editor
#     #----------
# 
#     #----------
#     def AddSegmentationModule(self, bTF):
# 
#         if bTF == True:
#             # add segment editor tab to quiz widget
#             self.oSlicerInterface.qTabWidget.addTab(slicer.modules.quizzereditor.widgetRepresentation(),"Segment Editor")
# #             self._bSegmentationModule = True
#             self.SetTabIndex('SegmentEditor', self.oSlicerInterface.qTabWidget.count - 1)
#             self.oSlicerInterface.qTabWidget.setTabEnabled(self.GetTabIndex('SegmentEditor'), True)
#             self.InitializeTabSettings()
#             
# #         else:
# #             self._bSegmentationModule = False
#         
#     #----------
#     def InitializeNullEditorSettings(self):
#         
#         slicer.modules.quizzereditor.widgetRepresentation().self().toolsBox.selectEffect('DefaultTool')
#         slicer.modules.quizzereditor.widgetRepresentation().self().updateLabelFrame(None)
#         slicer.modules.quizzereditor.widgetRepresentation().self().helper.setMasterVolume(None)
# 
#     #----------
#     def CaptureEditorSettings(self):
#         
#         self.slEditorCurrentTool = EditUtil.getCurrentEffect()
#         self.slEditorMasterVolume = slicer.modules.quizzereditor.widgetRepresentation().self().helper.masterSelector.currentNode()
#         self.fCurrentContourRadius = EditUtil.getParameterNode().GetParameter("PaintEffect,radius")
#         
#     #----------
#     def ResetEditorSettings(self):
#         
#         if self.slEditorMasterVolume != None:
#             # note : this order is important
#             slicer.modules.quizzereditor.widgetRepresentation().self().helper.setMasterVolume(self.slEditorMasterVolume)
#             slicer.modules.quizzereditor.widgetRepresentation().self().updateLabelFrame(True)
#             EditUtil.setCurrentEffect(self.slEditorCurrentTool)
#             EditUtil.getParameterNode().SetParameter("PaintEffect,radius", self.fCurrentContourRadius)
#             
#         else:
#             self.InitializeNullEditorSettings()
#             
#     #----------
#     def SetEditorContourToolRadius(self, fRadius):
#         
#         slicer.modules.quizzereditor.widgetRepresentation().self().SetContourToolRadius(fRadius)
#         
#     
#     #----------
#     #----------   NPlanes View
#     #----------
#     
#     #----------
#     def GetNPlanesImageComboBoxSelection(self):
#         ''' return the index and image view object to the xml image that matches the image name and 
#             orientation selected in the combo boxes
#         '''
#         
#         # orientation has been defined in the NPlanes orientation-destination variable
#         if len(self.GetNPlanesView()) > 1:
#             sSelectedOrientation = 'All'   # all 3 planes was selected
#         else:
#             sSelectedOrientation = self.GetNPlanesViewOrientation(0)  # 1 Plane in a specific orientation
#         
#         # get selected image name from combo box
#         sImageName = self.qComboImageList.currentText
#         iQuizIndex = 0
#         oImageViewNode = None
#         bFoundFirstNameMatch = False
#         bFoundOrientationMatch = False
#         
#         # determine which image is to be displayed in an alternate viewing mode (3 Planes or 1 Plane)
#         loImageViewNodes = self.oImageView.GetImageViewList()
#         for oImageViewNode in loImageViewNodes:
#             if oImageViewNode.sNodeName == sImageName:
#                 if not bFoundFirstNameMatch:
#                     bFoundFirstNameMatch = True
#                     iQuizFirstNameMatch = iQuizIndex
#                     oImageViewNodeFirstNameMatch = oImageViewNode
#                 if sSelectedOrientation == 'All':
#                     break
#                 else:
#                     if sSelectedOrientation == oImageViewNode.sOrientation:
#                         bFoundOrientationMatch = True
#                         break
#                     else:
#                         iQuizIndex = iQuizIndex + 1
# 
#             
#             else:
#                 iQuizIndex = iQuizIndex + 1
#         
#         # There may not have been an xml element with the selected orientation view
#         #    Reset to the first name match
#         if not bFoundOrientationMatch:
#             iQuizIndex = iQuizFirstNameMatch
#             oImageViewNode = oImageViewNodeFirstNameMatch
#             
#         return oImageViewNode, iQuizIndex
#         
#     #----------
#     def GetNPlanesComboBoxCount(self):
#         return self.qComboImageList.count
#     
#     #----------
#     def SetNPlanesView(self):
#         
#         self.sViewingMode = self.qComboNPlanesList.currentText
# 
#        
#         self.lsLayoutWidgets = []  # widgets for contour visibility list
#         self.lsLayoutWidgets.append('Red')
# 
#         
#         if self.sViewingMode == "1 Plane Axial":
#             self.llsNPlanesOrientDest = [["Axial","Red"]]
#         elif self.sViewingMode == "1 Plane Sagittal":
#             self.llsNPlanesOrientDest = [["Sagittal","Red"]]
#         elif self.sViewingMode == "1 Plane Coronal":
#             self.llsNPlanesOrientDest = [["Coronal","Red"]]
#         elif self.sViewingMode == "3 Planes":
#             self.llsNPlanesOrientDest = [["Axial","Red"],["Coronal","Green"],["Sagittal","Yellow"]]
#             self.lsLayoutWidgets.append('Green')
#             self.lsLayoutWidgets.append('Yellow')
#             
# 
#         
#     #----------
#     def GetNPlanesView(self):
#         return self.llsNPlanesOrientDest
#                 
#     #----------
#     def GetNPlanesViewOrientation(self, indPlane):
# 
#         return self.llsNPlanesOrientDest[indPlane][0]
# 
#     #----------
#     def SetNPlanesComboBoxImageNames(self):
#         
#         self.qComboImageList.clear()
#         
#         lNamesAdded = []
#         loImageViewNodes = self.oImageView.GetImageViewList()
#         for oImageViewNode in loImageViewNodes:
#             if oImageViewNode.sViewLayer == 'Background' or oImageViewNode.sViewLayer == 'Foreground':
#                 if oImageViewNode.sNodeName in lNamesAdded:
#                     pass
#                 else:
#                     lNamesAdded.append(oImageViewNode.sNodeName)
#                     self.qComboImageList.addItem(oImageViewNode.sNodeName)
#                     
# 
#     #----------
#     #----------   Contours outline/fill and opacity
#     #----------
# 
#     #----------
#     def SetContourVisibilityCheckBox(self, sVisibility): 
#         # set the contour visibility widget in Extra Tools 
#             
#         if sVisibility == 'Fill':
#             self.qChkBoxFillOrOutline.setChecked(True)
#         else:
#             self.qChkBoxFillOrOutline.setChecked(False)
# 
#     #----------
#     def GetSessionContourOpacityDefault(self):
#         # default for opacity for the session
#         
#         return self._sSessionContourOpacity
# 
#     #----------
#     def GetContourDisplayState(self):
#         # get current settings from the extra tools widgets describing the contour display state
#         
#         bFill = self.qChkBoxFillOrOutline.checked
#         if bFill:
#             sFillOrOutline = 'Fill'
#         else:
#             sFillOrOutline = 'Outline'
# 
#         iSliderValue = self.qVisibilityOpacity.value
#         if self.qVisibilityOpacity.maximum > self.qVisibilityOpacity.minimum:
#             fOpacity = iSliderValue / (self.qVisibilityOpacity.maximum - self.qVisibilityOpacity.minimum)
#         else:
#             fOpacity = self.GetSessionContourOpacityDefault()
#         
#         return sFillOrOutline, iSliderValue, fOpacity
#     
#     #----------
#     def ResetContourDisplayState(self, sFillOrOutline, iSliderValue, fOpacity):
#         
#         self.SetContourVisibilityCheckBox(sFillOrOutline)           # tool widget Fill/Outline
#         self.SetSliderToolFromContourOpacity(fOpacity)              # tool widget Opacity
#         self.SetContourOpacityFromSliderValue(iSliderValue)         # image view property
#         
#     #----------
#     def SetContourOpacityFromSliderValue(self, iSliderValue):
#         # set the ContourOpacity property of the image view object based on slider value for opacity
#         
#         if self.oImageView != None:
#             if self.qVisibilityOpacity.maximum > self.qVisibilityOpacity.minimum:  # no div by zero
#                 self.oImageView.SetContourOpacity(iSliderValue / (self.qVisibilityOpacity.maximum - self.qVisibilityOpacity.minimum))
#             else:
#                 self.oImageView.SetContourOpacity(self.GetSessionContourOpacityDefault())
#                 
#             # reset outline or fill
#             self.onContourDisplayStateChanged()
#         
#     #----------
#     def SetSliderToolFromContourOpacity(self, fOpacity):
#         # set Slider widget position for opacity
#         
#         #
#         # if self.qVisibilityOpacity.maximum > self.qVisibilityOpacity.minimum:
#         #     fOpacity = self.GetSessionContourOpacityDefault()
#             
#         iSliderValue = int(fOpacity * (self.qVisibilityOpacity.maximum - self.qVisibilityOpacity.minimum))    
#         self.qVisibilityOpacity.setValue(iSliderValue)
# 
#     #----------
#     def ResetContourVisibilityToSessionDefault(self):
#         # reset widgets and the imageView property to the session default of contour visibility 
#         
#         self.SetContourVisibilityCheckBox(self.oCustomWidgets.GetSessionContourVisibilityDefault())    # tool widget Fill/Outline
#         self.SetSliderToolFromContourOpacity(self.GetSessionContourOpacityDefault())    # tool widget Opacity
#         self.SetContourOpacityFromSliderValue(self.qVisibilityOpacity.value)            # image view property
# 
#     
#     #----------
#     #----------   Quiz tabs
#     #----------
# 
#     #----------
#     def SegmentationTabEnabler(self, bTF):
# 
#         self.oSlicerInterface.qTabWidget.setTabEnabled(self.GetTabIndex('SegmentEditor') , bTF)
#         
#     #----------
#     def GetSegmentationTabEnabled(self):
#         bTF = self.oSlicerInterface.qTabWidget.isTabEnabled(self.GetTabIndex('SegmentEditor') )
#         return bTF
#     
#     #----------
#     def EnableTabBar(self, bTF):
#         self.oSlicerInterface.qTabWidget.tabBar().setEnabled(bTF)
#         
# 
#     #----------
#     #----------   Markup lines
#     #----------
# 
#     #----------
#     def EnableMarkupLinesTF(self, bTF):
#         
#         self.btnAddMarkupsLine.enabled = bTF
#         self.btnClearLines.enabled = bTF
#         if bTF:
#             self.btnAddMarkupsLine.setStyleSheet("QPushButton{ background-color: rgb(0,179,246); color: black }")
#             self.btnClearLines.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: black }")
#         else:
#             self.btnAddMarkupsLine.setStyleSheet("QPushButton{ background-color: rgb(0,179,246); color: white }")
#             self.btnClearLines.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: white }")
# 
#     #----------
#     def SetMeasurementVisibility(self, bTF):
#         self.qChkBoxMeasurementVisibility.setChecked(bTF)
#         self.onMeasurementVisibilityStateChanged()
#         
#     #----------
#     def SetViewLinesOnAllDisplays(self, bTF):
#         self.qChkBoxViewOnAllDisplays.setChecked(bTF)
#         self.onViewLinesOnAllDisplaysStateChanged()
#         


#     #-------------------------------------------
#     #        Event Handlers
#     #-------------------------------------------
#     
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def onTabChanged(self):
#         ''' When changing tabs reset segment editor interface.
#             Ensure window/level tool is turned off.
#         '''
# 
#         self.btnWindowLevel.setChecked(False)
#         self.onWindowLevelClicked()
#     
#     
#         # when moving off the Segment Editor tab
#         if self.GetPreviousTabIndex() == self.GetTabIndex('SegmentEditor'):
#             self.CaptureEditorSettings()
#             self.InitializeNullEditorSettings()
#             
#         # when returning to the Segment Editor tab
#         if self.oSlicerInterface.qTabWidget.currentIndex == self.GetTabIndex('SegmentEditor'):
#             self.ResetEditorSettings()
# 
#         self.SetPreviousTabIndex(self.oSlicerInterface.qTabWidget.currentIndex)
#     
#         
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def onNextButtonClicked(self):
# 
#         try:        
#             if self._btnRepeat.enabled == True:
#                 if self._btnNext.text == 'Finish':
#                     sNextPhrase = 'Finish'
#                 else:
#                     sNextPhrase = 'move to Next set'
#                 sMsg = "You have the option to repeat this set of images and questions." +\
#                         "\nClick 'OK' to " + sNextPhrase + " otherwise click 'Cancel'."
#                 
#                 qtAns = self.oUtilsMsgs.DisplayOkCancel(sMsg)
#                 if qtAns == qt.QMessageBox.Cancel:
#                     return
# 
#             sMsg = ''
#             sCompletedMsg = ''
#             sSaveMsg = ''
#             sInteractionMsg = 'Next'
#                     
#             self.SetInteractionLogOnOff('Off',sInteractionMsg)
#                 
#             self.DisableButtons()    
#             if self.sViewingMode != 'Default':
#                 self.onResetViewClicked('Next')
#     
#             if self.GetCurrentNavigationIndex() + 1 == len(self.GetNavigationList()):
#     
#                 # the last question was answered - check if user is ready to exit
#                 self.onExitButtonClicked('Finish') # a save is done in here
#                 
#                 # the user may have cancelled the 'finish'
#                 # bypass remainder of the 'next' button code
#     
#             else:
#                 # this is not end of quiz, do a save and display the next page
#                 
#                 bSuccess, sSaveMsg = self.PerformSave('NextBtn') 
#                 if bSuccess:
#                     
#                     bSuccess, sCompletedMsg = self.UpdateCompletions('NextBtn')
#                     if bSuccess:
#                         
#                         self.CaptureAndSaveImageState()
#     
#                         ########################################    
#                         # set up for next page
#                         ########################################    
#                         
#                         # if last question set, clear list and scene
#                         if self.CheckForLastQuestionSetForPage() == True:
#                             self._loQuestionSets = []
#                             slicer.mrmlScene.Clear()
#                             bChangeXmlPageIndex = True
#                         else:
#                             # clear quiz widgets only
#                             self.oSlicerInterface.ClearLayout(self.oSlicerInterface.qQuizLayout)
#                             bChangeXmlPageIndex = False
#     
#     
#                         self.SetCurrentNavigationIndex(self.GetCurrentNavigationIndex() + 1 )
#                         self.progress.setValue(self.GetCurrentNavigationIndex())
#                         self.InitializeImageDisplayOrderIndices(self.GetCurrentPageIndex())
#                         
#                         if bChangeXmlPageIndex:
#                             self.SetupPageState(self.GetCurrentPageIndex())
#                             if self.oCustomWidgets.GetButtonScriptRerunRequired(self.GetCurrentPageIndex()):
#                                 self.oCustomWidgets.SetPageIncomplete(self.GetCurrentPageIndex())
#                             
#                         self.InitializeTabSettings()
#                         self.DisplayQuizLayout()
#                         self.DisplayImageLayout()
# 
#                         
#             sInteractionMsg = sInteractionMsg + sSaveMsg + sCompletedMsg
# 
#             self.SetInteractionLogOnOff('On',sInteractionMsg)
#             self.EnableButtons()
#                 
#         except:
#             iPage = self.GetCurrentPageIndex() + 1
#             tb = traceback.format_exc()
#             sMsg = "onNextButtonClicked: Error moving to next page. Current page: " + str(iPage) \
#                    + "\n\n" + tb 
#             self.oUtilsMsgs.DisplayError(sMsg)
#                 
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def onPreviousButtonClicked(self):
#         
#             
#         sMsg = ''
#         try:
#  
#             self.SaveAndGoToPreviousPageDisplay('Previous', self.GetNavigationPage(self.GetCurrentNavigationIndex() - 1), self.GetCurrentNavigationIndex() - 1)
#              
#  
#  
#         except:
#             iPage = self.GetCurrentPageIndex() + 1
#             tb = traceback.format_exc()
#             sMsg = "onPreviousButtonClicked: Error moving to previous page. Current page: " + str(iPage) \
#                    + "\n\n" + tb 
#             self.oUtilsMsgs.DisplayError(sMsg)
#             
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def onExitButtonClicked(self,sCaller):
#         ''' this Exit function can be triggered by pressing 'Exit' button or by pressing 'Finish'
#         '''
# 
#         try:
#             bExit = False
#             sMsg = ''
#             sCompletedMsg = ''
#             sSaveMsg = ''
#             sCancelExitMsg = ''
#             sInteractionMsg = 'Exit'
#                     
#             
#             self.progress.setValue(self.GetCurrentNavigationIndex() + 1)
#             if len(self.GetNavigationList()) >0:
#                 iProgressPercent = int((self.GetCurrentNavigationIndex() + 1) / len(self.GetNavigationList()) * 100)
#             else:
#                 # error in creating the composite navigation index - assign percent to 100 for exiting
#                 self.oUtilsMsgs.DisplayError('ERROR creating quiz indices - Exiting')
#             self.progress.setFormat(self.sPageID + '  ' + self.sPageDescriptor + '    ' + str(iProgressPercent) + '%')
#             
#             sMsg = 'Do you wish to exit?'
#             if sCaller == 'ExitBtn':
#                 sMsg = sMsg + ' \nYour responses will be saved. Quiz may be resumed.'
#             else:
#                 if sCaller == 'Finish':
#                     sMsg = sMsg + " \nYour quiz is complete and your responses will be locked." \
#                                 + " \n\nIf you wish to resume at a later time, press 'Cancel' here, then use the 'Exit' button."
#     
#             qtAns = self.oUtilsMsgs.DisplayOkCancel(sMsg)
#             if qtAns == qt.QMessageBox.Ok:
# 
#                 self.SetInteractionLogOnOff('Off',sInteractionMsg)
#                 self.DisableButtons()    
# 
#                 bSuccess, sSaveMsg = self.PerformSave(sCaller)
#                 if bSuccess:
#                     
#                     bSuccess, sCompletedMsg = self.UpdateCompletions(sCaller)
#                     if bSuccess:
# 
#                         self.CaptureAndSaveImageState()
#             
#                         self.QueryThenSendEmailResults()
#                         
#                         # update shutdown batch file to remove SlicerDICOMDatabase
#                         self.oFilesIO.CreateShutdownBatchFile()
#                 
#                         slicer.util.exit(status=EXIT_SUCCESS)
#                         bExit = True    # added for delay in slicer closing down - prevent remaining code from executing
#     
#             
#             else:
#                 sCancelExitMsg = ' ... cancelled Exit to continue with quiz'
#                 
#             sInteractionMsg = sInteractionMsg + sSaveMsg + sCompletedMsg + sCancelExitMsg
#                 
#             # if code reaches here, either the exit was cancelled or there was 
#             # an error in the save
#             
#             if not(bExit):
#                 self.SetInteractionLogOnOff('On',sInteractionMsg)
#                 self.EnableButtons() 
#         
#                 self.progress.setValue(self.GetCurrentNavigationIndex())
#                 iProgressPercent = int(self.GetCurrentNavigationIndex() / len(self.GetNavigationList()) * 100)
#                 self.progress.setFormat(self.sPageID + '  ' + self.sPageDescriptor + '    ' + str(iProgressPercent) + '%')
#     
#     
#         except:
#             iPage = self.GetCurrentPageIndex() + 1
#             tb = traceback.format_exc()
#             sMsg = "onExitButtonClicked: Error exiting quiz. Current page: " + str(iPage) \
#                    + "\n\n" + tb 
#             self.oUtilsMsgs.DisplayError(sMsg)
#             
#         
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def onRepeatButtonClicked(self):
#         ''' Function to manage repeating a page node when user requests a repeat (looping).
#             This is generally used for multiple lesions.
#         '''
#         
#         try:        
#             qtAns = self.oUtilsMsgs.DisplayOkCancel(\
#                                 "Are you sure you want to repeat this set of images and questions?" +\
#                                 "\nIf No, click 'Cancel' and press 'Next' to continue.")
#             if qtAns == qt.QMessageBox.Ok:
#                 sMsg = ''
#                 sCompletedMsg = ''
#                 sSaveMsg = ''
#                 sInteractionMsg = 'Repeat'
# 
#                 self.SetInteractionLogOnOff('Off', sInteractionMsg)
#                 
#                 self.DisableButtons()    
#                 if self.sViewingMode != 'Default':
#                     self.onResetViewClicked('Repeat')
# 
#                 bSuccess, sSaveMsg = self.PerformSave('NextBtn')
#                 if bSuccess:
# 
#                     bSuccess, sCompletedMsg = self.UpdateCompletions('NextBtn')
#                     if bSuccess:
#     
#                         self.CaptureAndSaveImageState()
#                         
#                         self.CreateRepeatedPageNode()
#     
#                         # cleanup
#                         self._loQuestionSets = []
#                         slicer.mrmlScene.Clear()
#                 
#                         
#                         self.progress.setMaximum(len(self.GetNavigationList()))
#                         self.progress.setValue(self.GetCurrentNavigationIndex())
#                         
#                         self.SetupPageState(self.GetCurrentPageIndex())
#                         if self.oCustomWidgets.GetButtonScriptRerunRequired(self.GetCurrentPageIndex()):
#                             self.oCustomWidgets.SetPageIncomplete(self.GetCurrentPageIndex())
# 
#                         self.InitializeTabSettings()
#                         self.DisplayQuizLayout()
#                         self.DisplayImageLayout()
#                         
# 
#                 sInteractionMsg = sInteractionMsg + sSaveMsg + sCompletedMsg
#    
#                 self.SetInteractionLogOnOff('On', sInteractionMsg)
#                 self.EnableButtons()
#                 
#         except:
#             iPage = self.GetCurrentPageIndex() + 1
#             tb = traceback.format_exc()
#             sMsg = "onRepeatButtonClicked: Error repeating this page. Current page: " + str(iPage) \
#                    + "\n\n" + tb 
#             self.oUtilsMsgs.DisplayError(sMsg)
#     
#     
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def onAddLinesButtonClicked(self):
#         ''' Add a new markup line - using the PlaceMode functionality
#         '''
#         self.slMarkupsLineWidget.setMRMLScene(slicer.mrmlScene)
#         markupsNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode")
#         self.slMarkupsLineWidget.setCurrentNode(slicer.mrmlScene.GetNodeByID(markupsNode.GetID()))
#         self.slMarkupsLineWidget.setPlaceModeEnabled(True)
# 
#         markupsNode.AddObserver(slicer.vtkMRMLMarkupsLineNode.PointModifiedEvent, self.onMarkupInteraction)
# 
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def onClearLinesButtonClicked(self):
#         ''' A function to clear all markup line nodes from the scene.
#         '''
#         sMsg = ''
#         xPageNode = self.oCustomWidgets.GetNthPageNode(self.GetCurrentPageIndex())
#         bPageComplete = self.oCustomWidgets.GetPageCompleteAttribute(self.GetCurrentPageIndex())
# 
#         if bPageComplete and not self.GetMultipleResponseAllowed():
#             sMsg = '\nThis page has already been completed. You cannot remove the markup lines.'
#             self.oUtilsMsgs.DisplayWarning(sMsg)
#         else:
#             try:           
#                 slLineNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLMarkupsLineNode')
#                 for node in slLineNodes:
#                     slicer.mrmlScene.RemoveNode(node)
#                 
#                 # remove all markup line elements stored in xml for this page node
#                 # and delete the markup line file stored in folder
#                 lxImages = self.oIOXml.GetChildren(xPageNode, 'Image')
#                 for xImage in lxImages:
#                     lxMarkupLines = self.oIOXml.GetChildren(xImage, 'MarkupLinePath')
#                     for xMarkupLine in lxMarkupLines:
#                         sPath = self.oIOXml.GetDataInNode(xMarkupLine)
#                         sAbsolutePath = self.oFilesIO.GetAbsoluteUserPath(sPath)
#                         if os.path.exists(sAbsolutePath):    # same path may exist in multiple xml Image elements
#                             os.remove(sAbsolutePath)
#                 
#                     self.oIOXml.RemoveAllElements(xImage, 'MarkupLinePath')
#                 self.oIOXml.SaveXml(self.oFilesIO.GetUserQuizResultsPath())
#             
#             except:
#                 tb = traceback.format_exc()
#                 sMsg = "onClearLinesButtonClicked: Error clearing all markup lines.  \n\n" + tb 
#                 self.oUtilsMsgs.DisplayError(sMsg)
#             
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def onMarkupInteraction(self, caller, event):
#         ''' adjust display once the full markups line is completed
#         '''
#         markupsNode = caller
#         markupIndex = markupsNode.GetDisplayNode().GetActiveControlPoint()
# 
#         if markupIndex == 1:        
#             self.SetViewLinesOnAllDisplays(self.qChkBoxViewOnAllDisplays.isChecked())
#             self.SetMeasurementVisibility(self.qChkBoxMeasurementVisibility.isChecked())
#         
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def onWindowLevelClicked(self):
#         
#         if self.btnWindowLevel.isChecked():
#             self.btnWindowLevel.setStyleSheet("QPushButton{ background-color: rgb(0,179,246); color: black }")
#             slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(slicer.vtkMRMLInteractionNode.AdjustWindowLevel)
#         else:
#             self.btnWindowLevel.setStyleSheet("QPushButton{ background-color: rgb(173,220,237); color: black }")
#             slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(slicer.vtkMRMLInteractionNode.ViewTransform)
#         
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def onCrosshairsClicked(self):
#         ''' activate the crosshairs tool
#         '''
#         if self.btnCrosshairs.isChecked():
#             
#             self.btnCrosshairs.setStyleSheet("QPushButton{ background-color: rgb(0,179,246); color: black }")
#             slCrosshairNode = slicer.mrmlScene.GetNodeByID('vtkMRMLCrosshairNodedefault')
#             slCrosshairNode.SetCrosshairBehavior(1) # offset jump slice
#             slCrosshairNode.SetCrosshairMode(2)     # basic intersection
#         else:
#             self.btnCrosshairs.setStyleSheet("QPushButton{ background-color: rgb(173,220,237); color: black }")
#             slCrosshairNode = slicer.mrmlScene.GetNodeByID('vtkMRMLCrosshairNodedefault')
#             slCrosshairNode.SetCrosshairBehavior(1) # offset jump slice
#             slCrosshairNode.SetCrosshairMode(0)     # basic intersection
#     
#         
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
#     def onNPlanesViewClicked(self):
#         ''' display the requested image in the requested viewing mode
#         '''
#         try:
#             self.SetInteractionLogOnOff('Off','Changing View - Display View Button - NPlanes')
# 
#             if self.GetNPlanesComboBoxCount() > 0:
#                 self.CaptureAndSaveImageState()
#                 
#                 self.SetNPlanesView()
#                 oImageNodeOverride, iQuizImageIndex = self.GetNPlanesImageComboBoxSelection()
#                 self.liImageDisplayOrder = self.ReorderImageIndexToEnd(iQuizImageIndex)
#                 self.oImageView.AssignNPlanes(oImageNodeOverride, self.llsNPlanesOrientDest)
#                 self.bNPlanesViewingMode = True
#         
#                 #    the current image node being displayed in an alternate view may have been 
#                 #    repeated in different orientations in the quiz file
#                 self.loCurrentQuizImageViewNodes = self.oCustomWidgets.GetMatchingQuizImageNodes(oImageNodeOverride.sImagePath, self.oImageView)
#                 self.ApplySavedImageState()
#             else:
#                 sMsg = 'No images have been loaded to display in an alternate viewing mode.'
#                 self.oUtilsMsgs.DisplayWarning(sMsg)
#                 
#             self.oUtilsMsgs.DisplayTimedMessage('***','Waiting',100) #force Slicer to refresh display before logging resumes
#             self.SetInteractionLogOnOff('On','Changing View - Display View Button - ' + self.qComboNPlanesList.currentText)
# 
#         except:
#             tb = traceback.format_exc()
#             sMsg = "onNPlanesViewClicked: Error setting the NPlanes view (closeup) request.  \n\n" + tb 
#             self.oUtilsMsgs.DisplayError(sMsg)
#             
#             
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def onResetViewClicked(self, sCaller=None):
#         ''' Capture responses in the current state (may not be completed) before 
#             resetting the viewing nodes to original layout for this page.
#             Restore the current responses.
#         '''
#         
#         lsCurrentResponses = []
# 
#         try:
#             
#             self.SetInteractionLogOnOff('Off','Changing View - Reset Button')
#             
#             sCaptureSuccessLevel, lsCurrentResponses, sMsg = self.CaptureNewResponses()
#             self.CaptureAndSaveImageState()
#             
#             sFillOrOutline, iOpacitySliderValue, fOpacity = self.GetContourDisplayState()
#             self.AdjustToCurrentQuestionSet()
#             self.bNPlanesViewingMode = False
#             self.sViewingMode = "Default"
#             self.loCurrentQuizImageViewNodes = []
#             self.DisplayQuizLayout()
#             self.DisplayImageLayout('ResetView')
#             
#             self.ResetContourDisplayState(sFillOrOutline, iOpacitySliderValue, fOpacity)
#             slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(slicer.vtkMRMLInteractionNode.ViewTransform)
#             
#             # Populate quiz with current responses
#             self.DisplayCurrentResponses(lsCurrentResponses)
#             self.ApplySavedImageState()
#             
# 
#             if sCaller == 'NPlanes':
#                 self.oUtilsMsgs.DisplayTimedMessage('***','Waiting',100) #force Slicer to refresh display before logging resumes
#                 self.SetInteractionLogOnOff('On','Changing View - Reset Button - caller: ' + sCaller)
#                 
#         except:
#             tb = traceback.format_exc()
#             sMsg = "onResetViewClicked: Error resetting the view after NPlanes (closeup) request.  \n\n" + tb 
#             self.oUtilsMsgs.DisplayError(sMsg)
#             
# 
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def onContourDisplayStateChanged(self):
#         # when user changes a contour visibility widget setting in the extra tools tab,
#         #    adjust the image view property and turn on fill/outline for label maps and segmentations
#         
#         if self.oImageView != None:
#             if self.qChkBoxFillOrOutline.isChecked():
#                 self.oImageView.SetContourVisibility('Fill')
#             else:
#                 self.oImageView.SetContourVisibility('Outline')
#             
#             self.oImageView.SetLabelMapOutlineOrFill(self.lsLayoutWidgets)
#     
#             xPageNode = self.oCustomWidgets.GetNthPageNode(self.GetCurrentPageIndex())
#             loImageViewNodes = self.oImageView.GetImageViewList()
#             for oViewNode in loImageViewNodes:
#                 if oViewNode.sViewLayer == 'Segmentation':
#                     slSegDisplayNode, slSegDataNode = oViewNode.GetSegmentationNodes(xPageNode)
#                     self.oImageView.SetSegmentationOutlineOrFill(oViewNode, slSegDisplayNode)
#                 
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def onViewLinesOnAllDisplaysStateChanged(self):
#         ''' function to turn on/off display of markup lines in all viewing windows
#             or on just the windows displaying the image linked with the viewing window
#             where it was created
#         '''
#         
#         dictViewNodes = {"Red":"vtkMRMLSliceNodeRed", "Green":"vtkMRMLSliceNodeGreen", "Yellow":"vtkMRMLSliceNodeYellow", "Slice4":"vtkMRMLSliceNodeSlice4"}
# 
# 
#         slMarkupNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLMarkupsLineNode')
#         
#         for slMarkupNode in slMarkupNodes:
#             slMarkupDisplayNode = slMarkupNode.GetDisplayNode()
#             lViewNodes = []
#             
#             if self.qChkBoxViewOnAllDisplays.isChecked():
#                 slMarkupDisplayNode.SetViewNodeIDs(list(dictViewNodes.values()))
#                 
#             else:
#                 slAssociatedNodeID = slMarkupNode.GetNthMarkupAssociatedNodeID(0)
#                 
#                 
#                 for oViewNode in self.oImageView.GetImageViewList():
# 
#                     if oViewNode.slNode.GetID() == slAssociatedNodeID:                
#                         slViewNode = oViewNode.sDestination
#                         lViewNodes.append(dictViewNodes[slViewNode])
#                         slMarkupDisplayNode.SetViewNodeIDs(lViewNodes)
# 
#         slMarkupNodes.UnRegister(slicer.mrmlScene)    #cleanup memory
# 
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def onMeasurementVisibilityStateChanged(self):
#         # display line measurements on/off
#         slMarkupNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLMarkupsLineNode')
#         
#         for slNode in slMarkupNodes:
#             slDisplayNode = slNode.GetDisplayNode()
#             if self.qChkBoxMeasurementVisibility.isChecked():
#                 slDisplayNode.PropertiesLabelVisibilityOn()
#             else:
#                 slDisplayNode.PropertiesLabelVisibilityOff()
# 
#         slMarkupNodes.UnRegister(slicer.mrmlScene)    #cleanup memory
# 
#         
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def onGoToBookmarkButtonClicked(self):
#         ''' Function to change to previous bookmarked page
#             The user will be taken to the most recent Page that has the specified 'BookmarkID'
#             Quiz validation checks to see if the GoToBookmark and BookmarkID have the same
#             PageGroup number if randomization is turned on. 
#             Quiz validation also checks if there is an historical BookmarkID for the GoToBookmark 
#         '''
#         # find previous page with the BookmarkID match
#         xPageNode = self.oCustomWidgets.GetNthPageNode(self.GetCurrentPageIndex())
# 
#         sGoToBookmark = ''
#         sGoToBookmarkRequest = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'GoToBookmark')
#         if sGoToBookmarkRequest != '':
#             sGoToBookmark = sGoToBookmarkRequest.split()[0]
# 
#         # set up dictionary with value to match in historical pages
#         dictAttribToMatchInHistory = {}
#         dictAttribToMatchInHistory['BookmarkID'] = sGoToBookmark
#         
#         # all page nodes that match - ordered with most recent first
#         dictPgNodeAndPgIndex = self.oIOXml.GetMatchingXmlPagesFromAttributeHistory(self.GetCurrentNavigationIndex(), self.GetNavigationList(), dictAttribToMatchInHistory)
#         lPageIndices = list(dictPgNodeAndPgIndex.values())
#         if len(lPageIndices) > 0:
#             iBookmarkedPageIndex = lPageIndices[0]
#             iBookmarkedNavigationIndex = self.oIOXml.GetNavigationIndexForPage(self.GetNavigationList(), iBookmarkedPageIndex)
#             
#             
#     #### for debug ###            
#     #         sMsg = 'Leaving current screen - return to Bookmark page'\
#     #                 + '\nCurrentNavigationIndex: ' + str(self.GetCurrentNavigationIndex()) \
#     #                 + '\nCurrentPage (0-based): ' + str( self.GetCurrentPageIndex()) \
#     #                 + '\nPageIndex: ' + str(iBookmarkedPageIndex)\
#     #                 + '\nNavigationIndex: ' + str(iBookmarkedNavigationIndex)
#     #                   
#     #         self.oUtilsMsgs.DisplayWarning(sMsg)
#              
#     
#     
#             try:
#                 sMsg = ''
#     
#                 self.SaveAndGoToPreviousPageDisplay('GoToBookmark', iBookmarkedPageIndex, iBookmarkedNavigationIndex)
#     
#             except:
#                 iPage = self.GetCurrentPageIndex() + 1
#                 tb = traceback.format_exc()
#                 sMsg = "onGoToBookmarkButtonClicked: Error moving to bookmarked page. Current page: " + str(iPage) \
#                        + "\n\n" + tb 
#                 self.oUtilsMsgs.DisplayError(sMsg)
#             
#         
#         
#         
#     
# 
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def SaveAndGoToPreviousPageDisplay(self, sCaller, iNewPageIndex, iNewNavigationIndex):
#         ''' Function will save current state of questions and images.
#             Called when going to Previous page or if the GoToBookmark button is clicked. 
#  
#             During the 'UpdateCompletions' function, only the completion requirement lists
#             (not the completed flags) are updated allowing the user to return 
#             to the current page to complete it.
#         '''
#         
#         sSaveMsg = ''
#         sInteractionMsg = sCaller
#         sCompletedMsg = ''
# 
#         self.SetInteractionLogOnOff('Off',sCaller)
#         
#            
#         self.DisableButtons()    
#         if self.sViewingMode != 'Default':
#             self.onResetViewClicked(sCaller)
# 
#         bChangeXmlPageIndex = True
# 
#         if self.GetCurrentNavigationIndex() > 0:
#             if self.GetCurrentPageIndex() == iNewPageIndex:
#                 bChangeXmlPageIndex = False  
#         
#         bSuccess, sSaveMsg = self.PerformSave(sCaller)
#         if bSuccess:
#             
#             bSuccess, sCompletedMsg = self.UpdateCompletions(sCaller)
#             if bSuccess:
# 
#                 self.CaptureAndSaveImageState()
#     
#                 ########################################    
#                 # set up for new display page
#                 ########################################    
#         
#                 self.SetCurrentNavigationIndex(iNewNavigationIndex)
#                 self.progress.setValue(self.GetCurrentNavigationIndex())
#                 self.InitializeImageDisplayOrderIndices(self.GetCurrentPageIndex())
#         
#                 if self.GetCurrentNavigationIndex() < 0:
#                     # reset to beginning
#                     self.SetCurrentNavigationIndex( 0 )
#                 
#                 self.AdjustToCurrentQuestionSet()
#                 
#                 if bChangeXmlPageIndex:
#                     slicer.mrmlScene.Clear()
#                     self.SetupPageState(self.GetCurrentPageIndex())
#                     if self.oCustomWidgets.GetButtonScriptRerunRequired(self.GetCurrentPageIndex()):
#                         self.oCustomWidgets.SetPageIncomplete(self.GetCurrentPageIndex())
#         
#                 self.InitializeTabSettings()
#                 self.DisplayQuizLayout()
#                 self.DisplayImageLayout()
#             
#         sInteractionMsg = sInteractionMsg + sSaveMsg + sCompletedMsg
# 
#         self.SetInteractionLogOnOff('On', sInteractionMsg)
#         self.EnableButtons()
# 
#         
    
    
    
    
    #-------------------------------------------
    #        Functions
    #-------------------------------------------
    
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def SetupWidgets(self, slicerMainLayout):
# 
#         self.oSlicerInterface = SlicerInterface(self.oFilesIO)
#         self.oSlicerInterface.CreateLeftLayoutAndWidget()
# 
#         self.SetupButtons()
#         self.oSlicerInterface.qLeftLayout.addWidget(self.qButtonGrpBox)
# 
#         self.oSlicerInterface.AddQuizLayoutWithTabs()
#         self.oSlicerInterface.qTabWidget.currentChanged.connect(self.onTabChanged)
#        
#         slicerMainLayout.addWidget(self.oSlicerInterface.qLeftWidget)  
# 
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def SetupButtons(self):
#         
#         qProgressLabel = qt.QLabel('Progress ')
#         self.progress = qt.QProgressBar()
#         self.progress.setGeometry(0, 0, 100, 20)
#         self.progress.setStyleSheet("QProgressBar{ text-align: center } QProgressBar::chunk{ background-color: rgb(0,179,246) }")
#  
# 
#         # create buttons
#         
#         # add horizontal layout
#         self.qButtonGrpBox = qt.QGroupBox()
#         self.qButtonGrpBox.setTitle('Baines Image Quizzer')
#         self.qButtonGrpBox.setStyleSheet("QGroupBox{ font-size: 14px; font-weight: bold}")
#         self.qButtonGrpBoxLayout = qt.QHBoxLayout()
#         self.qButtonGrpBox.setLayout(self.qButtonGrpBoxLayout)
# 
#         # Next button
#         self._btnNext = qt.QPushButton("Next")
#         self._btnNext.toolTip = "Save responses and display next set of questions."
#         self._btnNext.enabled = True
#         self._btnNext.setStyleSheet("QPushButton{ background-color: rgb(0,179,246); color: black }")
# #         self._btnNext.connect('clicked(bool)',self.onNextButtonClicked)
#         self._btnNext.clicked.connect(self.onNextButtonClicked)
#         
#         # Back button
#         self._btnPrevious = qt.QPushButton("Previous")
#         self._btnPrevious.toolTip = "Display previous set of questions."
#         self._btnPrevious.enabled = True
#         self._btnPrevious.setStyleSheet("QPushButton{ background-color: rgb(255,149,0); color: black }")
# #         self._btnPrevious.connect('clicked(bool)',self.onPreviousButtonClicked)
#         self._btnPrevious.clicked.connect(self.onPreviousButtonClicked)
# 
# 
#         # Exit button
#         self._btnExit = qt.QPushButton("Exit")
#         self._btnExit.toolTip = "Save quiz and exit Slicer."
#         self._btnExit.enabled = True
#         self._btnExit.setStyleSheet("QPushButton{ background-color: rgb(255,0,0); color: black; font-weight: bold }")
#         # use lambda to pass argument to this PyQt slot without invoking the function on setup
# #         self._btnExit.connect('clicked(bool)',lambda: self.onExitButtonClicked('ExitBtn'))
#         self._btnExit.clicked.connect(lambda: self.onExitButtonClicked('ExitBtn'))
# 
#         # Repeat button
#         self._btnRepeat = qt.QPushButton("Repeat")
#         self._btnRepeat.toolTip = "Save current responses and repeat."
#         self._btnRepeat.enabled = False
#         self._btnRepeat.visible = False
#         self._btnRepeat.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: black}")
# #         self._btnRepeat.connect('clicked(bool)', self.onRepeatButtonClicked)
#         self._btnRepeat.clicked.connect(self.onRepeatButtonClicked)
# 
# 
#         # Bookmark button
#         self._btnGoToBookmark = qt.QPushButton("Return")
#         self._btnGoToBookmark.toolTip = "Returns to pre-defined page"
#         self._btnGoToBookmark.enabled = True
#         self._btnGoToBookmark.visible = True
#         self._btnGoToBookmark.setStyleSheet("QPushButton{ background-color: rgb(136, 82, 191); color: white; font-weight: bold}")
# #         self._btnGoToBookmark.connect('clicked(bool)', self.onGoToBookmarkButtonClicked)
#         self._btnGoToBookmark.clicked.connect(self.onGoToBookmarkButtonClicked)
#         
# 
#         self.qButtonGrpBoxLayout.addWidget(self._btnExit)
#         self.qButtonGrpBoxLayout.addWidget(qProgressLabel)
#         self.qButtonGrpBoxLayout.addWidget(self.progress)
#         self.qButtonGrpBoxLayout.addWidget(self._btnPrevious)
#         self.qButtonGrpBoxLayout.addWidget(self._btnNext)
#         self.qButtonGrpBoxLayout.addWidget(self._btnRepeat)
#         self.qButtonGrpBoxLayout.addWidget(self._btnGoToBookmark)
# 
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def SetupExtraToolsButtons(self):
#         
#         # create buttons
# 
#         self.tabExtraToolsLayout = qt.QVBoxLayout()
# 
#         
# 
#         # >>>>>>>>>>>>>>>>>>>>
#         # Window/Level interactive mode
#         self.qDisplayMgrGrpBox = qt.QGroupBox()
#         self.qDisplayMgrGrpBox.setTitle("Interactive Modes")
#         self.qDisplayMgrGrpBox.setStyleSheet("QGroupBox{ font-size: 11px; font-weight: bold}")
#         self.qDisplayMgrGrpBoxLayout = qt.QGridLayout()
#         self.qDisplayMgrGrpBoxLayout.addLayout(0,0,1,3)
#         self.qDisplayMgrGrpBox.setLayout(self.qDisplayMgrGrpBoxLayout)
#         
#         self.tabExtraToolsLayout.addWidget(self.qDisplayMgrGrpBox)
# 
#         btnHidden = qt.QPushButton('')
#         btnHidden.enabled = False
#         btnHidden.setStyleSheet("QPushButton{ border:none }")
#         self.qDisplayMgrGrpBoxLayout.addWidget(btnHidden,0,0)
#         
#         
#         self.btnWindowLevel = qt.QPushButton('Window / Level')
#         self.btnWindowLevel.enabled = True
#         self.btnWindowLevel.setCheckable(True)
#         self.btnWindowLevel.setStyleSheet("QPushButton{ background-color: rgb(173,220,237); color: black }")
# #         self.btnWindowLevel.connect('clicked(bool)',self.onWindowLevelClicked)
#         self.btnWindowLevel.clicked.connect(self.onWindowLevelClicked)
#         self.qDisplayMgrGrpBoxLayout.addWidget(self.btnWindowLevel,0,1)
# 
#         btnHidden = qt.QPushButton('')
#         btnHidden.enabled = False
#         btnHidden.setStyleSheet("QPushButton{ border:none }")
#         self.qDisplayMgrGrpBoxLayout.addWidget(btnHidden,0,2)
# 
# 
#         # >>>>>>>>>>>>>>>>>>>>
#         # Crosshairs
#         
#         self.btnCrosshairs = qt.QPushButton('Crosshairs - use Shift key')
#         self.btnCrosshairs.enabled = True
#         self.btnCrosshairs.setCheckable(True)
#         self.btnCrosshairs.setStyleSheet("QPushButton{ background-color: rgb(173,220,237); color: black }")
# #         self.btnCrosshairs.connect('clicked(bool)',self.onCrosshairsClicked)
#         self.btnCrosshairs.clicked.connect(self.onCrosshairsClicked)
#         self.qDisplayMgrGrpBoxLayout.addWidget(self.btnCrosshairs,0,3)
# 
# 
#         btnHidden = qt.QPushButton('')
#         btnHidden.enabled = False
#         btnHidden.setStyleSheet("QPushButton{ border:none }")
#         self.qDisplayMgrGrpBoxLayout.addWidget(btnHidden,0,4)
# 
#         
#         # >>>>>>>>>>>>>>>>>>>>
#         # Viewing modes
#         self.qDisplayOptionsGrpBox = qt.QGroupBox()
#         self.qDisplayOptionsGrpBox.setTitle('Viewing Display Options')
#         self.qDisplayOptionsGrpBox.setStyleSheet("QGroupBox{ font-size: 11px; font-weight: bold}")
#         self.qDisplayOptionsGrpBoxLayout = qt.QGridLayout()
#         self.qDisplayOptionsGrpBox.setLayout(self.qDisplayOptionsGrpBoxLayout)
#         
#         qViewImageLabel = qt.QLabel("Select image:")
#         self.qDisplayOptionsGrpBoxLayout.addWidget(qViewImageLabel,0,0)
#         
#         self.qComboImageList = qt.QComboBox()
#         qSize = qt.QSizePolicy()
#         qSize.setHorizontalPolicy(qt.QSizePolicy.Ignored)
#         self.qComboImageList.setSizePolicy(qSize)
#         self.qDisplayOptionsGrpBoxLayout.addWidget(self.qComboImageList,0,1)
# 
#         qViewNPlanesLabel = qt.QLabel("Select view mode:")
#         self.qDisplayOptionsGrpBoxLayout.addWidget(qViewNPlanesLabel,1,0)
#         
#         self.qComboNPlanesList = qt.QComboBox()
#         self.qDisplayOptionsGrpBoxLayout.addWidget(self.qComboNPlanesList,1,1)
#         self.qComboNPlanesList.addItem("3 Planes")
#         self.qComboNPlanesList.addItem("1 Plane Axial")
#         self.qComboNPlanesList.addItem("1 Plane Sagittal")
#         self.qComboNPlanesList.addItem("1 Plane Coronal")
# 
#         
#         self.btnNPlanesView = qt.QPushButton('Display view')
#         self.btnNPlanesView.enabled = True
#         self.btnNPlanesView.setStyleSheet("QPushButton{ background-color: rgb(0,179,246); color: black }")
# #         self.btnNPlanesView.connect('clicked(bool)', self.onNPlanesViewClicked)
#         self.btnNPlanesView.clicked.connect(self.onNPlanesViewClicked)
#         self.qDisplayOptionsGrpBoxLayout.addWidget(self.btnNPlanesView,0,2)
# 
#         
#         self.btnResetView = qt.QPushButton('Reset to default')
#         self.btnResetView.enabled = True
#         self.btnResetView.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: black }")
# #         self.btnResetView.connect('clicked(bool)', lambda: self.onResetViewClicked('NPlanes'))
#         self.btnResetView.clicked.connect(lambda: self.onResetViewClicked('NPlanes'))
#         self.qDisplayOptionsGrpBoxLayout.addWidget(self.btnResetView,1,2)
# 
#         self.tabExtraToolsLayout.addWidget(self.qDisplayOptionsGrpBox)
#         
# 
#         # >>>>>>>>>>>>>>>>>>>>
#         # Ruler tools
#         self.qLineToolsGrpBox = qt.QGroupBox()
#         self.qLineToolsGrpBox.setTitle('Line Measurement')
#         self.qLineToolsGrpBox.setStyleSheet("QGroupBox{ font-size: 11px; font-weight: bold}")
#         self.qLineToolsGrpBoxLayout = qt.QGridLayout()
#         self.qLineToolsGrpBox.setLayout(self.qLineToolsGrpBoxLayout)
# 
# 
#  
#         self.slMarkupsLineWidget = slicer.qSlicerMarkupsPlaceWidget()
#         # Hide all buttons and only show delete button
#         self.slMarkupsLineWidget.buttonsVisible=False
#         self.slMarkupsLineWidget.deleteButton().show()
#         self.qLineToolsGrpBoxLayout.addWidget(self.slMarkupsLineWidget,0,0)
# 
#         # remove the last point of markup line created
#         qLineToolLabelTrashPt = qt.QLabel('Remove last point')
#         qLineToolLabelTrashPt.setAlignment(QtCore.Qt.AlignCenter)
#         self.qLineToolsGrpBoxLayout.addWidget(qLineToolLabelTrashPt,1,0)
#         
#         # Clear all markup lines
#         self.btnClearLines = qt.QPushButton("Clear all")
#         self.btnClearLines.toolTip = "Remove all markup lines."
#         self.btnClearLines.enabled = True
#         self.btnClearLines.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: black }")
# #         self.btnClearLines.connect('clicked(bool)',self.onClearLinesButtonClicked)
#         self.btnClearLines.clicked.connect(self.onClearLinesButtonClicked)
#         self.qLineToolsGrpBoxLayout.addWidget(self.btnClearLines,0,1)
# 
#         self.btnAddMarkupsLine = qt.QPushButton("Add new line")
#         self.btnAddMarkupsLine.enabled = True
#         self.btnAddMarkupsLine.setStyleSheet("QPushButton{ background-color: rgb(0,179,246); color: black }")
# #         self.btnAddMarkupsLine.connect('clicked(bool)', self.onAddLinesButtonClicked)
#         self.btnAddMarkupsLine.clicked.connect(self.onAddLinesButtonClicked)
#         self.qLineToolsGrpBoxLayout.addWidget(self.btnAddMarkupsLine,0,2)
#         
#         # Markup display view visibility
#         self.qChkBoxViewOnAllDisplays = qt.QCheckBox('Display in all views')
#         self.qChkBoxViewOnAllDisplays.setChecked(False)
#         self.qChkBoxViewOnAllDisplays.setStyleSheet("margin-left:75%")
#         self.qChkBoxViewOnAllDisplays.stateChanged.connect(self.onViewLinesOnAllDisplaysStateChanged)
#         self.qLineToolsGrpBoxLayout.addWidget(self.qChkBoxViewOnAllDisplays,1,2)
#         
#         # Markup measurement visibility
#         self.qChkBoxMeasurementVisibility = qt.QCheckBox('Show length')
#         self.qChkBoxMeasurementVisibility.setChecked(True)
#         self.qChkBoxMeasurementVisibility.setStyleSheet("margin-left:75%")
#         self.qChkBoxMeasurementVisibility.stateChanged.connect(self.onMeasurementVisibilityStateChanged)
#         self.qLineToolsGrpBoxLayout.addWidget(self.qChkBoxMeasurementVisibility,2,2)
#  
#         
#         
#         self.tabExtraToolsLayout.addWidget(self.qLineToolsGrpBox)
# 
#         # >>>>>>>>>>>>>>>>>>>>
#         # Contour visibility tools
#         self.qContourVisibilityGrpBox = qt.QGroupBox()
#         self.qContourVisibilityGrpBox.setTitle('Contour Visibility - Fill/Outline and Opacity')
#         self.qContourVisibilityGrpBox.setStyleSheet("QGroupBox{ font-size: 11px; font-weight: bold}")
#         self.qContourVisibilityGrpBoxLayout = qt.QHBoxLayout()
#         self.qContourVisibilityGrpBox.setLayout(self.qContourVisibilityGrpBoxLayout)
# 
#         qLabelOpacity = qt.QLabel(' Opacity')
#         qLabelOpacity.setMinimumWidth(200)
#         qLabelOpacity.setAlignment(QtCore.Qt.AlignRight)
#         self.qContourVisibilityGrpBoxLayout.addWidget(qLabelOpacity)
#         
#         self.qVisibilityOpacity = qt.QSlider(QtCore.Qt.Horizontal)
#         self.qVisibilityOpacity.setMinimum(0)
#         self.qVisibilityOpacity.setMaximum(100)
#         self.qVisibilityOpacity.setValue(50)
#         self.qVisibilityOpacity.setPageStep(1)
#         self.qVisibilityOpacity.connect("valueChanged(int)", self.SetContourOpacityFromSliderValue)
#         self.qContourVisibilityGrpBoxLayout.addWidget(self.qVisibilityOpacity)
#         self.qContourVisibilityGrpBoxLayout.addSpacing(30)
# 
#         self.qChkBoxFillOrOutline = qt.QCheckBox('Fill')
#         self.qChkBoxFillOrOutline.stateChanged.connect(self.onContourDisplayStateChanged)
#         self.qContourVisibilityGrpBoxLayout.addWidget(self.qChkBoxFillOrOutline)
#         self.qContourVisibilityGrpBoxLayout.addSpacing(30)
# 
# 
#         self.tabExtraToolsLayout.addWidget(self.qContourVisibilityGrpBox)
#         
#         self.tabExtraToolsLayout.addStretch()
#         
# 
#         return self.tabExtraToolsLayout
#     
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def EnableButtons(self):
#         
#         
#         # for Repeat button
#         if self.oCustomWidgets.GetPageLooping(self.GetCurrentPageIndex()):
#             self._btnRepeat.visible = True
#             
#             
#             # only enable Repeat button in looping if the page is not complete and the user is on the last question set
#             
#             if self.oCustomWidgets.GetPageCompleteAttribute(self.GetCurrentPageIndex()) == False:
#                 if self.CheckForLastQuestionSetForPage() == True:
#                     self._btnRepeat.enabled = True
#                     self._btnRepeat.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: black}")
#                     
#                     # check if button script rerun is required
#                     if self.oCustomWidgets.GetButtonScriptRerunRequired(self.GetCurrentPageIndex()):
#                         if self.CheckIfLastRepAndNextPageIncomplete() == True:
#                             self._btnRepeat.enabled = True
#                             self._btnRepeat.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: black}")
#                         else: # force user to step through subsequent reps
#                             self._btnRepeat.enabled = False
#                             self._btnRepeat.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: white}")
#                             
#                 else:
#                     self._btnRepeat.enabled = False
#                     self._btnRepeat.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: white}")
#             else:
#                 self._btnRepeat.enabled = False
#                 self._btnRepeat.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: white}")
#                     
# 
#         else:
#             self._btnRepeat.visible = False
#             self._btnRepeat.enabled = False
#             self._btnRepeat.setStyleSheet("QPushButton{ background-color: rgb(211,211,211); color: white}")
# 
#             
#             
#         # assign button description           
#         if (self.GetCurrentNavigationIndex() == len(self.GetNavigationList()) - 1):
#             self._btnNext.setText("Finish")
#         else:
#             self._btnNext.setText("Next")
#         
#         # beginning of quiz
#         if (self.GetCurrentNavigationIndex() == 0):
#             self._btnNext.enabled = True
#             self._btnPrevious.enabled = False
# 
#         # end of quiz
#         elif (self.GetCurrentNavigationIndex() == len(self.GetNavigationList()) - 1):
#             self._btnNext.enabled = True
#             self._btnPrevious.enabled = True
# 
#         # somewhere in middle
#         else:
#             self._btnNext.enabled = True
#             self._btnPrevious.enabled = True
# 
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def DisableButtons(self):
#         self._btnNext.enabled = False
#         self._btnPrevious.enabled = False
#         self._btnRepeat.enabled = False
# 
# 
# 
#         
# 
#     #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#     #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# 
# 
# ##########################################################################
# #
# # class SlicerInterface
# #
# ##########################################################################
# 
# class SlicerInterface:
#     
#     def __init__(self, oFilesIOInput, parent=None):
#         self.sClassName = type(self).__name__
#         self.parent = parent
# #         print('Constructor for SlicerInterface')
#         
#         self.oFilesIO = oFilesIOInput
#         
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# 
# 
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def ClearLayout(self, layout):
#         # remove widgets from layout - ready for new widgets
#         for i in reversed(range(layout.count())):
#             widget = layout.takeAt(i).widget()
#             if widget != None:
#                 widget.deleteLater()
# 
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def CreateLeftLayoutAndWidget(self):
#         
#         # create a layout for the quiz to go in Slicer's left widget
#         self.qLeftLayout = qt.QVBoxLayout()
#         
#         # add the quiz main layout to Slicer's left widget
#         self.qLeftWidget = qt.QWidget()
#         self.qLeftWidget.setLayout(self.qLeftLayout)
# 
#     
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def AddQuizTitle(self):
#         
#         qTitleGroupBox = qt.QGroupBox()
#         qTitleGroupBoxLayout = qt.QHBoxLayout()
#         qTitleGroupBox.setLayout(qTitleGroupBoxLayout)
#                                 
#         qLogoImg = qt.QLabel(self)
#         sLogoName = 'BainesChevrons.png'
#         sLogoPath = os.path.join(self.oFilesIO.GetScriptedModulesPath(),'Resources','Icons',sLogoName)
#         pixmap = qt.QPixmap(sLogoPath)
# #         pixmapTarget = pixmap.scaled(pixmap.height()-430, pixmap.width()-430, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation);
# #         qLogoImg.setPixmap(pixmapTarget)
#         qLogoImg.setPixmap(pixmap)
#         qLogoImg.setAlignment(QtCore.Qt.AlignCenter)
# 
#         qTitle = qt.QLabel('Baines Image Quizzer')
# #         qTitle.setMinimumHeight(pixmap.height())
#         qTitle.setFont(qt.QFont('Arial',12, qt.QFont.Bold))
#         qTitle.setAlignment(QtCore.Qt.AlignCenter)
# 
#         qTitleGroupBoxLayout.addWidget(qLogoImg)
#         qTitleGroupBoxLayout.addWidget(qTitle)
#         
#         qTitleGroupBoxLayout.setSpacing(20)
#         qTitleGroupBoxLayout.addStretch()
#         
#         
#         return qTitleGroupBox
#         
#  
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def AddQuizLayoutWithTabs(self):
# 
#         # setup the tab widget
#         self.qTabWidget = qt.QTabWidget()
#         qTabQuiz = qt.QWidget()
#         self.qTabWidget.addTab(qTabQuiz,"Quiz")
#         self.qTabWidget.setStyleSheet("QTabBar{ font: bold 9pt}")
#         
#         
#         # Layout within the tab widget - form needs a frame
#         self.qQuizLayout = qt.QFormLayout(qTabQuiz)
#         quizFrame = qt.QFrame(qTabQuiz)
#         quizFrame.setLayout(qt.QVBoxLayout())
#         self.qQuizLayout.addWidget(quizFrame)
#     
#         # add to left layout
#         self.qLeftLayout.addWidget(self.qTabWidget)
# 
# ##########################################################################
# #
# # class SlicerWindowSize
# #
# ##########################################################################
#  
# class SlicerWindowSize:
#      
#     def __init__(self, parent=None):
#         self.slMainWindowPos = None
#         self.slMainWindowWidth = 0
#         self.slMainWindowHeight = 0
#          
#         self.CaptureWindowSize()
#          
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def CaptureWindowSize(self):
#         slMainWindow = slicer.util.mainWindow()
#         self.slMainWindowPos = slMainWindow.pos
#         self.slMainWindowWidth = slMainWindow.geometry.width()
#         self.slMainWindowHeight = slMainWindow.geometry.height()
