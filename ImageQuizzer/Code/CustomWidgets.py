import os
import vtk, qt, ctk, slicer
import sys
import unittest

from Utilities.UtilsIOXml import *
from Utilities.UtilsFilesIO import *
from Utilities.UtilsMsgs import *
from Utilities.UtilsEmail import *

from UserInteraction import *


##########################################################################
#
# class CustomWidgets
#
##########################################################################

class CustomWidgets:
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #-------------------------------------------
    #        Custom Widgets
    #-------------------------------------------
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, oIOXml, oFilesIO, parent=None):
        self.sClassName = type(self).__name__
        self.parent = parent
        
        self._sLoginTime = ''
        self._bQuizComplete = False
        self._bEmailResults = False
        self._bUserInteractionLog = False
        self._fhInteractionLog = None
        self._bBtnScriptRerunRequired = False
        self._xPageNode = None
        self._sPageID = ''
        self._sPageDescriptor = ''
        self._sPageRep = ''
        self._bAllowMultipleResponse = False
        self._bRandomizeRequired = False
        self._bPageLooping = False
        self._sSessionContourVisibility = ''
        self._fContourToolRadius = 0
#         self._xRootNode = None
        
        self.oUtilsMsgs = UtilsMsgs()
        self.oIOXml = oIOXml
        self.oFilesIO = oFilesIO


        self.setupTestEnvironment()

    #----------
    def setupTestEnvironment(self):
        # check if function is being called from unit testing
        if "testing" in os.environ:
            self.sTestMode = os.environ.get("testing")
        else:
            self.sTestMode = "0"
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #-------------------------------------------
    #        Getters / Setters
    #-------------------------------------------
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    #----------
    def SetIOXml(self, oIOXml):
        self.oIOXml = oIOXml
        
    #----------
    def SetFilesIO(self, oFilesIO):
        self.oFilesIO = oFilesIO

    #----------
    def OpenQuiz(self, oFilesIO):
        bSuccess = self.oIOXml.OpenXml(oFilesIO.GetUserQuizResultsPath(),'Session')

        return bSuccess
    
    #----------
    def GetXmlUtils(self):
        return self.oIOXml
        
    #----------
    def SetRootNode(self, xInputNode):
        self._xRootNode = xInputNode
        
    #----------
    def GetRootNode(self):
#         return self._xRootNode
        return self.oIOXml.GetRootNode()
        
    #----------
    def SetLoginTime(self, sTime):
        self._sLoginTime = sTime
        
    #----------
    def LoginTime(self):
        return self._sLoginTime
    
    #----------
    def SetQuizComplete(self, bInput):
        self._bQuizComplete = bInput
        
    #----------
    def GetQuizComplete(self):
        return self._bQuizComplete
            
    #----------
    def GetPageDescriptor(self, iPageIndex):
        xmlPageNode = self.oIOXml.GetNthChild(self.GetRootNode(), 'Page', iPageIndex)
        self._sPageDescriptor = self.oIOXml.GetValueOfNodeAttribute(xmlPageNode, 'Descriptor')
        return self._sPageDescriptor

    #----------
    def SetEmailResultsRequest(self, oUtilsEmail, oFilesIO):
        self._bEmailResults = oUtilsEmail.SetupEmailResults(oFilesIO, \
                            self.oIOXml.GetValueOfNodeAttribute(self.GetRootNode(), 'EmailResultsTo'))
        
    #----------
    def GetEmailResultsRequest(self):
        return self._bEmailResults
    
    #----------
#     def SetSessionContourVisibilityDefault(self):
#         # quiz validation checked for valid values
#         # if no attribute exists, set with the default
#         self._sSessionContourVisibility = self.oIOXml.GetValueOfNodeAttribute(self.GetRootNode(), 'ContourVisibility')
#         if self._sSessionContourVisibility == '':
#             self._sSessionContourVisibility = 'Outline'  # default
            
    #----------
    def GetSessionContourVisibilityDefault(self):
        # quiz validation checked for valid values
        # if no attribute exists, set with the default
        self._sSessionContourVisibility = self.oIOXml.GetValueOfNodeAttribute(self.GetRootNode(), 'ContourVisibility')
        if self._sSessionContourVisibility == '':
            self._sSessionContourVisibility = 'Outline'  # default
            
        return self._sSessionContourVisibility
    
#     #----------
#     def SetPageID(self, iPageIndex):
#         xmlPageNode = self.oIOXml.GetNthChild(self.GetRootNode(), 'Page', iPageIndex)
#         self._sPageID = self.oIOXml.GetValueOfNodeAttribute(xmlPageNode, 'ID')
        
    #----------
    def GetPageID(self, iPageIndex):
        xmlPageNode = self.oIOXml.GetNthChild(self.GetRootNode(), 'Page', iPageIndex)
        self._sPageID = self.oIOXml.GetValueOfNodeAttribute(xmlPageNode, 'ID')
        return self._sPageID

