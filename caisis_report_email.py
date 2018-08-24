# -*- coding: utf-8 -*-
"""
Created on Wed Nov 01 14:21:36 2017

@author: esilgard
"""


## set up email through outlook
import win32com.client
import datetime
import os

def send(email_recipients, err_msg, workbook_path, formatted_dzs):
    olMailItem = 0x0
    obj = win32com.client.Dispatch("Outlook.Application")
    newMail = obj.CreateItem(olMailItem)
    newMail.Subject = "Monthly Caisis Report " + str(datetime.datetime.now())
    newMail.Body = \
        'This is an automatically generated email detailing the monthly ' + \
        'Caisis clinical data updates per STTR disease group \n\n'
    ## this should not be sent to anyone who can't see Caisis PHI
    ## in case of MRN in error message
    
    newMail.To = email_recipients   
    for dz in formatted_dzs:
        newMail.Attachments.Add(workbook_path + os.path.sep + dz + 'CaisisReport.xlsx')    
    newMail.Body += err_msg
    newMail.Send()    