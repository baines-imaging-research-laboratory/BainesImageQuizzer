from abc import ABC, abstractmethod, abstractproperty

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
#         self.ltupQuestions = []
        self._loQuestions = []
        
        self.oIOXml = UtilsIOXml()
        self.oMsgUtil = UtilsMsgs()
        
    #----------
    def GetQuestionList(self):
        return self._loQuestions
        
    #-----------------------------------------------
        
    def ExtractQuestionsFromXML(self, xNodeQuestionSet):
        
        
        sNodeName = self.oIOXml.GetElementNodeName(xNodeQuestionSet)
        if not (sNodeName == "QuestionSet"):
            raise Exception("Invalid XML node. Expecting 'QuestionSet', node name was: %s" % sNodeName)
        else:
            # for each child named 'Question' extract labels and options
            iNumQuestions = self.oIOXml.GetNumChildrenByName(xNodeQuestionSet, "Question")
            
            self.id = self.oIOXml.GetValueOfNodeAttribute(xNodeQuestionSet, 'id')
            self.title = self.oIOXml.GetValueOfNodeAttribute(xNodeQuestionSet, 'title')
            
            xQuestions = self.oIOXml.GetChildren(xNodeQuestionSet, 'Question')
            
            for xNodeQuestion in xQuestions:

                lsQuestionOptions = []
                dictModifiers = {}

                sQuestionType = self.oIOXml.GetValueOfNodeAttribute(xNodeQuestion, 'type')
                sQuestionDescriptor = self.oIOXml.GetValueOfNodeAttribute(xNodeQuestion, 'descriptor')


                bQuestionTypeGood = True

                if (sQuestionType == 'Radio'):
                    self.question = RadioQuestion()

                elif (sQuestionType == 'Checkbox'):
                    self.question = CheckBoxQuestion()

                elif (sQuestionType == 'Text'):
                    self.question = TextQuestion()

                elif (sQuestionType == 'IntegerValue'):
                    self.question = IntegerValueQuestion()
                    dictModifiers = self.question.GetMinMaxAttributesFromXML(xNodeQuestion)
                    self.question.UpdateDictionaryModifiers(dictModifiers)

                elif (sQuestionType == 'FloatValue'):
                    self.question = FloatValueQuestion()
                    dictModifiers = self.question.GetMinMaxAttributesFromXML(xNodeQuestion)
                    self.question.UpdateDictionaryModifiers(dictModifiers)

                elif (sQuestionType == 'InfoBox'):
                    self.question = InfoBox()

                else:
                    sLabel = 'Warning : Contact Administrator - Invalid question    '
                    sWarningMsg = self.sClassName + ':' + self.sFnName + ':' + 'UnrecognizedQuestionType - Contact Administrator'
                    self.oMsgUtil.DisplayWarning(sWarningMsg)
                    bQuestionTypeGood = False
                    

                if bQuestionTypeGood == True:
                    self.question._sGrpBoxTitle_setter(sQuestionDescriptor)
                    
                    lOptions = self.GetOptionsFromXML(xNodeQuestion)
                    self.question._lsOptions_setter(lOptions)
                    self._loQuestions.append(self.question)

                
    #-----------------------------------------------

    def GetOptionsFromXML(self, xNodeQuestion):

        lOptions = []
        # get options for each question
        xOptions = self.oIOXml.GetChildren(xNodeQuestion, 'Option')

        for iIndex in range(len(xOptions)):
            
            xQuestionOption = self.oIOXml.GetNthChild(xNodeQuestion, 'Option', iIndex)
            sValue = self.oIOXml.GetDataInNode(xQuestionOption)
            lOptions.append(sValue)
            
        return lOptions
    #-----------------------------------------------
        
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

        self.CreateGroupBoxWidget()
        

        bBuildSuccess = True
        for i in range(len(self._loQuestions)):
            question = self._loQuestions[i]
            bBuildQuestion, qGrpboxWidget = question.BuildQuestion()
            if bBuildQuestion :
                self.qQuizWidgetLayout.addWidget(qGrpboxWidget)
                bBuildSuccess = bBuildSuccess * bBuildQuestion

                
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

        self._lsOptions = []
        self._lsResponses = []
        self._sGrpBoxTitle = ''

    
    # abstract properties require level of indirection
    #----------
    # _lsOptions
    #----------
    @property
    def lsOptions(self):
        return self._lsOptions
        
    @lsOptions.setter
    def lsOptions(self,x):
        self._lsOptions_setter(x)
        
    @abstractmethod
    def _lsOptions_setter(self, x):
        pass
        
    @abstractmethod
    def _lsOptions_getter(self):
        return self._lsOptions
    #----------
    
    #----------
    # _lsOptions
    #----------
    @property
    def lsResponses(self):
        return self._lsResponses
        
    @lsResponses.setter
    def lsResponses(self,x):
        self._lsResponses_setter(x)
        
    @abstractmethod
    def _lsResponses_setter(self, x):
        pass
        
    @abstractmethod
    def _lsResponses_getter(self):
        return self._lsResponses
    #----------
    
    #----------
    # _sGrpBoxTitle
    #----------
    @property
    def sGrpBoxTitle(self):
        return self._sGrpBoxTitle
    
    @sGrpBoxTitle.setter
    def sGrpBoxTitle(self, x):
        self._sGrpBoxTitle_setter(x)
        
    @abstractmethod
    def _sGrpBoxTitle_setter(self,x):
        pass
    
    @abstractmethod
    def _sGrpBoxTitle_getter(self):
        return self._sGrpBoxTitle
    #----------
    
    
    @abstractmethod        
    def BuildQuestion(self): pass
    
    @abstractmethod        
    def CaptureResponse(self): pass
    
    @abstractmethod
    def PopulateQuestionWithResponses(self, lsResponseValues): pass

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

    def GetMinMaxAttributesFromXML(self, xNodeQuestion):

        oIOXml = UtilsIOXml()
        dictModifiers = {}

        sMin = oIOXml.GetValueOfNodeAttribute(xNodeQuestion, 'min')               
        sMax = oIOXml.GetValueOfNodeAttribute(xNodeQuestion, 'max')

        dictModifiers['min'] = sMin
        dictModifiers['max'] = sMax

        return dictModifiers
    
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
    # Inputs : 
    # Outputs: exitCode - boolean describing whether function exited successfully
    #          qGrpBox  - group box widget holding radio buttons
    
    def __init__(self):
        self.sClassName = type(self).__name__

       
    def _lsOptions_setter(self, lsInput):
        self._lsOptions = lsInput
        
    def _lsOptions_getter(self):
        return self._lsOptions
        
    def _lsResponses_setter(self, lsInput):
        self._lsResponses = lsInput
        
    def _lsResponses_getter(self):
        return self._lsResponses
        
    def _sGrpBoxTitle_setter(self, sInput):
        self._sGrpBoxTitle = sInput
        
    def _sGrpBoxTitle_getter(self):
        return self._sGrpBoxTitle

    #-----------------------------------------------
    
    def BuildQuestion(self):
        self.sFnName = sys._getframe().f_code.co_name

        self.CreateGroupBox(self._sGrpBoxTitle_getter())
        
        lsStoredOptions = self._lsOptions_getter()
        length = len(lsStoredOptions)
        if length < 1 :
            self.DisplayGroupBoxEmpty()
            return False, self.qGrpBox
        
        i = 0
        while i < length:
            element1 = lsStoredOptions[i]
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
            sMsg = 'Missing radio option for: ' + self._sGrpBoxTitle_getter()

        return bSuccess, lsResponses, sMsg
    
    
    
    #-----------------------------------------------
    
    def PopulateQuestionWithResponses(self, lsValues):
        
        i = 0
        for qBtn in self.qGrpBox.findChildren(qt.QRadioButton):
            
            if lsValues[i] == 'n':
                qBtn.setChecked(False)
            else:
                if lsValues[i] == 'y':
                    qBtn.setChecked(True)
            i = i + 1
            