#     #----------
#     def SetPageDescriptor(self, iPageIndex):
#         xmlPageNode = self.oIOXml.GetNthChild(self.GetRootNode(), 'Page', iPageIndex)
#         self._sPageDescriptor = self.oIOXml.GetValueOfNodeAttribute(xmlPageNode, 'Descriptor')
#         

    #----------
    def GetPageRep(self, iPageIndex):
        xmlPageNode = self.oIOXml.GetNthChild(self.GetRootNode(), 'Page', iPageIndex)
        self._sPageRep = self.oIOXml.GetValueOfNodeAttribute(xmlPageNode, 'Rep')
        return self._sPageRep

    #----------
    def SetUserInteractionLogRequest(self, xPageNode):
        ''' Function to define whether a page is to be set for user interaction logging.
            If logging is on - the Slicer layout is locked down otherwise, 
                window and widget resizing is enabled.
        '''

        sUserInteractionLog = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'UserInteractionLog')

        if sUserInteractionLog == 'Y':
            self._bUserInteractionLog = True
            
        else:
            self._bUserInteractionLog = False


#         if self.oUserInteraction == None:
#             self.oUserInteraction = UserInteraction()
#             
#         self.oUserInteraction.Lock_Unlock_Layout(self.oMaximizedWindowSize, self.GetUserInteractionLogRequest())
        
            
        
    #----------
    def GetUserInteractionLogRequest(self):
        return self._bUserInteractionLog
    
    #----------
    def GetGoToBookmarkRequest(self, iPageIndex):
        
        xPageNode = self.GetNthPageNode(iPageIndex)
        lsBookmarkRequest = []
        sGoToBookmarkRequest =  self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'GoToBookmark')
        
        if sGoToBookmarkRequest != '':
            lsBookmarkRequest = sGoToBookmarkRequest.split()
            
        return lsBookmarkRequest
        
    #----------
    def SetMultipleResponseAllowed(self,iPageIndex):
        
        xPageNode = self.GetNthPageNode(iPageIndex)
        sYN = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'AllowMultipleResponse')

        if sYN == 'y' or sYN == 'Y':
            self._bAllowMultipleResponse = True
        else: # default
            self._bAllowMultipleResponse = False

    #----------
    def SetMultipleResponse(self, bInput):
        self._bAllowMultipleResponse = bInput
    #----------
    def GetMultipleResponseAllowed(self):
        return self._bAllowMultipleResponse
            
    #----------
    def GetROIColorFile(self):
        return self.oIOXml.GetValueOfNodeAttribute(self.GetRootNode(), 'ROIColorFile') 

    #----------
    def GetPageCompleteAttribute(self, iPageIndex):
        bPageComplete = False
        xPageNode = self.oIOXml.GetNthChild(self.GetRootNode(), 'Page', iPageIndex)

        sPageComplete = self.oIOXml.GetValueOfNodeAttribute(xPageNode,'PageComplete')
        if sPageComplete == "Y":
            bPageComplete = True
        
        return bPageComplete
        
    #----------
    def GetAllQuestionSetsForNthPage(self, iPageIndex):
        self._xPageNode = self.oIOXml.GetNthChild(self.GetRootNode(), 'Page', iPageIndex)
        xNodesAllQuestionSets = self.oIOXml.GetChildren(self._xPageNode, 'QuestionSet')
        
        return xNodesAllQuestionSets

    #----------
    def GetAllQuestionSetNodesForCurrentPage(self, iPageIndex):
        xPageNode = self.GetNthPageNode(iPageIndex)
        xAllQuestionSetNodes = self.oIOXml.GetChildren(xPageNode, 'QuestionSet')
        
        return xAllQuestionSetNodes
    #----------
    def GetNthQuestionSetForCurrentPage(self, idxQSet, iPageIndex):
        xPageNode = self.GetNthPageNode(iPageIndex)
        xQuestionSetNode = self.oIOXml.GetNthChild(xPageNode, 'QuestionSet', idxQSet)
        
        return xQuestionSetNode
        
    #----------
    def GetNthPageNode(self,iPageIndex):
        ''' From the  navigation index in the composite indices list, get the page index.
            Return the nth page node (using the page index) from the root.
        '''
#         iPageIndex = self.GetNavigationPage(self.GetCurrentNavigationIndex())
        xPageNode = self.oIOXml.GetNthChild(self.GetRootNode(), 'Page', iPageIndex)
        
        return xPageNode
    
#     #----------
#     def GetNthPageNode(self, iPageIndex):
#         xPageNode = self.oIOXml.GetNthChild(self.GetRootNode(), 'Page', iPageIndex)
#         return xPageNode
#         
    #----------
    def GetImageElements(self, iPageIndex):
        lxImageElements = self.oIOXml.GetChildren(self.GetNthPageNode(iPageIndex), 'Image')
        return lxImageElements
    
    #----------
    def GetCurrentQuestionSetNode(self, iPageIndex, iQSetIndex):
#         iQSetIndex = self.GetNavigationQuestionSet(self.GetCurrentNavigationIndex())
        xPageNode = self.GetNthPageNode(iPageIndex)
        xQuestionSetNode = self.oIOXml.GetNthChild(xPageNode, 'QuestionSet', iQSetIndex)
        
        return xQuestionSetNode

    #----------
    def GetCurrentQuestionNode(self, iPageIndex, iQSetIndex, iQuestionIndex):
        xQSetNode = self.GetCurrentQuestionSetNode(iPageIndex, iQSetIndex)
        xQuestionNode = self.oIOXml.GetNthChild(xQSetNode, 'Question', iQuestionIndex)
    
        return xQuestionNode
 
