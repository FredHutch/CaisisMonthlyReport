# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 15:26:45 2017

@author: esilgard

query through pyodbc for caisis data
"""
import json
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
config = json.load(open(dir_path + os.path.sep + 'resources' + os.path.sep + 'config.json','r'))
STTR_TEAM = config["sttr_gu_team"]
def get(cur, formatted_dz_group, query_disease_groups):
    '''
    get patient counts, demographics, and clinical data from caisis
    based on the given disease group (as definied in the status table)
    '''

    if formatted_dz_group == 'Prostate':
        # get only prostate patients who have been updated in the "Actions" table
        # by an STTR abstractor (listed in config file)
        pt_query_string = "SELECT distinct PatientId, ActionDate FROM Actions WHERE \
            (UpdatedBy in " + STTR_TEAM + " OR EnteredBy in " + STTR_TEAM + ')'
        
    elif formatted_dz_group == 'LiverMets':
        # select only the patients who have a metastasis to the liver, no matter what the primary dz
        pt_query_string = "SELECT distinct PatientId, StatusDate FROM Status WHERE \
            Status.Status = 'Metastatic Disease' "
   
    else:
        # standard case - query by the last known alive date 
        # (a marker for which disease the patient was abstracted)
        pt_query_string = "SELECT distinct PatientId, StatusDate FROM Status WHERE \
            Status.Status = 'Alive' AND StatusDate is not NULL AND " + query_disease_groups

    cur.execute(pt_query_string)
    patients = set([str(x[0]) for x in cur.fetchall()])

    ## store diagnosis dates
    dx_query_string = "SELECT distinct Patientid, statusDate, statusDateText FROM Status WHERE \
    Status.Status = 'Diagnosis Date' AND StatusDate is not NULL AND Patientid in \
    ('" + "','".join(patients) + "') "
    if formatted_dz_group != 'LiverMets':
        # for everything OTHER than liver mets - make sure you're getting the primary diagnosis date
        # for liver mets cases, we're not guaranteeing that the diagnosis date will be for the
        # liver mets related disease (could be a different primary)
        dx_query_string += " AND " + query_disease_groups
    cur.execute(dx_query_string)
    
    dx = dict((x[0],x[1]) for x in cur.fetchall())
    fuzzy_dx = dict((x[0],x[2]) for x in cur.fetchall() if x[1] == None)
    #print out basic patient counts - sanity check
    print (formatted_dz_group + ' yeilding ' + str(len(patients)) + 'patients')
    
    ## basic demographic data
    cur.execute("SELECT PatientId, PtGender, PtBirthDate, PtDeathDate, PtMRN FROM \
    Patients WHERE PatientId in ('" + "','".join(patients) + "')")
    demographics = dict((x[0],x[1:]) for x in cur.fetchall())

    ## query medical(chemo) therapy data
    cur.execute("SELECT distinct PatientId  FROM MedicalTherapy WHERE \
    PatientId in ('" + "','".join(patients) + "')")
    med_tx = set([x[0] for x in cur.fetchall()])
    
    ## query radiation therapy data
    cur.execute("SELECT distinct PatientId  FROM RadiationTherapy WHERE \
    PatientId in ('" + "','".join(patients) + "')")
    rad_tx = set([x[0] for x in cur.fetchall()])
    
    ## query oncolplex test results
    cur.execute("SELECT distinct PatientId  FROM PathTest INNER JOIN \
    Pathology ON Pathology.PathologyId = PathTest.PathologyId WHERE \
    PatientId in ('" + "','".join(patients) + "') AND PathMethod LIKE '%OncoPlex%' ")
    oncoplex = set([x[0] for x in cur.fetchall()])
    
    cur.execute("SELECT distinct PatientId, StatusDisease FROM status \
        WHERE PatientId in('" + "','".join(patients) + "') AND Status = 'Alive'")    
    primary_list = [x[1] for x in cur.fetchall()]
    primaries = dict((y,primary_list.count(y)) for y in set(primary_list))
    return patients, dx, demographics ,med_tx, rad_tx, oncoplex, primaries
