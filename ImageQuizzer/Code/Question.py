from abc import ABC, abstractmethod, abstractproperty

import PythonQt
import os
import vtk, qt, ctk, slicer
import sys
import warnings
import traceback


from Utilities.UtilsMsgs import *
from Utilities.UtilsIOXml import *



#========================================================================================
#                     Class Question Set
#========================================================================================

class QuestionSet():
    """ Class to hold array of all questions that were built into group boxes on the form
    """
    
    def __init__(self, oFilesIO):
        self.sClassName = type(self).__name__
        self.id = ''
        self.descriptor = ''
        self._bAllowMultipleResponse = False
        
        self._loQuestions = []
        
        self.oIOXml = UtilsIOXml()
        self.oMsgUtil = UtilsMsgs()
        self.oFilesIO = oFilesIO
        
    #----------
    def SetQuestionList(self, loQuestionsInput):
        self._loQuestions = loQuestionsInput

    #----------
    def GetQuestionList(self):
        return self._loQuestions
    
    #----------
    #----------
        
    #-----------------------------------------------
        
    def ExtractQuestionsFromXML(self, xNodeQuestionSet):
        sFnName = sys._getframe().f_code.co_name
        
        
        sNodeName = self.oIOXml.GetElementNodeName(xNodeQuestionSet)
        if not (sNodeName == "QuestionSet"):
            raise Exception("Invalid XML node. Expecting 'QuestionSet', node name was: %s" % sNodeName)
        else:
            # for each child named 'Question' extract labels and options
            iNumQuestions = self.oIOXml.GetNumChildrenByName(xNodeQuestionSet, "Question")
            
            self.id = self.oIOXml.GetValueOfNodeAttribute(xNodeQuestionSet, 'ID')
            self.descriptor = self.oIOXml.GetValueOfNodeAttribute(xNodeQuestionSet, 'Descriptor')
            
            
            lxQuestions = self.oIOXml.GetChildren(xNodeQuestionSet, 'Question')
            
            for xNodeQuestion in lxQuestions:

                dictModifiers = {}

                sQuestionType = self.oIOXml.GetValueOfNodeAttribute(xNodeQuestion, 'Type')
                sQuestionDescriptor = self.oIOXml.GetValueOfNodeAttribute(xNodeQuestion, 'Descriptor')
                sGroupBoxLayout = self.oIOXml.GetValueOfNodeAttribute(xNodeQuestion, 'GroupLayout')


                bQuestionTypeGood = True

                if (sQuestionType == 'Radio'):
                    oQuestion = RadioQuestion()

                elif (sQuestionType == 'CheckBox'):
                    oQuestion = CheckBoxQuestion()

                elif (sQuestionType == 'Text'):
                    oQuestion = TextQuestion()

                elif (sQuestionType == 'IntegerValue'):
                    oQuestion = IntegerValueQuestion()
                    dictModifiers = oQuestion.GetMinMaxAttributesFromXML(xNodeQuestion)
                    oQuestion.UpdateDictionaryModifiers(dictModifiers)

                elif (sQuestionType == 'FloatValue'):
                    oQuestion = FloatValueQuestion()
                    dictModifiers = oQuestion.GetMinMaxAttributesFromXML(xNodeQuestion)
                    oQuestion.UpdateDictionaryModifiers(dictModifiers)

                elif (sQuestionType == 'InfoBox'):
                    oQuestion = InfoBox()

                elif (sQuestionType == 'Button'):
                    oQuestion = Button()
                    
                elif (sQuestionType == 'Picture'):
                    oQuestion = Picture()
                    
                else:
                    sLabel = 'Warning : Contact Administrator - Invalid question    '
                    sWarningMsg = self.sClassName + ':' + sFnName + '\nType = ' + sQuestionType + '    ...UnrecognizedQuestionType'\
                                + '\nRemaining Questions will be displayed \n\n - Contact Administrator'
                    self.oMsgUtil.DisplayWarning(sWarningMsg)
                    bQuestionTypeGood = False
                    

                if bQuestionTypeGood == True:
                    oQuestion._sGrpBoxTitle_setter(sQuestionDescriptor)
                    oQuestion._sGrpBoxLayout_setter(sGroupBoxLayout)
                    oQuestion._oFilesIO_setter(self.oFilesIO)
                    
                    lOptions = self.GetOptionsFromXML(xNodeQuestion)
                    oQuestion._lsOptions_setter(lOptions)
                    self._loQuestions.append(oQuestion)

                
    #-----------------------------------------------

    def GetOptionsFromXML(self, xNodeQuestion):

        lOptions = []

        # get options for each question
        lxOptions = self.oIOXml.GetChildren(xNodeQuestion, 'Option')

        for iElem in range(len(lxOptions)):
            
            xNodeOption = self.oIOXml.GetNthChild(xNodeQuestion, 'Option', iElem)
            sValue = self.oIOXml.GetDataInNode(xNodeOption)
            
            lOptions.append(sValue)

        return lOptions
    
    #-----------------------------------------------
        
    #-----------------------------------------------
        
    def BuildQuestionSetForm(self):
        # for each item in the list of Questions
        #    - create the appropriate question widget based on the 
        #        the type of question object stored in the list
        #    - add to layout
        sFnName = sys._getframe().f_code.co_name

        self.CreateGroupBoxWidget()
        

        bBuildSuccess = True
        for i in range(len(self._loQuestions)):
            question = self._loQuestions[i]
            bBuildQuestion, qGrpboxWidget = question.BuildQuestion()
            if bBuildQuestion :
                self.qQuizWidgetLayout.addSpacing(5)
                self.qQuizWidgetLayout.addWidget(qGrpboxWidget)
                bBuildSuccess = bBuildSuccess * bBuildQuestion

                
        return bBuildSuccess, self.qQuizWidget

    #-----------------------------------------------
    
    def CreateGroupBoxWidget(self):
        # create group box widget to which each subclass can add elements
        self.qQuizWidget = qt.QWidget()
        self.qQuizWidgetLayout = qt.QVBoxLayout()
        self.qQuizWidget.setLayout(self.qQuizWidgetLayout)
        self.qQuizTitle = qt.QLabel(self.id + '     ' + self.descriptor)
        self.qQuizTitle.setStyleSheet("QLabel{ font: bold}")
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
        self._sGrpBoxTitle = ''
        self._sGrpBoxLayout = ''
        self._oFilesIO = None

    
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
    
    
    #----------
    # _sGrpBoxLayout
    #----------
    @property
    def sGrpBoxLayout(self):
        return self._sGrpBoxLayout
    
    @sGrpBoxLayout.setter
    def sGrpBoxLayout(self, x):
        self._sGrpBoxLayout_setter(x)
        
    @abstractmethod
    def _sGrpBoxLayout_setter(self,x):
        pass
    
    @abstractmethod
    def _sGrpBoxLayout_getter(self):
        return self._sGrpBoxLayout
    #----------
    
    
    #----------
    # _oFilesIO
    #----------
    @property
    def oFilesIO(self):
        return self._oFilesIO
    
    @oFilesIO.setter
    def oFilesIO(self, x):
        self._oFilesIO_setter(x)
        
    @abstractmethod
    def _oFilesIO_setter(self,x):
        pass
    
    @abstractmethod
    def _oFilesIO_getter(self):
        return self._oFilesIO
    #----------

    
    #----------
    @abstractmethod        
    def BuildQuestion(self): pass
    
    @abstractmethod        
    def CaptureResponse(self): pass
    
    @abstractmethod
    def PopulateQuestionWithResponses(self, lsResponseValues): pass

    #-----------------------------------------------
    
    def CreateGroupBox(self, sTitle, sGrpBoxLayout='Vertical'):
        # create group box widget to which each subclass can add elements
        self.qGrpBox = qt.QGroupBox()
        self.qGrpBox.setTitle(sTitle)
        if sGrpBoxLayout == 'Horizontal':
            self.qGrpBoxLayout = qt.QHBoxLayout()
        else:
            self.qGrpBoxLayout = qt.QVBoxLayout()
        self.qGrpBox.setLayout(self.qGrpBoxLayout)
        self.qGrpBox.setStyleSheet("QGroupBox { \
            margin: 10px; border: 1px solid gray;\
            border-top-style:solid; border-bottom-style:none;\
            border-left-style:solid; border-right-style:none; }")
        
        return self.qGrpBox

    #-----------------------------------------------

    def DisplayGroupBoxEmpty(self):
        # check if group box was already created
        
        sLabel = 'Warning : No options were given. Group Box is empty - Contact Administrator'
        sWarningMsg = self.sClassName + ':' + self.sFnName + ':' + 'NoOptionsAvailable - Contact Administrator'
        qLabel = qt.QLabel(sLabel)
        qLabel.setWordWrap(True)
        self.qGrpBoxLayout.addWidget(qLabel)
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

        sMin = oIOXml.GetValueOfNodeAttribute(xNodeQuestion, 'Min')               
        sMax = oIOXml.GetValueOfNodeAttribute(xNodeQuestion, 'Max')

        dictModifiers['Min'] = sMin
        dictModifiers['Max'] = sMax

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
        
    def _sGrpBoxTitle_setter(self, sInput):
        self._sGrpBoxTitle = sInput
        
    def _sGrpBoxTitle_getter(self):
        return self._sGrpBoxTitle

    def _sGrpBoxLayout_setter(self, sInput):
        self._sGrpBoxLayout = sInput
        
    def _sGrpBoxLayout_getter(self):
        return self._sGrpBoxLayout

    def _oFilesIO_setter(self, sInput):
        self._oFilesIO = sInput
        
    def _oFilesIO_getter(self):
        return self._oFilesIO

    #-----------------------------------------------
    
    def BuildQuestion(self):
        self.sFnName = sys._getframe().f_code.co_name

        self.CreateGroupBox(self._sGrpBoxTitle_getter(), self._sGrpBoxLayout_getter())
        
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
                lsResponses.append('Y')
                bResponseFound = True
            else:
                lsResponses.append('N')

        if bResponseFound:
            bSuccess = True
        else:
            sMsg = 'Missing radio option for: ' + self._sGrpBoxTitle_getter()

        return bSuccess, lsResponses, sMsg
    
    
    
    #-----------------------------------------------
    
    def PopulateQuestionWithResponses(self, lsValues):
        
        if len(lsValues) > 0:
            i = 0
            for qBtn in self.qGrpBox.findChildren(qt.QRadioButton):
                
                if lsValues[i] == 'N':
                    qBtn.setChecked(False)
                else:
                    if lsValues[i] == 'Y':
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
        
    def _sGrpBoxTitle_setter(self, sInput):
        self._sGrpBoxTitle = sInput
        
    def _sGrpBoxTitle_getter(self):
        return self._sGrpBoxTitle

    def _sGrpBoxLayout_setter(self, sInput):
        self._sGrpBoxLayout = sInput
        
    def _sGrpBoxLayout_getter(self):
        return self._sGrpBoxLayout

    def _oFilesIO_setter(self, sInput):
        self._oFilesIO = sInput
        
    def _oFilesIO_getter(self):
        return self._oFilesIO

    #-----------------------------------------------
       
    def BuildQuestion(self):
        self.sFnName = sys._getframe().f_code.co_name

        self.CreateGroupBox(self._sGrpBoxTitle_getter(), self._sGrpBoxLayout_getter())
        
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
                lsResponses.append('Y')
                bResponseFound = True
            else:
                lsResponses.append('N')
                
        if bResponseFound:
            bSuccess = True
        else:
            sMsg = 'Missing check box option for: ' + self._sGrpBoxTitle_getter()

        return bSuccess, lsResponses, sMsg

    #-----------------------------------------------
    
    def PopulateQuestionWithResponses(self, lsValues):
            
        if len(lsValues) > 0:
            i = 0
            for qBox in self.qGrpBox.findChildren(qt.QCheckBox):
                
                if lsValues[i] == 'N' or lsValues == '':
                    qBox.setChecked(False)
                else:
                    if lsValues[i] == 'Y':
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
        
    def _sGrpBoxTitle_setter(self, sInput):
        self._sGrpBoxTitle = sInput
        
    def _sGrpBoxTitle_getter(self):
        return self._sGrpBoxTitle

    def _sGrpBoxLayout_setter(self, sInput):
        self._sGrpBoxLayout = sInput
        
    def _sGrpBoxLayout_getter(self):
        return self._sGrpBoxLayout

    def _oFilesIO_setter(self, sInput):
        self._oFilesIO = sInput
        
    def _oFilesIO_getter(self):
        return self._oFilesIO

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
            qLabel.setWordWrap(True)
            newLayout.addWidget(qLabel, i, 0)
            newLayout.addWidget(qLineEdit, i, 1)
            i = i + 1

        return True, self.qGrpBox
        
    #-----------------------------------------------
    
    def CaptureResponse(self):
        self.sFnName = sys._getframe().f_code.co_name

        lsResponses = []
        bSuccess = False
        bResponseFound = True
        sMsg = ''
        
        for qTextBox in self.qGrpBox.findChildren(qt.QLineEdit):
            sText = qTextBox.text
