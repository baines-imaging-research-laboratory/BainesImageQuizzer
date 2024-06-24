
import os, sys
from os.path import basename

import smtplib
import traceback

import Utilities.UtilsMsgs as UtilsMsgs
import Utilities.UtilsFilesIO as UtilsFilesIO

from Utilities.UtilsMsgs import *
from Utilities.UtilsFilesIO import *

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

    sHostServer = ''
    sHostUsername = ''
    sHostPassword = ''
    iHostPort = 0
    
    sEmailResultsFrom = ''
    sEmailResultsTo = ''
    sEmailSubjectLine = ''
    sEmailMessage = ''
    sEmailAttachment = ''
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def SetupEmailResults( sEmailResultsTo):
        """ Setup if request was set to have the quiz results emailed upon completion.
            Extract server configuration.
        """
        
        try:
            
            bEmailRequest = False
            sMsg = ''
            
            if sEmailResultsTo != '':
                bEmailRequest = True
                sSmtpConfigFile = os.path.join(UtilsFilesIO.GetConfigDir(), 'smtp_config.txt')
                
                if sSmtpConfigFile != '':
                    UtilsEmail.sHostServer = UtilsEmail.ParseConfigFile(sSmtpConfigFile, 'smtp', 'host')
                    UtilsEmail.sHostUsername = UtilsEmail.ParseConfigFile(sSmtpConfigFile, 'smtp', 'username')
                    UtilsEmail.sHostPassword = UtilsEmail.ParseConfigFile(sSmtpConfigFile, 'smtp', 'password')
                    UtilsEmail.iHostPort = int(UtilsEmail.ParseConfigFile(sSmtpConfigFile, 'smtp', 'port'))
                
                    UtilsEmail.sEmailResultsTo = sEmailResultsTo
                    UtilsEmail.sEmailResultsFrom = UtilsEmail.sHostUsername
                    UtilsEmail.sEmailSubjectLine = 'Image Quizzer results file from ' + UtilsFilesIO.GetUsername()
                    UtilsEmail.sEmailMessage = 'Attached are the results for the quiz '\
                         + UtilsFilesIO.GetQuizFilename()\
                         + ' from user ' + UtilsFilesIO.GetUsername()\
                         + '.'
                         
                    sQuizResultsZipFile = UtilsFilesIO.GetQuizFilename().rstrip('.xml') + '.zip'
                    UtilsEmail.sEmailAttachment = os.path.join(UtilsFilesIO.GetUserDir(), sQuizResultsZipFile)
                    
                    if UtilsEmail.sEmailResultsTo == '' or\
                            UtilsEmail.sEmailResultsFrom == '' or\
                            UtilsEmail.sEmailSubjectLine == '' or\
                            UtilsEmail.sEmailMessage == '' or\
                            UtilsEmail.sEmailAttachment == '' or\
                            UtilsEmail.sHostServer == '' or\
                            UtilsEmail.sHostUsername == '' or\
                            UtilsEmail.sHostPassword == '' or\
                            UtilsEmail.iHostPort == 0 :

                        raise

        except:
            tb = traceback.format_exc()
            sMsg = "SetupEmailResults: Error setting up email configuration\n " \
                   + UtilsEmail.GetEmailConfiguration() + '\n\n'+  tb 
            UtilsMsgs.DisplayError(sMsg)
            
        return bEmailRequest
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def ParseConfigFile( sFullFilename, sCategory, sItem):
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
    @staticmethod
    def GetEmailConfiguration():
        """ Return string description of email configuration properties
        """
        
        sConfiguration = '\nHost Server: '       + UtilsEmail.sHostServer\
                        + '\nHost Username: '    + UtilsEmail.sHostUsername\
                        + '\nHost Password:    ' + UtilsEmail.sHostPassword\
                        + '\nHost Port: '        + str(UtilsEmail.iHostPort)\
                        + '\n\nEmail From: '     + UtilsEmail.sEmailResultsFrom\
                        + '\nEmail To: '         + UtilsEmail.sEmailResultsTo\
                        + '\nEmail Subject: '    + UtilsEmail.sEmailSubjectLine\
                        + '\nEmail Message: '    + UtilsEmail.sEmailMessage\
                        + '\nEmail Attachment: ' + UtilsEmail.sEmailAttachment
                        
        return sConfiguration
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def SendEmail( sPathToZipFile):
        """ Send email through host server
        """
        s = smtplib.SMTP( host=UtilsEmail.sHostServer, port=UtilsEmail.iHostPort )
        s.starttls()
        s.login( UtilsEmail.sHostUsername, UtilsEmail.sHostPassword )
        
        msg = MIMEMultipart()
        msg['From'] = UtilsEmail.sEmailResultsFrom
        msg['To'] = UtilsEmail.sEmailResultsTo
        msg['Subject'] = UtilsEmail.sEmailSubjectLine
        msg.attach(MIMEText(UtilsEmail.sEmailMessage,'plain'))
        
        with open(sPathToZipFile, 'rb') as fil:
            part = MIMEApplication(fil.read(), Name=basename(sPathToZipFile))
        
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(sPathToZipFile)
        msg.attach(part)
        
        s.send_message(msg)
        
        del(msg)
        
        s.quit()
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    
