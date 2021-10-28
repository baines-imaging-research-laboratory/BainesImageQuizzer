# from abc import ABC, abstractmethod
import os, sys
import warnings
import vtk, qt, ctk, slicer

import xml.dom.minidom

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
#   class Utilities
#
##########################################################################

class Utilities:
    """ Class Utilities 
        stub set up for importing all classes in the Utilities file
    """
    
    def __init__(self, parent=None):
        self.parent = parent
        
        
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
        
        self.sTimestampFormat = "%Y%m%d_%H:%M:%S"
        self.oUtilsMsgs = UtilsMsgs()
    
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
                    sErrorMsg = "ERROR", "Not a valid quiz - Invalid XML root node:" + sXmlPath
                    self.oUtilsMsgs.DisplayError(sErrorMsg)
                    raise NameError('Invalid XML root node: %s' % sXmlPath)
 
                
            except NameError:
                raise
 
            except:
                bSuccess = False
                sErrorMsg = "ERROR", "Not a valid quiz - Parsing XML file error:" + sXmlPath
                self.oUtilsMsgs.DisplayError(sErrorMsg)
                raise Exception('Parsing XML file error: %s' % sXmlPath)
                 
        else:
            bSuccess = False
            sErrorMsg = "ERROR", "XML file does not exist:" + sXmlPath
            self.oUtilsMsgs.DisplayError(sErrorMsg)
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
        
#         iNumChildren = xParentNode.getElementsByTagName(sChildTagName).length

#         iNumChildren = xParentNode.countChildren()

        iNumChildren = len(xParentNode.findall(sChildTagName))
        return iNumChildren

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetChildren(self, xParentNode, sChildTagName):
        """
        given an xml node, return the child nodes with the specified tagname
        """
        
#         xmlChildren = xParentNode.getElementsByTagName(sChildTagName)

        xmlChildren = xParentNode.findall(sChildTagName)
        
        return xmlChildren

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetNthChild(self, xParentNode, sChildTagName, indElem):
        """
        given an xml node, return the nth child node with the specified tagname
        """
        
#         xmlChildNode = xParentNode.getElementsByTagName(sChildTagName)[iIndex]

        xmlChildNode = None

        # for elem in parent[indElem].iter(sElemName):
        #     print(elem.tag, elem.attrib, elem.text)

        ind = 0
        for elem in xParentNode.findall(sChildTagName):
            if ( ind == indElem ):
                xmlChildNode = elem
#                 print(elem.tag, elem.attrib, elem.text)

            ind = ind + 1
        
        
        return xmlChildNode

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetLatestChildElement(self, xParentNode, sChildTagName):
        """
        retrieve the latest child with the tag name given, from 
        the parent xml input element
        """
                 
        dtLatestTimestamp = ''    # timestamp of type 'datetime'
        xLatestChildElement = None
 
        xAllChildren = self.GetChildren(xParentNode, sChildTagName)
        for xChild in xAllChildren:
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
        
#         listOfAttributes = []
#         for index in range(0,xNode.attributes.length):
#             (name, value) = xNode.attributes.items()[index]
#             tupAttribute = name, value
#             listOfAttributes.append(tupAttribute)

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
        
#         sAttributeValue = xNode.getAttribute(sAttributeName)

        try:
            dictAttribs = xNode.attrib
            sAttributeValue = dictAttribs[sAttributeName]
        except:
            sAttributeValue = ''
            
        
        return sAttributeValue

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetDataInNode(self, xNode):
        # given a node get the value
        
#         xData = 'Empty'
#         nodes = xNode.childNodes
#         for node in nodes:
#             if node.nodeType == node.TEXT_NODE:
#                 xData =node.data
# #                 print(xData)
#             else:
#                 print('invalid data node  check xml schema' )
        
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
                
        return sData
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddElement(self, xParentNode, sTagName, sText, dictAttrib):
        
        elem = xParentNode.makeelement(sTagName, dictAttrib)
        elem.text = sText
        xParentNode.append(elem)

#         elem = etree.Element(sTagName)
#         elem.text = sText
#         elem.attrib = dictAttrib
#         xParentNode.insert(1, elem)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def UpdateAtributesInElement(self, xElement, dictAttrib):
        
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



##########################################################################
#
#   class UtilsMsgs
#
##########################################################################

class UtilsMsgs:
    """ Class UtilsMsgs
        create message box to handle displaying errors, warnings and general information
    """
    
    def __init__(self, parent=None):
        self.parent = parent
        self.msgBox = qt.QMessageBox()
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def DisplayError(self,sErrorMsg):
        self.msgBox.critical(slicer.util.mainWindow(),"Image Quizzer: ERROR",sErrorMsg)
        exit()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def DisplayWarning(self,sWarningMsg):
        self.msgBox.warning(slicer.util.mainWindow(), 'Image Quizzer: Warning', sWarningMsg)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def DisplayInfo(self, sTextMsg):
        self.msgBox.information(slicer.util.mainWindow(), 'Image Quizzer: Information', sTextMsg)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def DisplayYesNo(self, sMsg):
        qtAns = self.msgBox.question(slicer.util.mainWindow(),'Image Quizzer: Continue?',sMsg, qt.QMessageBox.Yes, qt.QMessageBox.No)
        return qtAns

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def DisplayOkCancel(self,sMsg):
        qtAns = self.msgBox.question(slicer.util.mainWindow(),"Image Quizzer: ",sMsg, qt.QMessageBox.Ok, qt.QMessageBox.Cancel)
        return qtAns

        