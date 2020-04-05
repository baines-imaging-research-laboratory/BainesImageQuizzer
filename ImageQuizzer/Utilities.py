# from abc import ABC, abstractmethod
import os, sys
import warnings
import vtk, qt, ctk, slicer

import xml.dom.minidom


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
        
    
    #-------------------------------------------

    def OpenXml(self, sXmlPath, sRootNodeName):
        # given a path, open the xml document
        
        # initialize a document node
        xNode = None
        # test for existence
        if (os.path.isfile(sXmlPath)):
            
            try:
                xDoc = xml.dom.minidom.parse(sXmlPath)
                xNode = xDoc.documentElement
                   
                # check for expected root node
                sNodeName = self.GetNodeName(xNode)
                if sNodeName == sRootNodeName:
                    bSuccess = True

                else:
                    bSuccess = False
                    raise Exception('Invalid XML root node: %s' % sXmlPath)
            except:
                raise Exception('Parsing XML file error: %s' % sXmlPath)
                
        else:
            bSuccess = False
            raise Exception('XML file does not exist: %s' % sXmlPath)
        
        return bSuccess, xNode

    
    #-------------------------------------------

    def GetNodeName(self, xNode):

        # check for correct type of node  
        if xNode.nodeType == xml.dom.Node.ELEMENT_NODE:
            sNodeName = xNode.nodeName
        else:
            raise Exception('Invalid XML node type')

        return sNodeName
                
    #-------------------------------------------

    def GetNumChildren(self, xParentNode, sChildTagName):
        # given an xml node, return the number of children with the specified tagname
        
        iNumChildren = xParentNode.getElementsByTagName(sChildTagName).length
        
        return iNumChildren

    #-------------------------------------------

    def GetChildren(self, xParentNode, sChildTagName):
        # given an xml node, return the child nodes with the specified tagname
        
        xmlChildren = xParentNode.getElementsByTagName(sChildTagName)
        
        return xmlChildren

    #-------------------------------------------

    def GetNthChild(self, xParentNode, sChildTagName, iIndex):
        # given an xml node, return the nth child node with the specified tagname
        
        xmlChildNode = xParentNode.getElementsByTagName(sChildTagName)[iIndex]
        
        return xmlChildNode

    #-------------------------------------------

    def GetListOfNodeAttributes(self, xNode):
        # given a node, return a list of all its attributes
        listOfAttributes = []
        for index in range(0,xNode.attributes.length):
            (name, value) = xNode.attributes.items()[index]
            tupAttribute = name, value
            listOfAttributes.append(tupAttribute)
            
        return listOfAttributes
        
    #-------------------------------------------

    def GetValueOfNodeAttribute(self, xNode, sAttributeName):
        # given a node and an attribute name, get the value
        sAttributeValue = xNode.getAttribute(sAttributeName)
        
        return sAttributeValue

    #-------------------------------------------

    def GetDataInNode(self, xNode):
        # given a node get the value
        
        xData = 'Empty'
        
#         name = self.GetNodeName(xNode)
#         print('???? NAME ????: %s' % name)
# 
#         infoObj = xNode.getElementsByTagName("Option")
#         
#         for i in range(0,infoObj.length):
#             optNode = self.GetNthChild(xNode, 'Option', i)
# 
#             nodes = optNode.childNodes
#             for node in nodes:
#                 if node.nodeType == node.TEXT_NODE:
#                     xData = node.data
#                     print(xData)
#                 else:
#                     print('invalid data node  check xml schema' )


        nodes = xNode.childNodes
        for node in nodes:
            if node.nodeType == node.TEXT_NODE:
                xData =node.data
#                 print(xData)
            else:
                print('invalid data node  check xml schema' )
             
            
        return xData
    


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
        self._sResourcesPath = ''
        self._sUsersBasePath = ''
        self._sQuizFilename = ''
        self._sQuizUsername = ''
        self._sTestDataBasePath = ''
        self._sTestDataFilename = ''
        self._sUserDir = ''

    #-------------------------------------------
    #        Getters / Setters
    #-------------------------------------------

    def SetQuizFilename(self, sSelectedQuiz):
        self._sQuizFilename = sSelectedQuiz
        
    #----------
    def SetQuizUsername(self, sSelectedUser):
        self._sQuizUsername = sSelectedUser
        
    #----------
    def SetTestDataFilename(self, sTestDataFilename):
        self._sTestDataFilename = sTestDataFilename
        
    #----------
    def GetQuizFilename(self):
        return self._sQuizFilename
    
    #----------
    def GetQuizUsername(self):
        return self._sQuizUsername

#     #----------
#     def GetUsersBasePath(self):
#         return self._sUsersBasePath
    
    #----------
    def GetUsersDir(self):
        return self._sUserDir
    
    #----------
    def GetResourcesPath(self):
        return self._sResourcesPath
    
    #----------
    def GetTestDataFilename(self):
        return self._sTestDataFilename


    #-------------------------------------------
    #        Functions
    #-------------------------------------------

    def SetupModulePaths(self, sModuleName):
        sScriptedModulesPath = eval('slicer.modules.%s.path' % sModuleName.lower())
        sScriptedModulesPath = os.path.dirname(sScriptedModulesPath)
        self._sResourcesPath = os.path.join(sScriptedModulesPath, 'Resources', 'XML')
        self._sUsersBasePath = os.path.join(sScriptedModulesPath, 'Users')
        self._sTestDataBasePath  = os.path.join(sScriptedModulesPath, 'Testing', 'TestData')
        
    #-------------------------------------------

    def SetupUserDir(self, sUsername):
        _sUserDir = os.path.join(self._sUsersBasePath, sUsername)

        # check that the user folder exists - if not, create it
        if not os.path.exists(_sUserDir):
            os.makedirs(_sUserDir)
        