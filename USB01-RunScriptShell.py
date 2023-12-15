''' 
	USB01_RunScriptShell.py
	
	Author: C.Johnson
	Date: 	Dec. 15, 2023
	
	Shell script to run the secondary Python script through the Slicer Python Interactor
	that will update Slicer's extension list.
	
	Updating the extensions list adds the Image Quizzer module with the correct drive that 
	the USB is mounted on the PC.
	
'''
import slicer

exec(open("USB02-UpdateSlicerExtensionList.py").read())

slicer.util.exit(status=EXIT_SUCCESS)