#
#   https://www.freecodecamp.org/news/send-emails-using-code-4fcea9df63f/
#

import os, sys

import smtplib
import traceback

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# MY_ADDRESS = 'my_address@example.com'
# PASSWORD = 'mypassword'

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
    def GetEmailConfiguration(self):
        """ Return string description of email configuration properties
        """
        
        sConfiguration = '\nHost Server: ' + self.sHostServer\
                        + '\nHost Username: ' + self.sHostUsername\
                        + '\nHost Password: ' + self.sHostPassword\
                        + '\nHost Port: ' + str(self.iHostPort)\
                        + '\n\nEmail From: ' + self.sEmailResultsFrom\
                        + '\nEmail To: ' + self.sEmailResultsTo\
                        + '\nEmail Subject: ' + self.sEmailSubjectLine\
                        + '\nEmail Message: ' + self.sEmailMessage\
                        + '\nEmail Attachment: ' + self.sEmailAttachment
                        
        return sConfiguration
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetupEmailResults(self, oFilesIO, sEmailResultsTo):
        """ Setup if request was set to have the quiz results emailed upon completion.
            Extract server configuration.
        """
        
        try:
            sMsg = ''
            if sEmailResultsTo != '':
                # get path to sntp sercer config file  (having a paths file allows for the
                #         config file to be outside the repository)
                
                sConfigPathsFilename = os.path.join(oFilesIO.GetResourcesConfigDir(),\
                                                   'smtp_config_paths.txt')
                sSmtpConfigFile = self.ParseConfigFile(sConfigPathsFilename,'paths','config')
                
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
                   
        return sMsg
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ParseConfigFile(self, sFullFilename, sCategory, sItem):
        """ Function to parse config file given the category and item.
            Syntax:
                [sCategory]
                sItem=xxxxxxx
            Any lines beginning with '#' are ignored
        """
        
        itemValue = ''
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
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    
                    
# def get_contacts(filename):
#     """
#     Return two lists names, emails containing names and email addresses
#     read from a file specified by filename.
#     """
#     
#     names = []
#     emails = []
#     with open(filename, mode='r', encoding='utf-8') as contacts_file:
#         for a_contact in contacts_file:
#             names.append(a_contact.split()[0])
#             emails.append(a_contact.split()[1])
#     return names, emails
# 
# def read_template(filename):
#     """
#     Returns a Template object comprising the contents of the 
#     file specified by filename.
#     """
#     
#     with open(filename, 'r', encoding='utf-8') as template_file:
#         template_file_content = template_file.read()
#     return Template(template_file_content)

def main():
    names, emails = get_contacts('path\\to\\contacts.txt') # read contacts
    message_template = read_template('path\\to\\message.txt')

    # set up the SMTP server
    s = smtplib.SMTP(host='your_host_address_here', port=your_port_here)
    s.starttls()
    s.login(MY_ADDRESS, PASSWORD)

    # For each contact, send the email:
    for name, email in zip(names, emails):
        msg = MIMEMultipart()       # create a message

        # add in the actual person name to the message template
        message = message_template.substitute(PERSON_NAME=name.title())

        # Prints out the message body for our sake
        print(message)

        # setup the parameters of the message
        msg['From']=MY_ADDRESS
        msg['To']=email
        msg['Subject']="This is TEST"
        
        # add in the message body
        msg.attach(MIMEText(message, 'plain'))
        
        # send the message via the server set up earlier.
        s.send_message(msg)
        del msg
        
    # Terminate the SMTP session and close the connection
    s.quit()
    
if __name__ == '__main__':
    main()