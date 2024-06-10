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
