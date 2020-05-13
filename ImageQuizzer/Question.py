from abc import ABC, abstractmethod

import PythonQt
import os
import vtk, qt, ctk, slicer
import sys
import warnings

from Utilities import *

#========================================================================================
#                     Class Question Set
#========================================================================================

class QuestionSet():
    """ Class to hold array of all questions that were built into group boxes on the form
    """
    
    def __init__(self):
        self.sClassName = type(self).__name__
        self.id = ''
        self.title = ''
        self.overwritableResponsesYN = False
        self.ltupQuestions = []
        self._loQuestions = []
        
    #----------
    def GetQuestionList(self):
        return self._loQuestions
        
    #-----------------------------------------------
        
    def ExtractQuestionsFromXML(self, xNodeQuestionSet):
        # given the xml question set node, extract the questions and set up
        # the list of tuples for building the question set form
        
        oIOXml = UtilsIOXml()
        sNodeName = oIOXml.GetElementNodeName(xNodeQuestionSet)
        if not (sNodeName == "QuestionSet"):
            raise Exception("Invalid XML node. Expecting 'QuestionSet', node name was: %s" % sNodeName)
        else:
            # for each child named 'Question' extract labels and options
            iNumQuestions = oIOXml.GetNumChildrenByName(xNodeQuestionSet, "Question")
            
            self.id = oIOXml.GetValueOfNodeAttribute(xNodeQuestionSet, 'id')
            self.title = oIOXml.GetValueOfNodeAttribute(xNodeQuestionSet, 'title')
            
            xQuestions = oIOXml.GetChildren(xNodeQuestionSet, 'Question')
            
            for xNodeQuestion in xQuestions:

                lsQuestionOptions = []
                dictModifiers = {}

                sQuestionType = oIOXml.GetValueOfNodeAttribute(xNodeQuestion, 'type')
                sQuestionDescriptor = oIOXml.GetValueOfNodeAttribute(xNodeQuestion, 'descriptor')

                # get modifiers for type = IntegerValue
                if sQuestionType =="IntegerValue" or sQuestionType == "FloatValue":
                    sMin = oIOXml.GetValueOfNodeAttribute(xNodeQuestion, 'min')               
                    sMax = oIOXml.GetValueOfNodeAttribute(xNodeQuestion, 'max')
                    dictModifiers['min'] = sMin
                    dictModifiers['max'] = sMax
                    
                                   
                # get options for each question
                
                xOptions = oIOXml.GetChildren(xNodeQuestion, 'Option')

                for iIndex in range(0,len(xOptions)):
                    
                    xQuestionOption = oIOXml.GetNthChild(xNodeQuestion, 'Option', iIndex)
                    sValue = oIOXml.GetDataInNode(xQuestionOption)
                    lsQuestionOptions.append(sValue)
                
            
                tupQuestionGroup = [sQuestionType, sQuestionDescriptor, lsQuestionOptions, dictModifiers]
                self.ltupQuestions.append(tupQuestionGroup)
                

    #-----------------------------------------------
        
    def BuildQuestionSetForm(self):
        # for each item in the list of Questions
        #    - parse the tuple into question items:
        #        0: question type (string)
        #        1: question descriptor (string)
        #        2: list of question options (list of strings)
        #      [ 3: dictionary of modifiers (eg. min, max) for certain question types ] 
        #    - create the appropriate group box
        #    - add to layout
        self.sFnName = sys._getframe().f_code.co_name
        bBuildSuccess = True
        self.CreateGroupBoxWidget()
        
        for i in range(len(self.ltupQuestions)):
            tupQuestionItemInfo = self.ltupQuestions[i]
            sQuestionType = str(tupQuestionItemInfo[0])
            sQuestionDescriptor = str(tupQuestionItemInfo[1])
            lsQuestionOptions = tupQuestionItemInfo[2]
            if len(tupQuestionItemInfo) > 3:
                dictModifiers = tupQuestionItemInfo[3]

            bQuestionTypeGood = True
            if (sQuestionType == 'Radio'):
                self.question = RadioQuestion(lsQuestionOptions, sQuestionDescriptor)
            elif (sQuestionType == 'Checkbox'):
                self.question = CheckBoxQuestion(lsQuestionOptions, sQuestionDescriptor)
            elif (sQuestionType == 'Text'):
                self.question = TextQuestion(lsQuestionOptions, sQuestionDescriptor)
            elif (sQuestionType == 'IntegerValue'):
                self.question = IntegerValueQuestion(lsQuestionOptions, sQuestionDescriptor, dictModifiers)
            elif (sQuestionType == 'FloatValue'):
                self.question = FloatValueQuestion(lsQuestionOptions, sQuestionDescriptor, dictModifiers)
            elif (sQuestionType == 'InfoBox'):
                self.question = InfoBox(lsQuestionOptions, sQuestionDescriptor)
            else:
                sLabel = 'Warning : Contact Administrator - Invalid question    '
                sWarningMsg = self.sClassName + ':' + self.sFnName + ':' + 'UnrecognizedQuestionType - Contact Administrator'
                qlabel = qt.QLabel(sLabel + sWarningMsg)
                qGrpBox = qt.QGroupBox()
                qGrpBoxLayout = qt.QVBoxLayout()
                qGrpBox.setLayout(qGrpBoxLayout)
                qGrpBoxLayout.addWidget(qlabel)
                # TODO .... is the warnings.warn failing??? 
                warnings.warn( sWarningMsg )
                self.qQuizWidgetLayout.addWidget(qGrpBox)
                bQuestionTypeGood = False
                bBuildSuccess = False

            if bQuestionTypeGood:
                bItemSuccess, qWidget = self.question.BuildQuestion()
                if bItemSuccess :
                    self.qQuizWidgetLayout.addWidget(qWidget)
                    self._loQuestions.append(self.question)

            if i > 0:
                bBuildSuccess = bBuildSuccess & bItemSuccess
                
        return bBuildSuccess, self.qQuizWidget

    #-----------------------------------------------
    
    def CreateGroupBoxWidget(self):
        # create group box widget to which each subclass can add elements
        self.qQuizWidget = qt.QWidget()
        self.qQuizWidgetLayout = qt.QVBoxLayout()
        self.qQuizWidget.setLayout(self.qQuizWidgetLayout)
        self.qQuizTitle = qt.QLabel(self.title)
        self.qQuizWidgetLayout.addWidget(self.qQuizTitle)
        
