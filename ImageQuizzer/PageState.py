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
    
    def __init__(self):
        ''' Class to keep track of completed items that belong to a page.

            A completed page requires:
                - all questions in all question sets to be completed
                - either all or any segmentations to have been completed
                  (depending on the required segmentations attribute)
                - if a number of markup lines was specified as required, at least that number must exist
            

            Segmentation completion state is a list of lists. Each image (one row) has a list of 2 elements
                The first element specifies whether the requirement has been completed. (0 or 1)
                The second element specifies whether it is required (0 or 1)                

                Codes for completed states:
                    0 = incomplete
                    1 = complete
                Code for required states:
                    0 = not required
                    1 = required 
                
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
                        
            Markup Lines completion state is a list of lists. Each image (one row) has a list of 3 elements.
                The first element specifies whether the requirement has been completed. (0 or 1)
                The second element specifies the minimum number of lines required for that image
                The third element holds the number of markup lines currently saved in the xml for that image
                               
                Codes for completed states (first element):
                    0 = incomplete
                    1 = complete
                Code for required states (second element):
                    0 = not required
                    n = minimum n number of items required for markup lines on a specified image
                Code for current markup lines (third element):
                    n = number of markup lines currently saved in the xml
                    
               
            States for variable: sMarkupLineRequiredState and iMarkupLinesOnAnyImageMinimum
                NoLinesReq:    This variable is set to 'NoLinesReq' as a default. If there are no markup lines attributes
                        ('MinMarkupLinesRequiredOnAnyImage' at the Page level or 'MinMarkupLinesRequired'at the image level)
                        then this variable remains at NoLinesReq
                        
                AnyLinesReq:    This variable gets set to 'AnyLinesReq' if at the Page level the attribute 'MinMarkupLinesRequiredOnAnyImage'
                        is set. The value of this attribute represents minimum number of lines must be created and they can be on any image.
                        For 'AnyLinesReq' this minimum number is stored in the variable iMarkupLinesOnAnyImageMinimum for comparison
                        when determining page completeness.
                        
                SpecificLinesReq: This variable gets set to 'SpecificLinesReq' if there is an attribute 'MinMarkupLinesRequired' set
                        at the image level. The value of this attribute represents the minimum number of lines must be created for this image.
                    
        '''
        self.ClearPageStateVariables()
        
    #----------
    def ClearPageStateVariables(self):
        
        self.liCompletedQuestionSets = []
        self.l2iCompletedSegmentations = []
        self.l3iCompletedMarkupLines = []
        self.sSegmentationRequiredState = 'NoSegReq'
        self.sMarkupLineRequiredState = 'NoLinesReq'
        self.bQuestionSetsCompleted = 'False'
        self.bSegmentationsCompleted = 'False'
        self.bMarkupLinesCompleted = 'False'
        self.iMarkupLinesOnAnyImageMinimum = 0
        
        
    #----------
    def GetCompletedQuestionSetsList(self):
        return self.liCompletedQuestionSets
    
    
    #----------
    def GetSegmentationsCompletedState(self):
        return self.bSegmentationsCompleted
    
    #----------
    def GetPageCompletedTF(self):
        ''' return T/F if all elements are completed
        '''        
        if self.bQuestionSetsCompleted and \
                self.bSegmentationsCompleted and \
                self.bMarkupLinesCompleted:
            
            bCompleted = True
        else:
            bCompleted = False
            
        return bCompleted
    
    #----------
    #----------
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def InitializeStates(self, oSession, xPageNode):
        ''' 
            Each question set is intialized as incomplete.

            Each image segmentation state is initialized as incomplete.
            If the xml Image element has an attribute 'SegmentRequired' then 
                there must exist a seg file specifically for that image.
            If the xml Page element has the attribute 'SegmentRequiredOnAnyImage' then 
                there must exist a non-empty/modified labelmap file.

            Each image markup lines state is initialized as incomplete
            If the xml Image element has an attribute 'MinMarkupLinesRequired' then there must exist
                a markup line(s) specifically for that image.
                The value of the attribute is the minimum number of lines that must be created.
            If the xml Page element has the attribute 'MinMarkupLinesRequiredOnAnyImage', then
                the value of the attribute represents the minimum number of lines that must be
                created. These can be associated with any displayed image.
             
        '''
        self.oSession = oSession
        self.oIOXml = self.oSession.oIOXml
        self.oFilesIO = self.oSession.oFilesIO

        self.ClearPageStateVariables()
        
        sPageComplete = self.oIOXml.GetValueOfNodeAttribute(xPageNode,'PageComplete')
        if sPageComplete == 'Y':
            self.bQuestionSetsCompleted = True
            self.bSegmentationsCompleted = True
            self.bMarkupLinesCompleted = True
            iCompletedTF = 1
        else:
            self.bQuestionSetsCompleted = False
            self.bSegmentationsCompleted = False
            self.bMarkupLinesCompleted = False
            iCompletedTF = 0
            
        lxQuestionSets = self.oIOXml.GetChildren(xPageNode,'QuestionSet')
        lxImageNodes = self.oIOXml.GetChildren(xPageNode,'Image')

        # initialize list of question sets to incomplete
        for xQSetNode in lxQuestionSets:
            self.liCompletedQuestionSets.append(iCompletedTF)


        ##########################
        # store requirement codes - for not required or required on any image
        ##########################
        sSegRequiredAnyImage = self.oIOXml.GetValueOfNodeAttribute(xPageNode,'SegmentRequiredOnAnyImage')
        if sSegRequiredAnyImage == 'Y' or sSegRequiredAnyImage == 'y':
            self.sSegmentationRequiredState = 'AnySegReq'

        self.iMarkupLinesOnAnyImageMinimum = 0
        sLinesRequiredAnyImage = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'MinMarkupLinesRequiredOnAnyImage')
        if sLinesRequiredAnyImage != '':
            self.sMarkupLineRequiredState = 'AnyLinesReq'
            self.iMarkupLinesOnAnyImageMinimum = int(sLinesRequiredAnyImage)


        ##########################
        # store requirement codes - for required on specific images
        ##########################

        # initialize list of lists to zeros avoiding implicit reference sharing
        self.l2iCompletedSegmentations = [[0 for col in range(2)] for row in range(len(lxImageNodes))]
        self.l3iCompletedMarkupLines = [[0 for col in range(3)] for row in range(len(lxImageNodes))]
            
        for iImgIdx in range(len(lxImageNodes)):
            xImageNode = self.oIOXml.GetNthChild(xPageNode, 'Image', iImgIdx)
            lxMarkupLinePathNodes = self.oIOXml.GetChildren(xImageNode, 'MarkupLinePath')
