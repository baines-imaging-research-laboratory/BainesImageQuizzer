
import os, sys
from os.path import basename

import smtplib
import traceback

import Utilities.UtilsMsgs as UtilsMsgs

from Utilities.UtilsMsgs import *

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

##########################################################################
#
#   class UtilsEmail
#
##########################################################################

class UtilsEmail:
    """ Functions to email the quiz results to the requested email address.
    """

    def __init__(self):
        
        self.sHostServer = ''
        self.sHostUsername = ''
        self.sHostPassword = ''
        self.iHostPort = 0
        
        self.sEmailResultsFrom = ''
        self.sEmailResultsTo = ''
        self.sEmailSubjectLine = ''
        self.sEmailMessage = ''
        self.sEmailAttachment = ''
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetupEmailResults(self, oFilesIO, sEmailResultsTo):
        """ Setup if request was set to have the quiz results emailed upon completion.
            Extract server configuration.
        """
        
        try:
            
            bEmailRequest = False
            sMsg = ''
            
            if sEmailResultsTo != '':
                bEmailRequest = True
                sSmtpConfigFile = os.path.join(oFilesIO.GetConfigDir(), 'smtp_config.txt')
                
                if sSmtpConfigFile != '':
                    self.sHostServer = self.ParseConfigFile(sSmtpConfigFile, 'smtp', 'host')
                    self.sHostUsername = self.ParseConfigFile(sSmtpConfigFile, 'smtp', 'username')
                    self.sHostPassword = self.ParseConfigFile(sSmtpConfigFile, 'smtp', 'password')
                    self.iHostPort = int(self.ParseConfigFile(sSmtpConfigFile, 'smtp', 'port'))
                
                    self.sEmailResultsTo = sEmailResultsTo
                    self.sEmailResultsFrom = self.sHostUsername
                    self.sEmailSubjectLine = 'Image Quizzer results file from ' + oFilesIO.GetUsername()
                    self.sEmailMessage = 'Attached are the results for the quiz '\
                         + oFilesIO.GetQuizFilename()\
                         + ' from user ' + oFilesIO.GetUsername()\
                         + '.'
                         
                    sQuizResultsZipFile = oFilesIO.GetQuizFilename().rstrip('.xml') + '.zip'
                    self.sEmailAttachment = os.path.join(oFilesIO.GetUserDir(), sQuizResultsZipFile)
                    
                    if self.sEmailResultsTo == '' or\
                            self.sEmailResultsFrom == '' or\
                            self.sEmailSubjectLine == '' or\
                            self.sEmailMessage == '' or\
                            self.sEmailAttachment == '' or\
                            self.sHostServer == '' or\
                            self.sHostUsername == '' or\
                            self.sHostPassword == '' or\
                            self.iHostPort == 0 :

                        raise

        except:
            tb = traceback.format_exc()
            sMsg = "SetupEmailResults: Error setting up email configuration\n " \
                   + self.GetEmailConfiguration() + '\n\n'+  tb 
            UtilsMsgs.DisplayError(sMsg)
            
        return bEmailRequest
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ParseConfigFile(self, sFullFilename, sCategory, sItem):
        """ Function to parse config file given the category and item.
            Syntax:
                [sCategory]
                sItem=xxxxxxx
            Any lines beginning with '#' are ignored
        """
        
        sItemValue = ''
        bItemFound = False
        sCategorySyntax = '[' + sCategory + ']'
        sItemSyntax = sItem + '='
        
        iNumLines = sum(1 for line in open(sFullFilename))
        
        fileConfig = open(sFullFilename, mode='r', encoding='utf-8')
        sLine = fileConfig.readline()
        iCnt = 1
        while sLine and iCnt <= iNumLines:
            if sLine[0] != '#':
                if sLine.find(sCategorySyntax) != -1 :
                    # search for item in category group
                    while sLine:
                        sLine = fileConfig.readline()
                        iCnt = iCnt + 1
                        if sLine.find(sItemSyntax) != -1 :
                            sItemValue = sLine[len(sItemSyntax):len(sLine)]
                            sItemValue = sItemValue.rstrip('\n')
                            
                            bItemFound = True
                            break
                    
            if not bItemFound:
                sLine = fileConfig.readline()
                iCnt = iCnt + 1
            else:
                fileConfig.close()
                break
                
        return sItemValue
                    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetEmailConfiguration(self):
        """ Return string description of email configuration properties
        """
        
        sConfiguration = '\nHost Server: '       + self.sHostServer\
                        + '\nHost Username: '    + self.sHostUsername\
                        + '\nHost Password:    ' + self.sHostPassword\
                        + '\nHost Port: '        + str(self.iHostPort)\
                        + '\n\nEmail From: '     + self.sEmailResultsFrom\
                        + '\nEmail To: '         + self.sEmailResultsTo\
                        + '\nEmail Subject: '    + self.sEmailSubjectLine\
                        + '\nEmail Message: '    + self.sEmailMessage\
                        + '\nEmail Attachment: ' + self.sEmailAttachment
                        
        return sConfiguration
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SendEmail(self, sPathToZipFile):
        """ Send email through host server
        """
        s = smtplib.SMTP( host=self.sHostServer, port=self.iHostPort )
        s.starttls()
        s.login( self.sHostUsername, self.sHostPassword )
        
        msg = MIMEMultipart()
        msg['From'] = self.sEmailResultsFrom
        msg['To'] = self.sEmailResultsTo
        msg['Subject'] = self.sEmailSubjectLine
        msg.attach(MIMEText(self.sEmailMessage,'plain'))
        
        with open(sPathToZipFile, 'rb') as fil:
            part = MIMEApplication(fil.read(), Name=basename(sPathToZipFile))
        
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(sPathToZipFile)
        msg.attach(part)
        
        s.send_message(msg)
        
        del(msg)
        
        s.quit()
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    
