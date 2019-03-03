# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 15:26:45 2017

@author: esilgard
"""
import json
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
config = json.load(open(dir_path + os.path.sep + 'config.json','r'))
STTR_GU_TEAM = config["sttr_gu_team"]
STTR_BR_TEAM = config["sttr_breast_team"]
def get(cur, formatted_dz_group, query_disease_groups):
    '''
    get patient counts, demographics, and clinical data from caisis
    based on the given disease group (as definied in the status table)
    '''

    if formatted_dz_group == 'Prostate':
        pt_query_string = "SELECT distinct PatientId, ActionDate FROM Actions WHERE \
            (UpdatedBy in " + STTR_GU_TEAM + " OR EnteredBy in " + STTR_GU_TEAM + ")"
    elif formatted_dz_group == 'Breast':
        pt_query_string = "SELECT distinct PatientId, StatusDate FROM Status WHERE \
            (UpdatedBy in " + STTR_BR_TEAM + " OR EnteredBy in " + STTR_BR_TEAM + \
            ") AND Status.StatusDisease = 'Breast Cancer' and Status = 'Alive' "
    elif formatted_dz_group == 'LiverMets':
        pt_query_string = "SELECT distinct PatientId, StatusDate FROM Status WHERE \
            Status.Status = 'Metastatic Disease' "
   
    else:
        pt_query_string = "SELECT distinct PatientId, StatusDate FROM Status WHERE \
            Status.Status = 'Alive' AND StatusDate is not NULL AND " + query_disease_groups

    cur.execute(pt_query_string)
    patients = set([str(x[0]) for x in cur.fetchall()])

    ## store diagnosis dates
    dx_query_string = "SELECT distinct Patientid, statusDate, statusDateText FROM Status WHERE \
    Status.Status = 'Diagnosis Date' AND StatusDate is not NULL AND Patientid in \
    ('" + "','".join(patients) + "') "
    if formatted_dz_group != 'LiverMets':
        dx_query_string += " AND " + query_disease_groups
    cur.execute(dx_query_string)
    
    dx = dict((x[0],x[1]) for x in cur.fetchall())
    fuzzy_dx = dict((x[0],x[2]) for x in cur.fetchall() if x[1] == None)
    # an FYI on how many patients have a "fuzzy" dx date
    # just year, or month and year will have a textdate, but no datetime
    #print fuzzy_dx, 'patients with fuzzy diagnosis date'
    #print out basic patient counts - sanity check
    print (formatted_dz_group + '-' + str(len(patients)))
        ## basic demographic data
    cur.execute("SELECT PatientId, PtGender, PtBirthDate, PtDeathDate, PtMRN FROM \
    Patients WHERE PatientId in ('" + "','".join(patients) + "')")
    demographics = dict((x[0],x[1:]) for x in cur.fetchall())

    ## query clinical therapy data
    cur.execute("SELECT distinct PatientId  FROM MedicalTherapy WHERE \
    PatientId in ('" + "','".join(patients) + "')")
    med_tx = set([x[0] for x in cur.fetchall()])
    
    cur.execute("SELECT distinct PatientId  FROM RadiationTherapy WHERE \
    PatientId in ('" + "','".join(patients) + "')")
    rad_tx = set([x[0] for x in cur.fetchall()])
    
    cur.execute("SELECT distinct PatientId  FROM PathTest INNER JOIN \
    Pathology ON Pathology.PathologyId = PathTest.PathologyId WHERE \
    PatientId in ('" + "','".join(patients) + "') AND PathMethod LIKE '%OncoPlex%' ")
    oncoplex = set([x[0] for x in cur.fetchall()])
    
    cur.execute("SELECT distinct PatientId, StatusDisease FROM status \
        WHERE PatientId in('" + "','".join(patients) + "') AND Status = 'Alive'")    
    primes = [p[1] for p in cur.fetchall()]
    primaries = dict((y,primes.count(y)) for y in set(primes))
    
    return patients, dx, demographics ,med_tx, rad_tx, oncoplex, primaries
