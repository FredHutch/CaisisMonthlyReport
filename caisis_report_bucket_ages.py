# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 14:59:48 2017

@author: esilgard

bucket ages for bar graphs in monthly caisis report script
"""
import datetime
current_ages = ['0-10', '11-20', '21-30','31-40', '41-50','51-60', '61-70', \
                '71-80', '81-90', '91-100', '101-110', 'deceased']
dx_ages = ['Unknown'] + current_ages[:-1]
   
def bucket(dx, dob, dod, err_msg, demographics):       

    dx_age_counts = dict.fromkeys(dx_ages, 0)
    current_age_counts = dict.fromkeys(current_ages, 0)
    current_age_counts['deceased'] = len(dod)
    
    for each in demographics:
        ## put patients into correct bucket based on age
        each = int(each)
        their_dob = dob[each]   
        try:
            dx_age = (dx[each]-their_dob).days/365.0
        except:  
            # find missing diagnosis dates for QA review
            dx_age = 'Unknown'
            err_msg += 'ERROR determining diagnosis age for patient '+ \
            demographics.get(each)[-1] + '\n'
       
        if each not in dod:
            try:
                cur_age = (datetime.datetime.today()-their_dob).days/365.0
            except:
                cur_age = 0
            for b in dx_ages:   
                if b == 'Unknown':
                    if dx_age == 'Unknown':
                        dx_age_counts[b] += 1
                else:
                    lower = int(b.split('-')[0])
                    upper = int(b.split('-')[1])
                    if dx_age < upper and dx_age > lower:
                        dx_age_counts[b] += 1
                    if cur_age < upper and cur_age > lower:
                        current_age_counts[b] += 1

    return current_age_counts, dx_age_counts, current_ages, dx_ages, err_msg