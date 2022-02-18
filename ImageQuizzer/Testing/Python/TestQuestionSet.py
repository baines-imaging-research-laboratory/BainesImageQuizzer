import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from Question import *
from TestingStatus import *
import sys


##########################################################################
#
# TestQuestionSet
#
##########################################################################

class TestQuestionSet(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    #------------------------------------------- 

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Test QuestionSet and Question classes" # TODO make this more human readable by adding spaces
        self.parent.categories = ["Baines Custom Modules.Testing_ImageQuizzer"]
        self.parent.dependencies = []
        self.parent.contributors = ["Carol Johnson (Baines Imaging Research Laboratories)"] 
        self.parent.helpText = """
        This tests the QuestionSet class as well as the types of Questions that can be created.
        """
        self.parent.helpText += self.getDefaultModuleDocumentationLink()
        self.parent.acknowledgementText = """
        This file was originally developed by Carol Johnson of the Baines Imaging Research Laboratories, 
        under the supervision of Dr. Aaron Ward
        """ 
        
##########################################################################
#
# TestQuestionSet_ModuleWidget
#
##########################################################################

class TestQuestionSetWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    #------------------------------------------- 

    def setup(self):
        self.developerMode = True
        ScriptedLoadableModuleWidget.setup(self)
        # Instantiate and connect widgets ...

        # Start test button
        startTestButton = qt.QPushButton("Start Tests Question Class")
        startTestButton.toolTip = "start unit tests for Question class."
#         self.testFormLayout.addWidget(startTestButton)
#         self.layout.addWidget(startTestButton)
#         startTestButton.connect('clicked(bool)', self.onStartTestButtonClicked)

        # Collapsible button
        testQuestionCollapsibleButton = ctk.ctkCollapsibleButton()
        testQuestionCollapsibleButton.text = "Testing Question Layout"
        self.layout.addWidget(testQuestionCollapsibleButton)
        
        
        
        # Collapsible button
        testQuestionSetCollapsibleButton = ctk.ctkCollapsibleButton()
        testQuestionSetCollapsibleButton.text = "Testing Question Set Layout"
        self.layout.addWidget(testQuestionSetCollapsibleButton)
        
        # Layout within the collapsible buttons
        self.groupsLayout = qt.QFormLayout(testQuestionCollapsibleButton)
        self.questionSetLayout = qt.QFormLayout(testQuestionSetCollapsibleButton)

        # Add vertical spacer
        self.layout.addStretch(1)

        
##########################################################################
#
# TestQuestionSet_ModuleLogic
#
##########################################################################

class TestQuestionSetLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget
    """

    #------------------------------------------- 

    def __init__(self):
        ScriptedLoadableModuleLogic.__init__(self)
        self.sClassName = type(self).__name__
        print("\n************ Unittesting for class QuestionSet ************\n")
        self.questionSetStatus = TestingStatus()


##########################################################################
#
# TestQuestionSet_ModuleTest
#
##########################################################################

class TestQuestionSetTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    #------------------------------------------- 

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear(0)
        self.sClassName = type(self).__name__
        self.lsClassNames = ['RadioQuestion', 'CheckBoxQuestion','TextQuestion', 'IntegerValueQuestion', 'FloatValueQuestion', 'InfoBox', 'InvalidType']

    #------------------------------------------- 

    def runTest(self):
        self.setUp()
        logic = TestQuestionSetLogic()

        tupResults = []

        tupResults.append(self.test_NoErrors_BuildQuestionWidget())
        tupResults.append(self.test_NoErrors_RadioButtons())
        tupResults.append(self.test_NoErrors_CheckBoxes())
        tupResults.append(self.test_NoErrors_TextQuestion())
        tupResults.append(self.test_NoErrors_InfoBox())
        tupResults.append(self.test_NoOptionsWarning())
#         tupResults.append(self.test_NoErrors_QuestionSetTest())
#         tupResults.append(self.test_Error_QuestionSetTest())
        tupResults.append(self.test_CaptureResponse_RadioButtons())
        tupResults.append(self.test_CaptureResponse_CheckBoxes())
        tupResults.append(self.test_CaptureResponse_Text())
        tupResults.append(self.test_CaptureResponse_IntegerValue())
        tupResults.append(self.test_CaptureResponse_FloatValue())

        
        logic.questionSetStatus.DisplayTestResults(tupResults)
 
    #------------------------------------------- 

    def test_NoErrors_BuildQuestionWidget(self):
        """ Test for each question type with no errors encountered
        """
        fnName = sys._getframe().f_code.co_name

        # initialize
        lsOptions = ['Opt1','Opt2']
        sGroupTitle = 'Group Title'
        oQuestion = None
        bTestResultTF = False
        
        dictModifiers = {}
        
        i = 0
        while i < len(self.lsClassNames):
            if self.lsClassNames[i] == 'RadioQuestion':
                oQuestion = RadioQuestion()
            elif self.lsClassNames[i] == 'CheckBoxQuestion':
                oQuestion = CheckBoxQuestion()
            elif self.lsClassNames[i] == 'TextQuestion':
                oQuestion = TextQuestion()
            elif self.lsClassNames[i] == 'IntegerValueQuestion':
                oQuestion = IntegerValueQuestion()
                oQuestion.UpdateDictionaryModifiers(dictModifiers)
            elif self.lsClassNames[i] == 'FloatValueQuestion':
                oQuestion = FloatValueQuestion()
                oQuestion.UpdateDictionaryModifiers(dictModifiers)
            elif self.lsClassNames[i] == 'InfoBox':
                oQuestion = InfoBox()
            else:
#  TODO ??               oQuestion = LabelWarningBox('Invalid question type', 'WARNING- See administrator')
                oQuestion = None
                if (self.lsClassNames[i] == 'InvalidType'):
                    # If here, the test was successful. We specifically tried to trap the 'InvalidType'
                    bTestResultTF = True
                else:
                    # If here, test failed. The class did not get picked up in the valid types above
                    sMsg = 'Test for unknown class. Test passes if following string = InvalidType ----->\n ----> UNKNOWN CLASS: "'+ self.lsClassNames[i] + '"' 
                    print(sMsg)
                    bTestResultTF = False
                    break
                
            if oQuestion != None:
                # Question type was constructed - try to create a widget
                sQuestionDescriptor = sGroupTitle + '...' + self.lsClassNames[i]
                oQuestion._sGrpBoxTitle_setter(sQuestionDescriptor)
                
                oQuestion._lsOptions_setter(lsOptions)

                
                bTestResult, qWidgetBox = oQuestion.BuildQuestion()
                slicer.modules.TestQuestionSetWidget.groupsLayout.addWidget(qWidgetBox)
                bTestResultTF = True

            i = i + 1
            
        tupResult = fnName, bTestResultTF
        return tupResult
        
    #-----------------------------------------------

    def test_NoErrors_RadioButtons(self):
        """ Class is called with no errors encountered
        """
        fnName = sys._getframe().f_code.co_name
 
        lsOptions = ['Injury','Recurrence']
        sGroupTitle = 'Assessment'
        bTestResult = False
         
        oQuestion = RadioQuestion()
        
        sQuestionDescriptor = sGroupTitle + ' ...Test No Errors for Radio Buttons'
        oQuestion._sGrpBoxTitle_setter(sQuestionDescriptor)
        oQuestion._lsOptions_setter(lsOptions)

        bTestResult, qGrpBox = oQuestion.BuildQuestion()
        slicer.modules.TestQuestionSetWidget.groupsLayout.addWidget(qGrpBox)
         
        tupResult = fnName, bTestResult
        return tupResult
 
    #-----------------------------------------------
 
    def test_NoErrors_CheckBoxes(self):
        """ Class is called with no errors encountered
        """
        fnName = sys._getframe().f_code.co_name
 
        sGroupTitle = 'High Risk Factors'
        lsOptions = ['Enlarging Opacity','Bulging Margin', 'Sequential Enlargement']
        bTestResult = False
         
        oQuestion = CheckBoxQuestion()
        sQuestionDescriptor = sGroupTitle + ' ...Test No Errors for Check Boxes'
        oQuestion._sGrpBoxTitle_setter(sQuestionDescriptor)
        oQuestion._lsOptions_setter(lsOptions)
        
        bTestResult, qGrpBox = oQuestion.BuildQuestion()
        slicer.modules.TestQuestionSetWidget.groupsLayout.addWidget(qGrpBox)
         
        tupResult = fnName, bTestResult
        return tupResult
     
    #-----------------------------------------------
 
    def test_NoErrors_TextQuestion(self):
        """ Class is called with no errors encountered
        """
        fnName = sys._getframe().f_code.co_name
 
        sGroupTitle = 'Physician Notes'
        lsOptions = ['Enter patient observations:','Describe next steps:']
        bTestResult = False
         
        oQuestion = TextQuestion()
        sQuestionDescriptor = sGroupTitle + ' ...Test No Errors for Line Edits'
        oQuestion._sGrpBoxTitle_setter(sQuestionDescriptor)
        oQuestion._lsOptions_setter(lsOptions)
        
        bTestResult, qGrpBox = oQuestion.BuildQuestion()
        slicer.modules.TestQuestionSetWidget.groupsLayout.addWidget(qGrpBox)
         
        tupResult = fnName, bTestResult
        return tupResult
     
    #-----------------------------------------------
 
    def test_NoErrors_InfoBox(self):
        """ Class is called with no errors encountered
        """
        fnName = sys._getframe().f_code.co_name
 
        sGroupTitle = 'Welcome Notes'
        lsOptions = ['Welcome to Image Quizzer','Following are instructions for the next question set']
        bTestResult = False
         
        oQuestion = InfoBox()
        sQuestionDescriptor = sGroupTitle + ' ...Test no errors for information boxes'
        oQuestion._sGrpBoxTitle_setter(sQuestionDescriptor)
        oQuestion._lsOptions_setter(lsOptions)

        bTestResult, qGrpBox = oQuestion.BuildQuestion()
        slicer.modules.TestQuestionSetWidget.groupsLayout.addWidget(qGrpBox)
         
        tupResult = fnName, bTestResult
        return tupResult
     
    #-----------------------------------------------
 
    def test_NoOptionsWarning(self):
        """ Test warning when no options are given.
            Test for each class in the list of classes defined in constructor.
        """
        fnName = sys._getframe().f_code.co_name
 
        # initialize
        lsOptions = []
        sGroupTitle = 'Test No Options'
        oQuestion = None       
        bTestResultTF = False
         
        dictModifiers = {}
         
        i = 0
        while i < len(self.lsClassNames):
            if self.lsClassNames[i] == 'RadioQuestion':
                oQuestion = RadioQuestion()
            elif self.lsClassNames[i] == 'CheckBoxQuestion':
                oQuestion = CheckBoxQuestion()
            elif self.lsClassNames[i] == 'TextQuestion':
                oQuestion = TextQuestion()
            elif self.lsClassNames[i] == 'IntegerValueQuestion':
                oQuestion = IntegerValueQuestion()
                oQuestion.UpdateDictionaryModifiers(dictModifiers)
            elif self.lsClassNames[i] == 'FloatValueQuestion':
                oQuestion = FloatValueQuestion()
                oQuestion.UpdateDictionaryModifiers(dictModifiers)
            elif self.lsClassNames[i] == 'InfoBox':
                oQuestion = InfoBox()
            else:
                    # If here, the test was successful. We specifically tried to trap the 'InvalidType'
                oQuestion = None 
                if (self.lsClassNames[i] == 'InvalidType'):
                    bTestResultTF = True
                else:
                    # If here, test failed. The class did not get picked up in the valid types above
                    sMsg = 'Test for unknown class. Test passes if following string = InvalidType ----->\n ----> UNKNOWN CLASS: "'+ self.lsClassNames[i] + '"' 
                    print(sMsg)
                    bTestResultTF = False
                    break
 
            if oQuestion != None:
                sExpWarning = self.lsClassNames[i] + ':buildQuestion:NoOptionsAvailable'
                with warnings.catch_warnings (record=True) as w:
                    warnings.simplefilter("always")

                    sQuestionDescriptor = sGroupTitle + '...' + self.lsClassNames[i]
                    oQuestion._sGrpBoxTitle_setter(sQuestionDescriptor)
                    oQuestion._lsOptions_setter(lsOptions)

                    
                    bFnResultSuccess, qGrpBox = oQuestion.BuildQuestion() 
                    if bFnResultSuccess == False:   # error was encountered - check the warning msg
                        if len(w) > 0:
                            print(str(w[0].message))
                            if sExpWarning == str(w[0].message):
                                if i > 0:   # consider previous result - test fails if any loop fails
                                    bTestResultTF = True & bTestResultTF 
                                else:
                                    bTestResultTF = True
                                    slicer.modules.TestQuestionSetWidget.groupsLayout.addWidget(qGrpBox)
                            else:
                                bTestResultTF = False
            i = i + 1
             
        tupResult = fnName, bTestResultTF
        return tupResult
             
#     #-----------------------------------------------
#  
#     def test_NoErrors_QuestionSetTest(self):
#         """ Test building a form given a list of questions.
#         """
#         fnName = sys._getframe().f_code.co_name
#          
#         bTestResultTF = True
#          
#         # initialize
#         ltupQuestionSet = []
#         sID = 'QS 1.0'
#         sQuestionSetTitle = 'Test Baines Image Quizzer Title'
# #         self.oQuestionSet = QuestionSet(sID, sQuestionSetTitle )
#         oQuestionSet = QuestionSet()
#          
#         lsQuestionOptions = ['rbtn1', 'rbtn2', 'rbtn3']
#         sQuestionType = 'Radio'
#         sQuestionDescriptor = 'Title for radio button group'
#         tupQuestionGroup = [sQuestionType, sQuestionDescriptor, lsQuestionOptions]
#         ltupQuestionSet.append(tupQuestionGroup)
#          
#         lsQuestionOptions = ['box1', 'box2', 'box3']
#         sQuestionType = 'Checkbox'
#         sQuestionDescriptor = 'Title for checkbox group'
#         tupQuestionGroup = [sQuestionType, sQuestionDescriptor, lsQuestionOptions]
#         ltupQuestionSet.append(tupQuestionGroup)
#  
#         lsQuestionOptions = ['text label1', 'text label2']
#         sQuestionType = 'Text'
#         sQuestionDescriptor = 'Title for line edit text group'
#         tupQuestionGroup = [sQuestionType, sQuestionDescriptor, lsQuestionOptions]
#         ltupQuestionSet.append(tupQuestionGroup)
#          
#  
#         lsQuestionOptions = ['infobox label1', ' ', 'infobox label2']
#         sQuestionType = 'InfoBox'
#         sQuestionDescriptor = 'Title for information label group - including spacer'
#         tupQuestionGroup = [sQuestionType, sQuestionDescriptor, lsQuestionOptions]
#         ltupQuestionSet.append(tupQuestionGroup)
#  
#         oQuestionSet.ltupQuestions = ltupQuestionSet
#         bTestResultTF, qQuizWidget = oQuestionSet.BuildQuestionSetForm()
#   
#         slicer.modules.TestQuestionSetWidget.questionSetLayout.addWidget(qQuizWidget)
#          
#         tupResult = fnName, bTestResultTF
#         return tupResult
#      
#     #-----------------------------------------------
#  
#     def test_Error_QuestionSetTest(self):
#         """ Test building a form given a list of questions.
#         """
#         fnName = sys._getframe().f_code.co_name
#          
#         bBuildSetSuccess = True
#          
#         # initialize
#         ltupQuestionSet = []
#         sID = 'QS 1.0'
#         sQuestionSetTitle = 'Test Baines Image Quizzer Title'
# 
#         oQuestionSet = QuestionSet()
#          
#         lsQuestionOptions = ['option1']
#         sQuestionType = 'Invalid'
#         sQuestionDescriptor = 'Title invalid group'
#         tupQuestionGroup = [sQuestionType, sQuestionDescriptor, lsQuestionOptions]
#         ltupQuestionSet.append(tupQuestionGroup)
#  
#         lsQuestionOptions = ['rbtn1', 'rbtn2', 'rbtn3']
#         sQuestionType = 'Radio'
#         sQuestionDescriptor = 'Title for radio button group'
#         tupQuestionGroup = [sQuestionType, sQuestionDescriptor, lsQuestionOptions]
#         ltupQuestionSet.append(tupQuestionGroup)
#  
#         oQuestionSet.ltupQuestions = ltupQuestionSet
#         bBuildSetSuccess, qQuizWidget = oQuestionSet.BuildQuestionSetForm()
#  
#         if bBuildSetSuccess == False:
#             bTestResultTF = True # we expected an error
#          
#          
#         tupResult = fnName, bTestResultTF
#         return tupResult
#  
#     #-----------------------------------------------
# 
    #-----------------------------------------------
 
    def test_CaptureResponse_RadioButtons(self):
        """ Testing capture of user responses to radio button questions
        """
        fnName = sys._getframe().f_code.co_name
 
        lsOptions = ['RadioBtn 1 Test Unchecked','RadioBtn 2 Test Checked', 'RadioBtn 3 Test Unchecked']
        sGroupTitle = 'Capture Response - Radio Buttons'
        bTestResult = False
         
        oQuestion = RadioQuestion()

        sQuestionDescriptor = sGroupTitle + ' ...Test Capture Reponse for Radio Buttons'
        oQuestion._sGrpBoxTitle_setter(sQuestionDescriptor)
        oQuestion._lsOptions_setter(lsOptions)
        
        
        bBuildResult, qGrpBox = oQuestion.BuildQuestion()
        slicer.modules.TestQuestionSetWidget.groupsLayout.addWidget(qGrpBox)
         
#         for qBtns in qGrpBox.findChildren(qt.QRadioButton):
#             print('traversing grp box')
             
        # set a button to check for testing
        lqAllBtns = qGrpBox.findChildren(qt.QRadioButton)
        lqAllBtns[1].setChecked(True)
         
        lsExpectedResponse = ['N','Y','N']
         
        # get actual response list
        bSuccess, lActualResponse, sMsg = oQuestion.CaptureResponse()
        if lActualResponse == lsExpectedResponse:
            bTestResult = True
         
         
        tupResult = fnName, bTestResult
        return tupResult
 
    #-----------------------------------------------
 
    def test_CaptureResponse_CheckBoxes(self):
        """ Testing capture of user responses to check box questions
        """
        fnName = sys._getframe().f_code.co_name
 
        lsOptions = ['CheckBox 1 Test Unchecked','CheckBox 2 Test Checked', 'CheckBox 3 Test Checked']
        sGroupTitle = 'Capture Response - Check Boxes'
        bTestResult = False
         
        oQuestion = CheckBoxQuestion()

        sQuestionDescriptor = sGroupTitle + ' ...Test Capture Reponse for Check Boxes'
        oQuestion._sGrpBoxTitle_setter(sQuestionDescriptor)
        oQuestion._lsOptions_setter(lsOptions)
        
        
        bBuildResult, qGrpBox = oQuestion.BuildQuestion()
        slicer.modules.TestQuestionSetWidget.groupsLayout.addWidget(qGrpBox)
         
        lqAllBoxes = qGrpBox.findChildren(qt.QCheckBox)
        lqAllBoxes[0].setChecked(False)
        lqAllBoxes[1].setChecked(True)
        lqAllBoxes[2].setChecked(True)
         
        lsExpectedResponse = ['N','Y','Y']
         
        # get actual response list
        bSuccess, lActualResponse, sMsg = oQuestion.CaptureResponse()
        if lActualResponse == lsExpectedResponse:
            bTestResult = True
         
         
        tupResult = fnName, bTestResult
        return tupResult
 
 
    #-----------------------------------------------
 
    def test_CaptureResponse_Text(self):
        """ Testing capture of user responses to text box questions
        """
        fnName = sys._getframe().f_code.co_name
 
        lsOptions = ['TextBox 1:','TextBox 2:']
        sGroupTitle = 'Capture Response - Text Boxes'
        bTestResult = False
         
        oQuestion = TextQuestion()

        sQuestionDescriptor = sGroupTitle + ' ...Test Capture Reponse for Text Boxes'
        oQuestion._sGrpBoxTitle_setter(sQuestionDescriptor)
        oQuestion._lsOptions_setter(lsOptions)
        
        
        bBuildResult, qGrpBox = oQuestion.BuildQuestion()
        slicer.modules.TestQuestionSetWidget.groupsLayout.addWidget(qGrpBox)
         
        lqAllBoxes = qGrpBox.findChildren(qt.QLineEdit)
        lqAllBoxes[0].setText('First Entry')
        lqAllBoxes[1].setText('Second Entry')
         
        lsExpectedResponse = ['First Entry','Second Entry']
         
        # get actual response list
        bSuccess, lActualResponse, sMsg = oQuestion.CaptureResponse()
        if lActualResponse == lsExpectedResponse:
            bTestResult = True
         
         
        tupResult = fnName, bTestResult
        return tupResult
 
    #-----------------------------------------------
 
    def test_CaptureResponse_IntegerValue(self):
        """ Testing capture of user responses to integer value questions
        """
        fnName = sys._getframe().f_code.co_name
 
        lsOptions = ['IntegerValueSpinner 1:','IntegerValueSpinner 2:']
        sGroupTitle = 'Capture Response - Integer Value Spinbox'
        bTestResult = False
         
        dictModifiers = {'Min':'-10', 'Max':'200'}
        oQuestion = IntegerValueQuestion()

        sQuestionDescriptor = sGroupTitle + ' ...Test Capture Reponse for Integer Value box'
        oQuestion._sGrpBoxTitle_setter(sQuestionDescriptor)
        oQuestion._lsOptions_setter(lsOptions)
        oQuestion.UpdateDictionaryModifiers(dictModifiers)
        
        
        bBuildResult, qGrpBox = oQuestion.BuildQuestion()
        slicer.modules.TestQuestionSetWidget.groupsLayout.addWidget(qGrpBox)
         
        lqAllBoxes = qGrpBox.findChildren(qt.QLineEdit)
        lqAllBoxes[0].setText(2)
        lqAllBoxes[1].setText(102)
         
        lsExpectedResponse = ['2','102']
         
        # get actual response list
        bSuccess, lActualResponse, sMsg = oQuestion.CaptureResponse()
        if lActualResponse == lsExpectedResponse:
            bTestResult = True
         
         
        tupResult = fnName, bTestResult
        return tupResult
 
    #-----------------------------------------------
 
    def test_CaptureResponse_FloatValue(self):
        """ Testing capture of user responses to float value questions
        """
        fnName = sys._getframe().f_code.co_name
 
        lsOptions = ['FloatValue line edit 1:','FloatValue line edit 2:']
        sGroupTitle = 'Capture Response - Float Value edit box'
        bTestResult = False
         
        dictModifiers = {'Min':'-10.5', 'Max':'200.5'}
        oQuestion = FloatValueQuestion()

        sQuestionDescriptor = sGroupTitle + ' ...Test Capture Reponse for Float Value box'
        oQuestion._sGrpBoxTitle_setter(sQuestionDescriptor)
        oQuestion._lsOptions_setter(lsOptions)
        oQuestion.UpdateDictionaryModifiers(dictModifiers)
        
        
        bBuildResult, qGrpBox = oQuestion.BuildQuestion()
        slicer.modules.TestQuestionSetWidget.groupsLayout.addWidget(qGrpBox)
         
        lqAllBoxes = qGrpBox.findChildren(qt.QLineEdit)
        lqAllBoxes[0].setText(2.5)
        lqAllBoxes[1].setText(102.5)
         
        lsExpectedResponse = ['2.5','102.5']
         
        # get actual response list
        bSuccess, lActualResponse, sMsg = oQuestion.CaptureResponse()
        if lActualResponse == lsExpectedResponse:
            bTestResult = True
         
         
        tupResult = fnName, bTestResult
        return tupResult

       
##########################################################################################
#                      Launching from main (Reload and Test button)
##########################################################################################

def main(self):
    try:
        logic = TestQuestionSetLogic()
        logic.runTest()
        
    except Exception as e:
        print(e)
    sys.exit(0)


if __name__ == "__main__":
    main()

