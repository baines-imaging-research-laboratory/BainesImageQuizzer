'''
Created on Jul 18, 2019

@author: Carol
'''

if __name__ == '__main__':
    print("Loading Image Quizzer slicelet with extra modules")
    modules = ["imagequizzer","segmenteditor"]
    for module in modules:
        getattr(slicer.modules,module).widgetRepresentation().show()