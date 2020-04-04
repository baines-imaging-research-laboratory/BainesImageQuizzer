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
    
    def __init__(self, parent=None):
        self.parent = parent
        
        
##########################################################################
#
#   class UtilsIOXml
#
##########################################################################


class UtilsIOXml:
    
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
    
    def __init__(self, parent=None):
        self.parent = parent
        self.ScriptedModulesPath = ''
        self.sResourcesPath = ''
        self.sUsersBasePath = ''
        self.sQuizFilename = ''
        self.sQuizUsername = ''


    #-------------------------------------------

    def SetupModulePaths(self, sModuleName):
        self.ScriptedModulesPath = eval('slicer.modules.%s.path' % sModuleName.lower())
        self.ScriptedModulesPath = os.path.dirname(self.ScriptedModulesPath)
        self.sResourcesPath = os.path.join(self.ScriptedModulesPath, 'Resources', 'XML')
        self.sUsersBasePath = os.path.join(self.ScriptedModulesPath, 'Users')
        
    #-------------------------------------------

    def SetQuizFilename(self, sSelectedQuiz):
        self.sQuizFilename = sSelectedQuiz
        
    #-------------------------------------------

    def SetQuizUsername(self, sSelectedUser):
        self.sQuizUsername = sSelectedUser
        
    #-------------------------------------------

    def GetQuizFilename(self):
        return self.sQuizFilename
    
    #-------------------------------------------

    def GetQuizUsername(self):
        return self.sQuizUsername
