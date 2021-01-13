# from abc import ABC, abstractmethod
import os, sys
import warnings
import vtk, qt, ctk, slicer

import xml.dom.minidom
from shutil import copyfile

import DICOMLib
from DICOMLib import DICOMUtils

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
            sResponseTime = self.GetValueOfNodeAttribute(xChild, 'responsetime')
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
        
        self._sScriptedModulesPath = ''     # location of quizzer module project

        self._sXmlResourcesDir = ''         # folder - holds XML quiz files to copy to user
        self._sResourcesQuizPath = ''       # full path (dir/file) of quiz to copy to user
        self._sQuizFilename = ''            # quiz filename only (no dir)

        self._sDataParentDir = ''           # parent folder to images, DICOM database and users folders
        
        self._sUsersParentDir = ''          # folder - parent dir to all user folders
        self._sUsername = ''                # name of user taking the quiz
        self._sUserDir = ''                 # folder - holds quiz subfolders for specific user

        self._sUserQuizResultsDir = ''      # folder for quiz results
        self._sUserQuizResultsPath = ''     # full path (dir/file) for user's quiz results

        self._sDICOMDatabaseDir = ''
#         self._sImageVolumeDataDir = ''

        self._sResourcesROIColorFilesDir = ''  # folder to the Quizzer specific roi color files
        self._sQuizzerROIColorTableNameWithExt = 'QuizzerROIColorTable.txt'
        self._sDefaultROIColorTableName = 'GenericColors'

        self.oUtilsMsgs = UtilsMsgs()

#     def setup(self):
#         self.oUtilsMsgs = UtilsMsgs()
        
    #-------------------------------------------
    #        Getters / Setters
    #-------------------------------------------
    
    #----------
    def SetDataParentDir(self, sDataDirInput):
        self._sDataParentDir = sDataDirInput
        
    #----------
    def SetResourcesQuizPathAndFilename(self, sSelectedQuizPath):

        self._sResourcesQuizPath = os.path.join(self._sXmlResourcesDir, sSelectedQuizPath)
        self._sDir, self._sQuizFilename = os.path.split(self._sResourcesQuizPath)
        
    #----------
    def SetUsernameAndDir(self, sSelectedUser):
        self._sUsername = sSelectedUser
        self._sUserDir = os.path.join(self.GetUsersParentDir(), self._sUsername)
        
    #----------
    def SetResourcesROIColorFilesDir(self):
        self._sResourcesROIColorFilesDir = os.path.join(self.GetScriptedModulesPath(),\
                                                        'Resources','ColorFiles')
        
    #----------
    def GetResourcesROIColorFilesDir(self):
        return self._sResourcesROIColorFilesDir
    
    #----------
    def GetQuizzerROIColorTableNameWithExt(self):
        return self._sQuizzerROIColorTableNameWithExt
    
    #----------
    def GetDefaultROIColorTableName(self):
        return self._sDefaultROIColorTableName
#     ###################
#     #----------
#     def SetUserQuizResultsDir(self, sFilename):
#         self._sUserQuizResultsDir = os.path.join(self.GetUserDir(), sFilename)
#         
#     #----------
#     def SetUserQuizResultsPath(self, sFilename):
#         
#         self._sUserQuizResultsPath = os.path.join(self.GetUserQuizResultsDir(), sFilename)
#     #####################
    
    
    
    #----------
    def SetupForUserQuizResults(self):
        

        sQuizFileRoot, sExt = os.path.splitext(self.GetQuizFilename())
        
        self._sUserQuizResultsDir = os.path.join(self.GetUserDir(), sQuizFileRoot)
        self._sUserQuizResultsPath = os.path.join(self.GetUserQuizResultsDir(), self.GetQuizFilename())

        # check that the user folder exists - if not, create it
        if not os.path.exists(self._sUserQuizResultsDir):
            os.makedirs(self._sUserQuizResultsDir)
        
    
    #----------
    def CreatePageDir(self, sPageName):
        # page dir stores label maps for the specified page
        # store these in the user directory
        sPageDir = os.path.join(self.GetUserDir(), sPageName)
        
        # check that the Page directory exists - if not create it
        if not os.path.exists(sPageDir):
            os.makedirs(sPageDir)
    
        return sPageDir

    
    #----------

    #----------
    def GetDataParentDir(self):
        return self._sDataParentDir

    #----------
    def GetDICOMDatabaseDir(self):
        return self._sDICOMDatabaseDir
    
