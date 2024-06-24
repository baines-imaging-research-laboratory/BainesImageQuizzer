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

    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def DisplayError(sErrorMsg):
        qt.QMessageBox().critical(slicer.util.mainWindow(),"Image Quizzer: ERROR",sErrorMsg)
        exit()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def DisplayWarning(sWarningMsg):
        qt.QMessageBox().warning(slicer.util.mainWindow(), 'Image Quizzer: Warning', sWarningMsg)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def DisplayInfo(sTextMsg):
        qt.QMessageBox().information(slicer.util.mainWindow(), 'Image Quizzer: Information', sTextMsg)
 
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def DisplayYesNo(sMsg):
        qtAns = qt.QMessageBox().question(slicer.util.mainWindow(),'Image Quizzer: Continue?',sMsg, qt.QMessageBox.Yes, qt.QMessageBox.No)
        return qtAns
 
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def DisplayOkCancel(sMsg):
        qtAns = qt.QMessageBox().question(slicer.util.mainWindow(),"Image Quizzer: ",sMsg, qt.QMessageBox.Ok, qt.QMessageBox.Cancel)
        return qtAns
 
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def DisplayTimedMessage(chTitle, chMessage, iMSecs):
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

