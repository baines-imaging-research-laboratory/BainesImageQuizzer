#############################################################################
#
# USB02-UpdateSlicerExtensionList
#
#############################################################################
''' Script to update the NA-MIC Extensions Slicer-xxxx.ini file with the path to the 
    Baines Image Quizzer.

    This utility makes a USB more portable for the user. The user does not need to know 
    how to manually add the module path to this list.  The update of the Slicer-xxxx.ini file uses
    the current drive letter for the USB which can change depending on which PC or laptop the USB
    is plugged into.

    This script is called from USB01-RunScriptShell.py which launches Slicer's python interpreter.

'''
import os, sys, fileinput
import slicer

def main():
    args = sys.argv[1:]
     
    # open .ini file for Slicer extensions
    sFullPath = args[0]
    print(sFullPath)
    
    sImageQuizzerPath = os.path.join(os.getcwd(),'ImageQuizzer','Code').replace('\\','/')
    print(sImageQuizzerPath)
     
    
    sLineToFind = "AdditionalPaths"
 
    for line in fileinput.FileInput(sFullPath, inplace=True):
        if sLineToFind in line:
            if sImageQuizzerPath not in line:
                line = line.rstrip('\n')
                line = line + ', ' + sImageQuizzerPath + '\n'
        print(line, end='')
        
    fileinput.close()
    print('. Finished')

if __name__ == "__main__":
    main()

    # close the python interactor
    slicer.util.exit(status=EXIT_SUCCESS)
