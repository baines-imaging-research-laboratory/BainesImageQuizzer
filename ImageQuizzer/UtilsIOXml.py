# from abc import ABC, abstractmethod
import os, sys
import warnings

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

#     #-------------------------------------------
# 
#     def getListOfChildAttributes(self, xParentNode, sChildTagName):
#         # given the parent node and the name of the child node of interest,
#         #    return the list of name,value pairs of the attributes
#          
#         iNumAttributes = xParentNode.getElementsByTagName(sChildTagName)[0].attributes.length
#         
#         for i in range(0,iNumAttributes):
#             (name, value) = xParentNode.getElementsByTagName(sChildTagName)[0].attributes.items()[i]
#             print('name: %s ..... value: %s' % (name, value))
#         

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
                
 
        

        
    
        