#             print(sText)
            if not sText =='':
                bResponseFound = bResponseFound * True
                lsResponses.append(qTextBox.text)
            else:
                lsResponses.append('')
                bResponseFound = bResponseFound * False

        if bResponseFound:
            bSuccess = True
        else:
            sMsg = 'Missing text response for: ' + self._sGrpBoxTitle_getter()
            
        return bSuccess, lsResponses, sMsg

    #-----------------------------------------------
    
    def PopulateQuestionWithResponses(self, lsValues):

        if len(lsValues) > 0:
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
        
    def _sGrpBoxTitle_setter(self, sInput):
        self._sGrpBoxTitle = sInput
        
    def _sGrpBoxTitle_getter(self):
        return self._sGrpBoxTitle

    def _sGrpBoxLayout_setter(self, sInput):
        self._sGrpBoxLayout = sInput
        
    def _sGrpBoxLayout_getter(self):
        return self._sGrpBoxLayout

    def UpdateDictionaryModifiers(self, dictionaryInput):
        self.dictModifiers = dictionaryInput

    def _oFilesIO_setter(self, sInput):
        self._oFilesIO = sInput
        
    def _oFilesIO_getter(self):
        return self._oFilesIO
        
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
            self.sMin = self.dictModifiers.get('Min')
            self.sMax = self.dictModifiers.get('Max')
            
            sRangeMsg = self.CreateRangePrompt()
            sPlaceholderMsg = 'Enter integer value' + sRangeMsg

            qLineEdit = qt.QLineEdit()
            qLineEdit.setPlaceholderText(sPlaceholderMsg)

            
            qLabel = qt.QLabel(element1)
            qLabel.setWordWrap(True)
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
        bResponseFound = True
        
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
                        bResponseFound = bResponseFound * True

                    else:
                        bResponseFound = bResponseFound * False
                        raise ValueError()
                        
                except ValueError:
                    bResponseFound = bResponseFound * False
                    lsResponses.append('')  # return empty string if the field if invalid
                    
            else:
                bResponseFound = bResponseFound * False
                lsResponses.append('')

        if bResponseFound:
            bSuccess = True
        else:
            sMsg = 'Invalid integer value response for: ' + self._sGrpBoxTitle_getter() + sRangeMsg

                    
        return bSuccess, lsResponses, sMsg
    
    #-----------------------------------------------
    
    def PopulateQuestionWithResponses(self, lsValues):

        if len(lsValues) > 0:
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
        
    def _sGrpBoxTitle_setter(self, sInput):
        self._sGrpBoxTitle = sInput
        
    def _sGrpBoxTitle_getter(self):
        return self._sGrpBoxTitle

    def _sGrpBoxLayout_setter(self, sInput):
        self._sGrpBoxLayout = sInput
        
    def _sGrpBoxLayout_getter(self):
        return self._sGrpBoxLayout

    def UpdateDictionaryModifiers(self, dictionaryInput):
        self.dictModifiers = dictionaryInput

    def _oFilesIO_setter(self, sInput):
        self._oFilesIO = sInput
        
    def _oFilesIO_getter(self):
        return self._oFilesIO
        
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

            self.sMin = self.dictModifiers.get('Min')
            self.sMax = self.dictModifiers.get('Max')
            

            sRangeMsg = self.CreateRangePrompt()
            sPlaceholderMsg = 'Enter decimal value' + sRangeMsg

            qLineEdit = qt.QLineEdit()
            qLineEdit.setPlaceholderText(sPlaceholderMsg)
            
            
            qLabel = qt.QLabel(element1)
            qLabel.setWordWrap(True)
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
        bResponseFound = True
        
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
                        bResponseFound = bResponseFound * True

                    else:
                        bResponseFound = bResponseFound * False
                        raise ValueError()
                        
                except ValueError:
                    bResponseFound = bResponseFound * False
                    lsResponses.append('')  # return empty string if the field if invalid

            else:
                bResponseFound = bResponseFound * False
                lsResponses.append('')
    


        if bResponseFound:
            bSuccess = True
        else:
            sMsg = 'Invalid decimal value response for: ' + self._sGrpBoxTitle_getter() + sRangeMsg


        return bSuccess, lsResponses, sMsg

    #-----------------------------------------------
    
    def PopulateQuestionWithResponses(self, lsValues):

        if len(lsValues) > 0:
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
    #          qGrpBox  - group box widget holding information box
    
    def __init__(self):
        self.sClassName = type(self).__name__

        
    def _lsOptions_setter(self, lsInput):
        self._lsOptions = lsInput
        
    def _lsOptions_getter(self):
        return self._lsOptions
        
    def _sGrpBoxTitle_setter(self, sInput):
        self._sGrpBoxTitle = sInput
        
    def _sGrpBoxTitle_getter(self):
        return self._sGrpBoxTitle

    def _sGrpBoxLayout_setter(self, sInput):
        self._sGrpBoxLayout = sInput
        
    def _sGrpBoxLayout_getter(self):
        return self._sGrpBoxLayout

    def _oFilesIO_setter(self, sInput):
        self._oFilesIO = sInput
        
    def _oFilesIO_getter(self):
        return self._oFilesIO

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
            qLabel.setWordWrap(True)
            newLayout.addWidget(qLabel, i, 0)
            i = i + 1

        return True, self.qGrpBox

    #-----------------------------------------------
    
    def CaptureResponse(self):
        self.sFnName = sys._getframe().f_code.co_name

        bSuccess = True
        sMsg = ''
 
        lsResponses = []
        
        # set response for each option to null quotes
        #     each option needs a response for the check on whether 
        #     the question set was answered completely or partially
        lsStoredOptions = self._lsOptions_getter()
        for x in range( len(lsStoredOptions) ):
            lsResponses.append('')
                
        
        return bSuccess, lsResponses, sMsg
        
    #-----------------------------------------------
    
    def PopulateQuestionWithResponses(self, lsValues):
        # there is nothing to populate for info box type questions
        pass
    
