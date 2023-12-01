import os, sys
import vtk, qt, ctk, slicer
import traceback

from Utilities.UtilsIOXml import *
from Utilities.UtilsMsgs import *
from Utilities.UtilsFilesIO import *



##########################################################################
#
#   class UtilsValidate
#
##########################################################################

class UtilsValidate:
    """ Class UtilsValidate
        - to read the XML quiz file prior to launching the session
          capturing possible quiz setup pitfalls
    """

    
    def __init__(self, oFilesIO, parent=None):
        self.parent = parent


        self.oUtilsMsgs = UtilsMsgs()
        self.oFilesIO = oFilesIO
        self.oIOXml = self.oFilesIO.oIOXml

        self._liPageGroups = []
        self._liUniquePageGroups = []
        
        self.setupTestEnvironment()


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #-------------------------------------------
    #        Unit testing Utility
    #-------------------------------------------

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        
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
    #----------Page Groups
    #----------
    def SetListPageGroupNumbers(self, liNumbers):
        self._liPageGroups = liNumbers
        
    #----------
    def GetListPageGroupNumbers(self):
        return self._liPageGroups
    
    #----------
    def SetListUniquePageGroups(self, liNumbers):
        self._liUniquePageGroups = liNumbers
        
    #----------
    def GetListUniquePageGroups(self):
        return self._liUniquePageGroups
    
    #----------
    def ClearPageGroupLists(self):
        self._liPageGroups = []
        self._liUniquePageGroups = []
    

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #-------------------------------------------
    #        Utility Functions
    #-------------------------------------------

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetUniqueNumbers(self, liNumbers):
        ''' Utility to return the unique numbers from a given list of numbers.
        '''

        liUniqueNumbers = []
        for ind in range(len(liNumbers)):
            iNum = liNumbers[ind]
            if iNum not in liUniqueNumbers:
                liUniqueNumbers.append(iNum)
        
        return liUniqueNumbers
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #-------------------------------------------
    #        Validation Functions
    #-------------------------------------------

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateQuiz(self):
        '''
            a function to check for specific validation requirements for the quiz
        '''
        sMsg = ''
        bSuccess = True
        
        
        try:
            # open requested quiz xml 
            bSuccess, xRootNode = self.oIOXml.OpenXml(self.oFilesIO.GetXmlQuizPath(),'Session')
            self.l4iNavList = self.oIOXml.GetNavigationListBase(xRootNode)

            # >>>>>>>>>>>>>>>
            # check options for ContourVisibility at the Session level
            sContourVisibility = self.oIOXml.GetValueOfNodeAttribute(xRootNode, 'ContourVisibility')
            if not (sContourVisibility == 'Fill' or sContourVisibility == 'Outline' or sContourVisibility == ''):
                sValidationMsg = "\nContourVisibility value must be 'Fill' or 'Outline'. See attribute in Session"
                sMsg = sMsg + sValidationMsg
                
            sEmailResultsTo = self.oIOXml.GetValueOfNodeAttribute(xRootNode, 'EmailResultsTo')
            if sEmailResultsTo != '':
                # ensure that the smtp config file exists
                sSmtpConfigFile = os.path.join(self.oFilesIO.GetConfigDir(), 'smtp_config.txt')
                if not (os.path.exists(sSmtpConfigFile)) :
                    sMsg = sMsg + '\nMissing smtp configuration file for request to email quiz results : ' + sSmtpConfigFile
            
            sROIColorFile = self.oIOXml.GetValueOfNodeAttribute(xRootNode, 'ROIColorFile')
            if sROIColorFile != '':
                sROIColorFilePath = os.path.join(self.oFilesIO.GetXmlQuizDir(), sROIColorFile + '.txt')
                if not (os.path.exists(sROIColorFilePath)) :
                    sMsg = sMsg + '\nMissing ROIColorFile. Check that file exists: ' + sROIColorFilePath
                else:
                    sValidationMsg = self.ValidateROIColorFile(sROIColorFilePath)
                    sMsg = sMsg + sValidationMsg
            
            
            # check matches of LabelMapID with DisplayLabelMapID
            sValidationMsg = self.ValidateDisplayLabelMapID()
            sMsg = sMsg + sValidationMsg
            
            # check matches of BookmarkID with request 'GoToBookmark' attribute
            sValidationMsg = self.ValidateGoToBookmarkRequest()
            sMsg = sMsg + sValidationMsg
            
            # >>>>>>>>>>>>>>>
            lxPageElements = self.oIOXml.GetChildren(xRootNode, 'Page')
            
            iPageNum = 0
            for xPage in lxPageElements:
                lPathAndNodeNames= []
                iPageNum= iPageNum + 1

                sValidationMsg = self.ValidateRequiredAttribute(xPage, 'ID', str(iPageNum))
                sMsg = sMsg + sValidationMsg
                
                sPageID = self.oIOXml.GetValueOfNodeAttribute(xPage, 'ID')
                sPageReference = str(iPageNum) # initialize
                
                # for any page, make sure there is matching Images Volume to Segmentation or Volume to LabelMap for each destination
                sValidationMsg = self.ValidateImageToSegmentationMatch(xPage, sPageReference)
                sMsg = sMsg + sValidationMsg

                sValidationMsg = self.ValidateNoSpecialCharacters(xPage, str(iPageNum))
                sMsg = sMsg + sValidationMsg
                
                # Image element validations
                lxImageElements = self.oIOXml.GetChildren(xPage, 'Image')
                for xImage in lxImageElements:
                    sImageID = self.oIOXml.GetValueOfNodeAttribute(xImage, 'ID')
    
                    # Page ID + Image ID creates the node name for the image that is loaded (in ImageView>ViewNodeBase)
                    sNodeNameID = sPageID + '_' + sImageID
                    sPageReference = str(iPageNum) + ' ' + sNodeNameID

                    # >>>>>>>>>>>>>>> Attributes
                    sValidationMsg = self.ValidateRequiredAttribute(xImage, 'ID', sPageReference)
                    sMsg = sMsg + sValidationMsg
                    
                    sValidationMsg = self.ValidateRequiredAttribute(xImage, 'Type', sPageReference)
                    sMsg = sMsg + sValidationMsg
                    
                    sValidationMsg = self.ValidateAttributeOptions(xImage, 'Type', sPageReference, self.oIOXml.lValidImageTypes)
                    sMsg = sMsg + sValidationMsg
                    
                    sValidationMsg = self.ValidateOpacity(xImage, iPageNum)
                    sMsg = sMsg + sValidationMsg

                    # check merging of label maps have a matching LabelMapID Image and Loop in Page
                    sValidationMsg = self.ValidateMergeLabelMaps(xImage, xPage, iPageNum)
                    sMsg = sMsg + sValidationMsg

                    # >>>>>>>>>>>>>>> Elements
                    sValidationMsg = self.ValidateRequiredElement(xImage, 'Path', sPageReference)
                    sMsg = sMsg + sValidationMsg
                    
                    sValidationMsg = self.ValidateElementOptions(xImage, 'Layer', sPageReference, self.oIOXml.lValidLayers)
                    sMsg = sMsg + sValidationMsg
                    
                    sValidationMsg = self.ValidateElementOptions(xImage, 'DefaultDestination', sPageReference, self.oIOXml.lValidSliceWidgets)
                    sMsg = sMsg + sValidationMsg
                    
                    sImageType = self.oIOXml.GetValueOfNodeAttribute(xImage, 'Type')
                    if not (sImageType == 'Segmentation' or sImageType == 'RTStruct' or sImageType == 'LabelMap'):
                        sValidationMsg = self.ValidateElementOptions(xImage, 'DefaultOrientation', sPageReference, self.oIOXml.lValidOrientations)
                        sMsg = sMsg + sValidationMsg
                        
                    sPanOrigin = self.oIOXml.GetValueOfNodeAttribute(xImage, 'PanOrigin')
                    if sPanOrigin != '':
                        sValidationMsg = self.ValidateListOfNumbers(sPanOrigin, 'Float', 3, 'PanOrigin', sPageReference)
                        sMsg = sMsg + sValidationMsg
                    
                    # >>>>>>>>>>>>>>>
     

                    # For any page, test that a path always has only one associated PageID_ImageID (aka node name)
                    #    (Otherwise, the quizzer will reload the same image with a different node name)
                    lxImagePath = self.oIOXml.GetChildren(xImage, 'Path')
                    if len(lxImagePath) == 1:
                        sImagePath = self.oIOXml.GetDataInNode(lxImagePath[0])
                         
                        # create tuple of path, sNodeName
                        tupPathAndID = (sImagePath, sNodeNameID)
                         
                        # search list of path/nodeNames for existing match
                        bFoundMatchingPath = False
                        ind = 0
                        for lElement in lPathAndNodeNames:
                            ind = ind + 1
                            msg = (str(ind) + ':' )
                            if bFoundMatchingPath == False:
                                # check if path exists in the list elements
                                if sImagePath in lElement:
                                    bFoundMatchingPath = True
                                    # check that sNodeName exists in that list element
                                    if sNodeNameID not in lElement:
                                        sMsg = sMsg + "\nIn any Page Element, the 'PageID_ImageID' attributes when combined with an Image Path, must be distinct." +\
                                                "\nEither there are different paths sharing the same 'PageID_ImageID' on this Page" +\
                                                "\nOR there are identical image paths with different combined 'PageID_ImageID' attributes" +\
                                                "\n   .....Check all paths for Page: " + str(iPageNum) + ' '+ sNodeNameID
                                     
                        if not bFoundMatchingPath:
                            # new path found; add to list
                            lPathAndNodeNames.append(tupPathAndID)
                            
                            
                    # If the image type is an RTStruct or Segmentation, validate the ROIs element
                    sImageType = self.oIOXml.GetValueOfNodeAttribute(xImage, 'Type')
                    if sImageType == 'RTStruct' or sImageType == 'Segmentation':
                        sValidationMsg = self.ValidateRequiredElement(xImage, 'ROIs', sPageReference)
                        sMsg = sMsg + sValidationMsg
                        
                        lxROIs = self.oIOXml.GetChildren(xImage, 'ROIs')
                        if len(lxROIs) >0:
                            sValidationMsg = self.ValidateRequiredAttribute(lxROIs[0], 'ROIVisibilityCode', sPageReference)
                            sMsg = sMsg + sValidationMsg
                            sValidationMsg = self.ValidateAttributeOptions(lxROIs[0], 'ROIVisibilityCode', sPageReference, self.oIOXml.lValidRoiVisibilityCodes)
                            sMsg = sMsg + sValidationMsg
                            
                            # if the visibility code is Select or Ignore, there must be an ROI element(s) with the name(s) present
                            sVisibilityCode = self.oIOXml.GetValueOfNodeAttribute(lxROIs[0], 'ROIVisibilityCode')
                            if sVisibilityCode == 'Select' or sVisibilityCode == 'Ignore':
                                sValidationMsg = self.ValidateRequiredElement(lxROIs[0], 'ROI', sPageReference, True)  # True for multiple elements allowed
                                sMsg = sMsg + sValidationMsg

                    

                # >>>>>>>>>>>>>>>
                # validate attributes 'SegmentRequired' and 'SegmentRequiredOnAnyImage'
                sValidationMsg = self.ValidateSegmentRequiredSettings(xPage, iPageNum)
                sMsg = sMsg + sValidationMsg
                            
                # >>>>>>>>>>>>>>>
                # validate attributes 'SegmentRequired' and 'MinMarkupLinesRequiredOnAnyImage'
                sValidationMsg = self.ValidateMarkupLinesRequiredSettings(xPage, sPageReference)
                sMsg = sMsg + sValidationMsg
                            
                # Slice4 assignments and TwoOverTwo layout
                sValidationMsg = self.ValidateSlice4Layout(xPage, sPageReference)
                sMsg = sMsg + sValidationMsg
                
                # >>>>>>>>>>>>>>>
                # validate scripts exists for button type questions
                sValidationMsg = self.ValidateButtonTypeScripts(xPage, sPageReference)
                sMsg = sMsg + sValidationMsg
                  
            # >>>>>>>>>>>>>>>
            # validate that each page has a PageGroup attribute if the session requires page group randomization
            #    a quiz that has no PageGroup attributes will be assigned the default numbers during the session setup
            sRandomizeRequested = self.oIOXml.GetValueOfNodeAttribute(xRootNode, 'RandomizePageGroups')
            if sRandomizeRequested == "Y":
                sValidationMsg = self.ValidatePageGroupNumbers(xRootNode)
                sMsg = sMsg + sValidationMsg

            # check that the ROI Color file exists if requested
            sROIColorFile = self.oIOXml.GetValueOfNodeAttribute(xRootNode,'ROIColorFile')
            if sROIColorFile.endswith('.txt'):
                sMsg = sMsg + '\nRemove .txt extenstion from ROIColorFile name.'
            if sROIColorFile == '':
                sROIColorFilePath = self.oFilesIO.GetDefaultROIColorFilePath()
            else:
                sROIColorFilePath = self.oFilesIO.GetCustomROIColorTablePath(sROIColorFile)
            if not os.path.isfile(sROIColorFilePath):
                sMsg = sMsg + '\nCustom ROIColorFile does not exist in the directory with the quiz.' + sROIColorFilePath
                
                
            
            # >>>>>>>>>>>>>>>

            # validation errors found
            if sMsg != '':
                raise
        
        except ValueError:
            if self.sTestMode == "0":
                raise   # rethrow for live run
            else:
                raise ('Value Error: %s' % sMsg)
            
        except:
            bSuccess = False
            self.oUtilsMsgs.DisplayWarning('Quiz Validation Errors \n' + sMsg)
            # after warning, reset the message for calling function to display error and exit
            tb = traceback.format_exc()
            self.oUtilsMsgs.DisplayWarning('Quiz Validation Errors \n' + sMsg)
            # after warning, reset the message for calling function to display error and exit
            sMsg = 'See Administrator: ERROR in quiz XML validation. --Exiting--'\
                   + "\n\n" + tb 
            
            
        return bSuccess, sMsg
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateRequiredElement(self, xParentElement, sElementName, sPageReference, bMultipleAllowed=False):
        '''
            This function checks that there is exactly one child element for the input parent element if the flag for
            multiples has not been set to true.
        '''
        sMsg = ''
        sMsgPrefix = '\nError for ' + sElementName + ' Element. '
        sMsgMissing = 'Required element is missing.'
        sMsgMultipleNotAllowed = 'More than one of this element was found. Only one is allowed.'
        sMsgEnding = '  See Page:' + sPageReference
        
        lxChildren = self.oIOXml.GetChildren(xParentElement, sElementName)
        if len(lxChildren) == 0:
            sMsg = sMsgPrefix +  sMsgMissing + sMsgEnding
        elif len(lxChildren) >1 and bMultipleAllowed == False:
            sMsg = sMsgPrefix + sMsgMultipleNotAllowed + sMsgEnding
                     
        return sMsg
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateElementOptions(self, xParentElement, sElementName, sPageReference, lValidOptions):
        '''
            This function checks that the data stored in the xml element exists in the list of valid options.
        '''
        sMsg = ''
        sValidOptions = ''
        for sOption in lValidOptions:
            sValidOptions = sValidOptions + ', ' + sOption
        
        lxChildren = self.oIOXml.GetChildren(xParentElement, sElementName)

        for xChild in lxChildren:
            sDataValue = self.oIOXml.GetDataInNode(xChild)
            if sDataValue not in lValidOptions:
                sMsg = sMsg + '\nNot a valid option for ' + sElementName + ' : ' + sDataValue + '   See Page:' + sPageReference\
                        + '\n   .....Valid options are:' + sValidOptions

        if len(lxChildren) == 0:
            sMsg = sMsg + '\nMissing Element: ' + sElementName + '   See Page:' + sPageReference\
                        + '\n   .....Valid options are:' + sValidOptions
            

        return sMsg
                        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateRequiredAttribute(self, xParentElement, sAttributeName, sPageReference):
        sMsg = ''
        sDataValue = ''
        sDataValue = self.oIOXml.GetValueOfNodeAttribute(xParentElement, sAttributeName)
        if sDataValue == '':
            sMsg = sMsg + '\nError for ' + sAttributeName + ' Attribute.   See Page:' + sPageReference\
                     + '\n   .....The required attribute is missing.'
        
        return sMsg

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateAttributeOptions(self, xParentElement, sAttributeName, sPageReference, lValidOptions):
        ''' Given the list of valid options, the function checks that the
            data stored in the element exists in that list.
        '''
        
        sMsg = ''
        
        sDataValue = self.oIOXml.GetValueOfNodeAttribute(xParentElement, sAttributeName)

        # check for valid option if it exists
        if sDataValue != '':
            if sDataValue not in lValidOptions:
                sValidOptions = ''
                for sOption in lValidOptions:
                    sValidOptions = sValidOptions + ', ' + sOption
                sMsg = sMsg + '\nNot a valid option for ' + sAttributeName + ' : ' + sDataValue + '   See Page:' + sPageReference\
                        + '\n   .....Valid options are:' + sValidOptions
            
        return sMsg

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateDatabaseLocation(self):
        ''' collect all file paths and ensure the file exists in the given database location
        '''
        
        # open requested quiz xml 
        bSuccess, xRootNode = self.oIOXml.OpenXml(self.oFilesIO.GetXmlQuizPath(),'Session')
        
        if bSuccess:
            
            lsUniqueImagePaths = []
            sMissingFiles = ''
            sMissingFilesPrefix = 'Do you indicate the wrong Database directory? Check file path. \n\n'
            
            lxPageNodes = self.oIOXml.GetChildren(xRootNode,'Page')
            iPageNum = 0
            for xPageNode in lxPageNodes:
                iPageNum = iPageNum + 1
                
                lxImageNodes = self.oIOXml.GetChildren(xPageNode, 'Image')
                for xImageNode in lxImageNodes:
                    
                    lxPathNodes = self.oIOXml.GetChildren(xImageNode, 'Path')
                    for xPathNode in lxPathNodes:
                        sPath = self.oIOXml.GetDataInNode(xPathNode)
                        
                        if sPath in lsUniqueImagePaths:
                            pass
                        else:
                            lsUniqueImagePaths.append(sPath)
                            sFullPath = os.path.join(self.oFilesIO.GetDataParentDir(), sPath)
                            if not os.path.exists(sFullPath):
                                if sMissingFiles == '':
                                    sMissingFiles = sMissingFiles + sMissingFilesPrefix
                                sMissingFiles = sMissingFiles + 'Missing File... Page: ' + str(iPageNum) + '  File: ' + sFullPath + '\n'
                    

        return sMissingFiles
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidatePageGroupNumbers(self, xRootNode):
        ''' If the Session requires randomization of page groups, each page must have a PageGroup attribute
            If all page group numbers are equal, no randomization will be done.
            The page group values must be integer values.
            PageGroup = 0 is allowed. These will always appear at the beginning of the composite list of indices
        '''
        sMsg = ''
        sValidationMsg = ''
        self.ClearPageGroupLists()
        
        # check that each page has a page group number and that it is an integer
        lxPages = self.oIOXml.GetChildren(xRootNode,'Page')
        iPageNum = 0
        for xPage in lxPages:
            iPageNum = iPageNum + 1
            
            # required attribute for randomization
            sValidationMsg = self.ValidateRequiredAttribute(xPage, 'PageGroup', str(iPageNum))
            if sValidationMsg != '':
                sMsg = sMsg + sValidationMsg
                if self.sTestMode == "1":
                    raise Exception('Missing PageGroup attribute: %s' %sValidationMsg)
            
            try:
                # test that the value is an integer
                iPageGroup = int(self.oIOXml.GetValueOfNodeAttribute(xPage, 'PageGroup'))
                # if iPageGroup == 0:
                #     sValidationMsg = 'Page Group must be an integer > 0. See Page: ' + str(iPageNum)
                #     sMsg = sMsg + sValidationMsg
                
            except ValueError:
                sValidationMsg = '\nPage Group is not an integer. See Page: ' + str(iPageNum)
                sMsg = sMsg + sValidationMsg
                if self.sTestMode == "1":
                    raise ValueError('Invalid PageGroup value: %s' % sValidationMsg)
            
            if sMsg == '':
                self._liPageGroups.append(iPageGroup)

        # check that number of different page group numbers (that are >0) must be >1
        # you can't randomize if all the pages are assigned to the same group
        self.SetListUniquePageGroups(self.GetUniqueNumbers(self._liPageGroups))
        
        liValidationPageGroups=[]
        liValidationPageGroups = self._liUniquePageGroups[:]   # use a working copy of the list of unique page groups
        if 0 in liValidationPageGroups:
            liValidationPageGroups.remove(0) # ignore page groups set to 0
        if len(liValidationPageGroups) <= 1: # <= in case of an empty list
            sValidationMsg = '\nNot enough unique PageGroups for requested randomization. \nYou must have more than one page group (other than 0)'
            sMsg = sMsg + sValidationMsg
            if self.sTestMode == "1":
                raise Exception('Validating PageGroups Error: %s' % sValidationMsg)
            
        return sMsg

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateOpacity(self,xImage, iPageNum):
        sMsg = ''
        sErrorMsg = '\nOpacity must be a number between 0.0 and 1.0.   See Page: '
        
        sOpacity = self.oIOXml.GetValueOfNodeAttribute(xImage, 'Opacity')   # not required
        if sOpacity != '':
            try:
                fOpacity = float(sOpacity)
                if fOpacity < 0 or fOpacity > 1.0:
                    sMsg = sErrorMsg + str(iPageNum)
                    if self.sTestMode == "1":
                        raise
            except ValueError:  # to catch : not a number
                sMsg = sErrorMsg + str(iPageNum)
                if self.sTestMode == "1":
                    raise ValueError('Invalid Opacity value: %s' % sMsg)
            except:
                sMsg = sErrorMsg + str(iPageNum)
                if self.sTestMode == "1":
                    raise Exception('Invalid Opacity value: %s' % sMsg)
        
        return sMsg
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateSegmentRequiredSettings(self, xPageNode, iPageReference):
        
       
        sMsg = ''
        sErrorMsgEnableEditor = "\nPage must have 'EnableSegmentEditor' attribute set to 'Y' when a segment required attribute is set. See Page: "
        sErrorMsgSegmentOnAnyImage = "\nContradicting attributes. You cannot have both 'SegmentRequired' on an image and 'SegmentRequiredOnAnyImage' on a page. See Page: "
        sErrorMsgMismatchSegmentRequired = "\nAll image elements with the same path (but different destinations) must have the same attribute 'SegmentRequired' setting. See Page: "
        sErrorMsgSegmentRequiredOnWrongLayer = "\n'SegmentRequired' attribute cannot be on an image assigned to Layer='Segmentation' or 'Label' See Page: "
        
        sEnableSegmentEditorSetting = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'EnableSegmentEditor')
        sSegmentOnAnyImageSetting = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'SegmentRequiredOnAnyImage')
        
        lxImageNodes = self.oIOXml.GetChildren(xPageNode, 'Image')
        
        bFoundSegmentRequiredForImage = False
        l2tupImageSettings = []
        
        for idx in range(len(lxImageNodes)):
            xImageNode = lxImageNodes[idx]

            # collect settings for image
            sSegmentRequiredSetting = self.oIOXml.GetValueOfNodeAttribute(xImageNode, 'SegmentRequired')
            if sSegmentRequiredSetting == '':
                sSegmentRequiredSetting = 'N'
            sImageLayerNode = self.oIOXml.GetLastChild(xImageNode, 'Layer')
            sImageLayer = self.oIOXml.GetDataInNode(sImageLayerNode)
            sImagePathNode = self.oIOXml.GetLastChild(xImageNode,'Path')
            sImagePath = self.oIOXml.GetDataInNode(sImagePathNode)
            tupImageSettings = [sImagePath, sSegmentRequiredSetting]
            l2tupImageSettings.append(tupImageSettings)
            
            if sSegmentRequiredSetting == 'Y':
                bFoundSegmentRequiredForImage = True
                if (sImageLayer=="Segmentation" or sImageLayer=="Label"):
                    sMsg = sMsg + sErrorMsgSegmentRequiredOnWrongLayer + str(iPageReference)

                
        if sSegmentOnAnyImageSetting == "Y" or bFoundSegmentRequiredForImage == True :
            if sEnableSegmentEditorSetting != "Y":
                sMsg = sMsg + sErrorMsgEnableEditor + str(iPageReference)
                
        # if a segment required attribute was found for an image, ensure:
        #    - that it is not on an image set to Layer="Segmentation" or "Label"
        #    - that all images with that same path have the same attribute setting
        
        if sSegmentOnAnyImageSetting == "Y" and bFoundSegmentRequiredForImage == True:
            sMsg = sMsg + sErrorMsgSegmentOnAnyImage + str(iPageReference)
                

        if bFoundSegmentRequiredForImage:
            bMismatch = False
            for idxOuterLoop in range(len(l2tupImageSettings)):
                if bMismatch == True:
                    break
                sPathToCompare = l2tupImageSettings[idxOuterLoop][0]
                sSettingToCompare = l2tupImageSettings[idxOuterLoop][1]
                
                for idxInnerLoop in range(len(l2tupImageSettings)):
                    sPath = l2tupImageSettings[idxInnerLoop][0]
                    sSetting = l2tupImageSettings[idxInnerLoop][1]
                    if sPathToCompare == sPath:
                        if sSettingToCompare != sSetting:
                            sMsg = sMsg + sErrorMsgMismatchSegmentRequired + str(iPageReference)
                            bMismatch = True
                            break
        
        return sMsg
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateMarkupLinesRequiredSettings(self, xPageNode, iPageReference):
        
        sMsg = ''
        sErrorMsgMarkupLinesOnAnyImage = "\nContradicting attributes. You cannot have both 'MinMarkupLinesRequired' on an image and 'MinMarkupLinesRequiredOnAnyImage' on a page. See Page: "
        sErrorMsgMismatchMarkupLinesRequired = "\nAll image elements with the same path (but different destinations) must have the same attribute 'MinMarkupLinesRequired' setting. See Page: "
        sErrorMsgMarkupLinesRequiredOnWrongLayer = "\n'MinMarkupLinesRequired' attribute cannot be on an image assigned to Layer='Segmentation' or 'Label' See Page: "
        
        bFoundMarkupLinesRequiredForImage = False
        l2tupImageSettings = []

        sMarkupLinesOnAnyImageSetting = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'MinMarkupLinesRequiredOnAnyImage')
        lxImageNodes = self.oIOXml.GetChildren(xPageNode, 'Image')
        

        for idx in range(len(lxImageNodes)):
            xImageNode = lxImageNodes[idx]

            # collect settings for image
            sMarkupLinesRequiredSetting = self.oIOXml.GetValueOfNodeAttribute(xImageNode, 'MinMarkupLinesRequired')
            if sMarkupLinesRequiredSetting == '':
                iNumRequiredLines = 0
            else:
                iNumRequiredLines = int(sMarkupLinesRequiredSetting)
                
                
            sImageLayerNode = self.oIOXml.GetLastChild(xImageNode, 'Layer')
            sImageLayer = self.oIOXml.GetDataInNode(sImageLayerNode)
            sImagePathNode = self.oIOXml.GetLastChild(xImageNode,'Path')
            sImagePath = self.oIOXml.GetDataInNode(sImagePathNode)
            tupImageSettings = [sImagePath, sMarkupLinesRequiredSetting]
            l2tupImageSettings.append(tupImageSettings)


            if iNumRequiredLines > 0:
                bFoundMarkupLinesRequiredForImage = True
                if (sImageLayer=="Segmentation" or sImageLayer=="Label"):
                    sMsg = sMsg + sErrorMsgMarkupLinesRequiredOnWrongLayer + str(iPageReference)

        # if a markup line required attribute was found for an image, ensure:
        #    - that it is not on an image set to Layer="Segmentation" or "Label"
        #    - that all images with that same path have the same attribute setting
        
        if sMarkupLinesOnAnyImageSetting != '' and bFoundMarkupLinesRequiredForImage:
                sMsg = sMsg + sErrorMsgMarkupLinesOnAnyImage + str(iPageReference)
            
        if bFoundMarkupLinesRequiredForImage:
            bMismatch = False
            for idxOuterLoop in range(len(l2tupImageSettings)):
                if bMismatch == True:
                    break
                sPathToCompare = l2tupImageSettings[idxOuterLoop][0]
                sSettingToCompare = l2tupImageSettings[idxOuterLoop][1]
                
                for idxInnerLoop in range(len(l2tupImageSettings)):
                    sPath = l2tupImageSettings[idxInnerLoop][0]
                    sSetting = l2tupImageSettings[idxInnerLoop][1]
                    if sPathToCompare == sPath:
                        if sSettingToCompare != sSetting:
                            sMsg = sMsg + sErrorMsgMismatchMarkupLinesRequired + str(iPageReference)
                            bMismatch = True
                            break
        
        return sMsg
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateSlice4Layout(self, xPageNode, iPageReference):
        ''' For all image elements, check if it is assigned to Slice4, 
            that the Page has the attribute 'Layout="TwoOverTwo" '
        '''
        sMsg = ''
        sLayoutSetting = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'Layout')
        
        lxImageNodes = self.oIOXml.GetChildren(xPageNode, 'Image')

        for idx in range(len(lxImageNodes)):
            xImageNode = lxImageNodes[idx]
            xDestination = self.oIOXml.GetNthChild(xImageNode, 'DefaultDestination',0)
            sDestination = self.oIOXml.GetDataInNode(xDestination)
            
            if sDestination == 'Slice4' and sLayoutSetting != 'TwoOverTwo':
                sMsg = sMsg + "\nAssigning an image to Slice4 requires the Page Layout attribute to be set to 'TwoOverTwo'."\
                        + "\nSee Page:" + str(iPageReference)
        
        return sMsg
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateGoToBookmarkRequest(self):
        ''' For all instances of 'GoToBookmark', ensure that there is a corresponding
            BookmarkID. This can help trap spelling mistakes. 
            (This is not checked
            for a 'previous instance' of BookmarkID if RandomizePageGroups attribute
            is set to 'Y'.)
        '''
        sMsg = ''
        ltupGoToBookmarks = []
        ltupBookmarkIDs = []
        sRandomizeSetting = self.oIOXml.GetValueOfNodeAttribute(self.oIOXml.GetRootNode(), 'RandomizePageGroups')
        if sRandomizeSetting == 'Y':
            bRandomizing = True
        else:
            bRandomizing = False
        
        lxPageNodes = self.oIOXml.GetChildren(self.oIOXml.GetRootNode(), 'Page')
        
        # collect all instances of BookmarkID and GoToBookmark and which page they are set
        for idxPage in range(len(lxPageNodes)):
            xPageNode = lxPageNodes[idxPage]
        
            sBookmarkID = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'BookmarkID')
            sGoToBookmark = ''
            sGoToBookmarkRequest = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'GoToBookmark')
            if sGoToBookmarkRequest != '':
                sGoToBookmark = sGoToBookmarkRequest.split()[0]

            sPageGroup = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'PageGroup')
            if sPageGroup != '':
                iPageGroup = int(sPageGroup)
            else:
                iPageGroup = 0


            if sBookmarkID != '':
                ltupBookmarkIDs.append([sBookmarkID, idxPage, iPageGroup])
            if sGoToBookmark != '':
                ltupGoToBookmarks.append([sGoToBookmark, idxPage, iPageGroup])
                
            
        # for every instance of GoToBookmark, confirm there is a BookmarkID
         
        for idxGoToBookmark in range(len(ltupGoToBookmarks)):
            tupGoToBookmarkItem = ltupGoToBookmarks[idxGoToBookmark]
            sGoToBookmarkToSearch = tupGoToBookmarkItem[0]
            iGoToBookmarkPage = tupGoToBookmarkItem[1]
            iGoToBookmarkPageGroup = tupGoToBookmarkItem[2]

            bFoundMatch = False
        
            for idxBookmarkID in range(len(ltupBookmarkIDs)):
                
                if not bFoundMatch:
                    tupBookmarkIDItem = ltupBookmarkIDs[idxBookmarkID]
                    sBookmarkIDToCompare = tupBookmarkIDItem[0]
                    iBookmarkIDPage = tupBookmarkIDItem[1]
                    iBookmarkIDPageGroup = tupBookmarkIDItem[2]
        
                    if sBookmarkIDToCompare == sGoToBookmarkToSearch:
                        if not bRandomizing:
                            if (iBookmarkIDPage < iGoToBookmarkPage):
                                bFoundMatch = True
                                break
                        else:   # randomize is set , ignore page test
                            if iBookmarkIDPageGroup == iGoToBookmarkPageGroup:
                                if iBookmarkIDPage < iGoToBookmarkPage:
                                    bFoundMatch = True
                                    break
                            else: # page groups don't match - only allow if ID is in group 0
                                if iBookmarkIDPageGroup == 0:
                                    bFoundMatch = True
                                    break
       
        
            if not bFoundMatch:
                sMsg = sMsg + "\nFor attribute 'GoToBookmark' : "  + sGoToBookmarkToSearch \
                            + "\nMissing historical 'BookmarkID' setting to match 'GoToBookmark' "\
                            + "\n...OR... The attribute 'PageGroup' for both attributes 'GoToBookmark' and 'BookmarkID' do not match"\
                            + '\nSee Page #: '\
                            + str(iGoToBookmarkPage + 1)
                            
                if self.sTestMode == "1":
                    raise ValueError('Missing historical BookmarkID: %s' % sMsg)
                
        
        return sMsg
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateDisplayLabelMapID(self):
        ''' For all instances of DisplayLabelMapID, ensure that there is a corresponding
            LabelMapID. This can help trap spelling mistakes. 
            If Randomizing is set to "Y", an extra check is done to make sure the two pages with 
            these attributes have the same PageGroup number.
        '''
        
