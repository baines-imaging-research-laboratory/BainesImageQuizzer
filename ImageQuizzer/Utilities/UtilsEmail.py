#
#   https://www.freecodecamp.org/news/send-emails-using-code-4fcea9df63f/
#

import os, sys
import smtplib

from string import Template

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# MY_ADDRESS = 'my_address@example.com'
# PASSWORD = 'mypassword'

class UtilsEmail:
    """ To set up functions to email the results to the requested email address.
    """

    def __init__(self):
        
        self.sHostServer = ''
        self.sHostUserName = ''
        self.sHostPassword = ''
        self.iHostPort = 587
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SetupEmailResults(self, oFilesIO, sEmailResultsTo):
        """ Setup if request was set to have the quiz results emailed upon completion.
        """
        if sEmailResultsTo != '':
            # get path to config file
            sConfigPathsFilename = os.path.join(oFilesIO.GetResourcesConfigDir(),\
                                               'smtp_config_paths.txt')
            sSmtpConfigFile = self.ParseConfigFile(sConfigPathsFilename,'paths','config')
            
            if sSmtpConfigFile != '':
                self.sHostServer = self.ParseConfigFile(sSmtpConfigFile, 'smtp', 'host')
                self.sHostUserName = self.ParseConfigFile(sSmtpConfigFile, 'smtp', 'username')
                self.sHostPassword = self.ParseConfigFile(sSmtpConfigFile, 'smtp', 'password')
                self.iHostPort = int(self.ParseConfigFile(sSmtpConfigFile, 'smtp', 'port'))
            
            
            
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
#                             sItemValue = sLine.lstrip(sItemSyntax)
                            sItemValue = sLine[len(sItemSyntax):len(sLine)]
                            sItemValue.rstrip('\n')
                            
                            bItemFound = True
                            break
                    
            if not bItemFound:
                sLine = fileConfig.readline()
                iCnt = iCnt + 1
            else:
                fileConfig.close()
                break
                
        return sItemValue
                    
                    
                    
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