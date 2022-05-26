import os
import vtk, qt, ctk, slicer
import sys

import sitkUtils
import SimpleITK as sitk

import numpy as np



##########################################################################
#
# class PageState
#
##########################################################################

class PageState:
    
    def __init__(self, oSession):
        ''' Class to keep track of completed items that belong to a page.
            Segmentation completion state is a 2d list.
                The first element specifies whether it is required (0, 1, or -1)
                The second element specifies whether the requirement has been completed. (0 or 1)

                Code for required states:
                    0 = not required
                    1 = required
                    -1 = not applicable    (eg. image elements assigned to Layer='Segmentation' or 'Label')
                Codes for completed states:
                    0 = incomplete
                    1 = complete
                
            A completed page requires all questions in all question sets to be completed
            and either all or any segmentations (depending on the required segmentations attribute)
            to have been completed
            
            States for variable : sSegmentationRequiredState
                NoSegReq:   This variable is set to 'NoSegReq' as a default. The EnableSegmentEditor page attribute was set to "Y".
                        This remains at 'NoSegReq' if the other attributes (Image attribute: 'SegmentRequired' and 
                        Page attribute: 'SegmentRequiredOnAnyImage') are set to 'N' or are absent.
                        This means that the user is not required to create a contour (eg. if no tumor is present)
                        but has the ability to create one if desired.
                        
                AnySegReq:    This variable gets set to 'AnySegReq' if the page attribute SegmentRequiredOnAnyImage="Y" .
                        This means that the user is required to create at least one segmentation that is not zeroes
                        (zeros can happen if the user goes into the segment editor, selects a volume to edit but does
                        not actually create any segments. The mask is then all zeros.) 
                        Some kind of change must have been made to the segmentations - whether it is a new
                        segmentation on an image, or an existing segmentation is modified (if the segmentation was copied 
                        in from a previous page and redisplayed)           
                                     
                SpecificSegReq:   This variable gets set to 'SpecificSegReq' if there are any Image elements with the
                        'SegmentRequired' attribute set to "Y".
                        The user must create a segmentation for that specific image. It cannot be
                        an empty segmentation (where the mask is all zeros - see explanation in 'AnySegReq').
                        Also, if the image has a segmentation file that was copied in and redisplayed  
                        from a previous page (this occurs when the Image element has an attribute
                        'DisplayLabelMapID' set), the user is required to make a change to that copied in segmentation.
                        Images that are not set to 'SegmentRequired="Y"' are not subject to the above rules (they
                        could be empty or unmodified).
        '''
        self.liCompletedQuestionSets = []
        self.l2iCompletedSegmentations = []
        self.sSegmentationRequiredState = 'NoSegReq'
        self.bQuestionSetsCompleted = 'False'
        self.bSegmentationsCompleted = 'False'
        
        self.oSession = oSession
        self.oIOXml = self.oSession.oIOXml
        self.oFilesIO = self.oSession.oFilesIO
        
    #----------
    def GetCompletedQuestionSetsList(self):
        return self.liCompletedQuestionSets
    
    #----------
    def GetSegmentationsCompletedState(self):
        return self.bSegmentationsCompleted
        
    #----------
    def GetQuestionSetsCompletedState(self):
        return self.bQuestionSetsCompleted
    
    #----------
    def GetSegmentRequiredForImageTF(self, idxImage):
        ''' return T/F whether a segment is required for the image
        '''
        
        if self.l2iCompletedSegmentations[idxImage][0] == 1:
            return True
        else:
            return False
        
    #----------
    def GetPageCompletedTF(self):
        ''' return T/F if all elements are completed
        '''        
        if self.bQuestionSetsCompleted and self.bSegmentationsCompleted:
            bCompleted = True
        else:
            bCompleted = False
            
        return bCompleted
    
    #----------
    def CategorizeResponseCompletionLevel(self, iTotalItems, iCountedItems):
        ''' This function may be used to define the number of questions that had 
            responses stored in the XML or the number of responses the user
            made in the quiz form.
        '''
        
        if iCountedItems == iTotalItems:
            sCompletionLevel = 'AllResponses'
        elif iCountedItems == 0:
            sCompletionLevel = 'NoResponses'
        else:
            sCompletionLevel = 'PartialResponses'
        
        return sCompletionLevel        

    #----------
    def UpdateCompletionLists(self, xPageNode):
        ''' For the given indices, update the completion states in the lists
        '''
        
        self.UpdateQuestionSetCompletionList(xPageNode)
        self.UpdateSegmentationCompletionList(xPageNode)
        
    #----------
    def UpdateCompletedFlags(self, xPageNode):
        ''' Update completed flags for page elements
        '''
        sMsg = ''
        sQSetMsg = self.UpdatePageCompletionLevelForQuestionSets()
        sLabelMapMsg = self.UpdatePageCompletionLevelForSegmentations(xPageNode)
        sMsg = sQSetMsg + '\n' + sLabelMapMsg
        
        return sMsg
    
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def InitializeStates(self, xPageNode):
        ''' 
            Each question set is intialized as incomplete.
            Each image segmentation state is initialized as incomplete except when the image node
            has a layer defined as 'Segmentation' or 'Label'
            If the image has an attribute 'SegmentRequired' then there must exist a seg file specifically for that image.
            If the page has the attribute 'SegmentRequiredOnAnyImage' then there must exist a non-empty/modified labelmap file.
                
            The segmentation requirement attribute is captured at the Page element level.
            Each image that has a layer defined as 'Foreground' or 'Background'
            will have an entry initialized to 0. Other image layers (LabelMap or Segmentation)
            are set to a -1 (not applicable - segment only on fg/bg layers) 
        '''
        
        sPageComplete = self.oIOXml.GetValueOfNodeAttribute(xPageNode,'PageComplete')
        if sPageComplete == 'Y':
            self.bQuestionSetsCompleted = True
            self.bSegmentationsCompleted = True
            iCompletedTF = 1
        else:
            self.bQuestionSetsCompleted = False
            self.bSegmentationsCompleted = False
            iCompletedTF = 0
            
            
    
        lxQuestionSets = self.oIOXml.GetChildren(xPageNode,'QuestionSet')
        lxImageNodes = self.oIOXml.GetChildren(xPageNode,'Image')

        # initialize list of question sets to incomplete
        for xQSetNode in lxQuestionSets:
            self.liCompletedQuestionSets.append(iCompletedTF)


        # store segmentation requirement code (SpecificSegReq state introduced when looping through images)
        sSegmentationRequiredState = 'NoSegReq' # default
        sSegRequiredAnyImage = self.oIOXml.GetValueOfNodeAttribute(xPageNode,'SegmentRequiredOnAnyImage')
        if sSegRequiredAnyImage == 'Y' or sSegRequiredAnyImage == 'y':
            self.sSegmentationRequiredState = 'AnySegReq'

        l2iSegmentNotApplicableLayer = [-1,iCompletedTF]
        l2iSegmentNotRequired = [0,iCompletedTF]
        l2iSegmentRequired = [1,iCompletedTF]

        # initialize list of lists to zeros avoiding implicit reference sharing
        self.l2iCompletedSegmentations = [[0 for col in range(2)] for row in range(len(lxImageNodes))]
            
        for iImgIdx in range(len(lxImageNodes)):
            xImageNode = self.oIOXml.GetNthChild(xPageNode, 'Image', iImgIdx)
            xLayerNode = self.oIOXml.GetNthChild(xImageNode,'Layer',0)
            sLayer = self.oIOXml.GetDataInNode(xLayerNode)
            if sLayer == 'Segmentation' or sLayer == 'Label':
                self.l2iCompletedSegmentations[iImgIdx][0] = l2iSegmentNotApplicableLayer[0]
                self.l2iCompletedSegmentations[iImgIdx][1] = l2iSegmentNotApplicableLayer[1]
                
            else:
                sSegRequired = self.oIOXml.GetValueOfNodeAttribute(xImageNode,'SegmentRequired')
                if sSegRequired == 'Y' or sSegRequired == 'y':
                    self.l2iCompletedSegmentations[iImgIdx][0] = l2iSegmentRequired[0]
                    self.l2iCompletedSegmentations[iImgIdx][1] = l2iSegmentRequired[1]
                    
                    self.sSegmentationRequiredState = 'SpecificSegReq' # override default
                else:
                    self.l2iCompletedSegmentations[iImgIdx][0] = l2iSegmentNotRequired[0]
                    self.l2iCompletedSegmentations[iImgIdx][1] = l2iSegmentNotRequired[1]
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def UpdateQuestionSetCompletionList(self, xPageNode):
        ''' For the given page node, update the completion state level
            for each question set.
        '''
        
        lxQSetNodes = self.oIOXml.GetChildren(xPageNode, 'QuestionSet')
        iQSetIdx = -1
        for xQSetNode in lxQSetNodes:
            
            iQSetIdx = iQSetIdx + 1
            sSavedResponseCompletionLevel = self.GetSavedResponseCompletionLevel(xQSetNode)
        
            if sSavedResponseCompletionLevel == 'AllResponses':
                self.liCompletedQuestionSets[iQSetIdx] = 1
            else:
                self.liCompletedQuestionSets[iQSetIdx] = 0
                
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def UpdateSegmentationCompletionList(self, xPageNode):
        ''' Function to update the completion flags for segmentations for 
            each image stored in the list
        '''
        
        lxImageNodes = self.oIOXml.GetChildren(xPageNode,'Image')
        idxImage = -1

        #######################################
        # Image level segmentation completion
        for xImageNode in lxImageNodes:
            # initialize flags
            bExists = False
            bRedisplayed = False
            bEmptyLabelMap = True
            bModified = False
            idxImage = idxImage + 1
            xLabelMapElement = self.oIOXml.GetLastChild(xImageNode, 'LabelMapPath')

            
            if xLabelMapElement != None:
                sLabelMapRelativePath = self.oIOXml.GetDataInNode(xLabelMapElement)
                bExists = True
                
                # test for empty segmentation (label map exists but all zeros)
                sLabelMapAbsolutePath = self.oFilesIO.GetAbsoluteUserPath(sLabelMapRelativePath)
                bEmptyLabelMap = self.TestForEmptyLabelMap(sLabelMapAbsolutePath)
                
                # if labelmap is redisplayed from previous page, check for change in segmentation
                sLabelMapToRedisplay = self.oIOXml.GetValueOfNodeAttribute(xImageNode, 'DisplayLabelMapID')
                if sLabelMapToRedisplay != '':
                    bRedisplayed = True
                    # get image element from history that holds the same label map id; 
                    xHistoricalImageElement = None  # initialize
                    xHistoricalLabelMapMatch = None
                    xHistoricalImageElement = self.oSession.GetXmlElementFromAttributeHistory('Image','LabelMapID',sLabelMapToRedisplay)
                    if xHistoricalImageElement != None:
                        xHistoricalLabelMapMatch = self.oSession.oIOXml.GetLatestChildElement(xHistoricalImageElement, 'LabelMapPath')
                    
                        if xHistoricalLabelMapMatch != None:
                            # found a label map for this image in history
                            sHistoricalLabelMapRelativePath = self.oIOXml.GetDataInNode(xHistoricalLabelMapMatch)
                            sHistoricalLabelMapAbsolutePath = self.oFilesIO.GetAbsoluteUserPath(sHistoricalLabelMapRelativePath)
                            bModified = self.TestForModifiedLabelMap(sHistoricalLabelMapAbsolutePath, sLabelMapAbsolutePath)
                        else:
                            # there was no labelmap in history so this must be a 'new' contour - reset flag
                            bRedisplayed = False


            # set segmentation completion state for the image based on the image segmentation required level
            #     if state is 'NoSegReq' - segmentation just needs to exist; non-zero or modified is irrelevant
            if self.sSegmentationRequiredState == 'NoSegReq':
                if bExists:
                    self.l2iCompletedSegmentations[idxImage][1] = 1
                    
            #    if state is 'AnySegReq' - some kind of change must have happened to the segmentations
            #        (either new & non-zero or redisplayed & modified)
            if self.sSegmentationRequiredState == 'AnySegReq':
                if bExists:
                    if bRedisplayed:
                        if bModified and not bEmptyLabelMap:
                            self.l2iCompletedSegmentations[idxImage][1] = 1
                    else:   # a new segmentation
                        if not bEmptyLabelMap :
                            self.l2iCompletedSegmentations[idxImage][1] = 1
                    
            #    if state is 'SpecificSegReq' - check whether the code for segment required (first element) was set and
            #        the labelmap file must be non-zero; if redisplayed it must be modified
            if self.sSegmentationRequiredState == 'SpecificSegReq':
                if self.l2iCompletedSegmentations[idxImage][0] == 1:    # required
                    if bRedisplayed:
                        if bModified and not bEmptyLabelMap:
                            self.l2iCompletedSegmentations[idxImage][1] = 1
                    else:
                        if not bEmptyLabelMap:
                            self.l2iCompletedSegmentations[idxImage][1] = 1
                else:
                    # segmentation not required 
                    #    it is completed if it is not empty; does not require modification if redisplayed
                    if not bEmptyLabelMap:
                        self.l2iCompletedSegmentations[idxImage][1] = 1
            
                

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def UpdatePageCompletionLevelForQuestionSets(self):
        ''' Test to see if all question sets on a page have been completed.
        '''
        sMsg = ''
        if 0 in self.liCompletedQuestionSets:
            self.bQuestionSetsCompleted = False
            sMsg = 'Not all question sets were completed'
        else:
            self.bQuestionSetsCompleted = True
            
        return sMsg

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def UpdatePageCompletionLevelForSegmentations(self, xPageNode):
        ''' Based on the segmentation completion level over all the images, the flag for
            completion of segmentation at the Page level is determined. 
        '''
        #######################################
        # Page level segmentation completion
        # set the segmentations completed flag for this page if requirements are met for all images
        sMsg = ''
        
        if self.sSegmentationRequiredState == 'NoSegReq' or self.sSegmentationRequiredState == 'AnySegReq':
            self.bSegmentationsCompleted = False
            if len(self.l2iCompletedSegmentations) == 0:    # case for no images on page
                self.bSegmentationsCompleted = True
            else:
                for idx in range(len(self.l2iCompletedSegmentations)):
                    if self.l2iCompletedSegmentations[idx][1] == 1:
                        self.bSegmentationsCompleted = True

            # for 'AnySegReq' at least one completed segmentation must exist
            # for 'NoSegReq', no segmentations is acceptable
            if not self.bSegmentationsCompleted:
                if self.sSegmentationRequiredState == 'AnySegReq':
                    sMsg = sMsg + '\nYou must complete one segmentation for any of the images.' + \
                            '\nYou can create a new segmentation or modify a segmentation that was redisplayed.'
                else:
                    if self.sSegmentationRequiredState == 'NoSegReq':
                        self.bSegmentationsCompleted = True
                
        else:
            # for 'SpecificSegReq' the images marked with the 'required' code must also have the 'completed' code
            if self.sSegmentationRequiredState == 'SpecificSegReq':
                self.bSegmentationsCompleted = True
                for idx in range(len(self.l2iCompletedSegmentations)):
                    if self.l2iCompletedSegmentations[idx][0] == 1 : # required on this image
                        if self.l2iCompletedSegmentations[idx][1] != 1: # segmentation not complete
                            self.bSegmentationsCompleted = False
                            xImageNode = self.oIOXml.GetNthChild(xPageNode, 'Image', idx)
                            sPageID = self.oIOXml.GetValueOfNodeAttribute(xPageNode,'ID')
                            sImageID = self.oIOXml.GetValueOfNodeAttribute(xImageNode,'ID')
                            sNodeName = sPageID + '_' + sImageID
                            sMsg = sMsg +  '\nYou must complete a segmentation for this image: ' + sNodeName + \
                                '\nIf a contour has been redisplayed for this image, it must be modified. It cannot be empty.' + \
                                '\nSelect the image: "'+ sNodeName + '" as the Master Volume in the Segment Editor.'
        
        return sMsg
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def TestForEmptyLabelMap(self, sPath):
        ''' A function to look at pixels of label map node to determine if a segment exists
            (non-zero pixels)
        '''
        img = sitk.ReadImage(sPath)
        stats = sitk.StatisticsImageFilter()
        stats.Execute(img)
        fMin = stats.GetMinimum()
        fMax = stats.GetMaximum()
        
        if fMin == 0 and fMax == 0:
            bLabelMapEmpty = True
        else:
            bLabelMapEmpty = False
            
        return bLabelMapEmpty

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def TestForModifiedLabelMap(self, sPathHistorical, sPathNew):
        ''' A function to test if the labelmap file copied into the new page folder has been
            modified from the original.
        '''
        
        imgHistorical = sitk.ReadImage(sPathHistorical)
        imgNew = sitk.ReadImage(sPathNew)
        
        npArrayImgHistorical = sitk.GetArrayViewFromImage(imgHistorical)
        npArrayImgNew = sitk.GetArrayViewFromImage(imgNew)
        
        if np.array_equal(npArrayImgHistorical, npArrayImgNew):
            bModified = False
        else:
            bModified = True
        
        return bModified
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetSavedResponseCompletionLevel(self, xQuestionSetNode):
        """ Check through all questions for the question set looking for a response. This information
            comes from the currently saved elements in the XML.
             
            Assumption: All'Option' elements have a 'Response' element if the question was answered
            so we just query the first Response 
            
            eg: Radio Question     Success?
                    Opt 1            yes
                        Response:       y (checked)
                    Opt 2            no
                        Response:       n (not checked) 
            
        """
        
        iNumAnsweredQuestions = 0
        
        # xQuestionSetNode = self.GetCurrentQuestionSetNode()
        
        iNumQuestions = self.oIOXml.GetNumChildrenByName(xQuestionSetNode, 'Question')

        for indQuestion in range(iNumQuestions):
            # get first option for the question (all (or none) options have a response so just check the first)
            xQuestionNode = self.oIOXml.GetNthChild(xQuestionSetNode, 'Question', indQuestion)
            xOptionNode = self.oIOXml.GetNthChild(xQuestionNode, 'Option', 0)
         
            iNumResponses = self.oIOXml.GetNumChildrenByName(xOptionNode,'Response')
            if iNumResponses >0:
                iNumAnsweredQuestions = iNumAnsweredQuestions + 1
                 
        sSavedResponseCompletionLevel = self.CategorizeResponseCompletionLevel(iNumQuestions, iNumAnsweredQuestions)

        return sSavedResponseCompletionLevel
           
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
