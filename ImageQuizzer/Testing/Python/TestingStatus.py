
##########################################################################
#
# TestingStatus
#
##########################################################################

class TestingStatus:
    
    def __init__(self, parent=None):
        self.sClassName = type(self).__name__
        self.parent = parent
        print('Constructor for TestingStatus class')

    #------------------------------------------- 
    def DisplayTestResults(self, tupResults):
        
        if (len(tupResults) > 0):
            # print the boolean results for each test
            self.tupResults = tupResults
            print('--- Test Results ' + ' --------- ' + self.sClassName + ' functions -----')
            for i in range(len(tupResults)):
                success = False   # assume fail
                sFname, success = tupResults[i]
                if success == True:
                    sDisplay = "Ahh....... test passed.    : "
                else:
                    sDisplay = "!$!*^&#!@$%! Test Failed!! : "
                print(sDisplay, i+1, sFname)
        else:
            print("No results to report")

        print("\n************ Test Complete ************\n")
