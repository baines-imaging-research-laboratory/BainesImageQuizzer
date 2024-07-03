import os, sys

import Utilities.UtilsIOXml as UtilsIOXml

from Utilities.UtilsIOXml import *


##########################################################################
#
#   class UtilsCustomXml
#
##########################################################################


class UtilsCustomXml:
    """ Class UtilsCustomXml
        to handle accessing nodes XML elements based on the custom Image Quizzer element names
    """ 

    sTimestampFormat = "%Y%m%d_%H:%M:%S.%f"
    lValidSliceWidgets = ['Red', 'Green', 'Yellow', 'Slice4'] # Slice4 for two over two layout
    lValidLayouts = ['TwoOverTwo', 'OneUpRedSlice', 'SideBySideRedYellow', 'FourUp']
    lValidLayers = ['Foreground', 'Background', 'Segmentation', 'Label']
    lValidOrientations = ['Axial', 'Sagittal', 'Coronal']
    lValidImageTypes = ['Volume', 'VolumeSequence', 'LabelMap', 'Segmentation', 'RTStruct', 'Vector']
    lValidRoiVisibilityCodes = ['All', 'None', 'Select', 'Ignore']
    lValidVectorImageExtensions = ['PNG','BMP','JPG','JPEG','PDF','DCM']


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def GetLatestChildElement( xParentNode, sChildTagName):
        """
        retrieve the latest child with the tag name given, from 
        the parent xml input element
        """
                 
        dtLatestTimestamp = ''    # timestamp of type 'datetime'
        xLatestChildElement = None
 
        lxAllChildren = UtilsIOXml.GetChildren(xParentNode, sChildTagName)
        for xChild in lxAllChildren:
            sResponseTime = UtilsIOXml.GetValueOfNodeAttribute(xChild, 'ResponseTime')
            dtResponseTimestamp = datetime.strptime(sResponseTime, UtilsCustomXml.sTimestampFormat)
