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
        self.parent.categories = ["Testing.ImageQuizzer"]
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
        self.lsClassNames = ['RadioQuestion', 'CheckBoxQuestion','TextQuestion', 'InfoBox', 'InvalidType']

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
        tupResults.append(self.test_NoErrors_QuestionSetTest())
        tupResults.append(self.test_Error_QuestionSetTest())

        
        logic.questionSetStatus.DisplayTestResults(tupResults)
 
    #------------------------------------------- 

    def test_NoErrors_BuildQuestionWidget(self):
        """ Test for each question type with no errors encountered
        """

        # initialize
        self.lOptions = ['Opt1','Opt2']
        self.sGroupTitle = 'Group Title'
        self.fnName = sys._getframe().f_code.co_name
        self.questionType = None
        bTestResultTF = False
        
        i = 0
        while i < len(self.lsClassNames):
            if self.lsClassNames[i] == 'RadioQuestion':
                self.questionType = RadioQuestion(self.lOptions, self.sGroupTitle + '...' + self.lsClassNames[i])
            elif self.lsClassNames[i] == 'CheckBoxQuestion':
                self.questionType = CheckBoxQuestion(self.lOptions, self.sGroupTitle + '...' + self.lsClassNames[i])
            elif self.lsClassNames[i] == 'TextQuestion':
                self.questionType = TextQuestion(self.lOptions, self.sGroupTitle + '...' + self.lsClassNames[i])
            elif self.lsClassNames[i] == 'InfoBox':
                self.questionType = InfoBox(self.lOptions, self.sGroupTitle + '...' + self.lsClassNames[i])
            else:
#  TODO ??               self.questionType = LabelWarningBox('Invalid question type', 'WARNING- See administrator')
                self.questionType = None
                if (self.lsClassNames[i] == 'InvalidType'):
                    # If here, the test was successful. We specifically tried to trap the 'InvalidType'
                    bTestResultTF = True
                else:
                    # If here, test failed. The class did not get picked up in the valid types above
                    sMsg = 'Test for unknown class. Test passes if following string = InvalidType ----->\n ----> UNKNOWN CLASS: "'+ self.lsClassNames[i] + '"' 
                    print(sMsg)
                    bTestResultTF = False
                    break
                
            if self.questionType != None:
                # Question type was constructed - try to create a widget
                bTestResult, qWidgetBox = self.questionType.BuildQuestion()
                slicer.modules.TestQuestionSetWidget.groupsLayout.addWidget(qWidgetBox)
                bTestResultTF = True

            i = i + 1
            
        tupResult = self.fnName, bTestResultTF
        return tupResult
        
    #-----------------------------------------------

    def test_NoErrors_RadioButtons(self):
        """ Class is called with no errors encountered
        """
        self.lOptions = ['Injury','Recurrence']
        self.sGroupTitle = 'Assessment'
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name
        
        self.rq = RadioQuestion(self.lOptions, self.sGroupTitle + ' ...Test No Errors for Radio Buttons')
        bTestResult, qGrpBox = self.rq.BuildQuestion()
        slicer.modules.TestQuestionSetWidget.groupsLayout.addWidget(qGrpBox)
        
        tupResult = self.fnName, bTestResult
        return tupResult

    #-----------------------------------------------

    def test_NoErrors_CheckBoxes(self):
        """ Class is called with no errors encountered
        """
        self.sGroupTitle = 'High Risk Factors'
        self.lOptions = ['Enlarging Opacity','Bulging Margin', 'Sequential Enlargement']
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name
        
        self.cb = CheckBoxQuestion(self.lOptions, self.sGroupTitle + ' ...Test No Errors for Check Boxes')
        bTestResult, qGrpBox = self.cb.BuildQuestion()
        slicer.modules.TestQuestionSetWidget.groupsLayout.addWidget(qGrpBox)
        
        tupResult = self.fnName, bTestResult
        return tupResult
    
    #-----------------------------------------------

    def test_NoErrors_TextQuestion(self):
        """ Class is called with no errors encountered
        """
        self.sGroupTitle = 'Physician Notes'
        self.sNotes = ['Enter patient observations:','Describe next steps:']
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name
        
        self.textQuestion = TextQuestion(self.sNotes, self.sGroupTitle + ' ...Test No Errors for Line Edits')
        bTestResult, qGrpBox = self.textQuestion.BuildQuestion()
        slicer.modules.TestQuestionSetWidget.groupsLayout.addWidget(qGrpBox)
        
        tupResult = self.fnName, bTestResult
        return tupResult
    
    #-----------------------------------------------

    def test_NoErrors_InfoBox(self):
        """ Class is called with no errors encountered
        """
        self.sGroupTitle = 'Welcome Notes'
        self.sNotes = ['Welcome to Image Quizzer','Following are instructions for the next question set']
        bTestResult = False
        self.fnName = sys._getframe().f_code.co_name
        
        self.infoBox = InfoBox(self.sNotes, self.sGroupTitle + ' ...Test no errors for information boxes')
        bTestResult, qGrpBox = self.infoBox.BuildQuestion()
        slicer.modules.TestQuestionSetWidget.groupsLayout.addWidget(qGrpBox)
        
        tupResult = self.fnName, bTestResult
        return tupResult
    
    #-----------------------------------------------

    def test_NoOptionsWarning(self):
        """ Test warning when no options are given.
            Test for each class in the list of classes defined in constructor.
        """

        # initialize
        self.lOptions = []
        self.sGroupTitle = 'Test No Options'
        self.fnName = sys._getframe().f_code.co_name
        self.questionType = None       
        bTestResultTF = False
        
        i = 0
        while i < len(self.lsClassNames):
            if self.lsClassNames[i] == 'RadioQuestion':
                self.questionType = RadioQuestion(self.lOptions, self.sGroupTitle + '...' + self.lsClassNames[i])
            elif self.lsClassNames[i] == 'CheckBoxQuestion':
                self.questionType = CheckBoxQuestion(self.lOptions, self.sGroupTitle + '...' + self.lsClassNames[i])
            elif self.lsClassNames[i] == 'TextQuestion':
                self.questionType = TextQuestion(self.lOptions, self.sGroupTitle + '...' + self.lsClassNames[i])
            elif self.lsClassNames[i] == 'InfoBox':
                self.questionType = InfoBox(self.lOptions, self.sGroupTitle + '...' + self.lsClassNames[i])
            else:
                    # If here, the test was successful. We specifically tried to trap the 'InvalidType'
                self.questionType = None 
                if (self.lsClassNames[i] == 'InvalidType'):
                    bTestResultTF = True
                else:
                    # If here, test failed. The class did not get picked up in the valid types above
                    sMsg = 'Test for unknown class. Test passes if following string = InvalidType ----->\n ----> UNKNOWN CLASS: "'+ self.lsClassNames[i] + '"' 
                    print(sMsg)
                    bTestResultTF = False
                    break

            if self.questionType != None:
                sExpWarning = self.lsClassNames[i] + ':buildQuestion:NoOptionsAvailable'
                with warnings.catch_warnings (record=True) as w:
                    warnings.simplefilter("always")
                    bFnResultSuccess, qGrpBox = self.questionType.BuildQuestion() 
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
            
        tupResult = self.fnName, bTestResultTF
        return tupResult
            
    #-----------------------------------------------

    def test_NoErrors_QuestionSetTest(self):
        """ Test building a form given a list of questions.
        """
        self.fnName = sys._getframe().f_code.co_name
        
        bTestResultTF = True
        
        # initialize
        ltupQuestionSet = []
        sID = 'QS 1.0'
        sQuestionSetTitle = 'Test Baines Image Quizzer Title'