#             xLayerNode = self.oIOXml.GetNthChild(xImageNode,'Layer',0)
#             sLayer = self.oIOXml.GetDataInNode(xLayerNode)
#             if sLayer == 'Segmentation' or sLayer == 'Label':
#                 # use code = -1 for not applicable 
#                 self.l2iCompletedSegmentations[iImgIdx] = [-1, iCompletedTF]
#                 self.l3iCompletedMarkupLines[iImgIdx] = [-1, iCompletedTF, 0]
#             
#             else:

            
            ##########################
            # segments
            sSegRequired = self.oIOXml.GetValueOfNodeAttribute(xImageNode,'SegmentRequired')
            if sSegRequired == 'Y' or sSegRequired == 'y':
                # use code = 1 for required  
                self.l2iCompletedSegmentations[iImgIdx] = [iCompletedTF, 1]
                self.sSegmentationRequiredState = 'SpecificSegReq' # override default
            else:
                # self.l2iCompletedSegmentations[iImgIdx] = l2iNotRequired
                self.l2iCompletedSegmentations[iImgIdx] = [iCompletedTF, 0]
                

            ##########################
            # markup lines
            sLinesRequired = self.oIOXml.GetValueOfNodeAttribute(xImageNode,'MinMarkupLinesRequired')
            if sLinesRequired != '':
                # use code = 'n' for minimum number of lines required  
                self.sMarkupLineRequiredState = 'SpecificLinesReq' # override default
                self.l3iCompletedMarkupLines[iImgIdx][0] = iCompletedTF
                self.l3iCompletedMarkupLines[iImgIdx][1] = int(sLinesRequired)
                self.l3iCompletedMarkupLines[iImgIdx][2] = len(lxMarkupLinePathNodes)
            else:
                # use code = 0 for not required 
                self.l3iCompletedMarkupLines[iImgIdx] = [iCompletedTF, 0, len(lxMarkupLinePathNodes)]
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def UpdateCompletionLists(self, xPageNode):
        ''' For the given xml page element, update the completion states in the lists
        '''
        
        self.UpdateQuestionSetCompletionList(xPageNode)
        self.UpdateSegmentationCompletionList(xPageNode)
        self.UpdateMarkupLinesCompletionList(xPageNode)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def UpdateCompletedFlags(self, xPageNode):
        ''' Update completed flags for the give xml page element
        '''
        sMsg = ''
        sQSetMsg = self.UpdatePageCompletionLevelForQuestionSets()
        sLabelMapMsg = self.UpdatePageCompletionLevelForSegmentations(xPageNode)
        sMarkupLineMsg = self.UpdatePageCompletionLevelForMarkupLines(xPageNode)
        sMsg = sQSetMsg + '\n' + sLabelMapMsg + '\n' + sMarkupLineMsg
        
        return sMsg
    
    #-------------------------------------------
    #        Question Set Functions
    #-------------------------------------------

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def UpdateQuestionSetCompletionList(self, xPageNode):
        ''' For the given xml page node, update the completion state level
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
           

    #-------------------------------------------
    #        Segmentation Functions
    #-------------------------------------------
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def UpdateSegmentationCompletionList(self, xPageNode):
        ''' For the given xml page node, this function will update the completion flags 
            for segmentations for each image stored in the list.
            This is based on the LabelMapPath element stored in the xml Image element.
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
                    self.l2iCompletedSegmentations[idxImage][0] = 1
                    
            #    if state is 'AnySegReq' - some kind of change must have happened to the segmentations
            #        (either new & non-zero or redisplayed & modified)
            if self.sSegmentationRequiredState == 'AnySegReq':
                if bExists:
                    if bRedisplayed:
                        if bModified and not bEmptyLabelMap:
                            self.l2iCompletedSegmentations[idxImage][0] = 1
                    else:   # a new segmentation
                        if not bEmptyLabelMap :
                            self.l2iCompletedSegmentations[idxImage][0] = 1
                    
            #    if state is 'SpecificSegReq' - check whether the code for segment required (second element) was set and
            #        the labelmap file must be non-zero; if redisplayed it must be modified
            if self.sSegmentationRequiredState == 'SpecificSegReq':
                if self.l2iCompletedSegmentations[idxImage][1] == 1:    # required
                    if bRedisplayed:
                        if bModified and not bEmptyLabelMap:
                            self.l2iCompletedSegmentations[idxImage][0] = 1
                    else:
                        if not bEmptyLabelMap:
                            self.l2iCompletedSegmentations[idxImage][0] = 1
                else:
                    # segmentation not required 
                    #    it is completed if it is not empty; does not require modification if redisplayed
                    if not bEmptyLabelMap:
                        self.l2iCompletedSegmentations[idxImage][0] = 1
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def UpdatePageCompletionLevelForSegmentations(self, xPageNode):
        ''' Based on the segmentation completion level over all the images, the flag for
            completion of segmentation at the Page level is determined. 
        '''
        # set the segmentations completed flag for this page if requirements are met for all images
        sMsg = ''
        
        if self.sSegmentationRequiredState == 'NoSegReq' or self.sSegmentationRequiredState == 'AnySegReq':
            self.bSegmentationsCompleted = False
            if len(self.l2iCompletedSegmentations) == 0:    # case for no images on page
                self.bSegmentationsCompleted = True
            else:
                for idx in range(len(self.l2iCompletedSegmentations)):
                    if self.l2iCompletedSegmentations[idx][0] == 1:
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
                    if self.l2iCompletedSegmentations[idx][1] == 1 : # required on this image
                        if self.l2iCompletedSegmentations[idx][0] != 1: # segmentation not complete
                            self.bSegmentationsCompleted = False
                            xImageNode = self.oIOXml.GetNthChild(xPageNode, 'Image', idx)
                            sPageID = self.oIOXml.GetValueOfNodeAttribute(xPageNode,'ID')
                            sImageID = self.oIOXml.GetValueOfNodeAttribute(xImageNode,'ID')
                            sNodeName = sPageID + '_' + sImageID
                            sSegReqMsg = '\nYou must complete a segmentation for this image: ' + sNodeName + \
                                '\nIf a contour has been redisplayed for this image, it must be modified. It cannot be empty.' + \
                                '\nSelect the image: "'+ sNodeName + '" as the Master Volume in the Segment Editor.'
                            if sSegReqMsg != sMsg:
                                sMsg = sMsg + sSegReqMsg 
        
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
        

    #-------------------------------------------
    #        Markup Line Functions
    #-------------------------------------------

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def UpdateMarkupLinesCompletionList(self, xPageNode):
        ''' For the given xml page node, this function will update the completion flags 
            for markup lines for each image stored in the list.
            This is based on the MarkupLinePath element stored in the Image element.
        '''
        lsRecordedLinePaths = []
        lxImageNodes = self.oIOXml.GetChildren(xPageNode,'Image')
        idxImage = -1

        for xImageNode in lxImageNodes:
            idxImage = idxImage + 1
            lxMarkupLinePathElement = self.oIOXml.GetChildren(xImageNode, 'MarkupLinePath')
            self.l3iCompletedMarkupLines[idxImage][2] = len(lxMarkupLinePathElement)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def UpdatePageCompletionLevelForMarkupLines(self, xPageNode):
        ''' Test to see if all markup lines on a page have been completed.
        '''
        sMsg = ''

        self.bMarkupLinesCompleted = False
        
        if self.sMarkupLineRequiredState == 'NoLinesReq':
            self.bMarkupLinesCompleted = True

        
        elif self.sMarkupLineRequiredState == 'AnyLinesReq':
            lsUniqueImagePaths = []
            iNumLines = 0
            # count number of lines created - lines can be on any image
            #    - some images are repeated in different views so we want to
            #    only add to the total if it's a different image
            for iImageIdx in range(len(self.l3iCompletedMarkupLines)):
                xImageNode = self.oIOXml.GetNthChild(xPageNode, 'Image', iImageIdx)
                xImagePathNode = self.oIOXml.GetNthChild(xImageNode,'Path', 0)
                sImagePath = self.oIOXml.GetDataInNode(xImagePathNode)
                if iImageIdx == 0:
                    iNumLines = iNumLines + self.l3iCompletedMarkupLines[iImageIdx][2]
                    lsUniqueImagePaths.append(sImagePath)
                    
                bPathAlreadyRecorded = False
                for sUniquePath in lsUniqueImagePaths:
                    if sUniquePath == sImagePath:
                        bPathAlreadyRecorded = True
                        
                if bPathAlreadyRecorded == False:
                    iNumLines = iNumLines + self.l3iCompletedMarkupLines[iImageIdx][2]
                    lsUniqueImagePaths.append(sImagePath)
                    
                    
            # total number must be >= to the stored requirement
            if iNumLines >= self.iMarkupLinesOnAnyImageMinimum:
                self.bMarkupLinesCompleted = True
            else:
                self.bMarkupLinesCompleted = False
                sMsg = sMsg + '\nYou must complete at least ' + str(self.iMarkupLinesOnAnyImageMinimum) + ' markup lines on any image.' + \
                            '\nCurrently you have ' + str(iNumLines) + ' lines created.' + \
                            '\nUse the ruler markup tool to draw the lines on on any of the displayed images.'                       

        
        else:
            if self.sMarkupLineRequiredState == 'SpecificLinesReq':
                self.bMarkupLinesCompleted = True
                for idx in range(len(self.l3iCompletedMarkupLines)):
                    if self.l3iCompletedMarkupLines[idx][2] < self.l3iCompletedMarkupLines[idx][1]:
                        self.bMarkupLinesCompleted = False
                        xImageNode = self.oIOXml.GetNthChild(xPageNode, 'Image', idx)
                        sPageID = self.oIOXml.GetValueOfNodeAttribute(xPageNode,'ID')
                        sImageID = self.oIOXml.GetValueOfNodeAttribute(xImageNode,'ID')
                        sNodeName = sPageID + '_' + sImageID
                        sMsg = sMsg +  '\nYou must complete at least ' + str(self.l3iCompletedMarkupLines[idx][1]) + \
                                    ' markup lines for this image: ' + sNodeName + \
                                    '\nCurrently you have ' + str(self.l3iCompletedMarkupLines[idx][2]) + ' lines created.' + \
                                    '\nUse the markup tool to draw the lines on this image.'                       
        

        return sMsg
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