#     #----------
#     def GetAllQuestionsForCurrentQuestionSet(self):
#         xCurrentQuestionSetNode = self.GetCurrentQuestionSetNode()
#         xAllQuestionNodes = self.oIOXml.GetChildren(xCurrentQuestionSetNode, 'Question')
#         
#         return xAllQuestionNodes
    
    #----------
    def GetNthOptionNode(self, iPageIndex, iQSetIndex, indQuestion, indOption):

        xQuestionSetNode = self.GetCurrentQuestionSetNode(iPageIndex, iQSetIndex)
        xQuestionNode = self.oIOXml.GetNthChild(xQuestionSetNode, 'Question', indQuestion)
        xOptionNode = self.oIOXml.GetNthChild(xQuestionNode, 'Option', indOption)
        
        return xOptionNode
        
    #----------
    def GetAllOptionNodes(self, iPageIndex, iQSetIndex, indQuestion):

        xQuestionSetNode = self.GetCurrentQuestionSetNode(iPageIndex, iQSetIndex)
        xQuestionNode = self.oIOXml.GetNthChild(xQuestionSetNode, 'Question', indQuestion)
        xAllOptionNodes = self.oIOXml.GetChildren(xQuestionNode,'Option')
        
        return xAllOptionNodes
        
    #----------
    def GetPageLooping(self, iPageIndex):
        
        self._bPageLooping = False
        xPageNode = self.GetNthPageNode(iPageIndex)
        sPageLooping = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'Loop')
        if sPageLooping == "Y":
            self._bPageLooping = True
        return self._bPageLooping

    #----------
    def SetPageLooping(self, xPageNode):
        if self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'Loop') == "Y":
            self._bPageLooping = True
        else:
            self._bPageLooping = False

    #----------
    def GetSegmentationModuleRequired(self):
        # check if any page in the quiz requires the segmentation module
        bSegModuleRequired = False
        if self.oIOXml.CheckForRequiredFunctionalityInAttribute( './/Page', 'EnableSegmentEditor','Y' ):
            bSegModuleRequired = True
            
        return bSegModuleRequired
    
#     #----------
#     def SetRequestToEnableSegmentEditorTF(self, sYN):
#         if sYN == 'y' or sYN == 'Y':
#             self._bRequestToEnableSegmentEditor = True
#         else:
#             self._bRequestToEnableSegmentEditor = False
#         
    #----------
    def GetRequestToEnableSegmentEditorTF(self, iPageIndex):
        bSegmentEditorRequired = False
        xPageNode = self.GetNthPageNode(iPageIndex)
        sSegmentEditorRequired = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'EnableSegmentEditor')
        
        if sSegmentEditorRequired == "Y":
            bSegmentEditorRequired = True
        
        return bSegmentEditorRequired
    