#========================================================================================
#                     Class Button
#========================================================================================

class Button(Question):
    # Create a group box and add a button that will run an external script
    # There are no responses from the user to catch
    # Inputs :
    # Outputs: exitCode - boolean describing whether function exited successfully
    #          qGrpBox  - group box widget holding the button
    
    def __init__(self):
        self.sClassName = type(self).__name__

        self.oMsgUtil = UtilsMsgs()

        
    def _lsOptions_setter(self, lsInput):
        self._lsOptions = lsInput
        
    def _lsOptions_getter(self):
        return self._lsOptions
        
    def _sGrpBoxTitle_setter(self, sInput):
        self._sGrpBoxTitle = sInput
        
    def _sGrpBoxTitle_getter(self):
        return self._sGrpBoxTitle

    def _sGrpBoxLayout_setter(self, sInput):
        self._sGrpBoxLayout = sInput
        
    def _sGrpBoxLayout_getter(self):
        return self._sGrpBoxLayout

    def _oFilesIO_setter(self, sInput):
        self._oFilesIO = sInput
        
    def _oFilesIO_getter(self):
        return self._oFilesIO

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

        oFilesIO = self._oFilesIO_getter()
        self.dictQButtons = {}
        i = 0
        while i < length:
            element1 = os.path.join(oFilesIO.GetScriptsDir(),lsStoredOptions[i])
            head, tail = os.path.split(element1)
            qButton = qt.QPushButton(str(i+1)+'-'+tail)
            qButton.setStyleSheet("QPushButton{ background-color: rgb(173,220,237); color: black }")
            newLayout.addWidget(qButton, i, 0)
            self.dictQButtons[element1]=qButton
            i = i + 1

        for button in self.dictQButtons:
            self.dictQButtons[button].connect('clicked(bool)',lambda _, b=button: self.onQButtonClicked(b))
                                         
        return True, self.qGrpBox

    #-----------------------------------------------

    def onQButtonClicked(self,  sScript):
        
        try:
            qBtn = self.dictQButtons[sScript]
            # globals() runs the executable in the global namespace
            #    passes global dictionary of the main context to exec()
            exec(open(sScript).read(),globals())

            qBtn.setText(qBtn.text+'-Done')
            qBtn.setStyleSheet("QPushButton{ background-color: rgb(0,179,246); color: black }")

        except:
            tb = traceback.format_exc()
            qBtn.setStyleSheet("QPushButton{ background-color: rgb(245,159,159); color: black }")
            sMsg = "onButtonClicked: Error running script. \nContact administrator\n" + sScript \
                   + "\n\n" + tb 
            self.oMsgUtil.DisplayWarning(sMsg)

        
    #-----------------------------------------------
    
    def CaptureResponse(self):

        self.sFnName = sys._getframe().f_code.co_name

        lsResponses = []
        bSuccess = False
        bResponseFound = True
        sMsg = ''
        
        for qBtn in self.qGrpBox.findChildren(qt.QPushButton):
            if 'Done' in qBtn.text:
                bResponseFound = bResponseFound * True
                lsResponses.append(qBtn.text)
            else:
                bResponseFound = bResponseFound * False
                lsResponses.append('')
                

        if bResponseFound:
            bSuccess = True
        else:
            sMsg = 'Script run incomplete for: ' + self._sGrpBoxTitle_getter()
            
        return bSuccess, lsResponses, sMsg
            
        
    #-----------------------------------------------
    
    def PopulateQuestionWithResponses(self, lsValues):
        # there is nothing to populate for button type questions
        pass
    