#========================================================================================
#                     Class CheckBoxQuestion
#========================================================================================

class CheckBoxQuestion(Question):
    # Create a group box and add check boxes based on the options provided
    # Inputs : 
    # Outputs: exitCode - boolean describing whether function exited successfully
    #          qGrpBox  - group box widget holding check boxes
    
    def __init__(self):
        self.sClassName = type(self).__name__


    def _lsOptions_setter(self, lsInput):
        self._lsOptions = lsInput
        
    def _lsOptions_getter(self):
        return self._lsOptions
        
    def _lsResponses_setter(self, lsInput):
        self._lsResponses = lsInput
        
    def _lsResponses_getter(self):
        return self._lsResponses
        
    def _sGrpBoxTitle_setter(self, sInput):
        self._sGrpBoxTitle = sInput
        
    def _sGrpBoxTitle_getter(self):
        return self._sGrpBoxTitle

    #-----------------------------------------------
       
    def BuildQuestion(self):
        self.sFnName = sys._getframe().f_code.co_name

        self.CreateGroupBox(self._sGrpBoxTitle_getter())
        
        lsStoredOptions = self._lsOptions_getter()
        length = len(lsStoredOptions)
        if length < 1 :
            self.DisplayGroupBoxEmpty()
            return False, self.qGrpBox
        
        i = 0
        while i < length:
            element1 = lsStoredOptions[i]
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
            sMsg = 'Missing check box option for: ' + self._sGrpBoxTitle_getter()

        return bSuccess, lsResponses, sMsg

    #-----------------------------------------------
    
    def PopulateQuestionWithResponses(self, lsValues):
            
        i = 0
        for qBox in self.qGrpBox.findChildren(qt.QCheckBox):
            
            if lsValues[i] == 'n':
                qBox.setChecked(False)
            else:
                if lsValues[i] == 'y':
                    qBox.setChecked(True)
            i = i + 1
        
        

