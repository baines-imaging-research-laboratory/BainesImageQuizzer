import os
import vtk, qt, ctk, slicer
import sys






##########################################################################
#
# class PageState
#
##########################################################################

class PageState:
    
    def __init__(self, oIOXml):
        ''' Class to keep track of completed items that belong to a page.
            Codes for completed states:
                0 = incomplete
                1 = complete
            Code for required states:
                0 = not required
                1 = required
                2 = not applicable
            Segmentation completion state is a 2d list.
                The first element specifies whether it is required (0, 1, or 2)
                The second element specifies whether the requirement has been completed. (0 or 1)
                
            A completed page requires all questions in all question sets to be completed
            and either all or any segmentations (depending on the required segmentations attribute)
            to have been completed
        '''
        self.liCompletedQuestionSets = []
        self.l2iCompletedSegmentations = []
        self.sSegmentationRequiredState = 'None'
        self.bQuestionSetsCompleted = 'False'
        self.bSegmentationsCompleted = 'False'
        
        self.oIOXml = oIOXml
        
        
    def InitializeStates(self, xPageNode):
        ''' 
            Each question set is intialized as incomplete.
            Each image segmentation state is initialized as incomplete except when the image node
            has a layer defined as 'Segmentation' or 'Layer'
            If the image has an attribute 'SegmentRequired' then there must exist a seg file.
                
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
            
            
    
        xQuestionSets = self.oIOXml.GetChildren(xPageNode,'QuestionSet')
        xImages = self.oIOXml.GetChildren(xPageNode,'Image')

        # initialize list of question sets to incomplete
        for xQSetNode in xQuestionSets:
            self.liCompletedQuestionSets.append(iCompletedTF)


        # store segmentation requirement code
        sSegmentationRequiredState = 'None' # default
        sSegRequiredAnyImage = self.oIOXml.GetValueOfNodeAttribute(xPageNode,'SegmentRequiredOnAnyImage')
        if sSegRequiredAnyImage == 'Y' or sSegRequiredAnyImage == 'y':
            self.sSegmentationRequiredState = 'Any'

        l2iSegmentNotApplicableLayer = [2,iCompletedTF]
        l2iSegmentNotRequired = [0,iCompletedTF]
        l2iSegmentRequired = [1,iCompletedTF]

            
        for iImgIdx in range(len(xImages)):
            xImageNode = self.oIOXml.GetNthChild(xPageNode, 'Image', iImgIdx)
            xLayerNode = self.oIOXml.GetNthChild(xImageNode,'Layer',0)
            sLayer = self.oIOXml.GetDataInNode(xLayerNode)
            if sLayer == 'Segmentation' or sLayer == 'Label':
                self.l2iCompletedSegmentations.append(l2iSegmentNotApplicableLayer)
            else:
                sSegRequired = self.oIOXml.GetValueOfNodeAttribute(xQSetNode,'SegmentRequired')
                if sSegRequired == 'Y' or sSegRequired == 'y':
                    self.l2iCompletedSegmentations.append(l2iSegmentRequired)
                    self.sSegmentationRequiredState = 'Specific' # override default
                else:
                    self.l2iCompletedSegmentations.append(l2iSegmentNotRequired)
                    