#========================================================================================
#                     Class <<Question>> 
#========================================================================================

class Question(ABC):
    """ Inherits from ABC - Abstract Base Class
    """
    
    def __init__(self):
        self.sClassName = 'undefinedClassName'
        self.sFnName = 'undefinedFunctionName'

    
    @abstractmethod        
    def BuildQuestion(self): pass
    
    @abstractmethod        
    def CaptureResponse(self): pass

    #-----------------------------------------------
    
    def CreateGroupBox(self, sTitle):
        # create group box widget to which each subclass can add elements
        self.qGrpBox = qt.QGroupBox()
        self.qGrpBox.setTitle(sTitle)
        self.qGrpBoxLayout = qt.QVBoxLayout()
        self.qGrpBox.setLayout(self.qGrpBoxLayout)
        
        return self.qGrpBox

    #-----------------------------------------------

    def DisplayGroupBoxEmpty(self):
        # check if group box was already created
        
        sLabel = 'Warning : No options were given. Group Box is empty - Contact Administrator'
        sWarningMsg = self.sClassName + ':' + self.sFnName + ':' + 'NoOptionsAvailable - Contact Administrator'
        qlabel = qt.QLabel(sLabel)
        self.qGrpBoxLayout.addWidget(qlabel)
        warnings.warn( sWarningMsg )

    #-----------------------------------------------

    def CreateRangePrompt(self):
        # extract minimum and maximum restrictions defined in the XML element
        # return the message for prompting the user on allowed range

        sRangeMsg = ''
        if not self.sMin == '':
            sRangeMsg = sRangeMsg + ' ... minimum %s' % self.sMin
        if not self.sMax == '':
            sRangeMsg = sRangeMsg + '   maximum: %s' % self.sMax

        return sRangeMsg

    
    #-----------------------------------------------

    def ValidateRange(self, xValue, xMin, xMax):
        # return boolean to reflect whether the value input is within
        #     the defined minimum to maximum range
        # input values may be either integer or float
        
        bValid = True 
        
        if xMin == None and xMax == None:
            # there are no restrictions for the value
            bValid = True
            
        else:
            if not xMin == None:    # if there is a minimum restriction
                if xValue < xMin:
                    bValid = False
            if not xMax == None:    # if there is a maximum restriction
                if xValue > xMax:
                    bValid = False

        return bValid

#========================================================================================
#                     Class RadioQuestion
#========================================================================================

