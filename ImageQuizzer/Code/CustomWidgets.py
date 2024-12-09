import os
import vtk, qt, ctk, slicer
import sys
import unittest

import Utilities.UtilsMsgs as UtilsMsgs
import Utilities.UtilsFilesIO as UtilsFilesIO
import Utilities.UtilsEmail as UtilsEmail
import Utilities.UtilsIOXml as UtilsIOXml
import Utilities.UtilsCustomXml as UtilsCustomXml

from Utilities.UtilsCustomXml import *
from Utilities.UtilsIOXml import *
from Utilities.UtilsFilesIO import *
from Utilities.UtilsMsgs import *
from Utilities.UtilsEmail import *

from datetime import datetime


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
    def __init__(self, parent=None):
        self.sClassName = type(self).__name__
        self.parent = parent
        
        self._bUserInteractionLog = False
        self._bAllowMultipleResponse = False
        self._bRandomizeRequired = False

        
        self._sLoginTime = ''
        self._bQuizComplete = False

        self._xPageNode = None
        
        
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
    def OpenQuiz(self):
        bSuccess = UtilsIOXml.OpenXml(UtilsFilesIO.GetUserQuizResultsPath(),'Session')

        return bSuccess
    
    #----------
    def SetRootNode(self, xInputNode):
        self._xRootNode = xInputNode
        
    #----------
    def GetRootNode(self):
