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
    
    def __init__(self, parent=None):
        self.sClassName = 'undefinedClassName'
        self.sFnName = 'undefinedFunctionName'
        self.parent = parent
        
        self._xTree = None
        self._xRootNode = None
        
        self.sTimestampFormat = "%Y%m%d_%H:%M:%S.%f"
        self.lValidSliceWidgets = ['Red', 'Green', 'Yellow', 'Slice4'] # Slice4 for two over two layout
        self.lValidLayouts = ['TwoOverTwo', 'OneUpRedSlice', 'SideBySideRedYellow', 'FourUp']
        self.lValidLayers = ['Foreground', 'Background', 'Segmentation', 'Label']
        self.lValidOrientations = ['Axial', 'Sagittal', 'Coronal']
        self.lValidImageTypes = ['Volume', 'VolumeSequence', 'LabelMap', 'Segmentation', 'RTStruct']
        self.lValidRoiVisibilityCodes = ['All', 'None', 'Select', 'Ignore']

        self.setupTestEnvironment()
    
    #----------
    def setupTestEnvironment(self):
        # check if function is being called from unittesting
        if "testing" in os.environ:
            self.sTestMode = os.environ.get("testing")
        else:
            self.sTestMode = "0"

    #----------
    def GetXmlTree(self):
        return self._xTree
    
    #----------
    def GetRootNode(self):
        return self._xRootNode
    
    #----------
    def SetRootNode(self, xNodeInput):
        self._xRootNode = xNodeInput
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def OpenXml(self, sXmlPath, sRootNodeName):
        """
        given a path, open the xml document
        """
        
        # initialize a document node
        xNode = None
        # test for existence
        if (os.path.isfile(sXmlPath)):
             
            try:
