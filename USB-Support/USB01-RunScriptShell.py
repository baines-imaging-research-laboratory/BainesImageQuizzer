''' 
	USB01_RunScriptShell.py
	
	Author: C.Johnson
	Date: 	Dec. 15, 2023
	
	Shell script to run the secondary Python script to update Slicer's modules extension list. 
	
	Updating the extensions list adds the Image Quizzer module with the correct drive that 
	the USB is mounted on the PC.
	
	(A USB plugged into different machines does not guarantee that Python is available
	so we use Slicer's Python Interactor to run the secondary script.)
	

    Scripts layout:
        ImageQuizzerStartup-USB.bat (with Slicer-xxxx.ini file as argument for USB02-UpdateSlicerExtensionList)
                    |
                    |-> USB01-RunScriptShell.py (opens Slicer's Python interactor)
                                    |
                                    |-> USB02-UpdateSlicerExtensionList.py

	
'''
import slicer

exec(open("USB-Support/USB02-UpdateSlicerExtensionList.py").read())

slicer.util.exit(status=EXIT_SUCCESS)