class RadioQuestion(Question):
    # Create a group box and add radio buttons based on the options provided
    # Inputs : lOptions - list of labels for each radio button
    # Outputs: exitCode - boolean describing whether function exited successfully
    #          qGrpBox  - group box widget holding radio buttons
    
    def __init__(self, lOptions, sGrpBoxTitle):
        self.sClassName = type(self).__name__

        self.lOptions = lOptions
        self.sGrpBoxTitle = sGrpBoxTitle
       
    #-----------------------------------------------
    
    def BuildQuestion(self):
        self.sFnName = sys._getframe().f_code.co_name

        self.CreateGroupBox(self.sGrpBoxTitle)
        
        length = len(self.lOptions)
        if length < 1 :
            self.DisplayGroupBoxEmpty()
            return False, self.qGrpBox
        
        i = 0
        while i < length:
            element1 = self.lOptions[i]
            qRadioBtn = qt.QRadioButton(element1)
            self.qGrpBoxLayout.addWidget(qRadioBtn)
            i = i + 1

        return True, self.qGrpBox
        
    #-----------------------------------------------
    
    def CaptureResponse(self):
        self.sFnName = sys._getframe().f_code.co_name

        lsResponses = []
        bSuccess = False
        bResponseFound = False
        sMsg = ''

        for qBtn in self.qGrpBox.findChildren(qt.QRadioButton):
#             sText = qBtn.text
#             print(sText)
            if qBtn.isChecked():
                lsResponses.append('y')
                bResponseFound = True
            else:
                lsResponses.append('n')

        if bResponseFound:
            bSuccess = True
        else:
            sMsg = 'Missing radio option for: ' + self.sGrpBoxTitle

        return bSuccess, lsResponses, sMsg

#========================================================================================
#                     Class CheckBoxQuestion
#========================================================================================

class CheckBoxQuestion(Question):
    # Create a group box and add check boxes based on the options provided
    # Inputs : lOptions - list of options for each check box
    # Outputs: exitCode - boolean describing whether function exited successfully
    #          qGrpBox  - group box widget holding check boxes
    
    def __init__(self, lOptions, sGrpBoxTitle):
        self.sClassName = type(self).__name__

        self.lOptions = lOptions
        self.sGrpBoxTitle = sGrpBoxTitle

    #-----------------------------------------------
       
    def BuildQuestion(self):
        self.sFnName = sys._getframe().f_code.co_name

        self.CreateGroupBox(self.sGrpBoxTitle)
        
        length = len(self.lOptions)
        if length < 1 :
            self.DisplayGroupBoxEmpty()
            return False, self.qGrpBox
        
        i = 0
        while i < length:
            element1 = self.lOptions[i]
            qChkBox = qt.QCheckBox(element1)
            self.qGrpBoxLayout.addWidget(qChkBox)
            i = i + 1

        return True, self.qGrpBox
        
    #-----------------------------------------------
    
    def CaptureResponse(self):
        self.sFnName = sys._getframe().f_code.co_name

        lsResponses = []
        bSuccess = False
        bResponseFound = False
        sMsg = ''
        
        for qChBox in self.qGrpBox.findChildren(qt.QCheckBox):
#             sText = qBtn.text
#             print(sText)
            if qChBox.isChecked():
                lsResponses.append('y')
                bResponseFound = True
            else:
                lsResponses.append('n')
                
        if bResponseFound:
            bSuccess = True
        else:
            sMsg = 'Missing check box option for: ' + self.sGrpBoxTitle

        return bSuccess, lsResponses, sMsg


#========================================================================================
#                     Class TextQuestion
#========================================================================================

class TextQuestion(Question):
    # Create a group box and add a text box that allows the user to enter text
    # Inputs : lOptions - list of labels for each box 
    # Outputs: exitCode - boolean describing whether function exited successfully
    #          qGrpBox  - group box widget holding text edit boxes
    
    def __init__(self, lOptions, sGrpBoxTitle):
        self.sClassName = type(self).__name__

        self.lOptions = lOptions
        self.sGrpBoxTitle = sGrpBoxTitle
        
    def BuildQuestion(self):
        self.sFnName = sys._getframe().f_code.co_name

        # add grid layout to group box
        self.CreateGroupBox(self.sGrpBoxTitle)
        newLayout = qt.QGridLayout()
        self.qGrpBoxLayout.addLayout(newLayout)
       
        length = len(self.lOptions)
        if length < 1 :
            self.DisplayGroupBoxEmpty()
            return False, self.qGrpBox

        i = 0
        while i < length:
            element1 = self.lOptions[i]
            qLineEdit = qt.QLineEdit()
            qLabel = qt.QLabel(element1)
            newLayout.addWidget(qLabel, i, 0)
            newLayout.addWidget(qLineEdit, i, 1)
            i = i + 1

        return True, self.qGrpBox
        
    #-----------------------------------------------
    
    def CaptureResponse(self):
        self.sFnName = sys._getframe().f_code.co_name

        lsResponses = []
        bSuccess = False
        bResponseFound = False
        sMsg = ''
        
        for qTextBox in self.qGrpBox.findChildren(qt.QLineEdit):
            sText = qTextBox.text
