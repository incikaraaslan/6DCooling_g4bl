import subprocess
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import random
from tqdm import trange
from tolRFsinglestage import singleStageNoErr, singleStage
import re
import glob
from natsort import natsorted
import matplotlib.pyplot as plt
from itertools import islice

def searchforVals(filename):
    """
        Look for parameters for a given stage.
    """
    with open(filename, 'r') as f:
        content = f.read()

    # Use regex search on the whole content
    mrfgrad = re.search(r'param\s+rf_grad\s*=\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)', content)
    mrfphase = re.search(r'param\s+rf_ph\s*=\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)', content)
    mrffreq = re.search(r'param\s+rf_fre\s*=\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)', content)
    mrfwindowlength = re.search(r'param\s+rf_window_length\s*=\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)', content)
    mnocells = re.search(r'param\s+ncells\s*=\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)', content)

    # Extract number of cavities by looping over lines
    mnocav = None
    for line in content.splitlines():
        match = re.match(r'#\s*(\d+)\s+CAVITIES', line)
        if match:
            mnocav = match
            break

    # Check all matches
    if not all([mrfgrad, mrfphase, mrffreq, mrfwindowlength, mnocav, mnocells]):
        raise ValueError("One or more parameters not found in file.")

    return (
        float(mrfgrad.group(1)),
        float(mrfphase.group(1)),
        float(mrffreq.group(1)),
        float(mrfwindowlength.group(1)),
        int(mnocav.group(1)),
        int(mnocells.group(1))
    )

def allStages(meane, stdeve, stdev_phase, sample_size, number_of_particles):
    """
    
        We'd like to go through all 10 stages in one go FOR ALL # sample sizes. So ideally, it should create the 0th file for all 10 stages FIRST
        and then go back and create the 1st file for all 10.
    
    """
    file_list = natsorted(glob.glob("./incis_cleaned_cooling_stage*_variablerfs.g4bl"))
    noerr_list = natsorted(f for f in glob.glob("./incis_cleaned_cooling_stage*.g4bl") if re.fullmatch(r"\./incis_cleaned_cooling_stage\d+\.g4bl", f))
    
    err_data = []
    noerr_data = []
    last_data = []
    z_data = []
    
    for sample_no in trange(sample_size): #as many samples as frac_errs, i.e. 10 here.
        
        print("Sample #: " + str(sample_no))
        
        for i, filename in enumerate(file_list): # going through stages
            print(filename)
            stage_no = i+1
            # ACTUAL VALUES -- READ THEM FROM EACH STAGE
            rfgrad_actual, rfphase_actual, rffreq_actual, rfwindowlength_actual, ncavities, ncells = searchforVals(filename)
            mean = rfgrad_actual + meane
            stdev = stdeve
            meanp = rfphase_actual + meane
            stdevp = stdev_phase
            
            data = singleStage(filename, mean, stdev, meanp, stdevp, ncavities, ncells, number_of_particles, stage_no, sample_no)
            
            # GRAB OPTION 0
            # Get the last row ([-1]) which has the last values of each column
            last_values = data[-1]
            last_data.append([last_values[0],last_values[1],last_values[2],last_values[3], last_values[4]])
            z_data.append(last_values[0])

    # GRAB OPTION 0
    z_last = []
    z_avg = []
    z_sem =[]
    eperp_last = []
    eperp_sem = []
    eperp_avg = []
    elong_last = []
    elong_avg = []
    elong_sem = []
    e6d_last =[]
    e6d_avg = []
    e6d_sem = []
    trans_last = []
    trans_avg = []
    trans_sem = []
    
    zcur = 0
    trans = 1
    stage_no = 10
    for i in trange(stage_no):
        for j in trange(sample_size):
            if j == 0:
                zcur += last_data[i:stage_no*sample_size:stage_no][j][0]
                z_last.append(zcur)
                
            eperp_last.append(last_data[i:stage_no*sample_size:stage_no][j][1])
            elong_last.append(last_data[i:stage_no*sample_size:stage_no][j][2])
            e6d_last.append(last_data[i:stage_no*sample_size:stage_no][j][3])
            trans_last.append(last_data[i:stage_no*sample_size:stage_no][j][4])
        
        # z_avg.append(np.average(np.asarray(z_last[i*sample_size:sample_size*i+sample_size])))
        eperp_avg.append(np.average(np.asarray(eperp_last[i*sample_size:sample_size*i+sample_size])))
        elong_avg.append(np.average(np.asarray(elong_last[i*sample_size:sample_size*i+sample_size])))
        e6d_avg.append(np.average(np.asarray(e6d_last[i*sample_size:sample_size*i+sample_size])))
        trans_avg.append(np.average(np.asarray(trans_last[i*sample_size:sample_size*i+sample_size])))
        
        # z_sem.append(np.std(np.asarray(z_last[i*sample_size:sample_size*i+sample_size])) / np.sqrt(np.asarray(z_last[i*sample_size:sample_size*i+sample_size]).shape[0]))
        eperp_sem.append(np.std(np.asarray(eperp_last[i*sample_size:sample_size*i+sample_size])) / np.sqrt(np.asarray(eperp_last[i*sample_size:sample_size*i+sample_size]).shape[0]))
        elong_sem.append(np.std(np.asarray(elong_last[i*sample_size:sample_size*i+sample_size])) / np.sqrt(np.asarray(elong_last[i*sample_size:sample_size*i+sample_size]).shape[0]))
        e6d_sem.append(np.std(np.asarray(e6d_last[i*sample_size:sample_size*i+sample_size])) / np.sqrt(np.asarray(e6d_last[i*sample_size:sample_size*i+sample_size]).shape[0]))
        trans_sem.append(np.std(np.asarray(trans_last[i*sample_size:sample_size*i+sample_size])) / np.sqrt(np.asarray(trans_last[i*sample_size:sample_size*i+sample_size]).shape[0]))
    
    transmission = np.prod(np.asarray(trans_avg))
    transmission_error = np.prod(np.asarray(trans_sem))
    
    # NO ERR NEEDED ONCE
    eperp_noerrl = []
    elong_noerrl = []
    e6d_noerrl = []
    trans_noerrl = []
    for i, nfilename in enumerate(noerr_list):
        print(nfilename)
        stage_no = i+1
        datanoerr = singleStageNoErr(nfilename, number_of_particles, stage_no)
        z_noerr, eperp_noerr, elong_noerr, e6d_noerr, trans_noerr = datanoerr.T
        
        eperp_noerrl.append(eperp_noerr[-1])
        elong_noerrl.append(elong_noerr[-1])
        e6d_noerrl.append(e6d_noerr[-1])
        trans_noerrl.append(trans_noerr[-1])
    
    transmission_noerr = np.prod(np.asarray(trans_noerrl))

    return transmission_noerr, transmission, transmission_error, e6d_noerrl[-1], e6d_avg[-1], e6d_sem[-1]