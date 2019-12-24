from abc import ABC, abstractmethod
import os, sys
import warnings

import xml.dom.minidom


#-----------------------------------------------

class UtilsIOXml(ABC):
    """ Inherits from ABC - Abstract Base Class
    """
    
    def __init__(self):
        self.sClassName = 'undefinedClassName'
        self.sFnName = 'undefinedFunctionName'
        
    
#     @abstractmethod        
#     def getAttributes(self, xCurrentNode): pass
# 
#     @abstractmethod        
#     def getChildElement(self, xCurrentNode, sChildName ): pass
    
    
    def openXml(self, sXmlPath, sRootNodeName):
        # given a path, open the xml document
        
        # initialize a document node
        xNode = None
        # test for existence
        if (os.path.isfile(sXmlPath)):
            
            try:
                xDoc = xml.dom.minidom.parse(sXmlPath)
                xNode = xDoc.documentElement
                   
                # check for expected root node
                sNodeName = self.getNodeName(xNode)
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

    
    def getNodeName(self, xNode):

        # check for correct type of node  
        if xNode.nodeType == xml.dom.Node.ELEMENT_NODE:
            sNodeName = xNode.nodeName
        else:
            raise Exception('Invalid XML node type')

        return sNodeName
                
    def getNumChildren(self, xNode, sChildTagName):
        # given an xml node, return the number of children with the specified tagname
        
        xNodeChild = xNode.getElementsByTagName(sChildTagName)
#         for xChild in xNodeChild:
            
        

#-----------------------------------------------
class IOXmlImageNode(UtilsIOXml):
    
    def __init__(self):
        self.type = ''
        self.descriptor  = ''
        self.destination = 'All'
        self.path = ''
        
    def getAttributes(self,xCurrentNode):
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
                
 
        

        
    
        