#========================================================================================
#                     Class TextQuestion
#========================================================================================

class TextQuestion(Question):
    # Create a group box and add a text box that allows the user to enter text
    # Inputs : 
    # Outputs: exitCode - boolean describing whether function exited successfully
    #          qGrpBox  - group box widget holding text edit boxes
    
    def __init__(self):
        self.sClassName = type(self).__name__

        
    def _lsOptions_setter(self, lsInput):
        self._lsOptions = lsInput
        
    def _lsOptions_getter(self):
        return self._lsOptions
        
    def _lsResponses_setter(self, lsInput):
        self._lsResponses = lsInput
        
    def _lsResponses_getter(self):
        return self._lsResponses
        
    def _sGrpBoxTitle_setter(self, sInput):
        self._sGrpBoxTitle = sInput
        
    def _sGrpBoxTitle_getter(self):
        return self._sGrpBoxTitle

    #-----------------------------------------------
    
    def BuildQuestion(self):
        self.sFnName = sys._getframe().f_code.co_name

        # add grid layout to group box
        self.CreateGroupBox(self._sGrpBoxTitle_getter())
        newLayout = qt.QGridLayout()
        self.qGrpBoxLayout.addLayout(newLayout)
       
        lsStoredOptions = self._lsOptions_getter()
        length = len(lsStoredOptions)
        if length < 1 :
            self.DisplayGroupBoxEmpty()
            return False, self.qGrpBox

        i = 0
        while i < length:
            element1 = lsStoredOptions[i]
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
            sMsg = 'Missing text response for: ' + self._sGrpBoxTitle_getter()
            
        return bSuccess, lsResponses, sMsg

    #-----------------------------------------------
    
    def PopulateQuestionWithResponses(self, lsValues):
        i = 0
        for qTxt in self.qGrpBox.findChildren(qt.QLineEdit):
            
            qTxt.setText(lsValues[i])
            i = i + 1

#========================================================================================
#                     Class IntegerValueQuestion
#========================================================================================

class IntegerValueQuestion(Question):
    # Create a group box and add a line edit that allows the user to enter an integer value
    # Inputs : 
    # Outputs: exitCode - boolean describing whether function exited successfully
    #          qGrpBox  - group box widget holding the text box for integer input
    
    def __init__(self):
        self.sClassName = type(self).__name__

        self.oMsgUtil = UtilsMsgs()
        self.dictModifiers = {}
        self.sMin = ''
        self.sMax = ''
        
    def _lsOptions_setter(self, lsInput):
        self._lsOptions = lsInput
        
    def _lsOptions_getter(self):
        return self._lsOptions
        
    def _lsResponses_setter(self, lsInput):
        self._lsResponses = lsInput
        
    def _lsResponses_getter(self):
        return self._lsResponses
        
    def _sGrpBoxTitle_setter(self, sInput):
        self._sGrpBoxTitle = sInput
        
    def _sGrpBoxTitle_getter(self):
        return self._sGrpBoxTitle

    def UpdateDictionaryModifiers(self, dictionaryInput):
        self.dictModifiers = dictionaryInput
        
    #-----------------------------------------------
        
    def BuildQuestion(self):
        self.sFnName = sys._getframe().f_code.co_name

        # add grid layout to group box
        self.CreateGroupBox(self._sGrpBoxTitle_getter())
        newLayout = qt.QGridLayout()
        self.qGrpBoxLayout.addLayout(newLayout)
       
        lsStoredOptions = self._lsOptions_getter()
        length = len(lsStoredOptions)
        if length < 1 :
            self.DisplayGroupBoxEmpty()
            return False, self.qGrpBox

        i = 0
        while i < length:
            element1 = lsStoredOptions[i]
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
            sErrorMsg = 'See Administrator. Invalid range attribute in XML tag : ' + self._sGrpBoxTitle_getter()
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
                    sMsg = 'Please enter integer for: ' + self._sGrpBoxTitle_getter() + sRangeMsg
                    bSuccess = bSuccess * False
                    
            else:
                bResponseFound = False

        if bResponseFound:
            bSuccess = True
        else:
            sMsg = 'Invalid integer value response for: ' + self._sGrpBoxTitle_getter() + sRangeMsg

                    
        return bSuccess, lsResponses, sMsg
    
    #-----------------------------------------------
    
    def PopulateQuestionWithResponses(self, lsValues):

        i = 0
        for qTxt in self.qGrpBox.findChildren(qt.QLineEdit):
            
            qTxt.setText(lsValues[i])
            i = i + 1

