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
    
    This function looks for a previous connection to the module's code path (ImageQuizzer/Code)
    and if it exists it may have the wrong path.
    It will be removed from the line and new path will be appended to end of line.
    Any entries that are subfolders to ImageQuizzer/Code (eg. Testing) will also be removed.
    

    Scripts layout:
        ImageQuizzerStartup-USB.bat (with Slicer-xxxx.ini file as argument for USB02-UpdateSlicerExtensionList)
                    |
                    |-> USB01-RunScriptShell.py (opens Slicer's Python interactor)
                                    |
                                    |-> USB02-UpdateSlicerExtensionList.py
                                    

'''
import os, sys, fileinput
import slicer

def main():
    args = sys.argv[1:]
     
    # open .ini file for Slicer extensions
    sSlicerIniPath = args[0]
    
    sImageQuizzerCodePath = os.path.join(os.getcwd(),'ImageQuizzer','Code').replace('\\','/')
     
    sSubstringToFind = "ImageQuizzer/Code"
    sLineToFind = "AdditionalPaths"
    iStartAllEntries = len(sLineToFind)

 
    for line in fileinput.FileInput(sSlicerIniPath, inplace=True):
        if sLineToFind in line:
            
            #remove any existing entries
            indSearchStart = 0
            while (indSearchStart < len(line)):

                if sSubstringToFind in line:

                    # get start of substring
                    iStartIndSubstr = line.find(sSubstringToFind, indSearchStart)
                    if iStartIndSubstr > -1:
    
                        # find start index of removal - look for end of preceding entry
                        iStartIndOfRemoval = line.rfind(',',iStartAllEntries, iStartIndSubstr)
                        if iStartIndOfRemoval == -1 : # must be the first entry
                            iStartIndOfRemoval = iStartAllEntries
                        else:
                            iStartIndOfRemoval = iStartIndOfRemoval + 1 # after comma
    
                        # find end index of removal
                        iEndIndOfRemoval = line.find(',',iStartIndSubstr)
                        if iEndIndOfRemoval == -1 : # must be the last entry
                            iStartIndOfRemoval = iStartIndOfRemoval -1 # don't need comma
                            iEndIndOfRemoval = len(line)
                            indSearchStart = len(line)
                        else:
                            iEndIndOfRemoval = iEndIndOfRemoval + 1 # also remove the comma
                            indSearchStart = iStartIndOfRemoval
    
                        # remove entry
                        line = line[0:iStartIndOfRemoval] + line[iEndIndOfRemoval:]
                        
    
                    else: # not found in (remainder of) search
                        indSearchStart = len(line) # end the while loop
    
                else:   # not found
                    indSearchStart = len(line) # end the while loop


            # append to end of line
            line = line.rstrip('\n')
            if len(line) == len(sLineToFind):
                line = line + sImageQuizzerCodePath + '\n'
            else:
                line = line + ', ' + sImageQuizzerCodePath + '\n'

        print(line, end='')
            
    fileinput.close()

if __name__ == "__main__":
    main()

    # close the python interactor
    slicer.util.exit(status=EXIT_SUCCESS)
