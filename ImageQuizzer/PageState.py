import os
import vtk, qt, ctk, slicer
import sys

import sitkUtils
import SimpleITK as sitk




##########################################################################
#
# class PageState
#
##########################################################################

class PageState:
    
    def __init__(self, oSession):
        ''' Class to keep track of completed items that belong to a page.
            Segmentation completion state is a 2d list.
                The first element specifies whether it is required (0, 1, or 2)
                The second element specifies whether the requirement has been completed. (0 or 1)

                Codes for completed states:
                    0 = incomplete
                    1 = complete
                Code for required states:
                    0 = not required
                    1 = required
                    2 = not applicable
                
            A completed page requires all questions in all question sets to be completed
            and either all or any segmentations (depending on the required segmentations attribute)
            to have been completed
            
            States for variable : sSegmentationRequiredState
                None:   This variable is set to 'None' as a default. The EnableSegmentEditor page attribute was set to "Y".
                        This remains at 'None' if the other attributes (Image attribute: 'SegmentRequired' and 
                        Page attribute: 'SegmentRequiredOnAnyImage') are set to 'N' or are absent.
                        This means that the user is not required to create a contour (eg. if no tumor is present)
                        but has the ability to create one if desired.
                        
                Any:    This variable gets set to 'Any' if the page attribute SegmentRequiredOnAnyImage="Y" .
                        This means that the user is required to create at least one segmentation that is not zeroes
                        (zeros can happen if the user goes into the segment editor, selects a volume to edit but does
                        not actually create any segments. The mask is then all zeros.) The redisplayed segmentation
                        may remain unmodified.
                        
                Specific:   This variable gets set to 'Specific' if there are any Image elements with the
                            'SegmentRequired' attribute set to "Y".
                            The user must create a segmentation for that specific image. It cannot be
                            an empty segmentation (where the mask is all zeros - see explanation in 'Any').
                            Also, if the image has a segmentation file that was copied in and redisplayed  
                            from a previous page (this occurs when the Image element has an attribute
                            'DisplayLabelMapID' set), the user is required to make a change to that copied in segmentation.
        '''
        self.liCompletedQuestionSets = []
        self.l2iCompletedSegmentations = []
        self.sSegmentationRequiredState = 'None'
        self.bQuestionSetsCompleted = 'False'
        self.bSegmentationsCompleted = 'False'
        
        self.oSession = oSession
        self.oIOXml = self.oSession.oIOXml
        self.oFilesIO = self.oSession.oFilesIO
        
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
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def InitializeStates(self, xPageNode):
        ''' 
            Each question set is intialized as incomplete.
            Each image segmentation state is initialized as incomplete except when the image node
            has a layer defined as 'Segmentation' or 'Layer'
            If the image has an attribute 'SegmentRequired' then there must exist a seg file specifically for that image.
            If the page has the attribute 'SegmentRequiredOnAnyImage' then there must exist a non-empty/modified labelmap file.
                
            The segmentation requirement attribute is captured at the Page element level.
            Each image that has a layer defined as 'Foreground' or 'Background'
            will have an entry initialized to 0. Other image layers (LabelMap or Segmentation)
            are set to a 2 (not applicable - segment only on fg/bg layers) 
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


        # store segmentation requirement code
        sSegmentationRequiredState = 'None' # default
        sSegRequiredAnyImage = self.oIOXml.GetValueOfNodeAttribute(xPageNode,'SegmentRequiredOnAnyImage')
        if sSegRequiredAnyImage == 'Y' or sSegRequiredAnyImage == 'y':
            self.sSegmentationRequiredState = 'Any'

        l2iSegmentNotApplicableLayer = [2,iCompletedTF]
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
                    
                    self.sSegmentationRequiredState = 'Specific' # override default
                else:
                    self.l2iCompletedSegmentations[iImgIdx][0] = l2iSegmentNotRequired[0]
                    self.l2iCompletedSegmentations[iImgIdx][1] = l2iSegmentNotRequired[1]
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CheckPageCompletionLevelForQuestionSets(self):
        ''' Test to see if all question sets on a page have been completed.
        '''
        if 0 in self.liCompletedQuestionSets:
            self.bQuestionSetsCompleted = False
        else:
            self.bQuestionSetsCompleted = True
            
        return self.bQuestionSetsCompleted

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CheckPageCompletionLevelForSegmentations(self, xPageNode):
        ''' Based on the segmentation completion level over all the images, the flag for
            completion of segmentation at the Page level is determined. 
        '''
        #######################################
        # Page level segmentation completion
        # set the segmentations completed flag for this page if requirements are met for all images
        sMsg = ''
        
        if self.sSegmentationRequiredState == 'None' or self.sSegmentationRequiredState == 'Any':
            self.bSegmentationsCompleted = False
            for idx in range(len(self.l2iCompletedSegmentations)):
                if self.l2iCompletedSegmentations[idx][1] == 1:
                    self.bSegmentationsCompleted = True

            # for 'Any' at least one segmentation must exist
            # for 'None', no segmentations is acceptable
            if not self.bSegmentationsCompleted:
                if self.sSegmentationRequiredState == 'Any':
                    sMsg = sMsg + '\nYou must complete one segmentation for any of the images.'
                else:
                    if self.sSegmentationRequiredState == 'None':
                        self.bSegmentationsCompleted = True
                
        else:
            if self.sSegmentationRequiredState == 'Specific':
                self.bSegmentationsCompleted = True
                for idx in range(len(self.l2iCompletedSegmentations)):
                    if self.l2iCompletedSegmentations[idx][0] == 1 : # required on this image
                        if self.l2iCompletedSegmentations[idx][1] != 1: # segmentation not complete
                            self.bSegmentationsCompleted = False
                            xImageNode = self.oIOXml.GetNthChild(xPageNode, 'Image', idx)
                            sImageID = self.oIOXml.GetValueOfNodeAttribute(xImageNode,'ID')
                            sMsg = sMsg +  '\nSegmentation missing for image: ' + sImageID + \
                            '\nIf image has been redisplayed, it must be modified'
        
        return sMsg
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def UpdateQuestionSetCompletionState(self, iQSetIdx, iCompletionCode):
        ''' Function to update the completion level for a specific question set on a Page
        '''
        self.liCompletedQuestionSets[iQSetIdx] = iCompletionCode
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def UpdateSegmentationCompletionState(self, xPageNode):
        ''' Function to update the completion flags for segmentations for each image.
        '''
        
        sMsg = ''
        
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


            # set segmentation completion state for the image based on the image segmentation required level
            #     if 'None' - segmentation just needs to exist; non-zero or modified is irrelevant
            if self.sSegmentationRequiredState == 'None':
                if bExists:
                    self.l2iCompletedSegmentations[idxImage][1] = 1
                    
            #    if 'Any' - segmentation must be non-zero in order to be complete 
            #        - it can be unmodified if it was redisplayed
            if self.sSegmentationRequiredState == 'Any':
                if bExists and not bEmptyLabelMap :
                    self.l2iCompletedSegmentations[idxImage][1] = 1
                    
            #    if 'Specific' - check whether 'SegmentRequired' was set and
            #        the labelmap file must be non-zero; if redisplayed it must be modified
            if self.sSegmentationRequiredState == 'Specific':
                if self.l2iCompletedSegmentations[idxImage][0] == 1:
                    if bRedisplayed:
                        if bModified and not bEmptyLabelMap:
                            self.l2iCompletedSegmentations[idxImage][1] = 1
                    else:
                        if not bEmptyLabelMap:
                            self.l2iCompletedSegmentations[idxImage][1] = 1
            
                
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
        
#         bModified = False
#         bModified = filecmp.cmp(sPathHistorical, sPathNew, shallow=False)

        imgHistorical = sitk.ReadImage(sPathHistorical)
        imgNew = sitk.ReadImage(sPathNew)
        
        # if imgHistorical == imgNew:
        #     bModified = False
        # else:
        #     bModified = True
        
        npArrayImgHistorical = sitk.GetArrayViewFromImage(imgHistorical)
        npArrayImgNew = sitk.GetArrayViewFromImage(imgNew)
        
        if (npArrayImgHistorical == npArrayImgNew).all():
            bModified = False
        else:
            bModified = True
        
        return bModified
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
