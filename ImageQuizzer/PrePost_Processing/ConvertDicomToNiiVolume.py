'''
    Pre-processing utility to convert a DICOM series into a NIfTI volume file.
    If using a batch file for inputs, a log file is output in the same directory as the batch csv file. 
    This does not work for 4D images.


     
    Author: Carol Johnson (Baines Imaging Research Laboratories - LRCP London, ON)
    Date:   December 5, 2023
     
    Usage: ConvertDicomToNiiVolume -i [path to .dcm file as input] -o [path to output file] -b [path to batch csv file]
    
    
'''

import argparse, sys, os, logging
import subprocess
import time
import csv


def install(name):
    subprocess.call([sys.executable, '-m', 'pip', 'install', name])
    

install('dicom2nifti')
install('pydicom')


import dicom2nifti as dicom2nifti
import pydicom as pydicom



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ConvertDicomToNiiVolume():
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, sLogFilename=''):
        
        self.logger = None
        
        if sLogFilename != '':
            self.SetupLogging(sLogFilename)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __del__(self):
        
        if self.logger != None:
            handlers = self.logger.handlers[:]
            for handler in handlers:
                self.logger.removeHandler(handler)
                handler.close()


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetupLogging(self, sLogFilename):
        
        # create logger
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.WARNING)   # reduces INFO text from dicom2nifti function
        
        # create console handler and set level to DEBUG
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        
        # create handler and formatter for output
        fh = logging.FileHandler(sLogFilename)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
        
        # add formatter to handler
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        # add handlers to logger
        self.logger.addHandler(ch)
        self.logger.addHandler(fh)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def LogMessage(self, sLogMessage):
        
        if self.logger != None:                  
            self.logger.error(sLogMessage)
        else:
            print(sLogMessage)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetDicomData(self, sFilePath, sTagDescription):
        
        dcmData = pydicom.filereader.dcmread(sFilePath)
        
        return dcmData.get(sTagDescription)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def TestForSingleSeries(self, sInputDir):
        ''' Function reads the dicom files in the directory and returns
            True or False if one or more than one series exists, respectively
        '''

        lSeriesIDs = []
        sMsg = ''
        
        try:
            for sFilename in os.listdir(sInputDir):
                
                dcmFilePath = os.path.join(sInputDir, sFilename)

                sSeriesInstanceUID = self.GetDicomData(dcmFilePath, 'SeriesInstanceUID')
                sSeriesDescription = self.GetDicomData(dcmFilePath, 'SeriesDescription')

                if sSeriesInstanceUID not in lSeriesIDs:
                    lSeriesIDs.append(sSeriesInstanceUID)
                    
                
            if len(lSeriesIDs) != 1:
                   
                sLogMessage =   ',' + \
                                ',' + \
                                ',' + \
                                ',' + \
                                ',' + '*** ERROR *** There can only be 1 dicom series in this directory. (One of the series may have been converted.)' +\
                                ',' +  sInputDir 
                if self.logger != None:                  
                    self.logger.error(sLogMessage)
                else:
                    print(sLogMessage)
                 
                 
                
        except:
            sLogMessage =   ',' + \
                            ',' + \
                            ',' + \
                            ',' + \
                            ',' + '*** ERROR *** There is a non-dicom file or sub-folder in this directory. (One of the series may have been converted.)' +\
                            ',' +  sInputDir                            
            self.LogMessage(sLogMessage)
        
        return sMsg
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ConversionLogicSingle(self, sInputDir, sOutputDir):
        ''' Function to perform conversion for a single dicom series.
        
            - first test to make sure there is only one series in the directory
                else - can't convert
            - perform conversion of entire directory with specified output filename
            
        '''
        
        print('*** input  dir  :',sInputDir)
        
            
        sMsg = self.TestForSingleSeries(sInputDir)
        if sMsg == '':
            
            try:
                
                if not os.path.isdir(sInputDir) or not os.path.isdir(sOutputDir):
                    raise ValueError('*** ERROR *** Invalid input or output directory')
                
                else:
                
                    sFirstFile = os.listdir(sInputDir)[0]
                    sFilePath = os.path.join(sInputDir, sFirstFile)
                    sLogMessage =   ',' +\
                                    ',' +\
                                    ',' + str(self.GetDicomData(sFilePath, 'SeriesNumber')) + \
                                    ',' + self.GetDicomData(sFilePath, 'SeriesDescription') +\
                                    ',' + ',' +  sInputDir                            
                    self.LogMessage(sLogMessage)
                    
                   
                    # convert all series in the folder into volumes - filename is the series number
                    dicom2nifti.convert_directory(sInputDir, sOutputDir, compression=False, reorient=False)

            except ValueError as error:
                sLogMessage =   ',' + \
                                ',' + \
                                ',' + \
                                ',' + \
                                ',' + error.args[0] +\
                                ',' + sInputDir +\
                                ',' + sOutputDir
                self.LogMessage(sLogMessage)
                
            except:
                sMsg = "***ERROR*** failed to convert to .nii"
                sLogMessage =   ',' + \
                                ',' + \
                                ',' + \
                                ',' + \
                                ',' + sMsg +\
                                ',' +  sInputDir
                self.LogMessage(sLogMessage)


        else:
            print('\n\n ' + sMsg)

        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def BatchConversion(self, sCsvInputBatchFile):
        ''' Function to read in the csv file holding input and output folders for all images.
        
            Format:
                Each line: database folder, input folder, output folder
                
                
            The database folder string is joined to each of the input and output folder strings 
            to create the full folder paths.
            
        '''
        
        print("\n\nProcessing Batch file:", sCsvInputBatchFile)
        
        
        
        with open(sCsvInputBatchFile) as csv_file:

            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            
            for row in csv_reader:
            
                if row[0][:1] != "#":
                    sInputDir = os.path.join(row[0], row[1])
                    sOutputDir = os.path.join(row[0], row[2])
    
                    self.ConversionLogicSingle(sInputDir, sOutputDir)
                    line_count += 1

            print(f'Processed {line_count} lines.')
            
            
        
        

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main(argv):
    try:
        

        parser = argparse.ArgumentParser(description="ConvertDicomToNiiVolume preprocessor")
        parser.add_argument("-i", "--input-folder", dest="input_folder", metavar="PATH",
                            default="-", help="Folder of input DICOM files (can contain sub-folders)")
        parser.add_argument("-o", "--output-folder", dest="output_folder", metavar="PATH",
                            default=".", help="Folder to save converted datasets")
        parser.add_argument("-b", "--batch-csv", dest="batch_csv", metavar="CsvFilePath",
                            default='-', help="Full path to csv file for batch processing")
        args = parser.parse_args(argv)
        
        
        
        if args.output_folder == "." and args.input_folder != "-":
            print('Current directory is selected as output folder (default). To change it, please specify --output-folder')
        if args.batch_csv == "-" and args.input_folder == "-":
            print('One of -i for input-folder or -b for batch-csv file must be set as inputs.')

        
        sLogFilePath = ''
        
        
        if args.batch_csv != "-":
            sBatchLogName = os.path.splitext(os.path.basename(args.batch_csv))[0] + 'Log.csv'
            [head,tail] = os.path.split(args.batch_csv)
            sLogFilePath = os.path.join(head, sBatchLogName)
            
            if os.path.isfile(sLogFilePath):
                os.remove(sLogFilePath)


            logic = ConvertDicomToNiiVolume(sLogFilePath)


            logic.BatchConversion(args.batch_csv)

        else:
            if args.input_folder != "-":       
                logic = ConvertDicomToNiiVolume()
                logic.ConversionLogicSingle(args.input_folder, args.output_folder)
                
        
    except Exception as e:
        print(e)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":




    print(sys.argv)

    log_format = "\n%(asctime)s: %(message)s"
    logging.basicConfig(format=log_format, level=logging.INFO,
                        datefmt="%H:%M:%S")

 
    logging.info("----------: starting conversion %s", time.asctime())

    main(sys.argv[1:])



    logging.info("----------: conversion complete %s", time.asctime())
    
    print('\n\n','!'*10,'   FINISHED ConvertDicomToNiiVolume   ','!'*10)