# For future update - to isolate the actual problem
#         sErrorInvalidPageGroup = "\nRandomizing is set to Y. PageGroup attribute on pages with LabelMapID and DisplayLabelMapID must match : "
#         sErrorInvalidImagePath = "\nThe historical image Path for LabelMapID does not match the image Path where DisplayLabelMapID is requested : "
#         sErrorInvalidOrder = "\nThe attribute for LabelMapID must appear on a page before that of the page with the attribute DisplayLableMapID : "
        
        
        sMsg = ''
        ltupDisplayLabelMapIDs = []
        ltupLabelMapIDs = []
        sRandomizeSetting = self.oIOXml.GetValueOfNodeAttribute(self.oIOXml.GetRootNode(), 'RandomizePageGroups')
        if sRandomizeSetting == 'Y':
            bRandomizing = True
        else:
            bRandomizing = False
        
        lxPageNodes = self.oIOXml.GetChildren(self.oIOXml.GetRootNode(), 'Page')
        
        # collect all instances of LabelMapID and DisplayLabelMapID and which page they are set
        for idxPage in range(len(lxPageNodes)):
            xPageNode = lxPageNodes[idxPage]
            lxImageNodes = self.oIOXml.GetChildren(xPageNode, 'Image')
            sPageGroup = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'PageGroup')
            if sPageGroup != '':
                iPageGroup = int(sPageGroup)
            else:
                iPageGroup = 0
    
            for idxImage in range(len(lxImageNodes)):
                xImageNode = lxImageNodes[idxImage]
                sLabelMapID = self.oIOXml.GetValueOfNodeAttribute(xImageNode, 'LabelMapID')
                sDisplayLabelMapID = self.oIOXml.GetValueOfNodeAttribute(xImageNode, 'DisplayLabelMapID')
                xImagePath = self.oIOXml.GetNthChild(xImageNode, 'Path', 0)
                sImagePath = self.oIOXml.GetDataInNode(xImagePath)

                if sLabelMapID != '':
                    ltupLabelMapIDs.append([sLabelMapID, idxPage, sImagePath, iPageGroup])
                if sDisplayLabelMapID != '':
                    ltupDisplayLabelMapIDs.append([sDisplayLabelMapID, idxPage, sImagePath, iPageGroup])
        
        # for every DisplayLabelMapID confirm there is a LabelMapID
        
        for idxDisplayLabelMapID in range(len(ltupDisplayLabelMapIDs)):
            tupDisplayLabelMapIDItem = ltupDisplayLabelMapIDs[idxDisplayLabelMapID]
            sDisplayLabelMapIDToSearch = tupDisplayLabelMapIDItem[0]
            iDisplayLabelMapIDPage = tupDisplayLabelMapIDItem[1]
            sDisplayLabelMapIDPath = tupDisplayLabelMapIDItem[2]
            iDisplayLabelMapPageGroup = tupDisplayLabelMapIDItem[3]

            bFoundMatch = False
            for idxLabelMapID in range(len(ltupLabelMapIDs)):
                
                if not bFoundMatch:
                    tupLabelMapIDItem = ltupLabelMapIDs[idxLabelMapID]
                    sLabelMapIDToCompare = tupLabelMapIDItem[0]
                    iLabelMapIDPage = tupLabelMapIDItem[1]
                    sLabelMapIDPath = tupLabelMapIDItem[2]
                    iLabelMapIDPageGroup = tupLabelMapIDItem[3]
                    


                    if sLabelMapIDToCompare == sDisplayLabelMapIDToSearch:
                        if not bRandomizing:
                            if (sLabelMapIDPath == sDisplayLabelMapIDPath) and\
                                  (iLabelMapIDPage < iDisplayLabelMapIDPage):
                                bFoundMatch = True
                                break
                        else:
                            if sLabelMapIDPath == sDisplayLabelMapIDPath :
                                if iLabelMapIDPageGroup == iDisplayLabelMapPageGroup:
                                    if iLabelMapIDPage < iDisplayLabelMapIDPage:
                                        bFoundMatch = True
                                        break
                                else: # page groups don't match - only allow if ID is in group 0
                                    if iLabelMapIDPageGroup == 0:
                                        bFoundMatch = True
                                        break


    
            if not bFoundMatch:
                sMsg = sMsg + "\n\nFor 'DisplayLabelMapID' : " + sDisplayLabelMapIDToSearch\
                            + "\nMissing historical 'LabelMapID' setting to match."\
                            + "\n...OR... the historical image Path for LabelMapID does not match the image Path where DisplayLabelMapID is requested."\
                            + "\n...OR... if RandomizePageGroups is set to 'Y', the PageGroup numbers do not match for page with attribute 'LabelMapID' and 'DisplayLabelMapID'."\
                            + "\nSeePage #: " + str(iDisplayLabelMapIDPage + 1)
                            
                if self.sTestMode == "1":
                    raise ValueError('Missing historical LabelMapID: %s' % sMsg)
                
    
        return sMsg
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateMergeLabelMaps(self, xImage, xPage, iPageNum):
        ''' For the attribute MergeLabeMaps , this function makes sure of the following conditions:
            - EnableSegmentEditor attribute must be turned off (no contouring on a merge display page)
            - there is also a DisplayLabelMapID attribute on that image
            - an historical xml image exists on a page with Loop=Y and with a matching LabelMapID value
            - the PageGroup number must match
            - (Also, the image path of the historical element must match that of the current image -
               This validation is already done in ValidateDisplayLabelMapID)
        '''
        
        sAttributeName = 'MergeLabelMaps'

        sMsg = ''
        sErrorMsgSegmentingNotAllowed = "\n There can be no segmenting on a Page with the 'MergeLabelMaps' attribute"\
                        +"\nThis includes EnableSegmentEditor, SegmentRequired and SegmentRequiredOnAnyImage."
        sErrorMsgInvalidOption = "\nInvalid option - must be 'Y' or 'N'"
        sErrorMsgMissingDisplayLabelMapIDAttribute = "\nImage with 'MergeLabelMaps' attribute must also have the 'DisplayLabelMapID' attribute."
        sErrorMsgNoMatchingHistoricalLabelMapID = "\nThere was no previous Image with a LabelMapID attribute to match the ID in 'DisplayLabelMapID'."
        sErrorMsgNoLoopOnHistoricalPage = "\nYou requested a label map merge but the previous Image with matching LabelMapID was not on a Page with attribute Loop='Y'. No merge can be done."
        sErrorMsgNoMatchingPageGroups = "\nYou requested a label map merge but the PageGroup numbers of this page do not match with the previous page that has the matching LabelMapID."
        sErrorMsgEmptyPageGroups = "\nYou requested a label map merge but the PageGroup numbers of this page are either empty or don't exist. Page Group numbers must match with the previous page that has the matching LabelMapID to be merged."
        sErrorMsgLoopingNotAllowed = "\nThere can not be Looping on a Page with the 'MergeLabelMaps' attribute"
        
        sMergeLabelMaps = self.oIOXml.GetValueOfNodeAttribute(xImage, sAttributeName)

        if sMergeLabelMaps == "Y":                       
            try:
                
                # capture the DisplayLabelMapID attribute for this image
                sLabelMapIDLink = self.oIOXml.GetValueOfNodeAttribute(xImage, 'DisplayLabelMapID')

                if sLabelMapIDLink == '':
                    # missing attribute
                    raise Exception(sErrorMsgMissingDisplayLabelMapIDAttribute)
                
                
                
                if self.oIOXml.GetValueOfNodeAttribute(xPage, 'EnableSegmentEditor') == 'Y' or\
                    self.oIOXml.GetValueOfNodeAttribute(xPage, 'SegmentRequiredOnAnyImage') == 'Y' or\
                    self.oIOXml.GetValueOfNodeAttribute(xImage, 'SegmentRequired') == 'Y' :
                    raise Exception(sErrorMsgSegmentingNotAllowed)

                # look for historical LabelMapID match
                iPageIndex = iPageNum - 1  # zero indexing for current page
                iNavIdx = self.oIOXml.GetNavigationIndexForPage(self.l4iNavList, iPageIndex)  # zero indexing for current page
                xHistoricalImageElement, xHistoricalPageElement = self.oIOXml.GetXmlPageAndChildFromAttributeHistory(iNavIdx, self.l4iNavList, 'Image','LabelMapID',sLabelMapIDLink)
                if xHistoricalImageElement == None:
                    raise Exception(sErrorMsgNoMatchingHistoricalLabelMapID)
                
                # look for Loop=Y on historical page
                if self.oIOXml.GetValueOfNodeAttribute(xHistoricalPageElement, 'Loop') != "Y":
                    raise Exception(sErrorMsgNoLoopOnHistoricalPage)

                if self.oIOXml.GetValueOfNodeAttribute(xPage, 'Loop') == 'Y':
                    raise Exception(sErrorMsgLoopingNotAllowed)


                # look for matching PageGroup number (these might be empty strings)
                sPageGroupNumToMatch = self.oIOXml.GetValueOfNodeAttribute(xPage, 'PageGroup')
                sHistoricalPageGroupNum = self.oIOXml.GetValueOfNodeAttribute(xHistoricalPageElement, 'PageGroup')
                
                if sPageGroupNumToMatch == sHistoricalPageGroupNum and sPageGroupNumToMatch ==  '':
                    raise Exception(sErrorMsgEmptyPageGroups)
                if sPageGroupNumToMatch != sHistoricalPageGroupNum:
                    raise Exception(sErrorMsgNoMatchingPageGroups)
                
                
            except Exception as error:
                sMsg = str(error) + '\nSee Page #: ' + str(iPageNum) + ' for attribute: ' + sAttributeName + '\n'
         
        else:       
            if (sMergeLabelMaps == '' or sMergeLabelMaps == 'N') == False:
                # not a valid option
                sMsg = sErrorMsgInvalidOption + '\nSee Page #: ' + str(iPageNum) + ' for attribute: ' + sAttributeName + '\n'
                
        
        return sMsg
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateListOfNumbers(self, sString, sType, iLength, sAttributeName, sPageReference):
        # function to validate a string holds a list of values of given type and length
        
        sMsg = ''
        
        lSplitString = sString.split()
        
        # check for required length
        if len(lSplitString) != iLength:
            sMsg = '\nList of numbers does not match required length of ' + str(iLength)\
                     + ' for attribute ' + sAttributeName
        else:
            # check that each entry can be converted to the required type
            try:
                for ind in range(len(lSplitString)):
                    if sType == 'Float':
                        float(lSplitString[ind])
                    elif sType == 'Int':
                        int(lSplitString[ind])
                    else:
                        sMsg = '\nCannot validate this variable type :' + sType
            except:
                sMsg = '\nAttribute ' + sAttributeName + ' does not have valid entries.'\
                        + '\n The required variable type is a list of ' + str(iLength) \
                        +  ' entries of type ' + sType + ' delimited by spaces.'
             
        if sMsg != '':
            sMsg = sMsg + '\n----------See Page: ' + sPageReference

        return sMsg

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateNoSpecialCharacters(self, xPageNode, sPageReference):
        ''' Page ID and Page Descriptor are used to build a results folder name and
            are therefore not allowed certain characters.
        '''
        sMsg = ''
        special_characters = '"\'#&{}\\<>*?/$!:@+`~%^()+=,`|'
        sID = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'ID')
        sDescriptor  = self.oIOXml.GetValueOfNodeAttribute(xPageNode, 'Descriptor')

        if any(c in special_characters for c in sID):
            sMsg = sMsg + '\n Special characters are not allowed in the page attribute ID.'
        if any(c in special_characters for c in sDescriptor):
            sMsg = sMsg + '\n Special characters are not allowed in the page attribute Descriptor'

        if sMsg != '':
            sMsg = sMsg + '\n----------See Page: ' + sPageReference

        
        return sMsg
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateImageToSegmentationMatch(self, xPageNode, sPageReference):
        '''
        '''
        sMsg = ''
        lxAllImages = []
        llDestImageVolume = []
        llDestSegmentation = []
        llDestLabelMap = []
        llDestRTStruct = []
        llDestSegImageType = []
        
        # collect images and their destinations
        lxAllImages = self.oIOXml.GetChildren(xPageNode, 'Image')
        
        for xImage in lxAllImages:
            
            sImageType = self.oIOXml.GetValueOfNodeAttribute(xImage, 'Type')
            xDestination = self.oIOXml.GetNthChild(xImage, 'DefaultDestination', 0)
            sDestination = self.oIOXml.GetDataInNode(xDestination)
            xImagePath = self.oIOXml.GetNthChild(xImage, 'Path', 0)
            sImagePath = self.oIOXml.GetDataInNode(xImagePath)
            
            if sImageType == 'Volume' or sImageType == 'VolumeSequence':
                llDestImageVolume.append([sDestination, sImagePath])
            elif sImageType == 'Segmentation':
                llDestSegmentation.append([sDestination, sImagePath])
            elif sImageType == 'LabelMap':
                llDestLabelMap.append([sDestination, sImagePath])
            elif sImageType == 'RTStruct':
                llDestRTStruct.append([sDestination, sImagePath])
                

            
           
        sSegmentationMsg = self.SyncSegsAndVolumes(llDestImageVolume, 'Segmentation', llDestSegmentation)
        
        sLabelMapMsg = self.SyncSegsAndVolumes(llDestImageVolume, 'LabelMap', llDestLabelMap)
        
        sRTStructMsg = self.SyncSegsAndVolumes(llDestImageVolume, 'RTStruct', llDestRTStruct)

        sMsg = sMsg + sSegmentationMsg + sLabelMapMsg + sRTStructMsg
        if sMsg != '':
            sMsg = sMsg + '\n----------See Page: ' + sPageReference

        return sMsg
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateROIColorFile(self, sFilePath):
        
        # color files cannot use an ID = 0 
        # using ID=0 will cause images to disappear when segment editor is started
        # syntax: id descriptor r g b a
        # lines beginning with '#' are comments
        sMsg = ''
        
        fh = open(sFilePath, "r")
        lLines = fh.readlines()
        
        for sLine in lLines:
            if sLine[:1] == "#":
                pass
            elif sLine[:1] == "0":
                sMsg = "ROI Color File cannot have an entry with ID = '0'" \
                        + "\n See file " + sFilePath
                break
            else:
                pass
            
        return sMsg
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SyncSegsAndVolumes(self, llDestImageVolume, sSegImageType, llDestSegImageType):
        
        sMsg = ''
        bMismatchFound = False
        
        for indSegTypeToMatch in range(len(llDestSegImageType)):
            if not bMismatchFound:
                # there must be an image volume to sync with the  destination of this segmentation type of image
                sSegTypeDestToMatch = llDestSegImageType[indSegTypeToMatch][0]
                sSegTypePathToMatch = llDestSegImageType[indSegTypeToMatch][1]
                lDestMatchedVolImagePaths = []
                
                for indVol in range(len(llDestImageVolume)):
                    if llDestImageVolume[indVol][0] == sSegTypeDestToMatch:
                        lDestMatchedVolImagePaths.append(llDestImageVolume[indVol][1])
                        
                        
                if len(lDestMatchedVolImagePaths) > 0:        
                    # image volumes found at that destination
                    # there may have been more than one image found (FG and BG)
                    # check if they are repeated in another destination
                    lAllDests = []
                    for indMatchedPath in range(len(lDestMatchedVolImagePaths)):
                        sMatchedVolPathToSearch = lDestMatchedVolImagePaths[indMatchedPath]
                        for indMatchedPath in range(len(llDestImageVolume)):
                            if sMatchedVolPathToSearch == llDestImageVolume[indMatchedPath][1]:
                                if llDestImageVolume[indMatchedPath][0] not in lAllDests: # only keep FG or BG
                                    lAllDests.append(llDestImageVolume[indMatchedPath][0])
                    
                        if len(lAllDests) > 0:
                            # the same image volume is repeated in other destinations
                            # there needs to be the same seg type image in those destinations
                            iNumMatches = 0
                            for indDest in range(len(lAllDests)):
                                sDest = lAllDests[indDest]
                                for indSeg in range(len(llDestSegImageType)):
                                    if (sSegTypePathToMatch == llDestSegImageType[indSeg][1]):
                                        if llDestSegImageType[indSeg][0] == sDest:
                                            iNumMatches = iNumMatches + 1
                            
                        if iNumMatches == len(lAllDests):
                            pass
                        else:
                            sMsg = sMsg + '\n\nYou do not have a ' + sSegImageType + ' xml entry for each ' +\
                                    'of the associated image volume entries.' +\
                                    '\n(eg. If Vol1 is on Red and Green; there must be the same ' + sSegImageType + ' entry for each of these destinations' +\
                                    '\n.....Images defined as ' + sSegImageType + ' and Volumes are not in sync.'
                            bMismatchFound = True
                            break
        
                            
                        
                        
                        
                else:
                    sMsg = sMsg + '\n\nYou have a ' + sSegImageType + ' type of image defined in the xml ' +\
                            '\nwith no matching volume in the same default destination.' +\
                            '\n.....Images defined as ' + sSegImageType + ' and Volumes are not in sync.'
                            
                

       
        
        return sMsg
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ValidateButtonTypeScripts(self, xPage, sPageReference):
        ''' Check that each script defined in the options of a Button type of question
            exists in the Inputs/Scripts directory.
        '''
        
        sMsg = ''
        
        lxQuestionSetElements = self.oIOXml.GetChildren(xPage, 'QuestionSet')
        for xQuestionSet in lxQuestionSetElements:
            
            lxQuestionElements = self.oIOXml.GetChildren(xQuestionSet, 'Question')
            for xQuestion in lxQuestionElements:
                
                sQuestionType = self.oIOXml.GetValueOfNodeAttribute(xQuestion, 'Type')
                if sQuestionType == 'Button':
                    
                    lxOptionElements = self.oIOXml.GetChildren(xQuestion, 'Option')
                         
                    for xOption in lxOptionElements:
                        
                        sScriptName = self.oIOXml.GetDataInNode(xOption)
                        sScriptFullPath = os.path.join(self.oFilesIO.GetScriptsDir(),sScriptName)
                        
                        if os.path.exists(sScriptFullPath) == False:
                            sMsg = '\nYou have a Button type of question but the script name defined in the Option does not exist' \
                                    + '\nSee Page: ' + str(sPageReference)\
                                    + ' for Script: ' + sScriptName\
                                    + ' in path: ' + sScriptFullPath
                
        

        return sMsg
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
