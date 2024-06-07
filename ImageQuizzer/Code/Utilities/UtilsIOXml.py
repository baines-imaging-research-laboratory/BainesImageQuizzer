import os, sys
# import warnings
# import vtk, qt, ctk, slicer

import xml.dom.minidom
import shutil
import re

from datetime import datetime



try:
    from lxml import etree

    print("running with lxml.etree")
except ImportError:
    try:
        # Python 2.5
        import xml.etree.cElementTree as etree

        print("running with cElementTree on Python 2.5+")
    except ImportError:
        try:
            # Python 2.5
            import xml.etree.ElementTree as etree

            print("running with ElementTree on Python 2.5+")
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as etree

                print("running with cElementTree")
            except ImportError:
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree

                    print("running with ElementTree")
                except ImportError:
                    print("Failed to import ElementTree from any known place")


##########################################################################
#
#   class UtilsIOXml
#
##########################################################################


class UtilsIOXml:
    """ Class UtilsIOXml
        to handle accessing nodes, children, attributes and data of XML files
    """ 
    
   
    _xTree = None
    _xRootNode = None
    
    sTimestampFormat = "%Y%m%d_%H:%M:%S.%f"
    lValidSliceWidgets = ['Red', 'Green', 'Yellow', 'Slice4'] # Slice4 for two over two layout
    lValidLayouts = ['TwoOverTwo', 'OneUpRedSlice', 'SideBySideRedYellow', 'FourUp']
    lValidLayers = ['Foreground', 'Background', 'Segmentation', 'Label']
    lValidOrientations = ['Axial', 'Sagittal', 'Coronal']
    lValidImageTypes = ['Volume', 'VolumeSequence', 'LabelMap', 'Segmentation', 'RTStruct']
    lValidRoiVisibilityCodes = ['All', 'None', 'Select', 'Ignore']

    
    #----------
    @staticmethod
    def setupTestEnvironment():
        # check if function is being called from unittesting
        if "testing" in os.environ:
            UtilsIOXml.sTestMode = os.environ.get("testing")
        else:
            UtilsIOXml.sTestMode = "0"

    #----------
    @staticmethod
    def GetXmlTree():
        return UtilsIOXml._xTree
    
    #----------
    @staticmethod
    def GetRootNode():
        return UtilsIOXml._xRootNode
    
    #----------
    @staticmethod
    def SetRootNode( xNodeInput):
        UtilsIOXml._xRootNode = xNodeInput
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def OpenXml( sXmlPath, sRootNodeName):
        """
        given a path, open the xml document
        """
        
        # initialize a document node
        xNode = None
        # test for existence
        if (os.path.isfile(sXmlPath)):
             
            try:
#                 print(sXmlPath)
                UtilsIOXml._xTree = etree.parse(sXmlPath)
                UtilsIOXml._xRootNode = UtilsIOXml._xTree.getroot()

                # check if root node name matches expected name
                if UtilsIOXml._xRootNode.tag == sRootNodeName:
                    bSuccess = True
  
                else:
                    bSuccess = False
                    raise NameError('Invalid XML root node: %s' % sXmlPath)
 
                
            except NameError:
                raise
 
            except:
                bSuccess = False
                raise Exception('Parsing XML file error: %s' % sXmlPath)
                 
        else:
            bSuccess = False
            raise Exception('XML file does not exist: %s' % sXmlPath)
         

        return bSuccess

    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def GetElementNodeName( xNode):
        """
        get the name of the xml node
        """

        try:
            sNodeName = xNode.tag
        except:
            raise TypeError('Invalid XML node type: should be Element type of node')
        

        return sNodeName
                
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def GetNumChildrenByName( xParentNode, sChildTagName):
        """
        given an xml node, return the number of children with the specified tagname
        """

        iNumChildren = len(xParentNode.findall(sChildTagName))
        return iNumChildren

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def GetChildren( xParentNode, sChildTagName):
        """
        given an xml node, return the child nodes with the specified tagname
        """

        lxChildren = xParentNode.findall(sChildTagName)
        
        return lxChildren

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def GetNthChild( xParentNode, sChildTagName, indElem):
        """
        given an xml node, return the nth child node with the specified tagname
        """

        xmlChildNode = None

        ind = 0
        for elem in xParentNode.findall(sChildTagName):
            if ( ind == indElem ):
                xmlChildNode = elem