#         return self._xRootNode
        return UtilsIOXml.GetRootNode()
        
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
        xmlPageNode = UtilsIOXml.GetNthChild(self.GetRootNode(), 'Page', iPageIndex)
        sPageDescriptor = UtilsIOXml.GetValueOfNodeAttribute(xmlPageNode, 'Descriptor')
        
        return sPageDescriptor

    #----------
    def GetEmailResultsRequest(self):
        bEmailResults = UtilsEmail.SetupEmailResults( \
                            UtilsIOXml.GetValueOfNodeAttribute(self.GetRootNode(), 'EmailResultsTo'))
        
        return bEmailResults

    #----------
    def GetSessionContourVisibilityDefault(self):
        # quiz validation checked for valid values
        # if no attribute exists, set with the default
        sSessionContourVisibility = UtilsIOXml.GetValueOfNodeAttribute(self.GetRootNode(), 'ContourVisibility')
        if sSessionContourVisibility == '':
            sSessionContourVisibility = 'Outline'  # default
            
        return sSessionContourVisibility
    
    #----------
    def GetPageID(self, iPageIndex):
        xmlPageNode = UtilsIOXml.GetNthChild(self.GetRootNode(), 'Page', iPageIndex)
        sPageID = UtilsIOXml.GetValueOfNodeAttribute(xmlPageNode, 'ID')
        
        return sPageID

    #----------
    def GetPageRep(self, iPageIndex):
        xmlPageNode = UtilsIOXml.GetNthChild(self.GetRootNode(), 'Page', iPageIndex)
        sPageRep = UtilsIOXml.GetValueOfNodeAttribute(xmlPageNode, 'Rep')
        
        return sPageRep

    #----------
    def SetUserInteractionLogRequest(self, iPageIndex):

        xPageNode = self.GetNthPageNode(iPageIndex)
        sUserInteractionLog = UtilsIOXml.GetValueOfNodeAttribute(xPageNode, 'UserInteractionLog')

        self._bUserInteractionLog = False
        if sUserInteractionLog == 'Y':
            self._bUserInteractionLog = True
            
        return self._bUserInteractionLog
            
    #----------
    def GetUserInteractionLogRequest(self):
        return self._bUserInteractionLog
    
    #----------
    def GetGoToBookmarkRequest(self, iPageIndex):
        
        xPageNode = self.GetNthPageNode(iPageIndex)
        lsBookmarkRequest = []
        sGoToBookmarkRequest =  UtilsIOXml.GetValueOfNodeAttribute(xPageNode, 'GoToBookmark')
        
        if sGoToBookmarkRequest != '':
            lsBookmarkRequest = sGoToBookmarkRequest.split()
            
        return lsBookmarkRequest
        
    #----------
    def SetMultipleResponseAllowed(self,iPageIndex):
        
        xPageNode = self.GetNthPageNode(iPageIndex)
        sYN = UtilsIOXml.GetValueOfNodeAttribute(xPageNode, 'AllowMultipleResponse')

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
        return UtilsIOXml.GetValueOfNodeAttribute(self.GetRootNode(), 'ROIColorFile') 

    #----------
    def GetPageCompleteAttribute(self, iPageIndex):
        bPageComplete = False
        xPageNode = UtilsIOXml.GetNthChild(self.GetRootNode(), 'Page', iPageIndex)

        sPageComplete = UtilsIOXml.GetValueOfNodeAttribute(xPageNode,'PageComplete')
        if sPageComplete == "Y":
            bPageComplete = True
        
        return bPageComplete
        
    #----------
    def GetAllQuestionSetsForNthPage(self, iPageIndex):
        self._xPageNode = UtilsIOXml.GetNthChild(self.GetRootNode(), 'Page', iPageIndex)
        xNodesAllQuestionSets = UtilsIOXml.GetChildren(self._xPageNode, 'QuestionSet')
        
        return xNodesAllQuestionSets

    #----------
    def GetAllQuestionSetNodesForCurrentPage(self, iPageIndex):
        xPageNode = self.GetNthPageNode(iPageIndex)
        xAllQuestionSetNodes = UtilsIOXml.GetChildren(xPageNode, 'QuestionSet')
        
        return xAllQuestionSetNodes
    #----------
    def GetNthQuestionSetForCurrentPage(self, idxQSet, iPageIndex):
        xPageNode = self.GetNthPageNode(iPageIndex)
        xQuestionSetNode = UtilsIOXml.GetNthChild(xPageNode, 'QuestionSet', idxQSet)
        
        return xQuestionSetNode
        
    #----------
    def GetNthPageNode(self,iPageIndex):
        ''' From the  navigation index in the composite indices list, get the page index.
            Return the nth page node (using the page index) from the root.
        '''
        xPageNode = UtilsIOXml.GetNthChild(self.GetRootNode(), 'Page', iPageIndex)
        
        return xPageNode
    
    #----------
    def GetImageElements(self, iPageIndex):
        lxImageElements = UtilsIOXml.GetChildren(self.GetNthPageNode(iPageIndex), 'Image')
        return lxImageElements
    
    #----------
    def GetCurrentQuestionSetNode(self, iPageIndex, iQSetIndex):
        xPageNode = self.GetNthPageNode(iPageIndex)
        xQuestionSetNode = UtilsIOXml.GetNthChild(xPageNode, 'QuestionSet', iQSetIndex)
        
        return xQuestionSetNode

    #----------
    def GetCurrentQuestionNode(self, iPageIndex, iQSetIndex, iQuestionIndex):
        xQSetNode = self.GetCurrentQuestionSetNode(iPageIndex, iQSetIndex)
        xQuestionNode = UtilsIOXml.GetNthChild(xQSetNode, 'Question', iQuestionIndex)
    
        return xQuestionNode
 
    #----------
    def GetNthOptionNode(self, iPageIndex, iQSetIndex, indQuestion, indOption):

        xQuestionSetNode = self.GetCurrentQuestionSetNode(iPageIndex, iQSetIndex)
        xQuestionNode = UtilsIOXml.GetNthChild(xQuestionSetNode, 'Question', indQuestion)
        xOptionNode = UtilsIOXml.GetNthChild(xQuestionNode, 'Option', indOption)
        
        return xOptionNode
        
    #----------
    def GetAllOptionNodes(self, iPageIndex, iQSetIndex, indQuestion):

        xQuestionSetNode = self.GetCurrentQuestionSetNode(iPageIndex, iQSetIndex)
        xQuestionNode = UtilsIOXml.GetNthChild(xQuestionSetNode, 'Question', indQuestion)
        xAllOptionNodes = UtilsIOXml.GetChildren(xQuestionNode,'Option')
        
        return xAllOptionNodes
        
    #----------
    def GetPageLooping(self, iPageIndex):
        
        bPageLooping = False
        xPageNode = self.GetNthPageNode(iPageIndex)
        sPageLooping = UtilsIOXml.GetValueOfNodeAttribute(xPageNode, 'Loop')
        if sPageLooping == "Y":
            bPageLooping = True
        return bPageLooping

    #----------
    def GetSegmentationModuleRequired(self):
        # check if any page in the quiz requires the segmentation module
        bSegModuleRequired = False
        if UtilsIOXml.CheckForRequiredFunctionalityInAttribute( './/Page', 'EnableSegmentEditor','Y' ):
            bSegModuleRequired = True
            
        return bSegModuleRequired
    
    #----------
    def GetRequestToEnableSegmentEditorTF(self, iPageIndex):
        bSegmentEditorRequired = False
        xPageNode = self.GetNthPageNode(iPageIndex)
        sSegmentEditorRequired = UtilsIOXml.GetValueOfNodeAttribute(xPageNode, 'EnableSegmentEditor')
        
        if sSegmentEditorRequired == "Y":
            bSegmentEditorRequired = True
        
        return bSegmentEditorRequired
    
    #----------
    def GetButtonScriptRerunRequired(self, iPageIndex):

        xPageNode = self.GetNthPageNode(iPageIndex)
        sBtnScriptRequired = UtilsIOXml.GetValueOfNodeAttribute(xPageNode, 'ButtonScriptRerunRequired')
        if sBtnScriptRequired == 'Y' or sBtnScriptRequired == 'y':
            bBtnScriptRerunRequired = True

        else:
            bBtnScriptRerunRequired = False
            
        return bBtnScriptRerunRequired
                
    #----------
    def SetRandomizeRequired(self, sYN=None):
        # set randomize required to input value (from unit tests) or from the stored xml attribute
        if sYN == None:
            sYN = UtilsIOXml.GetValueOfNodeAttribute(self.GetRootNode(),'RandomizePageGroups')
        if sYN == 'Y':
            self._bRandomizeRequired = True
        else:
            self._bRandomizeRequired = False
             
    #----------
    def GetRandomizeRequired(self):
        return self._bRandomizeRequired

    #----------
    def GetContourToolRadius(self, iPageIndex):

        xPageNode = self.GetNthPageNode(iPageIndex)        
        sContourRadius = UtilsIOXml.GetValueOfNodeAttribute(xPageNode, 'ContourToolRadius')
        
        if sContourRadius != '':
            fContourToolRadius = float(sContourRadius)
        else:
            fContourToolRadius = 0.0
        
        return fContourToolRadius
                
    #----------
    def GetQuestionType(self, xQuestionNode):
        
        return UtilsIOXml.GetValueOfNodeAttribute(xQuestionNode, 'Type')
         
    #----------
    def GetSavedResponses(self, xQuestionNode):
 
        lsResponseValues = []                  
        xAllOptions = UtilsIOXml.GetChildren(xQuestionNode, 'Option')
        
        for xOptionNode in xAllOptions:
                                         
            sLatestResponse = ''
            xLatestResponseNode = UtilsCustomXml.GetLatestChildElement(xOptionNode, 'Response')
            if xLatestResponseNode != None:
                sLatestResponse = UtilsIOXml.GetDataInNode(xLatestResponseNode)
        
            # search for 'latest' response completed - update the list
            lsResponseValues.append(sLatestResponse)
        
        return lsResponseValues

    #----------

    def GetMinMaxAttributesFromXML(self, xNodeQuestion):

        dictModifiers = {}

        sMin = UtilsIOXml.GetValueOfNodeAttribute(xNodeQuestion, 'Min')               
        sMax = UtilsIOXml.GetValueOfNodeAttribute(xNodeQuestion, 'Max')

        dictModifiers['Min'] = sMin
        dictModifiers['Max'] = sMax

        return dictModifiers
    
    #----------

    def GetButtonCustomColorOn(self, xNodeQuestion):
        
        liButtonCustomColorOnRgb = []

        sButtonColorOnRgb = UtilsIOXml.GetValueOfNodeAttribute(xNodeQuestion, 'ButtonCustomColorOn')

        if sButtonColorOnRgb != '':
            lsButtonColorOnRgb = sButtonColorOnRgb.split()
            for ind in range(len(lsButtonColorOnRgb)):
                liButtonCustomColorOnRgb.append(int(lsButtonColorOnRgb[ind]))

        
        return liButtonCustomColorOnRgb

    #----------

    def GetButtonToggleColorOff(self, xNodeQuestion):
        
        liButtonToggleColorOffRgb = []

        sButtonToggleColorOffRgb = UtilsIOXml.GetValueOfNodeAttribute(xNodeQuestion, 'ButtonToggleColorOff')

        if sButtonToggleColorOffRgb != '':
            lsButtonToggleColorOffRgb = sButtonToggleColorOffRgb.split()
            for ind in range(len(lsButtonToggleColorOffRgb)):
                liButtonToggleColorOffRgb.append(int(lsButtonToggleColorOffRgb[ind]))

        
        return liButtonToggleColorOffRgb


                 
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #-------------------------------------------
    #        Functions
    #-------------------------------------------
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddRandomizedIndicesToQuizResultsFile(self,liIndices):
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
        UtilsIOXml.AddElement(self.GetRootNode(),'RandomizedPageGroupIndices',sIndicesToStore, dictAttrib)
        
                
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetStoredRandomizedIndices(self):
        ''' This function will check for existing element of randomized indices.
            If no element exists, a new list will be created.
        '''

        liRandIndices = []
        liStoredRandIndices = []
        
        xRandIndicesNode = UtilsIOXml.GetNthChild(self.GetRootNode(), 'RandomizedPageGroupIndices', 0)
        if xRandIndicesNode != None:
            sStoredRandIndices = UtilsIOXml.GetDataInNode(xRandIndicesNode)
            liStoredRandIndices = [int(s) for s in sStoredRandIndices.split(",")]
        
        return liStoredRandIndices
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetViewingLayout(self, iPageIndex):
        
        xPageNode = self.GetNthPageNode(iPageIndex)
        # clear combo box
        self.lsLayoutWidgets = []
        # set the requested layout for images
        self.sPageLayout = UtilsIOXml.GetValueOfNodeAttribute(xPageNode, 'Layout')
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
        dictImageState = UtilsIOXml.GetAttributes(ldictItems['StateElement'])
        return dictImageState
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetStateElementsForMatchingImagePath(self, sCurrentImagePath, iCurrentPageIndex):
        
        ldictAllImageStateItems = []
        
        lxPages = UtilsIOXml.GetChildren(self.GetRootNode(), 'Page')
        
        # for each page in the xml (up to and including  the current page) get all image elements
        for iPageIdx in range(len(lxPages)):
            if iPageIdx <= iCurrentPageIndex:
                xPage = UtilsIOXml.GetNthChild(self.GetRootNode(), 'Page', iPageIdx)
                lxImageElements = UtilsIOXml.GetChildren(xPage, 'Image')
                
                # for all images on the page, if a volume type image, collect the State elements
                for xImage in lxImageElements:
                    sImageType = UtilsIOXml.GetValueOfNodeAttribute(xImage, 'Type')
                    if sImageType == 'Volume' or sImageType == 'VolumeSequence':
                        

                        sPath = UtilsIOXml.GetDataFromLastChild(xImage, 'Path')
                        if sPath == sCurrentImagePath:
                            
                            
                            sImageDefaultOrientation = UtilsIOXml.GetDataFromLastChild(xImage, 'DefaultOrientation')
                                
                            if UtilsIOXml.GetNumChildrenByName(xImage, 'State') > 0:
                                lStateElements = UtilsIOXml.GetChildren(xImage, 'State')
                                for xState in lStateElements:
                                    
                                    dictImageStateItems = {'DefaultOrientation':sImageDefaultOrientation, 'Page':str(iPageIdx),'StateElement':xState}
                                    ldictAllImageStateItems.append(dictImageStateItems)

                        
        return ldictAllImageStateItems
                
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SaveQuiz(self, sQuizPath):
        UtilsIOXml.SaveXml(sQuizPath)
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def RepeatNode(self,  indXmlPageToRepeat, sXmlFilePath = None):
        ''' Function to copy the current page into the xml allowing the user to create new segments or  
            measurement lines for the same image. 
        '''
