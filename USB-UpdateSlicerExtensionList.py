#############################################################################
#
# Script to add Image Quizzer code path to the ini file for Slicer extensions
#
#############################################################################

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
