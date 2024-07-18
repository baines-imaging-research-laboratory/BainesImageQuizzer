# import PythonQt
import os
import vtk, qt, ctk, slicer
import sys
import unittest
import random
import traceback
from copy import deepcopy

import Utilities.UtilsMsgs as UtilsMsgs
import Utilities.UtilsFilesIO as UtilsFilesIO
import Utilities.UtilsEmail as UtilsEmail
import Utilities.UtilsValidate as UtilsValidate
import Utilities.UtilsIOXml as UtilsIOXml
import Utilities.UtilsCustomXml as UtilsCustomXml

from Utilities.UtilsCustomXml import *
from Utilities.UtilsIOXml import *
from Utilities.UtilsMsgs import *
from Utilities.UtilsFilesIO import *
from Utilities.UtilsEmail import *
from Utilities.UtilsValidate import *

from QuestionSet import *
from ImageView import *
from PageState import *
from UserInteraction import *
from CustomWidgets import *
from CoreWidgets import *


from slicer.util import EXIT_SUCCESS


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

       
        self.oUserInteraction = None

        self.oImageView = None
        
        self.oCustomWidgets = CustomWidgets()
        self.oCoreWidgets = CoreWidgets(self)
        
        
        self.loCurrentQuizImageViewNodes = []
        self.liImageDisplayOrder = []
        self.lsLayoutWidgets = []

        self.setupTestEnvironment()
        

    #----------
    def __del__(self):

        # clean up of editor observers and nodes that may cause memory leaks (color table?)
        if self.oCoreWidgets.GetTabIndex('SegmentEditor') > 0:
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
    def SetupCoreWidgets(self):
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
    def RunSetup(self, slicerMainLayout):
        
        sMsg = ''
        try:
            self.SetupCoreWidgets()

            self.oPageState = PageState(self)

            # open xml and check for root node
            bSuccess = self.oCustomWidgets.OpenQuiz()
            
    
            if bSuccess == False:
                sMsg = "ERROR   -    Not a valid quiz - Trouble with Quiz syntax."
                raise
    
            else:
                
                self.oMaximizedWindowSize = SlicerWindowSize()

                
                # >>>>>>>>>>>>>>>>> Widgets <<<<<<<<<<<<<<<<<<<<

                self.oCoreWidgets.SetupWidgets(slicerMainLayout)
                self.oCoreWidgets.oSlicerInterface.qLeftWidget.activateWindow()
                
                self.oCoreWidgets.AddExtraToolsTab()
    
                
                # turn on functionality if any page contains the attribute
                self.oCoreWidgets.AddSegmentationModule( self.oCustomWidgets.GetSegmentationModuleRequired())
                
                # set up and initialize Session attributes
                UtilsFilesIO.SetupROIColorFile(self.oCustomWidgets.GetROIColorFile())
                self.oCoreWidgets.SetROIColorSpinBoxLabels(\
                                    UtilsValidate.GetROIColorSpinBoxDefaultLabel(), UtilsValidate.GetROIListValidLabels())
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
                    self.oCustomWidgets.AddSessionLoginTimestamp()
                    self.oCustomWidgets.AddUserNameAttribute()
                    
                    
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
            UtilsMsgs.DisplayError(sMsg)
            
    
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
            self.oCoreWidgets.SetROIColorSpinBoxLabels( UtilsValidate.GetROIColorSpinBoxDefaultLabel(),\
                                                       UtilsValidate.GetROIListValidLabels())

    
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
            UtilsMsgs.DisplayError(sMsg)
            
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def DisplayImageLayout(self, sCaller=None):

        try:
            self.oCoreWidgets.EnableTabBar(False)
            
            self.lsLayoutWidgets = self.oCustomWidgets.SetViewingLayout(self.GetCurrentPageIndex())
    
            # set up the images on the page
            self.oImageView = ImageView()
            self.oCoreWidgets.SetImageView(self.oImageView)
            
            self.oImageView.RunSetup(self.oCustomWidgets.GetNthPageNode(self.GetCurrentPageIndex()),\
                                      UtilsFilesIO.GetDataParentDir())
            
    
            # load label maps and markup lines if a path has been stored in the xml for the images on this page
            UtilsFilesIO.LoadSavedLabelMaps(self)
            UtilsFilesIO.LoadSavedMarkupLines(self)

    
            # assign each image node and its label map (if applicable) to the viewing widget
            self.oImageView.AssignNodesToView()
            
            if sCaller == 'ResetView':
                self.oImageView.SetNewLabelMapsVisible()
            
            self.oCoreWidgets.SetNPlanesComboBoxImageNames()
    
            self.ApplySavedImageState()

            self.oCoreWidgets.ResetExtraToolsDefaults()
        
            self.oCoreWidgets.EnableTabBar(True)
        except:
            iPage = self.GetCurrentPageIndex() + 1
            tb = traceback.format_exc()
            sMsg = "Session:DisplayImageLayout: Error trying to display images. Page: " + str(iPage) \
                   + "\n\n" + tb 
            UtilsMsgs.DisplayError(sMsg)
    

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
        
        
                bLabelMapsSaved, sLabelMapMsg = UtilsFilesIO.SaveLabelMaps(self, sCaller)
                UtilsFilesIO.SaveMarkupLines(self)
      
                sCaptureSuccessLevel, lsNewResponses, sMsg = self.CaptureNewResponses()
                self.SetNewResponses(lsNewResponses)
                   
                if sCaller == 'NextBtn' or sCaller == 'Finish' or sCaller == 'Repeat':
                    # only write to xml if all responses were captured
                    if sCaptureSuccessLevel == 'AllResponses':
                        self.SaveResponses()
                        bResponsesSaved = True
                    else:
                        sMsg = sMsg + '\n\nAll questions must be answered to proceed'
                        UtilsMsgs.DisplayWarning( sMsg )
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
                        self.oCustomWidgets.SetPageIncomplete(self.GetCurrentPageIndex())
                        

                if bLabelMapsSaved and bResponsesSaved:
                    bSaveComplete = True
                
                sReturnMsg = sLabelMapMsg + sMissingMsg
                
                
                # tag new response with event 
                if bResponsesSaved == True:
                    if sCaller == 'EventFilter':
                        sEventMsg = 'Exit ...X'
                    elif sReturnMsg !='':
                        sEventMsg = sReturnMsg
                    else:
                        sEventMsg = sCaller
                    UtilsCustomXml.TagResponse( self.oCustomWidgets.GetCurrentQuestionSetNode(\
                                                            self.GetCurrentPageIndex(),\
                                                            self.GetCurrentQuestionSetIndex()),\
                                                    sEventMsg,\
                                                    UtilsFilesIO.GetUserQuizResultsPath())                
        
        
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
                
                if not self.oCoreWidgets.GetNPlanesViewingMode():
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
                        dictViewModeAttributes = {"Orientation": sOrientation, "Destination": sWidgetName, "ViewingMode": self.oCoreWidgets.GetViewingMode()}
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
                    self.oCustomWidgets.SaveQuiz(UtilsFilesIO.GetUserQuizResultsPath())
    
        except:
            bSuccess = False
            iPage = self.GetCurrentPageIndex() + 1
            tb = traceback.format_exc()
            sMsg = "CaptureAndSaveImageState: Error saving the image state. Current page: " + str(iPage) \
                   + "\n\n" + tb 
            UtilsMsgs.DisplayError(sMsg)
            
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
        
        if not self.oCoreWidgets.GetNPlanesViewingMode():
            loImageNodes = self.oImageView.GetImageViewList()
        else:
            oImageNodeOverride, iQuizImageIndex = self.oCoreWidgets.GetNPlanesImageComboBoxSelection()
            loImageNodes.append(oImageNodeOverride)
            for i in range(len(self.oCoreWidgets.llsNPlanesOrientDest)):
                lsRequiredOrientations.append(self.oCoreWidgets.llsNPlanesOrientDest[i][0])
                dictNPlanesOrientDest.update({self.oCoreWidgets.llsNPlanesOrientDest[i][0] : self.oCoreWidgets.llsNPlanesOrientDest[i][1]})
            
        for ind in range(len(loImageNodes)):
            if self.oCoreWidgets.GetNPlanesViewingMode():
                oImageNode = loImageNodes[ind]
            else:
                oImageNode = loImageNodes[self.GetImageDisplayOrderIndices()[ind]]
                
            dictImageState = {}
            
            if (oImageNode.sImageType == "Volume" or oImageNode.sImageType == "VolumeSequence"):

                if self.oCoreWidgets.GetViewingMode() == "Default":
                    lsRequiredOrientations = [oImageNode.sOrientation]
                    
                bLatestWindowLevelFound = False
                ldictAllImageStateItems =\
                    self.oCustomWidgets.GetStateElementsForMatchingImagePath(UtilsFilesIO.GetRelativeDataPath(oImageNode.sImagePath), self.GetCurrentPageIndex())
    
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
                    if not self.oCoreWidgets.GetNPlanesViewingMode():
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
                            
                        if not self.oCoreWidgets.GetNPlanesViewingMode():
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
            if not self.oCoreWidgets.GetNPlanesViewingMode():
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
                     
                    self.oCustomWidgets.SaveQuiz(UtilsFilesIO.GetUserQuizResultsPath())
                     
         
        except Exception:
            tb = traceback.format_exc()
            sMsg = 'Error writing responses to results file' + '\n Does this file exist? : \n' \
                + UtilsFilesIO.GetUserQuizResultsPath()\
                + '\n\n' + tb
            # critical error - exit
            UtilsMsgs.DisplayError( sMsg )
             
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
        sCompletionFlagMsg = self.oPageState.UpdateCompletedFlags(self.oCustomWidgets.GetNthPageNode(self.GetCurrentPageIndex()))
        
        
        if sCaller == 'NextBtn' or sCaller == 'Finish' or sCaller == 'Repeat':
            
            # if this was the last question set for the page, check for completion
            if idxQuestionSet == iNumQSets - 1:
                
                if self.oPageState.GetPageCompletedTF():
                    bPageStateComplete = True
                    self.oCustomWidgets.AddPageCompleteAttribute(self.GetCurrentPageIndex())
                    
                    if sCaller == 'Finish':
                        self.oCustomWidgets.AddQuizCompleteAttribute()
                        self.oCustomWidgets.SetQuizComplete(True)
    
                else:
                    bPageStateComplete = False
                    UtilsMsgs.DisplayWarning( sCompletionFlagMsg )
                    sReturnMsg = ' ... missing requirement for Page (contours / markuplines / questions) '
                        

        else:      # for 'Previous' 'GoToBookmark' 'Exit' 'EventFilter (exit)'
            if sCaller == 'ExitBtn' or sCaller == 'EventFilter':
                if not self.oPageState.GetPageCompletedTF() and not self.oCustomWidgets.GetQuizComplete():
                    self.oCustomWidgets.SetPageIncomplete(self.GetCurrentPageIndex())  # for Quiz resuming
                    
            bPageStateComplete = True    # allow with unfinished requirements
            
        if sReturnMsg != '':
            # update not required on missing questions as a new response element is not saved
            if 'question' not in sCompletionFlagMsg:
                UtilsCustomXml.TagResponse( self.oCustomWidgets.GetCurrentQuestionSetNode(\
                                                        self.GetCurrentPageIndex(),\
                                                        self.GetCurrentQuestionSetIndex()),\
                                                sReturnMsg,\
                                                UtilsFilesIO.GetUserQuizResultsPath())                
                                    
        return bPageStateComplete, sReturnMsg
    

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ExitOnQuizComplete(self):
        """ the last index in the composite navigation indices list was reached
            the quiz was completed - exit
        """
        self.QueryThenSendEmailResults()
        UtilsMsgs.DisplayInfo('Quiz Complete - Exiting')
        slicer.util.exit(status=EXIT_SUCCESS)
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def QueryThenSendEmailResults(self):
        
        if self.oCustomWidgets.GetEmailResultsRequest() and self.oCustomWidgets.GetQuizComplete():
            sMsg = 'Ready to email results?'
            qtEmailAns = UtilsMsgs.DisplayYesNo(sMsg)
    
            if qtEmailAns == qt.QMessageBox.Yes:
    
                sArchiveFilenameWithPath = os.path.join(UtilsFilesIO.GetUserDir(), UtilsFilesIO.GetQuizFilenameNoExt())
                sPathToZipFile = UtilsIOXml.ZipXml(sArchiveFilenameWithPath, UtilsFilesIO.GetUserQuizResultsDir())
                
                if sPathToZipFile != '':
                    UtilsEmail.SendEmail(sPathToZipFile)
                else:
                    sMsg = 'Trouble archiving quiz results: ' + sPathToZipFile
                    UtilsMsgs.DisplayError(sMsg)
        
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
        
        
        self.SetNavigationList(UtilsCustomXml.GetQuizLayoutForNavigationList(UtilsIOXml.GetRootNode()))
        
        # if randomization is requested - shuffle the page/questionset list
        if self.oCustomWidgets.GetRandomizeRequired():
            # check if xml already holds a set of randomized indices otherwise, call randomizing function
            liRandIndices = self.oCustomWidgets.GetStoredRandomizedIndices()
            if liRandIndices == []:
                # get the unique list  of all Page Group numbers to randomize
                #    this was set during xml validation during the initial read
                liIndicesToRandomize = UtilsValidate.GetListUniquePageGroups()
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
            if self.oCustomWidgets.GetEmailResultsRequest():
                sMsg = sMsg + '\n\nClick No to exit. You will have the option to email results.'
            else:
                sMsg = sMsg + '\n\nClick No to exit.'
                
            qtAns = UtilsMsgs.DisplayYesNo(sMsg)

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
                UtilsMsgs.DisplayInfo('Resuming quiz from previous login session.')
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
            sXmlFilePath = UtilsFilesIO.GetUserQuizResultsPath()   # for live run
         
        indXmlPageToRepeat = self.GetCurrentPageIndex()
         
        indNextXmlPageWithRep0, iCopiedRepNum = self.oCustomWidgets.RepeatNode(indXmlPageToRepeat, sXmlFilePath) 


