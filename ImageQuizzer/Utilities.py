# from abc import ABC, abstractmethod
import os, sys
import warnings
import vtk, qt, ctk, slicer

import xml.dom.minidom
from shutil import copyfile


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
        
    
    #----------
    def GetXmlTree(self):
        return self._xTree
    
    #----------
    def GetRootNode(self):
        return self._xRootNode
    
    #----------
    def SetRootNode(self, xNodeInput):
        self._xRootNode = xNodeInput
        
        
    #-------------------------------------------

    def OpenXml(self, sXmlPath, sRootNodeName):
#         # given a path, open the xml document
#         
#         # initialize a document node
#         xNode = None
#         # test for existence
#         if (os.path.isfile(sXmlPath)):
#             
#             try:
#                 xDoc = xml.dom.minidom.parse(sXmlPath)
#                 xNode = xDoc.documentElement
#                    
#                 # check for expected root node
#                 sNodeName = self.GetElementNodeName(xNode)
#                 if sNodeName == sRootNodeName:
#                     bSuccess = True
#  
#                 else:
#                     bSuccess = False
#                     raise NameError('Invalid XML root node: %s' % sXmlPath)
# 
#             except NameError:
#                 raise
# 
#             except:
#                 bSuccess = False
#                 raise Exception('Parsing XML file error: %s' % sXmlPath)
#                 
#         else:
#             bSuccess = False
#             raise Exception('XML file does not exist: %s' % sXmlPath)
#         
#         return bSuccess, xNode

        # given a path, open the xml document
         
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

    
    #-------------------------------------------

    def GetElementNodeName(self, xNode):

#         # check for correct type of node  
#         if xNode.nodeType == xml.dom.Node.ELEMENT_NODE:
#             sNodeName = xNode.nodeName
#         else:
#             raise TypeError('Invalid XML node type: should be Element type of node')

        try:
            sNodeName = xNode.tag
        except:
            raise TypeError('Invalid XML node type: should be Element type of node')
        

        return sNodeName
                
    #-------------------------------------------

    def GetNumChildrenByName(self, xParentNode, sChildTagName):
        # given an xml node, return the number of children with the specified tagname
        
#         iNumChildren = xParentNode.getElementsByTagName(sChildTagName).length

#         iNumChildren = xParentNode.countChildren()

        iNumChildren = len(xParentNode.findall(sChildTagName))
        return iNumChildren

    #-------------------------------------------

    def GetChildren(self, xParentNode, sChildTagName):
        # given an xml node, return the child nodes with the specified tagname
        
#         xmlChildren = xParentNode.getElementsByTagName(sChildTagName)

        xmlChildren = xParentNode.findall(sChildTagName)
        
        return xmlChildren

    #-------------------------------------------

    def GetNthChild(self, xParentNode, sChildTagName, indElem):
        # given an xml node, return the nth child node with the specified tagname
        
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

    #-------------------------------------------

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
        
    #-------------------------------------------

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

    #-------------------------------------------

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
        
        
        if '\n' or '\t' in sData: 
            # clean up any tabs or line feeds in the data string; replace with null
            #    Element tree stores '\n\t\t'  when the text property is empty for an element 
            sTab = '\t'
            sNull = ''
            sLineFeed = '\n'
            sData = sData.replace(sTab, sNull)
            sData = sData.replace(sLineFeed, sNull)
        
        return sData
    
    #-------------------------------------------

    def AddElement(self, xParentNode, sTagName, sText, dictAttrib):
        
        elem = xParentNode.makeelement(sTagName, dictAttrib)
        elem.text = sText
        xParentNode.append(elem)

#         elem = etree.Element(sTagName)
#         elem.text = sText
#         elem.attrib = dictAttrib
#         xParentNode.insert(1, elem)

        
    #-------------------------------------------

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

    #-------------------------------------------

    def SaveXml(self, sXmlPath, xTree):

        # by using minidom to reparse the root, we can get a 'pretty' - more user friendly 
        #    xml document output with indents and newlines using writexml
        
        reparsedRoot = self.prettify(self._xRootNode)
 
        try:
            with open(sXmlPath, 'w') as xml_outfile:
                reparsedRoot.writexml(xml_outfile, encoding="utf-8", indent="\t", addindent="\t", newl="\n")
           
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
    
    #-------------------------------------------

    def DisplayError(self,sErrorMsg):
        self.msgBox.critical(slicer.util.mainWindow(),"ERROR",sErrorMsg)
        exit()

    #-------------------------------------------

    def DisplayWarning(self,sWarningMsg):
        self.msgBox.warning(slicer.util.mainWindow(), 'Warning', sWarningMsg)

    #-------------------------------------------

    def DisplayInfo(self, sTextMsg):
        self.msgBox.information(slicer.util.mainWindow(), 'Information', sTextMsg)

    #-------------------------------------------