#         self.oQuestionSet = QuestionSet(sID, sQuestionSetTitle )
        self.oQuestionSet = QuestionSet()
        
        lsQuestionOptions = ['rbtn1', 'rbtn2', 'rbtn3']
        sQuestionType = 'Radio'
        sQuestionDescriptor = 'Title for radio button group'
        tupQuestionGroup = [sQuestionType, sQuestionDescriptor, lsQuestionOptions]
        ltupQuestionSet.append(tupQuestionGroup)
        
        lsQuestionOptions = ['box1', 'box2', 'box3']
        sQuestionType = 'Checkbox'
        sQuestionDescriptor = 'Title for checkbox group'
        tupQuestionGroup = [sQuestionType, sQuestionDescriptor, lsQuestionOptions]
        ltupQuestionSet.append(tupQuestionGroup)

        lsQuestionOptions = ['text label1', 'text label2']
        sQuestionType = 'Text'
        sQuestionDescriptor = 'Title for line edit text group'
        tupQuestionGroup = [sQuestionType, sQuestionDescriptor, lsQuestionOptions]
        ltupQuestionSet.append(tupQuestionGroup)
        

        lsQuestionOptions = ['infobox label1', ' ', 'infobox label2']
        sQuestionType = 'InfoBox'
        sQuestionDescriptor = 'Title for information label group - including spacer'
        tupQuestionGroup = [sQuestionType, sQuestionDescriptor, lsQuestionOptions]
        ltupQuestionSet.append(tupQuestionGroup)

        bTestResultTF, qQuizWidget = self.oQuestionSet.BuildQuestionSetForm(ltupQuestionSet)
 
        slicer.modules.TestQuestionSetWidget.questionSetLayout.addWidget(qQuizWidget)
        
        tupResult = self.fnName, bTestResultTF
        return tupResult
    
    #-----------------------------------------------

    def test_Error_QuestionSetTest(self):
        """ Test building a form given a list of questions.
        """
        self.fnName = sys._getframe().f_code.co_name
        
        bBuildSetSuccess = True
        
        # initialize
        ltupQuestionSet = []
        sID = 'QS 1.0'
        sQuestionSetTitle = 'Test Baines Image Quizzer Title'
#         self.oQuestionSet = QuestionSet(sID, sQuestionSetTitle )
        self.oQuestionSet = QuestionSet()
        
        lsQuestionOptions = ['option1']
        sQuestionType = 'Invalid'
        sQuestionDescriptor = 'Title invalid group'
        tupQuestionGroup = [sQuestionType, sQuestionDescriptor, lsQuestionOptions]
        ltupQuestionSet.append(tupQuestionGroup)

        lsQuestionOptions = ['rbtn1', 'rbtn2', 'rbtn3']
        sQuestionType = 'Radio'
        sQuestionDescriptor = 'Title for radio button group'
        tupQuestionGroup = [sQuestionType, sQuestionDescriptor, lsQuestionOptions]
        ltupQuestionSet.append(tupQuestionGroup)

        bBuildSetSuccess, qQuizWidget = self.oQuestionSet.BuildQuestionSetForm(ltupQuestionSet)

        if bBuildSetSuccess == False:
            bTestResultTF = True # we expected an error
        
        
        tupResult = self.fnName, bTestResultTF
        return tupResult

    #-----------------------------------------------


        
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