###         UtilsIOXml.SaveXml(sXmlFilePath)    # for debug
        self.oCustomWidgets.SaveQuiz(sXmlFilePath)
        self.BuildNavigationList() # update after adding xml page
         
        iNewNavInd = self.FindNewRepeatedPosition(indNextXmlPageWithRep0, iCopiedRepNum)
        self.SetCurrentNavigationIndex(iNewNavInd)
     
        # update the repeated page
        self.oCustomWidgets.AdjustQuizResultsFileForRepeatedPage(\
                 self.GetNavigationPage(iNewNavInd),\
                 self.GetNavigationPage( self.GetCurrentNavigationIndex() - 1) )



###         UtilsIOXml.SaveXml(sXmlFilePath)    # for debug
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
         
        sCurrentPageID = self.oCustomWidgets.GetPageID(self.GetCurrentPageIndex())
  
          
        sRepNum = self.oCustomWidgets.GetPageRep(self.GetCurrentPageIndex())
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
      
        # if next page is complete, then Repeat button will be disabled;
        #    user will have to step through until the next incomplete page  
        if bNextPageComplete:
            bLastPageComplete = False
         
        if bLastLoopingRep and bLastPageComplete:
            bEndOfLoopAndNextPageIncomplete = True  # enables Repeat button 
         
        return bEndOfLoopAndNextPageIncomplete
     