#       # allow for testing environment to use a pre-set testing file path
        
        self.SaveQuiz(sXmlFilePath)    # for debug
        xCopyOfXmlPageToRepeatNode = UtilsIOXml.CopyElement(self.GetNthPageNode(indXmlPageToRepeat))
        iCopiedRepNum = int(UtilsIOXml.GetValueOfNodeAttribute(xCopyOfXmlPageToRepeatNode, "Rep"))
        
        # find the next xml page that has Rep 0 (move past all repeated pages for this loop)
        indNextXmlPageWithRep0 = UtilsIOXml.GetIndexOfNextChildWithAttributeValue(self.GetRootNode(), "Page", indXmlPageToRepeat + 1, "Rep", "0")

        if indNextXmlPageWithRep0 != -1:
            UtilsIOXml.InsertElementBeforeIndex(self.GetRootNode(), xCopyOfXmlPageToRepeatNode, indNextXmlPageWithRep0)
        else:
            # attribute was not found
            UtilsIOXml.AppendElement(self.GetRootNode(), xCopyOfXmlPageToRepeatNode)
            indNextXmlPageWithRep0 = UtilsIOXml.GetNumChildrenByName(self.GetRootNode(), 'Page') - 1
            

        return indNextXmlPageWithRep0, iCopiedRepNum
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AdjustQuizResultsFileForRepeatedPage(self, iNewPageIndex, iPrevPageIndex):
        ''' Function to update the newly repeated Page node.
            The Page ID attribute will have '-Rep#' appended.
            Any previously stored label map and markup line paths are removed.
            Any previously stored responses to questions will be removed.
            Remove any BookmarkID attributes - 
                (a GoToBookmark attribute will have the user return to the first Page in a group of repetitions) 
        '''
        
        sMsg = ''
        try:
            
            xNewRepeatPage = self.GetNthPageNode(iNewPageIndex)
            
            # get last rep number to increment current rep
            xPreviousPage = UtilsIOXml.GetNthChild(self.GetRootNode(), "Page", iPrevPageIndex)
            sPreviousRepNum = UtilsIOXml.GetValueOfNodeAttribute(xPreviousPage, "Rep")
            sPreviousPageID = UtilsIOXml.GetValueOfNodeAttribute(xPreviousPage, 'ID')
            
            
            UtilsIOXml.UpdateAttributesInElement(xNewRepeatPage, {"PageComplete":"N"})
            iPreviousRepNum = int(sPreviousRepNum)
            sNewRepNum = str(iPreviousRepNum + 1)
            UtilsIOXml.UpdateAttributesInElement(xNewRepeatPage, {"Rep":sNewRepNum})
            UtilsIOXml.RemoveAttributeInElement(xNewRepeatPage, "BookmarkID")
            
            iSubIndex = sPreviousPageID.find('-Rep')
            if iSubIndex >=0:
                sStrippedPageID = sPreviousPageID[0:iSubIndex]
            else:
                sStrippedPageID = sPreviousPageID
            
            sNewPageID = sStrippedPageID + '-Rep' + str(sNewRepNum)
            UtilsIOXml.UpdateAttributesInElement(xNewRepeatPage, {"ID":sNewPageID})
            
            
                
            # remove LabelmapPath and MarkupLinePath elements
            lxImages = UtilsIOXml.GetChildren(xNewRepeatPage, 'Image')
            for xImage in lxImages:
                UtilsIOXml.RemoveAllElements(xImage, "LabelMapPath")
                UtilsIOXml.RemoveAllElements(xImage, "MarkupLinePath")
                
            # remove Response elements
            lxQuestionSets = UtilsIOXml.GetChildren(xNewRepeatPage, "QuestionSet")
            for xQuestionSet in lxQuestionSets:
                lxQuestions = UtilsIOXml.GetChildren(xQuestionSet, "Question")
                for xQuestion in lxQuestions:
                    lxOptions = UtilsIOXml.GetChildren(xQuestion, "Option")
                    for xOption in lxOptions:
                        UtilsIOXml.RemoveAllElements(xOption, "Response")
        
        
        
        except:
            tb = traceback.format_exc()
            iPage = iPrevPageIndex + 1
            sMsg = 'AdjustQuizResultsFileForRepeatedPage: Trouble updating repeated page.' + \
                    ' Previous page rep number should be a string that can be converted to an integer.' +\
                    '\nSee Page: ' + str(iPage) + '\n\n' + tb
            UtilsMsgs.DisplayError(sMsg)
        
        
        
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
        sResponseTime = now.strftime(UtilsCustomXml.sTimestampFormat)
        
        dictAttrib = { 'LoginTime': self.LoginTime(), 'ResponseTime': sResponseTime}
        
        UtilsIOXml.AddElement(xOptionNode,'Response', sResponse, dictAttrib)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddImageStateElement(self, xImageNode, dictAttrib):
        """ Add the image state element to the xml file including window/level
            and slice offset. 
        """

        sNullData = ''

        # add login and response times to the existing state attributes
        now = datetime.now()
        sResponseTime = now.strftime(UtilsCustomXml.sTimestampFormat)
        
        dictTimeAttributes = { 'LoginTime': self.LoginTime(), 'ResponseTime': sResponseTime} 
        dictAttrib.update(dictTimeAttributes)

        UtilsIOXml.AddElement(xImageNode,'State', sNullData, dictAttrib)
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddPathElement(self, sElementName, xImageNode, sInputPath):
        
        # add login and response times to the label map path element
        now = datetime.now()
        sResponseTime = now.strftime(UtilsCustomXml.sTimestampFormat)
        
        dictAttrib = { 'LoginTime': self.LoginTime(), 'ResponseTime': sResponseTime} 
        
        UtilsIOXml.AddElement(xImageNode, sElementName, sInputPath, dictAttrib)
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddSessionLoginTimestamp(self):
        ''' Function to add an element holding the login time for the session.
            Set up the logout time attribute to be updated on each write.
            Also - record the user's name
        '''

        now = datetime.now()

        self.SetLoginTime( now.strftime(UtilsCustomXml.sTimestampFormat) )
        
        dictAttrib = {'LoginTime': self.LoginTime(), 'LogoutTime': self.LoginTime()}
        
        sNullText = ''
        
        UtilsIOXml.AddElement(self.GetRootNode(),'Login', sNullText, dictAttrib)
        
        UtilsIOXml.SaveXml(UtilsFilesIO.GetUserQuizResultsPath())
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def UpdateSessionLogoutTimestamp(self):
        ''' This function will add the attribute LogoutTime to the last entry of the Login element.
            Each time a 'Save' is done to the XML file, this Logout time will be overwritten.
            Then when the exit finally happens, it will reflect the last time a write was performed.
        '''

        now = datetime.now()

        sLogoutTime = now.strftime(UtilsCustomXml.sTimestampFormat)
        
        # get existing attributes from the Login element
        xLoginNode = UtilsIOXml.GetLastChild(self.GetRootNode(), "Login")
        
        if xLoginNode != None:
            # update logout time if login element exists
            dictAttrib = UtilsIOXml.GetAttributes(xLoginNode)
    
            dictAttrib['LogoutTime'] = sLogoutTime
                
            # reset the Login element
            UtilsIOXml.UpdateAttributesInElement(xLoginNode, dictAttrib)

            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetLastLoginTimestamp(self):
        # function to scan the user's quiz file for all session login times
        # return the last session login time

        lsTimestamps = []
        dtLastTimestamp = ''    # timestamp of type 'datetime'

        
        xmlLoginNodes = UtilsIOXml.GetChildren(self.GetRootNode(), 'Login')

        # collect all login timestamps (type 'string')
        for indElem in range(len(xmlLoginNodes)):
            # get date/time from attribute
            xmlLoginNode = UtilsIOXml.GetNthChild(self.GetRootNode(), 'Login', indElem)

            sTimestamp = UtilsIOXml.GetValueOfNodeAttribute(xmlLoginNode, 'LoginTime')
            lsTimestamps.append(sTimestamp)
            
            # look for Quiz Complete status
            sQuizCompleteStatus = UtilsIOXml.GetValueOfNodeAttribute(xmlLoginNode, 'QuizComplete')
            if sQuizCompleteStatus == 'Y':
                self.SetQuizComplete(True)
            

        # loop through timestamps to search for the last login occurrence
        for indTime in range(len(lsTimestamps)):
            
            sNewTimestamp = lsTimestamps[indTime]
            # convert to datetime format for compare
            dtNewTimestamp = datetime.strptime(sNewTimestamp, UtilsCustomXml.sTimestampFormat)
            
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
        xmlLastLoginElement = UtilsIOXml.GetLastChild(self.GetRootNode(),'Login')
        xmlLastLoginElement.set('QuizComplete','Y')
        UtilsIOXml.SaveXml(UtilsFilesIO.GetUserQuizResultsPath())

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddPageCompleteAttribute(self, idxPage):
        ''' add attribute to current page element to indicate all 
            question sets and segmentations have been completed
        '''
        xmlCurrentPageElement = UtilsIOXml.GetNthChild(self.GetRootNode(),'Page', idxPage)
        xmlCurrentPageElement.set('PageComplete','Y')
        UtilsIOXml.SaveXml(UtilsFilesIO.GetUserQuizResultsPath())

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetPageIncomplete(self, iPageIndex):
        ''' if requirements were not met, reset the PageComplete attribute to 'N'
        '''
        xPageNode = self.GetNthPageNode(iPageIndex)
        UtilsIOXml.UpdateAttributesInElement(xPageNode, {"PageComplete":"N"})
        UtilsIOXml.SaveXml(UtilsFilesIO.GetUserQuizResultsPath())
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddUserNameAttribute(self):
        ''' add attribute to Session to record the user's name
        '''
        xRootNode = self.GetRootNode()
        dictAttrib = UtilsIOXml.GetAttributes(xRootNode)

        dictAttrib['UserName'] = UtilsFilesIO.GetUsername()
            
        # reset the Login element
        UtilsIOXml.UpdateAttributesInElement(xRootNode, dictAttrib)

        UtilsIOXml.SaveXml(UtilsFilesIO.GetUserQuizResultsPath())

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetupLoopingInitialization(self):
        
        # if Loop="Y" for any page in the quiz, add Rep="0" to each page if not defined
        
        xRootNode = self.GetRootNode()
        bLoopingInQuiz = False
        lxPages = UtilsIOXml.GetChildren(xRootNode,'Page')
        for xPageNode in lxPages:
            sLoopAllowed = UtilsIOXml.GetValueOfNodeAttribute(xPageNode, "Loop")
            if sLoopAllowed == "Y":
                bLoopingInQuiz = True
                break
            
        if bLoopingInQuiz:
            for xPageNode in lxPages:
                sRepNum = UtilsIOXml.GetValueOfNodeAttribute(xPageNode, "Rep")
                try:
                    int(sRepNum)
                except:
                    # not a valid integer - create/set the attribute to 0
                    UtilsIOXml.UpdateAttributesInElement(xPageNode, {"Rep":"0"})
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetupPageGroupInitialization(self):
        ''' If no PageGroup attribute exists, update the XML to initialize each page
            to a unique number. Start PageGroup numbers at '1'. ('0' has specialized
            meaning when randomizing page groups.
        '''
        
        bPageGroupFound = False
        xRootNode = self.GetRootNode()
        
        lxPages = UtilsIOXml.GetChildren(xRootNode,'Page')
        for xPageNode in lxPages:
            sPageGroupNum = UtilsIOXml.GetValueOfNodeAttribute(xPageNode, "PageGroup")
            if sPageGroupNum != '':
                bPageGroupFound = True
                break
       
        if not bPageGroupFound:
            for iPageNum in range(len(lxPages)):
                xPageNode = UtilsIOXml.GetNthChild(xRootNode, "Page", iPageNum)
                UtilsIOXml.UpdateAttributesInElement(xPageNode, {"PageGroup":str(iPageNum + 1)})
        