#                 print(elem.tag, elem.attrib, elem.text)

            ind = ind + 1
        
        
        return xmlChildNode

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def GetLastChild( xParentNode, sChildTagName):
        """
        given an xml node, return the last child node with the specified tagname
        """

        xmlChildNode = None
        
        for elem in xParentNode.findall(sChildTagName):
            xmlChildNode = elem
            # print(elem.tag, elem.attrib, elem.text)

        
        return xmlChildNode
        
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
            dtResponseTimestamp = datetime.strptime(sResponseTime, UtilsIOXml.sTimestampFormat)
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
    def GetListOfNodeAttributes( xNode):
        # given a node, return a list of all its attributes
        
        # attributes are stored in dictionary format
        listOfAttributes = []
        lNames = list(xNode.attrib.keys())
        lValues = list(xNode.attrib.values())

        for index in range(len(xNode.attrib)):
            name = lNames[index]
            value = lValues[index]
            tupAttribute = name, value
            listOfAttributes.append(tupAttribute)

            
        return listOfAttributes
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def GetValueOfNodeAttribute( xNode, sAttributeName):
        # given a node and an attribute name, get the value
        #   if the attribute did not exist, return null string
        
        try:
            dictAttribs = xNode.attrib
            sAttributeValue = dictAttribs[sAttributeName]
        except:
            sAttributeValue = ''
            
        
        return sAttributeValue

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def GetDataInNode( xNode):
        # given a node get the value
        #   if the node did not exist, return null string

        try:
            sData = xNode.text
            
            if sData is None:        
                sData = ''
            else:
                if '\n' or '\t' in sData: 
                    # clean up any tabs or line feeds in the data string; replace with null
                    #    Element tree stores '\n\t\t'  when the text property is empty for an element 
                    sTab = '\t'
                    sNull = ''
                    sLineFeed = '\n'
                    sData = sData.replace(sTab, sNull)
                    sData = sData.replace(sLineFeed, sNull)
        except:
            sData = ''
        return sData
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def GetDataFromLastChild( xParentNode, sChildTagName):
        
        sData = ''
        
        xChildNode = UtilsIOXml.GetLastChild(xParentNode, sChildTagName)
        if xChildNode != None:
            sData = UtilsIOXml.GetDataInNode(xChildNode)
        
        return sData
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def CreateParentNode( sTagName, dictAttrib):
        
        xNode = etree.Element(sTagName)
        
        for attrib, value in dictAttrib.items():
            xNode.set(attrib, value)
        
        return xNode
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def CreateSubNode( xParentNode, sTagName, dictAttrib):
        
        xSubNode = etree.SubElement(xParentNode, sTagName)
        
        for attrib, value in dictAttrib.items():
            xSubNode.set(attrib, value)
        
        return xSubNode
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def AddElement( xParentNode, sTagName, sText, dictAttrib):
        
        elem = xParentNode.makeelement(sTagName, dictAttrib)
        elem.text = sText
        xParentNode.append(elem)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def InsertElementBeforeIndex( xParentNode, xElement, iInd):
        xParentNode.insert(iInd, xElement)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def AppendElement( xParentNode, xElement):
        xParentNode.append(xElement)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def RemoveAllElements( xParentNode, sTagName):
        ''' from the parent node, remove all children with the input tag name
        '''
        for xElem in xParentNode.findall(sTagName):
            xParentNode.remove(xElem)
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def GetAttributes( xParentNode):
        
        dictAttrib = {}
        if not xParentNode == None:
            dictAttrib = xParentNode.attrib
            
        return dictAttrib

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def UpdateAttributesInElement( xElement, dictAttrib):
        
        # for each key, value in the dictionary, update the element attributes
        for sKey, sValue in dictAttrib.items():
            xElement.attrib[sKey] = sValue
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def RemoveAttributeInElement( xElement, key ):
        # remove a key/value pair from an element if it exists
        
        dictAttrib = UtilsIOXml.GetAttributes(xElement)
        
        if key in dictAttrib:
            del dictAttrib[key]
            
        # reset element with updated key/value pairs
        UtilsIOXml.UpdateAttributesInElement(xElement, dictAttrib)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def CheckForRequiredFunctionalityInAttribute( sTreeLevel, sAttribute, sSetting):
        
        # query the Question Set elements in the selected quiz xml
        # functionality is defined at the Question Set level
        # if any question set has the specified attribute setting, return true
        
        bRequired = False 
        
        tree = UtilsIOXml.GetXmlTree()
        for node in tree.findall(sTreeLevel):
            sAns = UtilsIOXml.GetValueOfNodeAttribute(node, sAttribute)
            if sAns == sSetting:
                bRequired = True
                break
        
        return bRequired
        
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
    def GetIndexOfNextChildWithAttributeValue( xParentNode, sChildTagName, indFrom, sAttrib, sAttribValue):
        ''' given an index to search from, search the attributes in the child that matches the input
            attribute value
        '''
        
        iNextInd = -1
        
        iSearchIndex = 0
        for elem in xParentNode.findall(sChildTagName):
            if iSearchIndex >= indFrom:
                sSearchValue = UtilsIOXml.GetValueOfNodeAttribute(elem, sAttrib)
                if sSearchValue == sAttribValue:
                    iNextInd = iSearchIndex
                    break
                else:
                    iSearchIndex = iSearchIndex + 1
                
            else:
                iSearchIndex = iSearchIndex + 1
                
        return iNextInd
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def GetFirstXmlNodeWithMatchingAttributes( lxNodesToSearch, dictAttrib):
        ''' Search the list of nodes.
            Return first node and navigation index that match the given  attributes.
        '''
        bAttribMatch = True

        for iNavIdx, xNode in enumerate(lxNodesToSearch):

            bAttribMatch = True # reinitialize for each page
            
            # get values of attributes to get a match
            for attrib, sValueToMatch in dictAttrib.items():
                
                
                if bAttribMatch:    #continue through all attributes 
                    sStoredValue = UtilsIOXml.GetValueOfNodeAttribute(xNode, attrib)
                    
                    if sStoredValue == sValueToMatch:
                        bAttribMatch = True
                    else:
                        bAttribMatch = False
                    
            if bAttribMatch == False:
                iNavIdx = -1
                xNode = None
            else:
                # all attributes matched - exit loop
                break
                
        return iNavIdx, xNode 
        
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
    def CopyElement( xElemToCopy):
        ''' Create a copy of the element that is not shared by reference to the original
        '''
        sElemToCopy = etree.tostring(xElemToCopy)
        xNewCopiedElem = etree.fromstring(sElemToCopy)
        
        return xNewCopiedElem
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def prettify( elem):
        
        """Return a pretty-printed XML string for the Element.

            - returning the reparsed string lets you use 'writexml' function
                with indent options
                
            (NB. 'toprettyxml' works on a DOM document and sets up the
                 reparsed string for the print function. 
                 This function is working only on the string.  )
        """

        rough_string = etree.tostring(elem, 'utf-8')

        # remove existing line feeds and tabs from the string (byte encoding is required)
        byteTab = bytes('\t'.encode())
        byteNull = bytes(''.encode())
        byteLineFeed = bytes('\n'.encode())
        rough_string = rough_string.replace(byteTab, byteNull)
        rough_string = rough_string.replace(byteLineFeed, byteNull)

        # use minidom to parse the string after line feeds and tabs have been removed
        reparsed = xml.dom.minidom.parseString(rough_string)

        return reparsed

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def SaveXml( sXmlPath):

        # by using minidom to reparse the root, we can get a 'pretty' - more user friendly 
        #    xml document output with indents and newlines using writexml
        
        try:

            reparsedRoot = UtilsIOXml.prettify(UtilsIOXml._xRootNode)
 
            with open(sXmlPath, 'w') as xml_outfile:
                reparsedRoot.writexml(xml_outfile, encoding="utf-8", indent="\t", addindent="\t", newl="\n")
                xml_outfile.flush()
           
        except:
            raise Exception('Write XML file error: %s' % sXmlPath)



    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def ZipXml( sQuizName, sQuizFolderPath):
        """ Zip the quiz results in the user's folder.
        """
        
        try:
            sOutputFilename = ''
            sOutputFilename = sQuizName
            shutil.make_archive(sOutputFilename, 'zip', sQuizFolderPath)
            
            return sOutputFilename + '.zip'
            
        except:
            raise Exception('Trouble archiving the quiz results folder.')
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