#             print(sText)
            if not sText =='':
                bResponseFound = True
                lsResponses.append(qTextBox.text)
                

        if bResponseFound:
            bSuccess = True
        else:
            sMsg = 'Missing text response for: ' + self.sGrpBoxTitle
            
        return bSuccess, lsResponses, sMsg

#========================================================================================
#                     Class IntegerValueQuestion
#========================================================================================

class IntegerValueQuestion(Question):
    # Create a group box and add a line edit that allows the user to enter an integer value
    # Inputs : lOptions - list of labels for each box 
    # Outputs: exitCode - boolean describing whether function exited successfully
    #          qGrpBox  - group box widget holding the text box for integer input
    
    def __init__(self, lOptions, sGrpBoxTitle, dictModifiers):
        self.sClassName = type(self).__name__

        self.oMsgUtil = UtilsMsgs()
        self.lOptions = lOptions
        self.sGrpBoxTitle = sGrpBoxTitle
        self.dictModifiers = dictModifiers
        self.sMin = ''
        self.sMax = ''
        
        
    def BuildQuestion(self):
        self.sFnName = sys._getframe().f_code.co_name

        # add grid layout to group box
        self.CreateGroupBox(self.sGrpBoxTitle)
        newLayout = qt.QGridLayout()
        self.qGrpBoxLayout.addLayout(newLayout)
       
        length = len(self.lOptions)
        if length < 1 :
            self.DisplayGroupBoxEmpty()
            return False, self.qGrpBox

        i = 0
        while i < length:
            element1 = self.lOptions[i]
            self.sMin = self.dictModifiers.get('min')
            self.sMax = self.dictModifiers.get('max')
            
            sRangeMsg = self.CreateRangePrompt()
            sPlaceholderMsg = 'Enter integer value' + sRangeMsg

            qLineEdit = qt.QLineEdit()
            qLineEdit.setPlaceholderText(sPlaceholderMsg)

            
            qLabel = qt.QLabel(element1)
            newLayout.addWidget(qLabel, i, 0)
            newLayout.addWidget(qLineEdit, i, 1)
            i = i + 1

        return True, self.qGrpBox
        
    #-----------------------------------------------
    
    def CaptureResponse(self):
        self.sFnName = sys._getframe().f_code.co_name

        oMsgUtil = UtilsMsgs()

        lsResponses = []
        bSuccess = False
        sMsg = ''
        bResponseFound = False
        
        sRangeMsg = self.CreateRangePrompt()

        iMin = None
        iMax = None

        try:
            if not self.sMin == '':
                iMin = int(self.sMin)
                
            if not self.sMax == '':
                iMax = int(self.sMax)
        except ValueError:
            bSuccess = False
            sErrorMsg = 'See Administrator. Invalid range attribute in XML tag : ' + self.sGrpBoxTitle
            self.oMsgUtil.DisplayError(sErrorMsg)
            
                
        
        for qTextBox in self.qGrpBox.findChildren(qt.QLineEdit):
            sText = qTextBox.text

            if not sText =='':

                try:
                    iValue = int(sText)
                    bValid = self.ValidateRange(iValue, iMin, iMax)
                    if bValid == True:
                        lsResponses.append(qTextBox.text)
                        bResponseFound = True

                    else:
                        raise ValueError()
                        
                except ValueError:
                    sMsg = 'Please enter integer for: ' + self.sGrpBoxTitle + sRangeMsg
                    bSuccess = bSuccess * False
                    
            else:
                bResponseFound = False

        if bResponseFound:
            bSuccess = True
        else:
            sMsg = 'Invalid integer value response for: ' + self.sGrpBoxTitle + sRangeMsg

                    
        return bSuccess, lsResponses, sMsg
    

#========================================================================================
#                     Class FloatValueQuestion
#========================================================================================

