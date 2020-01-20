# from abc import ABC, abstractmethod
import os, sys
import warnings
import vtk, qt, ctk, slicer

import xml.dom.minidom


#-----------------------------------------------

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
                print(xData)
            else:
                print('invalid data node  check xml schema' )
             
            
        return xData
    
#-----------------------------------------------
class IOXmlImageNode(UtilsIOXml):
    
    def __init__(self):
        self.type = ''
        self.descriptor  = ''
        self.destination = 'All'
        self.path = ''
        
    def GetAttributes(self,xCurrentNode):
        print('Element Name: %s' % xCurrentNode.nodeName)
        for(name, value) in xCurrentNode.attributes.items():
            print('name: %s value: %s' % (name, value))
            if name == 'type':
                self.type = value
            if name == 'descriptor':
                self.descriptor = value
            if name == 'destination':
                self.destination = value
            if name == 'path':
                self.path = value
                
 

#-----------------------------------------------
class QuizzerMessages:
    
    def __init__(self):
        pass
    
    def DisplayError(self,sErrorMsg):
        self.msgBox = qt.QMessageBox()
        self.msgBox.critical(slicer.util.mainWindow(),"ERROR",sErrorMsg)
        
    def DisplayWarning(self,sWarningMsg):
        self.msgBox = qt.QMessageBox()
        self.msgBox.warning(slicer.util.mainWindow(), 'Warning', sWarningMsg)