##########################################################################
#
#   class UtilsIO
#
##########################################################################

class UtilsIO:
    """ Class UtilsIO
        to set up path and filenames for the Image Quizzer module
    """
    
    def __init__(self, parent=None):
        self.parent = parent
        
        self._sXmlResourcesDir = '' # folder - holds XML quiz files to copy to user
        self._sUsersBaseDir = ''    # folder - parent dir to all user folders
        self._sUserDir = ''         # folder - holds quiz for specific user

        self._sQuizFilename = ''    # quiz filename only (no dir)
        self._sQuizUsername = ''    # name of user taking the quiz

        self._sResourcesQuizPath = ''   # full path (dir/file) of quiz to copy to user
        self._sUserQuizPath = ''        # full path (dir/file) for user's quiz

        self._sTestDataBaseDir = ''
        self._sTestDataFilename = ''



    def setup(self):
        self.oUtilsMsgs = UtilsMsgs()
        
    #-------------------------------------------
    #        Getters / Setters
    #-------------------------------------------

    def SetResourcesQuizPath(self, sSelectedQuiz):

        self._sResourcesQuizPath = os.path.join(self._sXmlResourcesDir, sSelectedQuiz)
        
    #----------
    def SetQuizUsername(self, sSelectedUser):
        self._sQuizUsername = sSelectedUser
        
    #----------
    def SetUserDir(self):
        self._sUserDir = os.path.join(self._sUsersBaseDir, self._sQuizUsername)

        # check that the user folder exists - if not, create it
        if not os.path.exists(self._sUserDir):
            os.makedirs(self._sUserDir)

    #----------
    def SetUserQuizPath(self, sFilename):
        
        self._sUserQuizPath = os.path.join(self._sUserDir, sFilename)
        
        
    #----------
    def SetModuleDirs(self, sModuleName, sSourceDirForQuiz):
        sScriptedModulesPath = eval('slicer.modules.%s.path' % sModuleName.lower())
        sScriptedModulesPath = os.path.dirname(sScriptedModulesPath)
        self._sXmlResourcesDir = os.path.join(sScriptedModulesPath, sSourceDirForQuiz)
        self._sUsersBaseDir = os.path.join(sScriptedModulesPath, 'Users')
        
        
    #----------
    def GetResourcesQuizPath(self):
        return self._sResourcesQuizPath
    
    #----------
    def GetQuizUsername(self):
        return self._sQuizUsername

    #----------
    def GetUsersBaseDir(self):
        return self._sUsersBaseDir
    
    #----------
    def GetUserDir(self):
        return self._sUserDir
    
    #----------
    def GetUserQuizPath(self):
        return self._sUserQuizPath
    
    #----------
    def GetXmlResourcesDir(self):
        return self._sXmlResourcesDir
    

    #-------------------------------------------
    #        Functions
    #-------------------------------------------

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def PopulateUserQuizFolder(self):
#         # create user folder if it doesn't exist

        self.SetUserDir()
            
        # check if quiz file already exists in the user folder - if not, copy from Resources

        # setup for new location
        sPath, self._sQuizFilename = os.path.split(self._sResourcesQuizPath)
        self._sUserQuizPath = os.path.join(self._sUserDir, self._sQuizFilename)
        if not os.path.isfile(self._sUserQuizPath):
            # file not found, copy file from Resources to User folder
            copyfile(self._sResourcesQuizPath, self._sUserQuizPath)
            return True

        else:

                
            # create backup of existing file
            self.BackupUserQuiz()
                
            # file exists - make sure it is readable
            if not os.access(self._sUserQuizPath, os.R_OK):
                # existing file is unreadable
                sErrorMsg = 'Quiz file is not readable'
                self.oUtilsMsgs.DisplayWarning(sErrorMsg)     
                return False
            else:
                return True
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def BackupUserQuiz(self):
        
        # get current date/time
        from datetime import datetime
        now = datetime.now()
        sSuffix = now.strftime("%b-%d-%Y-%H-%M-%S")
        
        sFileRoot, sExt = os.path.splitext(self._sQuizFilename)
        
        sNewFileRoot = '_'.join([sFileRoot, sSuffix])
        sNewFilename = ''.join([sNewFileRoot, sExt])
        
        sBackupQuizPath = os.path.join(self._sUserDir, sNewFilename)
        
        # create copy with data/time stamp as suffix
        copyfile(self._sUserQuizPath, sBackupQuizPath)
        
        
        
#     def CloseFiles(self):
#         self.msgBox.information(slicer.util.mainWindow(), 'Information', 'Closing Time')
    
        