class FloatValueQuestion(Question):
    # Create a group box and add a line edit that allows the user to enter a float value
    # Outputs: exitCode - boolean describing whether function exited successfully
    #          qGrpBox  - group box widget holding the text box for float input
    
    def __init__(self, lOptions, sGrpBoxTitle, dictModifiers):
        self.sClassName = type(self).__name__

        self.oMsgUtil = UtilsMsgs()
        self.lOptions = lOptions
        self.sGrpBoxTitle = sGrpBoxTitle
        self.dictModifiers = dictModifiers
        self.sMin = ''
        self.sMax = ''

    def BuildQuestion(self):
        self.sFnName = sys._getframe().f_code.co_name

        # add grid layout to group box
        self.CreateGroupBox(self.sGrpBoxTitle)
        newLayout = qt.QGridLayout()
        self.qGrpBoxLayout.addLayout(newLayout)
       
        length = len(self.lOptions)
        if length < 1 :
            self.DisplayGroupBoxEmpty()
            return False, self.qGrpBox

        i = 0
        while i < length:
            element1 = self.lOptions[i]

            self.sMin = self.dictModifiers.get('min')
            self.sMax = self.dictModifiers.get('max')
            

            sRangeMsg = self.CreateRangePrompt()
            sPlaceholderMsg = 'Enter decimal value' + sRangeMsg

            qLineEdit = qt.QLineEdit()
            qLineEdit.setPlaceholderText(sPlaceholderMsg)
            
            
            qLabel = qt.QLabel(element1)
            newLayout.addWidget(qLabel, i, 0)
            newLayout.addWidget(qLineEdit, i, 1)
            i = i + 1

        return True, self.qGrpBox
        
    #-----------------------------------------------
    
    def CaptureResponse(self):
        self.sFnName = sys._getframe().f_code.co_name

#         lsResponses = []
#         bSuccess = True
#         sMsg = ''
#         
#         for qSpinner in self.qGrpBox.findChildren(qt.QDoubleSpinBox):
#             lsResponses.append(str(qSpinner.value))


        oMsgUtil = UtilsMsgs()

        lsResponses = []
        bSuccess = False
        sMsg = ''
        bResponseFound = False
        
        sRangeMsg = self.CreateRangePrompt()

        fMin = None
        fMax = None

        try:
            if not self.sMin == '':
                fMin = float(self.sMin)
                
            if not self.sMax == '':
                fMax = float(self.sMax)
        except ValueError:
            bSuccess = False
            sErrorMsg = 'See Administrator. Invalid range attribute in XML tag : ' + self.sGrpBoxTitle
            self.oMsgUtil.DisplayError(sErrorMsg)
            
                
        
        for qTextBox in self.qGrpBox.findChildren(qt.QLineEdit):
            sText = qTextBox.text

            if not sText =='':

                try:
                    fValue = float(sText)
                    bValid = self.ValidateRange(fValue, fMin, fMax)
                    if bValid == True:
                        lsResponses.append(qTextBox.text)
                        bResponseFound = True

                    else:
                        raise ValueError()
                        
                except ValueError:
                    sMsg = 'Please enter decimal value for: ' + self.sGrpBoxTitle + sRangeMsg
                    bSuccess = bSuccess * False
            else:
                bResponseFound = False
    


        if bResponseFound:
            bSuccess = True
        else:
            sMsg = 'Invalid decimal value response for: ' + self.sGrpBoxTitle + sRangeMsg


        return bSuccess, lsResponses, sMsg


#========================================================================================
#                     Class InfoBox
#========================================================================================

class InfoBox(Question):
    # Create a group box and add a label holding information
    # There are no responses from the user to catch
    # Inputs : lOptions - list of labels to go in this label box
    # Outputs: exitCode - boolean describing whether function exited successfully
    #          qGrpBox  - group box widget holding text edit boxes
    
    def __init__(self, lOptions, sGrpBoxTitle):
        self.sClassName = type(self).__name__

        self.lOptions = lOptions
        self.sGrpBoxTitle = sGrpBoxTitle
        
    #-----------------------------------------------

    def BuildQuestion(self):
        self.sFnName = sys._getframe().f_code.co_name

        # add grid layout to group box
        self.CreateGroupBox(self.sGrpBoxTitle)
        newLayout = qt.QGridLayout()
        self.qGrpBoxLayout.addLayout(newLayout)
       
        length = len(self.lOptions)
        if length < 1 :
            self.DisplayGroupBoxEmpty()
            return False, self.qGrpBox

        i = 0
        while i < length:
            element1 = self.lOptions[i]
            qLabel = qt.QLabel(element1)
            newLayout.addWidget(qLabel, i, 0)
            i = i + 1

        return True, self.qGrpBox

    #-----------------------------------------------
    
    def CaptureResponse(self):
        self.sFnName = sys._getframe().f_code.co_name

        bSuccess = True
        sMsg = ''

        lsResponses = ['']
        
        return bSuccess, lsResponses, sMsg
        
    