#                 print(sXmlPath)
                self._xTree = etree.parse(sXmlPath)
                self._xRootNode = self._xTree.getroot()

                # check if root node name matches expected name
                if self._xRootNode.tag == sRootNodeName:
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
         

        return bSuccess, self._xRootNode

    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetElementNodeName(self, xNode):
        """
        get the name of the xml node
        """

        try:
            sNodeName = xNode.tag
        except:
            raise TypeError('Invalid XML node type: should be Element type of node')
        

        return sNodeName
                
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetNumChildrenByName(self, xParentNode, sChildTagName):
        """
        given an xml node, return the number of children with the specified tagname
        """

        iNumChildren = len(xParentNode.findall(sChildTagName))
        return iNumChildren

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetChildren(self, xParentNode, sChildTagName):
        """
        given an xml node, return the child nodes with the specified tagname
        """

        lxChildren = xParentNode.findall(sChildTagName)
        
        return lxChildren

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetNthChild(self, xParentNode, sChildTagName, indElem):
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
    def GetLastChild(self, xParentNode, sChildTagName):
        """
        given an xml node, return the last child node with the specified tagname
        """

        xmlChildNode = None
        
        for elem in xParentNode.findall(sChildTagName):
            xmlChildNode = elem
            # print(elem.tag, elem.attrib, elem.text)

        
        return xmlChildNode
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetLatestChildElement(self, xParentNode, sChildTagName):
        """
        retrieve the latest child with the tag name given, from 
        the parent xml input element
        """
                 
        dtLatestTimestamp = ''    # timestamp of type 'datetime'
        xLatestChildElement = None
 
        lxAllChildren = self.GetChildren(xParentNode, sChildTagName)
        for xChild in lxAllChildren:
            sResponseTime = self.GetValueOfNodeAttribute(xChild, 'ResponseTime')
            dtResponseTimestamp = datetime.strptime(sResponseTime, self.sTimestampFormat)
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
    def GetListOfNodeAttributes(self, xNode):
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
    def GetValueOfNodeAttribute(self, xNode, sAttributeName):
        # given a node and an attribute name, get the value
        #   if the attribute did not exist, return null string
        
        try:
            dictAttribs = xNode.attrib
            sAttributeValue = dictAttribs[sAttributeName]
        except:
            sAttributeValue = ''
            
        
        return sAttributeValue

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetDataInNode(self, xNode):
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
    def GetDataFromLastChild(self, xParentNode, sChildTagName):
        
        sData = ''
        
        xChildNode = self.GetLastChild(xParentNode, sChildTagName)
        if xChildNode != None:
            sData = self.GetDataInNode(xChildNode)
        
        return sData
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CreateParentNode(self, sTagName, dictAttrib):
        
        xNode = etree.Element(sTagName)
        
        for attrib, value in dictAttrib.items():
            xNode.set(attrib, value)
        
        return xNode
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CreateSubNode(self, xParentNode, sTagName, dictAttrib):
        
        xSubNode = etree.SubElement(xParentNode, sTagName)
        
        for attrib, value in dictAttrib.items():
            xSubNode.set(attrib, value)
        
        return xSubNode
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddElement(self, xParentNode, sTagName, sText, dictAttrib):
        
        elem = xParentNode.makeelement(sTagName, dictAttrib)
        elem.text = sText
        xParentNode.append(elem)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def InsertElementBeforeIndex(self, xParentNode, xElement, iInd):
        xParentNode.insert(iInd, xElement)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AppendElement(self, xParentNode, xElement):
        xParentNode.append(xElement)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def RemoveAllElements(self, xParentNode, sTagName):
        ''' from the parent node, remove all children with the input tag name
        '''
        for xElem in xParentNode.findall(sTagName):
            xParentNode.remove(xElem)
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def UpdateAttributesInElement(self, xElement, dictAttrib):
        
        # for each key, value in the dictionary, update the element attributes
        for sKey, sValue in dictAttrib.items():
            xElement.attrib[sKey] = sValue
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetAttributes(self, xParentNode):
        
        dictAttrib = {}
        if not xParentNode == None:
            dictAttrib = xParentNode.attrib
            
        return dictAttrib

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CheckForRequiredFunctionalityInAttribute(self, sTreeLevel, sAttribute, sSetting):
        
        # query the Question Set elements in the selected quiz xml
        # functionality is defined at the Question Set level
        # if any question set has the specified attribute setting, return true
        
        bRequired = False 
        
        tree = self.GetXmlTree()
        for node in tree.findall(sTreeLevel):
            sAns = self.GetValueOfNodeAttribute(node, sAttribute)
            if sAns == sSetting:
                bRequired = True
                break
        
        return bRequired
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetIndexOfNextChildWithAttributeValue(self, xParentNode, sChildTagName, indFrom, sAttrib, sAttribValue):
        ''' given an index to search from, search the attributes in the child that matches the input
            attribute value
        '''
        
        iNextInd = -1
        
        iSearchIndex = 0
        for elem in xParentNode.findall(sChildTagName):
            if iSearchIndex >= indFrom:
                sSearchValue = self.GetValueOfNodeAttribute(elem, sAttrib)
                if sSearchValue == sAttribValue:
                    iNextInd = iSearchIndex
                    break
                else:
                    iSearchIndex = iSearchIndex + 1
                
            else:
                iSearchIndex = iSearchIndex + 1
                
        return iNextInd
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetXmlPageAndChildFromAttributeHistory(self, iCrrentPageIndex, sChildToSearch, sImageAttributeToMatch, sAttributeValue):
        ''' Function will return the historical elements (page and child)  that contains the attribute requested for the search.
            This attribute is associated with a child of the 'Page' element.
            The search goes through the pages in reverse. 
                For each page, the requested children are searched (forward) for the requested attribute.
            When found, the xml child element that contains the attribute is returned as well as the parent Page element.
        '''
        
        xHistoricalChildElement = None
        xHistoricalPageElement = None
        
        # start searching pages in reverse order - to get most recent setting
        # first match will end the search
        bHistoricalElementFound = False
        for iPageIndex in range(iCrrentPageIndex-1, -1, -1):
            xPageNode = self.GetNthChild(self.GetRootNode(), 'Page', iPageIndex)
        
            if bHistoricalElementFound == False:
                
                if xPageNode != None:
                    #get all requested children
                    lxChildElementsToSearch = self.GetChildren(xPageNode, sChildToSearch)
                    if len(lxChildElementsToSearch) > 0:
        
                        for xImageNode in lxChildElementsToSearch:
                            
                            # get image attribute
                            sPotentialAttributeValue = self.GetValueOfNodeAttribute(xImageNode, sImageAttributeToMatch)
                            if sPotentialAttributeValue == sAttributeValue:
                                xHistoricalChildElement = xImageNode
                                bHistoricalElementFound = True
                                xHistoricalPageElement = xPageNode
                                break
            else:
                break
        
        return xHistoricalChildElement, xHistoricalPageElement
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetMatchingXmlPagesFromAttributeHistory(self, iCurrentPageIndex, dictPageAttrib, reIgnoreSubstring=''):
        ''' Function to get a list of previous page elements that match the list of attributes 
            ignoring the substring defined as a regular expression (which can be null).
        '''
        
        lxHistoricalPages = []
        bAttribMatch = True
        
        for iPageIndex in range( iCurrentPageIndex -1, -1, -1):
            xPageNode = self.GetNthChild(self.GetRootNode(), 'Page', iPageIndex)
            
            bAttribMatch = True # initialize for next page

            # get values of attributes to get a match
            for attrib, sValueToMatch in dictPageAttrib.items():
                if bAttribMatch: # stop if any of the attributes don't match
                    
                    sStoredPageValue = self.GetValueOfNodeAttribute(xPageNode, attrib)
                    
                    # remove ignore string
                    sPotentialPageValue = re.sub(reIgnoreSubstring,'',sStoredPageValue)

                    if sPotentialPageValue == sValueToMatch:
                        bAttribMatch = True
                    else:
                        bAttribMatch = False

            if bAttribMatch:
                lxHistoricalPages.append(xPageNode)
        
        
        
        return lxHistoricalPages
        
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CopyElement(self, xElemToCopy):
        ''' Create a copy of the element that is not shared by reference to the original
        '''
        sElemToCopy = etree.tostring(xElemToCopy)
        xNewCopiedElem = etree.fromstring(sElemToCopy)
        
        return xNewCopiedElem
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def prettify(self, elem):
        
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
    def SaveXml(self, sXmlPath):

        # by using minidom to reparse the root, we can get a 'pretty' - more user friendly 
        #    xml document output with indents and newlines using writexml
        
        try:

            reparsedRoot = self.prettify(self._xRootNode)
 
            with open(sXmlPath, 'w') as xml_outfile:
                reparsedRoot.writexml(xml_outfile, encoding="utf-8", indent="\t", addindent="\t", newl="\n")
                xml_outfile.flush()
           
        except:
            raise Exception('Write XML file error: %s' % sXmlPath)



    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ZipXml(self, sQuizName, sQuizFolderPath):
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