#     #----------
#     def GetImageVolumeDataDir(self):
#         return self._sImageVolumeDataDir

    #----------
    def GetScriptedModulesPath(self):
        return self._sScriptedModulesPath
    
    #----------
    def GetResourcesQuizPath(self):
        return self._sResourcesQuizPath
    
    #----------
    def GetUsername(self):
        return self._sUsername
     
    #----------
    def GetUserDir(self):
        return self._sUserDir

    def GetUsersParentDir(self):
        return self._sUsersParentDir    

    #----------
    def GetUserQuizResultsDir(self):
        return self._sUserQuizResultsDir

    #----------
    def GetUserQuizResultsPath(self):
        return self._sUserQuizResultsPath
    
    #----------
    def GetXmlResourcesDir(self):
        return self._sXmlResourcesDir
    
    #----------
    def GetRelativeUserPath(self, sInputPath):
        # remove absolute path to user folders
        return sInputPath.replace(self.GetUserDir()+'\\','')

    #----------
    def GetAbsoluteDataPath(self, sInputPath):
        return os.path.join(self._sDataParentDir, sInputPath)
    
    #----------
    def GetAbsoluteUserPath(self, sInputPath):
        return os.path.join(self.GetUserDir(), sInputPath)
    
    #----------
    def GetQuizFilename(self):
        return self._sQuizFilename

    #----------
    def GetFilenameWithExtFromPath(self, sFilePath):
        sDir,sFilenameWithExt = os.path.split(sFilePath)

        return sFilenameWithExt
    
    #----------
    def GetFilenameNoExtFromPath(self, sFilePath):
        sDir, sFilenameExt = os.path.split(sFilePath)
        sFilenameNoExt = os.path.splitext(sFilenameExt)[0]

        return sFilenameNoExt
    
    
    #----------
    def CleanFilename(self, sInputFilename):
#         sInvalid = '<>:"/\|?* '
        sInvalid = '<>:"/\|?*'
        sCleanName = sInputFilename
        
        for char in sInvalid:
            sCleanName = sCleanName.replace(char,'')
            
        return sCleanName

    #----------
    def getNodes(self):
        
        ##### For Debug #####
        # return nodes in the mrmlScene
        #    Can be used to flag differences in nodes before and after code
        #    being investigated (example: for memory leaks)

        nodes = slicer.mrmlScene.GetNodes()
        return [nodes.GetItemAsObject(i).GetID() for i in range(0,nodes.GetNumberOfItems())]

        ######################
        # set the following line before code being investigated
        #
        #        nodes1 = self.oFilesIO.getNodes()
        #
        # set these lines after code being investigated
        #
        #        nodes2 = self.oFilesIO.getNodes()
        #        filteredX = ' '.join((filter(lambda x: x not in nodes1, nodes2)))
        #        print(':',filteredX)
        ######################

    #----------
    def PrintDirLocations(self):
        
        ##### For Debug #####
        print('Data parent dir:      ', self.GetDataParentDir())
        print('DICOM DB dir:         ', self.GetDICOMDatabaseDir())
        print('User parent dir:      ', self.GetUsersParentDir())
        print('User dir:             ', self.GetUserDir())
        print('User Quiz Results Dir:', self.GetUserQuizResultsDir())
        print('User Quiz Reults path:', self.GetUserQuizResultsPath())
        
    #-------------------------------------------
    #        Functions
    #-------------------------------------------

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetModuleDirs(self, sModuleName, sSourceDirForQuiz):
        self._sScriptedModulesPath = eval('slicer.modules.%s.path' % sModuleName.lower())
        self._sScriptedModulesPath = os.path.dirname(self._sScriptedModulesPath)
        self._sXmlResourcesDir = os.path.join(self._sScriptedModulesPath, sSourceDirForQuiz)
        self.SetResourcesROIColorFilesDir()
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetupUserAndDataDirs(self, sParentDirInput):
        
        # user selected data directory - the parent
        #    ImageVolumes subfolder will contain image volumes ready for import 
        #    Quiz results in XML format are stored in the Users subfolders
        #        as well as any saved label volumes
        #    Slicer updates the dicom database in the SlicerDICOMDatabase subfolder
        #        to coordinate import/load of images
        
        
        self._sDataParentDir = sParentDirInput
        
        # all paths for images in the XML quiz files are relative to the data parent directory
        