#========================================================================================
#                     Class Picture
#========================================================================================

class Picture(Question):
    # Create a group box and add a picture
    # There are no responses from the user to catch
    # Inputs :
    # Outputs: exitCode - boolean describing whether function exited successfully
    #          qGrpBox  - group box widget holding information box
    
    def __init__(self):
        self.sClassName = type(self).__name__

        
    def _lsOptions_setter(self, lsInput):
        self._lsOptions = lsInput
        
    def _lsOptions_getter(self):
        return self._lsOptions
        
    def _sGrpBoxTitle_setter(self, sInput):
        self._sGrpBoxTitle = sInput
        
    def _sGrpBoxTitle_getter(self):
        return self._sGrpBoxTitle

    def _sGrpBoxLayout_setter(self, sInput):
        self._sGrpBoxLayout = sInput
        
    def _sGrpBoxLayout_getter(self):
        return self._sGrpBoxLayout

    def _oFilesIO_setter(self, sInput):
        self._oFilesIO = sInput
        
    def _oFilesIO_getter(self):
        return self._oFilesIO

    #-----------------------------------------------

    def BuildQuestion(self):
        self.sFnName = sys._getframe().f_code.co_name

        self.CreateGroupBox(self._sGrpBoxTitle_getter(), self._sGrpBoxLayout_getter())
        
        lsStoredOptions = self._lsOptions_getter()
        length = len(lsStoredOptions)
        if length < 1 :
            self.DisplayGroupBoxEmpty()
            return False, self.qGrpBox


        oFilesIO = self._oFilesIO_getter()
        i = 0
        while i < length:
            qLabel = qt.QLabel(self)

            element1 = os.path.join(oFilesIO.GetXmlQuizDir(),lsStoredOptions[i])

            qPixmap = qt.QPixmap(element1)
            qLabel.setPixmap(qPixmap)
            self.qGrpBoxLayout.addWidget(qLabel)
            i = i + 1

        return True, self.qGrpBox

    #-----------------------------------------------
    
    def CaptureResponse(self):
        self.sFnName = sys._getframe().f_code.co_name

        bSuccess = True
        sMsg = ''
 
        lsResponses = []
        
        # set response for each option to null quotes
        #     each option needs a response for the check on whether 
        #     the question set was answered completely or partially
        lsStoredOptions = self._lsOptions_getter()
        for x in range( len(lsStoredOptions) ):
            lsResponses.append('')
                
        
        return bSuccess, lsResponses, sMsg
        
    #-----------------------------------------------
    
    def PopulateQuestionWithResponses(self, lsValues):
        # there is nothing to populate for info box type questions
        pass
    

    