#========================================================================================
#                     Class FloatValueQuestion
#========================================================================================

class FloatValueQuestion(Question):
    # Create a group box and add a line edit that allows the user to enter a float value
    # Outputs: exitCode - boolean describing whether function exited successfully
    #          qGrpBox  - group box widget holding the text box for float input
    
    def __init__(self):
        self.sClassName = type(self).__name__

        self.oMsgUtil = UtilsMsgs()
        self.dictModifiers = {}
        self.sMin = ''
        self.sMax = ''

    def _lsOptions_setter(self, lsInput):
        self._lsOptions = lsInput
        
    def _lsOptions_getter(self):
        return self._lsOptions
        
    def _lsResponses_setter(self, lsInput):
        self._lsResponses = lsInput
        
    def _lsResponses_getter(self):
        return self._lsResponses
        
    def _sGrpBoxTitle_setter(self, sInput):
        self._sGrpBoxTitle = sInput
        
    def _sGrpBoxTitle_getter(self):
        return self._sGrpBoxTitle

    def UpdateDictionaryModifiers(self, dictionaryInput):
        self.dictModifiers = dictionaryInput
        
    #-----------------------------------------------

    def BuildQuestion(self):
        self.sFnName = sys._getframe().f_code.co_name

        # add grid layout to group box
        self.CreateGroupBox(self._sGrpBoxTitle_getter())
        newLayout = qt.QGridLayout()
        self.qGrpBoxLayout.addLayout(newLayout)
       
        lsStoredOptions = self._lsOptions_getter()
        length = len(lsStoredOptions)
        if length < 1 :
            self.DisplayGroupBoxEmpty()
            return False, self.qGrpBox

        i = 0
        while i < length:
            element1 = lsStoredOptions[i]

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
            sErrorMsg = 'See Administrator. Invalid range attribute in XML tag : ' + self._sGrpBoxTitle_getter()
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
                    sMsg = 'Please enter decimal value for: ' + self._sGrpBoxTitle_getter() + sRangeMsg
                    bSuccess = bSuccess * False
            else:
                bResponseFound = False
    


        if bResponseFound:
            bSuccess = True
        else:
            sMsg = 'Invalid decimal value response for: ' + self._sGrpBoxTitle_getter() + sRangeMsg


        return bSuccess, lsResponses, sMsg

    #-----------------------------------------------
    
    def PopulateQuestionWithResponses(self, lsValues):

        i = 0
        for qTxt in self.qGrpBox.findChildren(qt.QLineEdit):
            
            qTxt.setText(lsValues[i])
            i = i + 1

#========================================================================================
#                     Class InfoBox
#========================================================================================

class InfoBox(Question):
    # Create a group box and add a label holding information
    # There are no responses from the user to catch
    # Inputs :
    # Outputs: exitCode - boolean describing whether function exited successfully
    #          qGrpBox  - group box widget holding text edit boxes
    
    def __init__(self):
        self.sClassName = type(self).__name__

        
    def _lsOptions_setter(self, lsInput):
        self._lsOptions = lsInput
        
    def _lsOptions_getter(self):
        return self._lsOptions
        
    def _lsResponses_setter(self, lsInput):
        self._lsResponses = lsInput
        
    def _lsResponses_getter(self):
        return self._lsResponses
        
    def _sGrpBoxTitle_setter(self, sInput):
        self._sGrpBoxTitle = sInput
        
    def _sGrpBoxTitle_getter(self):
        return self._sGrpBoxTitle

    #-----------------------------------------------

    def BuildQuestion(self):
        self.sFnName = sys._getframe().f_code.co_name

        # add grid layout to group box
        self.CreateGroupBox(self._sGrpBoxTitle_getter())
        newLayout = qt.QGridLayout()
        self.qGrpBoxLayout.addLayout(newLayout)
       
        lsStoredOptions = self._lsOptions_getter()
        length = len(lsStoredOptions)
        if length < 1 :
            self.DisplayGroupBoxEmpty()
            return False, self.qGrpBox

        i = 0
        while i < length:
            element1 = lsStoredOptions[i]
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
        
    #-----------------------------------------------
    
    def PopulateQuestionWithResponses(self, lsValues):
        # there is nothing to populate for info box type questions
        pass
    
    

    