#         #  importing will use this directory as the root
#         self._sImageVolumeDataDir = os.path.join(sParentDirInput, 'ImageVolumes')

        # if users directory does not exist yet, it will be created
        self._sUsersParentDir = os.path.join(sParentDirInput, 'Users')
        if not os.path.exists(self._sUsersParentDir):
            os.makedirs(self._sUsersParentDir)
            
        # create the DICOM database if it is not there ready for importing
        self._sDICOMDatabaseDir = os.path.join(sParentDirInput, 'SlicerDICOMDatabase')
        if not os.path.exists(self._sDICOMDatabaseDir):
            os.makedirs(self._sDICOMDatabaseDir)
        
        # assign the database directory to the browser widget
        slDicomBrowser = slicer.modules.dicom.widgetRepresentation().self() 
        slDicomBrowserWidget = slDicomBrowser.browserWidget
        slDicomBrowserWidget.dicomBrowser.setDatabaseDirectory(self._sDICOMDatabaseDir)
        
        # update the database through the dicom browser 
        # this clears out path entries that can no longer be resolved
        #    (in the case of database location changes)
        slDicomBrowserWidget.dicomBrowser.updateDatabase()
        
        # test opening the database
        bSuccess, sMsg = self.OpenSelectedDatabase()
        if not bSuccess:
            self.oUtilsMsgs.DisplayWarning(sMsg)

        
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def OpenSelectedDatabase(self):
        
        sMsg = ''
        if DICOMUtils.openDatabase(self._sDICOMDatabaseDir):
            return True, sMsg
        else:
            sMsg = 'Trouble opening SlicerDICOMDatabase in : '\
                 + self._sDataParentDir\
                 + '\n Reselect Image Quizzer data directory or contact administrator.'
            return False, sMsg
            
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def PopulateUserQuizFolder(self):
            
        # check if quiz file already exists in the user folder - if not, copy from Resources

#         # setup for new location
#         self._sUserQuizResultsPath = os.path.join(self._sUserDir, self._sQuizFilename)

        if not os.path.isfile(self.GetUserQuizResultsPath()):
            # file not found, copy file from Resources to User folder
            copyfile(self.GetResourcesQuizPath(), self.GetUserQuizResultsPath())
            return True

        else:

            # create backup of existing file
            self.BackupUserQuizResults()
                
            # file exists - make sure it is readable
            if not os.access(self.GetUserQuizResultsPath(), os.R_OK):
                # existing file is unreadable
                sErrorMsg = 'Quiz file is not readable'
                self.oUtilsMsgs.DisplayWarning(sErrorMsg)     
                return False
            else:
                return True
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def BackupUserQuizResults(self):
        
        # get current date/time
        from datetime import datetime
        now = datetime.now()
        sSuffix = now.strftime("%b-%d-%Y-%H-%M-%S")
        
        sFileRoot, sExt = os.path.splitext(self.GetQuizFilename())
        
        sNewFileRoot = '_'.join([sFileRoot, sSuffix])
        sNewFilename = ''.join([sNewFileRoot, sExt])
        
        sBackupQuizResultsPath = os.path.join(self.GetUserQuizResultsDir(), sNewFilename)
        
        # create copy with data/time stamp as suffix
        copyfile(self.GetUserQuizResultsPath(), sBackupQuizResultsPath)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetupROIColorFile(self, sInputROIColorFile):
        """ If quiz has a custom color table for segmenting ROI's, move this 
            into the color table file that is read in by the QuizzerHelperBox
        """
        # set up for default
        if sInputROIColorFile == '' or sInputROIColorFile == 'default':
            sInputROIColorFile = self.GetDefaultROIColorTableName()
        
        sInputROIColorFileWithExt = sInputROIColorFile + '.txt'   
        
        # get resources dir and join to requested color file
        sROIColorFileDir = self.GetResourcesROIColorFilesDir()
        sROIColorFilePath = os.path.join(sROIColorFileDir, sInputROIColorFileWithExt)
        sQuizzerROIColorTablePath = os.path.join(sROIColorFileDir, \
                                                 self.GetQuizzerROIColorTableNameWithExt())
        
        # check if requested table exists
        if not os.path.isfile(sROIColorFilePath):
            sMsg = 'ROI Color file "' + sInputROIColorFileWithExt + '" does not exist in :' + sROIColorFileDir
            self.oUtilsMsgs.DisplayError(sMsg)
        else:
            # if yes - overwrite QuizzerColorTable
            copyfile(sROIColorFilePath, sQuizzerROIColorTablePath)
                
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
#     def CloseFiles(self):
#         self.msgBox.information(slicer.util.mainWindow(), 'Information', 'Closing Time')
    
        