#             print('*** TIME : %s' % sResponseTime)
              
            if dtLatestTimestamp == '':
                dtLatestTimestamp = dtResponseTimestamp
                xLatestChildElement = xChild
            else:
                # compare with >= in order to capture 'last' response 
                #    in case there are responses with the same timestamp
                if dtResponseTimestamp >= dtLatestTimestamp:
                    dtLatestTimestamp = dtResponseTimestamp
                    xLatestChildElement = xChild
 
        return xLatestChildElement

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def GetQuizLayoutForNavigationList( xRootNode):
         
        l4iNavList = []
         
        # get Page nodes
        xPages = UtilsIOXml.GetChildren(xRootNode, 'Page')
 
        iPageNum = 0
        for iPageIndex in range(len(xPages)):
            iPageNum = iPageNum + 1
            # for each page - get number of question sets
            xPageNode = UtilsIOXml.GetNthChild(xRootNode, 'Page', iPageIndex)
            xQuestionSets = UtilsIOXml.GetChildren(xPageNode,'QuestionSet')
 
            sPageGroup = UtilsIOXml.GetValueOfNodeAttribute(xPageNode, 'PageGroup')
            # if there is no request to randomize the page groups, there may not be a page group number
            try:
                iPageGroup = int(sPageGroup)
            except:
                # assign a unique page number if no group number exists
                iPageGroup = iPageNum
                 
            sRepNum = UtilsIOXml.GetValueOfNodeAttribute(xPageNode, 'Rep')
            try:
                iRepNum = int(sRepNum)
            except:
                iRepNum = 0
             
            # if there are no question sets for the page, insert a blank shell
            #    - this allows images to load
            if len(xQuestionSets) == 0:
                UtilsIOXml.AddElement(xPageNode,'QuestionSet', 'Blank Quiz',{})
                xQuestionSets = UtilsIOXml.GetChildren(xPageNode, 'QuestionSet')
             
            # append to composite indices list
            #    - if there are 2 pages and the 1st page has 2 question sets, 2nd page has 1 question set,
            #        and each page is in a different page group
            #        the indices will look like this:
            #        Page    QS    PageGroup  Rep
            #        0        0        1       0
            #        0        1        1       0
            #        1        0        2       0
            #    - there can be numerous questions in each question set
            for iQuestionSetIndex in range(len(xQuestionSets)):
                l4iNavList.append([iPageIndex,iQuestionSetIndex, iPageGroup, iRepNum])
         
         
         
         
        return l4iNavList
     
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def GetNavigationIndexForPage( l4iNavList, iPageIndex):
        ''' Returns first navigation index that matches the Page index given.
            (Question sets are not taken into account.)
        '''
        iNavigationIndex = -1
        for idx in range(len(l4iNavList)):
            if l4iNavList[idx][0] == iPageIndex:
                iNavigationIndex = idx
                break
             
        return iNavigationIndex
     
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def GetXmlPageAndChildFromAttributeHistory( iCurrentNavigationIndex, l4iNavigationIndices, sChildToSearch, sImageAttributeToMatch, sAttributeValue):
        ''' Function will return the historical elements (page and child)  that contains the attribute requested for the search.
            This attribute is associated with a child of the 'Page' element.
            The search goes through the pages in reverse. 
                For each page, the requested children are searched (forward) for the requested attribute.
            When found, the xml child element that contains the attribute is returned as well as the parent Page element.
        '''
        
        xHistoricalChildElement = None
        xHistoricalPageElement = None
        
        # start searching pages in reverse order through the navigation indices - to get most recent setting
        # first match will end the search
        bHistoricalElementFound = False
        for iNavIndex in range( iCurrentNavigationIndex -1, -1, -1):
            iPageIndex = l4iNavigationIndices[iNavIndex][0]

            xPageNode = UtilsIOXml.GetNthChild(UtilsIOXml.GetRootNode(), 'Page', iPageIndex)
        
            if bHistoricalElementFound == False:
                
                if xPageNode != None:
                    #get all requested children
                    lxChildElementsToSearch = UtilsIOXml.GetChildren(xPageNode, sChildToSearch)
                    if len(lxChildElementsToSearch) > 0:
        
                        for xImageNode in lxChildElementsToSearch:
                            
                            # get image attribute
                            sPotentialAttributeValue = UtilsIOXml.GetValueOfNodeAttribute(xImageNode, sImageAttributeToMatch)
                            if sPotentialAttributeValue == sAttributeValue:
                                xHistoricalChildElement = xImageNode
                                bHistoricalElementFound = True
                                xHistoricalPageElement = xPageNode
                                break
            else:
                break
        
        return xHistoricalChildElement, xHistoricalPageElement
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def GetXmlElementFromAttributeHistory( iCurrentNavigationIndex, l4iNavigationIndices, sPageChildrenToSearch, sImageAttributeToMatch, sAttributeValue):
        ''' Function will return the historical element that contains the attribute requested for the search.
            This attribute is associated with a child of the 'Page' element.
            The search goes through the navigation indices in reverse. 
                For each page, the requested children are searched (forward) for the requested attribute.
            When found, the xml element that contains the attribute is returned.
        '''
        
        xHistoricalChildElement = None
        
        # start searching pages in reverse order through the navigation indices - to get most recent setting
        # first match will end the search
        bHistoricalElementFound = False
        for iNavIndex in range( iCurrentNavigationIndex -1, -1, -1):
            iPageIndex = l4iNavigationIndices[iNavIndex][0]
            
            xPageNode = UtilsIOXml.GetNthChild(UtilsIOXml.GetRootNode(), 'Page', iPageIndex)
        
            if bHistoricalElementFound == False:
                
                #get all requested children
                lxChildElementsToSearch = UtilsIOXml.GetChildren(xPageNode, sPageChildrenToSearch)
                if len(lxChildElementsToSearch) > 0:
    
                    for xImageNode in lxChildElementsToSearch:
                        
                        # get image attribute
                        sPotentialAttributeValue = UtilsIOXml.GetValueOfNodeAttribute(xImageNode, sImageAttributeToMatch)
                        if sPotentialAttributeValue == sAttributeValue:
                            xHistoricalChildElement = xImageNode
                            bHistoricalElementFound = True
                            break
            else:
                break
        
        return xHistoricalChildElement
    

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def GetMatchingXmlPagesFromAttributeHistory( iCurrentNavigationIndex, l4iNavigationIndices, dictPageAttrib, reIgnoreSubstring=''):
        ''' Function to get a list of previous page elements and the navigation index that match the list of attributes 
            ignoring the substring defined as a regular expression (which can be null).
            Randomized data is handled by stepping through the navigation indices which reflect the random order.
            (Multiple question sets in the navigation list do not affect the resulting dictionary.
            Only the page node and the page index are stored.)
        '''
        
        dictPgNodeAndPgIndex = {}
        bAttribMatch = True
        
        for iNavIndex in range( iCurrentNavigationIndex -1, -1, -1):
            iPageIndex = l4iNavigationIndices[iNavIndex][0]
            
            xPageNode = UtilsIOXml.GetNthChild(UtilsIOXml.GetRootNode(), 'Page', iPageIndex)
            
            bAttribMatch = True # initialize for next page
            
            # get values of attributes to get a match
            for attrib, sValueToMatch in dictPageAttrib.items():
                    
                if bAttribMatch: # stop if any of the attributes don't match
                    sStoredPageValue = UtilsIOXml.GetValueOfNodeAttribute(xPageNode, attrib)
                    
                    # remove ignore string
                    sPotentialPageValue = re.sub(reIgnoreSubstring,'',sStoredPageValue)
    
                    if sPotentialPageValue == sValueToMatch:
                        bAttribMatch = True
                    else:
                        bAttribMatch = False
                
            if bAttribMatch:        
                dictPgNodeAndPgIndex.update({xPageNode:iPageIndex})
        
        
        
        return dictPgNodeAndPgIndex
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def TagResponse(xQuestionSet, sDescription, sQuizPath):
        ''' Function to add attribute to response element to give a description
            as to what event took place to generate the save of the response
            (eg. a Next or Previous button click; remain on page due to missing requirement etc.
        '''
        
        sMissingDescription   = "Missed contour/line"
        sCancelledDescription = "Canc for contouring"
        
        # shorten event messages
        if 'missing' in sDescription:
            sDescription = sMissingDescription
        elif 'cancelled' in sDescription:
            sDescription = sCancelledDescription
            
        if len(sDescription) < len(sMissingDescription):
            sDescription = sDescription.ljust(len(sMissingDescription)) 
                
        
        lxQuestions = UtilsIOXml.GetChildren(xQuestionSet, 'Question')
        
        for xQuestion in lxQuestions:
            lxOptions = UtilsIOXml.GetChildren(xQuestion, 'Option')
            
            for xOption in lxOptions:
                xLastResponse = UtilsIOXml.GetLastChild(xOption, 'Response')
                dictAttribute = {'Event':sDescription}
                if xLastResponse != None:
                    UtilsIOXml.UpdateAttributesInElement(xLastResponse, dictAttribute )
                
        UtilsIOXml.SaveXml(sQuizPath)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        