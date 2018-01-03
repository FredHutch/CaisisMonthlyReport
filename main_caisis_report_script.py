# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 13:47:24 2016

@author: esilgard
"""

'''
query caisis disease groups for basic counts of data elements for a report
write counts and charts to excel

•	Age brackets for diagnosis age and current age
•	Gender
•	MedTx yes/no,
•	RadTx yes/no
•	Oncoplex results yes/no

'''

import xlsxwriter
import pyodbc
import os
import json

import caisis_report_bucket_ages as age
import caisis_report_data as data
import caisis_report_bar_charts as bar
import caisis_report_pie_charts as pie
import caisis_report_email as email


dir_path = os.path.dirname(os.path.realpath(__file__))
config = json.load(open(dir_path + os.path.sep + 'config.json','r'))
pattern_fills = config['pattern_fills']
brand_colors = config['brand_colors']
###############################################################################
## disease groups should be a string match to those listed in the Status table
err_msg = ''

for formatted_dz, query_string in config['dz_groups'].items():
    
    email_recipients = ';'.join(config["email_recipients"])
    ## pyodbc connection string details
    inst = 'vanilla'
    if formatted_dz == 'Prostate':
        inst = 'gu'
    connStr = ('DRIVER=' + config[inst + '_caisis']['driver'] + ';SERVER=' + \
               config[inst + '_caisis']['server'] +';DATABASE=' + \
               config[inst + '_caisis']['database'] +';Trusted_Connection=yes')    
    conn = pyodbc.connect(connStr)
    cur = conn.cursor()
    ###############################################################################
    
    ## query database
    patients, dx, demographics, med_tx, rad_tx, oncoplex, primaries = \
        data.get(cur, formatted_dz, query_string) 
    workbook_name = formatted_dz + 'CaisisReport.xlsx' 
    # the space seems to be problematic in worksheet reference ranges
    workbook = xlsxwriter.Workbook(workbook_name)
    # format to use in the merged range (first cell in worksheet)
    merge_format = workbook.add_format({'bold': 1,'border': 8,'align': 'center',
        'valign': 'vcenter','fg_color': '#e9e9e9'})
    # formats to use in the counts tables (basically adds a border)
    table_format = workbook.add_format({'border': 2,'align': 'center',
        'valign': 'vcenter'})
    table_format_bold = workbook.add_format({'bold': 1,'border': 2, 'align': 'center',
        'valign': 'vcenter'})
    
    worksheet = workbook.add_worksheet(formatted_dz)
    # Add the worksheet data that the charts will refer to.
    worksheet.merge_range('A1:C1', str(len(patients)) + ' Total Patients', merge_format)
    all_genders = [y[0] for y in demographics.values()]
    gender_list = sorted(list(set(all_genders)))
    
    def add_table(title, t1, labels, l1, values, v1):
        worksheet.write_row(t1, [title, 'Counts'], table_format_bold)
        worksheet.write_column(l1, labels, table_format)
        worksheet.write_column(v1, values, table_format)   
    
        
    add_table('Gender', 'A2', ['Male', 'Female'], 'A3', [all_genders.count(h) for h in gender_list], 'B3')
    add_table('MedTx', 'D2', ['At Least 1', 'None'], 'D3', [len(med_tx),len(patients)-len(med_tx)], 'E3')
    add_table('RadTx', 'G2', ['At Least 1', 'None'], 'G3', [len(rad_tx),len(patients)-len(rad_tx)], 'H3')
    add_table('Oncoplex', 'J2', ['At Least 1', 'None'],'J3', [len(oncoplex),len(patients)-len(oncoplex)], 'K3')
    #primary tumor sites for liver mets cases
    if formatted_dz == 'LiverMets':
        prim_desc = sorted(primaries.items(), key=lambda x: x[1], reverse = True)
        add_table('Primary', 'M2', [p[0].replace(' Cancer','') for p in prim_desc], 
            'M3', [p[1] for p in prim_desc], 'N3' )
    
    pie_chart_space = [('Gender', 'A', '3:4', 's'),('MedTx', 'D', '3:4', 's'),
        ('RadTx','G', '3:4', 's'),('OPX','J', '3:4', 's')]
    if formatted_dz == 'LiverMets':
        pie_chart_space.append(('Primary','M','3:' + str(3+len(primaries)-1), 'l'))
    
    worksheet = pie.add(worksheet, pie_chart_space, workbook, formatted_dz)
    #worksheet = pie.add(worksheet, ('Primary','M'), workbook)
    dod = dict((a[0],a[1][2]) for a in demographics.items() if a[1][2] is not None)
    dob = dict((a[0],a[1][1]) for a in demographics.items())
    current_age_counts, dx_age_counts, buckets1, buckets2, err_msg = \
        age.bucket(dx, dob, dod, err_msg, demographics)
    
    bar_chart_space = [('Age At Diagnosis','A',dx_age_counts, buckets2), \
        ('Calculated Current Age','J', current_age_counts, buckets1)]
    
    worksheet = bar.add(workbook, worksheet, bar_chart_space, table_format_bold, formatted_dz)
    workbook.close()

email.send(email_recipients, err_msg, dir_path, config['dz_groups'].keys())
    