#     #----------
#     def GetSegmentationRequired(self, iPageIndex):
#         
#         bSegmentEditorRequired = False
#         xPageNode = self.oIOXml.GetNthPageNode(iPageIndex)
#         sSegmentEditorRequired = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'EnableSegmentEditor')
#         
#         if sSegmentEditorRequired == "Y":
#             bSegmentEditorRequired = True
#         
#         return bSegmentEditorRequired
#         
    #----------
    def SetButtonScriptRerunRequired(self, iPageIndex):

        xPageNode = self.GetNthPageNode(iPageIndex)
        sBtnScriptRequired = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'ButtonScriptRerunRequired')
        if sBtnScriptRequired == 'Y' or sBtnScriptRequired == 'y':
            self._bBtnScriptRerunRequired = True

        else:
            self._bBtnScriptRerunRequired = False
                
    #----------
    def GetButtonScriptRerunRequired(self):
        return self._bBtnScriptRerunRequired
    
    #----------
    def SetRandomizeRequired(self, sYN=None):
        # set randomize required to input value (from unit tests) or from the stored xml attribute
        if sYN == None:
            sYN = self.oIOXml.GetValueOfNodeAttribute(self.GetRootNode(),'RandomizePageGroups')
        if sYN == 'Y':
            self._bRandomizeRequired = True
        else:
            self._bRandomizeRequired = False
            
    #----------
    def GetRandomizeRequired(self):
        return self._bRandomizeRequired

    #----------
    def SetContourToolRadius(self, xPageNode):
        
        sContourRadius = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'ContourToolRadius')
        
        if sContourRadius != '':
            self._fContourToolRadius = float(sContourRadius)
        else:
            self._fContourToolRadius = 0.0
        
        slicer.modules.quizzereditor.widgetRepresentation().self().SetContourToolRadius(self._fContourToolRadius)        
    #----------
    def GetCountourToolRadius(self):
        return self._fContourToolRadius
    #----------
    def GetQuestionType(self, xQuestionNode):
        
        return self.oIOXml.GetValueOfNodeAttribute(xQuestionNode, 'Type')
         
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetSavedResponses(self, xQuestionNode):
 
        lsResponseValues = []                  
        xAllOptions = self.oIOXml.GetChildren(xQuestionNode, 'Option')
        
        
        for xOptionNode in xAllOptions:
             
                                         
            sLatestResponse = ''
            xLatestResponseNode = self.oIOXml.GetLatestChildElement(xOptionNode, 'Response')
            if xLatestResponseNode != None:
                sLatestResponse = self.oIOXml.GetDataInNode(xLatestResponseNode)
        
            # search for 'latest' response completed - update the list
            lsResponseValues.append(sLatestResponse)
        
        return lsResponseValues
                 
     

        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #-------------------------------------------
    #        Functions
    #-------------------------------------------
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddRandomizedIndicesToXML(self,liIndices):
        ''' Function to coordinate adding the randomized indices into the user's XML.
        '''
        # convert indices into a string
        sIndicesToStore = ''
        iCounter = 0
        
        for iNum in liIndices:
            iCounter = iCounter + 1
            sIndicesToStore = sIndicesToStore + str(iNum)
            if iCounter < len(liIndices):
                sIndicesToStore = sIndicesToStore + ','
                
        dictAttrib = {}     # no attributes for this element
        self.oIOXml.AddElement(self.GetRootNode(),'RandomizedPageGroupIndices',sIndicesToStore, dictAttrib)
        
                
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetStoredRandomizedIndices(self):
        ''' This function will check for existing element of randomized indices.
            If no element exists, a new list will be created.
        '''

        liRandIndices = []
        liStoredRandIndices = []
        
        xRandIndicesNode = self.oIOXml.GetNthChild(self.GetRootNode(), 'RandomizedPageGroupIndices', 0)
        if xRandIndicesNode != None:
            sStoredRandIndices = self.oIOXml.GetDataInNode(xRandIndicesNode)
            liStoredRandIndices = [int(s) for s in sStoredRandIndices.split(",")]
        
        return liStoredRandIndices
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CheckIfLastRepAndNextPageIncomplete(self, iPageIndex):
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
        sNextPageComplete = ''
        
        xPageNode = self.GetNthPageNode(iPageIndex)
        sCurrentPageID = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'ID')
 
         
        sRepNum = self.oIOXml.GetValueOfNodeAttribute(xPageNode, "Rep")
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
            xNextPageNode = self.oIOXml.GetNthChild(self.GetRootNode(), 'Page', self.GetNavigationPage(iNextNavigationIndex))
            sNextPageID = self.oIOXml.GetValueOfNodeAttribute(xNextPageNode, 'ID')
            sNextPageComplete = self.oIOXml.GetValueOfNodeAttribute(xNextPageNode, 'PageComplete')
         
          
        if sNextPageID == sIDForNextRep:
            bLastLoopingRep = False
        else:
            bLastLoopingRep = True
     
         
        if sNextPageComplete == 'Y':
            bLastPageComplete = False
        
        if bLastLoopingRep and bLastPageComplete:
            bEndOfLoopAndNextPageIncomplete = True
        
        return bEndOfLoopAndNextPageIncomplete
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetViewingLayout(self, xmlPageNode):
        
        # clear combo box
        self.lsLayoutWidgets = []
        # set the requested layout for images
        self.sPageLayout = self.oIOXml.GetValueOfNodeAttribute(xmlPageNode, 'Layout')
        if self.sPageLayout == 'TwoOverTwo' :
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutTwoOverTwoView)
            self.lsLayoutWidgets.append('Red')
            self.lsLayoutWidgets.append('Green')
            self.lsLayoutWidgets.append('Yellow')
            self.lsLayoutWidgets.append('Slice4')
        elif self.sPageLayout == 'OneUpRedSlice' :
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)
            self.lsLayoutWidgets.append('Red')
        elif self.sPageLayout == 'FourUp' :
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
            self.lsLayoutWidgets.append('Red')
            self.lsLayoutWidgets.append('Green')
            self.lsLayoutWidgets.append('Yellow')
        elif self.sPageLayout == 'SideBySideRedYellow' :
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutSideBySideView)
            self.lsLayoutWidgets.append('Red')
            self.lsLayoutWidgets.append('Yellow')
        else:
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
            self.lsLayoutWidgets.append('Red')
            self.lsLayoutWidgets.append('Green')
            self.lsLayoutWidgets.append('Yellow')
                    
        return self.lsLayoutWidgets
    

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetMatchingQuizImageNodes(self, sImagePathToSearch, oImageView):
        ''' Search the xml image nodes for the current page that have the same
            path as the image node input to this function
        '''
        loMatchingImageNodes = []
        
        loImageViewNodes = oImageView.GetImageViewList()
        for oImageViewNode in loImageViewNodes:
            if oImageViewNode.sImagePath == sImagePathToSearch:
                loMatchingImageNodes.append(oImageViewNode)
                
        return loMatchingImageNodes    
                
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetImageStateAttributes(self, ldictItems):
        dictImageState = self.oIOXml.GetAttributes(ldictItems['StateElement'])
        return dictImageState
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetStateElementsForMatchingImagePath(self, sCurrentImagePath, iCurrentPageIndex):
        
        ldictAllImageStateItems = []
        
        lxPages = self.oIOXml.GetChildren(self.GetRootNode(), 'Page')
        
        # for each page in the xml (up to and including  the current page) get all image elements
        for iPageIdx in range(len(lxPages)):
            if iPageIdx <= iCurrentPageIndex:
                xPage = self.oIOXml.GetNthChild(self.GetRootNode(), 'Page', iPageIdx)
                lxImageElements = self.oIOXml.GetChildren(xPage, 'Image')
                
                # for all images on the page, if a volume type image, collect the State elements
                for xImage in lxImageElements:
                    sImageType = self.oIOXml.GetValueOfNodeAttribute(xImage, 'Type')
                    if sImageType == 'Volume' or sImageType == 'VolumeSequence':
                        

                        sPath = self.oIOXml.GetDataFromLastChild(xImage, 'Path')
                        if sPath == sCurrentImagePath:
                            
                            
                            sImageDefaultOrientation = self.oIOXml.GetDataFromLastChild(xImage, 'DefaultOrientation')
                                
                            if self.oIOXml.GetNumChildrenByName(xImage, 'State') > 0:
                                lStateElements = self.oIOXml.GetChildren(xImage, 'State')
                                for xState in lStateElements:
                                    
                                    dictImageStateItems = {'DefaultOrientation':sImageDefaultOrientation, 'Page':str(iPageIdx),'StateElement':xState}
                                    ldictAllImageStateItems.append(dictImageStateItems)

                        
        return ldictAllImageStateItems
                
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SaveQuiz(self, sQuizPath):
        self.oIOXml.SaveXml(sQuizPath)
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def RepeatNode(self,  indXmlPageToRepeat, sXmlFilePath = None):
        ''' Function to copy the current page into the xml allowing the user to create new segments or  
            measurement lines for the same image. 
        '''
