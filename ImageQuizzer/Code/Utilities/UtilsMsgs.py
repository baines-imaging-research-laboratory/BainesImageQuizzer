import os, sys
import warnings
import vtk, qt, ctk, slicer

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

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def DisplayTimedMessage(self, chTitle, chMessage, iMSecs):
        ''' This message box is a separate application that will display a message
            and automatically close after a given number of milliseconds
        '''

        def close_popup():
            msgBox.accept()    
            
        app = qt.QApplication
        msgBox = qt.QMessageBox()
        msgBox.setText(chMessage)
        msgBox.setWindowTitle(chTitle)
        msgBox.setStandardButtons(qt.QMessageBox.NoButton)  # Remove default button
    
        timer = qt.QTimer()
        timer.timeout.connect(close_popup)
        timer.start(iMSecs)  # Timeout after x seconds
        msgBox.exec_()  # Display the popup