#         # allow for testing environment to use a pre-set testing file path
#         if sXmlFilePath == None:
#             sXmlFilePath = self.oFilesIO.GetUserQuizResultsPath()   # for live run
        
#         indXmlPageToRepeat = self.GetCurrentPageIndex()
        
        
        self.SaveQuiz(sXmlFilePath)    # for debug
        xCopyOfXmlPageToRepeatNode = self.oIOXml.CopyElement(self.GetNthPageNode(indXmlPageToRepeat))
        iCopiedRepNum = int(self.oIOXml.GetValueOfNodeAttribute(xCopyOfXmlPageToRepeatNode, "Rep"))
        
        # find the next xml page that has Rep 0 (move past all repeated pages for this loop)
        indNextXmlPageWithRep0 = self.oIOXml.GetIndexOfNextChildWithAttributeValue(self.GetRootNode(), "Page", indXmlPageToRepeat + 1, "Rep", "0")

        if indNextXmlPageWithRep0 != -1:
            self.oIOXml.InsertElementBeforeIndex(self.GetRootNode(), xCopyOfXmlPageToRepeatNode, indNextXmlPageWithRep0)
        else:
            # attribute was not found
            self.oIOXml.AppendElement(self.GetRootNode(), xCopyOfXmlPageToRepeatNode)
            indNextXmlPageWithRep0 = self.oIOXml.GetNumChildrenByName(self.GetRootNode(), 'Page') - 1
            

        return indNextXmlPageWithRep0, iCopiedRepNum
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AdjustXMLForRepeatedPage(self, xCurrentPageNode, iPageIndex):
        ''' Function to update the newly repeated Page node.
            The Page ID attribute will have '-Rep#' appended.
            Any previously stored label map and markup line paths are removed.
            Any previously stored responses to questions will be removed.
            Remove any BookmarkID attributes - 
                (a GoToBookmark attribute will have the user return to the first Page in a group of repetitions) 
        '''
        
        sMsg = ''
        try:
            
#             xNewRepeatPage = self.GetCurrentPageNode()
            xNewRepeatPage = xCurrentPageNode
            
            # get last rep number to increment current rep
#             xPreviousPage = self.oIOXml.GetNthChild(self.GetRootNode(), "Page", self.GetNavigationPage( self.GetCurrentNavigationIndex() -1 ) )
            xPreviousPage = self.oIOXml.GetNthChild(self.GetRootNode(), "Page", iPageIndex)
            sPreviousRepNum = self.oIOXml.GetValueOfNodeAttribute(xPreviousPage, "Rep")
            sPreviousPageID = self.oIOXml.GetValueOfNodeAttribute(xPreviousPage, 'ID')
            
            
            self.oIOXml.UpdateAttributesInElement(xNewRepeatPage, {"PageComplete":"N"})
            iPreviousRepNum = int(sPreviousRepNum)
            sNewRepNum = str(iPreviousRepNum + 1)
            self.oIOXml.UpdateAttributesInElement(xNewRepeatPage, {"Rep":sNewRepNum})
            self.oIOXml.RemoveAttributeInElement(xNewRepeatPage, "BookmarkID")
            
            iSubIndex = sPreviousPageID.find('-Rep')
            if iSubIndex >=0:
                sStrippedPageID = sPreviousPageID[0:iSubIndex]
            else:
                sStrippedPageID = sPreviousPageID
            
            sNewPageID = sStrippedPageID + '-Rep' + str(sNewRepNum)
            self.oIOXml.UpdateAttributesInElement(xNewRepeatPage, {"ID":sNewPageID})
            
            
                
            # remove LabelmapPath and MarkupLinePath elements
            lxImages = self.oIOXml.GetChildren(xNewRepeatPage, 'Image')
            for xImage in lxImages:
                self.oIOXml.RemoveAllElements(xImage, "LabelMapPath")
                self.oIOXml.RemoveAllElements(xImage, "MarkupLinePath")
                
            # remove Response elements
            lxQuestionSets = self.oIOXml.GetChildren(xNewRepeatPage, "QuestionSet")
            for xQuestionSet in lxQuestionSets:
                lxQuestions = self.oIOXml.GetChildren(xQuestionSet, "Question")
                for xQuestion in lxQuestions:
                    lxOptions = self.oIOXml.GetChildren(xQuestion, "Option")
                    for xOption in lxOptions:
                        self.oIOXml.RemoveAllElements(xOption, "Response")
        
        
        
        except:
            tb = traceback.format_exc()
#             iPage = self.GetCurrentPageIndex() + 1
            iPage = iPageIndex + 1
            sMsg = 'AdjustXMLForRepeatedPage: Trouble updating repeated page.' + \
                    ' Previous page rep number should be a string that can be converted to an integer.' +\
                    '\nSee Page: ' + str(iPage) + '\n\n' + tb
            self.oUtilsMsgs.DisplayError(sMsg)
        
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def WriteResponses(self, iPageIndex, iQSetIndex, lsResponses):
        
        # using the list of question set responses, isolate responses for each question
        iNumQuestions = len(lsResponses)

        # for each question in the question set responses        
        for indQuestion in range(len(lsResponses)):
            
            # get the option responses for that question 
            #    (eg. for a checkbox question, there may be 3 options 'yes' 'no' 'maybe')
            lsQuestionResponses = lsResponses[indQuestion]


            # if the list of responses was empty (only a partial number of questions were answered), don't write
            if len(lsQuestionResponses) > 0:
            
                # for each option in the question
                for indOption in range(len(lsQuestionResponses)):
                    
                    # capture the xml node for the option
                    xOptionNode = self.GetNthOptionNode( iPageIndex, iQSetIndex, indQuestion, indOption)
                     
                    if not xOptionNode == None:
                        # write the response to the xml 
                        self.AddResponseElement(xOptionNode, lsQuestionResponses[indOption])
                
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddResponseElement(self, xOptionNode, sResponse):
        
        now = datetime.now()
        sResponseTime = now.strftime(self.oIOXml.sTimestampFormat)
        
        dictAttrib = { 'LoginTime': self.LoginTime(), 'ResponseTime': sResponseTime}
        
        self.oIOXml.AddElement(xOptionNode,'Response', sResponse, dictAttrib)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddImageStateElement(self, xImageNode, dictAttrib):
        """ Add the image state element to the xml file including window/level
            and slice offset. 
        """

        sNullData = ''

        # add login and response times to the existing state attributes
        now = datetime.now()
        sResponseTime = now.strftime(self.oIOXml.sTimestampFormat)
        
        dictTimeAttributes = { 'LoginTime': self.LoginTime(), 'ResponseTime': sResponseTime} 
        dictAttrib.update(dictTimeAttributes)

        self.oIOXml.AddElement(xImageNode,'State', sNullData, dictAttrib)
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddPathElement(self, sElementName, xImageNode, sInputPath):
        
        # add login and response times to the label map path element
        now = datetime.now()
        sResponseTime = now.strftime(self.oIOXml.sTimestampFormat)
        
        dictAttrib = { 'LoginTime': self.LoginTime(), 'ResponseTime': sResponseTime} 
        
        self.oIOXml.AddElement(xImageNode, sElementName, sInputPath, dictAttrib)
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddSessionLoginTimestamp(self, oFilesIO):
        ''' Function to add an element holding the login time for the session.
            Set up the logout time attribute to be updated on each write.
            Also - record the user's name
        '''

        now = datetime.now()

        self.SetLoginTime( now.strftime(self.oIOXml.sTimestampFormat) )
        
        dictAttrib = {'LoginTime': self.LoginTime(), 'LogoutTime': self.LoginTime()}
        
        sNullText = ''
        
        self.oIOXml.AddElement(self.GetRootNode(),'Login', sNullText, dictAttrib)
        
        self.oIOXml.SaveXml(oFilesIO.GetUserQuizResultsPath())
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def UpdateSessionLogoutTimestamp(self):
        ''' This function will add the attribute LogoutTime to the last entry of the Login element.
            Each time a 'Save' is done to the XML file, this Logout time will be overwritten.
            Then when the exit finally happens, it will reflect the last time a write was performed.
        '''

        now = datetime.now()

        sLogoutTime = now.strftime(self.oIOXml.sTimestampFormat)
        
        # get existing attributes from the Login element
        xLoginNode = self.oIOXml.GetLastChild(self.GetRootNode(), "Login")
        
        if xLoginNode != None:
            # update logout time if login element exists
            dictAttrib = self.oIOXml.GetAttributes(xLoginNode)
    
            dictAttrib['LogoutTime'] = sLogoutTime
                
            # reset the Login element
            self.oIOXml.UpdateAttributesInElement(xLoginNode, dictAttrib)

            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetLastLoginTimestamp(self):
        # function to scan the user's quiz file for all session login times
        # return the last session login time

        lsTimestamps = []
        dtLastTimestamp = ''    # timestamp of type 'datetime'

        
        xmlLoginNodes = self.oIOXml.GetChildren(self.GetRootNode(), 'Login')

        # collect all login timestamps (type 'string')
        for indElem in range(len(xmlLoginNodes)):
            # get date/time from attribute
            xmlLoginNode = self.oIOXml.GetNthChild(self.GetRootNode(), 'Login', indElem)

            sTimestamp = self.oIOXml.GetValueOfNodeAttribute(xmlLoginNode, 'LoginTime')
            lsTimestamps.append(sTimestamp)
            
            # look for Quiz Complete status
            sQuizCompleteStatus = self.oIOXml.GetValueOfNodeAttribute(xmlLoginNode, 'QuizComplete')
            if sQuizCompleteStatus == 'Y':
                self.SetQuizComplete(True)
            

        # loop through timestamps to search for the last login occurrence
        for indTime in range(len(lsTimestamps)):
            
            sNewTimestamp = lsTimestamps[indTime]
            # convert to datetime format for compare
            dtNewTimestamp = datetime.strptime(sNewTimestamp, self.oIOXml.sTimestampFormat)
            
            if dtLastTimestamp == '': # for initial compare
                dtLastTimestamp = dtNewTimestamp
                
            else:

                # update the last time stamp 
                if dtNewTimestamp > dtLastTimestamp:
                    dtLastTimestamp = dtNewTimestamp
                
                            
        return dtLastTimestamp
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddQuizCompleteAttribute(self):
        ''' add attribute to last login element to indicate user has completed the quiz
        '''
        xmlLastLoginElement = self.oIOXml.GetLastChild(self.GetRootNode(),'Login')
        xmlLastLoginElement.set('QuizComplete','Y')
        self.oIOXml.SaveXml(self.oFilesIO.GetUserQuizResultsPath())

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddPageCompleteAttribute(self, idxPage):
        ''' add attribute to current page element to indicate all 
            question sets and segmentations have been completed
        '''
        xmlCurrentPageElement = self.oIOXml.GetNthChild(self.GetRootNode(),'Page', idxPage)
        xmlCurrentPageElement.set('PageComplete','Y')
        self.oIOXml.SaveXml(self.oFilesIO.GetUserQuizResultsPath())

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetPageIncomplete(self, iPageIndex):
        ''' if requirements were not met, reset the PageComplete attribute to 'N'
        '''
        xPageNode = self.GetNthPageNode(iPageIndex)
        self.oIOXml.UpdateAttributesInElement(xPageNode, {"PageComplete":"N"})
        self.oIOXml.SaveXml(self.oFilesIO.GetUserQuizResultsPath())
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddUserNameAttribute(self, oFilesIO):
        ''' add attribute to Session to record the user's name
        '''
        xRootNode = self.GetRootNode()
        dictAttrib = self.oIOXml.GetAttributes(xRootNode)

        dictAttrib['UserName'] = oFilesIO.GetUsername()
            
        # reset the Login element
        self.oIOXml.UpdateAttributesInElement(xRootNode, dictAttrib)

        self.oIOXml.SaveXml(oFilesIO.GetUserQuizResultsPath())

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetupLoopingInitialization(self):
        
        # if Loop="Y" for any page in the quiz, add Rep="0" to each page if not defined
        
        xRootNode = self.GetRootNode()
        bLoopingInQuiz = False
        lxPages = self.oIOXml.GetChildren(xRootNode,'Page')
        for xPageNode in lxPages:
            sLoopAllowed = self.oIOXml.GetValueOfNodeAttribute(xPageNode, "Loop")
            if sLoopAllowed == "Y":
                bLoopingInQuiz = True
                break
            
        if bLoopingInQuiz:
            for xPageNode in lxPages:
                sRepNum = self.oIOXml.GetValueOfNodeAttribute(xPageNode, "Rep")
                try:
                    int(sRepNum)
                except:
                    # not a valid integer - create/set the attribute to 0
                    self.oIOXml.UpdateAttributesInElement(xPageNode, {"Rep":"0"})
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetupPageGroupInitialization(self):
        ''' If no PageGroup attribute exists, update the XML to initialize each page
            to a unique number. Start PageGroup numbers at '1'. ('0' has specialized
            meaning when randomizing page groups.
        '''
        
        bPageGroupFound = False
        xRootNode = self.GetRootNode()
        
        lxPages = self.oIOXml.GetChildren(xRootNode,'Page')
        for xPageNode in lxPages:
            sPageGroupNum = self.oIOXml.GetValueOfNodeAttribute(xPageNode, "PageGroup")
            if sPageGroupNum != '':
                bPageGroupFound = True
                break
       
        if not bPageGroupFound:
            for iPageNum in range(len(lxPages)):
                xPageNode = self.oIOXml.GetNthChild(xRootNode, "Page", iPageNum)
                self.oIOXml.UpdateAttributesInElement(xPageNode, {"PageGroup":str(iPageNum + 1)})
        
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def DisplayCurrentResponses(self, lsCurrentResponses):
# 
#         indQSet = self.GetCurrentQuestionSetIndex()
#  
#         oQuestionSet = self._loQuestionSets[indQSet]
#         loQuestions = oQuestionSet.GetQuestionList()
#          
#         for indQuestion in range(len(loQuestions)):
#             oQuestion = loQuestions[indQuestion]
#             oQuestion.PopulateQuestionWithResponses(lsCurrentResponses[indQuestion])
# 
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def DisplaySavedResponse(self):
# 
#         xNodeQuestionSet = self.GetCurrentQuestionSetNode()
#         indQSet = self.GetCurrentQuestionSetIndex()
#  
#         oQuestionSet = self._loQuestionSets[indQSet]
#         loQuestions = oQuestionSet.GetQuestionList()
#          
#         # for each question and each option, extract any existing responses from the XML
#          
#         lsAllResponsesForQuestions = []
#         for indQuestion in range(len(loQuestions)):
#             oQuestion = loQuestions[indQuestion]
#             xQuestionNode = self.oIOXml.GetNthChild(xNodeQuestionSet, 'Question', indQuestion)
#              
#                  
#             lsResponseValues = []                  
#             xAllOptions = self.oIOXml.GetChildren(xQuestionNode, 'Option')
# 
# 
#             xAllOptions = self.GetAllOptionNodes(indQuestion)
#             for xOptionNode in xAllOptions:
#                 
#                                             
#                 sLatestResponse = ''
#                 xLatestResponseNode = self.oIOXml.GetLatestChildElement(xOptionNode, 'Response')
#                 if xLatestResponseNode != None:
#                     sLatestResponse = self.oIOXml.GetDataInNode(xLatestResponseNode)
#     
#                 # search for 'latest' response completed - update the list
#                 lsResponseValues.append(sLatestResponse)
#                 
#             oQuestion.PopulateQuestionWithResponses(lsResponseValues)
# 
#             # only InfoBox type of question can have all responses equal to null string
#             if self.oIOXml.GetValueOfNodeAttribute(xQuestionNode, 'Type') != "InfoBox" \
#                     and (all(elem == '' for elem in lsResponseValues)):
#                 lsResponseValues = []   # reset if all are empty
# 
#             lsAllResponsesForQuestions.append(lsResponseValues)
#             
#     
#             lsResponseValues = []  # clear for next set of options 
# 
#         self.SetPreviousResponses(lsAllResponsesForQuestions)
#     
#     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     def CaptureNewResponses(self):
#         ''' When moving to another display of Images and QuestionSet (from pressing Next or Previous)
#             the new responses that were entered must be captured ready to do the save to XML.
#             A check for any missing responses to the questions is done and passed back to the calling function.
#         '''
#         
#         # sMsg may be set in Question class function to capture the response
#         sMsg = ''
#         sAllMsgs = ''
#         
#         # get list of questions from current question set
#         indQSet = self.GetCurrentQuestionSetIndex()
#         oQuestionSet = self._loQuestionSets[indQSet]
#         loQuestions = oQuestionSet.GetQuestionList()
#             
#         lsAllResponses = []
#         lsResponsesForOptions = []
#         iNumMissingResponses = 0
#         
#         for indQuestion in range(len(loQuestions)):
#             oQuestion = loQuestions[indQuestion]
#             bResponseCaptured = False
#             
#             bResponseCaptured, lsResponsesForOptions, sMsg = oQuestion.CaptureResponse()
# 
# 
#             # append all captured lists - even if it was empty (partial responses)
#             lsAllResponses.append(lsResponsesForOptions)
#             
#             # string together all missing response messages
#             if sMsg != '':
#                 if sAllMsgs == '':
#                     sAllMsgs = sMsg
#                 else:
#                     sAllMsgs = sAllMsgs + '\n' + sMsg 
#             
#             # keep track if a question was missed
#             if bResponseCaptured == False:
#                 iNumMissingResponses = iNumMissingResponses + 1
#                 
#         # define success level
#         sCaptureSuccessLevel = self.oPageState.CategorizeResponseCompletionLevel(len(loQuestions), len(loQuestions)-iNumMissingResponses)
#                 
#         return sCaptureSuccessLevel, lsAllResponses, sAllMsgs
#        



##########################################################################
#
# class SlicerWindowSize
#
##########################################################################

class SlicerWindowSize:
    
    def __init__(self, parent=None):
        self.slMainWindowPos = None
        self.slMainWindowWidth = 0
        self.slMainWindowHeight = 0
        
        self.CaptureWindowSize()
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CaptureWindowSize(self):
        slMainWindow = slicer.util.mainWindow()
        self.slMainWindowPos = slMainWindow.pos
        self.slMainWindowWidth = slMainWindow.geometry.width()
        self.slMainWindowHeight = slMainWindow.geometry.height()
